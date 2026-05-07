---
id: gw_story_01K9E4KV70NVS3TCGBW53YHJRB
type: story
title: Downgrade to a cheaper model near budget cap
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYHR90SG634KZAMVVKRDA0
release: v1.1
order: 18900
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: platform engineer
  i_want: the "downgrade-model" action to re-route traffic to a cheaper model near the cap
  so_that: work continues at lower cost instead of failing
owners: []
tags: []
depends_on:
- gw_story_01K9E4J0M04CH8J91RCK1YKEZV
---
# Downgrade to a cheaper model near budget cap

## Narrative

As a platform engineer, I want the "downgrade-model" action to re-route traffic to a cheaper model near the cap so that work continues at lower cost instead of failing.

## Acceptance Criteria

### AC-001 — Downgrade applied

**Given:**

- A BudgetPolicy with hard-cap 100% and action "downgrade-model" to "claude-haiku-4-5-20251001"
- Team is at 102% of budget

**When:**

- A request to "claude-sonnet-4-5" arrives for the team

**Then:**

- The request is served by "claude-haiku-4-5"
- Request.downgraded is set to true and Request.original_model_id records the model originally requested
- A BudgetEvent of type "enforce" records the downgrade

## API

_None._
## UI

_None._
## Data Models

- Budget
- BudgetPolicy
- RoutingRule
- BudgetEvent
- Request

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
