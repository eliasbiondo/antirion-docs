---
id: gw_story_00211
type: story
title: Upload a purchase order
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00094
release: v2.0
order: 211
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to upload a PO
  so_that: invoices reference the correct PO
owners: []
tags: []
---
# Upload a purchase order

## Narrative

As a finance operations lead, I want to upload a PO so that invoices reference the correct PO.

## Acceptance Criteria

### AC-001 — Upload PO

**Given:**

- I am on billing

**When:**

- I upload a PDF and set a PO number

**Then:**

- Billing.po_number is set and the file is attached

## API

_None._
## UI

_None._
## Data Models

- Billing

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
