# mypy: ignore-errors

# generated by datamodel-codegen:
#   filename:  https://schemas.getdbt.com/dbt/manifest/v8.json
#   timestamp: 2023-12-05T16:27:03+00:00

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr
from typing_extensions import Literal


class ManifestMetadata(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    dbt_schema_version: Optional[
        str
    ] = 'https://schemas.getdbt.com/dbt/manifest/v8.json'
    dbt_version: Optional[str] = '1.4.1'
    generated_at: Optional[AwareDatetime] = '2023-02-09T10:04:47.350768Z'
    invocation_id: Optional[str] = 'f795bc66-f417-4007-af6e-f2e513d33790'
    env: Optional[Dict[str, str]] = {}
    project_id: Optional[str] = Field(
        None, description='A unique identifier for the project'
    )
    user_id: Optional[
        constr(pattern=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
    ] = Field(None, description='A unique identifier for the user')
    send_anonymous_usage_stats: Optional[bool] = Field(
        None, description='Whether dbt is configured to send anonymous usage statistics'
    )
    adapter_type: Optional[str] = Field(
        None, description='The type name of the adapter'
    )


class FileHash(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    checksum: str


class Hook(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    sql: str
    transaction: Optional[bool] = True
    index: Optional[int] = None


class Docs(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    show: Optional[bool] = True
    node_color: Optional[str] = None


class ColumnInfo(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    name: str
    description: Optional[str] = ''
    meta: Optional[Dict[str, Any]] = {}
    data_type: Optional[str] = None
    quote: Optional[bool] = None
    tags: Optional[List[str]] = []


class DependsOn(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    macros: Optional[List[str]] = []
    nodes: Optional[List[str]] = []


class InjectedCTE(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: str
    sql: str


class TestConfig(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    enabled: Optional[bool] = True
    alias: Optional[str] = None
    schema_: Optional[str] = Field('dbt_test__audit', alias='schema')
    database: Optional[str] = None
    tags: Optional[Union[List[str], str]] = []
    meta: Optional[Dict[str, Any]] = {}
    materialized: Optional[str] = 'test'
    severity: Optional[
        constr(pattern=r'^([Ww][Aa][Rr][Nn]|[Ee][Rr][Rr][Oo][Rr])$')
    ] = 'ERROR'
    store_failures: Optional[bool] = None
    where: Optional[str] = None
    limit: Optional[int] = None
    fail_calc: Optional[str] = 'count(*)'
    warn_if: Optional[str] = '!= 0'
    error_if: Optional[str] = '!= 0'


class TestMetadata(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    kwargs: Optional[Dict[str, Any]] = {}
    namespace: Optional[str] = None


class SnapshotConfig(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    enabled: Optional[bool] = True
    alias: Optional[str] = None
    schema_: Optional[str] = Field(None, alias='schema')
    database: Optional[str] = None
    tags: Optional[Union[List[str], str]] = []
    meta: Optional[Dict[str, Any]] = {}
    materialized: Optional[str] = 'snapshot'
    incremental_strategy: Optional[str] = None
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    full_refresh: Optional[bool] = None
    unique_key: Optional[str] = None
    on_schema_change: Optional[str] = 'ignore'
    grants: Optional[Dict[str, Any]] = {}
    packages: Optional[List[str]] = []
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    strategy: Optional[str] = None
    target_schema: Optional[str] = None
    target_database: Optional[str] = None
    updated_at: Optional[str] = None
    check_cols: Optional[Union[str, List[str]]] = None


class SeedConfig(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    enabled: Optional[bool] = True
    alias: Optional[str] = None
    schema_: Optional[str] = Field(None, alias='schema')
    database: Optional[str] = None
    tags: Optional[Union[List[str], str]] = []
    meta: Optional[Dict[str, Any]] = {}
    materialized: Optional[str] = 'seed'
    incremental_strategy: Optional[str] = None
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    full_refresh: Optional[bool] = None
    unique_key: Optional[Union[str, List[str]]] = None
    on_schema_change: Optional[str] = 'ignore'
    grants: Optional[Dict[str, Any]] = {}
    packages: Optional[List[str]] = []
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    quote_columns: Optional[bool] = None


class MacroDependsOn(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    macros: Optional[List[str]] = []


class Quoting(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[bool] = None
    schema_: Optional[bool] = Field(None, alias='schema')
    identifier: Optional[bool] = None
    column: Optional[bool] = None


class FreshnessMetadata(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    dbt_schema_version: Optional[str] = 'https://schemas.getdbt.com/dbt/sources/v3.json'
    dbt_version: Optional[str] = '1.4.1'
    generated_at: Optional[AwareDatetime] = '2023-02-09T10:04:47.347023Z'
    invocation_id: Optional[str] = 'f795bc66-f417-4007-af6e-f2e513d33790'
    env: Optional[Dict[str, str]] = {}


class SourceFreshnessRuntimeError(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    unique_id: str
    error: Optional[Union[str, int]] = None
    status: Literal['runtime error']


class Time(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    count: Optional[int] = None
    period: Optional[Literal['minute', 'hour', 'day']] = None


class TimingInfo(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    started_at: Optional[AwareDatetime] = None
    completed_at: Optional[AwareDatetime] = None


class ExternalPartition(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    name: Optional[str] = ''
    description: Optional[str] = ''
    data_type: Optional[str] = ''
    meta: Optional[Dict[str, Any]] = {}


class SourceConfig(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    enabled: Optional[bool] = True


class MacroArgument(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    type: Optional[str] = None
    description: Optional[str] = ''


class Documentation(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    resource_type: Literal['doc']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    block_contents: str


class ExposureOwner(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    email: str
    name: Optional[str] = None


class ExposureConfig(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    enabled: Optional[bool] = True


class MetricFilter(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    field: str
    operator: str
    value: str


class MetricTime(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    count: Optional[int] = None
    period: Optional[Literal['day', 'week', 'month', 'year']] = None


class MetricConfig(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    enabled: Optional[bool] = True


class NodeConfig(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    enabled: Optional[bool] = True
    alias: Optional[str] = None
    schema_: Optional[str] = Field(None, alias='schema')
    database: Optional[str] = None
    tags: Optional[Union[List[str], str]] = []
    meta: Optional[Dict[str, Any]] = {}
    materialized: Optional[str] = 'view'
    incremental_strategy: Optional[str] = None
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    full_refresh: Optional[bool] = None
    unique_key: Optional[Union[str, List[str]]] = None
    on_schema_change: Optional[str] = 'ignore'
    grants: Optional[Dict[str, Any]] = {}
    packages: Optional[List[str]] = []
    docs: Optional[Docs] = {'show': True, 'node_color': None}


class SingularTestNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['test']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[TestConfig] = {
        'enabled': True,
        'alias': None,
        'schema': 'dbt_test__audit',
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'test',
        'severity': 'ERROR',
        'store_failures': None,
        'where': None,
        'limit': None,
        'fail_calc': 'count(*)',
        'warn_if': '!= 0',
        'error_if': '!= 0',
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.355371
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []


class HookNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['operation']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'view',
        'incremental_strategy': None,
        'persist_docs': {},
        'quoting': {},
        'column_types': {},
        'full_refresh': None,
        'unique_key': None,
        'on_schema_change': 'ignore',
        'grants': {},
        'packages': [],
        'docs': {'show': True, 'node_color': None},
        'post-hook': [],
        'pre-hook': [],
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.356482
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    index: Optional[int] = None


class ModelNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['model']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'view',
        'incremental_strategy': None,
        'persist_docs': {},
        'quoting': {},
        'column_types': {},
        'full_refresh': None,
        'unique_key': None,
        'on_schema_change': 'ignore',
        'grants': {},
        'packages': [],
        'docs': {'show': True, 'node_color': None},
        'post-hook': [],
        'pre-hook': [],
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.357701
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []


class RPCNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['rpc']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'view',
        'incremental_strategy': None,
        'persist_docs': {},
        'quoting': {},
        'column_types': {},
        'full_refresh': None,
        'unique_key': None,
        'on_schema_change': 'ignore',
        'grants': {},
        'packages': [],
        'docs': {'show': True, 'node_color': None},
        'post-hook': [],
        'pre-hook': [],
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.358761
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []


class SqlNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['sql operation']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'view',
        'incremental_strategy': None,
        'persist_docs': {},
        'quoting': {},
        'column_types': {},
        'full_refresh': None,
        'unique_key': None,
        'on_schema_change': 'ignore',
        'grants': {},
        'packages': [],
        'docs': {'show': True, 'node_color': None},
        'post-hook': [],
        'pre-hook': [],
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.359803
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []


class GenericTestNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    test_metadata: TestMetadata
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['test']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[TestConfig] = {
        'enabled': True,
        'alias': None,
        'schema': 'dbt_test__audit',
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'test',
        'severity': 'ERROR',
        'store_failures': None,
        'where': None,
        'limit': None,
        'fail_calc': 'count(*)',
        'warn_if': '!= 0',
        'error_if': '!= 0',
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.361009
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    column_name: Optional[str] = None
    file_key_name: Optional[str] = None


class SnapshotNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['snapshot']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: SnapshotConfig
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.364386
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []


class SeedNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['seed']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[SeedConfig] = {
        'enabled': True,
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'seed',
        'incremental_strategy': None,
        'persist_docs': {},
        'quoting': {},
        'column_types': {},
        'full_refresh': None,
        'unique_key': None,
        'on_schema_change': 'ignore',
        'grants': {},
        'packages': [],
        'docs': {'show': True, 'node_color': None},
        'quote_columns': None,
        'post-hook': [],
        'pre-hook': [],
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.366245
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    root_path: Optional[str] = None
    depends_on: Optional[MacroDependsOn] = {'macros': []}


class FreshnessThreshold(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    warn_after: Optional[Time] = {'count': None, 'period': None}
    error_after: Optional[Time] = {'count': None, 'period': None}
    filter: Optional[str] = None


class SourceFreshnessOutput(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    unique_id: str
    max_loaded_at: AwareDatetime
    snapshotted_at: AwareDatetime
    max_loaded_at_time_ago_in_s: float
    status: Literal['pass', 'warn', 'error', 'runtime error']
    criteria: FreshnessThreshold
    adapter_response: Dict[str, Any]
    timing: List[TimingInfo]
    thread_id: str
    execution_time: float


class ExternalTable(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    location: Optional[str] = None
    file_format: Optional[str] = None
    row_format: Optional[str] = None
    tbl_properties: Optional[str] = None
    partitions: Optional[Union[List[str], List[ExternalPartition]]] = None


class Macro(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    resource_type: Literal['macro']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    macro_sql: str
    depends_on: Optional[MacroDependsOn] = {'macros': []}
    description: Optional[str] = ''
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    arguments: Optional[List[MacroArgument]] = []
    created_at: Optional[float] = 1675937087.368656
    supported_languages: Optional[List[Literal['python', 'sql']]] = None


class Exposure(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    resource_type: Literal['exposure']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    type: Literal['dashboard', 'notebook', 'analysis', 'ml', 'application']
    owner: ExposureOwner
    description: Optional[str] = ''
    label: Optional[str] = None
    maturity: Optional[Literal['low', 'medium', 'high']] = None
    meta: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    config: Optional[ExposureConfig] = {'enabled': True}
    unrendered_config: Optional[Dict[str, Any]] = {}
    url: Optional[str] = None
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    created_at: Optional[float] = 1675937087.369866


class Metric(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    resource_type: Literal['metric']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    description: str
    label: str
    calculation_method: str
    expression: str
    filters: List[MetricFilter]
    time_grains: List[str]
    dimensions: List[str]
    timestamp: Optional[str] = None
    window: Optional[MetricTime] = None
    model: Optional[str] = None
    model_unique_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    config: Optional[MetricConfig] = {'enabled': True}
    unrendered_config: Optional[Dict[str, Any]] = {}
    sources: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    refs: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    created_at: Optional[float] = 1675937087.371092


class AnalysisNode(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['analysis']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'meta': {},
        'materialized': 'view',
        'incremental_strategy': None,
        'persist_docs': {},
        'quoting': {},
        'column_types': {},
        'full_refresh': None,
        'unique_key': None,
        'on_schema_change': 'ignore',
        'grants': {},
        'packages': [],
        'docs': {'show': True, 'node_color': None},
        'post-hook': [],
        'pre-hook': [],
    }
    tags: Optional[List[str]] = []
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True, 'node_color': None}
    patch_path: Optional[str] = None
    build_path: Optional[str] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    created_at: Optional[float] = 1675937087.353436
    config_call_dict: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    raw_code: Optional[str] = ''
    language: Optional[str] = 'sql'
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []
    metrics: Optional[List[List[str]]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    compiled_path: Optional[str] = None
    compiled: Optional[bool] = False
    compiled_code: Optional[str] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []


class SourceDefinition(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    database: Optional[str] = None
    schema_: str = Field(..., alias='schema')
    name: str
    resource_type: Literal['source']
    package_name: str
    path: str
    original_file_path: str
    unique_id: str
    fqn: List[str]
    source_name: str
    source_description: str
    loader: str
    identifier: str
    quoting: Optional[Quoting] = {
        'database': None,
        'schema': None,
        'identifier': None,
        'column': None,
    }
    loaded_at_field: Optional[str] = None
    freshness: Optional[FreshnessThreshold] = None
    external: Optional[ExternalTable] = None
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    source_meta: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    config: Optional[SourceConfig] = {'enabled': True}
    patch_path: Optional[str] = None
    unrendered_config: Optional[Dict[str, Any]] = {}
    relation_name: Optional[str] = None
    created_at: Optional[float] = 1675937087.368067


class DbtManifest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    metadata: ManifestMetadata = Field(..., description='Metadata about the manifest')
    nodes: Dict[
        str,
        Union[
            AnalysisNode,
            SingularTestNode,
            HookNode,
            ModelNode,
            RPCNode,
            SqlNode,
            GenericTestNode,
            SnapshotNode,
            SeedNode,
        ],
    ] = Field(
        ..., description='The nodes defined in the dbt project and its dependencies'
    )
    sources: Dict[str, SourceDefinition] = Field(
        ..., description='The sources defined in the dbt project and its dependencies'
    )
    macros: Dict[str, Macro] = Field(
        ..., description='The macros defined in the dbt project and its dependencies'
    )
    docs: Dict[str, Documentation] = Field(
        ..., description='The docs defined in the dbt project and its dependencies'
    )
    exposures: Dict[str, Exposure] = Field(
        ..., description='The exposures defined in the dbt project and its dependencies'
    )
    metrics: Dict[str, Metric] = Field(
        ..., description='The metrics defined in the dbt project and its dependencies'
    )
    selectors: Dict[str, Any] = Field(
        ..., description='The selectors defined in selectors.yml'
    )
    disabled: Optional[
        Dict[
            str,
            List[
                Union[
                    AnalysisNode,
                    SingularTestNode,
                    HookNode,
                    ModelNode,
                    RPCNode,
                    SqlNode,
                    GenericTestNode,
                    SnapshotNode,
                    SeedNode,
                    SourceDefinition,
                ]
            ],
        ]
    ] = Field(None, description='A mapping of the disabled nodes in the target')
    parent_map: Optional[Dict[str, List[str]]] = Field(
        None, description='A mapping from\xa0child nodes to their dependencies'
    )
    child_map: Optional[Dict[str, List[str]]] = Field(
        None, description='A mapping from parent nodes to their dependents'
    )
