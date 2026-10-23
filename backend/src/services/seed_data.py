"""Load the repository's synthetic CSV fixtures into a local database."""

import csv
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection


def _read_rows(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV file as dictionaries."""
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
    for line_number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"{path}:{line_number} does not match its CSV header.")
    return rows


def _insert_rows(connection: Connection, statement: str, rows: list[dict[str, object]]) -> int:
    """Insert rows without overwriting records already present."""
    if not rows:
        return 0
    result = connection.execute(text(statement), rows)
    return result.rowcount


def seed_synthetic_data(connection: Connection, data_directory: Path) -> dict[str, int]:
    """Insert customers, accounts, complaints, and profile snapshots idempotently."""
    customers = _read_rows(data_directory / "customers/customers.csv")
    accounts = _read_rows(data_directory / "accounts/accounts.csv")
    complaints = _read_rows(data_directory / "complaints/complaints.csv")
    snapshots = _read_rows(data_directory / "customers/profile_system_snapshots.csv")
    customer_ids = {row["customer_ref"]: row["customer_id"] for row in customers}

    inserted = {
        "customers": _insert_rows(
            connection,
            """INSERT INTO customers (
                customer_id, customer_ref, given_name, family_name, date_of_birth,
                email_address, phone_number, residential_address, preferred_language,
                kyc_status, customer_status, created_at, updated_at
            ) VALUES (
                :customer_id, :customer_ref, :given_name, :family_name, :date_of_birth,
                :email_address, :phone_number, CAST(:residential_address AS jsonb),
                :preferred_language, :kyc_status, :customer_status, :created_at, :updated_at
            ) ON CONFLICT (customer_id) DO NOTHING""",
            [
                {
                    **row,
                    "residential_address": row["residential_address_json"],
                }
                for row in customers
            ],
        ),
        "accounts": _insert_rows(
            connection,
            """INSERT INTO accounts (
                account_id, customer_id, account_ref, product_type, currency,
                account_status, opened_at, closed_at, masked_account_no
            ) VALUES (
                :account_id, :customer_id, :account_ref, :product_type, :currency,
                :account_status, :opened_at,
                CAST(NULLIF(:closed_at, '') AS date), :masked_account_no
            ) ON CONFLICT (account_id) DO NOTHING""",
            accounts,
        ),
        "complaints": _insert_rows(
            connection,
            """INSERT INTO complaints (
                complaint_id, complaint_ref, customer_id, account_id, category,
                subcategory, channel, priority, status, customer_summary,
                allegation_status, opened_at, target_resolution_at, resolved_at, assigned_team
            ) VALUES (
                :complaint_id, :complaint_ref, :customer_id, :account_id, :category,
                :subcategory, :channel, :priority, :status, :customer_summary,
                :allegation_status, :opened_at, :target_resolution_at,
                CAST(NULLIF(:resolved_at, '') AS timestamptz), :assigned_team
            ) ON CONFLICT (complaint_id) DO NOTHING""",
            complaints,
        ),
        "profile_snapshots": _insert_rows(
            connection,
            """INSERT INTO profile_system_snapshots (
                snapshot_id, customer_id, system_name, field_name, field_value,
                source_version, last_synced_at, sync_status, observed_at
            ) VALUES (
                gen_random_uuid(), :customer_id, :system_name, :field_name, :field_value,
                :source_version, :last_synced_at, :sync_status, :observed_at
            ) ON CONFLICT (customer_id, system_name, field_name, observed_at) DO NOTHING""",
            [
                {**row, "customer_id": customer_ids[row["customer_ref"]]}
                for row in snapshots
            ],
        ),
    }
    return inserted