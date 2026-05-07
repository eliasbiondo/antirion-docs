---
id: gw_policy_00002
type: policy
title: Non-functional baseline
lifecycle: active
summary: Cross-cutting non-functional standards every service and story inherits.
created: '2026-05-07'
updated: '2026-05-07'
---
# Non-functional baseline

Cross-cutting non-functional standards every service and story inherits. Individual stories only restate these when they deviate. Anything stated here is implicit in every acceptance criterion even when not spelled out.

## Deployment Model

Gateway data plane, control-plane API and background workers are each deployed as a horizontally scalable cluster of identical replicas behind a load balancer, scaled independently. No replica is a singleton. Loss of a single AZ or replica is transparent to callers.

## Statelessness

Gateway and control-plane API nodes hold no request, session, routing or budget state in local memory or disk beyond the lifetime of a single request. All shared state — sessions, rate-limit and budget counters, idempotency keys, circuit-breaker state, cached responses, trusted-browser records, approval tokens — lives in Redis, Postgres or ClickHouse so any node can serve any request and a rolling restart is transparent.

## Horizontal Scaling

Each fleet auto-scales on CPU, request rate and queue depth. Capacity plans hold the performance SLO under load with headroom for a 3x traffic burst without shedding. A node-loss event never loses more than that node's in-flight requests.

## Workers

Background work — metric aggregation, request-log ingestion, webhook delivery, cache eviction, retention sweeps, export generation, anomaly scoring, fine-tune job polling, SCIM sync, audit sink fan-out, notification delivery — runs in a dedicated worker fleet that consumes durable queues with visibility timeouts, exponential-backoff retry, poison-message dead-letter queues and at-least-once semantics. Handlers must be idempotent. Worker fleet health is surfaced by FEAT-170 (platform-operator observability) - FEAT-167 has been retired; tenant-admin cancel/requeue of owner_org_id-matched WorkerJob rows lives under FEAT-170 STORY-405.

## Concurrency And Backpressure

Each node enforces a max concurrent request cap and returns 429 or 503 with Retry-After when saturated; streaming connections count against the cap. Upstream provider pools, database connection pools and queue consumer pools are bounded with explicit acquire timeouts. Saturation on any tier surfaces as its own alert signal rather than bleeding into latency.

## Shared Limiters

Edge rate limits (FEAT-138), budget counters (EPIC-008) and provider outbound limiters (FEAT-161) use a shared-store sliding-window implementation so horizontal scaling does not multiply a tenant's effective limit. Idempotency-Key lookup (FEAT-141) is cluster-wide and survives node loss.

## Config Hot Reload

Routing rules, model catalog, safety and budget policies, rate limits, alert rules and feature flags propagate to every node within 30 seconds without restart and without dropping in-flight requests.

## Graceful Shutdown

On SIGTERM a node deregisters from the load balancer, stops accepting new work, drains in-flight requests up to a configurable timeout (default 60 seconds for API, 10 minutes for workers), flushes buffered telemetry and exits zero. Streaming connections receive a terminal event and close cleanly.

## Health Checks

Every service exposes a liveness probe (process up) and a readiness probe (dependencies reachable, config loaded, migrations applied, circuit-breaker state hydrated). Not-ready nodes are excluded from load-balancer routing and from queue consumption.

## Zero Downtime Deploy

Rolling and blue/green deploys complete with zero dropped requests and zero dropped stream connections. Schema migrations are backward-compatible for at least one release so the previous and next binary can run simultaneously against the same database.

## Performance Slo

Gateway-added latency — ingress acceptance to first upstream-provider byte, excluding provider time — targets <= 250 µs p50, <= 1 ms p95, <= 5 ms p99 under nominal load and <= 3 ms p95 at 80% node utilization. Each gateway node sustains >= 10,000 rps of non-streaming traffic or >= 20,000 concurrent streams at <= 70% CPU before autoscaling triggers, with a resident memory footprint under 256 MB at that load. These numbers are chosen to beat the best public Rust (Helicone) and Go (Bifrost) LLM-gateway benchmarks on identical hardware, and are the explicit baseline the implementation is designed against. A continuous-benchmark suite runs on every PR; any regression on p95 added latency, rps per node or memory footprint blocks merge unless an exception is filed with the rationale.

## Performance Implementation Notes

The gateway data plane is implemented in Rust on tokio and axum (or hyper directly) as a single statically linked binary. The hot path avoids heap allocation and locks — routing tables, policy caches and rate-limit shards are lock-free or read-copy-update; streaming uses zero-copy bytes. JSON uses simd-json on ingress and serde_json only on the slow path. TLS uses rustls with session resumption. Connection pools to upstream providers are bounded, keyed by provider+region, and warm. Telemetry emission is non-blocking and batched.

## Reference Benchmarks

The reference harness is the ferro-labs/ai-gateway-performance-benchmarks repo extended with internal cases — mock 60 ms upstream, identical hardware, 1/10/100/500/1000/2000 virtual users, non-streaming and streaming mixes. Competitors baselined on the same hardware include Bifrost (Go), Helicone (Rust), LiteLLM (Python) and Kong AI Gateway (Lua). Antirion's merge-gating numbers must come out ahead of every competitor on p50, p95 and p99 added latency, sustained rps per node, and memory per concurrent connection.

## Availability Slo

Control-plane API targets 99.9% monthly availability; gateway data plane targets 99.95%. Error budgets are tracked per FEAT-106 and gate release promotion when burned.

## Multi Region And Dr

Every stateful dependency (Postgres, Redis, ClickHouse, object store, queue broker — NATS JetStream) is deployed across at least three availability zones with automatic failover. Control plane targets RPO <= 5 minutes and RTO <= 30 minutes; gateway data plane targets RPO <= 1 minute and RTO <= 10 minutes. Disaster recovery is exercised at least quarterly. Cross-region failover honors residency per FEAT-130 and fails closed rather than crossing a residency boundary.

## Data Durability

Postgres uses synchronous replication to at least one standby. ClickHouse ingestion targets >= 99.99% row durability for the request log; ingestion gaps trigger the ingestion-health alert. Redis shards holding budget, rate-limit or idempotency state use AOF with appendfsync everysec; pure cache shards are best-effort.

## Streaming

SSE and chunked responses are proxied end-to-end without buffering. Mid-stream upstream failure retries per RoutingRule.retries only when no bytes have reached the client; once any bytes have been streamed, the same target is not retried - an optional fallback target may reissue the full request, otherwise the stream closes with an error event. Long streams do not depend on sticky sessions — the L7 load balancer drains connections on deploy.

## Observability

Every request, job and background task emits an OpenTelemetry span with Request-Id, org_id, team_id, user_id, model and provider. Structured JSON logs correlate by Request-Id. Prometheus metrics cover RED (rate, errors, duration) for request paths, USE (utilization, saturation, errors) for resources and queue depth / age / retry-count for workers.

## Security

TLS 1.2+ is required on every externally exposed endpoint; internal service-to-service traffic uses mTLS. Secrets live in the configured KMS (with FEAT-133 CMK where enabled) and never appear in logs, telemetry or persisted payloads. Audit log writes are append-only with tamper-evident hashing.

## Tenant Isolation

Every query is partitioned by org_id. Per-tenant quotas bound concurrency, CPU-seconds, queue slots and storage so a noisy tenant cannot degrade others. Tenant-isolation is continuously verified by FEAT-134.

## Portability

Services are stateless Linux containers that run identically on the reference Kubernetes deployment, the self_hosted Docker-Compose deployment and the managed saas. No component depends on a feature specific to a single cloud provider.

## Deployment Modes

Antirion ships in exactly two deployment modes. "saas" is the multi-tenant managed offering operated by Antirion staff; platform-operator surfaces (EPIC-013) are visible only to Antirion staff accounts and never to tenant workspaces. "self_hosted" is deployed inside a customer's own infrastructure; the same platform-operator surfaces are visible only to principals holding the platform admin role on that install. The running mode is pinned at install time, surfaced to every service via config, and included on every audit record. Every feature that differs in scope, availability or data shape between the two modes declares its mode availability explicitly in its description. Features additionally declare `installed_on` when they differ by install type, with values `tenant_install` (default — deployed on every customer install regardless of mode), `antirion_console` (deployed only on Antirion's internally-operated console and never on customer installs) or `both`; absence of `installed_on` means `tenant_install`.

## Notifications Model

Canonical audience roles for every event-notification story. Stories cite these roles instead of inventing local language, and acceptance criteria name the audience per deployment mode. Audience roles are (a) the acting principal (user_id), (b) the owning principal on the resource (Resource.owner_user_id or Team.lead_user_id), (c) the org-scoped contact fields on Org (security_contact, billing_contact, finance_contact, privacy_officer, primary_contact, tech_contact), (d) the platform operator — which resolves to Antirion staff in saas and to principals holding the platform admin role in self_hosted, (e) Antirion-staff-only sub-queues in saas (trust_and_safety, support, sre, dpo, renewals, legal) that have no counterpart in self_hosted. The collapse rules across modes are fixed and every story follows them unchanged. Tenant-scoped roles (a)(b)(c) behave identically in both modes. Platform-operator role (d) is Antirion staff in saas and platform admin in self_hosted. Antirion-staff sub-queues (e) exist only in saas; in self_hosted the same event routes to platform admin unless the customer has opted in to Antirion phone-home support for the event class (see FEAT-179). When a tenant-contact field is unset in self_hosted the event falls back to platform admin; when unset in saas the event falls back to Org.owner. Cross-tenant signals (isolation breaches, abuse heuristics, sustained anomalies) always reach Antirion trust_and_safety in saas and are silently dropped in self_hosted because the set of tenants is 1. Delivery channels per role are resolved by FEAT-102 notification-channels routing for user-addressable roles and by the platform operator's configured paging integration for (d) and (e). Every audit record on a notification-bearing event records the resolved audience list and the channel attempt, so routing correctness is diffable against this policy.
