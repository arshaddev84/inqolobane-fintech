"""Case queue endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_session
from repositories.case_repository import CaseRepository
from schemas.case import CaseListResponse, CaseStatus
from services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=CaseListResponse)
def list_cases(
    session: Annotated[Session, Depends(get_session)],
    search: Annotated[str | None, Query(max_length=120)] = None,
    status: CaseStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CaseListResponse:
    """Return a searchable and filterable case queue."""
    service = CaseService(CaseRepository(session))
    return service.list_cases(search, status, limit, offset)