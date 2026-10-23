"""Checks for referential integrity in the shipped synthetic fixtures."""

import csv
import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _read_csv(relative_path: str) -> list[dict[str, str]]:
    """Read one fixture file from the repository data directory."""
    fixture_path = REPOSITORY_ROOT / "data" / relative_path
    with fixture_path.open(newline="", encoding="utf-8") as fixture_file:
        return list(csv.DictReader(fixture_file))


def test_complaints_reference_existing_customers_and_accounts() -> None:
    """Every complaint fixture must point to an existing customer and account."""
    customer_ids = {row["customer_id"] for row in _read_csv("customers/customers.csv")}
    account_ids = {row["account_id"] for row in _read_csv("accounts/accounts.csv")}
    complaints = _read_csv("complaints/complaints.csv")

    assert complaints
    assert all(row["customer_id"] in customer_ids for row in complaints)
    assert all(row["account_id"] in account_ids for row in complaints)


def test_fixture_collections_have_fifty_records() -> None:
    """Every CSV collection and the Markdown catalog contains exactly 50 records."""
    for relative_path in (
        "accounts/accounts.csv",
        "complaints/complaints.csv",
        "customers/customers.csv",
        "customers/profile_system_snapshots.csv",
    ):
        assert len(_read_csv(relative_path)) == 50

    assert len(list((REPOSITORY_ROOT / "data" / "documents").glob("*.md"))) == 50


def test_profile_snapshots_reference_existing_customers() -> None:
    """Every profile snapshot must belong to a customer in the customer fixture."""
    customer_refs = {row["customer_ref"] for row in _read_csv("customers/customers.csv")}
    snapshots = _read_csv("customers/profile_system_snapshots.csv")

    assert len({(row["customer_ref"], row["system_name"], row["field_name"], row["observed_at"]) for row in snapshots}) == 50
    assert all(row["customer_ref"] in customer_refs for row in snapshots)


def test_customer_addresses_are_valid_json_csv_fields() -> None:
    """Customer address JSON must remain a single well-formed CSV field."""
    customers = _read_csv("customers/customers.csv")

    assert customers
    assert all(None not in row for row in customers)
    assert all(
        isinstance(json.loads(row["residential_address_json"]), dict)
        for row in customers
    )