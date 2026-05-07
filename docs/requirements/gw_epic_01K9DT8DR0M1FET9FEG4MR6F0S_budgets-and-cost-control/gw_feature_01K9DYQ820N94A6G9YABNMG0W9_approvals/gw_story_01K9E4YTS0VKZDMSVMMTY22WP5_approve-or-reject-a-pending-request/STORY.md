---
id: gw_story_01K9E4YTS0VKZDMSVMMTY22WP5
type: story
title: Approve or reject a pending request
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYQ820N94A6G9YABNMG0W9
release: v1.1
order: 19500
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: approver
  i_want: to approve or reject a pending approval with a note
  so_that: the original requester can proceed or adjust
owners: []
tags: []
depends_on:
- gw_story_01K9E4X0601X5WRVYC6W69HHPD
---
# Approve or reject a pending request

## Narrative

As a approver, I want to approve or reject a pending approval with a note so that the original requester can proceed or adjust.

## Acceptance Criteria

### AC-001 — Approve budget overage

**Given:**

- A pending Approval of kind "budget-overage" targets team "copilot"

**When:**

- I click "Approve" with note "one-off, launch week"

**Then:**

- The Approval status becomes "approved"
- A BudgetEvent of type "waiver" is created linked to this Approval
- The requester receives a notification
- An AuditLog entry records action "approval.approve"

### AC-002 — Reject with reason

**Given:**

- A pending Approval of kind "policy-change" exists

**When:**

- I click "Reject" with reason "breaks PII policy"

**Then:**

- The Approval status becomes "rejected"
- The requester is notified with the reason

### AC-003 — Expired approval

**Given:**

- An Approval's expires_at has passed

**When:**

- I try to decide it

**Then:**

- The Approve/Reject buttons are disabled
- The row shows "expired — ask requester to resubmit"

## API

### `POST /api/approvals/:id/decision`
**Request:**

```yaml
request:
  body:
    decision: string
    note: string
```
**Response:**

```yaml
response:
  approval: Approval
```
**Errors:**

```yaml
errors:
- 400
- 401
- 403
- 404
- 409
```
_inferred: true (carried over from source YAML)_

## UI

_None._
## Data Models

- Approval
- BudgetEvent
- AuditLog

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
