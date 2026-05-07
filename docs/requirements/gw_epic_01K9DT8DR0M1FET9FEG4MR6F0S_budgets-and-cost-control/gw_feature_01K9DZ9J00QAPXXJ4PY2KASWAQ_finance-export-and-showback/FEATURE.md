---
id: gw_feature_01K9DZ9J00QAPXXJ4PY2KASWAQ
type: feature
title: Finance export and showback
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_01K9DT8DR0M1FET9FEG4MR6F0S
release: v1.1
order: 9600
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
- [gw_story_01K9E6AS10AWSBJQH2XSJGR4DB](gw_story_01K9E6AS10AWSBJQH2XSJGR4DB_monthly-csv-showback-per-cost-center/STORY.md) — Monthly CSV showback per cost-center
- [gw_story_01K9E6CKM07MV8QD7TRTMQB68N](gw_story_01K9E6CKM07MV8QD7TRTMQB68N_scheduled-dispatch-to-finance-email/STORY.md) — Scheduled dispatch to finance email
<!-- generated:children:end -->

## Notes

_None._
