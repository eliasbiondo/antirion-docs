---
id: gw_story_00447
type: story
title: Write back Request.cost into Budget.spent
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00186
release: mvp
order: 447
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: every finalised Request to increment the right Budget counter deterministically
  so_that: enforcement decisions and invoices stay in sync with observed traffic
owners: []
tags: []
---
# Write back Request.cost into Budget.spent

## Narrative

As a finance operations lead, I want every finalised Request to increment the right Budget counter deterministically so that enforcement decisions and invoices stay in sync with observed traffic.

## Acceptance Criteria

### AC-001 — Counter moves with each Request

**Given:**

- A Request is finalised with cost, cache_cost, input_cost and output_cost set

**When:**

- The metering pipeline consumes the event

**Then:**

- The shared-store budget counter increments for every applicable Budget scope (org, team, project, user_budget)
- Cache-hit cost (Request.cache_cost) contributes to the counter
- Downgrade-served cost counts against the served model's Budget (Request.model_id), not against Request.original_model_id
- The ledger table writes an append-only BudgetEvent of type="spend" carrying (budget_id, amount, request_id)

### AC-002 — Reconciliation against live counter

**Given:**

- The reconciliation worker scans the ledger for the last N minutes

**When:**

- Aggregated ledger spend diverges from the live shared-store counter by more than 1%

**Then:**

- An AlertEvent with source="budget", title="budget.counter.drift" fires (provisioned by FEAT-199)
- An AuditLog entry records the divergence magnitude and the affected budget_ids

### AC-003 — Idempotent replay

**Given:**

- The metering worker receives the same Request.id twice (at-least-once delivery)

**When:**

- The second event is processed

**Then:**

- BudgetEvent rows are not duplicated; the counter is not double-incremented (dedup key is (budget_id, request_id))

## API

_None._
## UI

_None._
## Data Models

- Request
- Budget
- UserBudget
- BudgetEvent
- AlertEvent
- AuditLog

## Non-Functional Requirements

- Counter updates are atomic per budget scope; a partial failure leaves no counter in a skewed state
- Reconciliation lag rolling p95 under 60 seconds

## Notes

**External cross-epic references (will move to frontmatter once their epic is migrated in pass 2):**

- `depends_on`: `gw_story_00444`

## Open Questions

_None._
