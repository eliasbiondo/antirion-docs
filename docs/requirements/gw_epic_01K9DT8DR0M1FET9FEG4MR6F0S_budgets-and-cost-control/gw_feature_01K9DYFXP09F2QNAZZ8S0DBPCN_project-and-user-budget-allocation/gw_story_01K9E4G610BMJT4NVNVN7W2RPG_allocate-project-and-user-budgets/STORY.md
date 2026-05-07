---
id: gw_story_01K9E4G610BMJT4NVNVN7W2RPG
type: story
title: Allocate project and user budgets
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYFXP09F2QNAZZ8S0DBPCN
release: v1.1
order: 18700
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: team lead
  i_want: to split my team budget across projects and users
  so_that: each owner knows their allocation
owners: []
tags: []
depends_on:
- gw_story_01K9E4AP80JTV85VKDC8D76MTC
---
# Allocate project and user budgets

## Narrative

As a team lead, I want to split my team budget across projects and users so that each owner knows their allocation.

## Acceptance Criteria

### AC-001 — Allocate across projects

**Given:**

- A team has budget 120000 and projects P1, P2 and P3

**When:**

- I assign shares 50/30/20 and save

**Then:**

- A Budget row is created (or updated) per Project with scope="project" and amount 60000 / 36000 / 24000 respectively; Project.budget_id is set to the created Budget
- The sum matches the team budget

### AC-002 — Over-allocation warning

**Given:**

- The team has budget 100000

**When:**

- I save allocations that sum to 120000

**Then:**

- I see a non-blocking warning "Over-allocated by 20%"
- {'The allocations are still saved with `over_allocated': 'true`'}

## API

### `PATCH /api/budgets/:id/allocations`
**Request:**

```yaml
request:
  body:
    projects: json
    users: json
```
**Response:**

```yaml
response:
  budget: Budget
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

_None._
## Data Models

- Budget
- Project
- UserBudget

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts
- The allocation mutation (creating/updating N Budget rows + N Project.budget_id writes) runs in a single transaction
- Generated Budgets inherit the parent Budget's cycle (cycle_start, cycle_end, reset_schedule) and the parent BudgetPolicy

## Notes

_None._

## Open Questions

_None._
