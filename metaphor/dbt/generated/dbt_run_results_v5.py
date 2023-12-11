# mypy: ignore-errors

# generated by datamodel-codegen:
#   filename:  https://schemas.getdbt.com/dbt/run-results/v5.json
#   timestamp: 2023-12-05T16:27:08+00:00

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, RootModel
from typing_extensions import Literal


class BaseArtifactMetadata(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    dbt_schema_version: str
    dbt_version: Optional[str] = '1.7.0b2'
    generated_at: Optional[str] = None
    invocation_id: Optional[str] = None
    env: Optional[Dict[str, str]] = None


class TimingInfo(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class RunResultOutput(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    status: Union[
        Literal['success', 'error', 'skipped'],
        Literal['pass', 'error', 'fail', 'warn', 'skipped'],
        Literal['pass', 'warn', 'error', 'runtime error'],
    ]
    timing: List[TimingInfo]
    thread_id: str
    execution_time: float
    adapter_response: Dict[str, Any]
    message: Optional[str] = None
    failures: Optional[int] = None
    unique_id: str
    compiled: Optional[bool] = None
    compiled_code: Optional[str] = None
    relation_name: Optional[str] = None


class RunResultsArtifact(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    metadata: BaseArtifactMetadata
    results: List[RunResultOutput]
    elapsed_time: float
    args: Optional[Dict[str, Any]] = None


class DbtRunResults(RootModel[RunResultsArtifact]):
    root: RunResultsArtifact
