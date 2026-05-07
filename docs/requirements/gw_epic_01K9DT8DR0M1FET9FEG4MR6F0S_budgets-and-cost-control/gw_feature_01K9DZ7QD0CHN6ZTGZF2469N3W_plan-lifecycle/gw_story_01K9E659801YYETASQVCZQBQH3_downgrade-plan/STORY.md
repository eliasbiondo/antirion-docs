---
id: gw_story_01K9E659801YYETASQVCZQBQH3
type: story
title: Downgrade plan
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ7QD0CHN6ZTGZF2469N3W
release: v1.1
order: 21600
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: workspace owner
  i_want: to downgrade my plan at the end of the current period
  so_that: I do not lose paid features mid-period
owners: []
tags: []
---
# Downgrade plan

## Narrative

As a workspace owner, I want to downgrade my plan at the end of the current period so that I do not lose paid features mid-period.

## Acceptance Criteria

### AC-001 — Schedule downgrade

**Given:**

- I am on a higher plan

**When:**

- I pick a lower plan and confirm

**Then:**

- The downgrade is scheduled for the next period boundary
- I see a banner showing the scheduled change

## API

_None._
## UI

_None._
## Data Models

- Billing
- AuditLog

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
