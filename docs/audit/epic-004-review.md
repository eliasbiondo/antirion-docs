# EPIC-004 Observability — requirements.yaml audit

Scope: `docs/requirements.yaml` lines 118–138 (EPIC-004), 614–778 (FEAT-029..FEAT-044), 5260–6848 (STORY-070..STORY-103), cross-referenced against project baselines (1–73), the models block (20712+), EPIC-009 alerts, EPIC-010 retention, EPIC-011 telemetry (FEAT-143) and EPIC-013 platform-operator surfaces.

Method: read-only review. No changes to `requirements.yaml`. Every finding cites the line(s) and quoted text; each includes Problem and Fix.

## Summary

- **Critical**: 5 findings — broken feature reference, 3 data-model mismatches that make features unimplementable as written, 1 baseline-policy gap (notifications audience for anomalies).
- **Major**: 10 findings — scope drift between feature description and stories, duplicate replay semantics, RBAC and audience gaps, EPIC-009 anomaly-to-alert linkage absent, mode-availability declarations missing.
- **Minor**: 8 findings — copy-paste `non_functional` drift, `data_models` lists that omit models actually used in AC text, minor terminology churn.
- **Cross-epic**: 4 findings — OTel span attributes in FEAT-143 omit `org_id`/`Request-Id` required by the baseline, FEAT-034 is not declared as a dependency by FEAT-029/030/032, FEAT-036 export has no FEAT-102 linkage, EPIC-013 platform-wide observability overlap is undeclared.
- **Missing / dangling references**: 3 findings — one dangling FEAT ID, two implied-but-undeclared dependencies.

---

## Critical

### C1. Broken feature reference: "FEAT-022 signals" in FEAT-041 description

- **Where**: line 749.
- **Quoted**: `description: Configure the anomaly detectors that drive FEAT-022 signals — list, set thresholds, enable/disable by category.`
- **Problem**: FEAT-022 is `Issue API keys` in EPIC-003 (line 553-class territory) — it does not emit "signals". The feature that produces anomaly signals is FEAT-033 `Anomaly signals` (line 666). This is a dangling cross-reference that makes the feature self-inconsistent: FEAT-041's stated purpose (configure the detectors that feed FEAT-033) is obscured.
- **Fix**: Replace `FEAT-022` with `FEAT-033` in line 749. Consider also citing FEAT-099 (alert rule management) if detector thresholds are intended to produce Alert rows.

### C2. No `AnomalyDetector` model backs FEAT-041

- **Where**: lines 746–754 (FEAT-041), 6637–6705 (STORY-095/096/097), 21574–21605 (Anomaly model).
- **Quoted (STORY-095 AC-001, line 6653)**: `I see each detector with category, enabled status, threshold summary and last_fired_at`.
- **Quoted (STORY-096 AC-001, line 6670-6674)**: `A detector "latency_spike" has threshold "p95 > 2s for 5m" ... I change to "p95 > 3s for 10m" and save`.
- **Problem**: STORY-095/096/097 configure **detectors** (category, threshold, enabled, last_fired_at), but the three stories list `data_models: - Anomaly` (lines 6655, 6677, 6701). The `Anomaly` model (21574–21605) has fields `severity, provider_id, team_id, title, description, spark, actions, detected_at, reviewed_at, reviewed_by_user_id` — it represents a single *fired* anomaly, not a *detector* configuration. No `category`, no `threshold_config`, no `enabled`, no `last_fired_at` field exists on any model in the file (verified: `grep AnomalyDetector` returns zero matches).
- **Fix**: Add an `AnomalyDetector` model with at least `id, org_id, category (cost_spike|latency_spike|error_spike|...), enabled, threshold_config (json), cooldown_seconds, last_fired_at`. Update STORY-095/096/097 `data_models` to reference it. Add `detector_id FK:AnomalyDetector` to the Anomaly model so a fired Anomaly can be traced to the configuration that produced it.

### C3. `SavedView` model lacks `scope` and `view_type` fields required by FEAT-030/FEAT-042 stories

- **Where**: lines 5632, 5651, 6722, 21552–21573 (SavedView model).
- **Quoted (STORY-075 AC-001, line 5632)**: `I click "Save view", enter name "Copilot errors", choose scope "personal", click Save`.
- **Quoted (STORY-075 AC-003, line 5651)**: `I save a view with scope "workspace"`.
- **Quoted (STORY-098 AC-001, line 6722)**: `A SavedView with view_type="analytics" is created`.
- **Problem**: The `SavedView` model (21552–21573) has fields `id, user_id, org_id, name, filters, starred, created_at`. It has no `scope` column (personal|workspace) and no `view_type` column (requests|analytics). Without these, the two distinct user journeys (request-log saved view with personal/workspace scope, analytics saved view) cannot be stored or differentiated. STORY-076 (line 5707) further asserts `scope "workspace" requires admin` — impossible to enforce without the field.
- **Fix**: Add `scope: string (personal|workspace)` and `view_type: string (requests|analytics)` to the SavedView model. Consider also `owner_team_id: FK:Team nullable` if team-scoped views are intended.

### C4. `Request` model cannot back FEAT-043 and FEAT-044 stories

- **Where**: lines 765–778 (FEAT-043/044), 6797–6848 (STORY-102/103), 21419–21517 (Request model).
- **Quoted (FEAT-043, line 767)**: `Top tools by invocation, failure rate and latency.`
- **Quoted (STORY-102 AC, line 6813)**: `I see top 20 tools with invocations, failure rate and p50/p95 latency`.
- **Quoted (STORY-103 AC-002, line 6843)**: `I see counts of client_cancelled and mid-stream drops over time`.
- **Problem**:
  - `Request.tools` is typed `int` (line 21485) — a count, not a list of tool names/ids. Aggregating "top tools by invocation" requires per-tool data (tool name, invocation outcome, per-tool latency). No model in the file records tool invocations.
  - `Request` has no `client_cancelled` bool and no `mid_stream_dropped` bool. STORY-103 expects counts of these. Line 15605 (STORY-347 area) separately claims `the request completes and is logged with client_cancelled=true` — which assumes a field that does not exist. Line 15595 also writes `status_label "client_cancelled"`, so the file is inconsistent with itself about whether cancellation is a boolean column or a `status_label` value.
- **Fix**:
  - Introduce a `ToolInvocation` model (or reuse one if hidden in EPIC-011 — none found) with `request_id FK:Request, tool_name, tool_id, input_tokens, output_tokens, latency_ms, status`. Rename `Request.tools` to `tool_count` for clarity.
  - Either add `Request.client_cancelled: bool` and `Request.mid_stream_dropped: bool`, or commit to `status_label` as the single source of truth and document the enum (`client_cancelled|mid_stream_drop|...`). Align STORY-103 and the EPIC-011 cancellation stories to whichever representation is chosen.

### C5. FEAT-033 anomaly signals ignore `project.notifications_model` audience policy

- **Where**: lines 37–38 (`notifications_model`), 666–674 (FEAT-033), 6141–6193 (STORY-085).
- **Quoted (baseline, line 38)**: `Cross-tenant signals (isolation breaches, abuse heuristics, sustained anomalies) always reach Antirion trust_and_safety in saas and are silently dropped in self_hosted because the set of tenants is 1.`
- **Quoted (STORY-085 AC-001, line 6157)**: `I see its description, affected provider/team, mini-spark, and suggested actions`.
- **Problem**: The baseline defines audience routing for sustained anomalies, but STORY-085 only describes UI review — it does not require the anomaly-detection workers to route `severity=crit` anomalies to any audience (tenant contacts in-workspace, trust_and_safety in saas, silently dropped in self_hosted). As a result, every acceptance criterion on FEAT-033 can pass while the baseline policy is violated. The story also does not record a resolved audience list on the Anomaly row.
- **Fix**: Add an AC to STORY-085 (or a new story under FEAT-033) requiring: (a) for sustained/`crit` anomalies the worker resolves the audience per `project.notifications_model` and writes it to the Anomaly (or to AuditLog); (b) the resolved audience list is visible in the drawer; (c) in `saas` mode the event is dispatched to the `trust_and_safety` sub-queue; (d) in `self_hosted` mode the event is silently dropped. Add `Anomaly.audience_snapshot: json` to the model.

---

## Major

### M1. FEAT-029 description promises an "embedded request log" that no story implements

- **Where**: line 617, stories 5260–5368.
- **Quoted (FEAT-029 description, line 617)**: `KPI strip, charts band, team/model/provider breakdowns, embedded request log.`
- **Problem**: STORY-070 and STORY-071 cover KPIs, charts, breakdowns, and drill-in navigation — but neither story surfaces an embedded request log on `/gateway`. The description overstates the scope.
- **Fix**: Either add a story "Embedded recent-requests panel on /gateway" (with row count, columns, and link to `/requests`) or remove `embedded request log` from the description so it aligns with STORY-070/071.

### M2. FEAT-031 description lists "tools" and "flags" drill-in — not covered by stories

- **Where**: line 644, stories 5764–5931.
- **Quoted**: `Drill into a single request with prompt, response, timing, tools, flags, cURL, replay.`
- **Problem**: STORY-078..081 cover prompt/response/timing/cURL/replay/cache/retry, but no AC surfaces a per-request tool invocation list or a flag rationale (pii_flag / safety_flag breakdown). STORY-078 only mentions "tools used" in the `given`, not in any `then`.
- **Fix**: Add (or extend STORY-078) ACs showing the tool-invocation list and the safety/pii flag reasons with links to SafetyEvent rows.

### M3. Duplicate/overlapping replay semantics across FEAT-031 and FEAT-037

- **Where**: lines 5824–5876 (STORY-079) vs. 6366–6435 (STORY-090); `/api/requests/:id/replay` is defined twice.
- **Quoted (STORY-079 api, line 5863–5870)**: `method: POST path: /api/requests/:id/replay response: { new_request: Request }`.
- **Quoted (STORY-090 api, line 6416–6430)**: `method: POST path: /api/requests/:id/replay request: { body: { model_id, params, prompt_override } } response: { request_id: string }`.
- **Problem**: Two stories under two different features define the same endpoint with two different request/response shapes. A reader cannot tell whether replay-unchanged (FEAT-031) and replay-with-mutation (FEAT-037) share the same endpoint or are distinct, and the response contract conflicts (`new_request: Request` vs `request_id: string`).
- **Fix**: Either (a) consolidate replay into FEAT-037 (treating the drawer button as a UI entry-point to the same endpoint) and delete the API spec from STORY-079, or (b) declare `POST /api/requests/:id/replay` the canonical endpoint with one response shape (pick one), and have STORY-079 link to STORY-090 for the contract. Decide once and remove the duplicate.

### M4. FEAT-036 CSV export has no RBAC gate and no notification linkage

- **Where**: 695–703 (FEAT-036), 6286–6365 (STORY-088/089).
- **Quoted (STORY-088 AC-002, line 6314)**: `A modal offers an async export ... I receive a download link by email/webhook when ready.`
- **Problem**: (a) No role/scope gate on export — anyone who can read the request log can export full prompt/response bodies, which may bypass the `RetentionConfig` redaction posture (cf. FEAT-113). Compare with FEAT-031 STORY-079's `requests.replay` scope, which is at least declared. (b) The async completion notification names `email/webhook` but does not reference FEAT-102 notification channels, and does not specify audience per `project.notifications_model` — the baseline requires every notification-bearing event name the audience.
- **Fix**: Add an AC requiring a `requests.export` scope (or equivalent) and declaring that exported bodies honor the viewer's effective PII-redaction policy. Add a second AC naming the delivery audience (acting principal a) and citing FEAT-102 as the delivery mechanism. Consider adding `AuditLog` to `data_models` for STORY-088 (the export is an exfiltration event worth auditing).

### M5. FEAT-035 global search — no RBAC/team-scope gate on prompt search

- **Where**: 685–693 (FEAT-035), 6244–6285 (STORY-087).
- **Quoted (STORY-087 AC-002, line 6266)**: `I search "invoice totals" ... /requests filters to rows whose prompt matches`.
- **Problem**: The AC does not constrain which requests the user is allowed to see. If a workspace uses team-scoped RBAC (FEAT-005), the search must exclude rows the caller cannot read. Also, there is no redaction rule for matching against `prompt_redacted` vs. `prompt` depending on viewer entitlement — a cross-team user could observe the existence of a sensitive prompt via search-result counts even if the body is redacted.
- **Fix**: Add an AC: "search results include only Request rows the caller can list in /requests per FEAT-005 roles and team membership; when a row is redacted for the caller, only the redacted body is matched and rendered."

### M6. FEAT-033 anomaly lifecycle does not integrate with EPIC-009 alerts

- **Where**: 666–674 (FEAT-033), 1329–1418 (EPIC-009 features).
- **Problem**: The epic description line 120 lists `anomaly signals` alongside the request log; EPIC-009's description (line 215) speaks of threshold-based alert rules but no story in either epic connects the two. An `Anomaly` row of `severity=crit` does not create an Alert/AlertEvent, does not flow through FEAT-100 lifecycle, and does not fan out via FEAT-102 channels. The hint in the task brief ("EPIC-009 alerts consume anomaly signals") is not realized in the document.
- **Fix**: Add a story under FEAT-033 (or FEAT-099): "Anomaly converts to Alert when a detector's severity threshold is met; the resulting AlertEvent inherits Anomaly.category, provider_id, team_id, spark; acknowledging the Alert marks the Anomaly reviewed." Include data_models `Anomaly, AlertEvent, AlertRule`.

### M7. FEAT-040 breakdown cannot be served from `MetricSeries` as modeled

- **Where**: 736–744 (FEAT-040), 6584–6636 (STORY-094), 21518–21551 (MetricSeries).
- **Quoted (FEAT-040, line 738-739)**: `Break spend down by model, team, project, key and environment with input/output/cache decomposition.`
- **Quoted (MetricSeries.scope, line 21530)**: `description: org|team|provider|model`.
- **Problem**: `MetricSeries.scope` enumerates only `org|team|provider|model`. FEAT-040 promises breakdowns by **project**, **key** and **environment** in addition; STORY-094 non_functional (line 6636) says `Query uses pre-aggregated MetricSeries when the range exceeds 7 days`. The aggregate does not exist for project/key/env, so a 30-day breakdown by project is not servable from MetricSeries as declared. Cost decomposition (input/output/cache) is also not a column on MetricSeries — only `spend` is.
- **Fix**: Extend `MetricSeries.scope` enum to `org|team|provider|model|project|api_key|env`, and add `spend_input, spend_output, spend_cache` columns (matching Request.input_cost/output_cost/cache_cost). Alternatively, commit to raw-log aggregation for these breakdowns and remove the 7-day MetricSeries claim in STORY-094.

### M8. FEAT-042 analytics saved-views duplicates FEAT-039 share-link semantics

- **Where**: 725–734 (FEAT-039), 755–764 (FEAT-042), 6551–6583 (STORY-093), 6728–6752 (STORY-099).
- **Quoted (STORY-093 AC-001, line 6567)**: `A ShareLink is created with resource_type "analytics_view" and resource_id set to the view`.
- **Quoted (STORY-099 AC-001, line 6746)**: `A ShareLink with resource_type="analytics_view" is created`.
- **Problem**: STORY-093 (under FEAT-039) and STORY-099 (under FEAT-042) describe the same user journey and produce the same ShareLink shape. They disagree on scope (FEAT-039 is the canonical share-link feature; FEAT-042 replicates it). No AC differentiates what STORY-099 does that STORY-093 does not.
- **Fix**: Delete STORY-099 (or reduce it to a pointer: "FEAT-042 re-uses FEAT-039's share-link flow for view_type=analytics — see STORY-093"). Leaving both stories creates ambiguous ownership and will lead to two implementations.

### M9. FEAT-029..FEAT-044 do not declare `mode:` — baseline requires this for features that differ by mode

- **Where**: 614–778, baseline line 36.
- **Quoted (baseline, line 36)**: `Every feature that differs in scope, availability or data shape between the two modes declares its mode availability explicitly in its description.`
- **Problem**: EPIC-013 features consistently declare `mode: both|saas|self_hosted` (e.g. line 2013, 2024, 2033, 2063, 2093). EPIC-004's features do not. Most EPIC-004 surfaces are tenant-scoped and available in both modes — but FEAT-029's dashboard, FEAT-032's analytics and FEAT-033's anomaly signals overlap with EPIC-013's FEAT-170/172/176 platform-wide views. A reader cannot tell from EPIC-004 whether "overview dashboard" means per-tenant only (the intent) or platform-wide (the EPIC-013 view). Worse, the saas-vs-self_hosted data shape differs (FEAT-033 dropping cross-tenant signals in self_hosted per the notifications_model policy) but no feature declares it.
- **Fix**: Add `mode: both` to each of FEAT-029..FEAT-044 and add a clarifying sentence that they are tenant-scoped and that the platform-wide equivalents live in EPIC-013. For FEAT-033 explicitly state the saas-vs-self_hosted difference for `severity=crit` / sustained signals (see C5).

### M10. STORY-085 review flow uses a field that does not exist on the `Anomaly` model

- **Where**: 6158–6165 (STORY-085 AC-002), 21574–21605 (Anomaly).
- **Quoted (AC-002, line 6165)**: `The anomaly's review status becomes "reviewed" with my user as the reviewer.`
- **Problem**: The model exposes `reviewed_at` + `reviewed_by_user_id` (nullable) — "reviewed" is implicit when those are set. There is no `review_status` string enum. The phrasing hints at an intended enum (e.g. open|reviewed|suppressed) but none exists. The endpoint `POST /api/anomalies/:id/review` (line 6181) also does not describe the state machine.
- **Fix**: Either rewrite the AC in terms of the actual fields ("`reviewed_at` is set to now() and `reviewed_by_user_id` is set to my user id") or add `Anomaly.review_status: string (open|reviewed|suppressed)` and a `suppress_until: timestamp nullable`, and re-draft AC-002 against the enum.

---

## Minor

### m1. `non_functional` copy-paste drift — FEAT-030/031/032/033/036/042 inherit lines that do not apply

- **Where**: 5536-5538, 5613-5615, 5729-5731, 5761-5763, 5821-5823, 5874-5876, 5905-5907, 5929-5931, 6046-6049, 6083-6086, 6137-6140, 6191-6193, 6240-6243, 6331-6333, 6362-6365, 6490-6492, 6549-6550, 6581-6583, 6656-6658, 6679-6681, 6703-6705, 6725-6727, 6750-6752, 6772-6774, 6794-6796, 6815-6818, 6845-6848.
- **Quoted (recurring, e.g. line 5538)**: `Full-text search on prompt handled by a dedicated index (e.g. Postgres tsvector or an OpenSearch cluster)` appears under STORY-073/074/076 (FEAT-030 saved-view delete), where full-text prompt search is not invoked.
- **Quoted (recurring)**: `Anomaly scoring runs in the worker fleet; the UI reads the latest cached score` appears under STORY-082/083/084 (FEAT-032 analytics spend/heatmap/cache-impact), which have nothing to do with anomaly scoring.
- **Quoted (line 6243)**: `Export generation runs as an async worker job with a 24h SLO and a visible failure state` appears under STORY-086 (FEAT-034 time-range selector) — the time-range picker does not generate exports.
- **Problem**: The repeated phrases inflate each story's NFR surface and blur ownership: reviewers will interpret them as applicable constraints when they are not.
- **Fix**: Prune each `non_functional` block to the constraints that actually apply to that story. Centralize truly cross-cutting NFRs in the baseline (they already are) and drop them from per-story lists.

### m2. STORY-072 request-log filters are missing `api_key_id` and `user_id`

- **Where**: 5439-5468, 21443 (Request.api_key_id), 21437 (Request.user_id).
- **Quoted (query filters, line 5443–5468)**: `provider, team, model, env, status_class, tag, cached, streamed, flagged, min_latency, max_latency, min_cost, max_cost, q`.
- **Problem**: `api_key_id` and `user_id` exist on Request but cannot be filtered; FEAT-040 (cost breakdown by key) relies on key-level slicing and the detail drawer shows `user` and `api_key_id`, so users will expect to filter the log by them.
- **Fix**: Add `api_key_id: string[], user_id: string[]` to the `/api/requests` query filters and to the filter rail.

### m3. STORY-074 shortcut `e` references a story "(see STORY for CSV export)" without an explicit id

- **Where**: line 5600.
- **Quoted**: `The CSV export flow starts for the current filtered view (see STORY for CSV export)`.
- **Problem**: The reference is un-numbered and will rot. The intended story is STORY-088.
- **Fix**: Replace `(see STORY for CSV export)` with `(see STORY-088)`.

### m4. `ShareLink.revoked` audit event missing from STORY-092 `data_models`

- **Where**: 6519–6520, 6545–6548.
- **Quoted (AC-002, line 6520)**: `An AuditLog entry with action "share_link.revoked" is written.`
- **Problem**: The AC writes an AuditLog row but `data_models: [ShareLink, SavedView, Request]` (line 6545–6548) omits `AuditLog`.
- **Fix**: Add `AuditLog` to the `data_models` list.

### m5. STORY-093 does not declare a `POST /api/share-links` (relies on STORY-092)

- **Where**: 6551–6583.
- **Problem**: STORY-093 has no `api:` block, which is usually fine if the endpoint is shared — but readers of this story in isolation cannot tell. The `non_functional` block also omits the signed-token constraint from STORY-092 (`Tokens are signed with a rotating key; only the hash is stored`).
- **Fix**: Add `depends_on: [STORY-092]` and carry the signed-token NFR.

### m6. Anomaly detector enable/disable (STORY-097) writes AuditLog but does not expose an API

- **Where**: 6682–6705.
- **Problem**: STORY-097 has no `api:` block. STORY-096 also lacks one. Without an endpoint, the "save" behavior is undefined and the AuditLog entry has no origin.
- **Fix**: Define `PATCH /api/anomaly-detectors/:id { enabled: bool, threshold_config: json }` in STORY-096/097 and tie it to the future AnomalyDetector model (C2).

### m7. STORY-094 breakdown ACs demonstrate only two of the five promised dimensions

- **Where**: 6594–6609.
- **Quoted (FEAT-040, line 739)**: `Break spend down by model, team, project, key and environment`.
- **Quoted (STORY-094 AC-001, line 6598)**: `I select "Breakdown" and group by Model and Team for the current month`.
- **Problem**: The AC exercises only `model` and `team`. `project`, `key`, `env` are promised in the feature description but never asserted. A reader cannot tell if they are in scope for FEAT-040 or deferred.
- **Fix**: Either add ACs exercising the remaining three group-bys or tighten the feature description to "model and team".

### m8. Anomaly detection retention policy unspecified; RetentionConfig does not name "anomaly"

- **Where**: 22441–22456 (RetentionConfig), 21574–21605 (Anomaly), baseline line 30 (ClickHouse 99.99% ingestion).
- **Problem**: RetentionConfig classes are `request_body_days, response_body_days, metadata_days`. The `Anomaly` table is not bound by an explicit retention class; EPIC-004 stories do not declare an anomaly retention window. If anomalies live in Postgres indefinitely, `reviewed_at` triage queues will grow unbounded.
- **Fix**: Add an `anomalies_days` field to RetentionConfig and a retention sweep in the worker fleet for anomalies older than N days in `reviewed` state. Cross-reference FEAT-113.

---

## Cross-epic

### X1. FEAT-143 STORY-338 OTel span omits `org_id` and `Request-Id` — contradicts baseline

- **Where**: baseline line 32, STORY-338 line 16518.
- **Quoted (baseline, line 32)**: `Every request, job and background task emits an OpenTelemetry span with Request-Id, org_id, team_id, user_id, model and provider.`
- **Quoted (STORY-338 AC-001, line 16518)**: `A span "antirion.gateway.request" is exported with attributes model, provider, team, user, api_key_id, cost, input_tokens, output_tokens, latency_ms, ttft_ms`.
- **Problem**: `Request-Id` is implicit in `trace_id/span_id` but not enumerated as an attribute. `org_id` is not listed at all. EPIC-004 (request-log drill-in, analytics pre-aggregates, anomaly scoping) depends on `org_id` being present on every span/log/metric so tenant-scoped queries stay honest under the `project.tenant_isolation` baseline. The Prometheus label set at line 16570 also omits `org_id` — which is defensible on cardinality grounds only if the baseline is amended.
- **Fix**: Add `org_id` and `request_id` to STORY-338 AC-001 attributes. Decide explicitly whether Prometheus labels include `org_id` (baseline compatible, high cardinality) or scope per-org metrics via workspace-separated scrape jobs.

### X2. FEAT-034 Time-range selector is the shared range control but is not declared as a dependency by FEAT-029/030/032

- **Where**: 675–684 (FEAT-034), STORY-070, STORY-072, STORY-082.
- **Problem**: STORY-086 AC-001 (line 6203) states `I am on /gateway with default 6h range ... All charts and tables on the page recompute for the 24h window`. FEAT-029/030/032 stories assume the same range control but do not list STORY-086 in `depends_on`. Implementation teams could build per-page pickers and diverge.
- **Fix**: Add `depends_on: [STORY-086]` to STORY-070, STORY-072, STORY-082 (and STORY-094 breakdown).

### X3. FEAT-036 async export completion flow bypasses FEAT-102 notification channels

- **Where**: 6314 (STORY-088 AC-002), 1363–1372 (FEAT-102).
- **Problem**: The export completion message is described as `email/webhook` ad-hoc, rather than riding FEAT-102's notification-channels routing. This leaves the audience (acting principal vs owner) and per-user channel preferences unwired.
- **Fix**: Re-spec STORY-088 AC-002 to deliver via FEAT-102 with audience = acting principal (user_id) and channel = user's configured preference.

### X4. EPIC-004 overlap with EPIC-013 platform-wide views is undeclared

- **Where**: EPIC-004 epic description (line 120), FEAT-170/172/176 (2009–2077), baseline line 36.
- **Problem**: FEAT-170 (cluster/fleet health), FEAT-172 (tenant roster) and FEAT-176 (platform abuse signals) surface observability across tenants for the platform operator. EPIC-004 never states that its dashboards are tenant-scoped and that cross-tenant rollups live in EPIC-013. In saas mode this risks leaking a tenant dashboard to Antirion staff via a shared endpoint; in self_hosted it risks duplicating work.
- **Fix**: Add a line to EPIC-004's description: "All surfaces in this epic are tenant-scoped. The platform-wide analogues (cluster/fleet health, cross-tenant abuse signals, platform release rollups) live in EPIC-013 and are visible only to the platform operator." Apply the M9 `mode:` markers.

---

## Missing / dangling references

### R1. Dangling: `FEAT-022 signals` in FEAT-041 description

- **Citing line**: 749.
- **Missing id**: `FEAT-022` refers to a real feature (`Issue API keys`, EPIC-003) but the cited semantic ("signals") does not apply to it — a dangling cross-reference by meaning, not by id.
- **Fix**: see C1 — change to `FEAT-033`.

### R2. Missing (implied) dependency on FEAT-143 `Request telemetry`

- **Citing**: EPIC-004 epic description line 120 `Overview dashboard, request log, analytics, anomaly signals, search and export`. Every one of these features reads data produced by FEAT-143 (spans, metrics, structured logs) and by the request-ingestion worker (baseline line 18 `request-log ingestion`). FEAT-143 is never named by FEAT-029..044 nor in their stories.
- **Missing link**: FEAT-143 is the producer of the data EPIC-004 consumes. A dependency is implied but undeclared.
- **Fix**: Add a note to the EPIC-004 description citing FEAT-143 as the telemetry producer and the request-log ingestion worker as the durability owner (baseline data_durability, line 30).

### R3. Missing feature: no `AnomalyDetector` definition to back FEAT-041

- **Citing**: FEAT-041 description (line 749) and STORY-095/096/097 which require per-detector threshold/category/enabled state.
- **Missing**: No `AnomalyDetector` model is declared anywhere in the file (verified: the string `AnomalyDetector` has zero matches). FEAT-041 has no backing entity.
- **Fix**: see C2 — add the model and wire STORY-095..097 to it.

### R4. Missing (implied) cross-reference from FEAT-033 to FEAT-099 / FEAT-100 / FEAT-102

- **Citing**: FEAT-033 description line 668 `Auto-detected anomalies with severity, context, and contextual actions`; baseline line 38 (notifications_model routes sustained anomalies).
- **Missing link**: No story in FEAT-033 references FEAT-099 (alert rule), FEAT-100 (alert lifecycle) or FEAT-102 (notification channels). See M6 and C5.
- **Fix**: Add ACs that name the downstream features explicitly.

### R5. Missing FEAT scope promised by EPIC-004 description

- **Citing**: EPIC-004 description line 120 lists six scopes: `Overview dashboard, request log, analytics, anomaly signals, search and export`. The epic's actual feature list (FEAT-029..FEAT-044) covers these and **eight additional** areas (replay, compare, share links, cost breakdown, detector config, analytics saved views, tool-use analytics, streaming analytics).
- **Problem**: The description is too narrow; a reader scanning only the epic line will miss half the scope.
- **Fix**: Expand line 120 to `Overview dashboard, request log, request detail, analytics, anomaly signals and detector configuration, search and export, replay and comparison, share links, cost breakdown, saved views, tool-use and streaming views.`

---

## Appendix: inventory verified

- EPIC-004 feature count: 16 (FEAT-029 through FEAT-044) — matches `features:` list at lines 122–138.
- STORY count: 34 (STORY-070 through STORY-103) — all defined, no gaps.
- Feature→epic mapping for FEAT-029..FEAT-044 — all correctly set `epic: EPIC-004`.
- Story→feature mapping for STORY-070..STORY-103 — all `feature:` values present in the feature list.
- Models referenced in EPIC-004 stories: `Request, MetricSeries, SavedView, Anomaly, SafetyEvent, CacheEntry, ShareLink, Team, Provider, Model, AuditLog, User` — all present in the models block except the implied-missing `AnomalyDetector` (C2) and per-tool-invocation entity (C4).
