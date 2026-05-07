---
id: gw_feature_01K9E4EBE0ZTW1D58Y6VTAX3YV
type: feature
title: Budget metering and ledger reconciliation
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_01K9DT8DR0M1FET9FEG4MR6F0S
release: mvp
order: 18600
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
# Budget metering and ledger reconciliation

## Summary

Counter write-back pipeline Request.cost → Budget.spent (including cache_cost contribution; downgrade-served cost counted against the served model's budget). Reconciles live shared-store counters against persisted ledger on a worker cadence and raises the budget.counter.drift alert on deviation.

## Stories

<!-- generated:children:start -->
- [gw_story_01K9EKC8D0HDWJ5VG456K8BPR9](gw_story_01K9EKC8D0HDWJ5VG456K8BPR9_write-back-request-cost-into-budget-spent/STORY.md) — Write back Request.cost into Budget.spent
<!-- generated:children:end -->

## Notes

- **mode** (from source YAML): `both`
- **Migration note:** dropped self-edge in `depends_on` (`FEAT-186`); flagged for manual review.
