"""Read-only profile snapshot endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_session
from repositories.profile_repository import ProfileRepository
from schemas.source import ProfileSnapshot, ProfileSnapshotListResponse, ProfileSyncStatus

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/snapshots", response_model=ProfileSnapshotListResponse)
def list_profile_snapshots(
    session: Annotated[Session, Depends(get_session)],
    search: Annotated[str | None, Query(max_length=120)] = None,
    sync_status: ProfileSyncStatus | None = None,
) -> ProfileSnapshotListResponse:
    """List profile values across source systems for human review."""
    rows, total = ProfileRepository(session).list_snapshots(search, sync_status)
    return ProfileSnapshotListResponse(
        items=[ProfileSnapshot.model_validate(row) for row in rows],
        total=total,
    )