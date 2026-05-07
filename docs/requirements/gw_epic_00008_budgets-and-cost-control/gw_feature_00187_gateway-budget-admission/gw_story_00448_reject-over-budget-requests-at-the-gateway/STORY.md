---
id: gw_story_00448
type: story
title: Reject over-budget requests at the gateway
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00187
release: mvp
order: 448
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: platform engineer
  i_want: requests that would exceed a Budget with action="block" to fail fast with a defined error shape
  so_that: tenants get a predictable 402 rather than opaque upstream failures
owners: []
tags: []
depends_on:
- gw_story_00447
---
# Reject over-budget requests at the gateway

## Narrative

As a platform engineer, I want requests that would exceed a Budget with action="block" to fail fast with a defined error shape so that tenants get a predictable 402 rather than opaque upstream failures.

## Acceptance Criteria

### AC-001 — Hard cap reached

**Given:**

- A Budget for the caller has BudgetPolicy.action="block" and spent >= amount

**When:**

- A request arrives on the gateway admission stage

**Then:**

- The admission stage returns 402 Payment Required with error_code "budget_exhausted"
- Retry-After is set when the cycle boundary is within 24 hours; otherwise the header is omitted
- A BudgetEvent of type="enforce" and severity="block" is written with the affected budget_id and scope
- Request.status_label is set to "budget_exhausted" on the recorded Request row (if the row is written at all per STORY-453 pipeline order)

### AC-002 — Waiver raises effective cap

**Given:**

- The Budget has an active BudgetEvent of type="waiver" with amount adding to the effective cap

**When:**

- A request arrives

**Then:**

- Admission uses the effective cap (Budget.amount + active waivers) for the block decision

### AC-003 — Downgrade policy diverts instead of blocking

**Given:**

- A Budget has BudgetPolicy.action="downgrade-model" and BudgetPolicy.downgrade_target_model_id set

**When:**

- A request arrives that would exceed the cap for the requested model

**Then:**

- Admission allows the request but FEAT-139 routing rewrites Request.model_id to the downgrade target; Request.downgraded=true and Request.original_model_id records the requested model
- No 402 is returned

## API

_None._
## UI

_None._
## Data Models

- Budget
- BudgetPolicy
- BudgetEvent
- Request

## Non-Functional Requirements

- The admission stage sits between idempotency lookup and cache lookup per FEAT-191

## Notes

**External cross-epic references (will move to frontmatter once their epic is migrated in pass 2):**

- `depends_on`: `gw_story_00450`

## Open Questions

_None._
