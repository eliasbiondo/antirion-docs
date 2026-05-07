---
id: gw_feature_00096
type: feature
title: Finance export and showback
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_00008
release: v1.1
order: 96
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
# Finance export and showback

## Summary

Monthly CSV per cost-center with scheduled dispatch to finance email. Available in both modes, but the export is provider-passthrough cost only in self_hosted (no Antirion subscription line items), and in saas it includes both Antirion plan fees and provider passthrough so finance can reconcile the Antirion invoice.

## Stories

<!-- generated:children:start -->
- [gw_story_00219](gw_story_00219_monthly-csv-showback-per-cost-center/STORY.md) — Monthly CSV showback per cost-center
- [gw_story_00220](gw_story_00220_scheduled-dispatch-to-finance-email/STORY.md) — Scheduled dispatch to finance email
<!-- generated:children:end -->

## Notes

_None._
