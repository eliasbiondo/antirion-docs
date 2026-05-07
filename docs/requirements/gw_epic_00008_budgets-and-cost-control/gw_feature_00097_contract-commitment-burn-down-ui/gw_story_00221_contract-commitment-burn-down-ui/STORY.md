---
id: gw_story_00221
type: story
title: Contract commitment burn-down UI
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00097
release: v1.1
order: 221
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: a burn-down of contract commitment used vs days remaining
  so_that: I can negotiate renewals with evidence
owners: []
tags: []
---
# Contract commitment burn-down UI

## Narrative

As a finance operations lead, I want a burn-down of contract commitment used vs days remaining so that I can negotiate renewals with evidence.

## Acceptance Criteria

### AC-001 — Render burn-down

**Given:**

- Billing has commitment, commitment_used, contract_start and contract_end

**When:**

- I open the page

**Then:**

- I see a burn-down chart and projected end-of-contract spend with a runway indicator

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
