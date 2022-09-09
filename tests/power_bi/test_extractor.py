from typing import List
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from metaphor.common.base_config import OutputConfig
from metaphor.common.event_util import EventUtil
from metaphor.power_bi.config import PowerBIRunConfig
from metaphor.power_bi.extractor import (
    PowerBIApp,
    PowerBIDashboard,
    PowerBIDataset,
    PowerBIExtractor,
    PowerBIPage,
    PowerBIReport,
    PowerBITable,
    PowerBITableColumn,
    PowerBITableMeasure,
    PowerBITile,
    WorkspaceInfo,
    WorkspaceInfoDashboard,
    WorkspaceInfoDataset,
    WorkspaceInfoReport,
)
from tests.test_utils import load_json


@pytest.mark.asyncio
@freeze_time("2000-01-01")
async def test_extractor(test_root_dir):
    mock_instance = MagicMock()

    workspace1_id = "workspace-1"

    app1 = PowerBIApp(id="app-1", name="foo app", workspaceId=workspace1_id)

    app2 = PowerBIApp(id="app-2", name="bar app", workspaceId=workspace1_id)

    dataset1_id = "dataset-1"
    dataset1 = PowerBIDataset(
        id=dataset1_id, webUrl=f"https://powerbi.com/{dataset1_id}", name="Foo Dataset"
    )
    dataset2_id = "dataset-2"
    dataset2 = PowerBIDataset(
        id=dataset2_id, webUrl=f"https://powerbi.com/{dataset2_id}", name="Bar Dataset"
    )

    report1_id = "report-1"
    report1 = PowerBIReport(
        id=report1_id,
        name="Foo Report",
        datasetId=dataset1_id,
        reportType="",
        webUrl=f"https://powerbi.com/report/{report1_id}",
    )

    report2_id = "report-2"
    report2 = PowerBIReport(
        id=report2_id,
        name="Bar Report",
        datasetId=dataset2_id,
        reportType="",
        webUrl=f"https://powerbi.com/report/{report2_id}",
    )

    dashboard1_id = "dashboard-1"
    dashboard1 = PowerBIDashboard(
        id=dashboard1_id,
        displayName="Dashboard A",
        webUrl=f"https://powerbi.com/dashboard/{dashboard1_id}",
    )

    dashboard2_id = "dashboard-2"
    dashboard2 = PowerBIDashboard(
        id=dashboard2_id,
        displayName="Dashboard B",
        webUrl=f"https://powerbi.com/dashboard/{dashboard2_id}",
    )

    tile1 = PowerBITile(
        id="tile-1",
        title="First Chart",
        datasetId=dataset1_id,
        reportId=report1_id,
        embedUrl="",
    )

    tile2 = PowerBITile(
        id="tile-2",
        title="Second Chart",
        datasetId=dataset1_id,
        reportId=report1_id,
        embedUrl="",
    )

    tile3 = PowerBITile(
        id="tile-3",
        title="Third Chart",
        datasetId=dataset2_id,
        reportId=report2_id,
        embedUrl="",
    )

    tiles = {dashboard1_id: [tile1, tile3], dashboard2_id: [tile2, tile3]}

    page1 = PowerBIPage(name="name-1", displayName="First Page", order=1)

    page2 = PowerBIPage(name="name-2", displayName="Second Page", order=2)

    pages = {workspace1_id: {report1_id: [], report2_id: [page1, page2]}}

    mock_instance.get_workspace_info = MagicMock(
        return_value=[
            WorkspaceInfo(
                id=workspace1_id,
                name="Workspace",
                type="normal",
                state="",
                reports=[
                    WorkspaceInfoReport(
                        id=report1.id,
                        appId=app1.id,
                        name=report1.name,
                        datasetId=report1.datasetId,
                        description="This is a report about foo",
                    ),
                    WorkspaceInfoReport(
                        id=report2.id,
                        name=report2.name,
                        datasetId=report2.datasetId,
                        description="This is a report about bar",
                    ),
                ],
                datasets=[
                    WorkspaceInfoDataset(
                        configuredBy="alice@foo.com",
                        id=dataset1.id,
                        name=dataset1.name,
                        description="This is a dataset",
                        tables=[
                            PowerBITable(
                                name="table1",
                                columns=[
                                    PowerBITableColumn(name="col1", dataType="string"),
                                    PowerBITableColumn(name="col2", dataType="int"),
                                ],
                                measures=[
                                    PowerBITableMeasure(
                                        name="exp1", expression="avg(col1)"
                                    ),
                                    PowerBITableMeasure(
                                        name="exp2", expression="max(col1)"
                                    ),
                                ],
                                source=[
                                    {
                                        "expression": 'let\n    Source = AmazonRedshift.Database("url:5439","db"),\n    public = Source{[Name="public"]}[Data],\n    table1 = public{[Name="table"]}[Data]\nin\n    table1'
                                    }
                                ],
                            )
                        ],
                    ),
                    WorkspaceInfoDataset(
                        configuredBy="bob@foo.com",
                        id=dataset2.id,
                        name=dataset2.name,
                        description="This is another dataset",
                        tables=[
                            PowerBITable(
                                name="table2",
                                columns=[
                                    PowerBITableColumn(name="col1", dataType="string"),
                                    PowerBITableColumn(name="col2", dataType="int"),
                                ],
                                measures=[],
                                source=[
                                    {
                                        "expression": 'let\n    Source = Snowflake.Databases("some-account.snowflakecomputing.com","COMPUTE_WH"),\n    DB_Database = Source{[Name="DB",Kind="Database"]}[Data],\n    PUBLIC_Schema = DB_Database{[Name="PUBLIC",Kind="Schema"]}[Data],\n    TEST_Table = PUBLIC_Schema{[Name="TEST",Kind="Table"]}[Data]\nin\n    TEST_Table'
                                    }
                                ],
                            ),
                            PowerBITable(
                                name="table2",
                                columns=[
                                    PowerBITableColumn(name="col1", dataType="string"),
                                    PowerBITableColumn(name="col2", dataType="int"),
                                ],
                                measures=[],
                                source=[
                                    {
                                        "expression": 'let\n    Source = GoogleBigQuery.Database(),\n    #"test-project" = Source{[Name="test-project"]}[Data],\n    test_Schema = #"test-project"{[Name="test",Kind="Schema"]}[Data],\n    example_Table = test_Schema{[Name="example",Kind="Table"]}[Data]\nin\n    example_Table'
                                    }
                                ],
                            ),
                        ],
                    ),
                ],
                dashboards=[
                    WorkspaceInfoDashboard(
                        displayName="Dashboard A",
                        id="dashboard-1",
                        appId=app2.id,
                    ),
                    WorkspaceInfoDashboard(displayName="Dashboard B", id="dashboard-2"),
                ],
            )
        ]
    )

    def fake_get_datasets(workspace_id) -> List[PowerBIDataset]:
        return [dataset1, dataset2]

    def fake_get_reports(workspace_id) -> List[PowerBIReport]:
        return [report1, report2]

    def fake_get_dashboards(workspace_id) -> List[PowerBIReport]:
        return [dashboard1, dashboard2]

    def fake_get_tiles(dashboard_id) -> List[PowerBITile]:
        return tiles.get(dashboard_id)

    def fake_get_pages(workspace_id, report_id) -> List[PowerBIPage]:
        return pages.get(workspace_id).get(report_id)

    def fake_get_apps() -> List[PowerBIApp]:
        return [app1, app2]

    mock_instance.get_datasets.side_effect = fake_get_datasets
    mock_instance.get_reports.side_effect = fake_get_reports
    mock_instance.get_dashboards.side_effect = fake_get_dashboards
    mock_instance.get_tiles.side_effect = fake_get_tiles
    mock_instance.get_pages.side_effect = fake_get_pages
    mock_instance.get_apps.side_effect = fake_get_apps

    with patch("metaphor.power_bi.extractor.PowerBIClient") as mock_client:
        mock_client.return_value = mock_instance

        config = PowerBIRunConfig(
            output=OutputConfig(),
            tenant_id="fake",
            client_id="fake_client_id",
            secret="fake_secret",
            workspaces=["bar"],
        )
        extractor = PowerBIExtractor(config)

        events = [EventUtil.trim_event(e) for e in await extractor.extract()]

    assert events == load_json(f"{test_root_dir}/power_bi/expected.json")
