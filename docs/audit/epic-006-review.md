# EPIC-006 Caching — requirements.yaml audit

Scope: `docs/requirements.yaml` — EPIC-006 (line 159), FEAT-060..FEAT-068 (lines 938–1027), STORY-142..STORY-156 (lines 8465–9199), plus cross-references to EPIC-005 (routing), EPIC-007 (safety), EPIC-008 (cost), EPIC-011 (gateway pipeline), the non-functional baseline (lines 13–38) and the data-model section (lines 20983–23590).

All line numbers are from `docs/requirements.yaml`.

---

## Summary

EPIC-006 is structurally coherent but has meaningful drift between the data model, the stories and the non-functional baseline. The worst issues are:

1. **Tenant isolation is not representable in the cache models.** `CacheEntry` (line 21776) carries no `org_id`, and `CacheConfig.model_id` is marked `unique: true` (line 21687) — org scoping is only transitive through `Model.org_id`. This contradicts `non_functional_baseline.tenant_isolation` (line 34: "Every query is partitioned by org_id") and the non-functional refrain repeated on every cache story ("Cache keys normalize … without cross-tenant leakage").
2. **STORY-155 writes to fields that do not exist on `CacheConfig`.** `eviction_policy` and `max_size_mb` (lines 9130–9131, 9154–9155) are set by the AC and API, but neither field is declared in the `CacheConfig` model (21680–21710). FEAT-068's core functionality has no backing schema.
3. **Invalidation actions operate on keys the `CacheEntry` schema cannot hold.** `InvalidationRule.action` includes `drop-user` (line 21821), but `CacheEntry` has no `user_id`. STORY-148 invalidates "cache entries tied to a rotated BYOK credential" (line 8803), but `CacheEntry` has no `byok_credential_id` or `provider_id`. STORY-144 speaks of "CacheEntries linked to the [semantic] config" (line 8621), but `CacheEntry` has no `semantic_cache_config_id`.
4. **Streaming × caching is never reconciled.** `non_functional_baseline.streaming` (line 31) requires end-to-end, non-buffered SSE. No story in EPIC-006 defines whether streamed responses can populate or be served from the cache, how the response body is reconstructed from a `CacheEntry` for a streaming client, or how partial-stream failures interact with cache writes.
5. **Redaction / cache coherence is not defined.** EPIC-007 redacts prompts inline (STORY-159, line 9305). Whether the cache key is built over the original or redacted prompt is unspecified — leading to a real risk of serving cached responses produced under one redaction policy after the policy has changed.
6. **URL conventions are inconsistent.** FEAT-060..064 use `/api/cache/...` (e.g. line 8505, 8568, 8755, 8876, 8989) while FEAT-066..068 use `/api/caching/...` (lines 9047, 9098, 9151). Same epic, two namespaces.
7. **Feature ↔ story priority mismatches** exist on FEAT-060 (P0/STORY-142 P1), FEAT-061 (P1/STORY-143 P2, STORY-144 P2), FEAT-063 (P1/STORY-147 P2), FEAT-067 (P0/STORY-154 P2).

Counts below: **9 Critical**, **13 Major**, **11 Minor**, **6 Cross-epic**, **7 Missing / dangling references**.

---

## Critical

### C-1. `CacheEntry` has no `org_id`; tenant isolation is not enforceable in the cache

- Location: model `CacheEntry`, lines 21776–21808.
- Quote (21786–21788): `- name: team_id / type: FK:Team / nullable: true`.
- Problem: `non_functional_baseline.tenant_isolation` (line 34) mandates that every query is partitioned by `org_id`. `CacheEntry` carries only `model_id` and a nullable `team_id`; org scoping is only transitive through `Model.org_id`. That breaks on (a) BYOK rotation invalidation, where STORY-148 needs a per-provider scope; (b) global browse/search endpoints (`GET /api/cache/entries`, line 8755) where the server-side filter-by-org cannot be expressed without a join; (c) partition keys for Redis shards. The invariant "without cross-tenant leakage" printed on every cache story's `non_functional` block is then aspirational rather than schema-enforced.
- Fix: add `org_id: FK:Org` (non-null) to `CacheEntry`, and require every read/write API to include it in the key/index. Index on `(org_id, model_id, key_hash)`.

### C-2. `CacheConfig.model_id` is declared `unique: true`, forbidding per-env/per-project/per-BYOK variants

- Location: lines 21686–21688: `- name: model_id / type: FK:Model / unique: true`.
- Problem: Combined with `Model` being org-scoped (line 21235), this forces exactly one cache config per model per org. There is no per-project, per-environment (`Request.env`, line 21449) or per-BYOK variant, even though STORY-152 explicitly envisions settings-level overrides (`CacheOverride`, line 21834). The `CacheOverride` scope enum (line 21842) is `team|key`, excluding `project` and `env` — yet cost, safety and budget policies are all project- and env-scoped elsewhere.
- Fix: either (a) drop `unique: true` and make `CacheConfig` (`model_id`, `scope`, `scope_id`) keyed; or (b) make `CacheOverride` the authoritative override surface and expand its scope enum to `team|key|project|env|byok`. Document the precedence order in FEAT-065.

### C-3. `STORY-155` sets `CacheConfig.eviction_policy` and `CacheConfig.max_size_mb`, fields that do not exist

- Location: STORY-155 lines 9130–9131 ("CacheConfig.eviction_policy becomes 'LRU' / CacheConfig.max_size_mb becomes 2048"), API body lines 9153–9155.
- Problem: `CacheConfig` declares `id, model_id, backend, key_strategy, ttl_sec, max_entry_kb, max_items, token_discount, enabled, note` (21680–21710). Neither `eviction_policy` nor `max_size_mb` is present. FEAT-068's P2 stories are un-implementable against the declared schema.
- Fix: add `eviction_policy: string` (enum `LRU|LFU|TTL-first`), `max_size_mb: int nullable` to the `CacheConfig` model; or move them to a separate `CacheEvictionPolicy` model keyed by `cache_config_id`.

### C-4. `InvalidationRule.action = "drop-user"` is impossible against the current `CacheEntry` schema

- Location: `InvalidationRule.action` enum at line 21821 ("drop-matching|drop-user|refresh-oldest|drop-team|drop-all"); STORY-150 AC-001 lines 8858–8865.
- Problem: `CacheEntry` (21776–21808) has no `user_id` column, so "All CacheEntries for that user are deleted" (line 8864) cannot be executed. `drop-team` is executable because `team_id` exists; `drop-user` is not.
- Fix: add `user_id: FK:User, nullable: true` to `CacheEntry`, or drop `drop-user` from the `action` enum and document that user-scoped invalidation is not supported (which in turn breaks the "sensitive-data leak containment" promise in FEAT-064 description line 983).

### C-5. STORY-148 (BYOK rotation invalidation) has no per-provider/per-credential scope on `CacheEntry`

- Location: STORY-148 lines 8800–8822.
- Quote (8813–8814): "Matching CacheEntry rows for the affected provider are invalidated".
- Problem: `CacheEntry` has no `provider_id`, `byok_credential_id` or `api_key_id`. The invalidation is unimplementable without scanning every entry and joining to the request log — which is neither "automatic" nor fast. STORY-148's AC-001 is effectively vacuous.
- Fix: either add `provider_id` (and optionally `byok_credential_id`) to `CacheEntry`, or redefine STORY-148 as an async purge keyed off `Request.provider_id` / `Request.api_key_id` via the request log, and clarify the eventual-consistency window.

### C-6. Streaming × cache is never specified; contradicts the non-functional baseline

- Location: baseline line 31 (`streaming`); none of STORY-142..156 discusses streaming.
- Quote (31): "SSE and chunked responses are proxied end-to-end without buffering."
- Problem: A cache hit must replay a completed body. A cache write on a stream requires buffering the full response — which the baseline forbids on the forward path. Requests have `Request.streamed: bool` (line 21483) and the cache has no `streamed: bool`. Semantics are undefined for: (a) can a streaming request produce a `CacheEntry`? (b) on hit, does the gateway synthesize SSE framing from a stored body? (c) is `ttft_ms` populated for a cache hit? (d) does keep-alive honor the 15 s cadence from STORY-341 (line 16635)?
- Fix: add an explicit story to FEAT-060 ("Cache semantics for streaming responses") that defines: write path buffers in worker-side storage only if the complete response is accepted; hit path re-frames as SSE with an explicit `cached: true` SSE comment; no sticky-session requirement; interaction with FEAT-144.

### C-7. Redaction / cache coherence across EPIC-007 is undefined

- Location: STORY-159 lines 9305–9339 (PII inline redaction); STORY-145 lines 8654–8685; `non_functional_baseline.security` line 33.
- Problem: STORY-159 redacts the outbound prompt. The cache key must be defined either over the original prompt (then two tenants with identical inputs but different redaction rules share cache entries, which leaks redaction-differentiated content) or the redacted prompt (then turning off redaction later silently continues to serve responses generated from a redacted prompt). No story defines which. Additionally, when `SafetyEvent.action = "block"` (STORY-159 AC-002, line 9323–9331), a `CacheEntry` must not be written — not stated anywhere.
- Fix: add a short story under FEAT-060 or cross-reference in STORY-142 nonfunctional: (a) cache keys are computed after safety/redaction transforms have been applied; (b) `SafetyEvent.action ∈ {block}` suppresses cache writes; (c) changes to `DetectionRule` or `TeamSafetyPolicy` invalidate affected entries — ties into FEAT-064 `InvalidationRule.match` JSON.

### C-8. Cache-warmup bypasses safety and cost gates without stating so

- Location: STORY-154 lines 9066–9113.
- Quote (9083): "Each segment is issued as a non-billable cache write request, subject to the segment's TTL".
- Problem: The story does not say whether warmup requests: (a) run safety detectors (FEAT-070..081); (b) count against budgets (EPIC-008); (c) honor residency (FEAT-130); (d) respect tenant isolation when populating CacheEntries that have no tenant column (C-1); (e) consume BYOK credentials (then the "non-billable" claim is wrong because the upstream provider bills the customer). FEAT-067 is P0; the story is P2 — the most important bypass surface for safety/cost is the lowest-priority story.
- Fix: rewrite STORY-154 to state: warmup requests run the full safety and budget pipeline; "non-billable" means only that Antirion-side markup is zero, not that provider charges are zero; residency is honored; the `CacheWarmupJob` model (line 22928) records which API key / BYOK executed the warm writes.

### C-9. Purge-cache destructive confirmation policy is partially violated by STORY-147 "Invalidate all in view"

- Location: baseline line 5: "High-impact destructive actions (… purge cache …) require the user to type the target's name or slug to confirm"; STORY-147 AC-002 lines 8745–8752.
- Quote (8750): "I click 'Invalidate all in view' and confirm".
- Problem: A bulk invalidation by model is semantically a partial purge but STORY-147 AC-002 only requires a plain "confirm". STORY-275 (line 14234) correctly requires a typed slug for the workspace-wide purge, demonstrating the policy exists. Inconsistent enforcement.
- Fix: STORY-147 AC-002 should require typed confirmation of the model slug (or team slug when scoped to a team) before a bulk invalidation of > N entries. Pick a threshold (e.g. 100) and state it.

---

## Major

### M-1. `STORY-144` deletes a `SemanticCacheConfig` but the link from `CacheEntry` does not exist

- Location: STORY-144 AC-002 lines 8613–8621; `CacheEntry` model 21776–21808.
- Quote (8621): "Existing CacheEntries linked to the config are dropped or retained per retention policy".
- Problem: `CacheEntry` has no `semantic_cache_config_id`. There is no way to "link" entries to the config. The only way to approximate the link is `(team_id, model_id, backend='semantic')`, but that is not unique if a team later creates a new semantic config.
- Fix: add `semantic_cache_config_id: FK:SemanticCacheConfig, nullable: true` to `CacheEntry`, or redefine AC-002 to scope by `(team_id, model_id)` and accept that a replacement config inherits entries.

### M-2. `key_strategy` has no enum; drift between "canonical" (STORY-142 AC-001) and the epic's "prompt-prefix" vocabulary

- Location: EPIC-006 description line 161 ("Exact, prompt-prefix and semantic caching"); STORY-142 AC-001 line 8479 (`key strategy "canonical"`); `CacheConfig.key_strategy` field at lines 21692–21693 (no enum description).
- Problem: The epic names three *backends*: exact, prompt-prefix, semantic. The `CacheConfig.backend` enum in the description is `exact|prompt|semantic` (line 21691). `key_strategy` is a separate dimension where the only cited value is "canonical". Neither field is enumerated. A reader cannot tell whether `backend=prompt` with `key_strategy=canonical` is the prompt-prefix cache or a different thing.
- Fix: enumerate `backend` as `exact|prompt_prefix|semantic` and `key_strategy` (at least `canonical|raw|normalized-semantic`). Align the epic description to the enum.

### M-3. URL namespace split: `/api/cache/*` vs `/api/caching/*`

- Location: FEAT-060..064 use `/api/cache/...` (e.g. 8505, 8513, 8568, 8755, 8770, 8778, 8876, 8891, 8989); FEAT-066..068 use `/api/caching/...` (9047, 9098, 9151).
- Problem: No justification for the split within a single epic. Clients and the OpenAPI surface will have two parallel roots.
- Fix: pick one (the rest of the product uses the short singular form — e.g. `/api/safety`, `/api/routing`, `/api/analytics`), and rewrite lines 9047, 9098, 9151 accordingly.

### M-4. Feature/story priority mismatches

- Location:
  - FEAT-060 P0 (line 942) vs STORY-142 P1 (line 8472).
  - FEAT-061 P1 (line 953) vs STORY-143 P2 (line 8544) and STORY-144 P2 (line 8599). STORY-145 is P1 (line 8661) — consistent.
  - FEAT-063 P1 (line 973) vs STORY-147 P2 (line 8734). STORY-148, STORY-149 are P1.
  - FEAT-067 P0 (line 1013) vs STORY-154 P2 (line 9073).
- Problem: A feature's priority is the max priority of its stories. A P0 feature whose only story is P2 is not a P0 feature.
- Fix: bring the feature and its highest-priority story into alignment. For FEAT-067 specifically — warmup is almost certainly not P0; downgrade to P1 or P2.

### M-5. `PromptSegment` "retired" status confused with "cold"

- Location: STORY-146 AC-002 lines 8704–8710; model `PromptSegment.status` enum at line 21772.
- Quote (8708–8710): "The previous version v7 is marked retired / Its status becomes 'cold' and its TTL drops to 0".
- Problem: Enum is `hot|warm|cold|retired`. A segment that is retired has status `retired`, not `cold`. The AC conflates the two.
- Fix: set status to `retired` (not `cold`) when a new version supersedes the old.

### M-6. `CacheConfig.token_discount` vs `Model.cache_price` — which drives billing?

- Location: `CacheConfig.token_discount` at lines 21701–21702; `Model.cache_price` at lines 21267–21269; STORY-145 AC-001 lines 8664–8670; STORY-332 lines 16298–16302.
- Quote (8670): "The Request.cache_cost field reflects the cache price, not the full input/output price".
- Quote (16302): `cost = (cache_tokens * cache_price + non_cache_input * in_price + output_tokens * out_price) / 1,000,000`.
- Problem: Two pricing knobs — `CacheConfig.token_discount` and `Model.cache_price` — both touch the cost of a cached read. The cost formula cited in STORY-332 uses only `cache_price`. `token_discount` appears to be unused.
- Fix: either (a) delete `CacheConfig.token_discount` and document that cache cost is driven by `Model.cache_price` (with `ModelPricingHistory`); or (b) keep `token_discount` and state that effective cache cost = `cache_price * (1 - token_discount)`. Reconcile with STORY-332.

### M-7. Cache reads bypass the cost pipeline — no story pins the contract

- Location: STORY-145 AC-001 (8664–8670); `Request.cache_cost` description at 21470–21472.
- Problem: On a cache hit, `input_tokens`/`output_tokens` still need to be attributed. Are the tokens counted as "cache_tokens" (per STORY-332 formula) or as zero? `Request.input_cost` / `output_cost` / `cache_cost` decomposition is not defined for the hit case. Budgets (EPIC-008) and cost analytics (FEAT-031, line 739: "input/output/cache decomposition") depend on this.
- Fix: add AC-003 to STORY-145 stating: on a cache hit, `input_cost` and `output_cost` are zero, `cache_cost = tokens * cache_price / 1e6` (or `token_discount` variant per M-6), and `Request.cached = true`.

### M-8. `CacheOverride` precedence rules undefined

- Location: STORY-152 lines 8967–9010; model at 21834–21859.
- Problem: `CacheOverride.scope` is `team|key`. If a team-scoped override disables cache and a key-scoped override in the same team re-enables it, which wins? What about team-override vs `CacheConfig` default? No precedence spec. `CacheOverride.setting: string` is not enumerated — any key? typo-susceptible.
- Fix: define precedence (most-specific wins: key > team > model default), enumerate `setting` to the union of `CacheConfig` mutable fields plus `enabled`, and state that the resolved cache config is cached and honors `config_hot_reload` SLA (line 21).

### M-9. `POST /api/cache/invalidate` body has no enumerated scope

- Location: STORY-147 lines 8777–8789.
- Quote (8781–8782): `scope: string / target_id: uuid`.
- Problem: Valid scopes are not listed. Presumably `model|team|key|org` but undefined. A missing enum invites cross-tenant purge bugs.
- Fix: declare the scope enum and state that `org` requires platform-operator privileges (or match the destructive-action typed-slug policy).

### M-10. Permission model for cache endpoints is underspecified

- Location: STORY-147 (8727–8797), STORY-150 (8848–8906), STORY-152 (8967–9010); scope "cache.read" referenced in passing at STORY-017 line 4621.
- Problem: A "support engineer" role invalidates entries (STORY-147 narrative). There is a `cache.read` scope but no `cache.invalidate` / `cache.override` / `cache.admin` scope anywhere. DELETE endpoints list 401/404 but mostly not 403, while POST/PATCH do — asymmetry.
- Fix: enumerate the cache-related API-key scopes (`cache.read`, `cache.invalidate`, `cache.admin`, `cache.overrides.write`), and add 403 to every DELETE.

### M-11. Eviction events have no model

- Location: STORY-156 AC-001 line 9185.
- Quote: "An eviction event is written with reason (policy|ttl|size|safety_policy_change|manual_purge) and rule_id if applicable".
- Problem: No `CacheEvictionEvent` / `EvictionLog` model is defined anywhere in the models section (20983–23590). "Written" where? To `AuditLog`? To a dedicated table? The UI in AC-002 (9186–9193) reads "last 24h of events" — a query against what?
- Fix: define a `CacheEvictionEvent` model with `id, cache_entry_id (denormalized — entry is gone), model_id, org_id, reason, rule_id nullable, size_kb, ttl_remaining_sec, evicted_at`.

### M-12. "cache write that triggered eviction" and "eviction never drops an entry written in the last 60 seconds" collide

- Location: STORY-155 non_functional line 9166.
- Quote: "Eviction never drops an entry that was written in the last 60 seconds".
- Problem: Combined with `max_size_mb` (line 9131) this means: under a write burst exceeding the ceiling within 60 s, the cache must exceed `max_size_mb` rather than evict recent entries. There is no defined behavior — reject writes? Queue them? Bypass the ceiling? FEAT-068 description (line 1021) says "size-based eviction limits" full stop.
- Fix: pick one and say it. Preferred: bypass the ceiling until the 60 s window passes, then catch up. Cap the excess at a second, higher ceiling (e.g. 120% of `max_size_mb`).

### M-13. `CacheEntry.key_preview` has no length bound; PII risk

- Location: `CacheEntry.key_preview: string` at lines 21789–21790.
- Problem: "Preview" of a prompt key is a plaintext substring of the prompt. PII may end up in the cache browser without redaction, contradicting `RetentionConfig.pii_redaction_enabled` (line 22453) and the inline redaction story (STORY-159).
- Fix: document the truncation length, state that `key_preview` is generated from the *redacted* prompt (or hashed), and gate the browser behind `cache.read` + a PII-view capability (FEAT-075 reverse flow).

---

## Minor

### N-1. STORY-142 AC-001 "max entry 64 KB" implies units not declared on the field

- `CacheConfig.max_entry_kb: int` (line 21697) — unit encoded in name. Consistent with `max_size_mb` (M-3-style). OK but worth documenting precision (kilobytes = 1024 bytes or 1000?).

### N-2. STORY-143 `dim: int` in request body is redundant with `embed_model_id`

- Lines 8575–8577. The embedding model fixes the dimension. Accepting `dim` invites mismatch errors. Either derive from `embed_model_id` or validate.

### N-3. STORY-143 AC-002 "false-positive rate" has no source

- Line 8565. `SemanticCacheConfig` has no `fp_rate` column and no worker/feedback loop is defined. Where does the FP rate come from? Presumably user feedback on the request drawer — not connected anywhere.

### N-4. STORY-146 hotness threshold is hard-coded

- Line 8698: "A named PromptSegment has been read >= 50 times in the last hour".
- The threshold should be a model config (`PromptSegment.hot_threshold` or a global).

### N-5. STORY-152 AC-001 override renders `"override: off" vs "inherited: on"`

- Line 8986. This is UI copy; the story has no `ui.components` block (STORY-142 and STORY-153 do). Inconsistent.

### N-6. STORY-153 `GET /api/caching/analytics` returns `hit_rate: number` with no shape

- Lines 9047–9056. Is the number 0..1 or 0..100? Other dashboards (FEAT-029, line 5277) show "cache hit rate" as a KPI tile but don't pin the range either.

### N-7. STORY-154 segment_ids accept `string[]` but `PromptSegment.id` is `uuid`

- Line 9102 vs 21742. Typed as `string` on the wire but uuid in the model. Use `uuid` in the API spec.

### N-8. STORY-155 API is `PUT /api/caching/configs/:id` — earlier stories use `PATCH /api/cache/models/:id`

- Lines 9151 vs 8513. Same object, two verbs, two paths. See M-3.

### N-9. `CacheEntry.similarity_score` makes no sense for `backend != semantic`

- Line 21806–21808. Field is always present but meaningful only for semantic hits. Fine as nullable — but the schema should say so (it already does with `nullable: true`; however the AC for exact hits never mentions it, leaving the field underspecified).

### N-10. `CacheEntry` tracks `hits` but not `misses`; analytics story needs misses

- FEAT-066 (line 1001) reports hit rate. Hit rate = hits / (hits + misses). `CacheEntry.hits` tracks hits; misses are a per-request property recorded on `Request.cached=false`. The analytics endpoint (9047) must join `Request` to compute misses — fine, but not stated in the story.

### N-11. `FEAT-064` description lists four invalidation triggers; only one has a story

- Line 983: "logout, template update, nightly refresh, break-glass".
- STORY-150 covers logout. No story covers template update, nightly refresh, or break-glass invalidation. See "Missing / dangling references" below.

---

## Cross-epic

### X-1. EPIC-005 × EPIC-006: shadow and canary traffic cache behavior is undefined

- Shadow rule (STORY-119, lines 7653–7686): "Its response is discarded and never returned to the client" (7671). Should shadow produce cache writes? If yes, shadow traffic can prefill the primary's cache — potentially returning a "cheaper" response that was generated by the shadow model to real users. If no, the shadow path must skip the cache lookup too.
- Canary rule (STORY-118, 7626–7650): canary gets a fraction of real traffic. If canary's response lands in the same cache as primary, a 50-50 cache-key collision could let 10% canary responses be served to 100% of users at steady state.
- Fix: add to FEAT-060 a rule that shadow traffic never reads and never writes the cache, and canary writes only to a canary-scoped partition (e.g. extend the cache key with the resolved model id rather than the alias — see X-2).

### X-2. EPIC-005 × EPIC-006: aliases vs resolved model as cache-key input

- FEAT-054 (ModelAlias) resolves names like `fast-cheap` at request time (line 21400). If cache keys include the alias, a re-pointed alias serves stale entries generated under the old resolution. If they include the resolved model, identical prompts served under the same alias but different resolutions never share entries.
- Fix: pin cache key to the resolved `model_id` + `provider_id`; state explicitly in STORY-142.

### X-3. EPIC-007 × EPIC-006: redaction, blocks and cache-write suppression

- See Critical C-7. Also: when `SafetyEvent.action ∈ {block, flag}`, should the request be cached at all? What about `redact` — does the cache entry store the redacted or the model's original response? The `prompt_original` / `prompt_redacted` fields on `SafetyEvent` (21904–21909) have no analogue on `CacheEntry`.

### X-4. EPIC-008 × EPIC-006: cache hits and budget enforcement

- Budgets gate spend. On a cache hit, `Request.cost` is reduced but not zero (per M-6). Does a cache hit still decrement the budget counter? Best for correctness: yes, by `cache_cost`. No story states it.
- Warmup (STORY-154) is claimed "non-billable" (line 9083). Under BYOK, the provider still bills the customer; under managed, Antirion absorbs. The semantics of "non-billable" for budget-counter purposes are undefined.

### X-5. EPIC-011 × EPIC-006: where in the pipeline does cache lookup/write occur?

- FEAT-141 (line 1744), FEAT-142 (line 1753), FEAT-144 (line 1771), FEAT-148 (line 1799) define the pipeline. The phase ordering quoted in non-functional blocks is "auth, translate, upstream, post-processing" (e.g. line 15524). Cache lookup fits logically after auth/safety and before upstream; cache write fits after post-processing. No feature makes this placement explicit, and the `performance_slo` budget (25xx µs p50, line 25) does not allocate a slice for cache lookup — yet STORY-142 non-functional (line 8535) allocates 5 ms p95 to cache lookup, which is 5× the p95 gateway-added latency target. These are inconsistent budgets unless the cache slot is explicitly excluded from the baseline SLO.
- Fix: state the phase ordering in FEAT-060 ("cache check runs after edge auth and safety, before upstream dispatch; cache write runs after post-processing"), and either (a) revise STORY-142's 5 ms p95 to <= 500 µs to fit the gateway budget, or (b) exempt cache-hit requests from the gateway-added-latency SLO and document why.

### X-6. FEAT-148 (graceful degradation) "serve-cached" does not specify which backend

- STORY-345 AC-001 (16800–16809) says "A matching CacheEntry exists". Exact? Prompt-prefix? Semantic? If the operational intent is resilience, semantic should be allowed with a higher threshold; if the intent is correctness, only exact should match. Pick one and document.

---

## Missing / dangling references

For each entry: the citing location, the id implied, and whether it is defined.

### R-1. FEAT-064 description lists event classes with no matching stories

- Citing: lines 983 ("logout, template update, nightly refresh, break-glass").
- Defined stories under FEAT-064: STORY-150 (logout), STORY-151 (edit/delete). No story covers **template update**, **nightly refresh**, or **break-glass** invalidation. These are promised by the feature scope but absent.
- Fix: add STORY entries or prune the description.

### R-2. FEAT-062 has no PromptSegment CRUD

- Citing: FEAT-062 title "Prompt segment tracking" (line 962); `PromptSegment` model (line 21738).
- STORY-146 is the only story (line 8686). It reports on segments but does not create, edit, delete, or version them — yet AC-002 talks about editing to v8 (line 8706) and retiring v7. No POST/PATCH/DELETE endpoints exist anywhere for `PromptSegment`.
- Fix: add a story for segment lifecycle, or cross-reference the feature in EPIC-005/EPIC-007 that owns it.

### R-3. STORY-154 references a "stated ETA" for warmup jobs

- Citing: line 9084 ("completes within the stated ETA").
- `CacheWarmupJob` model (22928–22955) has no `eta` field and no story states the ETA. Dangling promise.

### R-4. STORY-156 `rule_id` reason refers to `InvalidationRule.id`, but eviction reasons `policy|ttl|size|safety_policy_change|manual_purge` are not rule-triggered

- Citing: line 9185.
- `InvalidationRule` is for invalidation, not eviction. The `rule_id` field on the eviction event only makes sense if `safety_policy_change` and `manual_purge` reasons carry an `InvalidationRule.id` — but manual purges (STORY-275 line 14234) don't go through `InvalidationRule`. Dangling FK semantics.

### R-5. STORY-145 AC-002 "savings report" has no referenced feature/report

- Citing: lines 8672–8678.
- "The savings report runs" — which report? No FEAT-066 story is cited, nor is a model/endpoint. Implicit cross-reference to STORY-153 but not stated.
- Fix: `depends_on: [STORY-153]` on STORY-145 or cite `FEAT-066`.

### R-6. STORY-150 event ids (`session.logout`, `role.change`) have no declared event catalog

- Citing: lines 8860, 8923.
- No feature defines an authoritative list of invalidation-eligible events. `InvalidationRule.match: json` (line 21817) accepts anything, but the UI cannot offer an autocomplete without a source of truth. Compare with FEAT-102 (notifications) which does carry an event catalog.
- Fix: add an `InvalidationEvent` model or reference the notifications event catalog.

### R-7. STORY-275 destructive-cache-purge references `CacheEntry` but no per-model or per-team variant

- Citing: line 14254.
- The Danger Zone purges all caches. FEAT-068 (line 1020) mentions "size-based eviction" but no story provides a per-scope purge (e.g. purge one team's entries) that is neither "invalidate one entry" (STORY-147) nor "purge everything" (STORY-275). The middle ground is absent.
- Fix: either extend STORY-147 to accept bulk scopes with typed-slug confirmation (see C-9) or add a new story under FEAT-068.

---

## Recommended sequencing for fixes

1. Land C-1, C-2, C-3, C-4, C-5, M-1, M-11, M-13 as a single schema revision (the model section is the root cause of most downstream issues).
2. Land C-6, C-7, C-8, X-1, X-2, X-3, X-6 as a "cache semantics" clarification patch to EPIC-006 — these are story-level rewrites, not schema changes.
3. Land C-9, M-3, M-8, M-9, M-10 as a "cache API surface" cleanup — path names, scopes, permissions, enumerations.
4. Land M-2, M-4, M-5, M-6, M-7, N-1..N-11 as a final tidy-up.
5. Land R-1..R-7 by adding the missing stories or pruning the over-promised feature descriptions.
