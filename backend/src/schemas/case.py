"""Public case-list response contracts."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CaseStatus(StrEnum):
    """Supported operational case statuses."""

    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    AWAITING_CUSTOMER = "AWAITING_CUSTOMER"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class CaseSummary(BaseModel):
    """A case queue row containing only fields needed for triage."""

    model_config = ConfigDict(from_attributes=True)

    complaint_ref: str
    customer_ref: str
    account_ref: str | None
    product_type: str | None
    category: str
    subcategory: str | None
    priority: str
    status: CaseStatus
    allegation_status: str
    customer_summary: str
    opened_at: datetime
    target_resolution_at: datetime | None


class CaseListResponse(BaseModel):
    """Paginated case queue response."""

    items: list[CaseSummary]
    total: int