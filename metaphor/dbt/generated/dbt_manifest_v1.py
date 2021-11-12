# mypy: ignore-errors

# generated by datamodel-codegen:
#   filename:  https://schemas.getdbt.com/dbt/manifest/v1.json
#   timestamp: 2021-11-10T06:43:38+00:00

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Extra, Field, constr
from typing_extensions import Literal


class ManifestMetadata(BaseModel):
    class Config:
        extra = Extra.forbid

    dbt_schema_version: Optional[
        str
    ] = 'https://schemas.getdbt.com/dbt/manifest/v1.json'
    dbt_version: Optional[str] = '0.19.0'
    generated_at: Optional[datetime] = '2021-02-10T04:42:33.683996Z'
    invocation_id: Optional[Optional[str]] = None
    env: Optional[Dict[str, str]] = {}
    project_id: Optional[Optional[str]] = Field(
        None, description='A unique identifier for the project'
    )
    user_id: Optional[
        Optional[
            constr(
                regex=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            )
        ]
    ] = Field(None, description='A unique identifier for the user')
    send_anonymous_usage_stats: Optional[Optional[bool]] = Field(
        None, description='Whether dbt is configured to send anonymous usage statistics'
    )
    adapter_type: Optional[Optional[str]] = Field(
        None, description='The type name of the adapter'
    )


class FileHash(BaseModel):
    class Config:
        extra = Extra.forbid

    name: str
    checksum: str


class Hook(BaseModel):
    class Config:
        extra = Extra.forbid

    sql: str
    transaction: Optional[bool] = True
    index: Optional[Optional[int]] = None


class DependsOn(BaseModel):
    class Config:
        extra = Extra.forbid

    macros: Optional[List[str]] = []
    nodes: Optional[List[str]] = []


class ColumnInfo(BaseModel):
    class Config:
        extra = Extra.allow

    name: str
    description: Optional[str] = ''
    meta: Optional[Dict[str, Any]] = {}
    data_type: Optional[Optional[str]] = None
    quote: Optional[Optional[bool]] = None
    tags: Optional[List[str]] = []


class Docs(BaseModel):
    class Config:
        extra = Extra.forbid

    show: Optional[bool] = True


class InjectedCTE(BaseModel):
    class Config:
        extra = Extra.forbid

    id: str
    sql: str


class TestConfig(BaseModel):
    class Config:
        extra = Extra.allow

    enabled: Optional[bool] = True
    materialized: Optional[str] = 'test'
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    vars: Optional[Dict[str, Any]] = {}
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    alias: Optional[Optional[str]] = None
    schema_: Optional[Optional[str]] = Field(None, alias='schema')
    database: Optional[Optional[str]] = None
    tags: Optional[Union[List[str], str]] = []
    full_refresh: Optional[Optional[bool]] = None
    severity: Optional[
        constr(regex=r'^([Ww][Aa][Rr][Nn]|[Ee][Rr][Rr][Oo][Rr])$')
    ] = 'ERROR'


class TestMetadata(BaseModel):
    class Config:
        extra = Extra.forbid

    namespace: Optional[Optional[str]] = None
    name: str
    kwargs: Dict[str, Any]


class SeedConfig(BaseModel):
    class Config:
        extra = Extra.allow

    enabled: Optional[bool] = True
    materialized: Optional[str] = 'seed'
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    vars: Optional[Dict[str, Any]] = {}
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    alias: Optional[Optional[str]] = None
    schema_: Optional[Optional[str]] = Field(None, alias='schema')
    database: Optional[Optional[str]] = None
    tags: Optional[Union[List[str], str]] = []
    full_refresh: Optional[Optional[bool]] = None
    quote_columns: Optional[Optional[bool]] = None


class ParsedDataTestNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['test']
    alias: str
    checksum: FileHash
    config: Optional[TestConfig] = {
        'enabled': True,
        'materialized': 'test',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
        'severity': 'ERROR',
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}


class ParsedSchemaTestNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    test_metadata: TestMetadata
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['test']
    alias: str
    checksum: FileHash
    config: Optional[TestConfig] = {
        'enabled': True,
        'materialized': 'test',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
        'severity': 'ERROR',
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    column_name: Optional[Optional[str]] = None


class ParsedSeedNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['seed']
    alias: str
    checksum: FileHash
    config: Optional[SeedConfig] = {
        'enabled': True,
        'materialized': 'seed',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
        'quote_columns': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}


class TimestampSnapshotConfig(BaseModel):
    class Config:
        extra = Extra.allow

    enabled: Optional[bool] = True
    materialized: Optional[str] = 'snapshot'
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    vars: Optional[Dict[str, Any]] = {}
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    alias: Optional[Optional[str]] = None
    schema_: Optional[Optional[str]] = Field(None, alias='schema')
    database: Optional[Optional[str]] = None
    tags: Optional[Union[List[str], str]] = []
    full_refresh: Optional[Optional[bool]] = None
    unique_key: str
    target_schema: str
    target_database: Optional[Optional[str]] = None
    strategy: Literal['timestamp']
    updated_at: str


class CheckSnapshotConfig(BaseModel):
    class Config:
        extra = Extra.allow

    enabled: Optional[bool] = True
    materialized: Optional[str] = 'snapshot'
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    vars: Optional[Dict[str, Any]] = {}
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    alias: Optional[Optional[str]] = None
    schema_: Optional[Optional[str]] = Field(None, alias='schema')
    database: Optional[Optional[str]] = None
    tags: Optional[Union[List[str], str]] = []
    full_refresh: Optional[Optional[bool]] = None
    unique_key: str
    target_schema: str
    target_database: Optional[Optional[str]] = None
    strategy: Literal['check']
    check_cols: Union[Literal['all'], List[str]]


class Strategy(BaseModel):
    pass


class GenericSnapshotConfig(BaseModel):
    class Config:
        extra = Extra.allow

    enabled: Optional[bool] = True
    materialized: Optional[str] = 'snapshot'
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    vars: Optional[Dict[str, Any]] = {}
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    alias: Optional[Optional[str]] = None
    schema_: Optional[Optional[str]] = Field(None, alias='schema')
    database: Optional[Optional[str]] = None
    tags: Optional[Union[List[str], str]] = []
    full_refresh: Optional[Optional[bool]] = None
    unique_key: str
    target_schema: str
    target_database: Optional[Optional[str]] = None
    strategy: Strategy


class Quoting(BaseModel):
    class Config:
        extra = Extra.forbid

    database: Optional[Optional[bool]] = None
    schema_: Optional[Optional[bool]] = Field(None, alias='schema')
    identifier: Optional[Optional[bool]] = None
    column: Optional[Optional[bool]] = None


class FreshnessMetadata(BaseModel):
    class Config:
        extra = Extra.forbid

    dbt_schema_version: Optional[str] = 'https://schemas.getdbt.com/dbt/sources/v1.json'
    dbt_version: Optional[str] = '0.19.0'
    generated_at: Optional[datetime] = '2021-02-10T04:42:33.675309Z'
    invocation_id: Optional[Optional[str]] = None
    env: Optional[Dict[str, str]] = {}


class SourceFreshnessRuntimeError(BaseModel):
    class Config:
        extra = Extra.forbid

    unique_id: str
    error: Optional[Optional[Union[str, int]]] = None
    status: Literal['runtime error']


class Time(BaseModel):
    class Config:
        extra = Extra.forbid

    count: int
    period: Literal['minute', 'hour', 'day']


class ExternalPartition(BaseModel):
    class Config:
        extra = Extra.allow

    name: Optional[str] = ''
    description: Optional[str] = ''
    data_type: Optional[str] = ''
    meta: Optional[Dict[str, Any]] = {}


class SourceConfig(BaseModel):
    class Config:
        extra = Extra.allow

    enabled: Optional[bool] = True


class MacroDependsOn(BaseModel):
    class Config:
        extra = Extra.forbid

    macros: Optional[List[str]] = []


class MacroArgument(BaseModel):
    class Config:
        extra = Extra.forbid

    name: str
    type: Optional[Optional[str]] = None
    description: Optional[str] = ''


class ParsedDocumentation(BaseModel):
    class Config:
        extra = Extra.forbid

    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    block_contents: str


class ExposureOwner(BaseModel):
    class Config:
        extra = Extra.forbid

    email: str
    name: Optional[Optional[str]] = None


class NodeConfig(BaseModel):
    class Config:
        extra = Extra.allow

    enabled: Optional[bool] = True
    materialized: Optional[str] = 'view'
    persist_docs: Optional[Dict[str, Any]] = {}
    post_hook: Optional[List[Hook]] = Field([], alias='post-hook')
    pre_hook: Optional[List[Hook]] = Field([], alias='pre-hook')
    vars: Optional[Dict[str, Any]] = {}
    quoting: Optional[Dict[str, Any]] = {}
    column_types: Optional[Dict[str, Any]] = {}
    alias: Optional[Optional[str]] = None
    schema_: Optional[Optional[str]] = Field(None, alias='schema')
    database: Optional[Optional[str]] = None
    tags: Optional[Union[List[str], str]] = []
    full_refresh: Optional[Optional[bool]] = None


class CompiledDataTestNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['test']
    alias: str
    checksum: FileHash
    config: Optional[TestConfig] = {
        'enabled': True,
        'materialized': 'test',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
        'severity': 'ERROR',
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None


class CompiledModelNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['model']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None


class CompiledHookNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['operation']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None
    index: Optional[Optional[int]] = None


class CompiledRPCNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['rpc']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None


class CompiledSchemaTestNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    test_metadata: TestMetadata
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['test']
    alias: str
    checksum: FileHash
    config: Optional[TestConfig] = {
        'enabled': True,
        'materialized': 'test',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
        'severity': 'ERROR',
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None
    column_name: Optional[Optional[str]] = None


class CompiledSeedNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['seed']
    alias: str
    checksum: FileHash
    config: Optional[SeedConfig] = {
        'enabled': True,
        'materialized': 'seed',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
        'quote_columns': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None


class CompiledSnapshotNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['snapshot']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None


class ParsedAnalysisNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['analysis']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}


class ParsedHookNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['operation']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    index: Optional[Optional[int]] = None


class ParsedModelNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['model']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}


class ParsedRPCNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['rpc']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}


class ParsedSnapshotNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['snapshot']
    alias: str
    checksum: FileHash
    config: Union[TimestampSnapshotConfig, CheckSnapshotConfig, GenericSnapshotConfig]
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}


class FreshnessThreshold(BaseModel):
    class Config:
        extra = Extra.forbid

    warn_after: Optional[Optional[Time]] = None
    error_after: Optional[Optional[Time]] = None
    filter: Optional[Optional[str]] = None


class SourceFreshnessOutput(BaseModel):
    class Config:
        extra = Extra.forbid

    unique_id: str
    max_loaded_at: datetime
    snapshotted_at: datetime
    max_loaded_at_time_ago_in_s: float
    status: Literal['pass', 'warn', 'error', 'runtime error']
    criteria: FreshnessThreshold
    adapter_response: Dict[str, Any]


class ExternalTable(BaseModel):
    class Config:
        extra = Extra.allow

    location: Optional[Optional[str]] = None
    file_format: Optional[Optional[str]] = None
    row_format: Optional[Optional[str]] = None
    tbl_properties: Optional[Optional[str]] = None
    partitions: Optional[Optional[List[ExternalPartition]]] = None


class ParsedMacro(BaseModel):
    class Config:
        extra = Extra.forbid

    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    macro_sql: str
    resource_type: Literal['macro']
    tags: Optional[List[str]] = []
    depends_on: Optional[MacroDependsOn] = {'macros': []}
    description: Optional[str] = ''
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    arguments: Optional[List[MacroArgument]] = []


class ParsedExposure(BaseModel):
    class Config:
        extra = Extra.forbid

    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    type: Literal['dashboard', 'notebook', 'analysis', 'ml', 'application']
    owner: ExposureOwner
    resource_type: Optional[
        Literal[
            'model',
            'analysis',
            'test',
            'snapshot',
            'operation',
            'seed',
            'rpc',
            'docs',
            'source',
            'macro',
            'exposure',
        ]
    ] = 'exposure'
    description: Optional[str] = ''
    maturity: Optional[Optional[Literal['low', 'medium', 'high']]] = None
    url: Optional[Optional[str]] = None
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List[str]]] = []


class CompiledAnalysisNode(BaseModel):
    class Config:
        extra = Extra.forbid

    raw_sql: str
    compiled: bool
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    fqn: List[str]
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    resource_type: Literal['analysis']
    alias: str
    checksum: FileHash
    config: Optional[NodeConfig] = {
        'enabled': True,
        'materialized': 'view',
        'persist_docs': {},
        'post-hook': [],
        'pre-hook': [],
        'vars': {},
        'quoting': {},
        'column_types': {},
        'alias': None,
        'schema': None,
        'database': None,
        'tags': [],
        'full_refresh': None,
    }
    tags: Optional[List[str]] = []
    refs: Optional[List[List[str]]] = []
    sources: Optional[List[List]] = []
    depends_on: Optional[DependsOn] = {'macros': [], 'nodes': []}
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    docs: Optional[Docs] = {'show': True}
    patch_path: Optional[Optional[str]] = None
    build_path: Optional[Optional[str]] = None
    deferred: Optional[bool] = False
    unrendered_config: Optional[Dict[str, Any]] = {}
    compiled_sql: Optional[Optional[str]] = None
    extra_ctes_injected: Optional[bool] = False
    extra_ctes: Optional[List[InjectedCTE]] = []
    relation_name: Optional[Optional[str]] = None


class ParsedSourceDefinition(BaseModel):
    class Config:
        extra = Extra.forbid

    fqn: List[str]
    database: Optional[Optional[str]] = None
    schema_: str = Field(..., alias='schema')
    unique_id: str
    package_name: str
    root_path: str
    path: str
    original_file_path: str
    name: str
    source_name: str
    source_description: str
    loader: str
    identifier: str
    resource_type: Literal['source']
    quoting: Optional[Quoting] = {
        'database': None,
        'schema': None,
        'identifier': None,
        'column': None,
    }
    loaded_at_field: Optional[Optional[str]] = None
    freshness: Optional[Optional[FreshnessThreshold]] = None
    external: Optional[Optional[ExternalTable]] = None
    description: Optional[str] = ''
    columns: Optional[Dict[str, ColumnInfo]] = {}
    meta: Optional[Dict[str, Any]] = {}
    source_meta: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    config: Optional[SourceConfig] = {'enabled': True}
    patch_path: Optional[Optional[str]] = None
    unrendered_config: Optional[Dict[str, Any]] = {}
    relation_name: Optional[Optional[str]] = None


class DbtManifest(BaseModel):
    class Config:
        extra = Extra.forbid

    metadata: ManifestMetadata = Field(..., description='Metadata about the manifest')
    nodes: Dict[
        str,
        Union[
            CompiledAnalysisNode,
            CompiledDataTestNode,
            CompiledModelNode,
            CompiledHookNode,
            CompiledRPCNode,
            CompiledSchemaTestNode,
            CompiledSeedNode,
            CompiledSnapshotNode,
            ParsedAnalysisNode,
            ParsedDataTestNode,
            ParsedHookNode,
            ParsedModelNode,
            ParsedRPCNode,
            ParsedSchemaTestNode,
            ParsedSeedNode,
            ParsedSnapshotNode,
        ],
    ] = Field(
        ..., description='The nodes defined in the dbt project and its dependencies'
    )
    sources: Dict[str, ParsedSourceDefinition] = Field(
        ..., description='The sources defined in the dbt project and its dependencies'
    )
    macros: Dict[str, ParsedMacro] = Field(
        ..., description='The macros defined in the dbt project and its dependencies'
    )
    docs: Dict[str, ParsedDocumentation] = Field(
        ..., description='The docs defined in the dbt project and its dependencies'
    )
    exposures: Dict[str, ParsedExposure] = Field(
        ..., description='The exposures defined in the dbt project and its dependencies'
    )
    selectors: Dict[str, Any] = Field(
        ..., description='The selectors defined in selectors.yml'
    )
    disabled: Optional[
        Optional[
            List[
                Union[
                    CompiledAnalysisNode,
                    CompiledDataTestNode,
                    CompiledModelNode,
                    CompiledHookNode,
                    CompiledRPCNode,
                    CompiledSchemaTestNode,
                    CompiledSeedNode,
                    CompiledSnapshotNode,
                    ParsedAnalysisNode,
                    ParsedDataTestNode,
                    ParsedHookNode,
                    ParsedModelNode,
                    ParsedRPCNode,
                    ParsedSchemaTestNode,
                    ParsedSeedNode,
                    ParsedSnapshotNode,
                    ParsedSourceDefinition,
                ]
            ]
        ]
    ] = Field(None, description='A list of the disabled nodes in the target')
    parent_map: Optional[Optional[Dict[str, List[str]]]] = Field(
        None, description='A mapping from\xa0child nodes to their dependencies'
    )
    child_map: Optional[Optional[Dict[str, List[str]]]] = Field(
        None, description='A mapping from parent nodes to their dependents'
    )
