---
id: gw_story_01K9E4V5K0SC93V8X25A53VKXR
type: story
title: Review the budget event timeline
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYNDF0BQT12JHBB6JJXF49
release: v1.1
order: 19300
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: a timeline of overages, thresholds, forecasts, waivers and enforcement events
  so_that: I can answer "what happened to the budget this month"
owners: []
tags: []
depends_on:
- gw_story_01K9E48VN051495FCN1NG25K2V
---
# Review the budget event timeline

## Narrative

As a finance operations lead, I want a timeline of overages, thresholds, forecasts, waivers and enforcement events so that I can answer "what happened to the budget this month".

## Acceptance Criteria

### AC-001 — Timeline populated

**Given:**

- The current cycle has 52 enforcement events and several waivers

**When:**

- I scroll through the timeline

**Then:**

- Each event shows type, severity, scope, title, body, actor and timestamp

## API

_None._
## UI

_None._
## Data Models

- BudgetEvent

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
