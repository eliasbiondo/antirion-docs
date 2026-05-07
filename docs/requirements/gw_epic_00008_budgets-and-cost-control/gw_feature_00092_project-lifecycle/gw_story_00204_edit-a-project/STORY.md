---
id: gw_story_00204
type: story
title: Edit a project
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00092
release: v1.1
order: 204
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: project owner
  i_want: to rename my project or change its budget
  so_that: it stays aligned with the work
owners: []
tags: []
---
# Edit a project

## Narrative

As a project owner, I want to rename my project or change its budget so that it stays aligned with the work.

## Acceptance Criteria

### AC-001 — Rename

**Given:**

- A Project exists

**When:**

- I change the name and save

**Then:**

- Project.name is updated

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
