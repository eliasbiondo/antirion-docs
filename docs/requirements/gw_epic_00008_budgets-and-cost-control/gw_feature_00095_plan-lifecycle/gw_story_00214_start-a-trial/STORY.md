---
id: gw_story_00214
type: story
title: Start a trial
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00095
release: v1.1
order: 214
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: workspace owner
  i_want: to start a trial of a paid plan
  so_that: I can evaluate it
owners: []
tags: []
---
# Start a trial

## Narrative

As a workspace owner, I want to start a trial of a paid plan so that I can evaluate it.

## Acceptance Criteria

### AC-001 — Start trial

**Given:**

- The workspace is on the free plan

**When:**

- I click "Start trial" on a paid plan

**Then:**

- Billing.plan changes with trial_ends_at set
- A notification announces the trial start

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
