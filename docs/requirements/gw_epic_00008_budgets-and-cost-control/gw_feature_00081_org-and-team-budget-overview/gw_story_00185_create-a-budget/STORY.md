---
id: gw_story_00185
type: story
title: Create a budget
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00081
release: mvp
order: 185
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to create a budget for the org, a team, project or user
  so_that: spend is constrained per scope
owners: []
tags: []
---
# Create a budget

## Narrative

As a finance operations lead, I want to create a budget for the org, a team, project or user so that spend is constrained per scope.

## Acceptance Criteria

### AC-001 — Create team budget

**Given:**

- I am on /budgets and click "New budget"

**When:**

- I pick scope "team", scope_id the UUID of team "copilot" (slugs are resolved to Team.id before write), amount 120000, cycle "monthly"
- I click Create

**Then:**

- A Budget is created for the current cycle
- The team card appears in the org dashboard
- An AuditLog entry records actor and action "budget.create"

### AC-002 — Duplicate scope prevented

**Given:**

- A Budget already exists for scope "team" and scope_id "copilot" in the current cycle

**When:**

- I try to create another with the same scope

**Then:**

- I see "A budget already exists for this scope"
- No duplicate is created

## API

### `POST /api/budgets`
**Request:**

```yaml
request:
  body:
    scope: string
    scope_id: uuid
    amount: number
    cycle: string
    owner_user_id: uuid
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
- 409
```
_inferred: true (carried over from source YAML)_

## UI

**Screens:**

- Budgets

**Components:**

- NewBudgetModal

**States:**

- default
- submitting
- error

## Data Models

- Budget
- Team
- AuditLog

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts
- Budget evaluation is shared-state and survives node loss

## Notes

_None._

## Open Questions

_None._
