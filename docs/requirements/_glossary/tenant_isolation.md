---
id: gw_glossary_01K9DSQPK05FXT40B1Z6KH0T9K
type: glossary
title: Tenant isolation
lifecycle: active
summary: Every query partitioned by org_id; per-tenant quotas; continuously verified by FEAT-134.
created: '2026-05-07'
updated: '2026-05-07'
---
# Tenant isolation

Every query is partitioned by `org_id`. Per-tenant quotas bound concurrency, CPU-seconds, queue slots and storage so a noisy tenant cannot degrade others. Tenant isolation is continuously verified by FEAT-134.

See `_policies/non_functional_baseline.md#tenant-isolation`.
