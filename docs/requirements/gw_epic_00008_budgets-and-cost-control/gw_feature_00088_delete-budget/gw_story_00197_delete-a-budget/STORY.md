---
id: gw_story_00197
type: story
title: Delete a budget
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00088
release: v1.1
order: 197
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to remove a budget that is no longer needed
  so_that: stale budgets do not clutter reports
owners: []
tags: []
depends_on:
- gw_story_00196
---
# Delete a budget

## Narrative

As a finance operations lead, I want to remove a budget that is no longer needed so that stale budgets do not clutter reports.

## Acceptance Criteria

### AC-001 — Delete with reassignment

**Given:**

- A Budget is referenced by 3 Projects

**When:**

- I click "Delete" and choose to reassign Projects to a parent Team budget

**Then:**

- The 3 Projects' budget_id is updated
- The original Budget row is soft-deleted with deleted_at set
- A BudgetEvent of type "change" with title "budget deleted" is written

### AC-002 — Block delete on active Approval

**Given:**

- A Budget has a pending Approval

**When:**

- I click "Delete"

**Then:**

- I see "Resolve pending approvals before deleting"
- No deletion occurs

## API

### `DELETE /api/budgets/:id`
**Request:**

```yaml
request:
  body:
    reassign_to_budget_id: string
```
**Response:**

```yaml
response:
  ok: bool
```
**Errors:**

```yaml
errors:
- 403
- 404
- 409
```
_inferred: true (carried over from source YAML)_

## UI

**Screens:**

- Budgets

**Components:**

- BudgetDetail
- DangerDialog

**States:**

- default
- blocked
- confirming

## Data Models

- Budget
- Project
- BudgetEvent
- Approval

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
