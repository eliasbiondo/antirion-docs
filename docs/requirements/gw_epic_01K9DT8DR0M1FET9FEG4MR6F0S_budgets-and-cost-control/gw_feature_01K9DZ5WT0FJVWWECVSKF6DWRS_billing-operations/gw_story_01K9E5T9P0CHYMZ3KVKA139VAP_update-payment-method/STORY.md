---
id: gw_story_01K9E5T9P0CHYMZ3KVKA139VAP
type: story
title: Update payment method
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ5WT0FJVWWECVSKF6DWRS
release: v1.1
order: 21000
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to update the payment method
  so_that: billing continues without interruption
owners: []
tags: []
---
# Update payment method

## Narrative

As a finance operations lead, I want to update the payment method so that billing continues without interruption.

## Acceptance Criteria

### AC-001 — Update

**Given:**

- I am on billing

**When:**

- I enter new card details and save

**Then:**

- Billing.payment_method updates
- An AuditLog entry records "billing.payment_method.update"

## API

_None._
## UI

_None._
## Data Models

- Billing
- AuditLog

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
