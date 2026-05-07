---
id: gw_story_00190
type: story
title: See projected spend and runout date
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00084
release: v1.1
order: 190
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: projected month-end spend and a runout date
  so_that: I can preempt overages
owners: []
tags: []
depends_on:
- gw_story_00184
---
# See projected spend and runout date

## Narrative

As a finance operations lead, I want projected month-end spend and a runout date so that I can preempt overages.

## Acceptance Criteria

### AC-001 — Projection under budget

**Given:**

- A team is at 40% spent with 18 days left

**When:**

- I open the team card

**Then:**

- Projected is calculated as spent + (7d_burn * days_left * trend)
- The card state is "ok" or "warn" based on thresholds

### AC-002 — Runout date for over-budget team

**Given:**

- A team is already over budget

**When:**

- I open the team card

**Then:**

- A "runs out on" date is displayed based on current burn

## API

_None._
## UI

_None._
## Data Models

- Budget
- Team

## Non-Functional Requirements

- Burn rate computed on a 7-day rolling window
- Projection recomputed at least every hour

## Notes

_None._

## Open Questions

_None._
