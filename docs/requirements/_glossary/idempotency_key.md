---
id: gw_glossary_01K9DSQRHG03P40BBKWBER8X0R
type: glossary
title: Idempotency key
lifecycle: active
summary: Cluster-wide Idempotency-Key lookup that lets the gateway dedupe retries; FEAT-141.
created: '2026-05-07'
updated: '2026-05-07'
---
# Idempotency key

An optional `Idempotency-Key` header on a gateway request causes the same response to be replayed for at-most-once semantics across retries. Lookup is cluster-wide and survives node loss; see FEAT-141 and `_policies/non_functional_baseline.md#shared-limiters`.
