---
id: gw_story_00200
type: story
title: Budget in a non-USD currency with FX conversion
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00091
release: v2.0
order: 200
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead in a multinational org
  i_want: to express budgets in EUR or GBP
  so_that: regional teams plan in their local currency while the org reports in USD
owners: []
tags: []
---
# Budget in a non-USD currency with FX conversion

## Narrative

As a finance operations lead in a multinational org, I want to express budgets in EUR or GBP so that regional teams plan in their local currency while the org reports in USD.

## Acceptance Criteria

### AC-001 — Set budget currency

**Given:**

- My team operates in EUR

**When:**

- I create a Budget with currency "EUR"

**Then:**

- Budget.currency is "EUR"
- Budget.amount is stored as entered
- Reports show both EUR and the org reporting currency using the daily FX rate

### AC-002 — FX rate unavailable

**Given:**

- The FX provider has no rate for a given day

**When:**

- The system attempts conversion

**Then:**

- The last known rate is used and the row is flagged "stale FX"

## API

### `POST /api/budgets`
**Request:**

```yaml
request:
  body:
    amount: number
    currency: string
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
```
_inferred: true (carried over from source YAML)_

## UI

**Screens:**

- Budgets

**Components:**

- BudgetEditor
- CurrencyPicker

**States:**

- default

## Data Models

- Budget
- FxRate

## Non-Functional Requirements

- FX conversion caches rates for 24h

## Notes

_None._

## Open Questions

_None._
