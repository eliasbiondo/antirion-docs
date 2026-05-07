---
id: gw_feature_00197
type: feature
title: Budget to AlertRule bridge
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_00008
release: mvp
order: 197
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
# Budget to AlertRule bridge

## Summary

Provisions system-managed AlertRule rows (category="budget") per Budget at create/edit time. Metrics budget.utilisation_pct (threshold=BudgetPolicy.soft_alert_pct), budget.overage, budget.forecast.mape, budget.fx.staleness_hours, budget.counter.drift. Resolves the parallel-paging gap (prior M1/M2/M3/M8) by making the AlertRule the single paging source; BudgetEvent stays as the audit trail.

## Stories

<!-- generated:children:start -->
- [gw_story_00458](gw_story_00458_provision-budget-alertrules/STORY.md) — Provision Budget AlertRules
<!-- generated:children:end -->

## Notes

- **mode** (from source YAML): `both`

**External cross-epic references (will move to frontmatter once their epic is migrated in pass 2):**

- `depends_on`: `gw_feature_00188`
