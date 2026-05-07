---
id: gw_feature_00094
type: feature
title: Billing operations
lifecycle: active
created: '2026-05-07'
updated: '2026-05-07'
parent: gw_epic_00008
release: v1.1
order: 94
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
# Billing operations

## Summary

Contest invoice, request credit, update payment method, upload PO, set tax id, view invoice history. Available in saas mode only — Antirion invoices the workspace. In self_hosted mode the Antirion commercial relationship is the license (FEAT-175), not a metered invoice, and every endpoint and screen under this feature returns 404 and is hidden from navigation.

## Stories

<!-- generated:children:start -->
- [gw_story_00208](gw_story_00208_contest-an-invoice/STORY.md) — Contest an invoice
- [gw_story_00209](gw_story_00209_request-a-credit/STORY.md) — Request a credit
- [gw_story_00210](gw_story_00210_update-payment-method/STORY.md) — Update payment method
- [gw_story_00211](gw_story_00211_upload-a-purchase-order/STORY.md) — Upload a purchase order
- [gw_story_00212](gw_story_00212_set-tax-id/STORY.md) — Set tax id
- [gw_story_00213](gw_story_00213_view-invoice-history/STORY.md) — View invoice history
<!-- generated:children:end -->

## Notes

_None._
