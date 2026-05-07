---
id: gw_story_01K9E48VN051495FCN1NG25K2V
type: story
title: View org-wide budget health
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYE3303ZBCMT6S2DCWEBVQ
release: mvp
order: 18300
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: one dashboard with total budget, total spent, at-risk teams and enforced-today count
  so_that: I can manage spend at the org level
owners: []
tags: []
---
# View org-wide budget health

## Narrative

As a finance operations lead, I want one dashboard with total budget, total spent, at-risk teams and enforced-today count so that I can manage spend at the org level.

## Acceptance Criteria

### AC-001 — Populated dashboard

**Given:**

- The workspace has budgets set for several teams

**When:**

- I open /budgets

**Then:**

- I see total budget, total spent, total projected, at-risk team count and enforced-today count
- I see a card per team with state (ok/warn/over/blocked)

### AC-002 — No budgets configured

**Given:**

- No Budget records exist

**When:**

- I open /budgets

**Then:**

- The empty state "Create your first budget" is shown
- A CTA opens the create-budget modal

## API

### `GET /api/budgets/org`
**Response:**

```yaml
response:
  totals: json
  teams:
  - Budget
```
**Errors:**

```yaml
errors:
- 401
```
_inferred: true (carried over from source YAML)_

## UI

**Screens:**

- Budgets

**Components:**

- BudgetsPage
- TeamCard
- BudgetEventList

**States:**

- loading
- populated
- empty

## Data Models

- Budget
- Team

## Non-Functional Requirements

- Dashboard reads roll up MTD spend from the Request stream (materialized daily + intraday cache)

## Notes

_None._

## Open Questions

_None._
