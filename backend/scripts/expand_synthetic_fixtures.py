"""Append deterministic synthetic rows until each fixture collection has 50 records."""

import csv
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = REPOSITORY_ROOT / "data"
TARGET_COUNT = 50
FIRST_NEW_NUMBER = 5
LAST_NEW_NUMBER = 50

SCENARIOS = (
    (
        "CUSTOMER_DATA",
        "CONTACT_DETAILS_SYNC",
        "Customer reports that a profile update is not reflected in every contact channel and requests a review.",
        "CUSTOMER_OPERATIONS",
    ),
    (
        "PAYMENT_PROCESSING",
        "SCHEDULED_PAYMENT_QUERY",
        "Customer asks for a review of the status and timing shown for a scheduled payment.",
        "PAYMENTS_OPERATIONS",
    ),
    (
        "CARD_SERVICES",
        "CARD_TRANSACTION_QUERY",
        "Customer questions a card transaction entry and requests a review of its displayed status.",
        "CARD_OPERATIONS",
    ),
    (
        "CREDIT_INFORMATION",
        "PAYMENT_PROFILE_QUERY",
        "Customer asks for a review of how an account payment is represented in a profile snapshot.",
        "CREDIT_SERVICING",
    ),
    (
        "FEES_AND_BALANCE",
        "FEE_CALCULATION_QUERY",
        "Customer requests an explanation of a displayed fee and asks for the account calculation to be checked.",
        "CUSTOMER_OPERATIONS",
    ),
    (
        "ACCOUNT_ACCESS",
        "MOBILE_ACCESS_QUERY",
        "Customer reports difficulty accessing the mobile channel and requests an account-access review.",
        "DIGITAL_SUPPORT",
    ),
    (
        "LOAN_SERVICING",
        "INSTALLMENT_ALLOCATION_QUERY",
        "Customer asks how a scheduled installment was allocated and requests a servicing review.",
        "LENDING_OPERATIONS",
    ),
    (
        "CUSTOMER_DATA",
        "ADDRESS_UPDATE_QUERY",
        "Customer reports that an address change is not visible in a downstream profile and asks for a review.",
        "CUSTOMER_OPERATIONS",
    ),
)

PRODUCT_TYPES = (
    "CURRENT_ACCOUNT",
    "SAVINGS",
    "CREDIT_CARD",
    "PERSONAL_LOAN",
    "HOME_LOAN",
)
CHANNELS = ("CALL_CENTRE", "MOBILE_APP", "EMAIL", "BRANCH", "WEB_PORTAL")
PRIORITIES = ("LOW", "NORMAL", "HIGH", "URGENT")
CASE_STATUSES = (
    "OPEN",
    "TRIAGED",
    "INVESTIGATING",
    "AWAITING_CUSTOMER",
    "ESCALATED",
    "RESOLVED",
    "CLOSED",
)
PROFILE_STATUSES = ("CURRENT", "STALE", "FAILED", "PENDING_REVIEW")
SNAPSHOT_FIELDS = ("preferred_language", "email_address", "profile_address")
PROFILE_SYSTEMS = ("CORE_CUSTOMER_PROFILE", "NOTIFICATION_SERVICE", "CHANNEL_PREFERENCES")


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _records(number: int) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    customer_number = 1000 + number
    account_number = 3000 + number
    complaint_number = 2000 + number
    customer_id = f"00000000-0000-4000-8000-{customer_number:012d}"
    account_id = f"00000000-0000-4000-8000-{account_number:012d}"
    complaint_id = f"00000000-0000-4000-8000-{complaint_number:012d}"
    customer_ref = f"CUS-{customer_number}"
    account_ref = f"ACC-{account_number}"
    complaint_ref = f"CMP-{complaint_number}"

    opened = datetime(2026, 9, 21, 9, 0, tzinfo=timezone.utc) + timedelta(days=(number - 5) % 30)
    updated = opened - timedelta(days=1)
    created = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=number)
    scenario = SCENARIOS[(number - FIRST_NEW_NUMBER) % len(SCENARIOS)]
    category, subcategory, summary, team = scenario
    product_type = PRODUCT_TYPES[(number - FIRST_NEW_NUMBER) % len(PRODUCT_TYPES)]
    case_status = CASE_STATUSES[(number - FIRST_NEW_NUMBER) % len(CASE_STATUSES)]
    priority = PRIORITIES[(number - FIRST_NEW_NUMBER) % len(PRIORITIES)]
    target_date = opened + timedelta(days=5)
    resolved_at = _timestamp(opened + timedelta(days=2)) if case_status in {"RESOLVED", "CLOSED"} else ""

    synthetic_address = {
        "line1": f"Unit {number:03d}, Synthetic Lane",
        "suburb": "Test Suburb",
        "city": "Testville",
        "province": "Test Region",
        "postal_code": "0000",
        "country": "ZA",
    }
    email_address = f"synthetic.cus{customer_number}@example.test"
    customer = {
        "customer_id": customer_id,
        "customer_ref": customer_ref,
        "given_name": "Synthetic",
        "family_name": f"Customer {number:03d}",
        "date_of_birth": date(1980 + (number % 20), 1 + (number % 12), 1 + (number % 26)).isoformat(),
        "email_address": email_address,
        "phone_number": "",
        "residential_address_json": json.dumps(synthetic_address, separators=(",", ":")),
        "preferred_language": "en-ZA",
        "kyc_status": ("VERIFIED", "PENDING", "REVIEW_REQUIRED")[number % 3],
        "customer_status": "ACTIVE",
        "created_at": _timestamp(created),
        "updated_at": _timestamp(updated),
    }
    account = {
        "account_id": account_id,
        "customer_id": customer_id,
        "account_ref": account_ref,
        "product_type": product_type,
        "currency": "ZAR",
        "account_status": "OPEN",
        "opened_at": (date(2023, 1, 1) + timedelta(days=number)).isoformat(),
        "closed_at": "",
        "masked_account_no": f"**** **** **** {account_number:04d}",
    }
    complaint = {
        "complaint_id": complaint_id,
        "complaint_ref": complaint_ref,
        "customer_id": customer_id,
        "account_id": account_id,
        "category": category,
        "subcategory": subcategory,
        "channel": CHANNELS[(number - FIRST_NEW_NUMBER) % len(CHANNELS)],
        "priority": priority,
        "status": case_status,
        "customer_summary": summary,
        "allegation_status": "UNVERIFIED",
        "opened_at": _timestamp(opened),
        "target_resolution_at": _timestamp(target_date),
        "resolved_at": resolved_at,
        "assigned_team": team,
    }

    field_name = SNAPSHOT_FIELDS[(number - FIRST_NEW_NUMBER) % len(SNAPSHOT_FIELDS)]
    field_value = {
        "preferred_language": "en-ZA",
        "email_address": email_address,
        "profile_address": f"Unit {number:03d}, Synthetic Lane, Testville",
    }[field_name]
    sync_status = PROFILE_STATUSES[(number - FIRST_NEW_NUMBER) % len(PROFILE_STATUSES)]
    observed = opened + timedelta(days=1)
    sync_age = {"CURRENT": 0, "STALE": 14, "FAILED": 1, "PENDING_REVIEW": 3}[sync_status]
    snapshot = {
        "customer_ref": customer_ref,
        "system_name": PROFILE_SYSTEMS[(number - FIRST_NEW_NUMBER) % len(PROFILE_SYSTEMS)],
        "field_name": field_name,
        "field_value": field_value,
        "source_version": f"synthetic-v{number:03d}",
        "last_synced_at": _timestamp(observed - timedelta(days=sync_age)),
        "sync_status": sync_status,
        "observed_at": _timestamp(observed),
    }
    return customer, account, complaint, snapshot


def _key(row: dict[str, str], fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(row[field] for field in fields)


def _append_to_target(
    relative_path: str,
    generated_rows: list[dict[str, str]],
    key_fields: tuple[str, ...],
) -> int:
    path = DATA_DIRECTORY / relative_path
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        fieldnames = next(reader, None)
        parsed_rows = list(reader)
    if not fieldnames:
        raise ValueError(f"{path} has no CSV header.")
    expected_width = len(fieldnames)
    first_generated_key = generated_rows[0][fieldnames[0]]
    normalized_rows: list[list[str]] = []
    repaired_boundary = False
    for row in parsed_rows:
        if len(row) == expected_width * 2 - 1 and first_generated_key in row[expected_width - 1]:
            original_last, generated_first = row[expected_width - 1].split(first_generated_key, 1)
            original_row = row[: expected_width - 1] + [original_last]
            generated_row = [first_generated_key, *row[expected_width:]]
            if len(original_row) != expected_width or len(generated_row) != expected_width:
                raise ValueError(f"Unable to repair the first appended record in {path}.")
            normalized_rows.extend((original_row, generated_row))
            repaired_boundary = True
        elif len(row) == expected_width:
            normalized_rows.append(row)
        else:
            raise ValueError(f"{path} contains a malformed row with {len(row)} fields; expected {expected_width}.")

    existing_rows = [dict(zip(fieldnames, row, strict=True)) for row in normalized_rows]
    if len(existing_rows) > TARGET_COUNT:
        raise ValueError(f"{path} already has more than {TARGET_COUNT} data rows.")

    existing_keys = {_key(row, key_fields) for row in existing_rows}
    rows_to_append = []
    for row in generated_rows:
        row_key = _key(row, key_fields)
        if row_key in existing_keys:
            continue
        rows_to_append.append(row)
        existing_keys.add(row_key)
        if len(existing_rows) + len(rows_to_append) == TARGET_COUNT:
            break

    if len(existing_rows) + len(rows_to_append) != TARGET_COUNT:
        raise ValueError(f"Not enough deterministic rows available to bring {path} to {TARGET_COUNT}.")

    if rows_to_append or repaired_boundary:
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="raise")
            writer.writeheader()
            writer.writerows(existing_rows)
            writer.writerows(rows_to_append)
    return len(rows_to_append)


def _document_content(numbers: tuple[int, ...]) -> str:
    customer_refs = [f"CUS-{1000 + number}" for number in numbers]
    account_refs = [f"ACC-{3000 + number}" for number in numbers]
    complaint_refs = [f"CMP-{2000 + number}" for number in numbers]
    document_ref = f"DOC-CASE-{2000 + numbers[0]}"
    references = "\n".join(
        [f"- **Complaint reference:** {ref}" for ref in complaint_refs]
        + [f"- **Customer reference:** {ref}" for ref in customer_refs]
        + [f"- **Account reference:** {ref}" for ref in account_refs]
    )
    return f"""# Synthetic Case Review Record

- **Document reference:** {document_ref}
{references}
- **Record type:** Synthetic operations review
- **Sensitivity:** Internal test data

## Customer-reported issue
This fictional record represents a request for a human review of the linked case reference(s). The summary and identifiers are generated test data and do not describe a real customer, account, transaction, or event.

## Review notes
- Confirm the applicable source-system records before drawing a conclusion.
- Treat the complaint description as customer-reported, not as an established finding.
- Record any outcome through an authorised workflow outside this read-only prototype.

## Resolution
No cause or outcome is asserted. This document exists only to exercise synthetic search, reference linking, and review workflows.
"""


def _ensure_documents() -> int:
    document_directory = DATA_DIRECTORY / "documents"
    existing_paths = list(document_directory.glob("*.md"))
    if len(existing_paths) > TARGET_COUNT:
        raise ValueError(f"{document_directory} already has more than {TARGET_COUNT} Markdown documents.")

    planned_documents: list[tuple[Path, str]] = []
    for number in range(5, 49):
        complaint_number = 2000 + number
        filename = f"case-review-CMP-{complaint_number}.md"
        planned_documents.append((document_directory / filename, _document_content((number,))))
    shared_filename = "case-review-CMP-2049-CMP-2050.md"
    planned_documents.append((document_directory / shared_filename, _document_content((49, 50))))

    additions = 0
    known_paths = {path.resolve() for path in existing_paths}
    for path, content in planned_documents:
        if path.resolve() in known_paths:
            continue
        if len(existing_paths) + additions == TARGET_COUNT:
            break
        path.write_text(content, encoding="utf-8")
        additions += 1
        known_paths.add(path.resolve())

    if len(existing_paths) + additions != TARGET_COUNT:
        raise ValueError(f"Not enough deterministic documents available to bring {document_directory} to {TARGET_COUNT}.")
    return additions


def main() -> None:
    generated = [_records(number) for number in range(FIRST_NEW_NUMBER, LAST_NEW_NUMBER + 1)]
    datasets: tuple[tuple[str, Callable[[tuple[dict[str, str], ...]], dict[str, str]], tuple[str, ...]], ...] = (
        ("customers/customers.csv", lambda rows: rows[0], ("customer_ref",)),
        ("accounts/accounts.csv", lambda rows: rows[1], ("account_ref",)),
        ("complaints/complaints.csv", lambda rows: rows[2], ("complaint_ref",)),
        (
            "customers/profile_system_snapshots.csv",
            lambda rows: rows[3],
            ("customer_ref", "system_name", "field_name", "observed_at"),
        ),
    )
    counts: dict[str, int] = {}
    for relative_path, select_row, key_fields in datasets:
        counts[relative_path] = _append_to_target(
            relative_path,
            [select_row(rows) for rows in generated],
            key_fields,
        )
    counts["documents/*.md"] = _ensure_documents()

    for collection, count in counts.items():
        print(f"{collection}: appended {count}; target total {TARGET_COUNT}")


if __name__ == "__main__":
    main()