"""Case queue application service."""

from repositories.case_repository import CaseRepository
from schemas.case import CaseListResponse, CaseStatus, CaseSummary


class CaseService:
    """Coordinate case retrieval and API response construction."""

    def __init__(self, repository: CaseRepository) -> None:
        self._repository = repository

    def list_cases(
        self,
        search: str | None,
        status: CaseStatus | None,
        limit: int,
        offset: int,
    ) -> CaseListResponse:
        """List matching cases for the operations queue."""
        rows, total = self._repository.list_cases(search, status, limit, offset)
        return CaseListResponse(items=[CaseSummary.model_validate(row) for row in rows], total=total)