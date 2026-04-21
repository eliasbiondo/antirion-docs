# Deferred Follow-ups

Items surfaced during the EPIC-001..013 audit pass that were not applied to `docs/requirements.yaml` because they require product input, propose net-new features, or conflict with other findings.

Each entry: brief description, source audit citation, reason deferred.

## Items

### EPIC-001

- **m-4 STORY-003 "Forgot?" component naming** — audit wants a named screen/component for the Forgot-password link on the Login screen. Needs design input to confirm the component tree. (docs/audit/epic-001-review.md §m-4)
- **m-6 STORY-012 role-change notification audience** — audit suggests notifying actor + target + Org.security_contact on role changes. Needs product input on canonical audience list for role-change events. (docs/audit/epic-001-review.md §m-6)
- **m-8 STORY-018 typed confirmation on offboard** — audit suggests either adding "offboard user" to destructive_action_confirmation_policy or requiring email-typed confirmation. Needs product policy decision. (docs/audit/epic-001-review.md §m-8)
- **m-11 FEAT-010 priority vs FEAT-003** — audit flags that SSO SLO at P1 undermines FEAT-003 sign-out-everywhere at P0 when Org.sso_enforced=true. Priority tradeoff needs product input. (docs/audit/epic-001-review.md §m-11)
- **X-2 STORY-020 cross-epic reference to FEAT-015** — audit suggests adding a `related_features` list; no such field in the current schema. Needs cross-epic linkage convention. (docs/audit/epic-001-review.md §X-2)
- **X-3 STORY-018/019 cross-epic references to EPIC-003** — same issue as X-2. (docs/audit/epic-001-review.md §X-3)

### EPIC-002

- **C-4 FEAT-021/STORY-048 duplication of FEAT-003/STORY-006** — audit recommends collapsing FEAT-021 into FEAT-003 and moving STORY-048 list AC into STORY-006. Partial fix applied (depends_on added); full collapse requires product decision on feature ownership. (docs/audit/epic-002-review.md §C-4)
- **m-8 STORY-043 quiet-hours semantics** — single global user-level setting vs per-event overrides. Model and API disagree; needs product input. (docs/audit/epic-002-review.md §m-8)
- **(b)3 STORY-043 → FEAT-102 dependency** — canonical channel routing link not declarable without cross-epic reference field. (docs/audit/epic-002-review.md §(b)3)
- **(b)4/5 STORY-044 → FEAT-102 / FEAT-167 / FEAT-179 dependencies** — same linkage convention gap. (docs/audit/epic-002-review.md §(b)4-5)
- **(c)2 FEAT-015 trusted-browser list & individual revoke** — audit suggests a new story or AC to list/revoke TrustedBrowser rows individually. Needs product input. (docs/audit/epic-002-review.md §(c)2)

### EPIC-003

- **m7 Approval.kind shared between FEAT-027 and FEAT-160** — audit wants a separate Approval.kind for break-glass key creation vs elevated-scope grant. Belongs in the EPIC-011 pass. (docs/audit/epic-003-review.md §m7)
- **X1 FEAT-133 BYOK data class enumeration** — add BYOK credential ciphertext as a CMK-wrappable data class in FEAT-133. Deferred to EPIC-010 pass. (docs/audit/epic-003-review.md §X1)
- **(c) BYOK rotation policy edit story** — `rotate_policy_days` observable but not editable; needs a new story under FEAT-025. Product input required. (docs/audit/epic-003-review.md §(c))

### EPIC-004

- **C1 conflict FEAT-041 citation** — EPIC-003 audit proposed FEAT-024; EPIC-004 audit proposed FEAT-033. Applied later (more specific) fix to FEAT-033. Flagging in case reviewers disagree. (docs/audit/epic-003-review.md §C4 + docs/audit/epic-004-review.md §C1)
- **M2 FEAT-031 tools/flags drill-in** — add ACs surfacing per-request tool invocation list and safety/pii flag rationale. Needs product input on drawer UI. (docs/audit/epic-004-review.md §M2)
- **M6 FEAT-033 to EPIC-009 alerts integration** — add a story bridging Anomaly → Alert / AlertEvent. Needs product input. (docs/audit/epic-004-review.md §M6)
- **m1 non_functional copy-paste drift** — broad editorial pass to prune per-story NFR lists that inherit inapplicable constraints. Deferred; out of scope for the targeted-fix round. (docs/audit/epic-004-review.md §m1)

### EPIC-005

- **C3 mid-stream retry semantics contradiction** — baseline says "retry the remaining prefix"; FEAT-139 STORY-327 AC-002 says "do not retry mid-stream". Needs product input. (docs/audit/epic-005-review.md §C3)
- **C8 RoutingRule structured sub-schemas** — retry/canary/shadow/circuit still JSON blobs; audit proposes named sub-schemas. Structural change; needs product input. (docs/audit/epic-005-review.md §C8)
- **M1 canary evaluation windows** — three windows (5m/15m/60m) across stories; audit proposes distinct named fields. Needs product input. (docs/audit/epic-005-review.md §M1)
- **M2 missing strategy stories** — single, weighted, failover, least-loaded each lack a selection-semantics story. (docs/audit/epic-005-review.md §M2)
- **M4 CatalogPolicy ↔ RoutingRule precedence** — overlapping retry/fallback policies with no merge rule. Needs product input. (docs/audit/epic-005-review.md §M4)
- **M5 ModelAlias.fallback vs RoutingRule.fallback** — naming collision; needs product input. (docs/audit/epic-005-review.md §M5)
- **M7 canary auto-promote chain mutation** — promote silently rewrites fallback chain; needs UX decision. (docs/audit/epic-005-review.md §M7)
- **M10 cross-epic cache/safety interactions for canary/shadow** — unaddressed. (docs/audit/epic-005-review.md §M10)
- **M11 catalog-sync feature** — no automated sync from upstream provider catalogs today. New feature. (docs/audit/epic-005-review.md §M11)

### EPIC-006

- **C-6 streaming × cache** — write/hit semantics for SSE/chunked responses unspecified; new story required. (docs/audit/epic-006-review.md §C-6)
- **C-7 redaction/cache coherence** — cache key vs redacted prompt policy; SafetyEvent.action suppression rules. Needs product input. (docs/audit/epic-006-review.md §C-7)
- **M-10 cache scope enumeration** — define cache.read/invalidate/admin scopes. Needs product input. (docs/audit/epic-006-review.md §M-10)
- **M-12 eviction under write burst** — pick defined behavior when burst exceeds max_size_mb within 60s protection window. Needs product input. (docs/audit/epic-006-review.md §M-12)
- **X-3 redaction/blocks × cache writes** — cross-epic (EPIC-007). (docs/audit/epic-006-review.md §X-3)
- **X-4 cache hits × budget counters** — should cache hits still decrement budget? Needs product input. (docs/audit/epic-006-review.md §X-4)
- **X-6 graceful degradation backend choice** — FEAT-148 needs specified cache backend for degraded reads. (docs/audit/epic-006-review.md §X-6)
- **R-1/R-2/R-5/R-7 missing cache stories** — template-update/nightly-refresh/break-glass/prompt-segment-CRUD/STORY-145 savings report/per-team purge. Needs product input. (docs/audit/epic-006-review.md §R-1..R-7)
- **R-6 invalidation event catalog** — InvalidationRule.match has no authoritative event list. Needs product input. (docs/audit/epic-006-review.md §R-6)

### EPIC-007

- **M-2/M-3 action precedence and override matrix** — need product decision on block/redact/flag/allow ordering and override transitions. (docs/audit/epic-007-review.md §M-2, §M-3)
- **M-6 mode declarations** — add mode:both to all EPIC-007 features (editorial sweep). (docs/audit/epic-007-review.md §M-6)
- **M-8 cross-tenant abuse signal** — new feature/story needed for trust_and_safety aggregation. (docs/audit/epic-007-review.md §M-8)
- **M-9 ApproverDelegation model** — STORY-178 OOO/delegate has no backing model. (docs/audit/epic-007-review.md §M-9)
- **M-10 STORY-183 live flow RBAC/residency** — needs product input on operator visibility. (docs/audit/epic-007-review.md §M-10)
- **X-1..X-6 cross-epic interactions** — safety-rule-driven cache invalidation, semantic-cache coherence, pipeline ordering, residency × unredact — all need product input. (docs/audit/epic-007-review.md §X-1..X-6)
- **MR-1..MR-3 missing features/models** — pipeline ordering feature, cross-tenant abuse correlation, approver delegation. (docs/audit/epic-007-review.md §MR-1..MR-3)

### EPIC-008

- **M1 BudgetPolicy threshold overload** — split `approval_threshold_pct` into edit/waiver variants. Needs product input. (docs/audit/epic-008-review.md §M1)
- **M3 budget signals via AlertRule** — route soft-threshold alerts through managed AlertRule instead of direct AlertEvent writes. Needs product input. (docs/audit/epic-008-review.md §M3)
- **M4 FEAT-091 overage vs soft-alert surfaces** — pick one canonical emitter; reduces duplicate notifications. (docs/audit/epic-008-review.md §M4)
- **M8 budgets API path canonicalisation** — `/api/budgets/:id` vs `/api/budgets/teams/:id/...`. Structural API decision. (docs/audit/epic-008-review.md §M8)
- **M11 Budget.spent pipeline story** — specify Request→Budget counter reconciliation. Needs new story under FEAT-086. (docs/audit/epic-008-review.md §M11)
- **M12 BudgetForecast model** — move projected/runs_out_on off Budget; define trend and worker cadence. Needs product input. (docs/audit/epic-008-review.md §M12)
- **minor drift items (m1, m3, m4, m5, m7, m8, m9, m10, m11)** — boilerplate NFRs, typed-confirmation policy, audit of FX override magnitude, UserBudget.outlier definition, project owner join table, STORY-208 asymmetry, FEAT-097 mode branching, waiver cycle expiry, approval queue cleanup worker. (docs/audit/epic-008-review.md §m1..m11)

### EPIC-009

- **C1/C2 audience-driven notifications refactor** — structural change to AlertRule.channels and STORY-232 to adopt notifications_model roles. Needs product input. (docs/audit/epic-009-review.md §C1, §C2)
- **M2 FEAT-100 vs FEAT-103 overlap** — redraw feature boundaries. Needs product decision. (docs/audit/epic-009-review.md §M2)
- **M5 error-budget release gate** — tie error-budget burn to release promotion. Needs new story. (docs/audit/epic-009-review.md §M5)
- **M8 in-app inbox channel** — add in-app to FEAT-102 channels. Needs product input. (docs/audit/epic-009-review.md §M8)
- **M10 PagerDuty availability gating** — fallback when integration unreachable (air-gapped). Needs product input. (docs/audit/epic-009-review.md §M10)
- **X5 Anomaly → AlertEvent linkage** — connect cross-epic. Needs product input. (docs/audit/epic-009-review.md §X5)
- **X6 ingestion-health alert** — add concrete story. (docs/audit/epic-009-review.md §X6)
- **X7 tenant-internal vs public incident publication** — addressed by C5 model split; FEAT-173 publication flow still needs an explicit story. (docs/audit/epic-009-review.md §X7)
- **minor editorial (m1..m10)** — multiple small issues. (docs/audit/epic-009-review.md §m1..m10)

### EPIC-010

- **C-4 FEAT-133 revocation semantics** — reconcile saas fallback vs self_hosted fail-closed across the feature description and STORY-308/309/310 NFRs. Needs product input. (docs/audit/epic-010-review.md §C-4)
- **M-1 FEAT-107 identity vs billing mode split** — split into an identity feature (both modes) and a saas-only billing half. Needs product decision. (docs/audit/epic-010-review.md §M-1)
- **M-3 dual IP allowlist storage** — consolidate onto OrgIpAllowlist + /api/org/ip-allowlist. Structural. (docs/audit/epic-010-review.md §M-3)
- **M-4 FEAT-127 DR role gating** — saas vs self_hosted execute-restore vs request-restore. Needs product input. (docs/audit/epic-010-review.md §M-4)
- **M-7 GeoIP default behavior** — flip default to fail-closed. Needs product input. (docs/audit/epic-010-review.md §M-7)
- **Minor m-1..m-9 editorial** — SCIM NFR misapplication, FEAT-131 GeoPolicy model, FEAT-132 DlpExportConfig, ResidencyConfig.dpo_contact consolidation, SsoConfig.signed_users, /api/v1 versioning consistency, SSO-enforced invite race, AuditSink.credentials encryption, webhook signature replay-window wording. (docs/audit/epic-010-review.md §m-1..m-9)
- **X-1..X-7 cross-epic** — FEAT-107 vs FEAT-095/096/098, FEAT-127 vs FEAT-170, delete-org vs install lifecycle, FEAT-133 CMK data classes for BYOK, FEAT-113 PII toggle vs FEAT-070, STORY-280 audit-sink audience. Mostly product input. (docs/audit/epic-010-review.md §X-1..X-7)

### EPIC-011

- **M1 failover/circuit-breaker ownership split between EPIC-005 and EPIC-011** — declare which feature owns config vs runtime vs state machine. Needs product decision. (docs/audit/epic-011-review.md §M1)
- **M2 canonical pipeline ordering feature** — no feature describes where safety/cache/budget/retry/translation sit on the hot path. Needs new feature. (docs/audit/epic-011-review.md §M2)
- **M3 FEAT-160 break-glass belongs in EPIC-003** — structural move; FEAT-027 already has the Approval pattern. Needs product input. (docs/audit/epic-011-review.md §M3)
- **M4 provider API surface split** — Files/Batches/Audio/Image/Moderation/Embeddings/Fine-tune don't belong in the pipeline epic. Needs epic reshuffle. (docs/audit/epic-011-review.md §M4)
- **M9 STORY-323 rejection metadata contract** — pick Request row with nulls vs separate AccessLog. Needs product input. (docs/audit/epic-011-review.md §M9)
- **M11 FEAT-143 vs FEAT-149 sampling overlap** — choose owner for TelemetryConfig. Needs product decision. (docs/audit/epic-011-review.md §M11)
- **X2..X7** — cross-epic coordination (shared-credentials toggle, cache/safety/budget pipeline positions, telemetry cross-link, per-tenant concurrency cap). (docs/audit/epic-011-review.md §X2..X7)
- **Minor editorial (m1..m12)** — boilerplate NFRs, skeletal Files/Batches stories, minor wording. (docs/audit/epic-011-review.md §m1..m12)

### EPIC-012

- **C5 FEAT-167 vs FEAT-170 overlap** — worker fleet observability split between EPIC-012 (tenant) and EPIC-013 (platform) needs structural decision. (docs/audit/epic-012-review.md §C5)
- **M6 STORY-391/392 mode-specific ACs** — self_hosted status page host, widget routing. Needs product input. (docs/audit/epic-012-review.md §M6)
- **M7 STORY-396 mode split** — ToS versioning saas (Antirion legal) vs self_hosted (platform admin upload). Needs product input. (docs/audit/epic-012-review.md §M7)
- **M9 FEAT-166 air-gapped ACs** — bundled catalog, docs phone-home, URL degradation. Needs new stories. (docs/audit/epic-012-review.md §M9)
- **M10/M11 STORY-401 pricing calculator mode branching** — plan-fee / license lines in saas vs self_hosted. Needs product input. (docs/audit/epic-012-review.md §M10/M11)
- **m1..m8 minor editorial** — various. (docs/audit/epic-012-review.md §m1..m8)
- **X1..X3 cross-epic** — FEAT-168 vs FEAT-085 forecast scopes, FEAT-164 saas sub-queue routing, invitee first-run boundary. (docs/audit/epic-012-review.md §X1..X3)

