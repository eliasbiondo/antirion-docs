---
id: gw_policy_00003
type: policy
title: Notifications model
lifecycle: active
summary: Canonical audience roles for every event-notification story.
created: '2026-05-07'
updated: '2026-05-07'
---
# Notifications model

Canonical audience roles for every event-notification story. Stories cite these roles instead of inventing local language, and acceptance criteria name the audience per deployment mode. Audience roles are (a) the acting principal (user_id), (b) the owning principal on the resource (Resource.owner_user_id or Team.lead_user_id), (c) the org-scoped contact fields on Org (security_contact, billing_contact, finance_contact, privacy_officer, primary_contact, tech_contact), (d) the platform operator — which resolves to Antirion staff in saas and to principals holding the platform admin role in self_hosted, (e) Antirion-staff-only sub-queues in saas (trust_and_safety, support, sre, dpo, renewals, legal) that have no counterpart in self_hosted. The collapse rules across modes are fixed and every story follows them unchanged. Tenant-scoped roles (a)(b)(c) behave identically in both modes. Platform-operator role (d) is Antirion staff in saas and platform admin in self_hosted. Antirion-staff sub-queues (e) exist only in saas; in self_hosted the same event routes to platform admin unless the customer has opted in to Antirion phone-home support for the event class (see FEAT-179). When a tenant-contact field is unset in self_hosted the event falls back to platform admin; when unset in saas the event falls back to Org.owner. Cross-tenant signals (isolation breaches, abuse heuristics, sustained anomalies) always reach Antirion trust_and_safety in saas and are silently dropped in self_hosted because the set of tenants is 1. Delivery channels per role are resolved by FEAT-102 notification-channels routing for user-addressable roles and by the platform operator's configured paging integration for (d) and (e). Every audit record on a notification-bearing event records the resolved audience list and the channel attempt, so routing correctness is diffable against this policy.

_Source: `_policies/non_functional_baseline.md#notifications-model`._
