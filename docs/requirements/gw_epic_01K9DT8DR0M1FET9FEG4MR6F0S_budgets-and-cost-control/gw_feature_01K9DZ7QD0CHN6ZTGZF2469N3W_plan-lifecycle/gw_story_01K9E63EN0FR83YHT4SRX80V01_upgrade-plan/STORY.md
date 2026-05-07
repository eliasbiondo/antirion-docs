---
id: gw_story_01K9E63EN0FR83YHT4SRX80V01
type: story
title: Upgrade plan
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ7QD0CHN6ZTGZF2469N3W
release: v1.1
order: 21500
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: workspace owner
  i_want: to upgrade my plan
  so_that: I get higher limits and features
owners: []
tags: []
---
# Upgrade plan

## Narrative

As a workspace owner, I want to upgrade my plan so that I get higher limits and features.

## Acceptance Criteria

### AC-001 — Upgrade

**Given:**

- I am on a lower plan

**When:**

- I select a higher plan and confirm

**Then:**

- Billing.plan updates immediately
- Prorated charge is queued for next invoice

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
