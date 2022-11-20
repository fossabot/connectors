from typing import Dict, List, Optional, Tuple, Type, Union

from pydantic.utils import unique_list

from metaphor.common.entity_id import EntityId
from metaphor.common.logger import get_logger
from metaphor.dbt.config import DbtRunConfig
from metaphor.dbt.util import (
    build_metric_docs_url,
    build_model_docs_url,
    build_source_code_url,
    dataset_normalized_name,
    get_ownerships_from_meta,
    get_tags_from_meta,
    get_virtual_view_id,
    init_dataset,
    init_dbt_tests,
    init_documentation,
    init_field,
    init_field_doc,
    init_metric,
    init_virtual_view,
    to_dataset_entity_id,
)
from metaphor.models.metadata_change_event import (
    DataPlatform,
    Dataset,
    DbtMacro,
    DbtMacroArgument,
    DbtMaterialization,
    DbtMaterializationType,
    DbtMetric,
    DbtModel,
    DbtTest,
    Metric,
    MetricFilter,
    OwnershipAssignment,
    TagAssignment,
    VirtualView,
)

from .generated.dbt_manifest_v3 import CompiledModelNode as CompiledModelNodeV3
from .generated.dbt_manifest_v3 import CompiledSchemaTestNode as CompiledTestNodeV3
from .generated.dbt_manifest_v3 import DbtManifest as DbtManifestV3
from .generated.dbt_manifest_v3 import DependsOn as DependsOnV3
from .generated.dbt_manifest_v3 import ParsedMacro as ParsedMacroV3
from .generated.dbt_manifest_v3 import ParsedModelNode as ParsedModelNodeV3
from .generated.dbt_manifest_v3 import ParsedSchemaTestNode as ParsedTestNodeV3
from .generated.dbt_manifest_v3 import (
    ParsedSourceDefinition as ParsedSourceDefinitionV3,
)
from .generated.dbt_manifest_v5 import CompiledGenericTestNode as CompiledTestNodeV5
from .generated.dbt_manifest_v5 import CompiledModelNode as CompiledModelNodeV5
from .generated.dbt_manifest_v5 import DbtManifest as DbtManifestV5
from .generated.dbt_manifest_v5 import DependsOn as DependsOnV5
from .generated.dbt_manifest_v5 import ParsedGenericTestNode as ParsedTestNodeV5
from .generated.dbt_manifest_v5 import ParsedMacro as ParsedMacroV5
from .generated.dbt_manifest_v5 import ParsedMetric as ParsedMetricV5
from .generated.dbt_manifest_v5 import ParsedModelNode as ParsedModelNodeV5
from .generated.dbt_manifest_v5 import (
    ParsedSourceDefinition as ParsedSourceDefinitionV5,
)
from .generated.dbt_manifest_v6 import CompiledGenericTestNode as CompiledTestNodeV6
from .generated.dbt_manifest_v6 import CompiledModelNode as CompiledModelNodeV6
from .generated.dbt_manifest_v6 import DbtManifest as DbtManifestV6
from .generated.dbt_manifest_v6 import DependsOn as DependsOnV6
from .generated.dbt_manifest_v6 import ParsedGenericTestNode as ParsedTestNodeV6
from .generated.dbt_manifest_v6 import ParsedMacro as ParsedMacroV6
from .generated.dbt_manifest_v6 import ParsedMetric as ParsedMetricV6
from .generated.dbt_manifest_v6 import ParsedModelNode as ParsedModelNodeV6
from .generated.dbt_manifest_v6 import (
    ParsedSourceDefinition as ParsedSourceDefinitionV6,
)
from .generated.dbt_manifest_v7 import CompiledGenericTestNode as CompiledTestNodeV7
from .generated.dbt_manifest_v7 import CompiledModelNode as CompiledModelNodeV7
from .generated.dbt_manifest_v7 import DbtManifest as DbtManifestV7
from .generated.dbt_manifest_v7 import DependsOn as DependsOnV7
from .generated.dbt_manifest_v7 import ParsedGenericTestNode as ParsedTestNodeV7
from .generated.dbt_manifest_v7 import ParsedMacro as ParsedMacroV7
from .generated.dbt_manifest_v7 import ParsedMetric as ParsedMetricV7
from .generated.dbt_manifest_v7 import ParsedModelNode as ParsedModelNodeV7
from .generated.dbt_manifest_v7 import (
    ParsedSourceDefinition as ParsedSourceDefinitionV7,
)

logger = get_logger()


MODEL_NODE_TYPE = Union[
    CompiledModelNodeV3,
    CompiledModelNodeV5,
    CompiledModelNodeV6,
    CompiledModelNodeV7,
    ParsedModelNodeV3,
    ParsedModelNodeV5,
    ParsedModelNodeV6,
    ParsedModelNodeV7,
]

TEST_NODE_TYPE = Union[
    CompiledTestNodeV3,
    CompiledTestNodeV5,
    CompiledTestNodeV6,
    CompiledTestNodeV7,
    ParsedTestNodeV3,
    ParsedTestNodeV5,
    ParsedTestNodeV6,
    ParsedTestNodeV7,
]

PARSED_SOURCE_DEFINITION_TYPE = Union[
    ParsedSourceDefinitionV3,
    ParsedSourceDefinitionV5,
    ParsedSourceDefinitionV6,
    ParsedSourceDefinitionV7,
]

PARSED_SOURCE_DEFINITION_MAP = Union[
    Dict[str, ParsedSourceDefinitionV3],
    Dict[str, ParsedSourceDefinitionV5],
    Dict[str, ParsedSourceDefinitionV6],
    Dict[str, ParsedSourceDefinitionV7],
]

PARSED_METRIC_TYPE = Union[
    ParsedMetricV5,
    ParsedMetricV6,
    ParsedMetricV7,
]

DEPENDS_ON_TYPE = Union[
    DependsOnV3,
    DependsOnV5,
    DependsOnV6,
    DependsOnV7,
]

PARSED_MACRO_MAP = Union[
    Dict[str, ParsedMacroV3],
    Dict[str, ParsedMacroV5],
    Dict[str, ParsedMacroV6],
    Dict[str, ParsedMacroV7],
]

MANIFEST_CLASS_TYPE = Union[
    Type[DbtManifestV3],
    Type[DbtManifestV5],
    Type[DbtManifestV6],
    Type[DbtManifestV7],
]

# Maps dbt schema version to manifest class
dbt_version_manifest_class_map: Dict[str, MANIFEST_CLASS_TYPE] = {
    "v1": DbtManifestV3,
    "v2": DbtManifestV3,
    "v3": DbtManifestV3,
    "v4": DbtManifestV5,
    "v5": DbtManifestV5,
    "v6": DbtManifestV6,
    "v7": DbtManifestV7,
}


class ManifestParser:
    def __init__(
        self,
        config: DbtRunConfig,
        platform: DataPlatform,
        datasets: Dict[str, Dataset],
        virtual_views: Dict[str, VirtualView],
        metrics: Dict[str, Metric],
    ):
        self._platform = platform
        self._account = config.account
        self._docs_base_url = config.docs_base_url
        self._project_source_url = config.project_source_url
        self._meta_ownerships = config.meta_ownerships
        self._meta_tags = config.meta_tags
        self._datasets = datasets
        self._virtual_views = virtual_views
        self._metrics = metrics

    def parse(self, manifest_json: Dict) -> None:
        manifest_metadata = manifest_json.get("metadata", {})

        schema_version = (
            manifest_metadata.get("dbt_schema_version", "")
            .rsplit("/", 1)[-1]
            .split(".")[0]
        )
        logger.info(f"parsing manifest.json {schema_version} ...")

        dbt_manifest_class = dbt_version_manifest_class_map.get(schema_version)
        if dbt_manifest_class is None:
            raise ValueError(f"unsupported manifest schema '{schema_version}'")

        try:
            manifest = dbt_manifest_class.parse_obj(manifest_json)
        except Exception as e:
            logger.error(f"Parse manifest json error: {e}")
            raise e

        nodes = manifest.nodes
        sources = manifest.sources
        macros = manifest.macros

        metrics: Dict = {} if isinstance(manifest, DbtManifestV3) else manifest.metrics

        models = {
            k: v
            for (k, v) in nodes.items()
            if isinstance(
                v,
                (
                    CompiledModelNodeV3,
                    CompiledModelNodeV5,
                    CompiledModelNodeV6,
                    CompiledModelNodeV7,
                    ParsedModelNodeV3,
                    ParsedModelNodeV5,
                    ParsedModelNodeV6,
                    ParsedModelNodeV7,
                ),
            )
            # if upgraded to python 3.8+, can use get_args(MODEL_NODE_TYPE)
        }
        tests = {
            k: v
            for (k, v) in nodes.items()
            if isinstance(
                v,
                (
                    CompiledTestNodeV3,
                    CompiledTestNodeV5,
                    CompiledTestNodeV6,
                    CompiledTestNodeV7,
                    ParsedTestNodeV3,
                    ParsedTestNodeV5,
                    ParsedTestNodeV6,
                    ParsedTestNodeV7,
                ),
            )
            # if upgraded to python 3.8+, can use get_args(TEST_NODE_TYPE)
        }

        source_map = self._parse_sources(sources)

        macro_map = self._parse_macros(macros)

        # initialize all virtual views to be used in cross-references
        for _, model in models.items():
            init_virtual_view(self._virtual_views, model.unique_id)

        for _, model in models.items():
            self._parse_model(model, source_map, macro_map)

        for _, test in tests.items():
            self._parse_test(test)

        for _, metric in metrics.items():
            self._parse_metric(metric, source_map, macro_map)

    def _parse_test(self, test: TEST_NODE_TYPE) -> None:
        # check test is referring a model
        if test.depends_on is None or not test.depends_on.nodes:
            return

        model_unique_id = test.depends_on.nodes[0]
        if not model_unique_id.startswith("model."):
            return

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
        )

        # v7 changed from "compiled_sql" to "compiled_code"
        if isinstance(
            test, (CompiledTestNodeV3, CompiledTestNodeV5, CompiledTestNodeV6)
        ):
            dbt_test.sql = test.compiled_sql
        elif isinstance(test, CompiledTestNodeV7):
            dbt_test.sql = test.compiled_code

        init_dbt_tests(self._virtual_views, model_unique_id).append(dbt_test)

    def _parse_model(
        self,
        model: MODEL_NODE_TYPE,
        source_map: Dict[str, EntityId],
        macro_map: Dict[str, DbtMacro],
    ):
        if model.config is None or model.database is None:
            logger.warning("Skipping model without config or database")
            return

        virtual_view = init_virtual_view(self._virtual_views, model.unique_id)
        virtual_view.dbt_model = DbtModel(
            package_name=model.package_name,
            description=model.description or None,
            url=build_source_code_url(
                self._project_source_url, model.original_file_path
            ),
            docs_url=build_model_docs_url(self._docs_base_url, model.unique_id),
            tags=model.tags,
            fields=[],
        )
        dbt_model = virtual_view.dbt_model

        if isinstance(
            model, (CompiledModelNodeV3, CompiledModelNodeV5, CompiledModelNodeV6)
        ):
            virtual_view.dbt_model.raw_sql = model.raw_sql
            dbt_model.compiled_sql = model.compiled_sql
        elif isinstance(model, CompiledModelNodeV7):
            virtual_view.dbt_model.raw_sql = model.raw_code
            dbt_model.compiled_sql = model.compiled_code

        self._parse_model_meta(model)

        self._parse_model_materialization(model, dbt_model)

        self._parse_model_columns(model, dbt_model)

        (
            dbt_model.source_datasets,
            dbt_model.source_models,
            dbt_model.macros,
        ) = self._parse_depends_on(model.depends_on, source_map, macro_map)

    def _parse_macros(self, macros: PARSED_MACRO_MAP) -> Dict[str, DbtMacro]:
        macro_map: Dict[str, DbtMacro] = {}
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

        return macro_map

    def _parse_model_meta(self, model: MODEL_NODE_TYPE) -> None:
        if (
            model.config is None
            or model.config.materialized is None
            or model.config.materialized.upper() in ["EPHEMERAL", "OTHER"]
        ):
            return

        # v3 use 'model.config.meta' while v1, v2 use 'model.meta'
        meta = model.config.meta if model.config.meta else model.meta

        def get_dataset():
            return init_dataset(
                self._datasets,
                model.database,
                model.schema_,
                model.alias or model.name,
                self._platform,
                self._account,
                model.unique_id,
            )

        # Assign ownership & tags to materialized table/view
        ownerships = get_ownerships_from_meta(meta, self._meta_ownerships)
        if len(ownerships) > 0:
            get_dataset().ownership_assignment = OwnershipAssignment(
                ownerships=ownerships
            )

        tag_names = get_tags_from_meta(meta, self._meta_tags)
        if len(tag_names) > 0:
            get_dataset().tag_assignment = TagAssignment(tag_names=tag_names)

    def _parse_model_materialization(
        self, model: MODEL_NODE_TYPE, dbt_model: DbtModel
    ) -> None:
        if model.config is None:
            return

        materialized = model.config.materialized
        if materialized is None:
            return

        try:
            materialization_type = DbtMaterializationType[materialized.upper()]
        except KeyError:
            materialization_type = DbtMaterializationType.OTHER

        dbt_model.materialization = DbtMaterialization(
            type=materialization_type,
            target_dataset=str(
                to_dataset_entity_id(
                    dataset_normalized_name(
                        model.database, model.schema_, model.alias or model.name
                    ),
                    self._platform,
                    self._account,
                )
            ),
        )

    def _parse_model_columns(self, model: MODEL_NODE_TYPE, dbt_model: DbtModel) -> None:
        if model.columns is not None:
            for col in model.columns.values():
                column_name = col.name.lower()
                field = init_field(dbt_model.fields, column_name)
                field.description = col.description
                field.native_type = col.data_type or "Not Set"

    def _parse_sources(
        self, sources: PARSED_SOURCE_DEFINITION_MAP
    ) -> Dict[str, EntityId]:
        source_map: Dict[str, EntityId] = {}
        for key, source in sources.items():
            assert source.database is not None
            source_map[key] = to_dataset_entity_id(
                dataset_normalized_name(
                    source.database, source.schema_, source.identifier
                ),
                self._platform,
                self._account,
            )

            self._parse_source(source)

        return source_map

    def _parse_source(self, source: PARSED_SOURCE_DEFINITION_TYPE) -> None:
        if not source.database or not source.columns:
            return

        dataset = init_dataset(
            self._datasets,
            source.database,
            source.schema_,
            source.identifier,
            self._platform,
            self._account,
            source.unique_id,
        )

        init_documentation(dataset)
        if source.description:
            dataset.documentation.dataset_documentations = [source.description]

        for col in source.columns.values():
            if col.description:
                column_name = col.name.lower()
                field_doc = init_field_doc(dataset, column_name)
                field_doc.documentation = col.description

    def _parse_depends_on(
        self,
        depends_on: Optional[DEPENDS_ON_TYPE],
        source_map: Dict[str, EntityId],
        macro_map: Dict[str, DbtMacro],
    ) -> Tuple[Optional[List], Optional[List], Optional[List]]:
        datasets, models, macros = None, None, None
        if depends_on is None:
            return datasets, models, macros

        if depends_on.nodes:
            datasets = unique_list(
                [
                    str(source_map[n])
                    for n in depends_on.nodes
                    if n.startswith("source.")
                ]
            )

            models = unique_list(
                [
                    get_virtual_view_id(self._virtual_views[n].logical_id)
                    for n in depends_on.nodes
                    if n.startswith("model.")
                ]
            )

        if depends_on.macros:
            macros = [macro_map[n] for n in depends_on.macros]

        return datasets, models, macros

    def _parse_metric(
        self,
        metric: PARSED_METRIC_TYPE,
        source_map: Dict[str, EntityId],
        macro_map: Dict[str, DbtMacro],
    ) -> None:
        metric_entity = init_metric(self._metrics, metric.unique_id)
        metric_entity.dbt_metric = DbtMetric(
            package_name=metric.package_name,
            description=metric.description or None,
            label=metric.label,
            tags=metric.tags,
            timestamp=metric.timestamp,
            time_grains=metric.time_grains,
            dimensions=metric.dimensions,
            filters=[
                MetricFilter(field=f.field, operator=f.operator, value=f.value)
                for f in metric.filters
            ],
            url=build_metric_docs_url(self._docs_base_url, metric.unique_id),
        )

        if isinstance(metric, (ParsedMetricV5, ParsedMetricV6)):
            metric_entity.dbt_metric.sql = metric.sql
            metric_entity.dbt_metric.type = metric.type
        elif isinstance(metric, ParsedMetricV7):
            metric_entity.dbt_metric.sql = metric.expression
            metric_entity.dbt_metric.type = metric.calculation_method

        dbt_metric = metric_entity.dbt_metric
        (
            dbt_metric.source_datasets,
            dbt_metric.source_models,
            _,
        ) = self._parse_depends_on(metric.depends_on, source_map, macro_map)
