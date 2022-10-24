from typing import Optional, Union

from canonicaljson import encode_canonical_json
from pydantic.dataclasses import dataclass

from metaphor.common.event_util import EventUtil
from metaphor.common.utils import md5_digest
from metaphor.models.metadata_change_event import (
    DashboardLogicalID,
    DataPlatform,
    DatasetLogicalID,
    EntityType,
    GroupID,
    KnowledgeCardLogicalID,
    PersonLogicalID,
    VirtualViewLogicalID,
    VirtualViewType,
)


@dataclass
class EntityId:
    type: EntityType
    logicalId: Union[
        DatasetLogicalID,
        DashboardLogicalID,
        GroupID,
        KnowledgeCardLogicalID,
        PersonLogicalID,
        VirtualViewLogicalID,
    ]

    def __str__(self) -> str:
        json = encode_canonical_json(EventUtil.clean_nones(self.logicalId.to_dict()))
        return f"{self.type.name}~{md5_digest(json).upper()}"

    def __hash__(self):
        return hash(str(self))


def to_dataset_entity_id(
    normalized_name: str, platform: DataPlatform, account: Optional[str] = None
) -> EntityId:
    """
    converts a dataset name, platform and account into a dataset entity ID
    """
    return EntityId(
        EntityType.DATASET,
        DatasetLogicalID(name=normalized_name, platform=platform, account=account),
    )


def to_dataset_entity_id_from_logical_id(logical_id: DatasetLogicalID) -> EntityId:
    """
    converts a dataset logical ID to entity ID
    """
    return EntityId(EntityType.DATASET, logical_id)


def to_virtual_view_entity_id(name: str, virtualViewType: VirtualViewType) -> EntityId:
    """
    converts a virtual view name and type into a Virtual View entity ID
    """
    return EntityId(
        EntityType.VIRTUAL_VIEW,
        VirtualViewLogicalID(name=name, type=virtualViewType),
    )


def to_person_entity_id(email: str) -> EntityId:
    """
    converts an email to a person entity ID
    """
    return EntityId(
        EntityType.PERSON,
        PersonLogicalID(email=email),
    )


def dataset_normalized_name(
    db: Optional[str] = None, schema: Optional[str] = None, table: Optional[str] = None
) -> str:
    """builds dataset normalized name"""
    return ".".join([part for part in [db, schema, table] if part]).lower()
