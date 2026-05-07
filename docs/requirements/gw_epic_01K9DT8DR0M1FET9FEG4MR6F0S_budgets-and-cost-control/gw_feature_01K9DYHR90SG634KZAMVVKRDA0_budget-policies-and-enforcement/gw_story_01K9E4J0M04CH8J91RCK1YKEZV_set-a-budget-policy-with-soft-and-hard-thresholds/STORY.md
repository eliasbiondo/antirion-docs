---
id: gw_story_01K9E4J0M04CH8J91RCK1YKEZV
type: story
title: Set a budget policy with soft and hard thresholds
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYHR90SG634KZAMVVKRDA0
release: mvp
order: 18800
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to set soft-alert %, hard-cap % and action (alert/require-approval/downgrade/block)
  so_that: enforcement matches our comfort level per team
owners: []
tags: []
depends_on:
- gw_story_01K9E4AP80JTV85VKDC8D76MTC
---
# Set a budget policy with soft and hard thresholds

## Narrative

As a finance operations lead, I want to set soft-alert %, hard-cap % and action (alert/require-approval/downgrade/block) so that enforcement matches our comfort level per team.

## Acceptance Criteria

### AC-001 — Alert-only policy fires

**Given:**

- A BudgetPolicy with soft-alert 80% and action "alert-only"

**When:**

- The team's spent crosses 80% of budget

**Then:**

- The Budget's FEAT-199-provisioned AlertRule (category="budget", metric="budget.utilisation_pct") fires at severity "warn"; the standard FEAT-100 lifecycle applies and BudgetEvent.type="threshold" is recorded as the audit trail
- Traffic is not throttled

### AC-002 — Hard-cap block

**Given:**

- A BudgetPolicy with hard-cap 100% and action "block"
- The team is at 100% of budget

**When:**

- A new request arrives for that team

**Then:**

- The gateway returns 402 Payment Required with error code "budget_exhausted" (aligned with FEAT-180 license hard-close); Retry-After is set only when the cycle boundary is within the retry horizon
- A BudgetEvent of type "enforce" is recorded

## API

### `PATCH /api/budgets/:id/policy`
**Request:**

```yaml
request:
  body:
    soft_alert_pct: int
    hard_cap_pct: int
    action: string
```
**Response:**

```yaml
response:
  budget: Budget
```
**Errors:**

```yaml
errors:
- 400
- 401
- 403
- 404
```
_inferred: true (carried over from source YAML)_

## UI

_None._
## Data Models

- Budget
- BudgetPolicy
- BudgetEvent
- AlertEvent

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
