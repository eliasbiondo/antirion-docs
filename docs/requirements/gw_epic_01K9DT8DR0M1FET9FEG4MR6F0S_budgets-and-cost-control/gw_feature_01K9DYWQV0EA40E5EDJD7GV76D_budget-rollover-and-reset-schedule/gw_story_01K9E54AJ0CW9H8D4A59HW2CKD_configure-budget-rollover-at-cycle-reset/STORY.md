---
id: gw_story_01K9E54AJ0CW9H8D4A59HW2CKD
type: story
title: Configure budget rollover at cycle reset
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYWQV0EA40E5EDJD7GV76D
release: v1.1
order: 19800
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to configure what happens to unused budget at cycle end
  so_that: teams keep underspent money or start fresh per our policy
owners: []
tags: []
---
# Configure budget rollover at cycle reset

## Narrative

As a finance operations lead, I want to configure what happens to unused budget at cycle end so that teams keep underspent money or start fresh per our policy.

## Acceptance Criteria

### AC-001 — Reset to zero

**Given:**

- A Budget has reset_schedule "reset" and cycle "monthly"

**When:**

- The cycle boundary is crossed

**Then:**

- Budget.spent becomes 0
- rollover_amount becomes 0
- A BudgetEvent of type "change" with title "cycle reset" is written

### AC-002 — Rollover capped balance

**Given:**

- Budget.amount=5000, spent=3500, reset_schedule "rollover", rollover_cap=2000

**When:**

- The cycle boundary is crossed

**Then:**

- The next cycle starts with available = 5000 + min(5000-3500, 2000) = 6500
- rollover_amount is set to 1500

## API

### `PUT /api/budgets/:id/schedule`
**Request:**

```yaml
request:
  body:
    reset_schedule: string
    rollover_cap: number
```
**Response:**

```yaml
response:
  budget: Budget
```
**Errors:**

```yaml
errors:
- 403
```
_inferred: true (carried over from source YAML)_

## UI

**Screens:**

- Budgets

**Components:**

- BudgetEditor
- CycleSettings

**States:**

- default

## Data Models

- Budget
- BudgetEvent

## Non-Functional Requirements

- Cycle rollover is performed by a single transactional job per org

## Notes

_None._

## Open Questions

_None._
