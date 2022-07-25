import json
import re
import tempfile
from time import sleep
from typing import Any, Callable, Collection, Dict, List, Optional, Type, TypeVar

import requests
from metaphor.models.crawler_run_metadata import Platform
from metaphor.models.metadata_change_event import (
    Chart,
    ChartType,
    Dashboard,
    DashboardInfo,
    DashboardLogicalID,
    DashboardPlatform,
    DashboardUpstream,
    DataPlatform,
    EntityType,
)
from metaphor.models.metadata_change_event import PowerBIApp as PbiApp
from metaphor.models.metadata_change_event import PowerBIColumn as PbiColumn
from metaphor.models.metadata_change_event import PowerBIDashboardType
from metaphor.models.metadata_change_event import (
    PowerBIDataset as VirtualViewPowerBIDataset,
)
from metaphor.models.metadata_change_event import PowerBIDatasetTable, PowerBIInfo
from metaphor.models.metadata_change_event import PowerBIMeasure as PbiMeasure
from metaphor.models.metadata_change_event import PowerBIWorkspace as PbiWorkspace
from metaphor.models.metadata_change_event import (
    SourceInfo,
    VirtualView,
    VirtualViewLogicalID,
    VirtualViewType,
)
from pydantic import BaseModel, parse_obj_as

from metaphor.common.entity_id import EntityId, dataset_fullname, to_dataset_entity_id
from metaphor.common.event_util import ENTITY_TYPES
from metaphor.common.extractor import BaseExtractor
from metaphor.common.logger import get_logger
from metaphor.common.utils import chunks, unique_list
from metaphor.power_bi.config import PowerBIRunConfig
from metaphor.power_bi.power_query_parser import PowerQueryParser

try:
    import msal
except ImportError:
    print("Please install metaphor[power_bi] extra\n")
    raise


logger = get_logger(__name__)


class PowerBIApp(BaseModel):
    id: str
    name: str
    workspaceId: str


class PowerBIDataSource(BaseModel):
    datasourceType: str
    datasourceId: str
    connectionDetails: Any
    gatewayId: str


class PowerBIDataset(BaseModel):
    id: str
    name: str
    webUrl: Optional[str]


class PowerBIDashboard(BaseModel):
    id: str
    displayName: str
    webUrl: Optional[str]


class PowerBIWorkspace(BaseModel):
    id: str
    name: str
    isReadOnly: bool
    type: str


class PowerBIReport(BaseModel):
    id: str
    name: str
    datasetId: Optional[str] = None
    reportType: str
    webUrl: Optional[str]


class PowerBITile(BaseModel):
    id: str
    title: str = ""
    datasetId: str = ""
    reportId: str = ""
    embedUrl: Optional[str]


class PowerBITableColumn(BaseModel):
    name: str
    datatype: str = "unknown"


class PowerBITableMeasure(BaseModel):
    name: str
    expression: str = ""


class PowerBITable(BaseModel):
    name: str
    columns: List[PowerBITableColumn] = []
    measures: List[PowerBITableMeasure] = []
    source: List[Any] = []


class WorkspaceInfoDataset(BaseModel):
    id: str
    name: str
    tables: List[PowerBITable] = []

    description: str = ""
    ContentProviderType: str = ""
    CreatedDate: str = ""

    upstreamDataflows: Any
    upstreamDatasets: Any


class WorkspaceInfoDashboard(BaseModel):
    id: str
    appId: Optional[str] = None
    displayName: str


class WorkspaceInfoReport(BaseModel):
    id: str
    appId: Optional[str] = None
    name: str
    datasetId: Optional[str] = None
    description: str = ""


class WorkspaceInfo(BaseModel):
    id: str
    name: str
    type: str
    state: str
    reports: List[WorkspaceInfoReport] = []
    datasets: List[WorkspaceInfoDataset] = []
    dashboards: List[WorkspaceInfoDashboard] = []


class PowerBIClient:
    AUTHORITY = "https://login.microsoftonline.com/{tenant_id}"
    SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]
    API_ENDPOINT = "https://api.powerbi.com/v1.0/myorg"

    # Only include active workspaces. Ignore personal workspaces & legacy workspaces.
    GROUPS_FILTER = "state eq 'Active' and type eq 'Workspace'"

    # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-post-workspace-info#request-body
    MAX_WORKSPACES_PER_SCAN = 100

    def __init__(self, config: PowerBIRunConfig):
        self._headers = {"Authorization": self.retrieve_access_token(config)}

    def retrieve_access_token(self, config: PowerBIRunConfig) -> str:
        app = msal.ConfidentialClientApplication(
            config.client_id,
            authority=self.AUTHORITY.format(tenant_id=config.tenant_id),
            client_credential=config.secret,
        )
        token = None
        token = app.acquire_token_silent(self.SCOPES, account=None)
        if not token:
            logger.info(
                "No suitable token exists in cache. Let's get a new one from AAD."
            )
            token = app.acquire_token_for_client(scopes=self.SCOPES)

        return f"Bearer {token['access_token']}"

    def get_groups(self) -> List[PowerBIWorkspace]:
        # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/groups-get-groups-as-admin
        url = f"{self.API_ENDPOINT}/admin/groups?$top=5000&$filter={PowerBIClient.GROUPS_FILTER}"
        return self._call_get(
            url, List[PowerBIWorkspace], transform_response=lambda r: r.json()["value"]
        )

    def get_apps(self) -> List[PowerBIApp]:
        # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/apps-get-apps-as-admin
        url = f"{self.API_ENDPOINT}/admin/apps?$top=5000"
        return self._call_get(
            url, List[PowerBIApp], transform_response=lambda r: r.json()["value"]
        )

    def get_tiles(self, dashboard_id: str) -> List[PowerBITile]:
        # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/dashboards-get-tiles-as-admin
        url = f"{self.API_ENDPOINT}/admin/dashboards/{dashboard_id}/tiles"
        return self._call_get(
            url, List[PowerBITile], transform_response=lambda r: r.json()["value"]
        )

    def get_datasets(self, group_id: str) -> List[PowerBIDataset]:
        # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/datasets-get-datasets-in-group-as-admin
        url = f"{self.API_ENDPOINT}/admin/groups/{group_id}/datasets"
        return self._call_get(
            url, List[PowerBIDataset], transform_response=lambda r: r.json()["value"]
        )

    def get_dashboards(self, group_id: str) -> List[PowerBIDashboard]:
        # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/dashboards-get-dashboards-in-group-as-admin
        url = f"{self.API_ENDPOINT}/admin/groups/{group_id}/dashboards"
        return self._call_get(
            url, List[PowerBIDashboard], transform_response=lambda r: r.json()["value"]
        )

    def get_reports(self, group_id: str) -> List[PowerBIReport]:
        # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/reports-get-reports-in-group-as-admin
        url = f"{self.API_ENDPOINT}/admin/groups/{group_id}/reports"
        return self._call_get(
            url, List[PowerBIReport], transform_response=lambda r: r.json()["value"]
        )

    def get_workspace_info(self, workspace_ids: List[str]) -> List[WorkspaceInfo]:
        def create_scan() -> str:
            # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-post-workspace-info
            url = f"{self.API_ENDPOINT}/admin/workspaces/getInfo"
            request_body = {"workspaces": workspace_ids}
            result = requests.post(
                url,
                headers=self._headers,
                params={
                    "datasetExpressions": True,
                    "datasetSchema": True,
                    "datasourceDetails": True,
                    "getArtifactUsers": True,
                    "lineage": True,
                },
                data=request_body,
            )

            assert result.status_code == 202, (
                "Workspace scan create failed, "
                f"workspace_ids: {workspace_ids}, "
                f"response: [{result.status_code}] {result.content.decode()}"
            )

            scan_id = result.json()["id"]
            logger.info(f"Create a scan, id: {scan_id}")

            return result.json()["id"]

        def wait_for_scan_result(scan_id: str, max_timeout_in_secs: int = 30) -> bool:
            # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-scan-status
            url = f"{self.API_ENDPOINT}/admin/workspaces/scanStatus/{scan_id}"

            waiting_time = 0
            sleep_time = 1
            while True:
                result = requests.get(url, headers=self._headers)
                if result.status_code != 200:
                    return False
                if result.json()["status"] == "Succeeded":
                    return True
                if waiting_time >= max_timeout_in_secs:
                    break
                waiting_time += sleep_time
                logger.info(f"Sleep {sleep_time} sec, wait for scan_id: {scan_id}")
                sleep(sleep_time)
            return False

        def transform_scan_result(response: requests.Response) -> dict:
            # Write output to file to help debug issues
            fd, name = tempfile.mkstemp(suffix=".json")
            with open(fd, "w") as fp:
                fp.write(response.text)
            logger.info(f"Scan result written to {name}")

            return response.json()["workspaces"]

        scan_id = create_scan()
        scan_success = wait_for_scan_result(scan_id)
        assert scan_success, f"Workspace scan failed, scan_id: {scan_id}"

        # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-scan-result
        url = f"{self.API_ENDPOINT}/admin/workspaces/scanResult/{scan_id}"
        return self._call_get(
            url,
            List[WorkspaceInfo],
            transform_response=transform_scan_result,
        )

    T = TypeVar("T")

    def _call_get(
        self,
        url: str,
        type_: Type[T],
        transform_response: Callable[[requests.Response], Any] = lambda r: r.json(),
    ) -> T:
        result = requests.get(url, headers=self._headers)
        assert (
            result.status_code != 401
        ), "Authentication error. Please enable read-only Power BI admin API access for the app."

        assert result.status_code == 200, f"GET {url} failed, {result.content.decode()}"

        logger.debug(f"Response from {url}:")
        logger.debug(json.dumps(result.json(), indent=2))
        return parse_obj_as(type_, transform_response(result))


class PowerBIExtractor(BaseExtractor):
    """Power BI metadata extractor"""

    def platform(self) -> Optional[Platform]:
        return Platform.POWER_BI

    def description(self) -> str:
        return "Power BI metadata crawler"

    @staticmethod
    def config_class():
        return PowerBIRunConfig

    def __init__(self):
        self._dashboards: Dict[str, Dashboard] = {}
        self._virtual_views: Dict[str, VirtualView] = {}

    async def extract(self, config: PowerBIRunConfig) -> Collection[ENTITY_TYPES]:
        assert isinstance(config, PowerBIExtractor.config_class())
        logger.info(f"Fetching metadata from Power BI tenant ID: {config.tenant_id}")

        self.client = PowerBIClient(config)

        if len(config.workspaces) == 0:
            config.workspaces = [w.id for w in self.client.get_groups()]

        logger.info(f"Process {len(config.workspaces)} workspaces: {config.workspaces}")

        apps = self.client.get_apps()
        app_map = {app.id: app for app in apps}

        for workspace_ids in chunks(
            config.workspaces, PowerBIClient.MAX_WORKSPACES_PER_SCAN
        ):
            for workspace in self.client.get_workspace_info(workspace_ids):
                logger.info(
                    f"Fetching metadata from Power BI workspace ID: {workspace.id}"
                )

                try:
                    self.map_wi_datasets_to_virtual_views(workspace)
                    self.map_wi_reports_to_dashboard(workspace, app_map)
                    self.map_wi_dashboards_to_dashboard(workspace, app_map)
                except Exception as e:
                    logger.exception(e)

        entities: List[ENTITY_TYPES] = []
        entities.extend(self._virtual_views.values())
        entities.extend(self._dashboards.values())

        return entities

    def map_wi_datasets_to_virtual_views(self, workspace: WorkspaceInfo) -> None:

        dataset_map = {d.id: d for d in self.client.get_datasets(workspace.id)}

        for wds in workspace.datasets:
            sources = []
            tables = []
            for table in wds.tables:
                tables.append(
                    PowerBIDatasetTable(
                        columns=[
                            PbiColumn(field=c.name, type=c.datatype)
                            for c in table.columns
                        ],
                        measures=[
                            PbiMeasure(field=m.name, expression=m.expression)
                            for m in table.measures
                        ],
                        name=table.name,
                    )
                )

                for source in table.source:
                    sources.append(source["expression"])

            source_datasets = [
                str(dataset)
                for source in sources
                for dataset in PowerQueryParser.parse_source_datasets(source)
            ]

            ds = dataset_map.get(wds.id, None)
            if ds is None:
                logger.warn(f"Skipping invalid dataset {wds.id}")
                continue

            virtual_view = VirtualView(
                logical_id=VirtualViewLogicalID(
                    name=wds.id, type=VirtualViewType.POWER_BI_DATASET
                ),
                power_bi_dataset=VirtualViewPowerBIDataset(
                    tables=tables,
                    name=wds.name,
                    url=ds.webUrl,
                    source_datasets=unique_list(source_datasets),
                    description=wds.description,
                ),
            )

            self._virtual_views[wds.id] = virtual_view

    def map_wi_reports_to_dashboard(
        self, workspace: WorkspaceInfo, app_map: Dict[str, PowerBIApp]
    ) -> None:

        report_map = {r.id: r for r in self.client.get_reports(workspace.id)}

        for wi_report in workspace.reports:
            if wi_report.datasetId is None:
                logger.warn(f"Skipping report without datasetId: {wi_report.id}")
                continue

            upstream_id = str(
                EntityId(
                    EntityType.VIRTUAL_VIEW,
                    self._virtual_views[wi_report.datasetId].logical_id,
                )
            )

            report = report_map.get(wi_report.id, None)
            if report is None:
                logger.warn(f"Skipping invalid report {wi_report.id}")
                continue

            pbi_info = self._make_power_bi_info(
                PowerBIDashboardType.REPORT, workspace, wi_report.appId, app_map
            )

            dashboard = Dashboard(
                logical_id=DashboardLogicalID(
                    dashboard_id=wi_report.id,
                    platform=DashboardPlatform.POWER_BI,
                ),
                dashboard_info=DashboardInfo(
                    description=wi_report.description,
                    title=wi_report.name,
                    power_bi=pbi_info,
                ),
                source_info=SourceInfo(
                    main_url=report.webUrl,
                ),
                upstream=DashboardUpstream(source_virtual_views=[upstream_id]),
            )
            self._dashboards[wi_report.id] = dashboard

    def map_wi_dashboards_to_dashboard(
        self, workspace: WorkspaceInfo, app_map: Dict[str, PowerBIApp]
    ) -> None:

        dashboard_map = {d.id: d for d in self.client.get_dashboards(workspace.id)}

        for wi_dashboard in workspace.dashboards:
            tiles = self.client.get_tiles(wi_dashboard.id)
            upstream = []
            for tile in tiles:
                dataset_id = tile.datasetId

                # skip tile not depends on a dataset
                if dataset_id == "":
                    continue

                upstream.append(
                    str(
                        EntityId(
                            EntityType.VIRTUAL_VIEW,
                            self._virtual_views[dataset_id].logical_id,
                        )
                    )
                )

            pbi_dashboard = dashboard_map.get(wi_dashboard.id, None)
            if pbi_dashboard is None:
                logger.warn(f"Skipping invalid dashboard {wi_dashboard.id}")
                continue

            pbi_info = self._make_power_bi_info(
                PowerBIDashboardType.DASHBOARD, workspace, wi_dashboard.appId, app_map
            )

            dashboard = Dashboard(
                logical_id=DashboardLogicalID(
                    dashboard_id=wi_dashboard.id,
                    platform=DashboardPlatform.POWER_BI,
                ),
                dashboard_info=DashboardInfo(
                    title=wi_dashboard.displayName,
                    charts=self.transform_tiles_to_charts(tiles),
                    power_bi=pbi_info,
                ),
                source_info=SourceInfo(
                    main_url=pbi_dashboard.webUrl,
                ),
                upstream=DashboardUpstream(source_virtual_views=unique_list(upstream)),
            )
            self._dashboards[wi_dashboard.id] = dashboard

    def _make_power_bi_info(
        self,
        type: PowerBIDashboardType,
        workspace: WorkspaceInfo,
        app_id: Optional[str],
        app_map: Dict[str, PowerBIApp],
    ) -> PowerBIInfo:
        pbi_info = PowerBIInfo(
            power_bi_dashboard_type=type,
            workspace=PbiWorkspace(id=workspace.id, name=workspace.name),
        )

        if app_id is not None:
            app = app_map.get(app_id)
            if app is not None:
                pbi_info.app = PbiApp(id=app.id, name=app.name)

        return pbi_info

    @staticmethod
    def parse_power_query(expression: str) -> EntityId:
        lines = expression.split("\n")
        platform_pattern = re.compile(r"Source = (\w+).")
        match = platform_pattern.search(lines[1])
        assert match, "Can't parse platform from power query expression."
        platform_str = match.group(1)

        field_pattern = re.compile(r'{\[Name="([\w\-]+)"(.*)\]}')

        def get_field(text: str) -> str:
            match = field_pattern.search(text)
            assert match, "Can't parse field from power query expression"
            return match.group(1)

        account = None
        if platform_str == "AmazonRedshift":
            platform = DataPlatform.REDSHIFT
            db_pattern = re.compile(r"Source = (\w+).Database\((.*)\),$")
            match = db_pattern.search(lines[1])
            assert (
                match
            ), "Can't parse AmazonRedshift database from power query expression"

            db = match.group(2).split(",")[1].replace('"', "")
            schema = get_field(lines[2])
            table = get_field(lines[3])
        elif platform_str == "Snowflake":
            platform = DataPlatform.SNOWFLAKE
            account_pattern = re.compile(r'Snowflake.Databases\("([\w\-\.]+)"')

            # remove trailing snowflakecomputing.com
            match = account_pattern.search(lines[1])
            assert match, "Can't parse Snowflake account from power query expression"

            account = ".".join(match.group(1).split(".")[:-2])
            db = get_field(lines[2])
            schema = get_field(lines[3])
            table = get_field(lines[4])
        elif platform_str == "GoogleBigQuery":
            platform = DataPlatform.BIGQUERY
            db = get_field(lines[2])
            schema = get_field(lines[3])
            table = get_field(lines[4])
        else:
            raise AssertionError(f"Unknown platform ${platform_str}")

        return to_dataset_entity_id(
            dataset_fullname(db, schema, table), platform, account
        )

    @staticmethod
    def transform_tiles_to_charts(tiles: List[PowerBITile]) -> List[Chart]:
        return [
            Chart(title=t.title, url=t.embedUrl, chart_type=ChartType.OTHER)
            for t in tiles
        ]
