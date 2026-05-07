---
id: gw_story_01K9E5MSX0CXZQ952P7Z3PH2MN
type: story
title: CRUD reusable budget policies
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ42708PEJD2MN424XAQRS
release: v1.1
order: 20700
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to manage a library of reusable BudgetPolicy rows
  so_that: multiple budgets can share the same policy
owners: []
tags: []
---
# CRUD reusable budget policies

## Narrative

As a finance operations lead, I want to manage a library of reusable BudgetPolicy rows so that multiple budgets can share the same policy.

## Acceptance Criteria

### AC-001 — Create policy

**Given:**

- I open the policy library

**When:**

- I create a policy with thresholds and action

**Then:**

- A BudgetPolicy row is created

### AC-002 — Attach to budget

**Given:**

- A Budget exists

**When:**

- I pick a library policy

**Then:**

- Budget.policy_id points at the library row

### AC-003 — Edit cascades

**Given:**

- A library policy is attached to 5 Budgets

**When:**

- I edit thresholds

**Then:**

- All attached Budgets see the new policy within the config-reload SLA (per project.non_functional_baseline.config_hot_reload)

### AC-004 — Delete blocked when in use

**Given:**

- A library policy is attached to Budgets

**When:**

- I click "Delete"

**Then:**

- The action is blocked with a list of dependent budgets

## API

_None._
## UI

_None._
## Data Models

- BudgetPolicy
- Budget

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
