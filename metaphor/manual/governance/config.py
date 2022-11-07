from dataclasses import field as dataclass_field
from typing import List

from pydantic.dataclasses import dataclass

from metaphor.common.base_extractor import BaseConfig
from metaphor.common.models import DeserializableDatasetLogicalID


@dataclass
class Ownership:
    # Type of ownership to assign
    type: str

    # Owner's email address
    email: str


@dataclass
class Description:
    # The description to assign
    description: str

    # The author's email address
    email: str


@dataclass
class DatasetGovernance:
    id: DeserializableDatasetLogicalID

    ownerships: List[Ownership] = dataclass_field(default_factory=lambda: [])

    tags: List[str] = dataclass_field(default_factory=lambda: [])

    descriptions: List[Description] = dataclass_field(default_factory=lambda: [])


@dataclass
class ManualGovernanceConfig(BaseConfig):
    datasets: List[DatasetGovernance]
