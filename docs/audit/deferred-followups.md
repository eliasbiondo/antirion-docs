# Deferred Follow-ups

Items surfaced during the EPIC-001..013 audit pass that were not applied to `docs/requirements.yaml` because they require product input, propose net-new features, or conflict with other findings.

Each entry: brief description, source audit citation, reason deferred.

## Items

### EPIC-001 (2026-04-20 re-audit)

- **M-6 STORY-018 offboarding typed confirmation** — re-audit still proposes typed-email confirmation on offboard, or a non_functional stating it is intentionally click-confirm. Needs product policy decision. (docs/audit/epic-001-review-2026-04-20.md §M-6)
- **U-1 SessionPolicy admin-edit surface** — no feature exposes write path for per-Org SessionPolicy (idle/absolute/lockout fields). Warrants a new FEAT in EPIC-001 or EPIC-010. (docs/audit/epic-001-review-2026-04-20.md §U-1)
- **U-2 Session idle/absolute enforcement** — SessionPolicy.idle_timeout_minutes and absolute_max_hours have no enforcer story. Add under FEAT-003 or sibling feature. (docs/audit/epic-001-review-2026-04-20.md §U-2)
- **U-3 Transactional email delivery** — invite/reset emails have no owning feature; provider/templates/retry/bounces unspecified. (docs/audit/epic-001-review-2026-04-20.md §U-3)
- **U-4 TrustedBrowser list/revoke** — no user-facing list/revoke; no cascade from password change / MFA reset / admin session revocation. (docs/audit/epic-001-review-2026-04-20.md §U-4)
- **U-5 platform_admin seeding path (self_hosted)** — no feature seeds first platform_admin on install or manages subsequent grants. Belongs to FEAT-012 or FEAT-177. (docs/audit/epic-001-review-2026-04-20.md §U-5)
- **U-7 LoginAttempt retention/sweep** — no retention policy + sweep worker; RetentionConfig.login_attempts_days missing. (docs/audit/epic-001-review-2026-04-20.md §U-7)
- **U-8 User.status = "inactive" lifecycle** — no writer or reader; either extend FEAT-007/008 with dormancy sweep or drop the enum value. (docs/audit/epic-001-review-2026-04-20.md §U-8)

### EPIC-001

- **m-4 STORY-003 "Forgot?" component naming** — audit wants a named screen/component for the Forgot-password link on the Login screen. Needs design input to confirm the component tree. (docs/audit/epic-001-review.md §m-4)
- **m-6 STORY-012 role-change notification audience** — audit suggests notifying actor + target + Org.security_contact on role changes. Needs product input on canonical audience list for role-change events. (docs/audit/epic-001-review.md §m-6)
- **m-8 STORY-018 typed confirmation on offboard** — audit suggests either adding "offboard user" to destructive_action_confirmation_policy or requiring email-typed confirmation. Needs product policy decision. (docs/audit/epic-001-review.md §m-8)
- **m-11 FEAT-010 priority vs FEAT-003** — audit flags that SSO SLO at P1 undermines FEAT-003 sign-out-everywhere at P0 when Org.sso_enforced=true. Priority tradeoff needs product input. (docs/audit/epic-001-review.md §m-11)
- **X-2 STORY-020 cross-epic reference to FEAT-015** — audit suggests adding a `related_features` list; no such field in the current schema. Needs cross-epic linkage convention. (docs/audit/epic-001-review.md §X-2)
- **X-3 STORY-018/019 cross-epic references to EPIC-003** — same issue as X-2. (docs/audit/epic-001-review.md §X-3)

### EPIC-002 (2026-04-20 re-audit)

- **C-3 FEAT-021 collapse into FEAT-003** — still open. Re-audit restates the collapse proposal; partial fix (depends_on) already landed. (docs/audit/epic-002-review-2026-04-20.md §C-3)
- **M-7 STORY-043 quiet-hours semantics** — global vs per-event row shape contradiction unchanged. (docs/audit/epic-002-review-2026-04-20.md §M-7)
- **M-8 FEAT-015 trusted-browser list/revoke** — still no list/revoke-by-id story under FEAT-015. (docs/audit/epic-002-review-2026-04-20.md §M-8)
- **X-3 STORY-044 FEAT-167 / FEAT-179 dependencies** — needs canonical cross-epic reference convention. (docs/audit/epic-002-review-2026-04-20.md §X-3)
- **U-1 Account-deletion cutover worker** — no feature transitions AccountDeletionRequest pending → completed at scheduled_for. (docs/audit/epic-002-review-2026-04-20.md §U-1)
- **U-2 Recovery-code consumption at sign-in** — no story consumes RecoveryCode.consumed_at on sign-in; codes are write-only. (docs/audit/epic-002-review-2026-04-20.md §U-2)
- **U-3 PersonalToken.last_used_at write path** — display-only; no auth-pipeline writer specified. (docs/audit/epic-002-review-2026-04-20.md §U-3)
- **U-4 MFA primary-factor toggle** — no story toggles MfaFactor.is_primary or enforces the "exactly one primary" invariant. (docs/audit/epic-002-review-2026-04-20.md §U-4)
- **U-5 Avatar image lifecycle** — bytes/content-type limits, replace-cleanup and removal path unspecified; 413 error code has no policy. (docs/audit/epic-002-review-2026-04-20.md §U-5)
- **U-6 UserPrefs row seeding** — no feature or AC creates UserPrefs with defaults; UI baseline reads may NPE. (docs/audit/epic-002-review-2026-04-20.md §U-6)
- **U-7 Account-deletion cascade for user-owned resources** — ApiKey/Team.lead/AlertRule/Webhook/PromptTemplate cascade/reassignment rules at cutover unspecified. (docs/audit/epic-002-review-2026-04-20.md §U-7)
- **U-8 LoginAttempt retention policy** — RetentionConfig class missing; worker feature needed. (docs/audit/epic-002-review-2026-04-20.md §U-8)

### EPIC-002

- **C-4 FEAT-021/STORY-048 duplication of FEAT-003/STORY-006** — audit recommends collapsing FEAT-021 into FEAT-003 and moving STORY-048 list AC into STORY-006. Partial fix applied (depends_on added); full collapse requires product decision on feature ownership. (docs/audit/epic-002-review.md §C-4)
- **m-8 STORY-043 quiet-hours semantics** — single global user-level setting vs per-event overrides. Model and API disagree; needs product input. (docs/audit/epic-002-review.md §m-8)
- **(b)3 STORY-043 → FEAT-102 dependency** — canonical channel routing link not declarable without cross-epic reference field. (docs/audit/epic-002-review.md §(b)3)
- **(b)4/5 STORY-044 → FEAT-102 / FEAT-167 / FEAT-179 dependencies** — same linkage convention gap. (docs/audit/epic-002-review.md §(b)4-5)
- **(c)2 FEAT-015 trusted-browser list & individual revoke** — audit suggests a new story or AC to list/revoke TrustedBrowser rows individually. Needs product input. (docs/audit/epic-002-review.md §(c)2)

### EPIC-003 (2026-04-20 re-audit)

- **M3 BYOK rotate_policy_days editable** — FEAT-025 promises "enforce rotation policy" but no story lets an operator set `rotate_policy_days`. Needs new story or extended STORY-060. (docs/audit/epic-003-review-2026-04-20.md §M3)
- **M4 ApiKey.scopes materialization vs derived** — model description implies auth-time compute; stories write materialized column. Pick one and align STORY-323 edge auth. (docs/audit/epic-003-review-2026-04-20.md §M4)
- **m3 ApiKey.rotation_due dead field** — no story writes or reads it; either drop or add a writer. (docs/audit/epic-003-review-2026-04-20.md §m3)
- **m7 non_functional boilerplate** — prune per-story lines that do not match scope. Editorial sweep. (docs/audit/epic-003-review-2026-04-20.md §m7)
- **m8 BYOKCredential.rate_limit_rpm/tpm vs ProviderRateLimit rows** — two structures, no canonical owner. (docs/audit/epic-003-review-2026-04-20.md §m8)
- **X2 STORY-323 edge auth / scopes representation** — edge logic must match whichever representation EPIC-003 picks. (docs/audit/epic-003-review-2026-04-20.md §X2)
- **U1 BYOK rotation-grace expiry job** — Critical. Predecessor never transitions to "revoked" after grace window; no analogous job exists. (docs/audit/epic-003-review-2026-04-20.md §U1)
- **U2 BYOK rotation-policy configuration surface** — no UI/API to set `rotate_policy_days`. Ties to M3. (docs/audit/epic-003-review-2026-04-20.md §U2)
- **U3 BYOK upstream-secret inbound leak-scan path** — FEAT-028 only covers gateway-issued keys; no BYOK-leak story. (docs/audit/epic-003-review-2026-04-20.md §U3)
- **U4 KeyAnomaly detector config surface** — FEAT-041 is generic (Anomaly); no mention of KeyAnomaly thresholds. (docs/audit/epic-003-review-2026-04-20.md §U4)
- **U5 ApiKeyExpiryNotice dedupe / quiet-hours** — dedupe key and NotificationPreference honouring unspecified. (docs/audit/epic-003-review-2026-04-20.md §U5)

### EPIC-003

- **m7 Approval.kind shared between FEAT-027 and FEAT-160** — audit wants a separate Approval.kind for break-glass key creation vs elevated-scope grant. Belongs in the EPIC-011 pass. (docs/audit/epic-003-review.md §m7)
- **X1 FEAT-133 BYOK data class enumeration** — add BYOK credential ciphertext as a CMK-wrappable data class in FEAT-133. Deferred to EPIC-010 pass. (docs/audit/epic-003-review.md §X1)
- **(c) BYOK rotation policy edit story** — `rotate_policy_days` observable but not editable; needs a new story under FEAT-025. Product input required. (docs/audit/epic-003-review.md §(c))

### EPIC-004 (2026-04-20 re-audit)

- **C4 FEAT-033 → FEAT-099/100/102 bridge** — Anomaly severity=crit still doesn't synthesize AlertEvent or go through FEAT-102 routing. (docs/audit/epic-004-review-2026-04-20.md §C4)
- **C5 ToolInvocation producer** — no story declares the row writer; producer should live under FEAT-146. (docs/audit/epic-004-review-2026-04-20.md §C5)
- **M2 FEAT-031 tools/flags drill-in** — tools/flags drawer panels still have no backing AC. (docs/audit/epic-004-review-2026-04-20.md §M2)
- **M4 STORY-099 pointer-only** — resolve by deletion + fold or by shape. (docs/audit/epic-004-review-2026-04-20.md §M4)
- **M7 FEAT-039 request-scoped ShareLink** — enum value "request" has no backing AC. (docs/audit/epic-004-review-2026-04-20.md §M7)
- **m1 non_functional copy-paste drift** — pervasive across STORY-073..077, 082..084, 086. Editorial sweep. (docs/audit/epic-004-review-2026-04-20.md §m1)
- **m2 STORY-094 CSV export controls** — inline CSV exports don't inherit STORY-088 guarantees. (docs/audit/epic-004-review-2026-04-20.md §m2)
- **X3 "Cache savings" dual emitter** — STORY-082 AC-004 and STORY-084 both emit the metric. (docs/audit/epic-004-review-2026-04-20.md §X3)
- **U1 Request-log ingestion pipeline** — Critical. No feature owns the pipeline. (docs/audit/epic-004-review-2026-04-20.md §U1)
- **U2 MetricSeries rollup worker** — Critical. 26 story NFRs pin to rollups with no producer. (docs/audit/epic-004-review-2026-04-20.md §U2)
- **U3 Anomaly detector evaluation worker** — Critical. STORY-085 AC-003 demands worker behavior no feature owns. (docs/audit/epic-004-review-2026-04-20.md §U3)
- **U4 Prompt full-text search index management** — Major. Index lifecycle and viewer-conditional indexing unowned. (docs/audit/epic-004-review-2026-04-20.md §U4)
- **U5 Async request-data export lifecycle** — Major. No model, no worker spec, no retry/expiry. (docs/audit/epic-004-review-2026-04-20.md §U5)
- **U6 ToolInvocation producer pipeline** — Major. See C5. (docs/audit/epic-004-review-2026-04-20.md §U6)
- **U7 Share-link visit authorization/audit** — Major. Visit-time RBAC, visit AuditLog, open_count concurrency unowned. (docs/audit/epic-004-review-2026-04-20.md §U7)
- **U8 Replay isolation mechanics** — Minor. Budget/anomaly-exclusion behavior unspecified. (docs/audit/epic-004-review-2026-04-20.md §U8)

### EPIC-004

- **C1 conflict FEAT-041 citation** — EPIC-003 audit proposed FEAT-024; EPIC-004 audit proposed FEAT-033. Applied later (more specific) fix to FEAT-033. Flagging in case reviewers disagree. (docs/audit/epic-003-review.md §C4 + docs/audit/epic-004-review.md §C1)
- **M2 FEAT-031 tools/flags drill-in** — add ACs surfacing per-request tool invocation list and safety/pii flag rationale. Needs product input on drawer UI. (docs/audit/epic-004-review.md §M2)
- **M6 FEAT-033 to EPIC-009 alerts integration** — add a story bridging Anomaly → Alert / AlertEvent. Needs product input. (docs/audit/epic-004-review.md §M6)
- **m1 non_functional copy-paste drift** — broad editorial pass to prune per-story NFR lists that inherit inapplicable constraints. Deferred; out of scope for the targeted-fix round. (docs/audit/epic-004-review.md §m1)

### EPIC-005 (2026-04-20 re-audit)

- **C2 Mid-stream retry config surface** — RoutingRule has no field for "fallback may reissue full request mid-stream". (docs/audit/epic-005-review-2026-04-20.md §C2)
- **C3 RoutingRule sub-schemas** — canary/shadow/retry remain opaque JSON. (docs/audit/epic-005-review-2026-04-20.md §C3)
- **M1 canary windows, M2 strategy stories, M4 CatalogPolicy precedence, M5 fallback naming, M6 auto-promote, M7 cache/safety cross-epic, M8 catalog sync, M9 FEAT-058/059 placement** — structural or product-input decisions. (docs/audit/epic-005-review-2026-04-20.md §M1..M9)
- **m1..m5 minors** — hero response shape, human_description persistence, divergence model, drawer copy source, allowed_regions enforcement. (docs/audit/epic-005-review-2026-04-20.md §m1..m5)
- **U1..U8 uncited-but-required** — provider catalog sync (Critical), shadow comparison model (Major), canary metric aggregation (Major), routing-rule validator (Major), routing change notifications (Major), readiness hydration (Major), preview allowlist (Minor), golden-dataset versioning (Minor). (docs/audit/epic-005-review-2026-04-20.md §U1..U8)

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

### EPIC-006 (2026-04-20 re-audit)

- **C-4 safety_policy_change firing path** — still dead; needs EPIC-007 story emitting CacheEvictionEvent on DetectionRule/PiiCategory change. (docs/audit/epic-006-review-2026-04-20.md §C-4)
- **C-6 streaming × cache** — replay framing, cache-write for streamed requests, ttft on hit. (docs/audit/epic-006-review-2026-04-20.md §C-6)
- **N-1, N-2, N-5, N-6, N-10, N-11 minors** — prompt_redacted naming, scope enum, fp_rate feedback loop, hot threshold config, AuditLog action catalog. (docs/audit/epic-006-review-2026-04-20.md §N-*)
- **X-1, X-3..X-7 cross-epic** — cache backend for graceful degradation, safety-policy → cache, budget on hits, shadow/canary × cache, AlertRule cache category, graceful shutdown. (docs/audit/epic-006-review-2026-04-20.md §X-*)
- **R-1, R-2, R-5, R-6, R-7, R-10 missing refs** — FEAT-064 over-promise, PromptSegment CRUD, safety_policy_change source, event catalog, scoped purge story, CacheWarmupJob eta. (docs/audit/epic-006-review-2026-04-20.md §R-*)
- **U-1..U-9 uncited-but-required** — streaming replay, safety-policy invalidation, write-suppression-on-block (now applied partial), event catalog, scope-keyed config, cache-event notifications, worker ownership, per-region topology, AlertRule integration. (docs/audit/epic-006-review-2026-04-20.md §U-*)

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

### EPIC-007 (2026-04-20 re-audit)

- **C-2 PiiCategory org-less** — needs structural decision on PiiCategory.org_id vs new PiiPolicy model. (docs/audit/epic-007-review-2026-04-20.md §C-2)
- **C-4 SafetyAllowanceGrant** — STORY-169 one-time allow has no backing model. (docs/audit/epic-007-review-2026-04-20.md §C-4)
- **m-1, m-3, m-4, m-5 minors** — PII category seeding, FEAT-102 audience resolution, SafetyPosture derivation, STORY-183 RBAC. (docs/audit/epic-007-review-2026-04-20.md §m-*)
- **X-1..X-7 cross-epic** — cache invalidation on safety publish, semantic-cache coherence, RetentionConfig coverage, pipeline ordering, residency vs unredact, AlertRule template for approval SLA, Request.pii_flag/safety_flag ownership. (docs/audit/epic-007-review-2026-04-20.md §X-*)
- **MR-1..MR-5 missing models** — ApproverDelegation, pipeline ordering feature, cross-tenant abuse correlation feature, SafetyAllowanceGrant, false_positive (now partial via review_status enum). (docs/audit/epic-007-review-2026-04-20.md §MR-*)
- **U-1..U-8 uncited-but-required** — pipeline ordering, SafetyPosture aggregator, vault lifecycle worker, cross-tenant abuse correlator, PII seeding, allowance grant feature, AlertRule template, hot-reload propagation. (docs/audit/epic-007-review-2026-04-20.md §U-*)

### EPIC-007

- **M-2/M-3 action precedence and override matrix** — need product decision on block/redact/flag/allow ordering and override transitions. (docs/audit/epic-007-review.md §M-2, §M-3)
- **M-6 mode declarations** — add mode:both to all EPIC-007 features (editorial sweep). (docs/audit/epic-007-review.md §M-6)
- **M-8 cross-tenant abuse signal** — new feature/story needed for trust_and_safety aggregation. (docs/audit/epic-007-review.md §M-8)
- **M-9 ApproverDelegation model** — STORY-178 OOO/delegate has no backing model. (docs/audit/epic-007-review.md §M-9)
- **M-10 STORY-183 live flow RBAC/residency** — needs product input on operator visibility. (docs/audit/epic-007-review.md §M-10)
- **X-1..X-6 cross-epic interactions** — safety-rule-driven cache invalidation, semantic-cache coherence, pipeline ordering, residency × unredact — all need product input. (docs/audit/epic-007-review.md §X-1..X-6)
- **MR-1..MR-3 missing features/models** — pipeline ordering feature, cross-tenant abuse correlation, approver delegation. (docs/audit/epic-007-review.md §MR-1..MR-3)

### EPIC-008 (2026-04-20 re-audit)

- **M1..M8 alert-bridge / paging surfaces / API paths / FEAT-091 overlap** — all tied to U14 system-managed AlertRules. (docs/audit/epic-008-review-2026-04-20.md §M1..M8)
- **M4 BudgetForecast persistence** — Budget derived fields have no history for backtest (U2 ties). (docs/audit/epic-008-review-2026-04-20.md §M4)
- **M5 Request.cost → Budget.spent pipeline** — unowned (U1 ties). (docs/audit/epic-008-review-2026-04-20.md §M5)
- **M7 API path split on /api/budgets/*** — structural canonicalization decision needed. (docs/audit/epic-008-review-2026-04-20.md §M7)
- **M12 STORY-185 effective_cap** — compute vs persisted decision. (docs/audit/epic-008-review-2026-04-20.md §M12)
- **m2..m7, m9, m10 minors** — waiver typed-confirmation, non_functional boilerplate, UserBudget.outlier definition, ProjectOwner model, asymmetric edit/delete, FEAT-097 mode split, approval expiry worker, FEAT-095 ui blocks. (docs/audit/epic-008-review-2026-04-20.md §m*)
- **X1..X7 cross-epic** — FEAT-141 citation, gateway budget gate owner, Budget→AlertRule bridge, routing-engine downgrade hook, cache-hit cost attribution, Billing mode split, self_hosted phone-home. (docs/audit/epic-008-review-2026-04-20.md §X*)
- **U1..U16 uncited-but-required** — counter pipeline, forecast store, approval expiry worker, gateway gate, downgrade hook, cycle scheduler, FX ingestion, plan lifecycle, Invoice model, Contest/Credit models, ScheduledExport, per-request cost-center (partial), readiness hydration, AlertRule bridge, dedup store (partial), drift metric. (docs/audit/epic-008-review-2026-04-20.md §U*)

### EPIC-008

- **M1 BudgetPolicy threshold overload** — split `approval_threshold_pct` into edit/waiver variants. Needs product input. (docs/audit/epic-008-review.md §M1)
- **M3 budget signals via AlertRule** — route soft-threshold alerts through managed AlertRule instead of direct AlertEvent writes. Needs product input. (docs/audit/epic-008-review.md §M3)
- **M4 FEAT-091 overage vs soft-alert surfaces** — pick one canonical emitter; reduces duplicate notifications. (docs/audit/epic-008-review.md §M4)
- **M8 budgets API path canonicalisation** — `/api/budgets/:id` vs `/api/budgets/teams/:id/...`. Structural API decision. (docs/audit/epic-008-review.md §M8)
- **M11 Budget.spent pipeline story** — specify Request→Budget counter reconciliation. Needs new story under FEAT-086. (docs/audit/epic-008-review.md §M11)
- **M12 BudgetForecast model** — move projected/runs_out_on off Budget; define trend and worker cadence. Needs product input. (docs/audit/epic-008-review.md §M12)
- **minor drift items (m1, m3, m4, m5, m7, m8, m9, m10, m11)** — boilerplate NFRs, typed-confirmation policy, audit of FX override magnitude, UserBudget.outlier definition, project owner join table, STORY-208 asymmetry, FEAT-097 mode branching, waiver cycle expiry, approval queue cleanup worker. (docs/audit/epic-008-review.md §m1..m11)

### EPIC-009 (2026-04-20 re-audit)

- **C5 AlertRuleSubscription model** — needs new model + API. (docs/audit/epic-009-review-2026-04-20.md §C5)
- **M2/M3/M4 STORY-232 coverage + audience refactor** — AlertRule.channels → audience is the structural fix; STORY-232 needs email/webhook/in-app ACs + mode collapse + audit-of-audience. (docs/audit/epic-009-review-2026-04-20.md §M2-M4)
- **M6 PagerDuty gating** — air-gapped fallback path unspecified. (docs/audit/epic-009-review-2026-04-20.md §M6)
- **M10 release gate on burned error budget** — new story needed under FEAT-174. (docs/audit/epic-009-review-2026-04-20.md §M10)
- **m2..m11 minors** — scope enum, config_hot_reload vs 10s eval, category enum, channels json, STORY-235 muted-match AC, severity validation, STORY-242 FEAT-102 + digest, STORY-246 depends_on, fires_30d writer, FEAT-104 updates field. (docs/audit/epic-009-review-2026-04-20.md §m*)
- **X1..X8 cross-epic** — AlertEvent.source not set by emitters (EPIC-008/011 pending), anomaly→AlertEvent, ingestion-health, worker-fleet→AlertEvents, STORY-269 forward-path assertion, etc. (docs/audit/epic-009-review-2026-04-20.md §X*)
- **U1..U11 uncited-but-required** — alert evaluation worker, notification dispatch worker, inbound PagerDuty webhook, AlertRuleSubscription CRUD, evaluation health monitor, ActionItem CRUD (partial), platform-scope AlertRule authoring, release-promotion SLO gate, anomaly fan-out, inbox writer, iCal on-call sync. (docs/audit/epic-009-review-2026-04-20.md §U*)

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

### EPIC-010 (2026-04-20 re-audit)

- **C-1 FEAT-107 mode split (identity vs billing)** — structural. (docs/audit/epic-010-review-2026-04-20.md §C-1)
- **C-3 FEAT-127 DR mode gating** — structural. (docs/audit/epic-010-review-2026-04-20.md §C-3)
- **M-2 STORY-296 DR-drill audience** — needs product input on mode. (docs/audit/epic-010-review-2026-04-20.md §M-2)
- **M-6 FEAT-131 geoip default** — fail-open vs fail-closed default unresolved. (docs/audit/epic-010-review-2026-04-20.md §M-6)
- **m-1..m-9 minors** — boilerplate NFRs, GeoPolicy/DlpExportConfig models, tech_contact roster gap, etc. (docs/audit/epic-010-review-2026-04-20.md §m*)
- **X-1..X-7 cross-epic** — FEAT-107 billing split, DR vs fleet health ownership, delete-org vs install lifecycle, SCIM cascade depends_on, CMK data-class coverage for BYOK ciphertext, STORY-257 PII precedence, STORY-280 alerting conventions. (docs/audit/epic-010-review-2026-04-20.md §X*)
- **U-1..U-11 uncited-but-required** — audit-log signing-key lifecycle (Critical), ScimConflict workflow (partial via M-10), restore-request ticket, cancel-delete, break-glass runtime state, Webhook auto-disable threshold, GeoPolicy model, DlpExportConfig model, ingestion-health alert, Org signing-secret lifecycle, Integration credentials encryption. (docs/audit/epic-010-review-2026-04-20.md §U*)

### EPIC-010

- **C-4 FEAT-133 revocation semantics** — reconcile saas fallback vs self_hosted fail-closed across the feature description and STORY-308/309/310 NFRs. Needs product input. (docs/audit/epic-010-review.md §C-4)
- **M-1 FEAT-107 identity vs billing mode split** — split into an identity feature (both modes) and a saas-only billing half. Needs product decision. (docs/audit/epic-010-review.md §M-1)
- **M-3 dual IP allowlist storage** — consolidate onto OrgIpAllowlist + /api/org/ip-allowlist. Structural. (docs/audit/epic-010-review.md §M-3)
- **M-4 FEAT-127 DR role gating** — saas vs self_hosted execute-restore vs request-restore. Needs product input. (docs/audit/epic-010-review.md §M-4)
- **M-7 GeoIP default behavior** — flip default to fail-closed. Needs product input. (docs/audit/epic-010-review.md §M-7)
- **Minor m-1..m-9 editorial** — SCIM NFR misapplication, FEAT-131 GeoPolicy model, FEAT-132 DlpExportConfig, ResidencyConfig.dpo_contact consolidation, SsoConfig.signed_users, /api/v1 versioning consistency, SSO-enforced invite race, AuditSink.credentials encryption, webhook signature replay-window wording. (docs/audit/epic-010-review.md §m-1..m-9)
- **X-1..X-7 cross-epic** — FEAT-107 vs FEAT-095/096/098, FEAT-127 vs FEAT-170, delete-org vs install lifecycle, FEAT-133 CMK data classes for BYOK, FEAT-113 PII toggle vs FEAT-070, STORY-280 audit-sink audience. Mostly product input. (docs/audit/epic-010-review.md §X-1..X-7)

### EPIC-011 (2026-04-20 re-audit)

- **C1 / U1 pipeline-stage ordering feature** — Critical. No FEAT declares the canonical ordering of cache/safety/budget/idempotency. (docs/audit/epic-011-review-2026-04-20.md §C1, §U1)
- **M2 FEAT-160 belongs in EPIC-003** — structural feature move. (docs/audit/epic-011-review-2026-04-20.md §M2)
- **M3 FEAT-150..FEAT-157 provider API surface** — epic split. (docs/audit/epic-011-review-2026-04-20.md §M3)
- **M4 FEAT-149 vs FEAT-143 telemetry overlap** — dual writer on TelemetryConfig. (docs/audit/epic-011-review-2026-04-20.md §M4)
- **M5 STORY-323 rejection metadata** — AccessLog model decision. (docs/audit/epic-011-review-2026-04-20.md §M5)
- **M9 STORY-348..STORY-371 skeletal stories** — needs expansion to match EPIC-011 depth. (docs/audit/epic-011-review-2026-04-20.md §M9)
- **m1..m8 minors** — boilerplate, shared-credentials toggle, break-glass dedupe window, per-phase timeouts, P1/P0 alignment, fallback_attempts field, pipeline cross-refs. (docs/audit/epic-011-review-2026-04-20.md §m*)
- **X1..X7 cross-epic** — retry/circuit ownership, cache placement, safety pipeline position, budget admission, OTel trace-id mapping, per-tenant concurrency, readiness hydration. (docs/audit/epic-011-review-2026-04-20.md §X*)
- **U1..U9 uncited-but-required** — pipeline ordering, AccessLog, per-tenant concurrency, readiness hydration, residency-aware cache lookup, ApiKey.kind/Request.break_glass, pipeline-stage timeouts, IngressEndpointState, IdempotencyKey. (docs/audit/epic-011-review-2026-04-20.md §U*)

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

### EPIC-013

- **C4 Antirion staff principal model** — saas needs an OperatorPrincipal concept distinct from tenant User. Structural; needs product input. (docs/audit/epic-013-review.md §C4)
- **M2 FEAT-181/182 mode tag expressiveness** — baseline `mode` tag cannot express "Antirion-console-only, both modes". Needs baseline schema decision. (docs/audit/epic-013-review.md §M2)
- **M4 /antirion/* gating contract** — FEAT-171 must gate both /operator/* and /antirion/*. Needs product input. (docs/audit/epic-013-review.md §M4)
- **M7 STORY-410 self_hosted branch** — audit visibility rule under 1-tenant install. Needs product input. (docs/audit/epic-013-review.md §M7)
- **M8 FEAT-112 residency pointer** — already fixed in EPIC-010 pass. (docs/audit/epic-013-review.md §M8)
- **M9 STORY-423 vs STORY-408 pre-completion carve-out** — bootstrap route must be reachable pre-platform-admin. Needs product input. (docs/audit/epic-013-review.md §M9)
- **M11 PlatformIncident.created_by in saas** — ties to C4 staff-principal. (docs/audit/epic-013-review.md §M11)
- **Minor m1..m9** — editorial drift. (docs/audit/epic-013-review.md §m1..m9)
- **X1..X8 cross-epic** — operator paging integration (FEAT-102 extension), cross-tenant abuse producer (EPIC-007), install_id handoff between FEAT-164 and FEAT-181, baseline mode-tag schema upgrade, notifications_model self_hosted exception, license.revoked story, read-vs-write definition for license enforcement. (docs/audit/epic-013-review.md §X1..X8)

