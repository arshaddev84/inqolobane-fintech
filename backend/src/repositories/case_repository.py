"""Read-only case queue queries."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from schemas.case import CaseStatus

CASE_SELECT = """
    SELECT
        complaint.complaint_ref,
        customer.customer_ref,
        account.account_ref,
        account.product_type,
        complaint.category,
        complaint.subcategory,
        complaint.priority,
        complaint.status,
        complaint.allegation_status,
        complaint.customer_summary,
        complaint.opened_at,
        complaint.target_resolution_at
    FROM complaints AS complaint
    JOIN customers AS customer ON customer.customer_id = complaint.customer_id
    LEFT JOIN accounts AS account ON account.account_id = complaint.account_id
        WHERE (CAST(:status AS varchar) IS NULL OR complaint.status = :status)
      AND (
                    CAST(:search AS varchar) IS NULL
          OR complaint.complaint_ref ILIKE :pattern
          OR customer.customer_ref ILIKE :pattern
          OR account.account_ref ILIKE :pattern
          OR complaint.category ILIKE :pattern
          OR complaint.customer_summary ILIKE :pattern
      )
"""


class CaseRepository:
    """Execute case queue queries against PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_cases(
        self,
        search: str | None,
        status: CaseStatus | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return matching cases and the unpaginated match count."""
        parameters = {
            "status": status.value if status else None,
            "search": search,
            "pattern": f"%{search}%" if search else None,
        }
        total = self._session.execute(
            text(f"SELECT count(*) FROM ({CASE_SELECT}) AS matching_cases"), parameters
        ).scalar_one()
        rows = self._session.execute(
            text(f"{CASE_SELECT} ORDER BY complaint.opened_at DESC LIMIT :limit OFFSET :offset"),
            {**parameters, "limit": limit, "offset": offset},
        ).mappings()
        return [dict(row) for row in rows], total