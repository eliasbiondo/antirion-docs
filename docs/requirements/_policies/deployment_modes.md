---
id: gw_policy_00005
type: policy
title: Deployment modes
lifecycle: active
summary: saas vs self_hosted, plus the installed_on dimension.
created: '2026-05-07'
updated: '2026-05-07'
---
# Deployment modes

Antirion ships in exactly two deployment modes. "saas" is the multi-tenant managed offering operated by Antirion staff; platform-operator surfaces (EPIC-013) are visible only to Antirion staff accounts and never to tenant workspaces. "self_hosted" is deployed inside a customer's own infrastructure; the same platform-operator surfaces are visible only to principals holding the platform admin role on that install. The running mode is pinned at install time, surfaced to every service via config, and included on every audit record. Every feature that differs in scope, availability or data shape between the two modes declares its mode availability explicitly in its description. Features additionally declare `installed_on` when they differ by install type, with values `tenant_install` (default — deployed on every customer install regardless of mode), `antirion_console` (deployed only on Antirion's internally-operated console and never on customer installs) or `both`; absence of `installed_on` means `tenant_install`.

_Source: `_policies/non_functional_baseline.md#deployment-modes`._
