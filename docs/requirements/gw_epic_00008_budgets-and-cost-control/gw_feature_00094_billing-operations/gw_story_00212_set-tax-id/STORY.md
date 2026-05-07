---
id: gw_story_00212
type: story
title: Set tax id
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00094
release: v2.0
order: 212
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to set or update the tax id
  so_that: invoices include the correct tax id
owners: []
tags: []
---
# Set tax id

## Narrative

As a finance operations lead, I want to set or update the tax id so that invoices include the correct tax id.

## Acceptance Criteria

### AC-001 — Set tax id

**Given:**

- I am on billing

**When:**

- I enter a tax id and save

**Then:**

- Billing.tax_id updates and it appears on the next invoice

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
