---
id: gw_feature_00187
type: feature
title: Gateway budget admission
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_00008
release: mvp
order: 187
status:
  backend: not_started
  frontend: not_started
  infra: not_started
  docs: not_started
  qa: not_started
deployment_modes:
- saas
- self_hosted
installed_on: tenant_install
owners: []
tags: []
---
# Gateway budget admission

## Summary

Hot-path pipeline stage that reads the budget counter and, when the hard cap is reached, rejects with 402 Payment Required (error_code="budget_exhausted", cycle-aware Retry-After). Emits BudgetEvent.type="enforce". Placed between idempotency lookup and cache lookup per FEAT-191.

## Stories

<!-- generated:children:start -->
- [gw_story_00448](gw_story_00448_reject-over-budget-requests-at-the-gateway/STORY.md) — Reject over-budget requests at the gateway
<!-- generated:children:end -->

## Notes

- **mode** (from source YAML): `both`

**External cross-epic references (will move to frontmatter once their epic is migrated in pass 2):**

- `depends_on`: `gw_feature_00188`, `gw_feature_00191`
