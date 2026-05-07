---
id: gw_story_00217
type: story
title: Cancel plan
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00095
release: v1.1
order: 217
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: workspace owner
  i_want: to cancel my plan
  so_that: I stop paying
owners: []
tags: []
---
# Cancel plan

## Narrative

As a workspace owner, I want to cancel my plan so that I stop paying.

## Acceptance Criteria

### AC-001 — Cancel

**Given:**

- I am on a paid plan

**When:**

- I click "Cancel" and type the workspace slug to confirm

**Then:**

- The plan is scheduled to drop to free at period end
- An AuditLog entry records the cancellation

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
