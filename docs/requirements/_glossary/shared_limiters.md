---
id: gw_glossary_01K9DSQNKR1XKKFEBWMJBJH9H2
type: glossary
title: Shared limiters
lifecycle: active
summary: Edge rate limits, budget counters and provider outbound limiters share a sliding-window store so horizontal scaling does not multiply effective limits.
created: '2026-05-07'
updated: '2026-05-07'
---
# Shared limiters

Edge rate limits (FEAT-138), budget counters (EPIC-008) and provider outbound limiters (FEAT-161) share a sliding-window implementation in a shared store (Redis), so adding gateway nodes does not multiply a tenant's effective limit. Idempotency-Key lookup (FEAT-141) is cluster-wide and survives node loss.

See `_policies/non_functional_baseline.md#shared-limiters`.
