---
id: gw_story_01K9E4SB00JGGBN6FFX5C8HCS7
type: story
title: Grant a one-time budget waiver
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYNDF0BQT12JHBB6JJXF49
release: v1.1
order: 19200
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: admin
  i_want: to grant a one-time waiver expanding a budget for the current cycle
  so_that: urgent work can continue
owners: []
tags: []
depends_on:
- gw_story_01K9E4J0M04CH8J91RCK1YKEZV
---
# Grant a one-time budget waiver

## Narrative

As a admin, I want to grant a one-time waiver expanding a budget for the current cycle so that urgent work can continue.

## Acceptance Criteria

### AC-001 — Waiver allows spend

**Given:**

- A team hit its hard cap

**When:**

- I grant a waiver of 5000 with reason "incident response"

**Then:**

- The effective cap for this cycle is raised by 5000
- A BudgetEvent of type "waiver" is recorded
- Enforcement resumes if the new cap is crossed

## API

### `POST /api/budgets/waivers`
**Request:**

```yaml
request:
  body:
    team_id: uuid
    amount: number
    reason: string
```
**Response:**

```yaml
response:
  waiver: BudgetEvent
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

**Screens:**

- Budgets

**Components:**

- WaiverModal
- AmountInput
- ReasonInput
- ValidUntilInput

**States:**

- default
- confirming
- submitting

## Data Models

- Budget
- BudgetEvent
- AuditLog

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
