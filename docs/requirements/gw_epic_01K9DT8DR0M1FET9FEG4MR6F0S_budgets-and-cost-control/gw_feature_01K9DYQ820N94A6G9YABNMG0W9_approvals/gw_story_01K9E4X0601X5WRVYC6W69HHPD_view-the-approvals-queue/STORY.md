---
id: gw_story_01K9E4X0601X5WRVYC6W69HHPD
type: story
title: View the approvals queue
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DYQ820N94A6G9YABNMG0W9
release: v1.1
order: 19400
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: admin or team lead
  i_want: a queue of pending approvals addressed to me or my role
  so_that: I can unblock requesters quickly
owners: []
tags: []
---
# View the approvals queue

## Narrative

As a admin or team lead, I want a queue of pending approvals addressed to me or my role so that I can unblock requesters quickly.

## Acceptance Criteria

### AC-001 — Populated queue

**Given:**

- 3 pending Approvals exist addressed to role "admin"
- I have role "admin"

**When:**

- I open /approvals

**Then:**

- I see 3 rows with kind, requester, context, age and "Review" button
- The topbar shows a badge "3" next to the approvals link

### AC-002 — Empty queue

**Given:**

- No pending Approvals are addressed to me

**When:**

- I open /approvals

**Then:**

- I see the empty state "No pending approvals"

## API

### `GET /api/approvals`
**Request:**

```yaml
request:
  query:
    status: string
    kind: string
    assignee: string
    cursor: string
    limit: int
```
**Response:**

```yaml
response:
  approvals:
  - Approval
  next_cursor: string
```
**Errors:**

```yaml
errors:
- 401
```
_inferred: true (carried over from source YAML)_

## UI

_None._
## Data Models

- Approval
- User

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
