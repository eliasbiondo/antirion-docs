---
id: gw_story_00202
type: story
title: Create a project
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_00092
release: v1.1
order: 202
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: team lead
  i_want: to create a Project inside my team
  so_that: I can attribute spend at project granularity
owners: []
tags: []
---
# Create a project

## Narrative

As a team lead, I want to create a Project inside my team so that I can attribute spend at project granularity.

## Acceptance Criteria

### AC-001 — Create

**Given:**

- I am a lead of team "copilot"

**When:**

- I click "New project", enter a name and pick an owner

**Then:**

- A Project row is created with team_id set

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
