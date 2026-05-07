---
id: gw_story_00458
type: story
title: Provision Budget AlertRules
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00197
release: mvp
order: 458
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: platform engineer
  i_want: every Budget to get a matching system-managed AlertRule the moment it is created or edited
  so_that: budget signals flow through the same ack/snooze/resolve lifecycle as every other alert
owners: []
tags: []
depends_on:
- gw_story_00447
---
# Provision Budget AlertRules

## Narrative

As a platform engineer, I want every Budget to get a matching system-managed AlertRule the moment it is created or edited so that budget signals flow through the same ack/snooze/resolve lifecycle as every other alert.

## Acceptance Criteria

### AC-001 — Create Budget provisions AlertRule

**Given:**

- I create a Budget with BudgetPolicy.soft_alert_pct=80 and action="alert-only"

**When:**

- The provisioner reacts

**Then:**

- A system-managed AlertRule is created with category="budget", metric="budget.utilisation_pct", scope_kind="tenant", threshold=80, owner_user_id=Budget.owner_user_id, system_managed=true
- The AlertRule's audience is the Budget owner plus Org.finance_contact per project.notifications_model
- An AuditLog entry records action "budget.alert_rule.provisioned" with the resolved audience

### AC-002 — Edit BudgetPolicy re-syncs AlertRule

**Given:**

- A Budget's BudgetPolicy.soft_alert_pct changes from 80 to 90

**When:**

- The provisioner reacts

**Then:**

- The existing AlertRule's threshold is updated in place; AlertRule.updated_at is set

### AC-003 — Delete Budget retires the AlertRule

**Given:**

- A Budget is soft-deleted (Budget.deleted_at set)

**When:**

- The provisioner reacts

**Then:**

- The system-managed AlertRule is disabled (enabled=false) and a 30-day retention sweep removes it

### AC-004 — Platform-scope system rules exist

**Given:**

- The control plane is installed

**When:**

- The install completes

**Then:**

- Platform-scope AlertRules exist for metric=budget.forecast.mape, budget.fx.staleness_hours, budget.counter.drift - each with scope_kind="platform", org_id=null and paged via FEAT-192

### AC-005 — STORY-189 fires through the AlertRule

**Given:**

- A Budget with utilisation >= 80% fires the soft threshold

**When:**

- The metering pipeline (STORY-450) signals the utilisation update

**Then:**

- The system-managed AlertRule fires a regular AlertEvent (not a bare non-rule AlertEvent); ack/snooze/resolve flow as usual
- BudgetEvent of type="threshold" is written as an audit trail

## API

_None._
## UI

_None._
## Data Models

- Budget
- BudgetPolicy
- AlertRule
- AlertEvent
- BudgetEvent
- AuditLog

## Non-Functional Requirements

- The provisioner consumes the Budget/BudgetPolicy change stream; handlers are idempotent on (budget_id, metric)
- system_managed=true AlertRules cannot be edited via the UI - changes must go through BudgetPolicy; STORY-224 enforces this

## Notes

**External cross-epic references (will move to frontmatter once their epic is migrated in pass 2):**

- `depends_on`: `gw_story_00222`

## Open Questions

_None._
