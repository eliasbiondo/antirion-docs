---
id: gw_feature_01K9E4G6107XV1BH41KVP2GRV5
type: feature
title: Gateway budget admission
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_01K9DT8DR0M1FET9FEG4MR6F0S
release: mvp
order: 18700
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
- [gw_story_01K9EKE300HEBG3F0A6ZV5G3JD](gw_story_01K9EKE300HEBG3F0A6ZV5G3JD_reject-over-budget-requests-at-the-gateway/STORY.md) — Reject over-budget requests at the gateway
<!-- generated:children:end -->

## Notes

- **mode** (from source YAML): `both`

**External cross-epic references (will move to frontmatter once their epic is migrated in pass 2):**

- `depends_on`: `gw_feature_01K9E4J0M07W0CXJ5E9ZTVPVXS`, `gw_feature_01K9E4QGD068KD78QCXW8KE0M0`
