---
id: gw_story_01K9E5H4Q0DZZ1X72GW9NCR019
type: story
title: Delete a project
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ27M0GQDWQQRC40C7V7VK
release: v1.1
order: 20500
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: team lead
  i_want: to delete an obsolete project
  so_that: retired projects do not clutter reports
owners: []
tags: []
---
# Delete a project

## Narrative

As a team lead, I want to delete an obsolete project so that retired projects do not clutter reports.

## Acceptance Criteria

### AC-001 — Delete with typed confirmation

**Given:**

- A Project has no active budgets

**When:**

- I click "Delete" and type the project name

**Then:**

- The Project is soft-deleted and an AuditLog entry records the deletion

### AC-002 — Block delete with active spend

**Given:**

- The Project has active spend

**When:**

- I click "Delete"

**Then:**

- I am asked to archive instead

## API

_None._
## UI

_None._
## Data Models

- Project
- AuditLog

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
