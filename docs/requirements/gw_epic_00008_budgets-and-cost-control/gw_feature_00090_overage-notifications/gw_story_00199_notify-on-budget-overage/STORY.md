---
id: gw_story_00199
type: story
title: Notify on budget overage
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00090
release: v1.1
order: 199
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: finance operations lead
  i_want: to be paged when actual spend exceeds the budget
  so_that: I can react even when soft thresholds did not fire
owners: []
tags: []
---
# Notify on budget overage

## Narrative

As a finance operations lead, I want to be paged when actual spend exceeds the budget so that I can react even when soft thresholds did not fire.

## Acceptance Criteria

### AC-001 — Overage triggers notification

**Given:**

- A Budget has amount 5000 and spent crosses from 4999 to 5050

**When:**

- The metering pipeline writes the latest bucket

**Then:**

- A BudgetEvent of type "overage" is written
- Notifications are delivered to Budget.owner_user_id and Org.billing_contact via the configured channels in both deployment modes (tenant-scoped roles behave identically per project.notifications_model)
- If Org.finance_contact is set, it is added to the audience; otherwise the billing_contact audience stands
- The notification is deduped for 1 hour on the same Budget

## API

### `GET /api/budgets/:id/events`
**Response:**

```yaml
response:
  items: BudgetEvent[]
```
**Errors:**

```yaml
errors:
- 401
- 403
- 404
```

## UI

**Screens:**

- Budgets

**Components:**

- OverageBanner

**States:**

- default
- over

## Data Models

- Budget
- BudgetEvent
- NotificationPreference

## Non-Functional Requirements

- Overage notifications are independent from BudgetPolicy soft_alert_pct

## Notes

_None._

## Open Questions

_None._
