# EPIC-005 — Model catalog and routing — requirements.yaml audit

Audit target: `docs/requirements.yaml` lines 139–158 (epic), 779–937 (features FEAT-045..FEAT-059), 6849–8464 (stories STORY-104..STORY-141), with cross-references to `project.non_functional_baseline` (lines 13–38) and the models block (lines 20712+).

Read-only review. No changes proposed to `requirements.yaml` itself; all fixes describe what should change there.

---

## Summary

EPIC-005 is internally consistent on the happy path (catalog → rules → deploys → approvals) but drifts in several load-bearing places:

1. The boundary between EPIC-005 (routing policy / configuration) and EPIC-011 (gateway runtime — retry, timeout, failover, circuit breaker) is fuzzy. FEAT-051 duplicates concepts owned by FEAT-139 and FEAT-142, with overlapping but mismatched vocabulary ("errors/timeouts/rate-limits" vs `["429","5xx"]`).
2. Routing-strategy semantics drift across stories. The `canary` shape (`rampPct`, `errorBudget`, `autoRollback`, `healthy`) is invented in story prose but never modeled, and three different evaluation windows (5 min, 15 min, 60 min) are used across STORY-118/124/125. `least-loaded` and `single` strategies are listed in the strategy enum but have no story exercising them.
3. Routing-decision performance non-functional ("under 2 ms p95 on the request path") is repeated 32× across the epic and exceeds the project gateway-added latency budget (p95 ≤ 1 ms) defined in the baseline.
4. The catalog hot-reload SLA cited in STORY-107 (60 s) contradicts the baseline (30 s).
5. Mid-stream retry semantics are silent in EPIC-005 even though the baseline mandates "retries only the remaining prefix"; the cross-referenced FEAT-139 story actively says "no retry" — the contradiction lands on EPIC-005 rules without being addressed.
6. Several internal references are broken: STORY-131→STORY-122, STORY-126→STORY-118, FEAT-059/STORY-141→FEAT-072. EPIC-011 STORY-327 also dangling-references STORY-134.
7. FEAT-058 (Prompt and template registry) and FEAT-059 (Model evaluation) are scoped under "Model catalog and routing" but address neither catalog nor routing.
8. There is no model-catalog-sync feature: every model entry is manual via STORY-108. No story covers reconciliation with upstream provider catalogs.
9. CatalogPolicy vs RoutingRule precedence is ambiguous: both define `retry_on_429`, `fallback_on_5xx` shapes; no story states which wins.

Severity buckets below.

---

## Critical

### C1. Routing decision p95 budget (2 ms) exceeds the gateway-added latency baseline (1 ms p95)

- **Where**: 32 stories repeat the line `Routing decisions execute in under 2 ms p95 on the request path`. Examples: STORY-104 (line 6900), STORY-105 (6948), STORY-107 (7073), STORY-114 (7443), STORY-115 (7511), STORY-117 (7622), STORY-118 — *implicitly omitted*, STORY-119 (7685), STORY-127, STORY-128 (8071), STORY-129..141.
- **Quote**: `Routing decisions execute in under 2 ms p95 on the request path` (e.g. line 7443).
- **Baseline**: `performance_slo` line 25 — `Gateway-added latency — ingress acceptance to first upstream-provider byte, excluding provider time — targets <= 250 µs p50, <= 1 ms p95, <= 5 ms p99 under nominal load`.
- **Problem**: Routing is one phase of the gateway-added pipeline (alongside auth, translate, outbound dispatch, post-processing). A single phase claiming a 2 ms p95 budget already busts the whole-pipeline 1 ms p95 baseline. Either the baseline is wrong, EPIC-005 is wrong, or "routing decision" excludes some phases — but no definition is given.
- **Fix**: Define the exact phase boundaries the routing-decision metric covers (e.g. "rule match + target selection only, excluding translate and outbound"). Then either set the per-phase budget below 1 ms p95 (e.g. 200 µs) so summation fits the baseline, or amend the baseline with an explicit decomposition. Do this once in EPIC-005's description and reference it from each story instead of repeating an unconstrained number.

### C2. Failover/retry/circuit-breaker responsibility split between FEAT-051 and EPIC-011

- **Where**:
  - FEAT-051 (line 850): `Provider-level circuit breaker and per-rule fallback chain on errors, timeouts, rate-limits.`
  - STORY-121 (line 7727+): cascades fallback chain on 5xx, opens circuit, persists state in Redis (line 7764).
  - FEAT-139 (line 1729): `Retry, timeout and runtime failover` — STORY-329 (line 16139+) owns the fallback cascade.
  - FEAT-142 (line 1755): `Provider health and circuit breaker runtime` — STORY-336 (line 16419+) owns circuit open/close, half-open, per-model scope.
- **Problem**: Two epics own the same runtime behavior with different vocabulary.
  - STORY-121 AC-002 ("circuit breaker for X is open and the first fallback Y is tried directly") and STORY-336 AC-001 ("circuit state for that provider becomes open... incoming requests skip that target and go straight to fallback") describe the same runtime decision in different stories.
  - STORY-121 says cooldown TTL persists in Redis (line 7764), but STORY-336 line 16465 puts cluster-wide propagation under FEAT-142. Two homes for the same state machine.
  - FEAT-051 trigger vocabulary is `errors, timeouts, rate-limits` (line 851); FEAT-139 STORY-327 vocabulary is `["429","5xx"]` (line 16066). The first is the rule-config language, the second is the runtime classifier — but the two are never reconciled.
- **Fix**: Make EPIC-005 own *configuration and rule shape* (trigger taxonomy, fallback chain JSON, cooldown values, scope=per-provider/per-model toggle). Make EPIC-011 own *runtime execution* (open/close transitions, retry execution, state storage). Restate FEAT-051 description as "Per-rule trigger taxonomy and fallback-chain configuration; runtime executed by FEAT-139/FEAT-142." Move STORY-121's runtime ACs into FEAT-139/FEAT-142 (or delete) and replace with config ACs.

### C3. Mid-stream retry semantics: baseline mandates resume, EPIC-011 mandates abort, EPIC-005 silent

- **Where**:
  - Baseline `streaming` line 31: `Mid-stream upstream failure retries only the remaining prefix.`
  - FEAT-139 STORY-327 AC-002 (line 16075): `Do not retry non-idempotent streams … No retry is attempted on the same target … The stream is closed with an error event.`
  - EPIC-005: no story addresses streaming behavior under failover/retry.
- **Problem**: The baseline says "retry the remaining prefix" — i.e. resume mid-stream from a checkpoint. The runtime story says "do not retry mid-stream". These are contradictory. Worse, EPIC-005 is silent on what happens to a *streaming* request when its routing rule's fallback chain fires mid-stream — STORY-121 (FEAT-051) and the canary/shadow stories never mention streaming at all.
- **Fix**: Reconcile baseline and FEAT-139. If the baseline's "retries only the remaining prefix" is the intended semantic, FEAT-139 STORY-327 AC-002 is wrong and a new story must define the prefix-resume protocol (checkpoint/resume token, idempotency, dedup at the client). If "no mid-stream retry" is the intended semantic, the baseline line 31 must be rewritten. Either way, add an explicit AC to STORY-121 (and STORY-118 canary) covering streaming behavior under fallback/canary auto-rollback.

### C4. Hot-reload SLA mismatch: STORY-107 says 60 s, baseline says 30 s

- **Where**: STORY-107 AC-002 line 7030: `Downstream resolvers (router, edge auth) pick up the change within 60 seconds.`
- **Baseline**: `config_hot_reload` line 21: `propagate to every node within 30 seconds`.
- **Problem**: CatalogPolicy is the most policy-laden routing surface in EPIC-005; doubling its propagation deadline directly contradicts the baseline.
- **Fix**: Change STORY-107 AC-002 to `within 30 seconds`, or replace with the canonical phrase already used elsewhere: `… changes reach every edge node within the config-reload SLA`.

### C5. Broken intra-epic story reference: STORY-131 → STORY-122

- **Where**: STORY-131 AC-002 line 8215: `Deletion proceeds as in STORY-122`.
- **Problem**: STORY-122 is `Dry-run a routing rule against recent traffic` (line 7765). The intent is the hard-delete flow defined in STORY-130 (`Hard-delete a disabled model`).
- **Fix**: Replace `STORY-122` with `STORY-130`.

### C6. Broken intra-epic story reference: STORY-126 → STORY-118

- **Where**: STORY-126 AC-001 line 7970: `The thresholds persist on the rule and drive STORY-118 auto-graduation`.
- **Problem**: STORY-118 is `Configure a canary routing rule` (line 7624) — the *configuration* story. Auto-graduation is STORY-125 (`Auto-graduate canary when metrics pass`, line 7915).
- **Fix**: Replace `STORY-118` with `STORY-125`.

### C7. Broken cross-feature reference: FEAT-059 / STORY-141 → FEAT-072

- **Where**:
  - FEAT-059 description line 932: `… and a translation regression suite that exercises FEAT-072.`
  - STORY-141 title and narrative line 8443+: `Translation regression suite for FEAT-072`.
- **Problem**: FEAT-072 (line 1062) is `Content classification` — safety category scoring, not translation. Cross-dialect translation lives in EPIC-011 (e.g. FEAT-146 `Tool-calling and function-calling passthrough`, line 1787). The translation regression suite has no business citing FEAT-072.
- **Fix**: Replace `FEAT-072` with the actual translation feature(s) in EPIC-011 — at minimum `FEAT-146` for tool/function-calling fidelity, and probably `FEAT-145` (multimodal) and the dialect ingress feature in FEAT-135..FEAT-138 if "translation" means dialect translation.

### C8. RoutingRule data model has no shape for retry triggers, backoff, or canary subfields used by stories

- **Where**:
  - RoutingRule fields line 21606+: `strategy`, `targets json`, `fallback json (nullable)`, `timeout_ms int`, `retries int`, `canary json (nullable)`, `shadow json (nullable)`.
  - Stories invent fields not modeled:
    - STORY-118 line 7638: `rampPct`, `errorBudget`, `autoRollback`, `canary.healthy`.
    - STORY-117 line 7580: `currentErrorRate`, `errorBudget`, plus a "persistence window".
    - STORY-126 line 7968: `error_rate < 1%`, `p95_latency_ms < 1.2x primary`, `cost_per_request within 1.1x primary`, all over 60m.
    - STORY-327 line 16066: `triggers ["429","5xx"]` and `base-delay 200 ms` on the rule — RoutingRule has no triggers/backoff fields.
    - STORY-336 AC-003 line 16450: `circuit scope "per-model"` on the rule — not a field.
- **Problem**: Stories assume a structured shape that the data model leaves as opaque JSON. Without explicit subfields, two implementations will diverge, validators can't be specced, dry-run (STORY-122) and approval diff (STORY-133) cannot render structured changes.
- **Fix**: Either (a) define the JSON sub-schemas inline on RoutingRule.fallback / .canary / .shadow with explicit field lists (e.g. `canary: {ramp_pct, error_budget_pct, auto_rollback, eval_window_s, healthy, current_error_rate}`), or (b) add new top-level fields. Same for retry: replace `retries: int` with `retry: {max, triggers, base_delay_ms, backoff, jitter}`. Decide whether `circuit.scope` is on the rule or on Provider/Model.

---

## Major

### M1. Three different canary evaluation windows across stories

- **Where**: STORY-118 AC-001 line 7639 (`5-minute window`), STORY-124 AC-002 line 7883 (`last 15m`), STORY-125 AC-001 line 7929 (`error_rate < 1% for 60m`), STORY-126 AC-001 line 7968 (`all over 60m`).
- **Problem**: Same canary, four narratives, three windows. Auto-rollback uses 5 min; "guarded promote" uses 15 min; auto-graduate uses 60 min; the configurable thresholds are 60 min by example. No story states which window is the authoritative source of truth, and the data model has no `eval_window_s` field.
- **Fix**: Pick distinct, named windows for distinct purposes (e.g. `auto_rollback_window_s`, `auto_graduate_window_s`, `manual_promote_lookback_s`) and add them to the canary sub-schema (see C8). Have each story cite the named field instead of inlining a number.

### M2. FEAT-050 description lists six strategies; stories cover only canary, shadow, and the reference drawer

- **Where**:
  - FEAT-050 description line 840: `Single, weighted, failover, least-loaded, canary and shadow routing strategies with an in-product reference drawer.`
  - Stories: STORY-118 (canary), STORY-119 (shadow), STORY-120 (drawer). No story for `single`, `weighted` (selection logic), `failover` (per-strategy semantics distinct from the fallback chain), or `least-loaded`.
  - "Weighted" *creation* exists in STORY-114 AC-001 (FEAT-049), and "failover" *editing* in STORY-116 AC-001, but neither defines the strategy's runtime selection semantics.
- **Problem**: `least-loaded` ships in the strategy enum (line 21624) and the reference drawer (line 7703) but has no story specifying inputs (which load metric? per-provider or per-target?), tie-breaking, or test cases. Same for `single` (degenerate but still needs a definition).
- **Fix**: Add a story per strategy under FEAT-050 covering the selection function, fairness/tie-breaking, and a worked example. At minimum a `least-loaded` story is mandatory because nothing else defines its input metric.

### M3. EPIC-005 epic description omits two strategies present in the strategy enum

- **Where**: EPIC-005 description line 141: `… route traffic with weighted, failover, canary and shadow strategies.`
- **Problem**: `single` and `least-loaded` are in `RoutingRule.strategy` (line 21624) and in FEAT-050 description (line 840). The epic description is the canonical scope statement and contradicts both.
- **Fix**: Update the epic description to list all six strategies, or drop the unused two from the enum and from FEAT-050.

### M4. CatalogPolicy and RoutingRule define overlapping retry/fallback policies with no precedence rule

- **Where**:
  - CatalogPolicy line 21363+: `fallback_on_5xx: {enabled, max_hops}`, `retry_on_429: {enabled, backoff_min_ms, backoff_max_ms}`.
  - RoutingRule line 21606+: `fallback json`, `retries int`, `timeout_ms int`.
  - STORY-107 AC-001 line 7020 lists CatalogPolicy fields verbatim; STORY-114 (rule create) lets the user set `fallback`/`retries` per-rule.
- **Problem**: Two layers, same controls, no precedence story. Does the rule override the catalog policy? Cap it? Multiply with it (e.g. effective `max_hops = min(rule.fallback.length, catalog.fallback_on_5xx.max_hops)`)? STORY-107 only says "Downstream resolvers pick up the change", not how the resolver merges layers.
- **Fix**: Add a story to FEAT-049 (or FEAT-045) defining the precedence: catalog policy as default + per-rule override, with explicit merge rules. Document on both data models that the rule wins on conflict (or whatever is decided).

### M5. ModelAlias.fallback is single-valued; RoutingRule.fallback is a chain — same word, different shape

- **Where**:
  - ModelAlias line 21400+: `resolves_to_model_id`, `fallback_model_id` (single).
  - RoutingRule line 21627: `fallback: json` (chain — STORY-329 line 16153 confirms `fallback chain ["B","C"]`).
  - FEAT-047 description line 806: `aliases that resolve to a model with a fallback`.
- **Problem**: Two different "fallbacks". When a request goes via an alias and then through a routing rule with its own fallback chain, the precedence is unspecified. Are alias fallbacks resolved at resolve-time (eagerly to a single model id) or at runtime (and combined with rule chain)?
- **Fix**: Either align ModelAlias to a chain, or rename one of the two. Add a story under FEAT-047 stating the resolution order: alias is resolved first to its primary; alias.fallback only fires when the alias itself cannot resolve (e.g. primary disabled), independent of routing-rule fallbacks.

### M6. Shadow routing is underspecified — no rampPct, no cache-interaction, no `Shadow traffic is never billed` non-functional on the shadow story

- **Where**:
  - RoutingRule.shadow line 21637: `json, nullable`.
  - STORY-119 line 7651+: `mirrors 100% of traffic`, "response is discarded", "latency and cost are logged against the rule". Non_functional list includes `Routing decisions execute in under 2 ms p95 …` but does NOT include `Shadow traffic is never billed to the tenant and never surfaces to the caller`.
  - That non-billing line *does* appear on STORY-114 (line 7444), STORY-115 (7512), STORY-116 (7547), STORY-117 (7623) — i.e. the rule-management stories — but is missing from the only story that actually creates shadow traffic.
- **Problem**: The non-functional invariant for shadow lives on the wrong stories. STORY-119 is also silent on (a) whether shadow rate is configurable (always 100%? `shadow.sample_rate`?), (b) whether cache hits on the primary still trigger a shadow call (interaction with EPIC-006), (c) whether shadow honors safety guardrails (interaction with EPIC-007 — does a shadow request count toward PII/safety blocks?).
- **Fix**: Move the "Shadow traffic is never billed" non-functional onto STORY-119. Add ACs covering sample-rate, cache-interaction (recommend: shadow runs on primary cache *miss only* to avoid distorting comparisons; or always — pick one and document), and safety-guardrail policy (recommend: same guardrails apply, blocked shadow requests count as divergence). Add an `Shadow` sub-schema to the data model with `sample_rate`, `target_model_id`, `divergence_metrics`.

### M7. Canary auto-promote silently mutates the rule's fallback chain

- **Where**: STORY-124 AC-001 line 7879: `The original primary is added to the fallback chain.`
- **Problem**: Promote-canary is a 1-click action whose side effect rewrites the rule's `fallback` field. Two issues: (a) this isn't user-controllable or surfaced in the confirmation dialog (line 7874 only mentions confirming the promote); (b) after enough promotions the fallback chain grows unboundedly with stale primaries. Combined with M4, the chain may also exceed CatalogPolicy `fallback_on_5xx.max_hops`.
- **Fix**: Add an explicit "Add prior primary to fallback chain" toggle (default on) to the promote dialog. Cap chain length at CatalogPolicy.max_hops with a visible warning when truncating. RoutingDeploy's `before/after` already captures this — make sure the diff highlights the chain mutation.

### M8. STORY-118 promotes a canary with `Canary health evaluated at least every 30 seconds` non-functional only — no whole-rule hot-reload non-functional

- **Where**: STORY-118 line 7649–7650: only one non-functional line (`Canary health evaluated at least every 30 seconds`). Compare to STORY-114 (lines 7441–7444) which includes 3 non-functional lines.
- **Problem**: The story that defines the canary configuration is missing the standard EPIC-005 non-functionals (config-reload SLA, decision p95). If a new canary RoutingRule is created, it must propagate via the same hot-reload SLA — silent here.
- **Fix**: Add the standard pair: `Routing and model-catalog changes reach every edge node within the config-reload SLA` and the routing-decision p95 line (after C1 is fixed).

### M9. STORY-129 audience bypasses the canonical notifications model

- **Where**: STORY-129 AC-001 line 8091: `Each affected user with role admin or owner receives an email`.
- **Baseline**: `notifications_model` line 37 — canonical audience roles are (a) acting principal, (b) owning principal on the resource, (c) org-scoped contact fields (security/billing/finance/privacy/primary), (d) platform operator, (e) Antirion sub-queues.
- **Problem**: "all admin or owner users" doesn't map cleanly onto the canonical roles. The notice should probably target (b) the owner of each affected ApiKey/Team and (c) Org.tech_contact. Also the "weekly reminder email until the deadline" non-functional (line 8130) doesn't say who; same fix.
- **Fix**: Restate the audience using the canonical (a)/(b)/(c)/(d)/(e) language. Audit-record the resolved audience as required by the baseline.

### M10. Cross-epic interaction with EPIC-006 (caching) and EPIC-007 (safety) is not specified for shadow/canary

- **Where**: No story in FEAT-050/FEAT-053 references EPIC-006 or EPIC-007.
- **Problem**:
  - Shadow + cache: if the primary is served from cache (EPIC-006 STORY-142), does the shadow still issue a real upstream call? If yes, comparison is biased; if no, the shadow misses the cached portion of traffic. Either decision needs a story.
  - Canary + cache: a new canary target gets cold-cache against a warm primary, distorting the latency comparison feeding STORY-126 thresholds. Should the canary's auto-graduate metrics exclude warm-cache requests, or be window-normalized? Not addressed.
  - Canary/shadow + safety: when an EPIC-007 rule blocks a request, does that count as a canary error? Counts as a fallback trigger? Silent.
- **Fix**: Add stories or ACs to FEAT-050 and FEAT-053 spelling out cache and safety interaction. Cross-link from EPIC-006 (FEAT-060) and EPIC-007 (FEAT-073) so the dependency is bi-directional.

### M11. No catalog-sync feature: every model is a manual entry

- **Where**: FEAT-046 description line 795: `Add a model; enable, disable, deprecate, restrict or promote from preview.` STORY-108 (line 7074) is a fully manual `POST /api/models`.
- **Problem**: Provider catalogs change frequently. A purely manual entry path is operational debt and almost guarantees drift between Antirion's catalog and what the upstream provider actually serves. There is no story for: (a) periodic sync from provider catalog APIs, (b) reconciliation reports (catalog vs upstream), (c) auto-deprecation when an upstream marks a model as legacy.
- **Fix**: Add a feature (or extend FEAT-046) for provider-catalog sync. Define which providers support an enumerable catalog API, a sync cadence, and a reconciliation surface (likely on /models). Auto-deprecation should plug into FEAT-055 runbook so notifications fire automatically.

### M12. FEAT-058 (Prompt and template registry) and FEAT-059 (Model evaluation) are scope-mismatched to EPIC-005

- **Where**: EPIC-005 title (line 140) and description (line 141) — `Model catalog and routing`. FEAT-058 (line 919) and FEAT-059 (line 930) are inside this epic.
- **Problem**: Prompts/templates are neither models nor routing. Evaluation/benchmarking is a quality discipline that uses the catalog but isn't part of catalog management. Their placement here muddles the epic boundary and dilutes "what is EPIC-005 responsible for". This is also why STORY-141 ended up cross-referencing FEAT-072 (C7) — placement encouraged a stretch.
- **Fix**: Split into a new epic (e.g. "Prompts and evaluation") or move FEAT-058 next to a content/template-aligned epic and FEAT-059 next to observability/quality. If the epic boundary is intentional, restate EPIC-005 as "Model catalog, routing, prompts and evaluation" so the description matches the contents.

---

## Minor

### m1. Strategy reference drawer (STORY-120) doesn't carry the "single" semantics anywhere either

- Line 7703: drawer shows cards for all six strategies. Without a backing story per strategy (M2), the drawer cards have no source of truth for their copy and "use this when" bullets.

### m2. STORY-117 hero KPI strip cites "currentErrorRate" / "errorBudget" but no API field

- STORY-117 AC-003 line 7580–7584 uses `currentErrorRate` and `errorBudget`. The /api/routing/hero response (line 7593+) lacks any canary-specific fields. Either add them to the response schema or describe how the UI obtains them.

### m3. STORY-114 generates a "human-readable rule description" — no source of truth for the generator

- STORY-114 AC-001 line 7397: `A human-readable rule description is generated`. No story defines the generator (template? localized?). RoutingRule has a `note` field (line 21643) but no `human_description` field — the generated text has nowhere to live.

### m4. Role drift in narrators

- STORY-108 / STORY-109 narrator: `admin` (line 7078, 7130). `primary_users` lists `workspace admin` and `platform admin` (lines 61, 72), not bare `admin`.
- STORY-133 narrator: `platform engineering lead` (line 8251). Not in `primary_users`. Closest is `team lead` or `engineering manager`.
- Fix: spell `workspace admin` and rename "platform engineering lead" to a role that exists.

### m5. STORY-104/STORY-108 use `as_a: ml engineer` and `as_a: admin` for the same surface

- /models is browsed by ml engineer (STORY-104) but added-to by `admin` (STORY-108). Roles are fine but the inconsistency matters when wiring permission checks (M9 is the same class of problem at the audience layer).

### m6. STORY-119 (shadow) AC-002 thresholds for divergence/cost/latency reports are not in the data model

- "divergence rate, latency delta and cost delta" (line 7679) — RoutingRule.shadow is opaque JSON; no `ShadowComparison` model exists. Compare with STORY-126 which also invents thresholds.

### m7. STORY-121 non-functional names Redis explicitly while other stories use abstracted phrasing

- STORY-121 line 7764: `Circuit breaker state persists in Redis (or equivalent) with TTL = cooldown`. Most other non-functionals refer to "shared store" / "cluster-wide" abstractions (baseline lines 16, 20). Either standardize on the baseline phrasing or move this to FEAT-142 (per C2).

### m8. "Routing decisions execute in under 2 ms p95 …" is repeated 32 times — should be inherited from baseline

- Baseline pattern explicitly says (line 14): `Individual stories only restate these when they deviate.` Once C1 is resolved, define the routing-decision budget once on EPIC-005 (or in baseline) and remove the per-story repetition. Same for `Routing and model-catalog changes reach every edge node within the config-reload SLA`.

### m9. CatalogPolicy.allowed_regions has no story

- CatalogPolicy field line 21390 (`allowed_regions: json`) referenced only in STORY-107 AC-001 listing. No story tests a request being blocked because a region is not allowed; no story covers what enforces it. Consider adding a story or moving to EPIC-009 residency.

### m10. RoutingDeploy.type enum includes "toggle" but no story creates one

- RoutingDeploy line 22878: `type: edit|canary.promote|rollback|toggle`. STORY-115 AC-002 (disable a rule) creates an AuditLog entry but no RoutingDeploy. Either add `toggle` deploy creation to STORY-115 or remove the enum value.

### m11. STORY-108 AC-001 omits provider-credential preflight

- Adding a model is the user's first opportunity to discover that no BYOK credential exists for the provider (FEAT-025). STORY-108 silently creates the Model regardless. STORY-330 (FEAT-140) AC-002 then returns 503 at request time. Adding a preflight warn-only check would dramatically reduce the foot-gun.

### m12. FEAT-049 description includes "view live router health KPIs and alerts" — covered by STORY-117, but FEAT-049 also doesn't depend on FEAT-051 (where the "alerts" come from)

- Cross-feature dependency is implicit only.

---

## Cross-epic

### X1. EPIC-005 ↔ EPIC-011 boundary

See C2. Net-net: EPIC-005 owns *static, per-tenant, hot-reloadable rule shape* (catalog, aliases, rules, deploys, approvals, history). EPIC-011 owns *dynamic, per-request runtime execution* (retry, timeout, fallback, circuit breaker, telemetry). Today both contain pieces of both. Recommended explicit split:

| Concept | Should live in | Currently lives in |
|---|---|---|
| Trigger taxonomy (when does a fallback fire?) | EPIC-005 (FEAT-051 config) | FEAT-051 prose + FEAT-139 STORY-327 ACs |
| Fallback chain shape on a rule | EPIC-005 (RoutingRule.fallback) | EPIC-005 ✓ |
| Fallback runtime cascade | EPIC-011 (FEAT-139 STORY-329) | Both STORY-121 and STORY-329 |
| Circuit breaker thresholds (cooldown, scope=provider/model) | EPIC-005 (config) — currently nowhere structured | Implicit only |
| Circuit breaker state machine, transitions | EPIC-011 (FEAT-142) | Both STORY-121 AC-002 and STORY-336 |
| Retry policy shape (max, triggers, backoff) | EPIC-005 (RoutingRule.retry sub-schema) | RoutingRule has only `retries: int` |
| Retry runtime execution | EPIC-011 (FEAT-139 STORY-327) | EPIC-011 ✓ |

### X2. EPIC-005 ↔ EPIC-003

- FEAT-046 (Add model) silently assumes a BYOK credential exists for the provider. m11 above. Add a soft cross-link.
- STORY-109 AC-002 (`status restricted` + `allowlist` of team ids) overlaps with EPIC-003 FEAT-023 (`allowed models` on a key). When both are set, which is checked first? Should be defined: model-side allowlist gates first (cheaper to check), then key-side allowlist.

### X3. EPIC-005 ↔ EPIC-006

- Per M10. Cache config is per-model (EPIC-006 STORY-142, line 8466), but routing rules can target multiple models with weighted/failover. The interaction is unspecified: does a weighted rule see one effective cache config per target, or is cache-key salted by rule id? Decide and document on FEAT-050 and FEAT-060.
- STORY-130 AC-001 says CacheConfig blocks model deletion (line 8143). This is the only story that actually wires EPIC-005 to EPIC-006 — keep it as a model for the other interactions.

### X4. EPIC-005 ↔ EPIC-007

- Per M10. Also: FEAT-074 (safety action overrides) can flip a safety block to allow on the safety side; nothing in EPIC-005 says whether the routing rule that ultimately served the request is recorded as a fallback / canary / shadow event in those overrides.

### X5. EPIC-005 ↔ EPIC-011 telemetry

- STORY-338 AC-001 (line 16518) lists span attributes but does not include `routing_rule_id`, `routing_strategy`, `canary_arm`, `shadow`. Without these the live decision stream (STORY-123) and the routing dashboard (STORY-117) can't be correlated to traces.
- Fix: add routing fields to the canonical span attribute set in FEAT-143.

---

## Missing / dangling references

This section enumerates every FEAT-XXX or STORY-XXX referenced inside the EPIC-005 surface (epic description, feature descriptions, feature stories, and acceptance criteria, and known cross-references *into* EPIC-005 from outside) and reports which ones do not resolve, do not exist, or are scope-incorrect.

### (a) Cited story or feature has no definition in `requirements.yaml`

| Citing line | Citation | Status |
|---|---|---|
| (none) | — | All FEAT-045..FEAT-059, STORY-104..STORY-141, FEAT-072 (cited in C7), STORY-385 (cited in STORY-106 depends_on, line 6958), STORY-379 (cited in STORY-106 AC-001, line 6963), STORY-380 (cited in STORY-106 AC-001, line 6963) all resolve to defined entries. |

No outright dangling IDs found inside EPIC-005. The reference correctness problems are all of the *wrong-target* class below.

### (b) Citation resolves but points at the wrong target (semantic dangling)

| Citing line | Citation | Actual definition | Should likely cite |
|---|---|---|---|
| 932 (FEAT-059 description) | `FEAT-072` | FEAT-072 = Content classification (safety) | Translation features in EPIC-011 — at minimum `FEAT-146`; possibly `FEAT-145` and the dialect features in FEAT-135..FEAT-138 (see C7) |
| 8443 (STORY-141 title), 8445 (narrative) | `FEAT-072` | same as above | same as above |
| 8215 (STORY-131 AC-002) | `STORY-122` | STORY-122 = Dry-run a routing rule against recent traffic | `STORY-130` (Hard-delete a disabled model) — see C5 |
| 7970 (STORY-126 AC-001) | `STORY-118` | STORY-118 = Configure a canary routing rule | `STORY-125` (Auto-graduate canary when metrics pass) — see C6 |
| 16091 (STORY-327 AC-003, EPIC-011) | `STORY-134` | STORY-134 = Version prompts and templates (FEAT-058) | `STORY-329` (Fall back through the target chain) or `STORY-121` (FEAT-051 fallback) — broken EPIC-011 → EPIC-005 cross-ref. Flagged here because it masquerades as a citation of an EPIC-005 routing story |

### (c) Implicit dependency surfaced by narrative but never declared

| Where | Implicit dependency | Why it matters |
|---|---|---|
| FEAT-046 STORY-108 (line 7074+) — "Add a new model" | EPIC-003 FEAT-025 (BYOK provider credentials) | Adding a Model with no credential for that provider creates a foot-gun (m11). Should be declared via cross-link or a preflight AC. |
| FEAT-049 STORY-117 (line 7548+) — KPI strip with circuit-open alert | EPIC-011 FEAT-142 (Provider health and circuit breaker runtime, STORY-336) | The "Circuit open" pill comes from the runtime; FEAT-049 never declares the dependency. |
| FEAT-050 STORY-118 / STORY-119 — canary and shadow | EPIC-006 FEAT-060/FEAT-061 (cache configuration), EPIC-007 FEAT-073 (detection rules) | Cache and safety interactions undefined (M10). |
| FEAT-053 STORY-124 — promote canary | FEAT-054 (RoutingDeploy) is implicit (a `RoutingDeploy of type "canary.promote"` is created at line 7876) but FEAT-053's description (line 869) doesn't reference FEAT-054. |
| FEAT-051 STORY-121 — fallback on error/timeout/rate-limit | EPIC-011 FEAT-139 (retry/timeout/runtime failover) and FEAT-142 (circuit breaker runtime) | The runtime that does the falling-back lives in EPIC-011; FEAT-051 narrates as if it owns the runtime (C2). |
| FEAT-055 STORY-129 — deprecation runbook | FEAT-103/FEAT-104 (notification channels) and the canonical notifications_model (M9) | Audience routing defaulted to "admin or owner" instead of canonical roles. |
| FEAT-056 STORY-130 — hard-delete model | EPIC-006 (CacheConfig) referenced ✓, but EPIC-008 (budgets) and EPIC-004 (request log retention) not — does deletion of a Model affect historic dashboards keyed on model_id? |
| FEAT-057 — routing rule change approvals | Approval.kind enum line 22628 ✓ (`routing-rule-change` is present). EPIC-005 doesn't declare a dependency on the Approvals epic anywhere in its description. |
| FEAT-058 (Prompt registry) — every story | EPIC-007 (safety) — published prompts likely need safety review; not addressed. |
| FEAT-059 STORY-141 — translation regression suite | EPIC-011 FEAT-146 (real owner of translation), EPIC-004 (where regression results surface) | C7 above, plus where regression reports live. |

### (d) Scope promised by epic/feature but absent from the features list or stories

| Promise | Where | Missing |
|---|---|---|
| EPIC-005 description: `weighted, failover, canary and shadow` | line 141 | Omits `single` and `least-loaded` — present in FEAT-050 and the strategy enum (M3). |
| FEAT-050: `Single, weighted, failover, least-loaded, canary and shadow routing strategies` | line 840 | No story for `single`, `weighted` (selection logic), `failover` (selection semantics distinct from fallback), `least-loaded` (M2). |
| FEAT-046 verbs: `enable, disable, deprecate, restrict or promote from preview` | line 795 | STORY-109 covers enable/disable/restrict; deprecate is FEAT-055; "promote from preview" has no AC. |
| FEAT-050 reference drawer | line 840 | STORY-120 ✓, but the drawer's per-strategy copy has no source-of-truth story (m1). |
| EPIC-005 description does not mention prompts/templates or evaluation | line 141 | But FEAT-058 and FEAT-059 are inside the epic (M12). |
| FEAT-045 description: `view provider headroom and the org-wide catalog policy panel` | line 782 | ✓ STORY-106 (headroom) and STORY-107 (catalog policy). |
| FEAT-051: `Provider-level circuit breaker and per-rule fallback chain` | line 851 | "Per-rule" circuit-breaker config (cooldown, threshold, scope=per-provider/per-model) is referenced by STORY-336 AC-003 ("rule specifies circuit scope per-model") but RoutingRule has no field for it (C8). Configuration surface is missing. |
| FEAT-055 description: `track affected keys and teams, and measure migration progress` | line 893 | ✓ STORY-129 covers it via ModelDeprecationNotice. |
| FEAT-056 description: `blocking deletion when still referenced by rules, aliases or carrying live traffic` | line 903 | STORY-130 covers rule/alias/cache references. STORY-131 covers live traffic. ✓ — but neither story checks ModelAlias.fallback_model_id (only resolves_to). Possible gap. |
| FEAT-057 description: `Approval of kind "routing-rule-change"` | line 913 | ✓ matches Approval.kind enum (line 22628). |
| FEAT-059 description: `Golden datasets, compare models side-by-side, and a translation regression suite` | line 932 | Translation suite cites the wrong feature (C7). Also no story covers dataset versioning rollouts even though `GoldenDataset.version` exists (line 24020). |
| Implied catalog-sync feature | (not in epic) | M11 — entire missing capability. |
| Mid-stream behavior on fallback / canary auto-rollback | (not in any EPIC-005 story) | C3 — entire missing capability inside EPIC-005, contradicted across baseline and EPIC-011. |

---

## Appendix — Scope and method

- Read: full project baseline (lines 1–73), EPIC-005 (lines 139–158), FEAT-045..FEAT-059 (lines 779–937), STORY-104..STORY-141 (lines 6849–8464), models block entries for Provider, Model, ProviderRateLimit, ProviderRateLimitWindow, CatalogPolicy, ModelAlias, RoutingRule, RoutingDecision, CacheConfig, Approval, ProviderHealth, RoutingDeploy, ModelDeprecationNotice, ModelPricingHistory, PromptTemplate, PromptTemplateVersion, GoldenDataset.
- Cross-checked against: EPIC-003 (FEAT-022..FEAT-028), EPIC-006 (FEAT-060..FEAT-067), EPIC-007 (FEAT-069..FEAT-073), EPIC-011 (specifically FEAT-138 edge auth, FEAT-139 retry/timeout/failover, FEAT-140 outbound auth, FEAT-141 metering/idempotency, FEAT-142 provider health and circuit breaker runtime, FEAT-143 telemetry, FEAT-144 streaming).
- Note on the assignment brief: the brief named `FEAT-143 runtime failover` and `FEAT-147 retries/timeouts`. Per the actual file these concepts live in `FEAT-139 (Retry, timeout and runtime failover)` (line 1729) and `FEAT-142 (Provider health and circuit breaker runtime)` (line 1755); FEAT-143 is `Request telemetry` and FEAT-147 is `Request and response size limits`. This audit cites the actual ids.
- No edits were made to `docs/requirements.yaml`.
