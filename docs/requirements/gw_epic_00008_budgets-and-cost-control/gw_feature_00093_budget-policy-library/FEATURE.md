---
id: gw_feature_00093
type: feature
title: Budget policy library
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_00008
release: v1.1
order: 93
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
# Budget policy library

## Summary

Manage reusable BudgetPolicy records that can be attached to multiple Budgets. Non-destructive edits (threshold/action changes) cascade to attached Budgets within the config_hot_reload SLA; destructive edits (deletion, incompatible action changes) require detachment from every dependent Budget first.

## Stories

<!-- generated:children:start -->
- [gw_story_00207](gw_story_00207_crud-reusable-budget-policies/STORY.md) — CRUD reusable budget policies
<!-- generated:children:end -->

## Notes

- **mode** (from source YAML): `both`
