---
id: gw_policy_01K9DSR2A0VM5W8WJA8QKMM4SS
type: policy
title: Destructive action confirmation
lifecycle: active
summary: Type-to-confirm vs click-to-confirm policy for destructive actions.
created: '2026-05-07'
updated: '2026-05-07'
---
# Destructive action confirmation

High-impact destructive actions (delete project, delete org, delete alert rule with active fires, delete model with live traffic, delete team, delete personal account, offboard user, grant waiver above 50% of budget, force reset schedule change mid-cycle, purge cache, rotate org secret) require the user to type the target's name or slug to confirm. Low-impact reversible deletions (alias, saved view, draft rule, personal token) require a single click-confirm.
