# EPIC-011 — Gateway request pipeline — read-only audit

Scope: `docs/requirements.yaml` lines 259–290 (epic), 1688–1928 (FEAT-135..FEAT-161), and 15338–18010 (STORY-312..STORY-386). Cross-referenced against `project.non_functional_baseline` (lines 13–38), `project.tech_stack_hints` (lines 39–58), the `models:` block (lines ~21000–24000), and EPICs 003, 004, 005, 006, 007, 008.

This is the runtime data plane — every line of `non_functional_baseline` applies. Findings below are anchored by line number and quoted text from `requirements.yaml`.

---

## Summary

EPIC-011 covers ingress dialects, translation, edge auth/limits, retry/timeout/failover, BYOK outbound auth, cost+idempotency, health/circuit-breakers, telemetry, streaming, multimodal, tools, size limits, graceful degradation, sampling, and ancillary endpoints (Files/Batches/Audio/Image/Moderation/Embeddings/Fine-tune/Egress/Private/Break-glass/Outbound limiter).

The biggest issues are:

1. **Performance-SLO conformance is broken in the FEAT-135/144 stories.** `STORY-312` claims a 15 ms gateway-overhead p95, `STORY-313` claims a 250 ms TTFT p95, `STORY-341` claims 10 ms per chunk, and `STORY-324`/`STORY-326` set a 2 ms p95 for edge auth+rate-limit alone — all of which exceed (or fully consume) the 1 ms p95 baseline at line 25. These would gate-fail every PR under the merge-gating rule on the same line.
2. **The `non_functional_baseline.shared_limiters` clause (line 20) cites the wrong feature numbers** — `FEAT-139` for "Edge rate limits" (actually `FEAT-138`) and `FEAT-142` for "Idempotency-Key lookup" (actually `FEAT-141`). Since the baseline is the doc's contract surface, these are not cosmetic — they make the limiter/idempotency invariants un-traceable to their owning feature.
3. **Three triple-overlapping circuit-breaker / failover / retry definitions exist** between EPIC-005 (`FEAT-051` + `STORY-121`) and EPIC-011 (`FEAT-139` + `FEAT-142`), with no story declaring the boundary or evaluation order.
4. **Cache, safety and budget pre-flight stages have no position declared in the EPIC-011 pipeline.** The pipeline ordering the prompt assumes (auth → rate-limit → idempotency → safety → cache → routing → retry → translation) is nowhere defined — `FEAT-148` references `CacheEntry` but no AC ties cache lookup or `EPIC-007`/`EPIC-008` enforcement to a pipeline phase.
5. **Streaming retry semantics are inconsistent across the baseline (line 31), `STORY-313` and `STORY-327`.**
6. **Several broken cross-references** (`STORY-385 → STORY-394`, `STORY-386 → FEAT-101`, `STORY-327 → STORY-134`).
7. **Mode availability is not declared** on `FEAT-160` (break-glass), `FEAT-159` (PrivateLink), `FEAT-158` (egress proxy) — `non_functional_baseline.deployment_modes` (line 36) requires every feature that differs in scope between modes to declare mode availability explicitly.
8. **Data-model gaps:** `IngressDialect`, `RateLimit`, `IdempotencyKey`, `CircuitBreaker`, `RetryPolicy`, `Timeout` are referenced conceptually but **not modeled**; `AlertRule.type` and `AlertRule.provider_id` referenced by `STORY-386` do not exist on `AlertRule`.

The full breakdown follows.

---

## Critical

### C1 — `STORY-312` p95 budget violates the gateway-added latency SLO by 15× (line 15418)

Quoted (line 15418):
> `p95 overhead (gateway decision + ingress/egress) <= 15 ms excluding upstream`

Baseline (line 25):
> `Gateway-added latency — ingress acceptance to first upstream-provider byte, excluding provider time — targets <= 250 µs p50, <= 1 ms p95, <= 5 ms p99 …`

Problem: the story sets a non-functional ceiling (15 ms p95) that is 15× higher than the baseline's 1 ms p95 ceiling. Per the same baseline line, "any regression on p95 added latency … blocks merge unless an exception is filed". The first OpenAI story would consume the entire SLO budget on its own.

Fix: delete the story-level p95 (or replace with a reference to the baseline). Same applies to the cookie-cutter `Additions to this phase must not breach the project performance_slo for gateway-added latency` line that already appears 40+ times elsewhere — it is the correct framing.

### C2 — `STORY-313` TTFT budget contradicts SLO and confuses TTFT with gateway-added latency (line 15469)

Quoted (line 15469):
> `TTFT p95 <= 250 ms excluding upstream`

Problem: "TTFT … excluding upstream" is incoherent — TTFT by definition includes the time until the first upstream byte reaches the client, so excluding upstream collapses it back to gateway-added latency, which the baseline pins to <= 1 ms p95. A 250 ms p95 either (a) silently includes upstream and contradicts the baseline reading rules, or (b) excludes upstream and is 250× the baseline ceiling.

Fix: split the assertion into "added latency p95 <= 1 ms (per baseline)" and "TTFT p95 <= upstream-TTFT + 1 ms".

### C3 — `STORY-341` per-chunk translation budget exceeds gateway-added SLO 10× (line 16634)

Quoted (line 16634):
> `The gateway translates each chunk to OpenAI's SSE format in under 10 ms`

Problem: each chunk traverses the gateway hot path. 10 ms per chunk on a 100-tps stream collapses to a 10× violation of the 1 ms p95 ceiling and forces buffering far above the "no buffering" claim immediately below at line 16661. Also clashes with `streaming` baseline line 31 ("proxied end-to-end without buffering").

Fix: replace with "translation per chunk runs in the same hot-path budget as a non-streaming request and contributes to the 1 ms p95 added-latency cap."

### C4 — `STORY-324`/`STORY-326` set a 2 ms p95 sub-budget that exceeds the entire SLO (lines 15977, 16053)

Quoted (line 15977 and 16053):
> `Edge auth and rate-limit decisions complete in under 2 ms p95`

Problem: the baseline's gateway-added p95 is 1 ms total. A 2 ms sub-budget for one phase necessarily breaks the whole-pipeline ceiling and contradicts the boilerplate two lines above ("must not breach the project performance_slo").

Fix: tighten to "<= 250 µs p95" (a fraction of the 1 ms whole-pipeline cap), or strike and rely on the boilerplate baseline reference.

### C5 — Baseline `shared_limiters` (line 20) cites the wrong feature IDs

Quoted (line 20):
> `shared_limiters: Edge rate limits (FEAT-139), budget counters (EPIC-008) and provider outbound limiters (FEAT-161) use a shared-store sliding-window implementation … Idempotency-Key lookup (FEAT-142) is cluster-wide and survives node loss.`

Problem (verified against lines 1717–1761):
- `FEAT-138` is "Edge authentication, authorization and rate limits" — the actual edge limiter.
- `FEAT-139` is "Retry, timeout and runtime failover" — has nothing to do with rate-limits.
- `FEAT-141` is "Cost attribution, metering and idempotency" — owns the Idempotency-Key path.
- `FEAT-142` is "Provider health and circuit breaker runtime" — has nothing to do with idempotency.

The baseline's most-cited gateway invariants therefore point at the wrong features. Every downstream document that traces to these IDs is wrong.

Fix: change `FEAT-139` → `FEAT-138` and `FEAT-142` → `FEAT-141` in line 20.

### C6 — `STORY-325` says "token-bucket"; baseline (line 20) says "sliding-window" (line 16020)

Quoted (line 16020):
> `Distributed token-bucket backed by Redis; lock-free hot path (CRC-sharded)`

Baseline (line 20):
> `… use a shared-store sliding-window implementation so horizontal scaling does not multiply a tenant's effective limit.`

Problem: token-bucket and sliding-window are different algorithms with different burst/fairness behavior. `STORY-384` (line 17909) and `STORY-386`/baseline say sliding-window. `STORY-325` and `STORY-326` (the edge-side feature) say token-bucket. The two limiter halves of the same product describe themselves differently.

Fix: pick one (the baseline-mandated sliding-window) and rewrite `STORY-325`'s non_functional accordingly.

### C7 — Streaming retry semantics conflict three ways

- Baseline line 31: `Mid-stream upstream failure retries only the remaining prefix.`
- `STORY-313` AC-002 (line 15450): `If configured, a retry is attempted on the next target with the request repeated from the beginning`
- `STORY-327` AC-002 (line 16080): `No retry is attempted on the same target. The stream is closed with an error event`

Problem: three contradictory rules for the same condition (mid-stream upstream failure). The "retry remaining prefix" claim in the baseline is also implementation-implausible since major LLM providers do not expose a resume/seek API.

Fix: collapse to a single rule. Recommend: "if no bytes have reached the client, retry per `RoutingRule.retries`; if any bytes reached the client, do not retry the same target, optionally fail over to a different target with full re-issue, otherwise close the stream with an error event."

### C8 — `STORY-385` links the operator from the rate-limit pressure card to a support-ticket story (line 17939)

Quoted (line 17939):
> `The card shows "Configure limits" with a link to STORY-394's screen`

Verification: `STORY-394` (line 18388) is "Attachments, follow-ups, close-as-resolved and rating on support tickets" under `FEAT-164`. Wrong target.

Fix: link to `STORY-382` (the configure-provider-rate-limits story).

### C9 — `STORY-386` cites `FEAT-101` for notification-channel routing (line 17993)

Quoted (line 17993):
> `An AlertEvent is created and the configured NotificationChannels fire (see FEAT-101)`

Verification: `FEAT-101` (line 1353) is "Runbooks". Notification channels is `FEAT-102` (line 1363).

Fix: change to `FEAT-102`.

### C10 — `STORY-327` cross-references `STORY-134` for failover (line 16091)

Quoted (line 16091):
> `If a fallback target exists, failover runs instead (STORY-134)`

Verification: `STORY-134` is part of `FEAT-058` (Prompt and template registry) — not failover. The intended target is `STORY-329` "Fall back through the target chain on terminal errors", or, if the EPIC-005 layer is meant, `STORY-121`.

Fix: change to `STORY-329` (intra-EPIC-011).

---

## Major

### M1 — Triple ownership of failover / circuit-breaker / fallback across EPIC-005 and EPIC-011

- `FEAT-051` (line 848, EPIC-005): "Circuit breaker and fallback" — `STORY-121` describes both fallback chain on 5xx and circuit opening on threshold.
- `FEAT-139` (line 1727, EPIC-011): "Retry, timeout and runtime failover" — `STORY-329` describes the same fallback cascade.
- `FEAT-142` (line 1753, EPIC-011): "Provider health and circuit breaker runtime" — `STORY-336` describes opening/closing circuits and propagation.

Problem: there is no story or feature description that says which feature is authoritative for the data structure (`RoutingRule.fallback`/`retries`), which one runs first at request time, or how `EPIC-005` "circuit-breaker" and `EPIC-011` "circuit-breaker runtime" share state. `STORY-121` and `STORY-336` both write the same `circuit_state` field on `ProviderHealth` (line 22679). At minimum two stories will race on the same Redis key.

Fix: declare one owner per concern. Suggested split:
- `EPIC-005` owns *configuration* of fallback chains and circuit thresholds (already in `RoutingRule`).
- `EPIC-011` `FEAT-139` owns *runtime evaluation* of retry+fallback per request.
- `EPIC-011` `FEAT-142` owns *health probing and circuit state machine* (writer of `circuit_state`).
- Strike `STORY-121` AC-002 and the FEAT-051 description's "circuit breaker" — leave only fallback config in EPIC-005.

### M2 — No story positions cache / safety / budget in the gateway pipeline

The epic description (line 261) explicitly omits cache and safety because they live in EPIC-006 and EPIC-007. But `non_functional_baseline.config_hot_reload` (line 21) names "safety and budget policies" as runtime concerns, and `FEAT-148` (`STORY-345`) reads `CacheEntry` during graceful degradation. Yet:

- No EPIC-011 story defines whether cache lookup precedes or follows routing/translation.
- No EPIC-011 story defines whether safety (`EPIC-007 FEAT-069..FEAT-081`) runs pre-translation, post-translation or post-routing.
- No EPIC-011 story defines whether budget enforcement (`EPIC-008 FEAT-084`) is a pre-flight check or an admission decision after routing.
- The `Request` model (line 21419) carries `pii_flag`, `safety_flag`, `cached`, `cost` — implying all four stages must run, but the order is left implicit.

Problem: implementations will diverge. Tail-latency, cost-attribution correctness and billing semantics depend on the order. (E.g. cache hit before safety = leaks unsafe content from history; safety before cache = wastes safety latency on cache hits.)

Fix: add a new `FEAT` (or extend the `EPIC-011` epic description) that fixes the canonical order: ingress → edge auth (`FEAT-138`) → size limit (`FEAT-147`) → rate-limit (`FEAT-138`) → idempotency lookup (`FEAT-141`) → input safety (`FEAT-070`/`FEAT-071`) → cache lookup (`FEAT-060`) → budget admission (`FEAT-084`) → routing (`FEAT-049`/`FEAT-050`) → translation (`FEAT-137`) → outbound auth (`FEAT-140`) → outbound limiter (`FEAT-161`) → upstream call → output safety → cost attribution (`FEAT-141`) → telemetry (`FEAT-143`).

### M3 — `FEAT-160` (Emergency break-glass scope) belongs in `EPIC-003`, not the runtime pipeline

`FEAT-160` (line 1903): "Create an audited, approval-gated, auto-expiring API key with elevated scope for incident response."

Problem: this is API-key lifecycle. `EPIC-003` already owns "API key lifecycle" (`FEAT-022`), "API key scopes and limits" (`FEAT-023`), "API key expiration and auto-revocation" (`FEAT-026`) and "Elevated API key scope approvals" (`FEAT-027`). The break-glass flow duplicates `FEAT-027`'s `Approval kind="key-elevated-scope"` (verified against `Approval.kind` at line 22628). Putting it in EPIC-011 also bypasses `EPIC-003`'s key-issuance UI and audit conventions.

Fix: move `FEAT-160` (and STORY-377..STORY-381) under `EPIC-003`. Reuse `FEAT-027`'s `Approval` flow rather than reimplementing the approval gate.

### M4 — `FEAT-157` (Fine-tune jobs), `FEAT-150` (Files), `FEAT-151` (Batches), `FEAT-153/154/155/156` (Audio/Image/Moderation/Embeddings) are dialect-API surfaces, not "runtime pipeline"

These features describe long-running job lifecycles or dialect-specific endpoints. They belong logically with `FEAT-135`/`FEAT-136` (ingress dialects) or as a sibling epic "Provider API surface". Their inclusion under "Gateway request pipeline" muddies the epic's promise (line 261 is about the *runtime that serves traffic*, not the API surface area).

Fix: either retitle `EPIC-011` to "Gateway request pipeline and provider API surface", or split into two epics with `FEAT-135..FEAT-149` + `FEAT-160..FEAT-161` in the pipeline epic and `FEAT-150..FEAT-159` in a new "Provider API endpoints" epic.

### M5 — `STORY-313` AC-002 retries from the beginning after partial bytes (line 15450)

Already covered in C7; re-listing because it also conflicts with the user-observable contract (clients of OpenAI's SDK assume a single response for a single request — repeating from the beginning duplicates content into the same SSE stream).

### M6 — `FEAT-148` graceful degradation has no residency check (line 1799–1806)

Baseline line 29: `Cross-region failover honors residency per FEAT-130 and fails closed rather than crossing a residency boundary.`

`STORY-345` (line 16790) returns a cached response when all providers are down. There is no AC that requires the cached response to be in the caller's residency region. If `CacheEntry` rows in another region are reachable (cross-region replication or shared Redis), graceful degradation will silently violate residency.

Fix: add an AC: "Cached response is served only if it is stored in the request's resolved residency region (`ResidencyConfig.region`)."

### M7 — Mode availability not declared on `FEAT-158`, `FEAT-159`, `FEAT-160`

`non_functional_baseline.deployment_modes` (line 36): "Every feature that differs in scope, availability or data shape between the two modes declares its mode availability explicitly in its description."

- `FEAT-158` Egress proxy (line 1886): no `mode:` field. Self-hosted environments often *require* an outbound proxy; saas does not. This differs.
- `FEAT-159` PrivateLink/VPC peering (line 1895): no `mode:` field. PrivateLink ingress is a saas concept; self-hosted has different network semantics.
- `FEAT-160` Break-glass scope (line 1903): no `mode:` field, despite stories `STORY-377`/`STORY-378`/`STORY-379` having different audience routing per mode (lines 17600, 17627, 17652).

Compare to `FEAT-178`/`FEAT-179`/`FEAT-180`/`FEAT-181`/`FEAT-182` (lines 2092–2138) which all declare `mode:`.

Fix: add `mode: both` (or `saas`/`self_hosted`) to each feature.

### M8 — `AlertRule` schema does not have the fields `STORY-386` requires (line 17989)

Quoted (line 17989):
> `An AlertRule of type "provider_rate_limit_pressure" with provider_id=anthropic, threshold=90 and for_duration_s=120`

`AlertRule` schema (line 22157) has `category`, `metric`, `scope` (string), `for_duration` (string like "5m") — but no `type` and no `provider_id`. `for_duration_s` is also typed differently from `for_duration: string` in the model.

Fix: either change AC-001 to use the existing fields (`category="provider_rate_limit_pressure"`, `metric=…`, `scope=Provider:anthropic`, `for_duration="2m"`), or extend `AlertRule` with `type` and `provider_id`. The former is consistent with how every other rule is described.

### M9 — `STORY-323` AC-001 conflicts with FEAT-141 cost attribution writes (line 15890)

Quoted (line 15890):
> `No Request row is written beyond the rejection metadata`

Problem: "rejection metadata" is undefined. Whether a `Request` row is written for unauthenticated traffic determines whether `FEAT-141` cost attribution (and `EPIC-004` analytics / `FEAT-024` per-key usage) can ever see auth-rejected traffic. The Request schema (line 21419) has every column nullable that would matter, so it can hold a "rejected" row, but `STORY-323` waves the question away.

Fix: pick one and put it in the AC: either (a) write a minimal `Request` with `status=401` and nulls everywhere, or (b) record the rejection on a separate `AccessLog` table (which doesn't currently exist).

### M10 — `STORY-377` notifies `Org.security_contact` but break-glass is mode-sensitive (line 17599)

Quoted (line 17599):
> `A creation notification is sent to Org.security_contact (falling back to Org.owner in saas and platform admin in self_hosted)`

Cross-check `non_functional_baseline.notifications_model` (line 37–38). The fallback there is `Org.owner` in saas and platform admin in self_hosted *when a tenant-contact field is unset*. This story applies the fallback unconditionally (it does not condition on `security_contact` being unset). This will silence the security-contact path even when configured.

Fix: condition on `Org.security_contact IS NULL`, then fall back per the baseline rule.

### M11 — `FEAT-149` trace sampling overlaps `FEAT-143` (lines 1807, 1762)

`FEAT-143` `STORY-340` AC-002 (line 16602) sets head-based sampling and rate. `FEAT-149` `STORY-347` does the same and adds tail-based and error-override. `TelemetryConfig` (line 23200) has `mode`/`rate`/`always_sample_on_error`/`tail_buffer_seconds` — both stories write the same row.

Fix: collapse `FEAT-149` into `FEAT-143`, or move sampling configuration entirely out of `FEAT-143` into `FEAT-149` so they don't both own `TelemetryConfig`.

---

## Minor

### m1 — Cookie-cutter non_functional lines paste idempotency claims onto unrelated stories (lines 16329, 16464, 16500)

Multiple stories carry `Idempotency-Key cache survives node loss and is cluster-wide; duplicate suppression holds under concurrent retries` even when the story does not touch idempotency (e.g. STORY-333 line 16329 cost attribution; STORY-336 line 16464 circuit breakers; STORY-337 line 16500 dashboard). Boilerplate copy-paste; harmless but noisy.

### m2 — `STORY-330` AC-002 generates `AlertEvent severity "warn"` but no `AlertRule` matches (line 16203)

`AlertEvent` rows belong to a parent `AlertRule` (per the EPIC-009 model). `STORY-330` raises an `AlertEvent` directly with no `AlertRule` configured. This bypasses the alert lifecycle.

Fix: emit a `Notification` directly, or pre-seed a system `AlertRule` for "no_provider_credential".

### m3 — `STORY-322` claims streaming images from object storage but no model captures the staged blob (line 15872)

Quoted: `Large images may be streamed from object storage to upstream without buffering in memory`. There is no model for inbound image staging in object storage; `FileObject` (line 23830) is the only adjacent thing and it's a different upload path.

Fix: either describe how the image makes it into object storage (and which model row tracks it) or strike the line — the `FEAT-145` AC already covers image handling.

### m4 — `STORY-339` "internal port not publicly exposed" 404s rather than 401/403 (line 16578)

Returning 404 from a separate listener for an unrelated public port reveals the listener exists. A pure listener separation should not respond at all on the public port; if the public port happens to terminate `/metrics`, 401 (or 403 with no body) is the more conventional answer.

Fix: state explicitly that `/metrics` is not bound on the public listener (so the request never reaches it) and remove the AC about a 404 response.

### m5 — `STORY-348..STORY-351` (Files) and `STORY-352..STORY-355` (Batches) are skeletal compared to the rest of EPIC-011

These are P1 P0-adjacent features but each has a single AC with no unhappy paths, no auth requirements (despite Files holding tenant data), no size/byte caps cross-referenced to `FEAT-147`. Expanding them to match the depth of `STORY-312`/`STORY-313` would close real gaps.

### m6 — `EPIC-011` description (line 261) lists "rate limits" separately from "edge auth" but the feature combines them into `FEAT-138`

Description-vs-features minor mismatch. Either rephrase the description to match `FEAT-138`, or split `FEAT-138` so the two surfaces are individually addressable in roadmaps.

### m7 — `STORY-378` 15-minute dedupe window is hard-coded (line 17628)

Quoted (line 17628): `Subsequent uses are aggregated into a 15-minute dedupe window`. This is a UX/policy decision and should be configurable on the break-glass approval, not hard-coded.

### m8 — `STORY-329` AC-002 returns 502 with `all_targets_failed` but the dialect-shaped error rule (`STORY-346`) is not invoked (line 16169)

`STORY-346` (line 16836) requires graceful-degradation responses to be dialect-shaped. `STORY-329` AC-002 does not say so. A multi-dialect client will see a non-dialect-conforming 502 here.

Fix: either route `all_targets_failed` through `FEAT-148` graceful degradation, or repeat the dialect-shape rule in `STORY-329` AC-002.

### m9 — `STORY-340` configures sampling within 60s, but baseline `config_hot_reload` is 30s (line 16609 vs line 21)

Quoted (line 16609): `TelemetryConfig is updated and takes effect within 60s`. Baseline (line 21): `propagate to every node within 30 seconds`.

Fix: tighten to "within 30 seconds (per `non_functional_baseline.config_hot_reload`)".

### m10 — `STORY-340` exists at P1 even though `FEAT-143` is P0 (line 1762)

Trace UI being P1 on a P0 feature is fine but worth flagging — many EPIC-011 ancillaries are P1 children of P0 parents (`STORY-326`, `STORY-340`, etc.). Confirm intent.

### m11 — Redundant "every phase has an explicit timeout" line on stories with no upstream call

Stories that never reach upstream (e.g. `STORY-317` endpoint enable/disable, `STORY-348..STORY-350` file CRUD against local storage) carry the "auth, translate, upstream, post-processing" boilerplate. Misleading on those stories.

### m12 — `STORY-385` `binding_layer` returned in API response but `ProviderRateLimitWindow.binding_layer` is computed each refresh — staleness window unspecified (line 17960 vs line 21354)

How fresh is the binding layer? Caller decisions depend on it.

---

## Cross-epic

### X1 — EPIC-005 routing/failover and EPIC-011 retry/failover/circuit-breaker overlap (M1, repeat for cross-epic visibility)

See M1. Resolution requires editing both epics in lockstep.

### X2 — EPIC-003 BYOK consumed correctly, but `STORY-330` AC-002 "no_provider_credential" never names how the workspace opts into "shared credentials" (line 16198)

Quoted: `the workspace does not allow shared credentials`. There is no `Org` field, no `BYOKCredential.shared` flag, and no `CatalogPolicy` knob (line 21363) that controls "shared credentials". Cross-reference is dead.

Fix: add the toggle to `CatalogPolicy` (e.g. `allow_shared_credentials: bool`) and reference it.

### X3 — EPIC-006 cache placement is undefined (M2 above)

See M2. Concretely: `FEAT-060` (per-model cache) configures backend/TTL/key-strategy but no story names the lookup point on the request path. `STORY-345` reads cache only as outage fallback — implying cache is *not* read on the happy path, which is the opposite of the entire EPIC-006 promise.

Fix: add an EPIC-011 AC that says "on the happy path, cache lookup runs after edge admission and before routing per `FEAT-060`'s key-strategy".

### X4 — EPIC-007 safety pipeline position is undefined (M2 above)

`EPIC-007` describes input safety, output safety and classification but no EPIC-011 story positions safety in the request path. The `Request.safety_flag` and `Request.pii_flag` are set somewhere — by which feature, in what order, on input vs output, is undeclared.

Fix: tie safety stages to a position in the EPIC-011 pipeline, ideally with the `FEAT-`-numbered stages from M2 above.

### X5 — EPIC-008 cost attribution uses `FEAT-141`, but EPIC-008 budget enforcement (`FEAT-084`) has no admission hook in EPIC-011

`FEAT-084` (line 1183, EPIC-008) sets soft/hard policies with actions including `block` and `downgrade`. The downgrade action would have to fire *before* routing/translation in the gateway pipeline. No EPIC-011 story names where it runs. (Note: prompt's "EPIC-008 FEAT-151 cost attribution" reference appears to be itself off — `FEAT-151` is Batches; cost attribution is `FEAT-141`.)

Fix: add an EPIC-011 AC for budget admission analogous to rate-limit admission; cite `FEAT-084`.

### X6 — EPIC-004 telemetry is in `FEAT-143` (not `FEAT-160` as the prompt suggested)

`FEAT-143` Request telemetry is the correct counterpart to `EPIC-004`. The trace UI in `STORY-340` overlaps `EPIC-004 FEAT-031..FEAT-038` request-log/analytics surfaces; the trace waterfall vs the request-log row should explain how they cross-link by `Request.id` ↔ OTel `trace_id`.

Fix: cross-link `STORY-340`'s waterfall to the EPIC-004 request log; ensure `Request.id` and OTel `trace_id` correspondence is explicit.

### X7 — `non_functional_baseline.tenant_isolation` (line 34) requires per-tenant concurrency caps; no EPIC-011 story enforces this

Baseline: `Per-tenant quotas bound concurrency, CPU-seconds, queue slots and storage so a noisy tenant cannot degrade others.`

EPIC-011 has rate-limit (rpm/tpm) but no concurrency cap. `concurrency_and_backpressure` baseline (line 19) names a per-node cap, not a per-tenant cap.

Fix: add an AC under `FEAT-138` or a new feature for per-tenant concurrency.

---

## Missing / dangling references

**(a) Cited feature/story IDs with no matching definition or wrong target**

| Citing line | Cited ID | Issue |
|---|---|---|
| 16091 (`STORY-327`) | `STORY-134` | `STORY-134` exists but is a prompt-registry story under `FEAT-058`. Intended target: `STORY-329` (intra-epic failover). |
| 17939 (`STORY-385`) | `STORY-394` | `STORY-394` exists but is a support-ticket story under `FEAT-164`. Intended target: `STORY-382` (configure provider rate limits). |
| 17993 (`STORY-386`) | `FEAT-101` | `FEAT-101` is "Runbooks". Intended target: `FEAT-102` (Notification channels). |
| 20 (baseline) | `FEAT-139` | `FEAT-139` is retry/timeout/failover, not edge rate limits. Intended: `FEAT-138`. |
| 20 (baseline) | `FEAT-142` | `FEAT-142` is health/circuit, not idempotency. Intended: `FEAT-141`. |

**(b) Dependency feature implied by narrative but never declared**

| Citing line | Implied feature | Where it should exist |
|---|---|---|
| 261 (epic) and the whole pipeline | "Pipeline ordering / dispatch" feature | No `FEAT-` describes the canonical request-stage order; M2 above. |
| 16198 (`STORY-330` AC-002) | "Allow shared provider credentials" toggle | No `Org`/`CatalogPolicy` field exists; X2 above. |
| 16198 (`STORY-330` AC-002) | Per-tenant concurrency cap (baseline line 34) | No EPIC-011 story owns it; X7 above. |
| 16808 (`STORY-345`) | Residency check on cached fallback | `FEAT-130` referenced by baseline line 29 but not by `FEAT-148`; M6 above. |
| 16329 etc. | An `IdempotencyKey` model | Stories assert "Idempotency entries stored in Redis with 5-minute TTL" but no `IdempotencyKey` row is modeled. |
| 16133 etc. | A `RetryPolicy` / `Timeout` model (or fields on `RoutingRule` distinct from `timeout_ms`/`retries`) | `RoutingRule` has `timeout_ms: int` and `retries: int` only — no per-phase timeouts despite `STORY-328` AC-001/AC-002/AC-003 requiring connect / first-byte / stream-idle separately. |
| 16135 etc. | `IngressDialect` model | `Request.endpoint` is a string but no model captures the dialect-set or the dialect's translation matrix. `STORY-317` enables/disables endpoints via `AuditLog "endpoint.disable"` but no row models the endpoint state — config drift risk. |
| 17600 etc. | A `BreakGlassKey` extension on `ApiKey` (or a `mode` flag) | `STORY-377`/`STORY-378` tag requests `break_glass=true` but no field on `ApiKey` records that the key is a break-glass key. The `ApiKey.type` field at line 21097 lists only `service|user|ephemeral`. |
| 22679 | `circuit_state` only carries provider-scope | `STORY-336` AC-003 asks for per-model breakers, but `ProviderHealth.circuit_state` is provider+region scoped. The per-model state has nowhere to live. |

**(c) Features the epic's scope promises but are absent from the features list (or not located in this epic)**

| Epic-text promise | Status |
|---|---|
| "ingress dialects" (line 261) | Partially: dialects defined per `FEAT-135`/`FEAT-136`; no `IngressDialect` registry/model. |
| "translation" (line 261) | `FEAT-137` present. |
| "edge auth, rate limits" (line 261) | `FEAT-138` covers both — minor wording mismatch (m6). |
| "retries and timeouts" (line 261) | `FEAT-139` present. |
| "runtime failover" (line 261) | `FEAT-139` present, overlapping `FEAT-051` (M1). |
| "outbound provider auth" (line 261) | `FEAT-140` present. |
| "cost attribution" (line 261) | `FEAT-141` present. |
| "idempotency" (line 261) | `FEAT-141` present. |
| "health and circuit breaker" (line 261) | `FEAT-142` present, overlapping `FEAT-051` (M1). |
| "telemetry" (line 261) | `FEAT-143` + `FEAT-149` (overlap M11). |
| Pipeline-stage ordering | Promised by the title "Gateway request pipeline" but never written down (M2). |
| Safety stage position in the pipeline | Not promised in epic description, but cannot be omitted given `Request.safety_flag` and `Request.pii_flag`. (M2 / X4) |
| Cache stage position in the pipeline | Same — not promised, but `Request.cached` is meaningless without it. (M2 / X3) |
| Budget admission gate | Same — `FEAT-084` has `block` and `downgrade` actions that must fire pre-routing. (X5) |
| Per-tenant concurrency cap | Required by baseline `tenant_isolation` (line 34); absent from EPIC-011. (X7) |
| Mode availability declarations on `FEAT-158`/`FEAT-159`/`FEAT-160` | Required by baseline `deployment_modes` (line 36); absent. (M7) |
| `IngressDialect`, `RateLimit`, `IdempotencyKey`, `CircuitBreaker`, `RetryPolicy`, `Timeout` data models | Referenced conceptually; not modeled. (b) |

---

## Recommended order of fixes

1. Correct the baseline `shared_limiters` references (C5) — single line edit, unblocks every downstream traceability check.
2. Strip story-level p95 budgets that contradict the baseline (C1, C2, C3, C4).
3. Fix dangling cross-refs (C8, C9, C10).
4. Resolve the streaming-retry trinity (C7) and the limiter-algorithm split (C6).
5. Add the canonical pipeline-ordering feature (M2 / X3 / X4 / X5).
6. Resolve EPIC-005 ↔ EPIC-011 failover/circuit ownership (M1 / X1).
7. Move `FEAT-160` to EPIC-003; add mode availability on `FEAT-158`/`FEAT-159`/`FEAT-160` (M3 / M7).
8. Reconcile `AlertRule` schema with `STORY-386` (M8).
9. Backfill dependency models — `IdempotencyKey`, per-phase `Timeout`, per-model `circuit_state` (b).
10. Tighten ancillary skeletal stories (m5, m11).
