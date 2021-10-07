import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, cast

from metaphor.models.metadata_change_event import (
    DataPlatform,
    Dataset,
    DatasetDocumentation,
    DatasetLogicalID,
    DatasetSchema,
    DatasetStatistics,
    DatasetUpstream,
    DbtMacro,
    DbtMacroArgument,
    DbtMaterialization,
    DbtMaterializationType,
    DbtModel,
    DbtTest,
    EntityType,
    FieldDocumentation,
    MetadataChangeEvent,
    SchemaField,
    SchemaType,
    SQLSchema,
    VirtualView,
    VirtualViewLogicalID,
    VirtualViewType,
)
from serde import deserialize

from metaphor.common.entity_id import EntityId, to_virtual_view_entity_id
from metaphor.common.event_util import EventUtil
from metaphor.common.extractor import BaseExtractor, RunConfig

from .generated.dbt_catalog import CatalogTable, DbtCatalog
from .generated.dbt_manifest import (
    CompiledModelNode,
    CompiledSchemaTestNode,
    DbtManifest,
    ParsedMacro,
    ParsedSourceDefinition,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class DbtDataset:
    database: str
    schema: str
    name: str


@deserialize
@dataclass
class DbtRunConfig(RunConfig):
    manifest: str
    catalog: str

    # the database service account this DBT project is connected to
    account: Optional[str] = None


class DbtExtractor(BaseExtractor):
    """DBT metadata extractor"""

    @staticmethod
    def config_class():
        return DbtRunConfig

    def __init__(self):
        self.platform: DataPlatform = DataPlatform.UNKNOWN
        self.account: Optional[str] = None
        self._manifest: DbtManifest
        self._catalog: DbtCatalog
        self._datasets: Dict[str, Dataset] = {}
        self._virtual_views: Dict[str, VirtualView] = {}

    async def extract(self, config: DbtRunConfig) -> List[MetadataChangeEvent]:
        assert isinstance(config, DbtExtractor.config_class())

        logger.info("Fetching metadata from DBT repo")
        self.account = config.account

        try:
            self._manifest = DbtManifest.parse_file(Path(config.manifest))
        except Exception as e:
            logger.error(f"Read manifest json error: {e}")
            raise e

        try:
            self._catalog = DbtCatalog.parse_file(Path(config.catalog))
        except Exception as e:
            logger.error(f"Read catalog json error: {e}")
            raise e

        self._parse_manifest()

        self._parse_catalog()

        dataset_events = [
            EventUtil.build_dataset_event(d) for d in self._datasets.values()
        ]
        virtual_view_events = [
            EventUtil.build_virtual_view_event(d) for d in self._virtual_views.values()
        ]
        return dataset_events + virtual_view_events

    def _parse_manifest(self) -> None:
        assert self._manifest is not None

        metadata = self._manifest.metadata

        assert metadata.adapter_type is not None
        platform = metadata.adapter_type.upper()
        assert platform in DataPlatform.__members__, f"Invalid data platform {platform}"
        self.platform = DataPlatform[platform]

        nodes = self._manifest.nodes
        sources = self._manifest.sources
        macros = self._manifest.macros

        models = {
            k: cast(CompiledModelNode, v)
            for (k, v) in nodes.items()
            if isinstance(v, CompiledModelNode)
        }
        tests = {
            k: cast(CompiledSchemaTestNode, v)
            for (k, v) in nodes.items()
            if isinstance(v, CompiledSchemaTestNode)
        }

        dataset_map = {}
        for key, model in models.items():
            assert model.database is not None
            dataset_map[key] = DbtDataset(model.database, model.schema_, model.name)
        for key, source in sources.items():
            assert source.database is not None
            dataset_map[key] = DbtDataset(source.database, source.schema_, source.name)

        for model in models.values():
            self._parse_model(model, dataset_map)

        for test in tests.values():
            self._parse_test(test)

        self._parse_manifest_nodes(sources, macros, tests, models)

    def _parse_model(
        self,
        model: CompiledModelNode,
        dataset_map: Dict[str, DbtDataset],
    ) -> None:
        assert model.database is not None
        dataset = self._init_dataset(
            model.database, model.schema_, model.name, model.unique_id
        )
        self._init_schema(dataset)

        if model.compiled_sql is not None:
            assert dataset.schema is not None
            dataset.schema.sql_schema = SQLSchema()
            dataset.schema.sql_schema.table_schema = model.compiled_sql

        if model.description is not None:
            dataset.schema.description = model.description
            self._init_documentation(dataset)
            assert (
                dataset.documentation is not None
                and dataset.documentation.dataset_documentations is not None
            )
            dataset.documentation.dataset_documentations.append(model.description)

        if model.columns is not None:
            for col in model.columns.values():
                column_name = col.name.lower()
                field = self._init_field(dataset.schema.fields, column_name)
                field.description = col.description
                field.native_type = (
                    "Not Set" if col.data_type is None else col.data_type
                )

                if col.description:
                    field_doc = self._init_field_doc(dataset, column_name)
                    field_doc.documentation = col.description

        if model.depends_on is not None:
            dataset.upstream = DatasetUpstream()
            dataset.upstream.source_code_url = model.original_file_path

            if model.depends_on.nodes is not None:
                dataset.upstream.source_datasets = [
                    self._get_dataset_id(dataset_map[n]) for n in model.depends_on.nodes
                ]

    def _parse_test(self, test: CompiledSchemaTestNode) -> None:
        if test.test_metadata is None:
            return

        if test.depends_on is None or not test.depends_on.nodes:
            return

        depends_on_model = test.depends_on.nodes[0]
        if depends_on_model not in self._datasets:
            return

        dataset = self._datasets[depends_on_model]

        columns = []
        if test.columns:
            columns = list(test.columns.keys())
        elif test.column_name is not None:
            columns = [test.column_name]

        for column in columns:
            field_doc = self._init_field_doc(dataset, column)
            if not field_doc.tests:
                field_doc.tests = []
            field_doc.tests.append(test.test_metadata.name)

    def _parse_catalog(self) -> None:
        if self._catalog is None:
            return

        nodes = self._catalog.nodes
        sources = self._catalog.sources

        for model in {**nodes, **sources}.values():
            self._parse_catalog_model(model)

    def _parse_catalog_model(self, model: CatalogTable):
        meta = model.metadata
        columns = model.columns
        stats = model.stats

        assert meta.database is not None
        assert model.unique_id is not None
        dataset = self._init_dataset(
            meta.database, meta.schema_, meta.name, model.unique_id
        )

        # TODO (ch1236): Re-enable once we figure the source & expected format
        # self._init_ownership(dataset)
        # assert dataset.ownership is not None and dataset.ownership.people is not None
        # dataset.ownership.people.append(self._build_owner(meta["owner"]))

        self._init_schema(dataset)
        self._init_documentation(dataset)

        for col in columns.values():
            column_name = col.name.lower()
            field = self._init_field(dataset.schema.fields, column_name)
            field.description = col.comment
            field.native_type = "Not Set" if col.type is None else col.type

            if col.comment:
                field_doc = self._init_field_doc(dataset, column_name)
                field_doc.documentation = col.comment

        has_stats = stats.get("has_stats")
        if has_stats is not None and has_stats.value is not None:
            statistics = DatasetStatistics()
            found_statistics = False

            row_count = stats.get("row_count")
            if row_count is not None and row_count.value is not None:
                found_statistics = True
                statistics.record_count = float(row_count.value)

            bytes = stats.get("bytes")
            if bytes is not None and bytes.value is not None:
                found_statistics = True
                statistics.data_size = (
                    float(bytes.value) / 1048576  # convert bytes to MB
                )

            last_modified = stats.get("last_modified")
            if last_modified is not None and last_modified.value is not None:
                found_statistics = True
                if isinstance(last_modified.value, str):
                    # Must set tzinfo explicitly due to https://bugs.python.org/issue22377
                    statistics.last_updated = datetime.strptime(
                        last_modified.value, "%Y-%m-%d %H:%M%Z"
                    ).replace(tzinfo=timezone.utc)
                else:
                    statistics.last_updated = datetime.fromtimestamp(
                        last_modified.value
                    ).replace(tzinfo=timezone.utc)

            if found_statistics:
                dataset.statistics = statistics

    def _parse_manifest_nodes(
        self,
        sources: Dict[str, ParsedSourceDefinition],
        macros: Dict[str, ParsedMacro],
        tests: Dict[str, CompiledSchemaTestNode],
        models: Dict[str, CompiledModelNode],
    ) -> None:
        source_map = {}
        for key, source in sources.items():
            assert source.database is not None
            source_map[key] = DbtDataset(source.database, source.schema_, source.name)

        macro_map = {}
        for key, macro in macros.items():
            arguments = (
                [
                    DbtMacroArgument(
                        name=arg.name,
                        type=arg.type,
                        description=arg.description,
                    )
                    for arg in macro.arguments
                ]
                if macro.arguments
                else []
            )

            macro_map[key] = DbtMacro(
                name=macro.name,
                unique_id=macro.unique_id,
                package_name=macro.package_name,
                description=macro.description,
                arguments=arguments,
                sql=macro.macro_sql,
                depends_on_macros=macro.depends_on.macros if macro.depends_on else None,
            )

        for _, model in models.items():
            self._init_virtual_view(model.unique_id)

        for key, model in models.items():
            virtual_view = self._init_virtual_view(model.unique_id)
            virtual_view.dbt_model = DbtModel(
                package_name=model.package_name,
                description=model.description,
                tags=model.tags,
                raw_sql=model.raw_sql,
                compiled_sql=model.compiled_sql,
                fields=[],
            )
            dbt_model = virtual_view.dbt_model

            assert model.config is not None and model.database is not None
            materialized = model.config.materialized

            if materialized:
                dbt_model.materialization = DbtMaterialization(
                    type=DbtMaterializationType[materialized.upper()],
                    target_dataset=self._get_dataset_id(
                        DbtDataset(model.database, model.schema_, model.name)
                    ),
                )

            if model.columns is not None:
                for col in model.columns.values():
                    column_name = col.name.lower()
                    field = self._init_field(dbt_model.fields, column_name)
                    field.description = col.description
                    field.native_type = (
                        "Not Set" if col.data_type is None else col.data_type
                    )

            if model.depends_on is not None:
                if model.depends_on.nodes:
                    dbt_model.source_models = [
                        self._get_virtual_view_id(self._virtual_views[n].logical_id)
                        for n in model.depends_on.nodes
                        if n.startswith("model.")
                    ]

                    dbt_model.source_datasets = [
                        self._get_dataset_id(source_map[n])
                        for n in model.depends_on.nodes
                        if n.startswith("source.")
                    ]

                if model.depends_on.macros:
                    dbt_model.macros = [macro_map[n] for n in model.depends_on.macros]

        for key, test in tests.items():
            # check test is referring a model
            if test.depends_on is None or not test.depends_on.nodes:
                continue

            model_unique_id = test.depends_on.nodes[0]
            if not model_unique_id.startswith("model."):
                continue

            columns = []
            if test.columns:
                columns = list(test.columns.keys())
            elif test.column_name:
                columns = [test.column_name]

            dbt_test = DbtTest(
                name=test.name,
                unique_id=test.unique_id,
                columns=columns,
                depends_on_macros=test.depends_on.macros,
                sql=test.compiled_sql,
            )

            self._init_dbt_tests(model_unique_id).append(dbt_test)

    @staticmethod
    def _dataset_name(db: str, schema: str, table: str) -> str:
        return f"{db}.{schema}.{table}".lower()

    def _get_dataset_id(self, dataset: DbtDataset) -> str:
        dataset_name = DbtExtractor._dataset_name(
            dataset.database, dataset.schema, dataset.name
        )

        dataset_id = DatasetLogicalID(
            name=dataset_name,
            platform=self.platform,
            account=self.account,
        )
        return str(EntityId(EntityType.DATASET, dataset_id))

    @staticmethod
    def _get_virtual_view_id(logical_id: VirtualViewLogicalID) -> str:
        return str(to_virtual_view_entity_id(logical_id.name, logical_id.type))

    @staticmethod
    def _get_model_name_from_unique_id(unique_id: str) -> str:
        assert unique_id.startswith("model."), f"invalid model id {unique_id}"
        return unique_id[6:]

    def _init_dataset(
        self, database: str, schema: str, name: str, unique_id: str
    ) -> Dataset:
        if unique_id not in self._datasets:
            self._datasets[unique_id] = Dataset(
                logical_id=DatasetLogicalID(
                    name=self._dataset_name(database, schema, name),
                    platform=self.platform,
                    account=self.account,
                )
            )
        return self._datasets[unique_id]

    def _init_virtual_view(self, unique_id: str) -> VirtualView:
        if unique_id not in self._virtual_views:
            self._virtual_views[unique_id] = VirtualView(
                logical_id=VirtualViewLogicalID(
                    name=self._get_model_name_from_unique_id(unique_id),
                    type=VirtualViewType.DBT_MODEL,
                ),
            )
        return self._virtual_views[unique_id]

    def _init_dbt_tests(self, dbt_model_unique_id: str) -> List[DbtTest]:
        assert dbt_model_unique_id in self._virtual_views

        dbt_model = self._virtual_views[dbt_model_unique_id].dbt_model
        if dbt_model.tests is None:
            dbt_model.tests = []
        return dbt_model.tests

    @staticmethod
    def _init_schema(dataset: Dataset) -> None:
        if not dataset.schema:
            dataset.schema = DatasetSchema()
            dataset.schema.schema_type = SchemaType.SQL
            dataset.schema.fields = []

    @staticmethod
    def _init_field(fields: List[SchemaField], column: str) -> SchemaField:
        field = next((f for f in fields if f.field_path == column), None)
        if not field:
            field = SchemaField(field_path=column)
            fields.append(field)
        return field

    @staticmethod
    def _init_documentation(dataset: Dataset) -> None:
        if not dataset.documentation:
            dataset.documentation = DatasetDocumentation()
            dataset.documentation.dataset_documentations = []
            dataset.documentation.field_documentations = []

    @staticmethod
    def _init_field_doc(dataset: Dataset, column: str) -> FieldDocumentation:
        assert (
            dataset.documentation is not None
            and dataset.documentation.field_documentations is not None
        )

        doc = next(
            (
                d
                for d in dataset.documentation.field_documentations
                if d.field_path == column
            ),
            None,
        )
        if not doc:
            doc = FieldDocumentation()
            doc.field_path = column
            dataset.documentation.field_documentations.append(doc)
        return doc
