---
id: gw_story_00219
type: story
title: Monthly CSV showback per cost-center
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00096
release: v1.1
order: 219
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: a monthly CSV per cost-center
  so_that: I can show back spend to business units
owners: []
tags: []
---
# Monthly CSV showback per cost-center

## Narrative

As a finance operations lead, I want a monthly CSV per cost-center so that I can show back spend to business units.

## Acceptance Criteria

### AC-001 — Generate CSV

**Given:**

- The workspace has tagged requests with cost-center

**When:**

- I click "Generate monthly CSV"

**Then:**

- A CSV per cost-center is produced with daily cost and a monthly total

## API

_None._
## UI

_None._
## Data Models

- Billing
- Request

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
