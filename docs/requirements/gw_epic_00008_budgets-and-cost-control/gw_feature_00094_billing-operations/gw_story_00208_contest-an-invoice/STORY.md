---
id: gw_story_00208
type: story
title: Contest an invoice
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00094
release: v1.1
order: 208
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to contest a line item on an invoice
  so_that: billing errors are corrected via a distinct status machine, not a generic support ticket
owners: []
tags: []
---
# Contest an invoice

## Narrative

As a finance operations lead, I want to contest a line item on an invoice so that billing errors are corrected via a distinct status machine, not a generic support ticket.

## Acceptance Criteria

### AC-001 — Submit contest against a specific InvoiceLine

**Given:**

- An Invoice is issued and I select a specific InvoiceLine

**When:**

- I click "Contest" on the line and submit with reason

**Then:**

- An InvoiceContest row is created with (invoice_line_id, org_id, reason, status="open", opened_by_user_id=me)
- A Notification of kind "billing" is delivered via FEAT-102 to Org.billing_contact and to Antirion-staff renewals sub-queue (saas); in self_hosted the renewals fan-out is suppressed
- An AuditLog entry records action "invoice.contest.open"

### AC-002 — Resolution terminal states

**Given:**

- An InvoiceContest is in status "open" or "under_review"

**When:**

- The resolver moves it to accepted, rejected or resolved

**Then:**

- resolved_at is stamped; a Notification is delivered to opened_by_user_id and Org.billing_contact

## API

### `POST /api/billing/invoice-lines/:id/contest`
**Request:**

```yaml
request:
  body:
    reason: string
```
**Response:**

```yaml
response:
  contest: InvoiceContest
```
**Errors:**

```yaml
errors:
- 400
- 401
- 403
- 404
```
_inferred: true (carried over from source YAML)_

## UI

**Screens:**

- Billing

**Components:**

- InvoiceList
- ContestModal

**States:**

- default
- submitting

## Data Models

- Invoice
- InvoiceLine
- InvoiceContest
- Notification
- AuditLog

## Non-Functional Requirements

- Contest creation is atomic; duplicate contests against the same invoice_line_id while a contest is "open" return 409

## Notes

_None._

## Open Questions

_None._
