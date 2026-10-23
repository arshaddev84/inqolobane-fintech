# Complaint Intake Record

- **Complaint reference:** CMP-2001
- **Customer reference:** CUS-1001
- **Opened at:** 2026-09-14T12:00:00Z
- **Channel:** Call centre
- **Category:** Customer data / contact details
- **Status at intake:** Investigating

## Customer-reported issue
The customer reports that they recently changed their contact details but some account notifications appear to be sent to an older phone number.

## Evidence available at intake
1. Customer profile update confirmation `DOC-KYC-1001`.
2. Core profile currently shows the new phone number.
3. Notification-service snapshot is seeded with an older phone number.
4. No confirmed evidence yet of a notification being delivered to an unintended recipient.

## Required checks
- Confirm the caller's identity using the approved authentication procedure.
- Inspect profile-change event and downstream sync correlation IDs.
- Check notification delivery logs with masked destinations.
- Establish whether any sensitive information was disclosed.
- Correct the downstream record through an authorised, audited workflow if the discrepancy is confirmed.
- Inform the customer of the outcome without exposing data belonging to another person.

## Resolution
Pending investigation. No root cause is asserted in this synthetic case.