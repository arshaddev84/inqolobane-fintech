# Data dictionary

All values are synthetic. The CSV files are starter fixtures, not a complete production export.

## CSV files

### `data/customers/customers.csv`
- `customer_id`: stable synthetic UUID primary key.
- `customer_ref`: human-readable fictional reference.
- `residential_address_json`: JSON-encoded synthetic address.
- `kyc_status`: `PENDING`, `VERIFIED`, `REVIEW_REQUIRED`, or `EXPIRED`.
- `customer_status`: `ACTIVE`, `RESTRICTED`, or `CLOSED`.
- `created_at`, `updated_at`: UTC ISO-8601 timestamps.

### `data/accounts/accounts.csv`
- `account_id`, `customer_id`: identifiers linking account to customer.
- `account_ref`: synthetic business reference.
- `product_type`: account or lending product category.
- `currency`: ISO 4217 currency code; samples use `ZAR`.
- `masked_account_no`: intentionally masked display value, not a full account number.

### `data/complaints/complaints.csv`
- `complaint_ref`: synthetic case reference.
- `category`, `subcategory`: operational taxonomy for triage.
- `customer_summary`: customer-reported issue, not a verified finding.
- `allegation_status`: defaults to `UNVERIFIED`.
- `target_resolution_at`: illustrative internal target, not a legal/regulatory deadline.

## Database tables

- `customers`: current customer profile and KYC/customer status.
- `accounts`: financial products held by a customer.
- `transactions`: account activity with status and channel.
- `complaints`: case intake, categorisation, status, and ownership.
- `complaint_events`: timeline of case handling and decisions.
- `complaint_transactions`: explicit link between a complaint and disputed transaction(s).
- `documents`: document metadata, source, version, effective time, and sensitivity.
- `complaint_documents`: explicit links between cases and evidence documents.
- `profile_change_events`: profile-field change history, verification, actor, and correlation ID.
- `profile_system_snapshots`: per-system snapshots used to identify stale/conflicting values.
- `access_audit_events`: record of access/action, resource, purpose, outcome, and correlation ID.

## Production design notes

A real implementation should use migration tooling, referential-integrity tests, retention policies, controlled vocabularies, data classification, and row/column-level access controls as appropriate. The schema intentionally avoids storing card security codes, PINs, passwords, or full card numbers. It is a reference model, not a complete regulatory data model.