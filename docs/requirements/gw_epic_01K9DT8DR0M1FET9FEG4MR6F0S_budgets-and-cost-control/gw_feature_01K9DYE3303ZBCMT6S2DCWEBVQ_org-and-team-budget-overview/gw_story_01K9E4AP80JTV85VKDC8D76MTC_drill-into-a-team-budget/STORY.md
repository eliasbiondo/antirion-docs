---
id: gw_story_01K9E4AP80JTV85VKDC8D76MTC
type: story
title: Drill into a team budget
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYE3303ZBCMT6S2DCWEBVQ
release: mvp
order: 18400
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: team lead
  i_want: to drill into my team's budget with projects and users
  so_that: I know who is burning it
owners: []
tags: []
depends_on:
- gw_story_01K9E48VN051495FCN1NG25K2V
---
# Drill into a team budget

## Narrative

As a team lead, I want to drill into my team's budget with projects and users so that I know who is burning it.

## Acceptance Criteria

### AC-001 — Team detail

**Given:**

- A team "copilot" with budget 120000 and projects/users

**When:**

- I click the team card

**Then:**

- I see MTD spend, projected month-end spend, daily burn, 7d burn and days-left
- I see projects and users sorted by spend

## API

### `GET /api/budgets`
**Request:**

```yaml
request:
  query:
    scope: string
    scope_id: uuid
```
**Response:**

```yaml
response:
  budget: Budget
  projects:
  - Project
  users:
  - UserBudget
```
**Errors:**

```yaml
errors:
- 401
- 403
- 404
```
_inferred: true (carried over from source YAML)_

## UI

_None._
## Data Models

- Budget
- Team
- Project
- UserBudget

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts
- Budget evaluation is shared-state and survives node loss

## Notes

_None._

## Open Questions

_None._
