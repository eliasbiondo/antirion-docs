---
id: gw_story_01K9E59TB04EV70N4PWFQB77JZ
type: story
title: View FX history, force override and alert on stale rate
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ0D106BQ4Y5P2K0CY0RM4
release: v1.1
order: 20100
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to review FX rate history, force an override, and be alerted when the rate is stale
  so_that: multi-currency conversions remain accurate
owners: []
tags: []
---
# View FX history, force override and alert on stale rate

## Narrative

As a finance operations lead, I want to review FX rate history, force an override, and be alerted when the rate is stale so that multi-currency conversions remain accurate.

## Acceptance Criteria

### AC-001 — View history

**Given:**

- The workspace uses USD reporting currency with a EUR budget

**When:**

- I open "FX history"

**Then:**

- I see each daily FxRate with source, timestamp and applied flag

### AC-002 — Force override

**Given:**

- I have permission

**When:**

- I enter an override rate for today

**Then:**

- An FxRate row with source "manual" is written and used for subsequent conversions
- An AuditLog entry records action "budget.fx.override" with context {prior_rate, override_rate, delta_pct}

### AC-003 — Stale rate alert

**Given:**

- The current FxRate is older than 48h

**When:**

- The daily check runs

**Then:**

- An alert fires to finance contact

## API

_None._
## UI

_None._
## Data Models

- FxRate
- AuditLog

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
