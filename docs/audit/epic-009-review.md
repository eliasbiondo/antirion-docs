# EPIC-009 "Alerts and notifications" — requirements.yaml audit

Scope: EPIC-009 (line 213) and its features FEAT-099..FEAT-106 (lines 1329–1418), plus stories STORY-223..STORY-246 (lines 11749–12916). Cross-referenced against `project.notifications_model` (line 37), `project.non_functional_baseline.observability` (line 32), `project.non_functional_baseline.availability_slo` (line 28), the data models section (line 20712+), and every inbound reference to an EPIC-009 entity from EPIC-004, EPIC-008, EPIC-010, EPIC-011, EPIC-012 and EPIC-013.

This audit is read-only. `docs/requirements.yaml` is unchanged.

---

## Summary

EPIC-009 gets the shape right — rules, events, runbooks, channels, snooze, on-call, SLOs — but it does not line up with the canonical framing the baseline lays down in January 2026. Three systemic problems dominate:

1. **The notifications_model contract is ignored.** The baseline at line 37 makes audience resolution the backbone of every notification-bearing event — stories are supposed to name canonical roles (acting principal, resource owner, org-scoped contacts, platform operator, saas sub-queues) and let FEAT-102 route channels. EPIC-009 instead lets alert rules carry a raw `channels: [string]` list (STORY-223 AC-001 at line 11770, data model field at line 22200) with no audience concept. STORY-232 — the single story for FEAT-102 — never mentions audience roles, collapse rules, deployment modes, or the resolved-audience audit trail required by line 38. This is the single largest gap in the epic.

2. **Deployment-mode awareness is absent from every EPIC-009 feature.** Line 36 requires "every feature that differs in scope, availability or data shape between the two modes" to declare its mode availability. FEAT-099–FEAT-106 declare none. FEAT-104 incidents overlap with the platform-wide incident flow in FEAT-173, FEAT-105 on-call has no meaningful "team" in a single-operator self_hosted install, and FEAT-102 channels silently assume SaaS integrations (PagerDuty, Slack) that can be unavailable or air-gapped per FEAT-179.

3. **Platform-scope alerting is not representable.** The baseline promises a specific "ingestion-health alert" at line 30 and a worker-fleet alert class at line 18 (FEAT-167 surfaces the data). STORY-246 declares platform-scope SLO events at line 12915. But `AlertRule.org_id` is non-nullable (line 22163–22164) and the FEAT-099 scope picker enumerates only `{provider, team, project, model, key}` (STORY-223 AC-005 at line 11811). There is no way for the platform operator to author a rule that lives outside any tenant.

Beyond those three, the epic has a specific broken cross-reference from EPIC-011 (FEAT-101 vs FEAT-102), duplicated ack/snooze semantics between FEAT-100 and FEAT-103, a StatusPageIncident data model that doesn't carry the fields the incident story requires, a PostMortem model that contradicts the "structured template with action items" story, a severity vocabulary that drifts from `{info, warn, crit}` to `"high"`, and an example SLO target in STORY-244 that contradicts the gateway 99.95% baseline.

Scale of issues: 7 critical, 11 major, 10 minor, plus a dedicated section of missing/dangling references.

---

## Critical

### C1. Alert rules bypass the canonical notifications_model

- Line 37 (`project.notifications_model`): "Stories cite these roles instead of inventing local language, and acceptance criteria name the audience per deployment mode… Delivery channels per role are resolved by FEAT-102 notification-channels routing."
- Line 11770 (STORY-223 AC-001): `I pick channels [email, slack]`
- Line 22200 (AlertRule.channels): `type: json`
- Line 12321–12355 (STORY-232, the only FEAT-102 story): never mentions `security_contact`, `billing_contact`, resource owner, platform operator, trust_and_safety, or any audience role.

**Problem.** The baseline is explicit that alert stories must cite the canonical audience roles and let FEAT-102 resolve channels by role and deployment mode. EPIC-009 instead stores the channel list directly on the rule, so a rule author picks `email` and `slack` as channel strings with no audience concept. This also breaks the baseline's requirement at line 38 that "every audit record on a notification-bearing event records the resolved audience list and the channel attempt" — there is no audience list to record because the rule never had one.

**Fix.** Rewrite FEAT-102 and AlertRule to be role-driven:

1. Replace `AlertRule.channels: json` with `AlertRule.audience: json` whose shape is a list of canonical role references (e.g., `{role: "resource_owner"}`, `{role: "org_contact", contact: "security_contact"}`, `{role: "platform_operator"}`, `{role: "user_subscription"}`).
2. Rewrite STORY-232 acceptance to resolve `audience → user set → channels` per FEAT-102, deployment mode and recipient `NotificationPreference`.
3. Add an acceptance stating that every AlertEvent delivery records the resolved audience list and per-channel attempt on the AlertTimelineEntry.

### C2. STORY-232 is silent on deployment-mode collapse rules

- Line 37–38: notifications_model spells out (a)(b)(c) identical across modes, (d) platform operator = Antirion staff in saas / platform admin in self_hosted, (e) Antirion sub-queues saas-only, self_hosted fallback to platform admin unless FEAT-179 phone-home is enabled, unset tenant contacts fall back to Org.owner (saas) or platform admin (self_hosted), cross-tenant signals dropped in self_hosted.
- Line 12321–12355 (STORY-232): two scenarios, Slack fire and PagerDuty ack-sync. No mention of modes, fallbacks, or platform-operator routing.

**Problem.** FEAT-102 is the only place the collapse rules are supposed to live. STORY-232 never exercises them. Without this, every other story that routes a notification (STORY-223, STORY-229, STORY-232, STORY-237, STORY-240, STORY-246) has no defined behavior in self_hosted and no fallback semantics for unset contacts.

**Fix.** STORY-232 needs acceptance criteria for at minimum: unset security_contact in each mode, platform-operator routing in each mode, cross-tenant signal dropped in self_hosted, and the audit-trail of resolved audience per line 38. Compare with FEAT-028 STORY-069 (line 5250–5253) and FEAT-134 / FEAT-115 (line 13715) which *do* spell this out and can be used as the model.

### C3. Platform-scope alerts are not representable in the data model

- Line 22163–22164 (AlertRule): `org_id type: FK:Org` with no `nullable: true`.
- Line 11811 (STORY-223 AC-005): "Scope must be one of provider:<id>, team:<id>, project:<id>, model:<slug>, key:<last4>"
- Line 30 (baseline): "ingestion gaps trigger the ingestion-health alert" — promised, never declared anywhere as an AlertRule definition.
- Line 12914–12916 (STORY-246): for platform-scope SLO the event must route to platform operator, but the AlertRule that backs that SLO has no place to live — it cannot be org-scoped.
- Line 18 (baseline): "Worker fleet health is surfaced by FEAT-167" — FEAT-167 is observability, not a rule authoring surface.

**Problem.** The canonical rule type cannot express ingestion-health, worker-fleet-health, cluster-health or platform SLO rules because every AlertRule belongs to a tenant. EPIC-013 doesn't define an alternative authoring surface either.

**Fix.** Either (a) make `AlertRule.org_id` nullable and add an `AlertRule.scope_kind` enum with values `{tenant, platform}` that gate rule creation and reading by mode + role, or (b) introduce a separate `PlatformAlertRule` model owned by EPIC-013 and link it from the baseline. Whichever path, the ingestion-health and worker-fleet-health rules need concrete acceptance criteria somewhere.

### C4. Broken cross-reference from EPIC-011 to FEAT-101

- Line 17993 (STORY-386 AC-001, in FEAT-161): "An AlertEvent is created and the configured NotificationChannels fire (see FEAT-101)"
- FEAT-101 (line 1353–1361) is **Runbooks**, not notification channels. FEAT-102 is the notification-channels feature.

**Problem.** Direct broken reference — the cited feature does not deliver notifications.

**Fix.** Change "see FEAT-101" to "see FEAT-102" on line 17993. Also consider a `data_models: [NotificationChannel]` entry — the story refers to a `NotificationChannels` entity that does not exist in the models section (see M-Dangle-3 below).

### C5. STORY-237 creates incidents with fields the data model does not carry

- Line 12558–12562 (STORY-237 AC-001): "I click 'Declare incident', pick severity SEV-2 and add 2 participants" → "A StatusPageIncident is created… with state 'investigating'"
- Line 23242–23265 (StatusPageIncident model): fields are `id, title, impact {minor|major|critical}, status {investigating|identified|monitoring|resolved}, components, updates, started_at, resolved_at`. There is no `severity`, no `participants`, no `alert_event_id`, no `org_id`.
- Line 12561: "A StatusPageIncident is created linked to the AlertEvent" — no FK field exists to carry that link.

**Problem.** The story cannot be implemented against the declared model. Severity SEV-2 and participants are narrative, not schema.

**Fix.** Either add fields to StatusPageIncident (`severity string`, `participants json`, `alert_event_id FK:AlertEvent nullable`, `org_id FK:Org`) or factor a separate `Incident` model from the public-status-page object (the StatusPageIncident is a *public* artifact; an internal incident with participants and alert linkage is a different concept — see also Major M1).

### C6. PostMortem model contradicts STORY-238's structured template

- Line 12604–12606 (STORY-238 AC-001): "I see a template with required sections summary, timeline, impact, root_cause and action_items" / "I cannot save without the required sections filled"
- Line 12608–12614 (STORY-238 AC-002): "A saved PostMortem with 3 action items" / "Each action item shows owner, due_date and status (open, in-progress, done)"
- Line 23064–23084 (PostMortem model): fields are `id, alert_event_id, title, content: string, author_user_id, created_at, updated_at`. Single string `content` — no structured sections, no action items, no ActionItem model anywhere in the file.

**Problem.** The declared schema cannot enforce required sections or track action items with owners, due dates and status.

**Fix.** Either (a) replace `content: string` with structured fields `summary, timeline, impact, root_cause` plus an `ActionItem` model (`id, post_mortem_id, description, owner_user_id, due_date, status {open|in_progress|done}`), or (b) loosen STORY-238 to "free-form content with template placeholders" and drop the enforcement promise. Option (a) is consistent with the "structured" promise in FEAT-104 description at line 1388.

### C7. AlertSnooze by fingerprint is unimplementable against the model

- Line 12470–12474 (STORY-235 AC-001): "An AlertEvent is active with fingerprint 'host=foo,model=gpt-5'" / "An AlertSnooze row with the fingerprint is created" / "Other events from the same rule with different fingerprints still fire"
- Line 23042–23063 (AlertSnooze model): fields are `id, rule_id, reason, created_by_user_id, created_at, ends_at, cancelled_at`. **No `fingerprint` field.**

**Problem.** Mute-by-fingerprint is a P0 story (line 12465) but the model only supports rule-wide snooze. Other events from the same rule cannot fire "with different fingerprints" because the snooze has no fingerprint to discriminate on.

**Fix.** Add `fingerprint: string nullable` to AlertSnooze. Update STORY-233 evaluation semantics to "snooze applies when AlertSnooze.fingerprint is null OR matches AlertEvent.fingerprint."

---

## Major

### M1. StatusPageIncident is the wrong concept for FEAT-104

- Line 1388 (FEAT-104): "declare incidents with severity/participants/updates, and write structured post-mortems linked to affected alerts"
- Line 23243 (StatusPageIncident): "A public incident posted on the status page."
- FEAT-173 (line 2040–2047) owns platform-wide incident broadcasts — this is where a public status page lives.

**Problem.** FEAT-104 conflates a *response* incident (internal, participants, linked to an alert) with a *public status-page* post. The declared model is the latter. Also, STORY-237 requires declaring from an AlertEvent — in self_hosted, an individual tenant declaring a "public incident" on someone else's status page is undefined.

**Fix.** Introduce a distinct `Incident` model for response-side state (participants, linked AlertEvent, severity, org_id), reserve `StatusPageIncident` for FEAT-173's public posts, and have STORY-237 create an `Incident` and optionally *publish* it as a `StatusPageIncident` through FEAT-173.

### M2. FEAT-100 and FEAT-103 overlap and drift

- FEAT-100 (line 1343–1352) description: "Acknowledge, resolve, snooze and escalate fired alerts." Stories STORY-228 (ack+resolve), STORY-229 (snooze+escalate).
- FEAT-103 (line 1373–1384) title: "Alert snooze and acknowledge" — description: "Snooze an alert rule or acknowledge an active alert". Stories STORY-233 (snooze rule), STORY-234 (ack alert), STORY-235 (mute fingerprint).
- STORY-229 AC-001 (line 12167–12173) snoozes an *event* for 1h; STORY-233 AC-001 (line 12367–12374) snoozes a *rule* for 2h. Different targets under overlapping feature titles.

**Problem.** The two features cover the same lifecycle verbs with slightly different targets. STORY-228 + STORY-234 both implement "acknowledge an AlertEvent". A rule author reading FEAT-100 and FEAT-103 cannot tell which owns ack or which owns snooze.

**Fix.** Collapse into one feature or redraw boundaries: FEAT-100 = AlertEvent lifecycle (ack, resolve, escalate an event); FEAT-103 = AlertRule-level suppression (snooze rule, snooze rule-by-fingerprint). Remove STORY-229 AC-001 (event-snooze) — that behavior already exists in STORY-233's by-rule form restricted to one fingerprint (which is STORY-235).

### M3. Severity vocabulary drifts across EPIC-009

- Line 11765 / 22199: `severity {info, warn, crit}` — the canonical enum on AlertRule.
- Line 12496 (STORY-236 AC-001): "I filter by severity 'high'"
- Line 12557 (STORY-237 AC-001 given): "An AlertEvent is firing at severity 'high'"

**Problem.** `high` is not in the declared enum. Stories that hard-code it either describe behavior that cannot be represented or silently accept a different vocabulary.

**Fix.** Rewrite STORY-236 and STORY-237 to use `{info, warn, crit}`. Alternatively, expand the enum to `{info, warn, high, crit}` if `high` is meaningful and update line 22199 accordingly — but pick one.

### M4. STORY-244's canonical SLO example contradicts the availability baseline

- Line 28 (baseline): "Control-plane API targets 99.9% monthly availability; gateway data plane targets 99.95%."
- Line 12867 (STORY-244 AC-001): "I create an SLO 'gateway-availability' with target 99.9% over 30d"

**Problem.** The baseline pins gateway data plane at 99.95%. The single concrete SLO example in STORY-244 uses 99.9% for the gateway — which is the *control-plane* target, not the gateway target.

**Fix.** Change the example to target 99.95% (or split into two examples: "control-plane-availability" at 99.9% and "gateway-availability" at 99.95%).

### M5. FEAT-106 never wires error-budget burn into release gating

- Line 28 (baseline): "Error budgets are tracked per FEAT-106 and **gate release promotion when burned**."
- FEAT-106 stories STORY-244, STORY-245, STORY-246 cover define/view/alert-on-burn. No story covers the release-promotion gate.
- FEAT-174 (line 2049–2058, EPIC-013) covers build promotion and "watch SLO impact in near-real time, and roll back on breach" — this is the counterpart — but the coupling is informal.

**Problem.** The promise in the baseline is not backed by a story. Neither FEAT-106 nor FEAT-174 declares that a burned error budget blocks promotion.

**Fix.** Add a STORY under FEAT-106 (or under FEAT-174) that formalises the gate: "Given an SLO with error_budget_remaining <= 0, when a release-promotion attempt is made, then it is rejected with reason 'slo-burned' and an AuditLog entry is recorded."

### M6. STORY-223 AC-001 fails STORY-223 AC-004's own validation

- Line 11763–11775 (AC-001): fills name, category, severity, scope, metric `p95_latency_ms`, operator, threshold, `for_duration 5m`, `cooldown 15m`, channels — and clicks Create. Rule saves successfully.
- Line 11795–11802 (AC-004): "metric 'p95_latency_ms' needs a window to compute the percentile" / "I leave window blank" / "The rule is not saved".

**Problem.** AC-001 does not set `window`. By AC-004's own rule that should block save, but AC-001 asserts it saves.

**Fix.** Add `I set window "30m"` (or similar) to AC-001's when-block, and add `window: string` to the form inputs explicitly listed there.

### M7. STORY-223's live-preview string is missing the window field

- Line 11783 (AC-002): 'The preview renders "when {scope}.{metric} {operator} {threshold} for {for_duration} → fire {severity}, cooldown {cooldown}"'

**Problem.** The preview omits `window`, which is a first-class required input for percentile metrics (see AC-004 and data model at line 22187–22189). A rule author editing `window` from `30m` to `5m` sees no preview change.

**Fix.** Extend the preview: `"when {scope}.{metric} over {window} {operator} {threshold} for {for_duration} → fire {severity}, cooldown {cooldown}"`.

### M8. FEAT-102 does not list the in-app inbox as a channel

- FEAT-102 description (line 1366): "Deliver notifications via email, Slack, PagerDuty and webhooks."
- FEAT-169 (line 2003–2008): "In-product notification inbox" surfaces "alert fires" — so the in-app inbox *is* an alert channel.
- Line 23940–23962 (Notification model): `kind` enum includes `alert`.

**Problem.** The in-app inbox is a user-addressable channel that the rest of the product treats as a first-class destination for alert fires, but FEAT-102 doesn't declare it, and STORY-232 doesn't exercise it.

**Fix.** Add "in-app" to the FEAT-102 description and add an acceptance to STORY-232 that writes a Notification row for alert fires per recipient.

### M9. STORY-240 fallback uses `team lead` while notifications_model names `Team.owner`

- Line 37: "(b) the owning principal on the resource (Resource.owner_user_id or Team.owner)"
- Line 20995 (Team model): `lead_user_id` (no `owner` field anywhere on Team)
- Line 12707 (STORY-240 AC-002): "The team lead user is paged instead"

**Problem.** The notifications_model names "Team.owner" but the actual schema uses `Team.lead_user_id`. The story is correct-against-the-model but inconsistent with the baseline's canonical language. Every other team-ownership reference in the file inherits the same naming mismatch.

**Fix.** Align the baseline and the model: either rename `Team.lead_user_id` → `Team.owner_user_id`, or change the notifications_model at line 37 to say "Team.lead_user_id". Once aligned, STORY-240 AC-002 should quote the canonical name.

### M10. PagerDuty is hard-coded in STORY-229 and STORY-232 with no integration gating

- Line 12181 (STORY-229 AC-002): "A PagerDuty notification is sent to the escalation policy"
- Line 12339 (STORY-232 AC-001): "A Slack message is posted"
- Line 12345–12348 (STORY-232 AC-002): "An on-call responder acknowledges in PagerDuty"
- FEAT-179 (line 2099–2109) phone-home channels — PagerDuty integration in self_hosted depends on outbound reach to a SaaS; air-gapped installs cannot reach PagerDuty.
- EPIC-010 (line 226–258) owns integration configuration (Slack, PagerDuty, webhooks).

**Problem.** Both acceptances assume the integration exists and is reachable. In self_hosted air-gapped installs PagerDuty is not usable. There is no "if PagerDuty is configured and reachable" qualifier and no fallback when it isn't.

**Fix.** Add mode/integration gating: "Given the PagerDuty integration is configured and the channel is reachable… otherwise fall back to the next channel on the resolved audience list and record an AlertTimelineEntry of type `page` with error='channel_unavailable'".

### M11. AlertRule has no mode field and no platform-vs-tenant flag

- Line 22157–22212 (AlertRule model): no `mode`, no `scope_kind`, no `platform_scoped` boolean.
- STORY-246 (line 12913–12916) speaks of "tenant-scope SLO" vs "platform-scope SLO" events but the AlertRule that backs a platform-scope SLO has no way to declare itself.

**Problem.** The tenant vs platform split that STORY-246 and the baseline rely on has no data-model anchor. Rule evaluators cannot filter "give me only the platform rules for this node".

**Fix.** Add `AlertRule.scope_kind string {tenant|platform}` (default tenant), tie to C3 fix.

---

## Minor

### m1. `AlertTimelineEntry.type` has both `page` and `escalate`

- Line 22277: enum `fire|ack|resolve|page|note|snooze|escalate`
- Line 12183 (STORY-229 AC-002): "An AlertTimelineEntry of type 'page' is recorded" — for a manual escalation click.
- Line 12836 (STORY-243 AC-001): "An AlertTimelineEntry records 'escalation.secondary'" — which is neither of the declared enum values.

Pick one: `escalate` for the action, `page` for the delivery side-effect; then make the stories consistent. `escalation.secondary` is ad-hoc and not in the enum.

### m2. STORY-237 "Participants are notified" has no channel resolution

- Line 12562: "Participants are notified" — no reference to FEAT-102, no role in notifications_model.

Add an explicit sub-acceptance that routes via FEAT-102 using the acting-principal and participant user IDs.

### m3. STORY-227 subscribe flow implies an undeclared model

- Line 12080 (AC-001): "A subscription row is created linking me to the rule"
- `data_models: [AlertRule, NotificationPreference]` (line 12083–12085) — neither is the subscription row.

Either add an `AlertRuleSubscription` model or repurpose NotificationPreference.event_type = `alert_rule:<id>` and specify that explicitly.

### m4. STORY-227 does not reference FEAT-102 for channel resolution

Same story, same problem — "Future fires notify me via my preferred channel" is an unresolved `preferred` concept.

### m5. STORY-236 post-mortem attach has no audit entry

- Line 12504–12507 (AC-002): PostMortem linked, but no `AuditLog` in `data_models` (line 12540) and no audit acceptance. Compare STORY-231 AC-002 (line 12278) which audits "runbook.update".

Add `AuditLog` and an entry for "post_mortem.create".

### m6. STORY-223 AC-007 "first evaluation within 10 seconds of save" vs 30s hot-reload SLA

- Line 21 (baseline): "alert rules… propagate to every node within 30 seconds"
- Line 11828 (AC-007): "The first evaluation runs within 10 seconds of save"

If a newly-created rule must evaluate within 10s but hot-reload takes up to 30s, the evaluation can run against stale config on some nodes. Either tighten the hot-reload SLA for alert rules or loosen AC-007 to 30s.

### m7. STORY-223 `category` has no enum

- Line 22175–22176 (AlertRule model): `category: string` (undocumented).
- AC-001 uses `category: "latency"`, AC-002 does not validate category.

Declare an enum or acceptance for category.

### m8. `AlertRule.channels: json` while the POST body is `channels: [string]`

- Line 11869–11870 (POST body): `channels: [string]`
- Line 22200–22201 (model): `channels: json` (unspecified shape)

Channels for Slack need a target channel name, PagerDuty needs a service key, webhook needs a URL — all richer than a plain string. Specify the json shape, or resolve via audience (see C1) so the rule only stores audience references.

### m9. STORY-232 covers only Slack fire and PagerDuty ack-sync

- Line 12331–12348: two acceptance criteria, both happy path, neither covers email, webhook, delivery retry, signature verification failure, or per-recipient failure.
- FEAT-102 title (line 1366) promises "email, Slack, PagerDuty **and webhooks**".

Add at least one AC per declared channel and an AC for retry/backoff surfacing `At-least-once delivery with exponential backoff to 6h` (line 12354).

### m10. STORY-246 platform-operator wording leaks sub-queue nomenclature

- Line 12915: "the platform operator audience — **Antirion SRE** in saas, platform admin in self_hosted"
- Line 37–38 (notifications_model): (d) platform operator = "Antirion staff"; `sre` is an (e) sub-queue that only exists in saas.

The intent is fine (SRE is a reasonable sub-queue pick for SLO burn) but the wording mixes role (d) with sub-queue (e). Either state "platform operator, sub-queued to Antirion SRE in saas" or stay at role (d). Compare with line 14964, which uses the same "Antirion SRE / platform admin" pairing — this is a recurring idiom but should be explicit about the (d)/(e) split.

---

## Cross-epic

### X1. EPIC-008 fires `AlertEvent` directly, bypassing AlertRule

- Line 10635–10640 (STORY-189, FEAT-084 in EPIC-008): "A BudgetPolicy with soft-alert 80% and action 'alert-only'" → "An AlertEvent of severity 'warn' is generated with type 'budget.soft'" — no AlertRule is created, no FEAT-099 surface is invoked.
- Line 22219–22220 (AlertEvent model): `rule_id type: FK:AlertRule` (not nullable).

**Problem.** An AlertEvent must reference a rule, but the budget path never creates one. Either budget alerts pre-seed a synthetic AlertRule per policy (never described) or the model constraint is violated. Budget alert categories are also missing from the FEAT-099 category enum (see m7) and the FEAT-099 scope-picker enum (line 11811) does not list `budget:<id>`.

**Fix.** Either make `AlertEvent.rule_id` nullable with a `source: string` field (`{rule, budget, anomaly, slo, system}`), or require that budget policies create and maintain an AlertRule of category `budget`. Mirror for anomaly signals (line 6151, Anomaly → AlertEvent is implied but not wired).

### X2. Deprovisioning reassigns `AlertRule.owner_user_id` which does not exist

- Line 13183 (STORY-269, FEAT-111 in EPIC-010): "AlertRule.owner_user_id is reassigned to the team lead"
- Line 22157–22212 (AlertRule model): no `owner_user_id` field.

**Problem.** Direct data-model mismatch. The cascade cannot execute against the declared model.

**Fix.** Add `owner_user_id: FK:User nullable` to AlertRule (makes sense — rules need an owner for notifications when the creator leaves) and document the default (creator). This also feeds FEAT-102's audience resolution for "resource owner" role.

### X3. EPIC-010 audit-sink-degraded uses the canonical audience pattern EPIC-009 should adopt

- Line 13714–13715 (STORY-263, FEAT-115): "An AlertEvent of severity 'warn' fires for 'audit.sink.degraded'" / "The event is delivered to Org.security_contact (falling back to Org.owner) and to the platform operator audience — Antirion SRE in saas, platform admin in self_hosted".

**Observation (not a defect).** This story demonstrates the notifications_model contract correctly — named contact, documented fallback, mode-aware platform operator. It is the template STORY-232 should follow. Worth citing in any fix to C1/C2 as the gold-standard pattern.

### X4. EPIC-011 circuit-open and provider-down generate AlertEvents without AlertRules

- Line 7757, 16411, 16439: gateway generates AlertEvents for `circuit.open`, `provider.down`.
- These events have no rule_id source. Same issue as X1.

**Fix.** Included in X1's fix.

### X5. EPIC-004 Anomaly → AlertEvent linkage is implied but missing

- Line 6151 (STORY-085): Anomaly of severity "crit" is acted on in UI. No acceptance says anomalies become AlertEvents.
- Line 21575 (Anomaly model): exists but not linked to AlertEvent.

**Fix.** Either declare in STORY-085 that a `crit` Anomaly fans out to an AlertEvent (with source='anomaly'), or declare explicitly that anomalies remain a separate signal class.

### X6. EPIC-011 ingestion-health alert is promised but never defined

- Line 30 (baseline): "ingestion gaps trigger the ingestion-health alert"
- No story in EPIC-009, EPIC-011, EPIC-012 or EPIC-013 creates, owns or fires this alert.

**Fix.** Add an AC under FEAT-135–FEAT-161 (EPIC-011 ingestion) or under FEAT-170 (EPIC-013 cluster & fleet health) that defines the rule (metric = row-durability deficit or ingest gap duration, threshold derived from the 99.99% baseline) and fires through FEAT-102's platform-operator path. This is a platform-scope AlertRule — ties to C3.

### X7. EPIC-013 FEAT-173 public-incident flow may conflict with STORY-237

- FEAT-173 (line 2039–2048): platform operator declares platform incidents broadcast via FEAT-164 and the in-app status widget.
- STORY-237 (line 12545–12586): any on-call engineer "declares an incident" against a StatusPageIncident.

**Problem.** In self_hosted, the platform admin is the platform operator; a tenant on-call cannot post to "the" status page. In saas, a tenant on-call definitely cannot publish to Antirion's public status page. The StatusPageIncident used in STORY-237 is the same model FEAT-173 broadcasts — so tenant-level declaration would leak tenant state to a shared public surface.

**Fix.** Separate tenant-internal Incident from public StatusPageIncident (see M1) and state explicitly that tenant on-call can declare the former and FEAT-173 gates publication to the latter.

---

## Missing / dangling references

Every FEAT-XXX or STORY-XXX id referenced in or from EPIC-009 is verified below. "Exists" means the id has a top-level `- id:` entry in docs/requirements.yaml. "Dangling" means it is cited but undefined or mismatched.

### (a) Cited feature/story that has no definition

- **(a.1)** Line 17993 — "see FEAT-101" — cited from STORY-386. FEAT-101 *exists* (line 1353) but is Runbooks, not NotificationChannels. This is a **misdirected reference** (see C4). The id the author meant (FEAT-102) does exist.
- **(a.2)** Line 17993 — entity "NotificationChannels" referenced in prose. No model `NotificationChannel`, `NotificationChannels`, or `Channel` exists in the models section (line 20712+). The closest are `NotificationPreference` (line 21045) and `Notification` (line 23940). **Dangling entity reference.**
- **(a.3)** Line 12080 (STORY-227 AC-001) — "A subscription row is created". No model `AlertRuleSubscription` or similar exists; `data_models: [AlertRule, NotificationPreference]` on STORY-227 is a placeholder. **Dangling entity reference.**
- **(a.4)** Line 12610 (STORY-238 AC-002) — "A saved PostMortem with 3 action items" / "Each action item shows owner, due_date and status". No `ActionItem` model exists in the models section. **Dangling entity reference** (see C6).
- **(a.5)** Line 13183 (STORY-269, EPIC-010) — "AlertRule.owner_user_id". Field does not exist on AlertRule (see X2). **Dangling field reference.**
- **(a.6)** Line 12470–12474 (STORY-235) — "An AlertSnooze row with the fingerprint is created". `fingerprint` field does not exist on AlertSnooze (see C7). **Dangling field reference.**
- **(a.7)** Line 12558 (STORY-237) — StatusPageIncident "severity SEV-2 and 2 participants". Neither `severity` nor `participants` fields exist on StatusPageIncident (see C5). **Dangling field reference.**
- **(a.8)** Line 12561 (STORY-237) — "A StatusPageIncident is created linked to the AlertEvent". No FK field links StatusPageIncident to AlertEvent (see M1). **Dangling relation.**
- **(a.9)** Line 12496, 12557 (STORY-236, STORY-237) — severity value "high" is cited but not a declared enum value (`info|warn|crit`). **Dangling enum value** (see M3).

### (b) Dependency feature implied by the narrative but never declared

- **(b.1)** STORY-232 (FEAT-102) implies integration configuration (Slack app, PagerDuty service, webhook endpoint signing). EPIC-010 FEAT-116 and FEAT-114 cover integrations. STORY-232's `depends_on` is only `STORY-223` (line 12329–12330). **Undeclared dependency** on EPIC-010 integrations.
- **(b.2)** STORY-229 AC-002 (PagerDuty escalation) and STORY-232 AC-002 (PagerDuty ack sync) depend on an inbound PagerDuty webhook receiver with signature verification. No story declares the webhook-receiver endpoint. **Undeclared dependency.**
- **(b.3)** STORY-244–STORY-246 (FEAT-106) depend on a metrics/SLI-query engine. Nothing in EPIC-009 or EPIC-004 declares that `sli_query` parser/executor. Slo.sli_query (line 23665) is a string field with no documented grammar. **Undeclared dependency.**
- **(b.4)** STORY-237 (FEAT-104) declare-incident depends on FEAT-173 (platform incident/maintenance) and FEAT-164 (in-app status widget) to actually publish. No `depends_on` declared. **Undeclared dependency** (also see X7).
- **(b.5)** STORY-223 AC-001 (`enabled=true and evaluated against live telemetry immediately on save`) depends on the rule-evaluation worker and metrics backend. No dependency on EPIC-012 FEAT-167 (worker fleet observability) or an explicit evaluation-engine feature is declared. **Undeclared dependency.**
- **(b.6)** STORY-240 (resolve on-call) depends on team membership (FEAT-006) and OncallSchedule existence. No `depends_on: STORY-013` or equivalent. **Undeclared dependency** (minor).
- **(b.7)** STORY-246 (SLO burn alert routing) depends on FEAT-102; it says "per FEAT-102" (line 12914) but does not declare FEAT-102 as a feature-level dep — acceptable prose reference, still worth a `depends_on` on STORY-232.

### (c) Features that the epic's scope promises but are absent from the features list

- **(c.1)** Baseline line 30 promises an "ingestion-health alert". Not declared in EPIC-009 or EPIC-011 or EPIC-013 (see X6). **Missing feature/story.**
- **(c.2)** Baseline line 18 promises "Worker fleet health is surfaced by FEAT-167" — FEAT-167 exists as an observability surface but no alerting story ties worker-queue-stalled signals into an AlertEvent. The alerts-for-worker-health path is implied but absent. **Missing story.**
- **(c.3)** Baseline line 28 promises "Error budgets are tracked per FEAT-106 and gate release promotion when burned." The release-gating half of that sentence has no story anywhere in FEAT-106 or FEAT-174 (see M5). **Missing story.**
- **(c.4)** EPIC-009 description (line 215) says "multi-channel notifications" but the in-app inbox channel is not declared in FEAT-102 (see M8). **Missing channel.**
- **(c.5)** Notifications_model at line 38 says "every audit record on a notification-bearing event records the resolved audience list and the channel attempt, so routing correctness is diffable against this policy." No EPIC-009 story writes such an audit record. **Missing acceptance criterion across all notification-bearing stories in EPIC-009.**
- **(c.6)** FEAT-102 description (line 1366) lists email, Slack, PagerDuty, webhooks — no story exercises webhook delivery (no webhook AC in STORY-232). **Missing story coverage** for a declared channel.
- **(c.7)** EPIC-008 budget alerts and EPIC-011 gateway-generated alerts (circuit.open, provider.down, byok.degraded) need a surface for tenant admins to manage their routing — there is no FEAT-099 category for `system` or `gateway` alerts and the scope picker cannot scope to a provider-circuit condition. **Missing rule-authoring coverage** for system-generated alerts (ties to X1, X4).

---

## Notes on methodology

- Read baseline 1–73, EPIC-009 (213–225), FEAT-099..FEAT-106 (1329–1418), STORY-223..STORY-246 (11749–12916), the alerts-related models (AlertRule, AlertEvent, AlertTimelineEntry, Runbook, AlertSnooze, PostMortem, OncallSchedule, OncallShift, StatusPageIncident, Slo, Notification, NotificationPreference) at lines 21045–23962.
- Grepped every inbound cross-reference to AlertRule, AlertEvent, FEAT-099..FEAT-106 from other epics (EPIC-001/003/005/008/010/011/012/013) — full hit list used to produce the Cross-epic and Missing-references sections.
- Dangling-reference verification: every FEAT-XXX and STORY-XXX id cited in or from EPIC-009 was checked with `grep '^- id: FEAT-XXX\|^- id: STORY-XXX'` against the file. Where an id exists but the cited role does not match (e.g., FEAT-101 cited in place of FEAT-102), the item is classified as a misdirected reference rather than a missing definition.
