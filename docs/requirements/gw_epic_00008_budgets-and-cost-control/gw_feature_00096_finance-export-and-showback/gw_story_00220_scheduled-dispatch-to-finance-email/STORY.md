---
id: gw_story_00220
type: story
title: Scheduled dispatch to finance email
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00096
release: v1.1
order: 220
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: the monthly CSV to be emailed automatically
  so_that: I do not have to download it each month
owners: []
tags: []
---
# Scheduled dispatch to finance email

## Narrative

As a finance operations lead, I want the monthly CSV to be emailed automatically so that I do not have to download it each month.

## Acceptance Criteria

### AC-001 — Configure dispatch

**Given:**

- I am on the finance export page

**When:**

- I configure a recipient and day-of-month

**Then:**

- On that day each month, the CSV is emailed with a link to the full archive

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
