---
id: gw_story_01K9E5RF30A5GEV9YRFQR23VKV
type: story
title: Request a credit
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ5WT0FJVWWECVSKF6DWRS
release: v1.1
order: 20900
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to request a credit with a distinct status machine from contests and support tickets
  so_that: downtime or errors can be compensated auditably
owners: []
tags: []
---
# Request a credit

## Narrative

As a finance operations lead, I want to request a credit with a distinct status machine from contests and support tickets so that downtime or errors can be compensated auditably.

## Acceptance Criteria

### AC-001 — Submit credit request

**Given:**

- I am on billing

**When:**

- I POST /api/billing/credit-requests with amount, currency and reason

**Then:**

- A CreditRequest row is created with status="open", opened_by_user_id=me
- A Notification of kind "billing" is delivered to Org.billing_contact and Antirion-staff renewals sub-queue (saas)
- An AuditLog entry records action "billing.credit.request"

### AC-002 — Approval applies credit to an InvoiceLine

**Given:**

- A CreditRequest is approved by Antirion finance

**When:**

- The approver records the applied InvoiceLine

**Then:**

- CreditRequest.status becomes "applied"; applied_invoice_line_id is set; a Notification fires to opened_by_user_id

## API

### `POST /api/billing/credit-requests`
**Request:**

```yaml
request:
  body:
    amount: number
    currency: string
    reason: string
```
**Response:**

```yaml
response:
  credit_request: CreditRequest
```
**Errors:**

```yaml
errors:
- 400
- 401
- 403
```
_inferred: true (carried over from source YAML)_

## UI

_None._
## Data Models

- CreditRequest
- InvoiceLine
- Notification
- AuditLog

## Non-Functional Requirements

_None._

## Notes

_None._

## Open Questions

_None._
