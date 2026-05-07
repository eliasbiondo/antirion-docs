---
id: gw_story_00191
type: story
title: Backtest forecast accuracy
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00084
release: v1.1
order: 191
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to backtest the forecast against prior actuals
  so_that: I trust the projected month-end spend
owners: []
tags: []
---
# Backtest forecast accuracy

## Narrative

As a finance operations lead, I want to backtest the forecast against prior actuals so that I trust the projected month-end spend.

## Acceptance Criteria

### AC-001 — Run backtest

**Given:**

- I have 90 days of actual spend

**When:**

- I click "Backtest"

**Then:**

- I see MAPE, bias and a chart comparing forecast vs actual day by day

### AC-002 — Alert on drift

**Given:**

- MAPE rises above 20%

**When:**

- The daily backtest runs

**Then:**

- An alert fires to notify the finance contact

## API

_None._
## UI

_None._
## Data Models

- Budget

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
