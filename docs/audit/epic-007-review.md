# EPIC-007 — Safety and guardrails: requirements.yaml review

Audit scope: `docs/requirements.yaml` lines 173–190 (epic), 1028–1160 (FEAT-069..FEAT-081), 9200–10372 (STORY-157..STORY-183), and the cross-referenced models (lines 21860–22011, 22618–22662, 22956–23025, 23616–23649). Cross-epic checks against EPIC-004, EPIC-006, EPIC-010, EPIC-011, the `non_functional_baseline.security`, `non_functional_baseline.observability` and the `notifications_model`.

This is a documentation review. No edits to `docs/requirements.yaml` were made.

---

## Summary

EPIC-007 covers the safety and guardrails surface (PII detection/redaction, prompt-injection/jailbreak detection, classification, rule management, overrides, versioning, dry-run/backtest, templates, per-team policy, policy-change approvals, PII unredact, live flow visualization). Internally the epic is largely self-consistent at the feature/story-id graph level — every cited STORY-/FEAT- id within the epic resolves. The serious problems are at the contract level:

1. **Data-model drift.** `DetectionRule.method` enumerates 8 method values but FEAT-073 advertises only 5; `PiiCategory` has no `action` field even though stories key block/redact decisions on a per-category action; `DetectionRule` exposes `hits_24h` only, but STORY-167 requires `fp_count`/`fire_count` to compute `fp_rate`; `SafetyEvent.sev` (the field) vs `severity` (the query parameter) — naming drift on the same axis.
2. **PII storage vs the security baseline.** `SafetyEvent.prompt_original` durably stores the raw, un-redacted prompt — directly contradicting `non_functional_baseline.security` ("never appear in logs, telemetry or persisted payloads") and the FEAT-113 retention story that says "Stored request bodies are redacted before persistence". This in turn collides with STORY-159's NFR ("Reversible redaction keys stored in a vault") because two reversal mechanisms cannot both be the source of truth for FEAT-080's unredact flow.
3. **Notifications-model violations across the entire epic.** None of FEAT-069..FEAT-081 cite the canonical audience roles (a–e) defined in `project.non_functional_baseline.notifications_model`. STORY-159 invents "the owner team"; STORY-177 says "the requester is notified"; STORY-178 fires an `AlertEvent` with no audience and no mode-collapse rule. There is zero mention of `trust_and_safety` anywhere in the epic, even though sustained jailbreak/PII-egress patterns are precisely the abuse-correlation signal the model says must reach `trust_and_safety` in saas and be silently dropped in self_hosted.
4. **Cross-epic incoherence with EPIC-006 (cache).** Cache invalidation is wired to retention changes (STORY-148) but not to safety-rule changes; semantic-cache hits across redaction-policy boundaries are undefined; `pii_to_provider = redacted|hash_in_route|passthrough` (CatalogPolicy) cuts across the cache-key strategy without any acceptance criterion that pins behavior.
5. **Cross-epic incoherence with EPIC-011 (pipeline).** Stories return HTTP 451 on a safety block but never set a `Request.status_label` — every other policy block in the codebase (`ip_denied`, `geo_blocked`, `residency_violation`) sets one, and EPIC-004's request-log filters depend on `status_label`. Pipeline ordering of safety vs cache vs residency is never declared.
6. **Mode availability is not declared anywhere.** EPIC-013 features carry an explicit `mode:` key. No EPIC-007 feature does, yet several stories have mode-relevant behavior (template catalogs in air-gapped self_hosted, `trust_and_safety` collapse, phone-home of safety signals via FEAT-179 "security" channel).
7. **`Approval.kind` is being overloaded.** PII unredact requests reuse `kind = "policy-change"` (STORY-179) — the enum doesn't have an unredact/data-reveal kind, and routing/approver-role resolution then depends on a string that means two different things.

Counts: 6 critical, 11 major, 9 minor, 6 cross-epic, 5 missing/dangling references. Detail below.

---

## Critical

### C-1. `SafetyEvent.prompt_original` violates the `security` baseline and the redaction promise

- Lines: model `SafetyEvent.prompt_original` at 21904–21906; baseline `security` at 33; FEAT-113 STORY-257 AC-002 at 13404–13412 ("Stored request bodies are redacted before persistence"); STORY-159 NFR at 9339 ("Reversible redaction keys stored in a vault with workspace-scoped access").
- Quoted text:
  - `21905: type: string` / `nullable: true` (the field), with no description that constrains what it stores.
  - `33: ... and never appear in logs, telemetry or persisted payloads.`
  - `13412: - Stored request bodies are redacted before persistence`
  - `9339: - Reversible redaction keys stored in a vault with workspace-scoped access`
- Problem: The model durably stores the un-redacted prompt on the safety event. That is the precise data class the security baseline forbids in any persisted payload, and it contradicts FEAT-113's retention story. STORY-159's NFR implies the canonical reversal path is a vault key (e.g., format-preserving encryption / detokenization), which is a different mechanism than "store the cleartext on SafetyEvent". FEAT-080's unredact flow then has two incompatible sources of truth.
- Fix: Drop `SafetyEvent.prompt_original`. Define a single canonical reversal store (a vault per workspace, residency-pinned, CMK-bound per FEAT-133), reference it by token from `SafetyEvent.spans`, and make FEAT-080 the only path that detokenizes. Add an explicit AC to STORY-159 stating that the original prompt is never persisted on `SafetyEvent` or on `Request`.

### C-2. The entire epic ignores the `notifications_model` — no canonical audience roles and no `trust_and_safety` routing

- Lines: baseline at 37–38; epic 173–190; every story between 9200–10372.
- Quoted text (sample):
  - `9331: - A SafetyEvent of action "block" is recorded and visible to the owner team` — "the owner team" is not one of the canonical roles (a)..(e).
  - STORY-177 AC-002 at 10148: `- The requester is notified` — no role, no channel, no mode-collapse rule.
  - STORY-178 AC-001 at 10173: `... an AlertEvent fires` — no audience.
  - STORY-180 AC-001 at 10241: `- The requester gets a one-time link to view the original span until expiry` — no role, no channel, no audit of who else is notified.
- Problem: The `notifications_model` is explicit: every event-bearing story names the audience by role and per deployment mode, and cross-tenant abuse signals (which is exactly what jailbreak/prompt-injection/PII-egress patterns are at the platform level) "always reach Antirion `trust_and_safety` in saas and are silently dropped in self_hosted". Not a single story in EPIC-007 does this.
- Fix: For every story that creates a `SafetyEvent`, an `Approval`, an `AlertEvent` or a `Notification`, name the audience using roles (a)..(e), name the contact field on `Org` (likely `security_contact` and/or `privacy_officer` for PII), and spell the saas-vs-self_hosted collapse — including the cross-tenant fanout to `trust_and_safety` for jailbreak/abuse classes (FEAT-071/072) and for break-glass-style overrides (FEAT-074, FEAT-080).

### C-3. PII unredact is funnelled through `Approval.kind = "policy-change"`, which is the wrong kind

- Lines: `Approval.kind` enum at 22628 (`budget-overage|policy-change|key-elevated-scope|routing-rule-change`); STORY-179 AC at 10213–10214; FEAT-079 description at 1135.
- Quoted text:
  - `22628: description: budget-overage|policy-change|key-elevated-scope|routing-rule-change`
  - `10214: - An Approval of kind "policy-change" is created linked to it`
- Problem: A PII unredact is a one-time data reveal request, not a policy change. Reusing the `policy-change` kind collapses two semantically different things, breaks any approver-role routing built on `kind`, and makes audit/reporting (e.g., DPIA, Dsar) ambiguous. FEAT-079's title and description also explicitly bind `policy-change` to "safety, retention or detection policies".
- Fix: Add a new `Approval.kind` value, e.g. `data-reveal` (or `pii-unredact`), and require STORY-179 to use it. Spell the approver role (privacy_officer per `Org`) and the SLA. Update FEAT-079's description so its `policy-change` kind is not silently overloaded by FEAT-080.

### C-4. `DetectionRule.method` taxonomy drift between feature and model

- Lines: FEAT-073 description at 1074 (`regex, NER, classifier, allowlist and fingerprint`); model at 21939 (`regex|regex+checksum|NER|classifier|prefix+entropy|allowlist|n-gram|fingerprint`).
- Quoted text:
  - `1074: description: Create, edit, toggle, save-as-draft and publish rules of regex, NER, classifier, allowlist and fingerprint types.`
  - `21939: description: regex|regex+checksum|NER|classifier|prefix+entropy|allowlist|n-gram|fingerprint`
- Problem: The model declares 8 methods; the feature declares 5. `regex+checksum`, `prefix+entropy` and `n-gram` are unreachable from the documented surface — no story creates one, no validator enumerates one, no UI is referenced for one. This is either dead code in the model or a missing story; either way the spec is internally inconsistent.
- Fix: Pick one source of truth. If the 8-method list is correct, expand FEAT-073's description and the rule editor stories (STORY-165/166/168) to enumerate all 8 and define example use-cases (`regex+checksum` for credit-card Luhn-aware detection, `prefix+entropy` for secret tokens, `n-gram` for fuzzy fingerprinting). If only 5 are real, prune the model.

### C-5. `PiiCategory` has no `action` field, but stories key block/redact decisions on category-level action

- Lines: `PiiCategory` model at 21996–22010; STORY-159 AC-002 at 9326 (`PII category "cc" has action "block"`); STORY-160 PATCH path at 9362.
- Quoted text:
  - `21996: - name: PiiCategory` (fields: `id, label, method, strictness, risk` — no `action`)
  - `9326: - PII category "cc" has action "block"`
- Problem: The acceptance criterion reads off a property the model doesn't expose. `PiiCategory` carries `strictness` (loose|balanced|strict) but no `action`, so there is no place to encode "cc → block" vs "email → redact". STORY-160 also keys strictness off the workspace via `PATCH /api/safety/pii-config` rather than on the per-category record — this implies a separate per-workspace `PiiPolicy` that is also missing from the model.
- Fix: Add an `action` field to `PiiCategory` (or introduce a `PiiCategoryPolicy` record keyed on `(org_id, category_id)` with `strictness` and `action`). Define how `TeamSafetyPolicy.overrides` references it. Update STORY-160 to PATCH the right resource.

### C-6. STORY-167's `fp_rate` formula references fields that do not exist

- Lines: STORY-167 AC-001 at 9633; `DetectionRule` model at 21925–21963.
- Quoted text:
  - `9633: - The DetectionRule.fp_rate is recomputed as fp_count / fire_count`
  - Model fields are `id, org_id, name, category, method, pattern, severity, action, status, enabled, hits_24h, fp_rate, note, created_at, updated_at` — there is no `fp_count` and no `fire_count`.
- Problem: The acceptance criterion describes a derivation against fields that aren't in the model, and `hits_24h` is a 24h rolling counter, not a lifetime denominator suitable for an FP rate. Without persisted counters, `fp_rate` is uncomputable in the contract.
- Fix: Either add `fp_count` and `fire_count` (lifetime, monotonic) to `DetectionRule`, or define `fp_rate` as a derived view computed from `SafetyEvent` rows (with an explicit window) and remove the field-on-model fiction.

---

## Major

### M-1. `SafetyEvent.sev` vs `severity` query parameter (naming drift on the same axis)

- Lines: STORY-157 query at 9248 (`severity:`); model at 21871–21873 (`sev`).
- Problem: The list/filter API uses `severity`; the persisted column is `sev`. Either is fine; both is not. Same drift on the data-export side (STORY-163 column heading).
- Fix: Rename `SafetyEvent.sev` → `SafetyEvent.severity` and update filter/export contracts. Touch the docs only — implementation is downstream.

### M-2. Block/redact/flag/allow precedence is undefined

- Lines: FEAT-073 (1074), STORY-161 AC-002 at 9399 ("Allowlist exception"), STORY-165 AC-001 at 9500 (regex with `action: "allow"`).
- Problem: The epic defines four `SafetyEvent.action` values and lets allow-typed rules and block-typed rules coexist without specifying which wins when both fire on the same span. STORY-161 implies allowlist short-circuits a classifier rule, but no story states this generally. Multi-action collisions (one rule says `redact`, another says `block` on the same Request) are undefined.
- Fix: Add a "rule precedence" subsection to FEAT-073 (or a new ordering doc): explicit total order of allow → block → redact → flag (or whichever is correct) and a deterministic tie-break by rule severity then rule id. Add an AC under STORY-165 covering simultaneous matches.

### M-3. FEAT-074 override surface is asymmetric with `SafetyEvent.action` enum

- Lines: FEAT-074 at 1085–1086 ("block -> allow, flag -> block"); model action enum at 21876.
- Problem: `SafetyEvent.action` is `block|redact|flag|allow` (4 values) but the override description only covers two transitions. There is no statement of legal transitions for `redact` (e.g., `redact -> allow` to expose original, `redact -> block` to harden) or `allow -> flag`. STORY-169 only implements `block -> allow`. The override matrix is incomplete.
- Fix: Specify the full transition matrix in FEAT-074 and add ACs to STORY-169 for at least `redact -> allow` (which is the natural pairing of FEAT-080) and `allow -> flag` (escalation).

### M-4. `Request.status_label` is set on every other policy block but not on safety blocks

- Lines: STORY-159 AC-002 at 9330 ("returns 451"), STORY-161 AC-001 at 9396; vs `status_label` settings at 14438 (`ip_denied`), 15180 (`residency_violation`), 15206 (`geo_blocked`), 15595 (`client_cancelled`).
- Problem: Safety-blocked requests need a `status_label` to be filterable in EPIC-004 (request log) and to show up in dashboards; otherwise a safety block is indistinguishable from any other 451 (and 451 itself is not a defined status_label anywhere else). Cross-tenant abuse correlation (per `notifications_model`) needs a stable label too.
- Fix: Add `status_label = "safety_blocked"` (or a per-category label like `pii_blocked`, `jailbreak_blocked`) to STORY-159/STORY-161 ACs, and add a corresponding filter to EPIC-004 STORY-073/074.

### M-5. API path drift: `/api/safety/rules` vs `/api/detection-rules`

- Lines: STORY-165 POST at 9515 (`/api/safety/rules`); STORY-168 POST at 9703 (`/api/detection-rules`); STORY-170 GET at 9838, POST at 9844 (`/api/detection-rules/...`).
- Problem: The same resource is addressed two different ways across stories of the same feature/epic. Either the rule lifecycle resource is `/api/safety/rules` or `/api/detection-rules` — pick one.
- Fix: Standardize on one path (recommend `/api/detection-rules` to align with the model name) and update STORY-165 and STORY-166.

### M-6. Mode availability is never declared on any EPIC-007 feature

- Lines: baseline at 36 (`Every feature that differs in scope, availability or data shape between the two modes declares its mode availability explicitly in its description.`); EPIC-013 features at 2104, 2114, 2124, 2134 carry `mode:`; FEAT-069..FEAT-081 do not.
- Problem: Several behaviors in EPIC-007 differ across modes:
  - FEAT-077 (template packs) — saas catalog vs bundled-with-install / air-gapped (parallels FEAT-166 docs).
  - FEAT-080 (unredact reveal) — privacy_officer routing differs by mode (saas may also fan out to Antirion DPO sub-queue; self_hosted collapses to platform admin).
  - FEAT-069/071/072 — abuse-correlation signals to Antirion `trust_and_safety` only exist in saas, gated by FEAT-179 "security" phone-home channel in self_hosted.
- Fix: Add `mode: both` to every FEAT-069..FEAT-081 (matches EPIC-013 convention), and where behavior differs across modes, restate the difference in the description (template provenance, audience routing, phone-home opt-in).

### M-7. STORY-168 and STORY-170 describe two parallel version-write paths

- Lines: STORY-168 AC-003 at 9678 ("A SafetyRuleVersion row is created capturing the published snapshot"); STORY-170 AC-001 at 9815 ("A SafetyRuleVersion row is created with actor, timestamp, before/after JSON and a change summary").
- Problem: STORY-168 writes a `SafetyRuleVersion` only on publish (draft edits do not). STORY-170 writes one on every save. The combination is ambiguous: when you edit a published rule, do you write one version (STORY-170) or none (STORY-168 says drafts don't, but this isn't a draft)?
- Fix: Restate the rule: every published-edit and every publish writes a `SafetyRuleVersion`; draft edits do not. Make STORY-170 reference STORY-168 as `depends_on` to lock the order and reuse the type enum.

### M-8. Cross-tenant abuse heuristics have no home in the epic

- Lines: baseline at 38 ("Cross-tenant signals (isolation breaches, abuse heuristics, sustained anomalies) always reach Antirion trust_and_safety in saas...").
- Problem: A repeated jailbreak attacker, a tenant emitting an unusual rate of PII-laden prompts to providers, or a sustained classification-toxic spike are exactly the abuse heuristics referenced — but no story defines that the gateway emits these aggregates anywhere, nor where they are stored, nor that they fan out to `trust_and_safety` in saas.
- Fix: Add a story under FEAT-071 or FEAT-072 (or a new feature) for "cross-tenant safety abuse signal" that aggregates per-tenant SafetyEvent rates, fires above a threshold, and routes to `trust_and_safety` in saas / drops in self_hosted per the model.

### M-9. STORY-178 invents OOO/delegation without a model or a feature

- Lines: STORY-178 AC-002 at 10174–10181 ("I am an approver with OOO set ... It is routed to my delegate with an AuditLog entry 'approval.delegate'").
- Problem: There is no `OutOfOffice` or `ApproverDelegation` model in the schema (closest is `OncallSchedule`/`OncallShift`, which are a different concept). The story's "delegate" is undefined: who configures it, where is it stored, how does it interact with `Approval.approver_user_id`?
- Fix: Either add an `ApproverDelegation` model and a small CRUD story to FEAT-079, or remove the OOO-delegate AC and degrade to an SLA-only contract.

### M-10. Live-flow story leaks data without an audience-or-residency contract

- Lines: STORY-183 AC-001 at 10321 ("Left column 'Your apps' lists top calling apps ... pulse dot ... inbound_per_min"); GET response at 10349.
- Problem: The story renders top app names, per-region traffic and a readiness composite without specifying who can see it (RBAC scope), what data class the `apps[].name` is (it could be a customer-internal hostname), and whether residency restricts which regions are listable. EPIC-013 operator views explicitly say "Operator drill-in never sees tenant prompt bodies; redaction is enforced before the data leaves the tenant's region" (line 19309) — STORY-183 has no equivalent guard.
- Fix: Add an AC: visible only to roles with `safety.read` (or whatever scope is canonical), and the `apps[].name` field is treated as PII — redacted/hashed for cross-tenant viewers and never crosses a residency boundary in the saas operator drill-in.

### M-11. Rule deletion leaves dangling FK on `SafetyEvent.rule_id`

- Lines: STORY-166 AC-002 at 9577 ("The rule is removed; Open SafetyEvents linked to the rule retain their rule_id for history").
- Problem: `SafetyEvent.rule_id` is `FK:DetectionRule` (line 21896), `nullable: true`. If the rule is hard-deleted, the FK either cascades (losing history) or dangles. The story mandates retention but the model has no soft-delete (`deleted_at`) or tombstone, and `SafetyRuleVersion` only captures changes, not deletes.
- Fix: Either soft-delete `DetectionRule` (add `deleted_at`) and treat `SafetyEvent.rule_id` as a normal FK to a soft-deleted parent; or extend `SafetyRuleVersion.type` to include `delete` and snapshot the rule on delete; or make `SafetyEvent.rule_id` a string and store rule name/method/pattern denormalized so history survives. Pick one and document it in STORY-166.

---

## Minor

### m-1. FEAT-070 advertises "twelve PII categories" but no list exists

- Line 1043. The model `PiiCategory` does not enumerate them, no story references the full set, no template (FEAT-077) is wired to bootstrap them. Add the canonical list (or remove the count).

### m-2. STORY-160 NFR is generic and out of place

- Lines 9376–9378 carry the generic detector NFRs ("Detectors run in-process with an explicit per-request latency budget...") on a story that only changes a config value. The setting story doesn't run a detector; the NFR is misapplied.

### m-3. STORY-163 (CSV export) does not constrain the `redacted content` column

- Line 9456: "A CSV with event id, time, category, rule, action, redacted content and request id is produced". No AC says the export refuses to embed `prompt_original` even if present, nor that the export goes through the same vault-detokenize gate as FEAT-080. Tighten.

### m-4. STORY-164 bulk action does not record `reviewed_by_user_id`

- Lines 9477–9479. Single-event review (STORY-169) sets `SafetyEvent.reviewed_by_user_id`; the bulk path only mentions `reviewed_at`. Either bulk should also set the actor or the model should explain why bulk is anonymous.

### m-5. STORY-171 dry-run scope is over-broad

- Line 9874 ("Last 24 hours") replays against `Request` rows. If those rows store cleartext, the dry-run reads cleartext PII into a draft-rule evaluation that could itself be an exfiltration vector. State that dry-run reads from the redacted projection and that any match samples are themselves redacted before display.

### m-6. STORY-173 template install lacks `template_pack_id` field on the model

- Line 9968 references `template_pack_id` on the installed `DetectionRule`, but the `DetectionRule` model has no such field. Add it (or store it on `SafetyRuleVersion` instead and document the join).

### m-7. STORY-172 "labelled sample set" is undefined

- Line 9931. Backtest precision/recall requires labels (true positives / true negatives) but no model holds them. There is no `SafetyLabelSet`, no `GoldenDataset` story for safety. Either reuse `GoldenDataset` (line 24009) and say so, or add the model.

### m-8. STORY-178 cites `AlertEvent` but does not name the AlertRule

- Line 10173: "an AlertEvent fires". Without a backing `AlertRule` and an audience, the alert lifecycle (FEAT-100) is incomplete. State which `AlertRule` template (or which built-in) creates these and who subscribes.

### m-9. `SafetyPosture` `redactor_coverage`/`allowlist_compliance`/`residency_enforcement` lack definitions

- Lines 21986–21992. Two of the three are described as `0..1`; one (`residency_enforcement`) has no description. STORY-183 hovers a tooltip that "explains" the score but the data model has no formula. Add field descriptions and a derivation formula.

---

## Cross-epic

### X-1. EPIC-006 (cache) has no safety-rule-driven invalidation

- Lines 8825–8847 (STORY-148 retention-driven invalidation) — the only invalidation story keyed on policy change. There is no parallel for "I changed a redaction rule from `passthrough` to `redact`": cached responses generated against the old policy would continue to serve. CatalogPolicy.`pii_to_provider` (line 21392, `redacted|hash_in_route|passthrough`) interacts directly with the cache key, but no story pins that interaction. Add an EPIC-006 story (or extend STORY-148) for `safety.rule.publish` and `safety.policy.change` invalidation events.

### X-2. EPIC-006 semantic-cache coherence with FEAT-070 is undefined

- STORY-143 at 8537 (semantic cache) embeds prompts and matches by cosine similarity. If the embedding is computed on the un-redacted prompt and the lookup key is the redacted prompt (or vice-versa), the cache returns cross-tenant or cross-policy hits. Pin: embeddings must be computed after redaction, with the embedding namespace partitioned by `(team_id, redaction_policy_version)`.

### X-3. EPIC-004 request-log redaction mentions an unstated source

- STORY-078 AC-002 at 5786–5795: "The prompt shows the redacted version ... The original prompt is not returned by the API." Combined with C-1, this is contradictory — `SafetyEvent.prompt_original` exists as a field and is returned by `GET /api/safety/events/:id` (STORY-158 response shape at 9290–9292). EPIC-004 forbids exposing original; EPIC-007's model exposes it. Resolve in favor of EPIC-004 (drop the field) and update STORY-158 to never expose original prompts unless coming through FEAT-080.

### X-4. EPIC-010 retention vs `SafetyEvent.prompt_original` and `SafetyEvent.prompt_redacted`

- `RetentionConfig` (line 22442) governs request bodies, not `SafetyEvent` rows. There is no per-class retention defined for `SafetyEvent.prompt_original` (which should be zero days — never persisted) or `SafetyEvent.prompt_redacted` (e.g., 90 days). Add a `RetentionConfig` row class for safety_event_redacted_body and tie it to STORY-258's per-class roster.

### X-5. EPIC-011 pipeline ordering of safety vs cache vs residency is never declared

- EPIC-011 features (1688–1927) describe ingress, edge auth, retry, outbound auth, telemetry, but no feature pins where safety detectors run relative to (a) cache lookup, (b) residency check, (c) edge auth, (d) outbound provider call. STORY-159 says "before sending to upstream", which is necessary but not sufficient — does redaction run before or after the cache lookup? If after, cache hits could leak PII; if before, the cache key changes per policy version (re-confirms X-1). Add a single explicit ordering story under FEAT-141 or as a new feature (e.g. "Pipeline stage ordering") that declares: edge-auth → ingress translation → policy/safety inbound → cache lookup → outbound auth → upstream → policy/safety outbound → cache write → telemetry.

### X-6. EPIC-010 residency vs FEAT-080 unredact reveal

- STORY-180/181 at 10222–10278 grant a one-time link to view original PII. There is no AC stating the reveal must occur within the residency-pinned region (FEAT-130) or that the vault key never leaves the region. CMK revocation interaction with active reveals is also unstated (compare FEAT-133 STORY-309 at 15267 "CMK revocation fails closed"). Add an AC: an approved unredact reveal is bound to the residency region and is invalidated within seconds of CMK revocation.

---

## Missing / dangling references

The text below lists every FEAT-/STORY-/concept id implied by EPIC-007 but missing a definition (or implied by the epic's scope but absent from the features list). Internal id graph (FEAT-069..081 ↔ STORY-157..183) is fully closed and self-resolving — the gaps are conceptual or external.

### MR-1. No FEAT for "safety pipeline ordering"

- The epic description (line 175) says "PII detection and redaction, prompt-injection and jailbreak detection, classification, rule management" but the actual runtime ordering of these vs cache/residency/edge auth is never defined in any FEAT-069..081, nor in EPIC-011 (FEAT-135..161). This is an undeclared dependency: every other feature in EPIC-007 sits implicitly inside a pipeline stage that has no spec.
- Citation lines: 175 (epic scope), STORY-159 narrative at 9308 ("before sending to upstream"), STORY-162 at 9429 ("A response is produced") — implies a post-upstream stage with no feature.
- Missing id: a new FEAT (e.g., FEAT-???) or an explicit story under FEAT-143 (telemetry) / FEAT-141 (cost+idempotency) that pins the order.

### MR-2. No FEAT for "cross-tenant safety abuse signal"

- The `notifications_model` at line 38 names "abuse heuristics, sustained anomalies" as `trust_and_safety` cross-tenant signals. EPIC-007 emits the events that should trigger this aggregation but no feature implements the aggregator nor the fanout.
- Citation: line 38; absence across 1028–1160.
- Missing id: a new FEAT under EPIC-007 (`Cross-tenant safety abuse correlation`) or an EPIC-013 counterpart explicitly linked from EPIC-007.

### MR-3. No model for "approver delegation / OOO" referenced by STORY-178

- STORY-178 AC-002 at 10174–10181 references an OOO + delegate flow with no backing model, no CRUD story, no feature. `OncallSchedule`/`OncallShift` (lines 23085–23135) are alerts-domain, not approvals.
- Citation: line 10181 ("AuditLog entry 'approval.delegate'").
- Missing id: an `ApproverDelegation` model and a small story under FEAT-079.

### MR-4. No model for "vault of reversible redaction keys" referenced by STORY-159 NFR

- STORY-159 NFR at 9339 ("Reversible redaction keys stored in a vault with workspace-scoped access") implies a per-workspace, residency-pinned, CMK-bound key store. No model exists. `CmkBinding` (line 23791) is for at-rest CMK, not for redaction reversal tokens.
- Citation: line 9339; FEAT-080 unredact relies on this without a backing record.
- Missing id: a `RedactionVault` (or similar) model + minimal config story under FEAT-070 or FEAT-080.

### MR-5. STORY-173 references `template_pack_id` and `safety_template.uninstall` — no carrier and no audit-action enum

- Line 9968 (`template_pack_id`) — no field on `DetectionRule` or `SafetyRuleTemplate` carries this back-pointer for the install grouping.
- Line 9978 (`safety_template.uninstall`) — `AuditLog` has `action` (line 22511 area) but no enumerated registry of action strings is defined anywhere; multiple stories invent action strings ad-hoc.
- Citation: 9968, 9978.
- Missing: either add `installed_template_id` FK on `DetectionRule` and an installed-pack collection on `SafetyRuleTemplate`, or define a separate `SafetyTemplateInstall` model. Independently, a registry of audit-action strings would close a class of similar drifts across the spec.

---

## End of review
