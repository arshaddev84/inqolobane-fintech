# Production evaluation plan

Use synthetic fixtures only. Record test results, test-data version, and commit hash so that changes are reproducible.

## Functional correctness
- [ ] Each complaint resolves to the expected customer and account.
- [ ] A complaint can link to multiple relevant transactions without treating every account transaction as disputed.
- [ ] Duplicate document ingestion is idempotent based on stable document reference/content hash.
- [ ] Out-of-order profile events do not overwrite a later verified value.
- [ ] A stale snapshot is detected only when comparison rules and provenance justify it.
- [ ] Null, malformed, and conflicting dates are handled explicitly.
- [ ] Currency amounts use decimal/numeric arithmetic, never binary floating point for financial calculations.

## Access control and privacy
- [ ] An agent authorised for CUS-1001 cannot retrieve CUS-1002 documents by changing a case ID or search term.
- [ ] Similar names, shared household phone numbers, and stale email addresses do not bypass identity checks.
- [ ] Authorisation is enforced before SQL retrieval and before vector retrieval.
- [ ] Logs do not include raw contact details, document contents, secrets, or authentication tokens.
- [ ] Denied access attempts create an audit event with actor, resource reference, purpose, and correlation ID.
- [ ] Uploaded documents are treated as untrusted content and cannot override system policies or access rules.

## RAG quality
Create a small gold set with question, allowed source IDs, expected facts, and prohibited unsupported conclusions.
- [ ] Recall@5 for relevant evidence chunks is measured.
- [ ] Citation correctness is reviewed at document and section level.
- [ ] Unsupported-claim rate is measured on generated case briefs.
- [ ] Contradictory sources are surfaced with dates and provenance rather than silently collapsed.
- [ ] The model clearly distinguishes customer-reported claims from verified facts.
- [ ] Cross-customer retrieval leakage is zero across adversarial tests.

## Reliability and performance
- [ ] Retry behaviour is bounded and uses backoff for transient integration failures.
- [ ] Replayed events do not create duplicate profile changes or complaint events.
- [ ] Timeouts, downstream unavailability, and malformed provider responses have explicit handling.
- [ ] Load test with at least 50 concurrent read-only case lookups; document p50/p95/p99 latency and error rate.
- [ ] Database query plans are inspected for the highest-volume case lookups.
- [ ] Database migrations are tested on both a fresh database and a previous-version fixture.

## Human review and observability
- [ ] Every recommendation includes evidence references and an uncertainty statement.
- [ ] No autonomous transaction reversal, bureau update, profile amendment, or case closure is possible from an LLM response.
- [ ] A case owner can record the decision, rationale, and supporting evidence.
- [ ] Metrics distinguish detection rate, false positives, resolution time, reopened cases, and escalations.
- [ ] Runbooks cover data-sync failures, suspected fraud, privacy incidents, and retrieval outages.