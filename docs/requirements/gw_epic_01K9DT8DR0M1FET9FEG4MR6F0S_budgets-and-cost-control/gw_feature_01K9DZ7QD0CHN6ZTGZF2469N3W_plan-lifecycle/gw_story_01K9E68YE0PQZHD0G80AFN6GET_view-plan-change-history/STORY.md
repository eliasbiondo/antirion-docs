---
id: gw_story_01K9E68YE0PQZHD0G80AFN6GET
type: story
title: View plan change history
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ7QD0CHN6ZTGZF2469N3W
release: v2.0
order: 21800
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: workspace owner
  i_want: to see the plan history
  so_that: I understand past changes
owners: []
tags: []
---
# View plan change history

## Narrative

As a workspace owner, I want to see the plan history so that I understand past changes.

## Acceptance Criteria

### AC-001 — View history

**Given:**

- The workspace has had multiple plan changes

**When:**

- I open "Plan history"

**Then:**

- I see each entry with plan, effective_at and actor

## API

_None._
## UI

_None._
## Data Models

- Billing

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
