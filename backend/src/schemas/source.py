"""Response contracts for profile snapshots and source documents."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ProfileSyncStatus(StrEnum):
    """Supported downstream profile synchronization states."""

    CURRENT = "CURRENT"
    STALE = "STALE"
    FAILED = "FAILED"
    PENDING_REVIEW = "PENDING_REVIEW"


class ProfileSnapshot(BaseModel):
    """One synthetic profile value observed in a source system."""

    customer_ref: str
    system_name: str
    field_name: str
    field_value: str | None
    source_version: str | None
    last_synced_at: datetime | None
    sync_status: ProfileSyncStatus
    observed_at: datetime


class ProfileSnapshotListResponse(BaseModel):
    """Filtered profile snapshot results."""

    items: list[ProfileSnapshot]
    total: int


class SourceDocument(BaseModel):
    """A local Markdown source document and its linked synthetic references."""

    document_ref: str
    filename: str
    title: str
    related_refs: list[str]
    content: str


class SourceDocumentListResponse(BaseModel):
    """Search results for local source documents."""

    items: list[SourceDocument]
    total: int