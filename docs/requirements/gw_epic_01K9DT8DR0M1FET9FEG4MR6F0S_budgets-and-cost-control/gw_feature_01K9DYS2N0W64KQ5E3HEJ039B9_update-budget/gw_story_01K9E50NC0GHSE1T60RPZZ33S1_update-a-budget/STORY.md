---
id: gw_story_01K9E50NC0GHSE1T60RPZZ33S1
type: story
title: Update a budget
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYS2N0W64KQ5E3HEJ039B9
release: mvp
order: 19600
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to change a budget's amount, cycle, owner or policy
  so_that: allocations stay aligned with the business
owners: []
tags: []
depends_on:
- gw_story_01K9E4G610BMJT4NVNVN7W2RPG
---
# Update a budget

## Narrative

As a finance operations lead, I want to change a budget's amount, cycle, owner or policy so that allocations stay aligned with the business.

## Acceptance Criteria

### AC-001 — Edit amount within policy

**Given:**

- A Budget with amount 5000 exists

**When:**

- I change the amount to 6000 and save

**Then:**

- Budget.amount becomes 6000
- A BudgetEvent of type "change" is written
- Downstream forecasts recompute

### AC-002 — Edit requires approval on critical increases

**Given:**

- BudgetPolicy.edit_approval_threshold_pct is 50

**When:**

- I change amount from 5000 to 10000 (a 100% increase)

**Then:**

- An Approval is created with kind "budget-change"
- Budget.amount remains 5000 until the Approval is approved

## API

### `PUT /api/budgets/:id`
**Request:**

```yaml
request:
  body:
    amount: number
    cycle: string
    owner_user_id: string
    policy_id: string
```
**Response:**

```yaml
response:
  budget: Budget
  approval_id: string
```
**Errors:**

```yaml
errors:
- 403
- 404
- 409
```

## UI

**Screens:**

- Budgets

**Components:**

- BudgetEditor
- ApprovalBanner

**States:**

- default
- pending_approval

## Data Models

- Budget
- BudgetEvent
- Approval

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
