"""Read-only profile snapshot queries."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from schemas.source import ProfileSyncStatus


class ProfileRepository:
    """Execute profile snapshot queries against PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_snapshots(
        self,
        search: str | None,
        sync_status: ProfileSyncStatus | None,
    ) -> tuple[list[dict[str, object]], int]:
        """Return profile snapshots filtered by customer, field, or status."""
        parameters = {
            "search": search,
            "pattern": f"%{search}%" if search else None,
            "sync_status": sync_status.value if sync_status else None,
        }
        selection = """
            FROM profile_system_snapshots AS snapshot
            JOIN customers AS customer ON customer.customer_id = snapshot.customer_id
            WHERE (
                  CAST(:sync_status AS varchar) IS NULL
                  OR snapshot.sync_status = :sync_status
              )
              AND (
                  CAST(:search AS varchar) IS NULL
                  OR customer.customer_ref ILIKE :pattern
                  OR snapshot.system_name ILIKE :pattern
                  OR snapshot.field_name ILIKE :pattern
                  OR snapshot.field_value ILIKE :pattern
              )
        """
        total = self._session.execute(
            text(f"SELECT count(*) {selection}"), parameters
        ).scalar_one()
        rows = self._session.execute(
            text(
                """SELECT customer.customer_ref, snapshot.system_name, snapshot.field_name,
                          snapshot.field_value, snapshot.source_version, snapshot.last_synced_at,
                          snapshot.sync_status, snapshot.observed_at
                   """
                + selection
                + " ORDER BY customer.customer_ref, snapshot.field_name, snapshot.observed_at DESC"
            ),
            parameters,
        ).mappings()
        return [dict(row) for row in rows], total