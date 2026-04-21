# EPIC-012 Audit — Platform foundations and customer experience

Read-only audit of `docs/requirements.yaml` for EPIC-012 (line 291) and its features FEAT-162..FEAT-169 with their stories STORY-387..STORY-402. Cross-referenced against `project.ui_baseline`, `project.non_functional_baseline` (workers line 18), `project.notifications_model`, the `models:` section (line 20712+), and sibling epics EPIC-001, EPIC-008, EPIC-010 and EPIC-013.

No edits were made to `requirements.yaml`.

## Summary

The epic scope — onboarding, public status, in-product support, legal, help, worker observability, pricing forecast, notification inbox — is coherent on paper, but multiple features have broken or misaligned wiring to the rest of the document.

Four classes of issue dominate:

1. **Data-model mismatches.** Acceptance criteria name fields (`SupportTicket.destination`, `ResidencyConfig.mode`/`source`, `HelpArticle.pinned`, `Notification.kind` values for license/maintenance/violation) that do not exist on the declared models.
2. **Broken cross-references.** FEAT-173 (line 2042) tells readers to see FEAT-164 for the in-app status widget — FEAT-164 is support contact; the widget lives in FEAT-163. FEAT-112 (line 1473) tells readers residency is pinned at "FEAT-163/STORY-409" — residency pinning is actually FEAT-162/STORY-387, and STORY-409 is the tenant roster.
3. **FEAT-167 under-delivers the baseline's explicit promise.** The non-functional baseline (line 18) declares "Worker fleet health is surfaced by FEAT-167." FEAT-167 ships two thin stories (STORY-399 dashboard, STORY-400 cancel/requeue) and the substantive queue/lag/DLQ/propagation surfaces actually live in EPIC-013 FEAT-170 (STORY-405, STORY-406). The two features overlap and FEAT-167 itself even routes to `/operator/workers`, making it an EPIC-013 surface misfiled under EPIC-012.
4. **Mode-availability silence.** Every FEAT-162..FEAT-169 description hand-waves mode differences in prose, but the stories that implement them (STORY-391/392/395/396/397/398/401/402) contain zero mode-gated acceptance criteria. EPIC-013 by contrast carries an explicit `mode:` field on every feature. EPIC-012 features do not.

Counts: **6 critical**, **11 major**, **8 minor**, **3 cross-epic**, **2 missing/dangling**.

---

## Critical

### C1. `SupportTicket` model has no `destination` field — every STORY-393 AC asserts setting it

- Cites: STORY-393 AC-001/002/003/004 (lines 18316, 18329, 18341), STORY-394 AC-002/003 (lines 18413, 18422).
- Quoted: `The SupportTicket.destination is "antirion_support_queue" and the ticket is enqueued into FEAT-181` (line 18316); `The SupportTicket.destination is "local_only"` (line 18329); `The SupportTicket.destination is "local_and_antirion"` (line 18341); `notification is delivered to the resolved responder audience stamped on SupportTicket.destination` (line 18413).
- Problem: `SupportTicket` (line 23266) declares only `id, org_id, user_id, subject, body, context, status, priority, created_at, resolved_at`. There is no `destination` column, no `redaction_profile`, no `escalated_to_antirion` flag. The mode-routing story is unimplementable against the declared schema.
- Fix: Add `destination: string (local_only|antirion_support_queue|local_and_antirion)`, `redaction_profile: string nullable` (to satisfy STORY-393 AC-003 "redaction profile used"), and `antirion_ticket_id: string nullable` to `SupportTicket`. Or: move routing/destination onto an associated `SupportTicketDelivery` row so one ticket can record multiple fan-outs.

### C2. `ResidencyConfig` model has no `mode` or `source` field — STORY-387 ACs write both

- Cites: STORY-387 AC-002 (line 18038), AC-003 (line 18051).
- Quoted: `A ResidencyConfig is created with region "eu-central-1" and mode "initial"` (line 18038); `Confirming records a ResidencyConfig pinned to "on-prem-dc1" with mode "initial" and source "install_config"` (line 18051).
- Problem: `ResidencyConfig` (line 22413) fields are `org_id, region, encryption_at_rest, encryption_in_transit, backup_frequency, backup_retention_days, last_backup_at, cmk_rotated_at, dpo_contact, migration_ends_at`. Neither `mode` nor `source` exists.
- Fix: Add `mode: string (initial|migrated)` and `source: string (user|install_config|api)` to `ResidencyConfig`, or remove those field names from the story text.

### C3. `HelpArticle` model has no `pinned` field or usage counters — STORY-398 writes both

- Cites: STORY-398 AC-001 (line 18575), AC-002 (line 18583).
- Quoted: `HelpArticle.pinned becomes true and it appears at the top of the help panel` (line 18575); `I see views per article over the selected time range` (line 18583).
- Problem: `HelpArticle` (line 23317) declares `id, title, summary, url, screens, tags, updated_at`. No `pinned`, no `view_count`, no pin relation. There is also no separate `HelpArticleView` model.
- Fix: Add `pinned: bool` (or join-table `HelpArticlePin(org_id, article_id)` because pinning is per-workspace per the narrative), and either add an event table or a denormalized counter.

### C4. `Notification.kind` enum is missing every EPIC-013-originated kind that FEAT-169 promises

- Cites: FEAT-169 description (line 2005), `Notification` model (line 23948).
- Quoted: `license events (renewal-approaching, entitlement-breach, fail-closed-warning) and by FEAT-180 license-violation incident events` (line 2005); `description: alert|approval|job|deprecation|billing|security` (line 23950).
- Problem: FEAT-169 guarantees the inbox surfaces platform notices (FEAT-173), license events (FEAT-175) and license-violation incidents (FEAT-180). The model enum has no `maintenance`, `incident`, `license`, `license_violation` values. STORY-402 AC is likewise limited to the original four kinds.
- Fix: Extend `Notification.kind` to include `maintenance|incident|license|license_violation|platform_notice`; add STORY-402 ACs for each mode's extra surfaces.

### C5. FEAT-167 does not deliver what `non_functional_baseline.workers` promises

- Cites: baseline line 18 (`Worker fleet health is surfaced by FEAT-167.`); FEAT-167 description (line 1986); STORY-399 (line 18589); STORY-400 (line 18648); STORY-405 (line 18919).
- Quoted baseline: `Background work ... runs in a dedicated worker fleet that consumes durable queues with visibility timeouts, exponential-backoff retry, poison-message dead-letter queues and at-least-once semantics. Handlers must be idempotent. Worker fleet health is surfaced by FEAT-167.` (line 18).
- Quoted FEAT-167: `Surface internal job queues (metric aggregation, webhook delivery, cache eviction, retention) and their health.` (line 1986).
- Quoted STORY-399: `I am on /operator/workers — the worker fleet is platform infrastructure, so the dashboard lives under the EPIC-013 operator shell, not under tenant /settings` (line 18602).
- Quoted STORY-405 non_functional: `Queue-health reads are served from the same metrics store that powers FEAT-167 — no direct broker polling from the UI path` (line 19003).
- Problem: (a) The baseline-promised surfaces — DLQ depth, retry counts, visibility-timeout stats, at-least-once idempotency evidence, consumer count — are not in FEAT-167; they live in FEAT-170 STORY-405 and STORY-406 (EPIC-013). (b) STORY-399 places the FEAT-167 dashboard at `/operator/workers`, which is an EPIC-013 route, and declares that tenant `/settings` is the wrong home. (c) STORY-400 assigns `workspace admin` the ability to cancel a running `WorkerJob` (metric aggregation, retention sweep — cross-tenant platform work), contradicting STORY-399's own "platform infrastructure" framing and escalating a tenant role into operator scope. (d) FEAT-167 UI reference is `proto/settings-sections.jsx` (tenant settings), also contradicting STORY-399's `/operator/workers` route.
- Fix: Either (i) merge FEAT-167 into FEAT-170 and update the baseline line 18 to point at FEAT-170, or (ii) scope FEAT-167 to a tenant-visible subset (tenant-owned worker jobs only, e.g. per-tenant retention sweep and export generation) and have FEAT-170 cover the platform-wide fleet; the baseline line 18 then needs to cite both.

### C6. FEAT-112 cross-references "FEAT-163/STORY-409" as the first-run residency pin — both are the wrong ids

- Cites: FEAT-112 description (line 1473).
- Quoted: `The region is set once at first-run (FEAT-163/STORY-409) and is immutable for the life of the workspace` (line 1473).
- Problem: FEAT-163 is "Public status page" (line 1944). STORY-409 is "Cross-tenant roster in saas mode" (line 19194). The actual first-run residency pinning is FEAT-162 / STORY-387 (line 18011).
- Fix: Change the reference to `FEAT-162/STORY-387`.

---

## Major

### M1. FEAT-173 description points to FEAT-164 for the in-app status widget — it is FEAT-163

- Cites: FEAT-173 description (line 2042).
- Quoted: `broadcast in real time to every affected tenant's in-app status widget (FEAT-164)` (line 2042).
- Problem: FEAT-164 is in-product support contact. FEAT-163 owns the status widget — STORY-391 component `StatusEmbed` (line 18251). STORY-412 (the implementation of the broadcast in FEAT-173) correctly references `FEAT-163` at line 19408, confirming the typo.
- Fix: Change FEAT-173's reference from `(FEAT-164)` to `(FEAT-163)`.

### M2. StatusPageIncident vs PlatformIncident — two models, one concept, no relationship declared

- Cites: `StatusPageIncident` (line 23242, used by FEAT-163 STORY-391 AC-002 line 18238 and STORY-392 data_models line 18293); `PlatformIncident` (line 23424, declared by FEAT-173 STORY-412/413/414 and broadcast to the FEAT-163 widget per line 19408).
- Problem: The public status page, the in-app widget and the operator incident console are supposed to be one source of truth — the `PlatformIncident.description` at line 23425 literally says `broadcast to affected tenants' in-app status widget and to the public status page`. But FEAT-163 stories persist `StatusPageIncident` while FEAT-173 stories persist `PlatformIncident` with a different field set (kind, severity, regions, affected_org_ids, state machine). There is no declared mapping, foreign key or derivation rule between them.
- Fix: Pick one. Either (a) make `StatusPageIncident` a public-facing projection of `PlatformIncident` (document the projection in the model description), or (b) collapse to a single `PlatformIncident` and retire `StatusPageIncident` from FEAT-163 stories. If kept separate, an explicit `platform_incident_id: FK:PlatformIncident nullable` is required on `StatusPageIncident`.

### M3. STORY-388 does not depend on STORY-387 — checklist can render before residency is pinned

- Cites: STORY-387 non_functional (line 18085); STORY-388 (line 18089); FEAT-162 description (line 1932).
- Quoted STORY-387: `No prompt, log row, derived artifact, key or setting is persisted before ResidencyConfig exists — the edge returns 409 "residency_not_pinned" for every write until then` (line 18085).
- Quoted FEAT-162: `Residency must be pinned before any tenant data can be written.` (line 1932).
- Problem: STORY-388 has no `depends_on` clause; STORY-389 depends only on STORY-388 (line 18149). Nothing in STORY-388 asserts that the SetupChecklist card is gated on an existing `ResidencyConfig`. Implementation could render the checklist before the picker closes.
- Fix: Add `depends_on: [STORY-387]` to STORY-388, and add an AC — `The SetupChecklist is not rendered until a ResidencyConfig exists for the Org`.

### M4. STORY-400 grants tenant `workspace admin` operator-level job control

- Cites: STORY-400 narrative (line 18651), AC-001 (line 18658).
- Quoted: `as_a: workspace admin / i_want: to cancel a running WorkerJob or requeue a dead-lettered one` (line 18653); `A WorkerJob is "running" / I click "Cancel" and confirm / The job is signalled to stop and its status becomes "cancelled"` (line 18658).
- Problem: The worker queues named by FEAT-167 (metric aggregation, webhook delivery, cache eviction, retention) and by the baseline (SCIM sync, audit sink fan-out, anomaly scoring, export generation, notification delivery) include cross-tenant platform work. Cancelling "metric aggregation" or "retention sweep" from a single tenant's admin violates tenant isolation — it affects other tenants' billing, audit retention or compliance. This conflicts with STORY-399's own framing that workers are "platform infrastructure ... not under tenant /settings" (line 18602).
- Fix: Restrict cancel/requeue to the platform operator audience (Antirion SRE in saas, platform admin in self_hosted). For jobs scoped to one Org (per-tenant export generation), allow tenant admins only against jobs matching the caller's org_id. Model change required: add `owner_org_id: FK:Org nullable` to `WorkerJob` so the ACL can enforce this.

### M5. Mode availability not declared on FEAT-162..FEAT-169

- Cites: `non_functional_baseline.deployment_modes` (line 36); FEAT-162..169 descriptions (lines 1932, 1945, 1955, 1965, 1976, 1986, 1996, 2005); FEAT-170..182 `mode:` fields (e.g. line 2013).
- Quoted baseline: `Every feature that differs in scope, availability or data shape between the two modes declares its mode availability explicitly in its description.` (line 36).
- Quoted FEAT-170: `mode: both` (line 2013).
- Problem: Every FEAT-162..169 hand-waves mode differences in its prose but none carries the explicit `mode:` key that EPIC-013 adopts. FEAT-168 (pricing) is arguably `mode: both` with different shape; FEAT-181 explicitly declares `mode: saas`. FEAT-167 has no `mode:` and its stories place it on an operator route. This is a structural gap that breaks the programmatic contract of the baseline.
- Fix: Add a `mode:` field to every FEAT-162..169 — `both` for 162/163/164/165/166/168/169, and reconsider 167 per C5.

### M6. STORY-391 / STORY-392 lack any mode-specific acceptance criteria

- Cites: FEAT-163 description (line 1945); STORY-391 (line 18218); STORY-392 (line 18267).
- Quoted FEAT-163: `In saas mode the page is operated by Antirion at status.antirion.example ... In self_hosted mode the page is operated by the local install at a platform admin-configured host ... the in-app widget always points at the mode-correct page` (line 1945).
- Problem: STORY-391 AC-001 hardcodes `status.antirion.example` (line 18230) and never states the self_hosted variant. STORY-392 AC-001 / AC-002 has no mode branch. Neither story covers "the in-app widget always points at the mode-correct page" — the most testable cross-mode invariant in the feature description.
- Fix: Add a self_hosted AC: page host comes from platform admin config; widget URL is derived from deployment mode at render time; in saas there is never a link to a self_hosted status page and vice versa.

### M7. STORY-395 / STORY-396 do not reflect FEAT-165's mode split

- Cites: FEAT-165 description (line 1965); STORY-395 (line 18428); STORY-396 (line 18483).
- Quoted FEAT-165: `In self_hosted mode the ToS and DPA governing the Antirion software are folded into the license agreement (FEAT-175) and are not re-prompted per user; the ToS/DPA surface in this feature is instead populated with the customer's own end-user legal texts uploaded by the platform admin` (line 1965).
- Quoted STORY-396: `as_a: workspace admin / i_want: to publish a new Terms of Service version` (line 18487).
- Problem: In saas mode Antirion legal publishes the ToS, not the workspace admin. STORY-396 asserts a tenant role can publish the document in all modes, which directly contradicts FEAT-165's description. No story covers (a) the self_hosted upload of customer legal texts by platform admin, (b) the saas path where ToS versioning is driven by Antirion, (c) the self_hosted case where no local ToS is configured yet (re-prompt on nothing?).
- Fix: Split STORY-396 into `STORY-396a saas: Antirion legal publishes a new global ToS version` and `STORY-396b self_hosted: platform admin uploads customer legal texts`. Add a `LegalDocument` model (see M8). STORY-395 re-prompt AC needs a self_hosted branch covering Antirion ToS not being re-prompted (covered by license).

### M8. No `LegalDocument` / `TosDocument` model exists — where do uploaded texts live?

- Cites: FEAT-165 description (line 1965); `TosAcceptance` (line 23294); the task's request header explicitly mentions a `LegalDocument` shape.
- Problem: FEAT-165 description says the self_hosted platform admin "uploads" customer legal texts, and STORY-396 requires publishing a new version. `TosAcceptance` models only the acceptance event (per-user version string). There is no model for the document, its version content, its effective date, its uploader, its publication state or the mapping from version-string to content bytes.
- Fix: Add a `LegalDocument` model — `id, org_id nullable (null = Antirion-global in saas), kind (tos|dpa|privacy|aup), version, content, published_at, effective_at, published_by_user_id`. `TosAcceptance.version` then becomes `FK:LegalDocument` or remains a string with an explicit uniqueness pairing.

### M9. FEAT-166 air-gapped behavior has no acceptance criterion anywhere

- Cites: FEAT-166 description (line 1976); STORY-397 (line 18508); STORY-398 (line 18559).
- Quoted FEAT-166: `In self_hosted mode the article catalog is bundled with the install image so help works fully offline and on air-gapped networks; the platform admin can opt in to periodic catalog refresh only when the "docs" phone-home channel (FEAT-179) is enabled. Deep-link URLs to external docs degrade to bundled anchors when air-gapped.` (line 1976).
- Problem: Neither story contains an AC for the bundled catalog, for the FEAT-179 opt-in refresh, or for the URL-degradation-to-local-anchor behavior. The testable promise in the feature description has no implementation story.
- Fix: Add `STORY-398a` — "self_hosted air-gapped help palette serves only the bundled article catalog"; add `STORY-398b` — "docs channel opt-in pulls a fresh catalog; the update is audited". Augment `HelpArticle` with `local_anchor: string nullable` so the URL-degradation behavior is implementable.

### M10. STORY-401 (pricing forecast) ignores FEAT-168's explicit saas/self_hosted cost-composition split

- Cites: FEAT-168 description (line 1996); STORY-401 (line 18680).
- Quoted FEAT-168: `In saas mode projected monthly cost sums provider passthrough plus Antirion plan fees and commitments (FEAT-096/FEAT-098). In self_hosted mode there is no per-request Antirion fee — the license is a flat commercial — so the calculator hides the Antirion subscription component and reports provider passthrough only; the license renewal figure comes from FEAT-175 and is shown as a separate annualized line.` (line 1996).
- Problem: STORY-401 AC-001 (line 18691) returns `a projected monthly cost with input/output/cache breakdown` — no mode branch, no Antirion plan-fee/commitment line, no license-renewal line. STORY-401 non_functional says `Forecast inputs never leave the org; no third-party pricing API calls` (line 18742), but saas plan fees come from the Antirion billing catalog — which is Antirion-originated data whether or not the inputs leave.
- Fix: Add ACs for each mode; add a commitment row from FEAT-098 in saas; add a license-renewal row from FEAT-175 in self_hosted. Relax the non_functional wording to: `Forecast inputs never leave the org; pricing catalog (provider rates + Antirion plan fees in saas) is read from the local read-through cache.`

### M11. STORY-401 `PricingQuote` breakdown has no schema for the saas-specific plan-fee line

- Cites: `PricingQuote` (line 23550); FEAT-168 description (line 1996).
- Problem: `PricingQuote.breakdown` is an opaque `json`. If the saas mode has a structured line for `antirion_plan_fee` and `antirion_commitment_offset`, that will emerge only at implementation time and is not discoverable from the model. Share-link reproducibility requires a stable shape.
- Fix: Declare a breakdown shape in the model description (e.g. `{ provider_input, provider_output, provider_cache, antirion_plan_fee?, antirion_commitment_offset?, license_annualized? }`) or add fields.

---

## Minor

### m1. STORY-389 uses `/v1/chat/completions` directly — misses OpenAI-compat indirection

- Cites: STORY-389 AC-001 (line 18158); FEAT-135 (line 1688).
- Quoted: `The gateway issues a /v1/chat/completions call using the newly created key` (line 18158).
- Problem: The gateway's ingress dialect is FEAT-135 (OpenAI-compatible ingress), and the endpoint path belongs to that feature. STORY-389 pins a path that is technically right today but should be expressed as "the canonical chat endpoint defined by FEAT-135" to avoid rot.
- Fix: Reword to reference FEAT-135.

### m2. STORY-387 has no GET endpoint for the residency picker's pre-state

- Cites: STORY-387 API block (line 18065).
- Problem: Only `POST /api/residency/initial` is declared. The page has to read whether a ResidencyConfig already exists (to decide whether to render the picker), to pre-fill in self_hosted, and to show the install_config source. No read endpoint is declared.
- Fix: Add `GET /api/residency` returning `{ config: ResidencyConfig | null, source: "user"|"install_config", editable: bool }`.

### m3. STORY-391 AC-001 hardcodes `status.antirion.example`

- Cites: STORY-391 AC-001 (line 18230).
- Problem: Tying the page to a literal host in the AC makes the self_hosted variant ambiguous (covered in M6). Even in saas, the domain is a deployment detail, not a testable requirement.
- Fix: Reword to "the platform-operator-configured status host" and cover mode in AC.

### m4. STORY-392 subscription endpoint lacks rate-limiting / abuse AC

- Cites: STORY-392 AC-001 (line 18277).
- Problem: Public unauthenticated email submission is an abuse vector. No AC for rate limit, double-opt-in failure, unsubscribe, or bounce handling.
- Fix: Add ACs for per-IP rate limit, one-step unsubscribe, and confirmation email expiry.

### m5. STORY-392 non_functional claims a 5-minute propagation — FEAT-173 claims 30 s

- Cites: STORY-392 non_functional (line 18297); STORY-412 non_functional (line 19464).
- Quoted STORY-392: `Status-page updates propagate within 5 minutes of a component state change` (line 18297).
- Quoted STORY-412: `Incident broadcasts reach every affected tenant's in-app widget within 30 seconds via the same propagation path as config hot-reload` (line 19464).
- Problem: Two different propagation SLAs for the same pipeline. If the public page and the in-app widget are one projection (see M2), the tighter bound must win or the weaker one must be justified.
- Fix: Align to 30 s (hot-reload SLA) or document the fan-out tier that takes longer.

### m6. STORY-393 confirmation copy is not localization-aware

- Cites: STORY-393 AC-001 (line 18317), AC-002 (line 18330).
- Quoted: `"Antirion support will reply by email" copy` (line 18317); `"Your IT team will reply" copy` (line 18330).
- Problem: The strings are pinned in English in the AC. The UI baseline (line 12) mandates localization via `UserPrefs/user.language`.
- Fix: Reword as "the configured localized ack copy for destination X" and move the exact string to the catalog.

### m7. STORY-398 "workspace admin" ability in self_hosted bundled mode is ambiguous

- Cites: STORY-398 AC-001 (line 18568); FEAT-166 description (line 1976).
- Problem: If the article catalog is bundled with the install image (self_hosted), pinning is still per-tenant — but nothing in the model supports per-tenant `pinned` state (see C3). The story silently assumes global pinning.
- Fix: Resolve with C3 model change — per-Org pin table.

### m8. STORY-402 does not define retention or pagination of the inbox

- Cites: STORY-402 (line 18743).
- Problem: No AC for inbox retention, pagination, bulk mark-read, or archive/delete. The `Notification` model has `read_at` but no `archived_at`.
- Fix: Add ACs and fields.

---

## Cross-epic

### X1. Duplication check — FEAT-168 vs FEAT-085 — not a duplicate but the naming is overlapping

- Cites: FEAT-168 description (line 1996); FEAT-085 description (line 1196); EPIC-012 description (line 293).
- Quoted FEAT-085: `Projected month-end spend and runout date driven by 7-day burn rate.` (line 1196).
- Quoted FEAT-168: `Let finance model monthly spend by mix of models, volume and caching before committing to a budget.` (line 1996).
- Problem: Both are "forecast" features. FEAT-085 is actuals-driven (burn rate projection, backtest MAPE), FEAT-168 is scenario-driven (what-if calculator). EPIC-012's description calls its scope `pricing/cost forecast tooling`, which reads as overlap with EPIC-008's forecast surface. They are not duplicates, but the epic descriptions do not disambiguate and share-link/UI routes both live under `/budgets/forecast` (STORY-401 AC-001, line 18692) — which is the same route an actuals forecast would live under.
- Fix: Clarify in FEAT-168 description that it is a what-if calculator distinct from FEAT-085's actuals-driven projection; route FEAT-168 under `/budgets/calculator` or `/budgets/what-if` to avoid URL overlap.

### X2. FEAT-164 support routing in self_hosted is fine; saas lacks explicit routing to `support` sub-queue

- Cites: FEAT-164 description (line 1955); notifications_model (line 37); FEAT-181 (line 2120).
- Quoted notifications_model: `Antirion-staff-only sub-queues in saas (trust_and_safety, support, sre, dpo, renewals, legal)` (line 37).
- Problem: FEAT-164 sends saas tickets to FEAT-181 "Antirion-side inbound support queue" — fine. But the notifications_model names `support` as one of several Antirion-staff sub-queues. FEAT-164 never picks one explicitly. If a ticket submitted from a security-context page (e.g., a tenant-isolation breach the tenant is about to raise) should route to `trust_and_safety`, FEAT-164 has no routing rule to do that; it always goes to `support`.
- Fix: Add a triage-routing AC to STORY-393 — ticket kind / originating screen determines which Antirion sub-queue receives it.

### X3. EPIC-001 first-run-after-invite vs FEAT-162 first-run-for-owner — boundary is unstated

- Cites: EPIC-001 features (line 79); FEAT-004 (line 357); FEAT-162 (line 1929); STORY-387 narrative (line 18015).
- Quoted STORY-387: `as_a: workspace owner on first sign-in (saas) or platform admin on first install (self_hosted)` (line 18015).
- Problem: FEAT-162 only covers the *owner's* first run. A user invited via FEAT-004 also has a "first run", but no story declares what their first-run experience looks like (no residency, no checklist, no onboarding). This is in EPIC-001 territory by the invite-acceptance path but is silently absent from both epics.
- Fix: Either add a cross-reference in FEAT-162 pointing invitee first-run to EPIC-001 STORY-010 (or wherever the invite-accept flow lives), or add an invitee first-run story under EPIC-001.

---

## Missing / dangling references

### D1. FEAT-112 cites `FEAT-163/STORY-409` as the first-run residency pin — wrong ids

- Cites: FEAT-112 description (line 1473).
- Quoted: `The region is set once at first-run (FEAT-163/STORY-409) and is immutable for the life of the workspace` (line 1473).
- Problem: FEAT-163 is Public status page (line 1944); STORY-409 is Cross-tenant roster in saas mode (line 19194). Both exist but mean the wrong thing here. The correct ids are FEAT-162 / STORY-387 (line 18011). Duplicate of C6 above, surfaced here as a dangling-semantic-reference item.
- Fix: Replace with `FEAT-162/STORY-387`.

### D2. FEAT-173 cites `FEAT-164` for the in-app status widget — wrong id

- Cites: FEAT-173 description (line 2042).
- Quoted: `broadcast in real time to every affected tenant's in-app status widget (FEAT-164)` (line 2042).
- Problem: FEAT-164 is in-product support contact (line 1952). The status widget is FEAT-163 (line 1942). STORY-412 AC-001 correctly uses FEAT-163 (line 19408), which is further evidence this is a typo. Duplicate of M1, surfaced here for the missing-references inventory.
- Fix: Replace with `FEAT-163`.

### D3. No missing FEAT-XXX / STORY-XXX id inside EPIC-012 itself

All ids explicitly cited inside FEAT-162..FEAT-169 and STORY-387..STORY-402 resolve to existing entries:

| Cited id | Citing line | Status |
|---|---|---|
| FEAT-096 | 1996 (in FEAT-168) | exists line 1303 |
| FEAT-098 | 1996 (in FEAT-168) | exists line 1322 |
| FEAT-130 | 18041 (in STORY-387) | exists line 1651 |
| FEAT-173 | 2005 (in FEAT-169) | exists line 2039 |
| FEAT-175 | 1932, 1965, 1996, 2005 | exists line 2059 |
| FEAT-177 | 1932 (in FEAT-162) | exists line 2078 |
| FEAT-179 | 1955, 1965, 1976, 2005 | exists line 2099 |
| FEAT-180 | 2005 (in FEAT-169) | exists line 2110 |
| FEAT-181 | 1955 (in FEAT-164) | exists line 2120 |

### D4. Implied dependencies that are never declared

- **FEAT-162 → FEAT-177 is asserted in prose, never in metadata.** FEAT-162 description (line 1932) says the install wizard (FEAT-177) `has already completed` as a precondition. FEAT-177 description (line 2081) says `the control plane refuses tenant traffic until the wizard has reported "complete"`. No `depends_on` exists at feature level. Consider adding a `depends_on: [FEAT-177]` (self_hosted only) or moving the precondition into STORY-387.
- **FEAT-169 → FEAT-173/175/180 is asserted in prose, never in metadata.** FEAT-169 description (line 2005) names three upstream event sources but STORY-402 has no `depends_on` on any of them.
- **STORY-388 → STORY-387.** See M3.
- **STORY-398 → FEAT-179 `docs` channel.** FEAT-166 prose says the admin-refresh path requires FEAT-179; no story binds them.

### D5. Missing features the epic's stated scope promises

EPIC-012 description (line 293) lists `pricing/cost forecast tooling`. FEAT-168 delivers the calculator; no separate story covers:

- **A pricing catalog snapshot viewer.** If the calculator uses current pricing (STORY-401 line 18697 assumes 30-day observed variance), there is no story for viewing the currently-loaded provider pricing or the Antirion plan catalog — the inputs the calculator relies on. Consider adding, or referencing FEAT-056 pricing overrides (line 816) explicitly in STORY-401's narrative.

No other scoped-but-missing features were identified.

---

## Appendix — models touched

Models named in EPIC-012 stories and their adequacy for the stated ACs:

| Model | Line | Adequate for EPIC-012 stories? |
|---|---|---|
| `ResidencyConfig` | 22413 | No — missing `mode`, `source` (C2). |
| `SetupChecklist` | 23218 | Yes. |
| `StatusPageIncident` | 23242 | Coexists with `PlatformIncident` without a declared relationship (M2). |
| `SupportTicket` | 23266 | No — missing `destination`, `redaction_profile` (C1). |
| `TosAcceptance` | 23294 | Yes for the acceptance event. No `LegalDocument` exists for the document itself (M8). |
| `HelpArticle` | 23317 | No — missing `pinned`, no usage counter, no local-anchor fallback (C3, M9). |
| `WorkerQueue` | 23336 | Adequate; observed through the wrong feature (C5). |
| `WorkerJob` | 23361 | Adequate fields, but needs `owner_org_id` to make STORY-400 safe (M4). |
| `PricingQuote` | 23550 | Adequate fields; `breakdown` needs a declared shape for mode-specific lines (M11). |
| `Notification` | 23940 | No — `kind` enum is too narrow for FEAT-169's promise (C4). |
| `PlatformIncident` | 23424 | Adequate, but overlaps `StatusPageIncident` (M2). |
