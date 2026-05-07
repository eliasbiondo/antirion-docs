---
id: gw_glossary_00005
type: glossary
title: Budget counter
lifecycle: active
summary: Per-Budget shared-store counter that the hot path consults before admitting a request; reconciled to the persisted ledger by FEAT-186.
created: '2026-05-07'
updated: '2026-05-07'
---
# Budget counter

A per-`Budget` counter held in the shared limiter store. Gateway budget admission (FEAT-187) reads this counter on the hot path; if the hard cap is reached the request is rejected with HTTP 402 (`error_code="budget_exhausted"`). Counter write-back (FEAT-186) reconciles live counters against the persisted Request ledger on a worker cadence and raises `budget.counter.drift` on deviation.

See FEAT-186, FEAT-187, FEAT-197 (budget→AlertRule bridge) and `_policies/non_functional_baseline.md#shared-limiters`.
