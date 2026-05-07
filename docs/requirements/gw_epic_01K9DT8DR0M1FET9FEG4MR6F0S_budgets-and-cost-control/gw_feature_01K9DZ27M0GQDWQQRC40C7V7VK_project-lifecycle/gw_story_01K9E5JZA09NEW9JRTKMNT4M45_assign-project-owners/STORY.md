---
id: gw_story_01K9E5JZA09NEW9JRTKMNT4M45
type: story
title: Assign project owners
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ27M0GQDWQQRC40C7V7VK
release: v1.1
order: 20600
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: team lead
  i_want: to assign one or more owners to a project
  so_that: responsibility is clear
owners: []
tags: []
---
# Assign project owners

## Narrative

As a team lead, I want to assign one or more owners to a project so that responsibility is clear.

## Acceptance Criteria

### AC-001 — Add owner

**Given:**

- A Project exists

**When:**

- I add a user as owner

**Then:**

- Project.owner_user_id is updated (and additional owners are recorded in a join table if multiple)

## API

_None._
## UI

_None._
## Data Models

- Project
- User

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
