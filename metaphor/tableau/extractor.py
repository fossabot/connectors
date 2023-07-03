import base64
import re
import traceback
from typing import Collection, Dict, List, Optional, Set, Union

try:
    import tableauserverclient as tableau
except ImportError:
    print("Please install metaphor[tableau] extra\n")
    raise
from sqllineage.runner import LineageRunner

from metaphor.common.base_extractor import BaseExtractor
from metaphor.common.entity_id import (
    EntityId,
    to_dataset_entity_id,
    to_dataset_entity_id_from_logical_id,
    to_virtual_view_entity_id,
)
from metaphor.common.event_util import ENTITY_TYPES
from metaphor.common.logger import get_logger, json_dump_to_debug_file
from metaphor.models.crawler_run_metadata import Platform
from metaphor.models.metadata_change_event import (
    Chart,
    Dashboard,
    DashboardInfo,
    DashboardLogicalID,
    DashboardPlatform,
    DashboardUpstream,
    DataPlatform,
    Dataset,
    DatasetLogicalID,
    SourceInfo,
    TableauDatasource,
    TableauField,
    VirtualView,
    VirtualViewLogicalID,
    VirtualViewType,
)
from metaphor.tableau.config import TableauRunConfig
from metaphor.tableau.graphql_utils import paginate_connection
from metaphor.tableau.query import (
    CustomSqlTable,
    DatabaseTable,
    WorkbookQueryResponse,
    connection_type_map,
    custom_sql_graphql_query,
    workbooks_graphql_query,
)

logger = get_logger()


class TableauExtractor(BaseExtractor):
    """Tableau metadata extractor"""

    @staticmethod
    def from_config_file(config_file: str) -> "TableauExtractor":
        return TableauExtractor(TableauRunConfig.from_yaml_file(config_file))

    @staticmethod
    def _build_base_url(server_url: str, site_name: str) -> str:
        return f"{server_url}/#/site/{site_name}" if site_name else f"{server_url}/#"

    def __init__(self, config: TableauRunConfig):
        super().__init__(config, "Tableau metadata crawler", Platform.TABLEAU)
        self._server_url = config.server_url
        self._site_name = config.site_name
        self._access_token = config.access_token
        self._user_password = config.user_password
        self._snowflake_account = config.snowflake_account
        self._bigquery_project_name_to_id_map = config.bigquery_project_name_to_id_map
        self._disable_preview_image = config.disable_preview_image

        self._views: Dict[str, tableau.ViewItem] = {}
        self._projects: Dict[str, str] = {}
        self._datasets: Dict[EntityId, Dataset] = {}
        self._virtual_views: Dict[str, VirtualView] = {}
        self._dashboards: Dict[str, Dashboard] = {}

        # The base URL for dashboards, data sources, etc.
        # Use alternative_base_url if provided, otherwise, use server_url as the base
        self._base_url = TableauExtractor._build_base_url(
            config.alternative_base_url or self._server_url, self._site_name
        )

    async def extract(self) -> Collection[ENTITY_TYPES]:
        logger.info("Fetching metadata from Tableau")

        tableau_auth: Union[tableau.PersonalAccessTokenAuth, tableau.TableauAuth]
        if self._access_token is not None:
            tableau_auth = tableau.PersonalAccessTokenAuth(
                self._access_token.token_name,
                self._access_token.token_value,
                self._site_name,
            )
        elif self._user_password is not None:
            tableau_auth = tableau.TableauAuth(
                self._user_password.username,
                self._user_password.password,
                self._site_name,
            )
        else:
            raise Exception(
                "Must provide either access token or user password in config"
            )

        server = tableau.Server(self._server_url, use_server_version=True)
        with server.auth.sign_in(tableau_auth):
            self._extract_dashboards(server)
            self._extract_datasources(server)

        return [
            *self._dashboards.values(),
            *self._virtual_views.values(),
            *self._datasets.values(),
        ]

    def _extract_dashboards(self, server: tableau.Server) -> None:
        # fetch all projects
        projects: List[tableau.ProjectItem] = list(tableau.Pager(server.projects))
        json_dump_to_debug_file([w.__dict__ for w in projects], "projects.json")
        logger.info(
            f"\nThere are {len(projects)} projects on site: {[project.name for project in projects]}"
        )
        self._parse_project_names(projects)

        # fetch all views, with preview image
        views: List[tableau.ViewItem] = list(tableau.Pager(server.views, usage=True))
        json_dump_to_debug_file([v.__dict__ for v in views], "views.json")
        logger.info(
            f"There are {len(views)} views on site: {[view.name for view in views]}\n"
        )
        for view in views:
            if not self._disable_preview_image:
                server.views.populate_preview_image(view)
            if not view.id:
                logger.exception(f"view {view.name} missing id")
                continue
            self._views[view.id] = view

        # fetch all workbooks
        workbooks: List[tableau.WorkbookItem] = list(tableau.Pager(server.workbooks))
        json_dump_to_debug_file([w.__dict__ for w in workbooks], "workbooks.json")
        logger.info(
            f"\nThere are {len(workbooks)} workbooks on site: {[workbook.name for workbook in workbooks]}"
        )
        for workbook in workbooks:
            server.workbooks.populate_views(workbook, usage=True)

            try:
                self._parse_dashboard(workbook)
            except Exception as error:
                traceback.print_exc()
                logger.error(f"failed to parse workbook {workbook.name}, error {error}")

    def _extract_datasources(self, server: tableau.Server) -> None:
        # fetch custom SQL tables from Metadata GraphQL API
        custom_sql_tables = paginate_connection(
            server, custom_sql_graphql_query, "customSQLTablesConnection"
        )

        json_dump_to_debug_file(custom_sql_tables, "graphql_custom_sql_tables.json")
        logger.info(f"Found {len(custom_sql_tables)} custom SQL tables.")

        datasource_upstream_datasets = {}
        for item in custom_sql_tables:
            custom_sql_table = CustomSqlTable.parse_obj(item)
            datasource_upstream_datasets.update(
                self._parse_custom_sql_table(custom_sql_table)
            )

        # fetch workbook related info from Metadata GraphQL API
        workbooks = paginate_connection(
            server, workbooks_graphql_query, "workbooksConnection"
        )
        json_dump_to_debug_file(workbooks, "graphql_workbooks.json")
        logger.info(f"Found {len(workbooks)} workbooks.")

        for item in workbooks:
            try:
                workbook = WorkbookQueryResponse.parse_obj(item)
                self._parse_workbook_query_response(
                    workbook, datasource_upstream_datasets
                )
            except Exception as error:
                logger.exception(
                    f"failed to parse workbook {item['vizportalUrlId']}, error {error}"
                )

    def _parse_project_names(self, projects: List[tableau.ProjectItem]) -> None:
        for project in projects:
            if project.id:
                self._projects[project.id] = project.name

        # second iteration to link child to parent project
        for project in projects:
            if project.id and project.parent_id in self._projects:
                parent_name = self._projects[project.parent_id]
                self._projects[project.id] = f"{parent_name}.{project.name}"

    def _parse_dashboard(self, workbook: tableau.WorkbookItem) -> None:
        if not workbook.webpage_url:
            logger.exception(f"workbook {workbook.name} missing webpage_url")
            return

        workbook_id = TableauExtractor._extract_workbook_id(workbook.webpage_url)
        project_name = (
            self._projects.get(workbook.project_id or "", None) or workbook.project_name
        )

        views: List[tableau.ViewItem] = workbook.views
        charts = [self._parse_chart(self._views[view.id]) for view in views if view.id]
        total_views = sum([view.total_views for view in views])

        dashboard_info = DashboardInfo(
            title=f"{project_name}.{workbook.name}",
            description=workbook.description,
            charts=charts,
            view_count=float(total_views),
        )

        source_info = SourceInfo(
            main_url=f"{self._base_url}/workbooks/{workbook_id}",
        )

        dashboard = Dashboard(
            logical_id=DashboardLogicalID(
                dashboard_id=workbook_id, platform=DashboardPlatform.TABLEAU
            ),
            dashboard_info=dashboard_info,
            source_info=source_info,
        )

        self._dashboards[workbook_id] = dashboard

    def _parse_custom_sql_table(
        self, custom_sql_table: CustomSqlTable
    ) -> Dict[str, List[str]]:
        platform = connection_type_map.get(custom_sql_table.connectionType)
        if platform is None:
            logger.warn(
                f"Unsupported connection type {custom_sql_table.connectionType} for custom sql table: {custom_sql_table.id}"
            )
            return {}

        account = (
            self._snowflake_account if platform == DataPlatform.SNOWFLAKE else None
        )

        datasource_ids = self._custom_sql_datasource_ids(custom_sql_table)
        if len(datasource_ids) == 0:
            logger.warn(
                f"Missing datasource IDs for custom sql table: {custom_sql_table.id}"
            )
            return {}

        try:
            parser = LineageRunner(custom_sql_table.query)
            source_tables = parser.source_tables
        except Exception as e:
            logger.error(f"Unable to parse custom query for {custom_sql_table.id}: {e}")
            return {}

        if len(source_tables) == 0:
            logger.error(
                f"Unable to extract source tables from custom query for {custom_sql_table.id}"
            )
            return {}

        upstream_datasets = []
        for source_table in source_tables:
            fullname = str(source_table).lower()
            if fullname.count(".") != 2:
                logger.warn(f"Ignore non-fully qualified source table {fullname}")
                continue

            self._init_dataset(fullname, platform, account)
            upstream_datasets.append(
                str(to_dataset_entity_id(fullname, platform, account))
            )

        datasource_upstream_datasets = {}
        for datasource_id in datasource_ids:
            datasource_upstream_datasets[datasource_id] = upstream_datasets

        return datasource_upstream_datasets

    def _custom_sql_datasource_ids(self, custom_sql_table: CustomSqlTable) -> Set[str]:
        datasource_ids = set()
        for column in custom_sql_table.columnsConnection.nodes:
            for field in column.referencedByFields:
                datasource_ids.add(field.datasource.id)

        return datasource_ids

    def _parse_workbook_query_response(
        self,
        workbook: WorkbookQueryResponse,
        datasource_upstream_datasets: Dict[str, List[str]],
    ) -> None:
        dashboard = self._dashboards[workbook.vizportalUrlId]
        source_virtual_views: List[str] = []
        published_datasources: List[str] = []

        project_name = (
            self._projects.get(workbook.projectLuid or "", None) or workbook.projectName
        )

        for published_source in workbook.upstreamDatasources:
            virtual_view_id = str(
                to_virtual_view_entity_id(
                    published_source.luid, VirtualViewType.TABLEAU_DATASOURCE
                )
            )
            if published_source.luid in self._virtual_views:
                # data source already parsed
                source_virtual_views.append(virtual_view_id)
                published_datasources.append(published_source.name)
                continue

            # Use the upstream datasets parsed from custom SQL if available
            source_datasets = datasource_upstream_datasets.get(
                published_source.id,
                self._parse_upstream_datasets(published_source.upstreamTables),
            )

            self._virtual_views[published_source.luid] = VirtualView(
                logical_id=VirtualViewLogicalID(
                    type=VirtualViewType.TABLEAU_DATASOURCE, name=published_source.luid
                ),
                tableau_datasource=TableauDatasource(
                    name=f"{project_name}.{published_source.name}",
                    description=published_source.description or None,
                    fields=[
                        TableauField(field=f.name, description=f.description or None)
                        for f in published_source.fields
                    ],
                    embedded=False,
                    url=f"{self._base_url}/datasources/{published_source.vizportalUrlId}",
                    source_datasets=source_datasets or None,
                ),
            )
            source_virtual_views.append(virtual_view_id)
            published_datasources.append(published_source.name)

        for embedded_source in workbook.embeddedDatasources:
            if embedded_source.name in published_datasources:
                logger.debug(
                    f"Skip embedded datasource {embedded_source.name} since it's published"
                )
                continue

            virtual_view_id = str(
                to_virtual_view_entity_id(
                    embedded_source.id, VirtualViewType.TABLEAU_DATASOURCE
                )
            )

            # Use the upstream datasets parsed from custom SQL if available
            source_datasets = datasource_upstream_datasets.get(
                embedded_source.id,
                self._parse_upstream_datasets(embedded_source.upstreamTables),
            )

            self._virtual_views[embedded_source.id] = VirtualView(
                logical_id=VirtualViewLogicalID(
                    type=VirtualViewType.TABLEAU_DATASOURCE, name=embedded_source.id
                ),
                tableau_datasource=TableauDatasource(
                    name=f"{workbook.projectName}.{embedded_source.name}",
                    fields=[
                        TableauField(field=f.name, description=f.description or None)
                        for f in embedded_source.fields
                    ],
                    embedded=True,
                    source_datasets=source_datasets or None,
                ),
            )
            source_virtual_views.append(virtual_view_id)

        dashboard.upstream = DashboardUpstream(
            source_virtual_views=source_virtual_views
        )

    def _parse_upstream_datasets(
        self, upstreamTables: List[DatabaseTable]
    ) -> List[str]:
        upstream_datasets = [self._parse_dataset_id(table) for table in upstreamTables]
        return list(
            set(
                [
                    str(dataset_id)
                    for dataset_id in upstream_datasets
                    if dataset_id is not None
                ]
            )
        )

    def _parse_dataset_id(self, table: DatabaseTable) -> Optional[EntityId]:
        if (
            not table.name
            or not table.schema_
            or not table.fullName
            or not table.database
        ):
            return None

        database_name = table.database.name
        connection_type = table.database.connectionType
        if connection_type not in connection_type_map:
            # connection type not supported
            return None

        platform = connection_type_map[connection_type]

        # if table fullname contains three segments, use it as dataset name
        if table.fullName.count(".") == 2:
            fullname = table.fullName
        else:
            # use BigQuery project ID to replace project name, to be consistent with the BigQuery crawler
            if platform == DataPlatform.BIGQUERY:
                if database_name in self._bigquery_project_name_to_id_map:
                    database_name = self._bigquery_project_name_to_id_map[database_name]
                else:
                    # use project name as database name, may not match with BigQuery crawler
                    logger.warning(
                        f"BigQuery project name {database_name} not defined in config 'bigquery_project_name_to_id_map'"
                    )

            # if table name has two segments, then it contains "schema" and "table_name"
            if "." in table.name:
                fullname = f"{database_name}.{table.name}"
            else:
                fullname = f"{database_name}.{table.schema_}.{table.name}"

        fullname = (
            fullname.replace("[", "")
            .replace("]", "")
            .replace("`", "")
            .replace("'", "")
            .replace('"', "")
            .lower()
        )

        account = (
            self._snowflake_account if platform == DataPlatform.SNOWFLAKE else None
        )

        logger.debug(f"dataset id: {fullname} {connection_type} {account}")
        self._init_dataset(fullname, platform, account)
        return to_dataset_entity_id(fullname, platform, account)

    def _parse_chart(self, view: tableau.ViewItem) -> Chart:
        # encode preview image raw bytes into data URL
        preview_data_url = None
        try:
            preview_data_url = (
                TableauExtractor._build_preview_data_url(view.preview_image)
                if not self._disable_preview_image and view.preview_image
                else None
            )
        except Exception as error:
            logger.error(
                f"Failed to build preview data URL for {view.name}, error {error}"
            )

        view_url = self._build_view_url(view.content_url)

        return Chart(title=view.name, url=view_url, preview=preview_data_url)

    _workbook_url_regex = r".+\/workbooks\/(\d+)(\/.*)?"

    def _init_dataset(
        self,
        normalized_name: str,
        platform: DataPlatform,
        account: Optional[str],
    ) -> Dataset:
        dataset = Dataset()
        dataset.logical_id = DatasetLogicalID(
            name=normalized_name, account=account, platform=platform
        )
        entity_id = to_dataset_entity_id_from_logical_id(dataset.logical_id)
        return self._datasets.setdefault(entity_id, dataset)

    @staticmethod
    def _extract_workbook_id(workbook_url: str) -> str:
        """Extracts the workbook ID from a workbook URL"""
        match = re.search(TableauExtractor._workbook_url_regex, workbook_url)
        assert match, f"invalid workbook URL {workbook_url}"

        return match.group(1)

    def _build_view_url(self, content_url: Optional[str]) -> Optional[str]:
        """
        Builds view URL from the API content_url field.
        content_url is in the form of <workbook>/sheets/<view>, e.g. 'Superstore/sheets/WhatIfForecast'
        """
        if not content_url:
            return None

        workbook, _, view = content_url.split("/")

        return f"{self._base_url}/views/{workbook}/{view}"

    @staticmethod
    def _build_preview_data_url(preview: bytes) -> str:
        return f"data:image/png;base64,{base64.b64encode(preview).decode('ascii')}"
