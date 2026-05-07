---
id: gw_story_01K9E4EBE0C95BV7PP5AZBJYTS
type: story
title: Reconcile direct-waiver and Approval-based budget paths
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYE3303ZBCMT6S2DCWEBVQ
release: v1.1
order: 18600
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: the behavior of direct-waiver (STORY-193) and Approval-based waivers (STORY-196) to be clearly separated by threshold
  so_that: small waivers are fast and big waivers are governed
owners: []
tags: []
---
# Reconcile direct-waiver and Approval-based budget paths

## Narrative

As a finance operations lead, I want the behavior of direct-waiver (STORY-193) and Approval-based waivers (STORY-196) to be clearly separated by threshold so that small waivers are fast and big waivers are governed.

## Acceptance Criteria

### AC-001 — Small waiver uses direct path

**Given:**

- BudgetPolicy.waiver_approval_threshold_pct is 50
- Requested waiver is 20% over current budget

**When:**

- The finance lead grants the waiver

**Then:**

- A BudgetEvent of type "waiver" is written directly with no Approval

### AC-002 — Large waiver requires approval

**Given:**

- BudgetPolicy.waiver_approval_threshold_pct is 50
- Requested waiver is 70%

**When:**

- The finance lead submits it

**Then:**

- An Approval of kind "budget-overage" is created
- The BudgetEvent is only written after the Approval is approved

## API

_None._
## UI

_None._
## Data Models

- Budget
- BudgetPolicy
- BudgetEvent
- Approval

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts
- Budget evaluation is shared-state and survives node loss

## Notes

_None._

## Open Questions

_None._
