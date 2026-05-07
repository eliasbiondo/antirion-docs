---
id: gw_story_01K9E5DFH05DBWCAPYDDF3A24F
type: story
title: List projects
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_feature_01K9DZ27M0GQDWQQRC40C7V7VK
release: v1.1
order: 20300
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
narrative:
  as_a: team lead
  i_want: to list projects in my team
  so_that: I can manage them
owners: []
tags: []
---
# List projects

## Narrative

As a team lead, I want to list projects in my team so that I can manage them.

## Acceptance Criteria

### AC-001 — List

**Given:**

- My team has 7 projects

**When:**

- I open /projects

**Then:**

- I see each with name, owner, budget status and created_at

## API

_None._
## UI

_None._
## Data Models

- Project

## Non-Functional Requirements

- Budget counters live in the shared limiter store; enforcement decisions complete in under 5 ms p95
- Counter reconciliation runs on a worker cadence; drift between live counters and ledger alerts

## Notes

_None._

## Open Questions

_None._
