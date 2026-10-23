CREATE TABLE customers (
    customer_id         UUID PRIMARY KEY,
    customer_ref        VARCHAR(32) NOT NULL UNIQUE,
    given_name          VARCHAR(80) NOT NULL,
    family_name         VARCHAR(80) NOT NULL,
    date_of_birth       DATE,
    email_address       VARCHAR(254),
    phone_number        VARCHAR(32),
    residential_address JSONB,
    preferred_language  VARCHAR(12) NOT NULL DEFAULT 'en-ZA',
    kyc_status          VARCHAR(24) NOT NULL CHECK (kyc_status IN ('PENDING','VERIFIED','REVIEW_REQUIRED','EXPIRED')),
    customer_status     VARCHAR(24) NOT NULL CHECK (customer_status IN ('ACTIVE','RESTRICTED','CLOSED')),
    created_at          TIMESTAMPTZ NOT NULL,
    updated_at          TIMESTAMPTZ NOT NULL
);

CREATE TABLE accounts (
    account_id          UUID PRIMARY KEY,
    customer_id         UUID NOT NULL REFERENCES customers(customer_id),
    account_ref         VARCHAR(32) NOT NULL UNIQUE,
    product_type        VARCHAR(32) NOT NULL CHECK (product_type IN ('CURRENT_ACCOUNT','SAVINGS','CREDIT_CARD','PERSONAL_LOAN','HOME_LOAN')),
    currency            CHAR(3) NOT NULL,
    account_status      VARCHAR(24) NOT NULL CHECK (account_status IN ('OPEN','BLOCKED','CLOSED','IN_ARREARS')),
    opened_at           DATE NOT NULL,
    closed_at           DATE,
    masked_account_no   VARCHAR(32) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (closed_at IS NULL OR closed_at >= opened_at)
);

CREATE TABLE transactions (
    transaction_id      UUID PRIMARY KEY,
    account_id          UUID NOT NULL REFERENCES accounts(account_id),
    transaction_ref     VARCHAR(48) NOT NULL UNIQUE,
    posted_at           TIMESTAMPTZ,
    initiated_at        TIMESTAMPTZ NOT NULL,
    amount              NUMERIC(18,2) NOT NULL CHECK (amount >= 0),
    currency            CHAR(3) NOT NULL,
    direction           VARCHAR(8) NOT NULL CHECK (direction IN ('DEBIT','CREDIT')),
    channel             VARCHAR(24) NOT NULL,
    status              VARCHAR(24) NOT NULL CHECK (status IN ('PENDING','POSTED','REVERSED','DECLINED','UNDER_REVIEW')),
    merchant_description VARCHAR(160),
    external_reference  VARCHAR(80),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE complaints (
    complaint_id        UUID PRIMARY KEY,
    complaint_ref       VARCHAR(32) NOT NULL UNIQUE,
    customer_id         UUID NOT NULL REFERENCES customers(customer_id),
    account_id          UUID REFERENCES accounts(account_id),
    category            VARCHAR(40) NOT NULL,
    subcategory         VARCHAR(60),
    channel             VARCHAR(24) NOT NULL,
    priority            VARCHAR(16) NOT NULL CHECK (priority IN ('LOW','NORMAL','HIGH','URGENT')),
    status              VARCHAR(24) NOT NULL CHECK (status IN ('OPEN','TRIAGED','INVESTIGATING','AWAITING_CUSTOMER','ESCALATED','RESOLVED','CLOSED')),
    customer_summary    TEXT NOT NULL,
    allegation_status   VARCHAR(24) NOT NULL DEFAULT 'UNVERIFIED'
                        CHECK (allegation_status IN ('UNVERIFIED','PARTIALLY_VERIFIED','VERIFIED','NOT_SUBSTANTIATED')),
    opened_at           TIMESTAMPTZ NOT NULL,
    target_resolution_at TIMESTAMPTZ,
    resolved_at         TIMESTAMPTZ,
    assigned_team       VARCHAR(80),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE complaint_events (
    event_id            UUID PRIMARY KEY,
    complaint_id        UUID NOT NULL REFERENCES complaints(complaint_id),
    event_type          VARCHAR(40) NOT NULL,
    event_at            TIMESTAMPTZ NOT NULL,
    actor_ref           VARCHAR(64) NOT NULL,
    channel             VARCHAR(24),
    outcome             VARCHAR(80),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE complaint_transactions (
    complaint_id        UUID NOT NULL REFERENCES complaints(complaint_id),
    transaction_id      UUID NOT NULL REFERENCES transactions(transaction_id),
    relationship_type   VARCHAR(32) NOT NULL DEFAULT 'DISPUTED_TRANSACTION',
    PRIMARY KEY (complaint_id, transaction_id)
);

CREATE TABLE documents (
    document_id         UUID PRIMARY KEY,
    document_ref        VARCHAR(64) NOT NULL UNIQUE,
    customer_id         UUID REFERENCES customers(customer_id),
    document_type       VARCHAR(40) NOT NULL,
    title               VARCHAR(200) NOT NULL,
    storage_uri         TEXT NOT NULL,
    source_system       VARCHAR(80) NOT NULL,
    document_version    VARCHAR(32) NOT NULL,
    effective_at        TIMESTAMPTZ,
    received_at         TIMESTAMPTZ NOT NULL,
    sensitivity         VARCHAR(24) NOT NULL CHECK (sensitivity IN ('INTERNAL','CONFIDENTIAL','RESTRICTED')),
    content_sha256      CHAR(64),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE complaint_documents (
    complaint_id        UUID NOT NULL REFERENCES complaints(complaint_id),
    document_id         UUID NOT NULL REFERENCES documents(document_id),
    relevance_note      VARCHAR(240),
    PRIMARY KEY (complaint_id, document_id)
);

CREATE TABLE profile_change_events (
    profile_change_id   UUID PRIMARY KEY,
    customer_id         UUID NOT NULL REFERENCES customers(customer_id),
    field_name          VARCHAR(40) NOT NULL,
    old_value           TEXT,
    new_value           TEXT,
    source_system       VARCHAR(80) NOT NULL,
    change_channel      VARCHAR(32) NOT NULL,
    changed_at          TIMESTAMPTZ NOT NULL,
    effective_at        TIMESTAMPTZ NOT NULL,
    verification_status VARCHAR(24) NOT NULL CHECK (verification_status IN ('UNVERIFIED','PENDING','VERIFIED','REJECTED')),
    actor_ref           VARCHAR(64) NOT NULL,
    correlation_id      VARCHAR(64) NOT NULL
);

CREATE TABLE profile_system_snapshots (
    snapshot_id         UUID PRIMARY KEY,
    customer_id         UUID NOT NULL REFERENCES customers(customer_id),
    system_name         VARCHAR(80) NOT NULL,
    field_name          VARCHAR(40) NOT NULL,
    field_value         TEXT,
    source_version      VARCHAR(64),
    last_synced_at      TIMESTAMPTZ,
    sync_status         VARCHAR(24) NOT NULL CHECK (sync_status IN ('CURRENT','STALE','FAILED','PENDING_REVIEW')),
    observed_at         TIMESTAMPTZ NOT NULL,
    UNIQUE (customer_id, system_name, field_name, observed_at)
);

CREATE TABLE access_audit_events (
    audit_event_id      UUID PRIMARY KEY,
    actor_ref           VARCHAR(64) NOT NULL,
    action              VARCHAR(40) NOT NULL,
    resource_type       VARCHAR(40) NOT NULL,
    resource_ref        VARCHAR(64) NOT NULL,
    purpose_code        VARCHAR(40) NOT NULL,
    outcome             VARCHAR(16) NOT NULL CHECK (outcome IN ('ALLOWED','DENIED','ERROR')),
    correlation_id      VARCHAR(64) NOT NULL,
    occurred_at         TIMESTAMPTZ NOT NULL,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_accounts_customer_id ON accounts(customer_id);
CREATE INDEX idx_transactions_account_posted ON transactions(account_id, posted_at);
CREATE INDEX idx_complaints_customer_status ON complaints(customer_id, status);
CREATE INDEX idx_complaints_opened_at ON complaints(opened_at);
CREATE INDEX idx_complaint_events_case_time ON complaint_events(complaint_id, event_at);
CREATE INDEX idx_profile_snapshots_status ON profile_system_snapshots(sync_status, customer_id);
CREATE INDEX idx_profile_changes_customer_time ON profile_change_events(customer_id, changed_at);
CREATE INDEX idx_documents_customer_type ON documents(customer_id, document_type);

COMMIT;