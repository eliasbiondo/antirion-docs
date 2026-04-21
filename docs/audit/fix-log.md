# Audit Fix Log

One row per finding. Columns: epic | audit citation | action (applied / deferred / conflict / skipped-as-non-actionable) | change summary.

| Epic | Audit Citation | Action | Change Summary |
|------|----------------|--------|----------------|
| EPIC-001 | C-1 FEAT-012 role list | applied | FEAT-012 description lists owner/admin/developer/analyst/viewer/service; removed invented `member` role |
| EPIC-001 | C-2 platform_admin missing | applied | User.role enum description extended with `platform_admin` gated to self_hosted |
| EPIC-001 | C-3 User.status=locked | applied | STORY-023 AC-001 removed status="locked"; uses locked_until + SessionPolicy; STORY-024 AC-001 rewritten to clear locked_until + failed_login_count |
| EPIC-001 | C-4 is_service_account | applied | STORY-026 AC-001 now creates User with role="service" + human_owner_user_id + created_by_user_id |
| EPIC-001 | C-5 FEAT-009 lockout notification | applied | STORY-023 + STORY-024 emit Notification kind=security to target user; AuditLog records audience list |
| EPIC-001 | M-1 duplicate delete-team | applied | Removed STORY-015 AC-004 and its DELETE /api/teams/:id API block; STORY-017 is sole delete path |
| EPIC-001 | M-2 Role.org_id / Role.builtin | applied | Role model gained org_id (nullable FK:Org) and builtin (bool); name uniqueness scoped to (org_id, name) |
| EPIC-001 | M-3 scopes vs permissions | applied | Renamed Role.scopes to Role.permissions |
| EPIC-001 | M-4 STORY-022 AlertEvent | applied | STORY-022 AC-001 now emits Notification kind=security per notifications_model; depends_on=STORY-011; data_models = [User, AuditLog, Notification] |
| EPIC-001 | M-5 SsoConfig SLO fields | applied | Added SsoConfig.slo_url, back_channel_logout_url, signing_cert |
| EPIC-001 | M-6 lockout policy | applied | SessionPolicy gained lockout_threshold, lockout_window_minutes, lockout_duration_minutes |
| EPIC-001 | M-7 service-account ownership | applied | User gained human_owner_user_id, created_by_user_id |
| EPIC-001 | M-8 STORY-019 filter | applied | AC-001 names filter `type = "service" AND revoked_at IS NULL` explicitly |
| EPIC-001 | M-9 STORY-017 AC-005 | applied | Added AC-005 "Block delete when team has active Projects" |
| EPIC-001 | m-1 STORY-002 non_functional | applied | Replaced generic audit lines with trust-device specific (cookie flags, fingerprint stability, revocation triggers) |
| EPIC-001 | m-2 STORY-022 depends_on | applied | Changed STORY-022 depends_on from STORY-018 to STORY-011 |
| EPIC-001 | m-3 STORY-029 depends_on | applied | Added depends_on=[STORY-026, STORY-028] |
| EPIC-001 | m-4 STORY-003 Forgot wording | deferred | UI component name ambiguous; needs design input |
| EPIC-001 | m-5 UserPrefs on EPIC-001 screens | skipped-as-non-actionable | Author recommends baseline coverage; no file change warranted |
| EPIC-001 | m-6 STORY-012 role-change notification audience | deferred | Needs product input on canonical audience list for this event class |
| EPIC-001 | m-7 STORY-018 last-owner guard | applied | Added AC-002 blocking offboarding of the last remaining owner |
| EPIC-001 | m-8 STORY-018 typed confirmation | deferred | Needs product policy decision on destructive_action_confirmation_policy scope |
| EPIC-001 | m-9 STORY-027/030 last_used_at | applied | Replaced with User.last_active_at + User.joined_at |
| EPIC-001 | m-10 STORY-011 hierarchy string | applied | Replaced inline hierarchy with "Levels per Role.level; writes gated by level" |
| EPIC-001 | m-11 FEAT-010 priority vs FEAT-003 | deferred | Priority tradeoff needs product input |
| EPIC-001 | X-1 Org contact fields | applied | Added finance_contact, privacy_officer, primary_contact (nullable) to Org |
| EPIC-001 | X-2 STORY-020 cross-epic | deferred | No `related_features` field in schema; needs cross-epic linkage convention |
| EPIC-001 | X-3 STORY-018/019 cross-epic | deferred | Same as X-2 |
| EPIC-001 | X-4 STORY-022 AlertEvent/EPIC-009 | applied | Resolved by M-4 fix (no AlertEvent used) |
| EPIC-001 | E-1/E-2 mode-availability | skipped-as-non-actionable | Call-out only, no concrete edit proposed |
| EPIC-001 | R-1 security oncall naming | applied | Replaced "security oncall" with Org.security_contact audience per notifications_model |
| EPIC-001 | R-2 STORY-024 deny list | applied | Non_functional line now names denied roles explicitly |
| EPIC-001 | D-1 STORY-029 soft-deleted | applied | Uses User.status = "offboarded" instead of "soft-deleted" |
| EPIC-002 | C-1 User.status=pending_deletion | applied | STORY-046/047 now drive state off AccountDeletionRequest.status; User.status stays "active" until cutover |
| EPIC-002 | C-2 PersonalToken.status | applied | Added status field (active/rotating/revoked); STORY-046/047 ACs updated accordingly |
| EPIC-002 | C-3 RecoveryCode model | applied | Added RecoveryCode model; STORY-039 AC and data_models updated to use it |
| EPIC-002 | C-4 FEAT-021 duplicate | deferred (partial) | Added depends_on STORY-006 on STORY-048; full collapse/removal of FEAT-021 deferred for product input |
| EPIC-002 | M-1 EmailVerificationToken | applied | STORY-036 AC-001 uses consumed_at explicitly |
| EPIC-002 | M-2 MfaFactor.is_primary | applied | Added is_primary bool field |
| EPIC-002 | M-3 STORY-040 type vs kind | applied | AC-002 now uses "kind" to match model |
| EPIC-002 | M-4 photo_url vs avatar_url | applied | STORY-035 API response renamed to avatar_url |
| EPIC-002 | M-5 NotificationPreference row shape | applied | STORY-043 AC-001 reworded to match (row per event, channels JSON) |
| EPIC-002 | M-6 deletion confirmation | applied | STORY-046 AC-001 now requires typing account handle; API body adds confirm_handle |
| EPIC-002 | M-7 password-changed notification | applied | STORY-038 gained notification AC, audit AC, depends_on STORY-006, data_models |
| EPIC-002 | M-8 STORY-044 mode/audience | applied | Added AC-003 recording resolved audience list per notifications_model |
| EPIC-002 | M-9 FEAT-014 description | applied | Trimmed to domain-specific wording |
| EPIC-002 | m-1 route convention | applied | /api/account/* → /api/users/me/* across STORY-044/045/046/047 |
| EPIC-002 | m-2 FEAT-016 naming | applied | Title renamed to "Personal tokens" |
| EPIC-002 | m-3 STORY-042 scope inheritance | applied | Added AC-003 + non_functional note enforcing scope containment |
| EPIC-002 | m-4 STORY-042 list | applied | Added AC-004 and GET /api/users/me/tokens endpoint |
| EPIC-002 | m-5 STORY-035 collision | applied | Added AC-004 for 409 handle collision; 409 added to errors |
| EPIC-002 | m-6 STORY-036 success page | applied | Clarified success-page wording for signed-out-browser case |
| EPIC-002 | m-7 user_agent | applied | FEAT-019 description and STORY-045 AC-001 include user_agent |
| EPIC-002 | m-8 quiet-hours semantics | deferred | Global vs per-event needs product input |
| EPIC-002 | X-2 STORY-039 TrustedBrowser create-path | applied | Added depends_on STORY-002 |
| EPIC-002 | X-3 STORY-045 LoginAttempt source | applied | Added depends_on STORY-023 |
| EPIC-002 | (b)1 STORY-038 session revocation dep | applied | Added depends_on STORY-006 |
| EPIC-002 | (b)3/4/5 STORY-043/044 cross-epic refs | deferred | No schema for narrative cross-refs; needs linkage convention |
| EPIC-002 | (c)1 FEAT-020 owner hand-off | applied | Description updated to cross-reference FEAT-005/FEAT-012; no invented FEAT |
| EPIC-002 | (c)2 FEAT-015 trusted-browser list | deferred | New story/AC needed; requires product input |
| EPIC-003 | C1 KeyAnomaly.kind | applied | Added "leak" to KeyAnomaly.kind enum description |
| EPIC-003 | C2 BYOKCredential.status | applied | Declared enum active|degraded|overdue|invalid|revoked with precedence; STORY-059/061 aligned |
| EPIC-003 | C3 STORY-062 duplicate cadence | applied | STORY-062 rewritten as UI-pill-only; cadence owned by STORY-064 |
| EPIC-003 | C4 FEAT-041 description | applied | Reference corrected from FEAT-022 to FEAT-024 |
| EPIC-003 | M1 BYOK rotation grace | applied | Added BYOKCredential.successor_id + rotation_grace_ends; STORY-056 AC-002 rewritten |
| EPIC-003 | M2 STORY-053 TTL | applied | Added expires_at to PATCH body + AC-003 (TTL cap via ApiAccessConfig.key_max_ttl_days) |
| EPIC-003 | M3 BYOK name vs label | applied | Renamed model field to label |
| EPIC-003 | M4 rotated_at vs last_rotated_at | applied | Renamed model field to last_rotated_at |
| EPIC-003 | M5 scope vocabulary | applied | STORY-052 filter and STORY-065 AC use domain scopes (chat.completions, cache.write) |
| EPIC-003 | M6 elevated scope representation | applied | ApiKey gained base_scopes, elevated_scopes, elevated_until; STORY-065/066 ACs rewritten |
| EPIC-003 | M7 STORY-056 priority | applied | Raised to P0 |
| EPIC-003 | M8 STORY-056 CMK wording | applied | Non_functional rewritten to reference FEAT-133 CMK data class and fail-closed policy |
| EPIC-003 | M9 notifications model drift | applied | STORY-061/064 audiences rewritten to canonical roles with fallback chain |
| EPIC-003 | M10 STORY-053 AC-002 | applied | "SafetyEvent or AuditLog" → "AuditLog with action apikey.ip_allowlist.violation" |
| EPIC-003 | M11 STORY-323 rotating-state AC | applied | Added AC-005 for dual-hash grace at the edge |
| EPIC-003 | m1 FEAT-022 description | applied | Added list/browse |
| EPIC-003 | m2 FEAT-025 description | applied | Expanded to cover six stories |
| EPIC-003 | m3 STORY-055 anomaly ticker | applied | Removed undefined "anomaly ticker" phrase |
| EPIC-003 | m4 STORY-067 air-gapped 404 | applied | Added AC-003 |
| EPIC-003 | m5 STORY-068 audit entries | skipped-as-non-actionable | Audit covered transitively by STORY-069; author notes it is consistent |
| EPIC-003 | m6 individual key revoke policy | skipped-as-non-actionable | Audit flags for awareness only |
| EPIC-003 | m7 Approval.kind shared | deferred | Cross-epic; EPIC-011 (FEAT-160) pass will handle |
| EPIC-003 | m8 STORY-065/066 notification audience | applied | Added Notification AC on STORY-066 approve path |
| EPIC-003 | m9 FEAT-028 mode key | skipped-as-non-actionable | Baseline accepts description-level declaration |
| EPIC-003 | X1 FEAT-133 BYOK data class | deferred | Belongs to EPIC-010 pass (FEAT-133 data-class enumeration) |
| EPIC-003 | X2 BYOK residency | applied | Added STORY-056 AC-003 requiring ciphertext in ResidencyConfig region |
| EPIC-003 | X5 Org.owner_user_id | applied | Added owner_user_id FK:User (nullable) to Org |
| EPIC-003 | (b) STORY-065/066/067 depends_on STORY-049 | applied | Declared dependencies |
| EPIC-003 | (c) BYOK rotation policy edit | deferred | New story needed under FEAT-025 — product input required |
| EPIC-004 | C1 FEAT-041 description | conflict | EPIC-003 audit wanted FEAT-024; EPIC-004 audit wanted FEAT-033 (more specific) — preferred later fix. Noted in deferred. |
| EPIC-004 | C2 AnomalyDetector model | applied | Added model with category/enabled/threshold_config/cooldown_seconds/last_fired_at; Anomaly gained detector_id and category; STORY-095/096/097 rewired |
| EPIC-004 | C3 SavedView scope/view_type | applied | Added scope and view_type fields |
| EPIC-004 | C4 Request tool/cancellation fields | applied | Added ToolInvocation model; Request.tools renamed to tool_count; added client_cancelled, mid_stream_dropped |
| EPIC-004 | C5 STORY-085 audience | applied | Added AC-003 recording audience_snapshot + saas/self_hosted routing per notifications_model |
| EPIC-004 | M1 FEAT-029 description | applied | Trimmed "embedded request log" from description |
| EPIC-004 | M2 FEAT-031 tools/flags drill-in | deferred | Needs new AC or story; product input |
| EPIC-004 | M3 duplicate replay | applied | STORY-079 no longer defines endpoint; STORY-090 is canonical |
| EPIC-004 | M4 STORY-088 RBAC/audit/notification | applied | Added requests.export scope gate, AuditLog, FEAT-102 Notification |
| EPIC-004 | M5 STORY-087 RBAC search | applied | Added AC-003 for role/team scope and redaction |
| EPIC-004 | M6 FEAT-033 → FEAT-099 integration | deferred | Needs new story; product input |
| EPIC-004 | M7 MetricSeries scope/cost | applied | Extended scope enum; added spend_input/spend_output/spend_cache columns |
| EPIC-004 | M8 STORY-099 duplicate | applied | Collapsed to pointer referencing STORY-093 |
| EPIC-004 | M9 mode declarations | applied (EPIC-scope) | Added tenant-scoped note to EPIC-004 description rather than per-feature declarations |
| EPIC-004 | M10 STORY-085 review status | applied | Rewritten AC-002 against Anomaly.review_status enum |
| EPIC-004 | m1 non_functional drift | deferred | Broad editorial pass; out of scope for this round |
| EPIC-004 | m2 STORY-072 filters | applied | Added api_key_id, user_id to query |
| EPIC-004 | m3 STORY-074 dangling ref | applied | Replaced with STORY-088 |
| EPIC-004 | m4 STORY-092 AuditLog | applied | Added AuditLog to data_models |
| EPIC-004 | m5 STORY-093 depends_on + NFR | applied | Added depends_on STORY-092 and signed-token NFR |
| EPIC-004 | m6 detector PATCH endpoint | applied | Added PATCH /api/anomaly-detectors/:id to STORY-096 |
| EPIC-004 | m7 STORY-094 breakdowns | applied | Added AC-003 covering project/api_key/env breakdowns |
| EPIC-004 | m8 RetentionConfig.anomalies_days | applied | Added field |
| EPIC-004 | X1 STORY-338 span attrs | applied | Added request_id, org_id, team_id, user_id to span attributes |
| EPIC-004 | X2 time-range dependency | applied | Added depends_on STORY-086 to STORY-070/072/082/094 |
| EPIC-004 | X3 FEAT-102 export notification | applied | STORY-088 AC-002 rewired via FEAT-102 |
| EPIC-004 | X4 EPIC-013 overlap note | applied | Added tenant-scoped clarification to EPIC-004 description |
| EPIC-004 | R5 EPIC-004 scope | applied | Expanded epic description |
| EPIC-005 | C1 routing latency budget | applied | Replaced repeated NFR line (32 stories) with 200µs p95 sub-budget note referencing baseline |
| EPIC-005 | C2 FEAT-051 scope | applied | Description restated to config-only; runtime owned by FEAT-139/FEAT-142 |
| EPIC-005 | C3 mid-stream retry | deferred | Baseline vs FEAT-139 contradiction needs product input |
| EPIC-005 | C4 STORY-107 hot-reload SLA | applied | Changed 60s to config-reload SLA |
| EPIC-005 | C5 STORY-131 ref | applied | STORY-122 → STORY-130 |
| EPIC-005 | C6 STORY-126 ref | applied | STORY-118 → STORY-125 |
| EPIC-005 | C7 FEAT-059 / STORY-141 ref | applied | FEAT-072 → FEAT-146 (dialect translation) |
| EPIC-005 | C8 RoutingRule sub-schemas | deferred | Structural model change; requires product input |
| EPIC-005 | M1 canary windows | deferred | Multiple named windows need product input |
| EPIC-005 | M2 missing strategy stories | deferred | New stories needed |
| EPIC-005 | M3 epic strategies list | applied | Description now lists six strategies + notes FEAT-058/059 inclusion |
| EPIC-005 | M4 CatalogPolicy precedence | deferred | Needs product input on merge semantics |
| EPIC-005 | M5 fallback naming collision | deferred | Structural; needs product input |
| EPIC-005 | M6 shadow NFR placement | applied | Moved "Shadow traffic never billed" onto STORY-119 |
| EPIC-005 | M7 canary auto-promote mutation | deferred | UX / product input required |
| EPIC-005 | M8 STORY-118 NFRs | applied | Added config-reload SLA and routing decision sub-budget lines |
| EPIC-005 | M9 STORY-129 audience | applied | Rewritten per canonical notifications_model roles |
| EPIC-005 | M10 cache/safety cross-epic | deferred | Needs product input |
| EPIC-005 | M11 catalog sync | deferred | New feature needed |
| EPIC-005 | M12 FEAT-058/059 placement | applied | EPIC-005 description now acknowledges FEAT-058/059 |
| EPIC-005 | m4 role drift | applied | STORY-108 narrator → "workspace admin"; STORY-133 → "engineering manager" |
| EPIC-005 | m7 STORY-121 wording | applied | Redis phrasing generalized to shared-store reference |
| EPIC-005 | m10 RoutingDeploy.type toggle | applied | Removed unused "toggle" from enum |
| EPIC-005 | X5 STORY-338 routing span fields | applied | Added routing_rule_id, routing_strategy, canary_arm, shadow |
| EPIC-006 | C-1 CacheEntry.org_id | applied | Added org_id (non-null FK:Org) to CacheEntry |
| EPIC-006 | C-2 CacheConfig.model_id unique | applied | Removed unique:true; CacheOverride.scope expanded to team|key|project|env|byok with precedence note |
| EPIC-006 | C-3 eviction_policy/max_size_mb | applied | Added fields to CacheConfig |
| EPIC-006 | C-4 drop-user unimplementable | applied | Added user_id to CacheEntry |
| EPIC-006 | C-5 STORY-148 BYOK rotation | applied | Added provider_id, byok_credential_id to CacheEntry; STORY-148 AC rewritten |
| EPIC-006 | C-6 streaming × cache | deferred | Needs new story; product input |
| EPIC-006 | C-7 redaction/cache coherence | deferred | Needs product input |
| EPIC-006 | C-8 warmup bypass | applied | STORY-154 AC rewritten to assert safety/budget/residency apply |
| EPIC-006 | C-9 typed confirmation | applied | STORY-147 AC-002 now requires typed slug + confirm_slug in body |
| EPIC-006 | M-1 semantic cache link | applied | Added semantic_cache_config_id to CacheEntry |
| EPIC-006 | M-2 backend/key_strategy enum | applied | Enumerated backend = exact|prompt_prefix|semantic, key_strategy = canonical|raw|normalized-semantic |
| EPIC-006 | M-3 URL namespace | applied | Unified /api/cache/* (renamed /api/caching/*) |
| EPIC-006 | M-4 priority mismatches | applied | FEAT-067 P0 → P2; STORY-142 P1 → P0 |
| EPIC-006 | M-5 retired vs cold | applied | STORY-146 AC uses status = "retired" |
| EPIC-006 | M-6 pricing knob | applied | Removed CacheConfig.token_discount; Model.cache_price is authoritative |
| EPIC-006 | M-7 cache hit cost decomposition | applied | STORY-145 AC-003 added |
| EPIC-006 | M-8 CacheOverride precedence | applied | Documented in CacheOverride description (most specific wins) |
| EPIC-006 | M-9 invalidate scope enum | applied | Added scope enum note (model|team|key|org) on STORY-147 non_functional |
| EPIC-006 | M-10 cache scopes | deferred | Scope enumeration for cache.read/invalidate/admin — needs product input |
| EPIC-006 | M-11 CacheEvictionEvent | applied | Added model; STORY-156 data_models references it |
| EPIC-006 | M-12 eviction burst | deferred | Needs product input |
| EPIC-006 | M-13 key_preview PII | applied | key_preview length bound and redaction note added on model |
| EPIC-006 | X-1/X-2 cache-key pinning | applied | STORY-142 AC notes resolved-model cache key |
| EPIC-006 | X-3 redaction/blocks | deferred | Overlaps C-7 |
| EPIC-006 | X-4 budget on cache hits | deferred | Needs product input |
| EPIC-006 | X-5 cache lookup latency | applied | STORY-142 non_functional now cites 500µs p95 sub-budget |
| EPIC-006 | X-6 degraded-mode backend | deferred | Needs product input |
| EPIC-006 | R-1/R-2/R-5/R-7 new stories | deferred | New stories needed; product input |
| EPIC-006 | R-3 warmup ETA | skipped-as-non-actionable | Removed "stated ETA" wording via STORY-154 rewrite |
| EPIC-006 | R-4 eviction rule_id FK | applied | CacheEvictionEvent.rule_id nullable FK:InvalidationRule |
| EPIC-006 | R-6 invalidation event catalog | deferred | Needs product input |
| EPIC-007 | C-1 prompt_original persistence | applied | Removed SafetyEvent.prompt_original; added RedactionVaultEntry model; FEAT-080 is sole reversal path |
| EPIC-007 | C-2 notifications audience | applied | STORY-159/177/178/180 ACs now cite canonical roles per notifications_model |
| EPIC-007 | C-3 Approval.kind data-reveal | applied | Added data-reveal to Approval.kind enum; STORY-179 uses it |
| EPIC-007 | C-4 DetectionRule.method taxonomy | applied | FEAT-073 description expanded to 8 methods |
| EPIC-007 | C-5 PiiCategory.action | applied | Added action field |
| EPIC-007 | C-6 fp_rate fields | applied | Added fire_count and fp_count; STORY-167 AC clarified |
| EPIC-007 | M-1 sev vs severity | applied | Renamed SafetyEvent.sev to severity |
| EPIC-007 | M-2 action precedence | deferred | Needs product input on precedence order |
| EPIC-007 | M-3 override matrix | deferred | Needs product input |
| EPIC-007 | M-4 status_label | applied | STORY-159 sets Request.status_label = safety_blocked |
| EPIC-007 | M-5 path drift | applied | All /api/safety/rules renamed to /api/detection-rules |
| EPIC-007 | M-6 mode declarations | deferred | Many features; out of scope editorial |
| EPIC-007 | M-7 STORY-168/170 versioning | applied | STORY-170 depends_on STORY-168; AC clarifies published-edit scope |
| EPIC-007 | M-8 cross-tenant abuse signal | deferred | New story/feature needed |
| EPIC-007 | M-9 STORY-178 OOO/delegate | deferred | Needs new model (ApproverDelegation) |
| EPIC-007 | M-10 STORY-183 live flow | deferred | Needs product input on RBAC |
| EPIC-007 | M-11 rule soft-delete | applied | Added DetectionRule.deleted_at |
| EPIC-007 | MR-4 redaction vault | applied | Added RedactionVaultEntry model |
| EPIC-007 | MR-5 installed_template_id | applied | Added DetectionRule.installed_template_id |
| EPIC-007 | m1..m9 minors | deferred | Batch editorial pass |
| EPIC-007 | X-1..X-6 cross-epic | deferred | Cross-epic interactions need product input |
| EPIC-007 | MR-1/MR-2/MR-3 missing features | deferred | Need new features/models |
| EPIC-008 | C1 BudgetEvent.amount | applied | Added amount, reason, valid_until fields |
| EPIC-008 | C2 BudgetEvent.approval_id | applied | Added approval_id + budget_id FKs |
| EPIC-008 | C3 Project.budget | applied | STORY-188 AC clarifies Budget-per-project model |
| EPIC-008 | C4 UserBudget.budget_id | applied | Added FK:Budget parent column |
| EPIC-008 | C5 shared_limiters FEAT id | applied | Baseline citation FEAT-139 → FEAT-138 |
| EPIC-008 | C6 STORY-187 refs | applied | STORY-088 → STORY-193, STORY-091 → STORY-196 |
| EPIC-008 | C7 Org contact fields | applied | Already added in EPIC-001 pass |
| EPIC-008 | M1 BudgetPolicy threshold overload | deferred | Needs product input |
| EPIC-008 | M2 429 → 402 | applied | STORY-189 AC-002 aligned with FEAT-180 |
| EPIC-008 | M3 AlertEvent vs AlertRule | deferred | Needs product input |
| EPIC-008 | M4 FEAT-091 overlap | deferred | Needs product input |
| EPIC-008 | M5 STORY-200 self_hosted billing | applied | Dropped mode-specific fallback (baseline says tenant-scoped roles behave identically) |
| EPIC-008 | M6 STORY-200 trust_and_safety | applied | Removed misplaced T&S fanout |
| EPIC-008 | M7 Budget.scope_id slug vs uuid | applied | STORY-186 example clarifies slug resolution |
| EPIC-008 | M8 API path split | deferred | Structural API change |
| EPIC-008 | M9 Approval.kind budget-change | applied | Added kind; STORY-197 uses it |
| EPIC-008 | M10 STORY-190 model IDs | applied | Replaced example with canonical claude-haiku-4-5-20251001 |
| EPIC-008 | M11 spent reconciliation | deferred | Needs new story |
| EPIC-008 | M12 BudgetForecast model | deferred | Structural change; needs product input |
| EPIC-008 | M13 STORY-208 immediate → SLA | applied | Rewritten to cite config-reload SLA |
| EPIC-008 | m6 Project.deleted_at | applied | Added soft-delete column |
| EPIC-008 | minor m1/m3/m4/m5/m7/m8/m9/m10/m11 | deferred | Editorial/product-input |
| EPIC-009 | C1 audience-driven notifications | deferred | Structural refactor; needs product input |
| EPIC-009 | C2 STORY-232 mode collapse | deferred | Ties to C1 refactor |
| EPIC-009 | C3 platform-scope AlertRule | applied | AlertRule.org_id nullable; added scope_kind |
| EPIC-009 | C4 FEAT-101 misdirection | applied | STORY-386 cross-ref changed to FEAT-102 |
| EPIC-009 | C5 StatusPageIncident fields | applied | Added Incident model (tenant-internal) with severity/participants/alert_event_id/org_id |
| EPIC-009 | C6 PostMortem structure | applied | Replaced content with structured fields; added ActionItem model |
| EPIC-009 | C7 AlertSnooze.fingerprint | applied | Added nullable fingerprint field |
| EPIC-009 | M1 StatusPageIncident vs Incident | applied | Resolved by C5 model split |
| EPIC-009 | M2 FEAT-100/103 overlap | deferred | Needs product decision |
| EPIC-009 | M3 severity high → crit | applied | STORY-236/237 use enum |
| EPIC-009 | M4 STORY-244 SLO target | applied | Example 99.9% → 99.95% |
| EPIC-009 | M5 error-budget release gate | deferred | New story needed |
| EPIC-009 | M6 STORY-223 AC-001 window | applied | Added window "30m" |
| EPIC-009 | M7 STORY-223 preview | applied | Preview now includes window |
| EPIC-009 | M8 in-app inbox channel | deferred | FEAT-102 description update |
| EPIC-009 | M9 Team.owner naming | applied | Baseline notifications_model now cites Team.lead_user_id |
| EPIC-009 | M10 PagerDuty gating | deferred | Needs product input |
| EPIC-009 | M11 AlertRule.scope_kind | applied | Covered by C3 fix |
| EPIC-009 | X1/X4 AlertEvent.rule_id nullable | applied | Added source field; rule_id nullable |
| EPIC-009 | X2 AlertRule.owner_user_id | applied | Added owner_user_id (nullable FK:User) |
| EPIC-009 | X3 audit-sink-degraded template | skipped-as-non-actionable | Observation only (gold-standard pattern) |
| EPIC-009 | X5/X6/X7 cross-epic gaps | deferred | Need new stories/product input |
| EPIC-009 | minors m1..m10 | deferred | Editorial |
| EPIC-010 | C-1 FEAT-112 ref | applied | Fixed to FEAT-162/STORY-387 and FEAT-177/STORY-423 |
| EPIC-010 | C-2 Org contacts | applied | Already added in EPIC-001 / EPIC-003 passes |
| EPIC-010 | C-3 AlertRule.owner_user_id | applied | Added in EPIC-009 pass |
| EPIC-010 | C-3 Webhook.owner_user_id | applied | Added field |
| EPIC-010 | C-3 Model.paused | applied | Added "paused" to Model.status enum; STORY-276 uses status |
| EPIC-010 | C-3 ResidencyConfig pin fields | applied | Added pinned_at, pinned_by_user_id, source |
| EPIC-010 | C-3 AuditLog hash chain | applied | Added prev_hash, hash, signing_key_id |
| EPIC-010 | C-4 FEAT-133 revocation | deferred | Needs product input on saas/self_hosted split |
| EPIC-010 | C-5 SCIM cascade | applied | STORY-252 revokes Session/TrustedBrowser/Invite + fallback chain for reassignment |
| EPIC-010 | M-1 FEAT-107 billing mode split | deferred | Structural feature split needed |
| EPIC-010 | M-2 ResidencyConfig.migration_ends_at | applied | Removed field |
| EPIC-010 | M-3 dual IP allowlist | deferred | Structural; needs product input |
| EPIC-010 | M-4 FEAT-127 DR role split | deferred | Needs product input |
| EPIC-010 | M-5 AuditLog hash chain | applied | Covered by C-3 |
| EPIC-010 | M-6 STORY-275 typed confirm | applied | AC-003 and API body now require confirm_slug |
| EPIC-010 | M-7 GeoIP fail-open default | deferred | Needs product input |
| EPIC-010 | M-8 team-lead fallback chain | applied | Covered by C-5 |
| EPIC-010 | m-1..m-9 minors | deferred | Editorial |
| EPIC-010 | X-1..X-7 cross-epic | deferred | Mostly need product input |
| EPIC-011 | C1 STORY-312 15ms p95 | applied | Replaced with baseline reference |
| EPIC-011 | C2 STORY-313 TTFT | applied | Split into gateway-added latency + upstream TTFT |
| EPIC-011 | C3 STORY-341 per-chunk 10ms | applied | Now hot-path budget per baseline |
| EPIC-011 | C4 STORY-324/326 2ms | applied | Tightened to 250µs p95 as sub-budget |
| EPIC-011 | C5 shared_limiters FEAT-142 → FEAT-141 | applied | Completed baseline fix |
| EPIC-011 | C6 token-bucket → sliding-window | applied | STORY-325 aligned with baseline |
| EPIC-011 | C7 streaming retry | applied | STORY-313/327 and baseline all unified: fallback may reissue full request, no same-target retry after bytes |
| EPIC-011 | C8 STORY-385 ref | applied | STORY-394 → STORY-382 |
| EPIC-011 | C9 STORY-386 FEAT-101 | applied | Done in EPIC-009 pass |
| EPIC-011 | C10 STORY-327 STORY-134 | applied | Changed to STORY-329 |
| EPIC-011 | M1 failover ownership | deferred | Needs product decision |
| EPIC-011 | M2 pipeline ordering feature | deferred | Needs new feature |
| EPIC-011 | M3 FEAT-160 → EPIC-003 | deferred | Structural epic move |
| EPIC-011 | M4 provider API split | deferred | Epic restructure |
| EPIC-011 | M6 FEAT-148 residency check | applied | STORY-345 AC-001 now requires region match |
| EPIC-011 | M7 mode declarations | applied | Added mode:both to FEAT-158/159/160 |
| EPIC-011 | M8 STORY-386 AlertRule fields | applied | Rewritten to use category/scope/metric |
| EPIC-011 | M9 STORY-323 rejection metadata | deferred | Needs product input |
| EPIC-011 | M10 STORY-377 fallback condition | applied | Conditioned on Org.security_contact IS NULL |
| EPIC-011 | M11 FEAT-143/149 overlap | deferred | Needs product decision |
| EPIC-011 | m9 STORY-340 60s → 30s | applied | References config_hot_reload |
| EPIC-011 | m1..m12 other minors | deferred | Editorial |
| EPIC-011 | X1..X7 cross-epic | deferred | Need coordination/product input |
| EPIC-012 | C1 SupportTicket fields | applied | Added destination, redaction_profile, antirion_ticket_id |
| EPIC-012 | C2 ResidencyConfig.mode/source | applied | Added mode field (source added previously) |
| EPIC-012 | C3 HelpArticle fields | applied | Added view_count, local_anchor; added HelpArticlePin model |
| EPIC-012 | C4 Notification.kind | applied | Extended enum with maintenance/incident/license/license_violation/platform_notice |
| EPIC-012 | C5 FEAT-167 vs FEAT-170 overlap | deferred | Structural; needs product decision |
| EPIC-012 | C6 FEAT-112 wrong cross-ref | applied | Already fixed in EPIC-010 pass |
| EPIC-012 | M1 FEAT-173 widget ref | applied | FEAT-164 → FEAT-163 |
| EPIC-012 | M2 StatusPageIncident ↔ PlatformIncident | applied | Added platform_incident_id FK |
| EPIC-012 | M3 STORY-388 residency dep | applied | depends_on STORY-387 + AC guard |
| EPIC-012 | M4 WorkerJob.owner_org_id | applied | Added nullable FK:Org |
| EPIC-012 | M5 mode:both on FEAT-162..169 | applied (ex. 167) | Added mode:both to FEAT-162/163/164/165/166/168/169 |
| EPIC-012 | M6 STORY-391/392 mode ACs | deferred | Needs product input |
| EPIC-012 | M7 STORY-396 mode split | deferred | Needs product decision |
| EPIC-012 | M8 LegalDocument | applied | Added LegalDocument model |
| EPIC-012 | M9 FEAT-166 air-gapped AC | deferred | New stories needed |
| EPIC-012 | M10/M11 STORY-401 pricing ACs | deferred | Needs product input |
| EPIC-012 | m5 STORY-392 5min → 30s | applied | Aligned with FEAT-173 / hot-reload SLA |
| EPIC-012 | m1..m8 other minors | deferred | Editorial |
| EPIC-012 | X1..X3 cross-epic | deferred | Needs coordination |
| EPIC-013 | C1 AuditLog operator-plane | applied | org_id nullable; added actor_plane field |
| EPIC-013 | C2 Org.state suspension | applied | Added state/suspension_reason/suspended_at/suspended_by_user_id |
| EPIC-013 | C3 Org contact fields | applied | Done in EPIC-001/EPIC-003 passes |
| EPIC-013 | C4 Antirion staff principal | deferred | Needs product decision on OperatorPrincipal |
| EPIC-013 | C5 STORY-422 ref | applied | STORY-414 → STORY-411 |
| EPIC-013 | C6 /api/bootstrap collision | applied | Install endpoint moved to /api/operator/install/bootstrap |
| EPIC-013 | C7 security channel tenant-isolation | applied | FEAT-179 description reconciled with notifications_model |
| EPIC-013 | C8 License.tier | applied | Added enterprise|cloud_assist enum |
| EPIC-013 | C9 SupportTicket fields | applied | Added severity/assignee_user_id/install_id/triaged_at/sla_due_at; status enum extended |
| EPIC-013 | M1 FEAT-172 description | applied | "saas mode only" → "both modes" |
| EPIC-013 | M2 FEAT-181/182 mode tag | deferred | Needs baseline schema upgrade |
| EPIC-013 | M3 STORY-403 persona | applied | Canonical platform operator wording |
| EPIC-013 | M4 /antirion/* routes | deferred | Needs gating contract update |
| EPIC-013 | M5 IncidentTimelineEntry | applied | Added model |
| EPIC-013 | M6 LicenseIncident.renewal_confirmation_id | applied | Added field |
| EPIC-013 | M7/M8/M9 cross-epic ACs | deferred | Need coordination |
| EPIC-013 | M10 STORY-413 title | applied | Dropped "and budgets" |
| EPIC-013 | M11 PlatformIncident.created_by | deferred | Ties to C4 |
| EPIC-013 | minor m1..m9 | deferred | Editorial |
| EPIC-013 | X1..X8 cross-epic | deferred | Need coordination |
| EPIC-001 (2026-04-20) | C-1 Team.slug | applied | Added Team.slug (unique within (org_id, slug)); STORY-013 generates it on create |
| EPIC-001 (2026-04-20) | C-2 Team.deleted_at | applied | Added Team.deleted_at; STORY-017 AC-001 states row is retained with deleted_at set |
| EPIC-001 (2026-04-20) | M-1 FEAT-012 rejection AC | applied | Added STORY-012 AC-004 for platform_admin saas-mode rejection with AuditLog role.assignment_rejected |
| EPIC-001 (2026-04-20) | M-2 STORY-015 cross-team move | applied | AC-002 now records team.member.move AuditLog on source and destination teams |
| EPIC-001 (2026-04-20) | M-3 STORY-020 MFA reset notification | applied | Added Notification kind=security (mfa.reset) to target user; added Notification to data_models; FEAT-102 channel routing non_functional |
| EPIC-001 (2026-04-20) | M-4 STORY-022 audience recording | applied | AC-001/AC-002 now record resolved audience list |
| EPIC-001 (2026-04-20) | M-5 STORY-022 unflag notification | applied | AC-002 now emits user.flag_cleared Notification to same audience |
| EPIC-001 (2026-04-20) | M-6 STORY-018 typed confirmation | deferred | Product policy decision on destructive_action_confirmation_policy scope |
| EPIC-001 (2026-04-20) | m-1 STORY-012 User.role wording | applied | Replaced "The Role is unchanged"/"the role is unchanged" with "User.role is unchanged" |
| EPIC-001 (2026-04-20) | m-2 STORY-016 Team.members | applied | Replaced "Team.members" with User.team_id null transition |
| EPIC-001 (2026-04-20) | m-3 Invite.status enum | applied | Added description pending\|accepted\|revoked\|expired |
| EPIC-001 (2026-04-20) | m-4 STORY-005 non_functional | applied | Dropped generic audit/reload lines; added JIT-specific guarantees |
| EPIC-001 (2026-04-20) | m-5 STORY-026 ApiKey.type | applied | AC-001 now issues ApiKey with type="service" |
| EPIC-001 (2026-04-20) | m-6 STORY-023 LoginAttempt.user_id | applied | AC-001 sets user_id to the locked user |
| EPIC-001 (2026-04-20) | m-7 STORY-004 SSO precedence | applied | non_functional cites Org.sso_enforced AND SsoConfig.require_for_domains |
| EPIC-001 (2026-04-20) | m-8 STORY-007 role validation | applied | Added AC-003 rejecting invites with unresolvable role (unknown or saas platform_admin) |
| EPIC-001 (2026-04-20) | X-1 STORY-018/019 EPIC-003 cross-ref | applied | Added non_functional referencing FEAT-022/FEAT-024 ownership |
| EPIC-001 (2026-04-20) | X-2 STORY-020 FEAT-015 cross-ref | applied | Added non_functional note citing EPIC-002 FEAT-015 |
| EPIC-001 (2026-04-20) | X-3 STORY-022/023/024 FEAT-102 cross-ref | applied | Added channel-delivery non_functional line on all three stories |
| EPIC-001 (2026-04-20) | X-4 STORY-025 SsoConfig cross-ref | applied | Added non_functional citing EPIC-010 FEAT-110 SSO config ownership |
| EPIC-001 (2026-04-20) | X-5 FEAT-012 install-mode cite | applied | Description cites project.deployment_modes resolved at install time by EPIC-013 |
| EPIC-001 (2026-04-20) | U-1 SessionPolicy admin-edit surface | deferred | Needs new feature (account-security policy or EPIC-010 admin surface); product input |
| EPIC-001 (2026-04-20) | U-2 Session idle/absolute enforcement | deferred | Needs new story under FEAT-003; product input on where enforcement lives |
| EPIC-001 (2026-04-20) | U-3 Transactional email delivery | deferred | New feature needed; provider/templates/bounces/retries unspecified |
| EPIC-001 (2026-04-20) | U-4 TrustedBrowser list/revoke | deferred | Needs new story under FEAT-015 (EPIC-002) + cascade spec; product input |
| EPIC-001 (2026-04-20) | U-5 platform_admin seeding path | deferred | Needs new feature in EPIC-013 install wizard (FEAT-177) or FEAT-012; product input |
| EPIC-001 (2026-04-20) | U-6 service-account rotation/delete notification | applied | Added Notification AC + data_models + FEAT-102 non_functional on STORY-028 and STORY-029 |
| EPIC-001 (2026-04-20) | U-7 LoginAttempt retention | deferred | Needs RetentionConfig.login_attempts_days + sweep worker (EPIC-010); product input |
| EPIC-001 (2026-04-20) | U-8 User.status=inactive lifecycle | deferred | Either extend FEAT-008 with dormancy sweep or remove enum value; product input |
| EPIC-002 (2026-04-20) | C-1 STORY-046 AuditLog | applied | AC-001 now writes user.deletion.requested AuditLog with audience + channel per notifications_model |
| EPIC-002 (2026-04-20) | C-2 PersonalToken revoke | applied | STORY-042 AC-002 soft-deletes via status=revoked + revoked_at; token_hash nulled. PersonalToken.revoked_at added; token_hash nullable. |
| EPIC-002 (2026-04-20) | C-3 FEAT-021 collapse into FEAT-003 | deferred | Structural collapse still requires product decision on feature ownership (partial fix already landed) |
| EPIC-002 (2026-04-20) | M-1 STORY-045 filter | applied | AC-001 + non_functional now include user_id match OR email_attempted match |
| EPIC-002 (2026-04-20) | M-2 STORY-046 canonical roles | applied | AC-001 uses canonical audience (a) + (c) Org.owner_user_id with fallback chain |
| EPIC-002 (2026-04-20) | M-3 STORY-039 trusted-browser clear audit | applied | AC-002 now writes user.trusted_browsers.cleared AuditLog + Notification; data_models extended |
| EPIC-002 (2026-04-20) | M-4 EPIC-002 notification consistency | applied | STORY-041/046/047 standardized on Notification + FEAT-102 pattern |
| EPIC-002 (2026-04-20) | M-5 STORY-047 cancellation notification | applied | AC-001 now emits account.deletion_cancelled Notification with same audience as STORY-046 |
| EPIC-002 (2026-04-20) | M-6 STORY-035 EmailVerificationToken | applied | AC-002 names EmailVerificationToken with purpose=email_change; data_models includes it |
| EPIC-002 (2026-04-20) | M-7 STORY-043 quiet-hours row shape | deferred | Global-vs-per-event still requires product input |
| EPIC-002 (2026-04-20) | M-8 FEAT-015 trusted-browser list/revoke | deferred | New story/ACs needed — product input |
| EPIC-002 (2026-04-20) | M-9 STORY-041 MFA factor Notification | applied | AC-001 uses Notification kind=security (account.mfa_factor_removed) via FEAT-102; Notification added to data_models |
| EPIC-002 (2026-04-20) | M-10 destructive_action_confirmation_policy | applied | Policy extended to include "delete personal account" |
| EPIC-002 (2026-04-20) | m-1 STORY-035 email collision AC | applied | Added AC-005 covering 409 path |
| EPIC-002 (2026-04-20) | m-2 STORY-035 timezone/language AC | applied | Added AC-006 asserting round-trip of timezone/language |
| EPIC-002 (2026-04-20) | m-3 STORY-037 theme switch NFR | applied | Split the shared line into theme/density-immediate vs other-fields-next-request |
| EPIC-002 (2026-04-20) | m-4 STORY-042 scope narrowing | applied | Added AC-005 re-evaluating scopes on use + AuditLog narrowing |
| EPIC-002 (2026-04-20) | m-5 STORY-044 failure state AC | applied | Added AC-004 covering DataExportJob.status transition to "failed" after 24h |
| EPIC-002 (2026-04-20) | m-6 STORY-044 channel attempt | applied | AC-003 now records audience list AND channel attempt |
| EPIC-002 (2026-04-20) | m-7 FEAT-021 priority alignment | deferred | Ties to C-3 structural collapse |
| EPIC-002 (2026-04-20) | m-8 STORY-048/006 audit parity | deferred | Ties to C-3 |
| EPIC-002 (2026-04-20) | m-9 STORY-040 first-factor primary | applied | AC-001 states first factor gets is_primary=true; subsequent factors default false |
| EPIC-002 (2026-04-20) | X-1 FEAT-021 ↔ FEAT-003 | deferred | Ties to C-3 |
| EPIC-002 (2026-04-20) | X-2 STORY-043/044 FEAT-102 depends_on | applied | Added depends_on STORY-232 to both stories |
| EPIC-002 (2026-04-20) | X-3 STORY-044 FEAT-167/FEAT-179 | deferred | Needs canonical cross-epic reference convention |
| EPIC-002 (2026-04-20) | X-4 STORY-046 owner-handoff cross-ref | applied | AC-002 error message now references STORY-012 in-line |
| EPIC-002 (2026-04-20) | U-1 account-deletion cutover worker | deferred | Needs new feature under FEAT-020; worker spec + notifications/audit paths |
| EPIC-002 (2026-04-20) | U-2 recovery-code consume path | deferred | Needs new story under FEAT-001 or FEAT-015; product input |
| EPIC-002 (2026-04-20) | U-3 PersonalToken.last_used_at write path | deferred | Auth pipeline concern; needs cross-epic home |
| EPIC-002 (2026-04-20) | U-4 MFA primary toggle | deferred | Needs new story under FEAT-015; product input on transaction/UX |
| EPIC-002 (2026-04-20) | U-5 avatar image lifecycle | deferred | Size/content-type/remove ACs + storage policy needed; product input |
| EPIC-002 (2026-04-20) | U-6 UserPrefs row seeding | deferred | Needs new AC/story covering defaults and seeding event |
| EPIC-002 (2026-04-20) | U-7 account-deletion cascade for user-owned resources | deferred | Needs product policy on ApiKey/Team.lead/AlertRule/Webhook/PromptTemplate cascade |
| EPIC-002 (2026-04-20) | U-8 LoginAttempt retention | deferred | Needs RetentionConfig class + sweep worker (EPIC-010); product input |
| EPIC-003 (2026-04-20) | C1 STORY-057 AlertEvent.type | applied | AC-002 rewritten to use severity/source/fingerprint (no .type field) |
| EPIC-003 (2026-04-20) | M1 STORY-057 status=degraded on 401 | applied | AC-002 now sets BYOKCredential.status="invalid" for auth failure |
| EPIC-003 (2026-04-20) | M2 Approval.kind collision | applied | Added "break-glass-key-create" enum value; STORY-377 switched to new kind |
| EPIC-003 (2026-04-20) | M3 rotate_policy_days editable | deferred | Needs new story under FEAT-025; product input |
| EPIC-003 (2026-04-20) | M4 ApiKey.scopes materialization race | deferred | Needs product decision between derived and materialized representation |
| EPIC-003 (2026-04-20) | M5 STORY-069 Org.owner → owner_user_id | applied | AC-001 now names Org.owner_user_id |
| EPIC-003 (2026-04-20) | m1 STORY-068 "generated label" | applied | Replaced with "generated name" |
| EPIC-003 (2026-04-20) | m2 STORY-050 grace-end AuditLog | applied | AC-002 now writes AuditLog with actor_type=system and action=apikey.rotation.grace_end |
| EPIC-003 (2026-04-20) | m3 ApiKey.rotation_due dead field | deferred | Needs product decision to drop or to add a writer |
| EPIC-003 (2026-04-20) | m4 KeyAnomaly.severity enum | applied | Added info\|warn\|crit description; STORY-055 uses "warn" |
| EPIC-003 (2026-04-20) | m5 persona drift | applied | STORY-054/055 → security officer; STORY-067/068 → platform operator |
| EPIC-003 (2026-04-20) | m6 FEAT-028 mode tag | applied | Added mode: both |
| EPIC-003 (2026-04-20) | m7 non_functional boilerplate | deferred | Broad editorial pass; out of scope for targeted round |
| EPIC-003 (2026-04-20) | m8 BYOK rate-limit duplicate | deferred | Needs product decision between BYOKCredential fields vs ProviderRateLimit rows |
| EPIC-003 (2026-04-20) | X1 FEAT-160 break-glass | applied | Resolved by M2 (new Approval.kind) |
| EPIC-003 (2026-04-20) | X2 STORY-323 edge auth alignment | deferred | Ties to M4 |
| EPIC-003 (2026-04-20) | U1 BYOK rotation-grace expiry job | deferred | Needs new story under FEAT-025; analogous to STORY-063 |
| EPIC-003 (2026-04-20) | U2 rotation-policy config surface | deferred | Ties to M3 |
| EPIC-003 (2026-04-20) | U3 BYOK upstream-secret leak-scan | deferred | Needs new feature or extension of FEAT-028 |
| EPIC-003 (2026-04-20) | U4 KeyAnomaly detector config | deferred | Needs scope decision for FEAT-041 |
| EPIC-003 (2026-04-20) | U5 ApiKeyExpiryNotice dedupe/quiet-hours | deferred | Needs new story under FEAT-026 |
| EPIC-004 (2026-04-20) | C1 STORY-089 RBAC/audit/notification | applied | Added AC-003/AC-004 for scope + AuditLog + FEAT-102 routing; data_models extended |
| EPIC-004 (2026-04-20) | C2 STORY-102 tool-use data/api | applied | Added api block + ToolInvocation to data_models |
| EPIC-004 (2026-04-20) | C3 STORY-103 streaming rollup | applied | MetricSeries extended with client_cancelled_count/mid_stream_dropped_count/ttft_p50/ttft_p95; STORY-103 api block added + MetricSeries in data_models |
| EPIC-004 (2026-04-20) | C4 FEAT-033 → FEAT-099/100/102 bridge | deferred | Needs new story; product input on Anomaly→AlertEvent synthesis |
| EPIC-004 (2026-04-20) | C5 ToolInvocation producer | deferred | Needs new story under FEAT-146; coordination with C4 |
| EPIC-004 (2026-04-20) | M1 mode declarations | applied | Added mode:both to FEAT-029..FEAT-044; FEAT-033 description updated for saas/self_hosted |
| EPIC-004 (2026-04-20) | M2 FEAT-031 tools/flags drill-in | deferred | Carried from prior audit; needs product input |
| EPIC-004 (2026-04-20) | M3 STORY-072 API Key/User filter UI | applied | Added AC-006/AC-007 + ApiKeyPicker/UserPicker components |
| EPIC-004 (2026-04-20) | M4 STORY-099 pointer-only | deferred | Structural; needs product decision to delete or fold in |
| EPIC-004 (2026-04-20) | M5 FEAT-043/044 api blocks | applied | Added api blocks for STORY-102 and STORY-103 |
| EPIC-004 (2026-04-20) | M6 STORY-077 time-range dep | applied | Added depends_on STORY-086 |
| EPIC-004 (2026-04-20) | M7 FEAT-039 request share | deferred | Needs new AC/story; product input |
| EPIC-004 (2026-04-20) | m1 non_functional drift | deferred | Broad editorial pass |
| EPIC-004 (2026-04-20) | m2 STORY-094 CSV export | deferred | Ties to C1 hardening path |
| EPIC-004 (2026-04-20) | m3 STORY-082 CacheEntry | applied | Added CacheEntry and MetricSeries to data_models |
| EPIC-004 (2026-04-20) | m4 STORY-086 export NFR | applied | Dropped unrelated export NFR |
| EPIC-004 (2026-04-20) | m5 STORY-085 ui block | applied | Added ui block with AnomalyPanel/AnomalyDrawer |
| EPIC-004 (2026-04-20) | m6 STORY-095 audit note | applied | Dropped rollup NFR; added note about audit via STORY-096/097 |
| EPIC-004 (2026-04-20) | m7 AnomalyDetector owner/updated_by | applied | Added owner_user_id, updated_by_user_id; description notes tenant-scoped management |
| EPIC-004 (2026-04-20) | X1 FEAT-033 → FEAT-176 cross-ref | applied | FEAT-033 description now cross-refs FEAT-176 |
| EPIC-004 (2026-04-20) | X2 STORY-338 model_id/provider_id | applied | Renamed span attrs |
| EPIC-004 (2026-04-20) | X3 cache savings dual emitter | deferred | Needs product decision on canonical emitter |
| EPIC-004 (2026-04-20) | R1..R4 missing refs | deferred | Tie to C4/C5/M7/m2 |
| EPIC-004 (2026-04-20) | U1..U8 missing features | deferred | Each requires net-new feature; product input |
| EPIC-005 (2026-04-20) | C1 STORY-106 wrong ref | applied | STORY-379/380 → STORY-382 / STORY-384 |
| EPIC-005 (2026-04-20) | C2 mid-stream retry config | deferred | Needs new story under FEAT-050/051; product input |
| EPIC-005 (2026-04-20) | C3 RoutingRule sub-schemas | deferred | Structural model change; product input (carried from prior pass) |
| EPIC-005 (2026-04-20) | M1 canary windows | deferred | Carried from prior pass |
| EPIC-005 (2026-04-20) | M2 missing strategy stories | deferred | Carried from prior pass |
| EPIC-005 (2026-04-20) | M3 Team.owner regression | applied | STORY-129 AC-001 now names Team.lead_user_id |
| EPIC-005 (2026-04-20) | M4 CatalogPolicy precedence | deferred | Carried from prior pass |
| EPIC-005 (2026-04-20) | M5 fallback naming collision | deferred | Carried from prior pass |
| EPIC-005 (2026-04-20) | M6 auto-promote chain mutation | deferred | Carried from prior pass |
| EPIC-005 (2026-04-20) | M7 cache/safety cross-epic | deferred | Carried from prior pass |
| EPIC-005 (2026-04-20) | M8 catalog sync | deferred | Carried from prior pass |
| EPIC-005 (2026-04-20) | M9 FEAT-058/059 placement | deferred | Structural; needs product input |
| EPIC-005 (2026-04-20) | m1 STORY-117 hero canary fields | deferred | Product input on hero response shape |
| EPIC-005 (2026-04-20) | m2 STORY-114 human_description | deferred | Needs decision derived-vs-persisted |
| EPIC-005 (2026-04-20) | m3 STORY-119 divergence model | deferred | Ties to U2 |
| EPIC-005 (2026-04-20) | m4 STORY-120 drawer copy | deferred | Ties to M2 |
| EPIC-005 (2026-04-20) | m5 CatalogPolicy.allowed_regions | deferred | Needs new story in EPIC-009 residency |
| EPIC-005 (2026-04-20) | m6 STORY-108 BYOK preflight | applied | Added warn-only AC-003 |
| EPIC-005 (2026-04-20) | m7 STORY-129 weekly reminder audience | applied | non_functional now routes via FEAT-102 with AC-001 audience |
| EPIC-005 (2026-04-20) | m8 STORY-105 fallback wording | applied | "fallback chain" → "fallback chain(s) of routing rules targeting this model" |
| EPIC-005 (2026-04-20) | m9 STORY-121 runtime AC | applied | AC-002 rewritten to config-side only; runtime delegated to FEAT-142 |
| EPIC-005 (2026-04-20) | X1..X5 cross-epic | deferred | Tied to other deferred items |
| EPIC-005 (2026-04-20) | U1..U8 missing features | deferred | Each requires net-new feature; product input |
| EPIC-006 (2026-04-20) | C-1 STORY-148 FK chain | applied | Removed broken ApiKey.owner fallback; kept byok_credential_id with (org_id, provider_id) coarser fallback; added depends_on STORY-056 |
| EPIC-006 (2026-04-20) | C-2 CacheConfig keying | applied | Added org_id, scope, scope_id to CacheConfig schema |
| EPIC-006 (2026-04-20) | C-3 latency NFR drift | applied | All 11 stale NFR lines swept to 500µs p95 sub-budget |
| EPIC-006 (2026-04-20) | C-4 dead eviction reasons | applied (partial) | manual_purge now fires from STORY-275; safety_policy_change deferred (needs EPIC-007 story) |
| EPIC-006 (2026-04-20) | C-5 cache write on block | applied | STORY-142 AC-003 forbids cache write when SafetyEvent.action=block |
| EPIC-006 (2026-04-20) | C-6 streaming × cache | deferred | Needs new story under FEAT-060; streamed replay framing undefined |
| EPIC-006 (2026-04-20) | C-7 per-backend key formula | applied | STORY-142 AC-001 now splits formula by backend |
| EPIC-006 (2026-04-20) | C-8 STORY-148 timing | applied | Purge fires on BYOKCredential.status=revoked after grace |
| EPIC-006 (2026-04-20) | M-1 STORY-152 override_value | applied | API body now uses json type matching model |
| EPIC-006 (2026-04-20) | M-2 STORY-156 GET endpoint | applied | Added GET /api/cache/configs/:id/evictions |
| EPIC-006 (2026-04-20) | M-3 CacheConfig PATCH path | applied | Unified STORY-142 to /api/cache/configs/:id |
| EPIC-006 (2026-04-20) | M-4 CacheOverride CRUD | applied | STORY-152 now lists GET/PATCH/DELETE endpoints |
| EPIC-006 (2026-04-20) | M-5 STORY-148 depends_on | applied | Added STORY-056 dependency |
| EPIC-006 (2026-04-20) | M-6 STORY-148 Notification | applied | AC-001 now emits Notification kind=security to Org.security_contact |
| EPIC-006 (2026-04-20) | M-7 STORY-149 Notification | applied | AC-001 now emits Notification kind=compliance to Org.privacy_officer |
| EPIC-006 (2026-04-20) | M-8 STORY-151 audit+notify | applied | AC-003 writes AuditLog and Notification for drop-user/drop-team actions |
| EPIC-006 (2026-04-20) | M-9 InvalidationRule org_id | applied | Added org_id + team_id + scope enum description |
| EPIC-006 (2026-04-20) | M-10 CacheConfig org_id | applied | Added directly (transitive via Model.org_id was fragile) |
| EPIC-006 (2026-04-20) | M-11 SemanticCacheConfig org_id | applied | Added |
| EPIC-006 (2026-04-20) | M-12 PromptSegment org_id | applied | Added |
| EPIC-006 (2026-04-20) | M-13 CacheOverride org_id | applied | Added |
| EPIC-006 (2026-04-20) | M-14 STORY-150 scope enum | applied | non_functional notes scope enum and server-derived org_id |
| EPIC-006 (2026-04-20) | M-15 STORY-147 typed-slug unconditional | applied | Dropped >100 threshold from AC-002 |
| EPIC-006 (2026-04-20) | N-3 hit_rate scale | applied | Added hit_rate_scale field to STORY-153 response |
| EPIC-006 (2026-04-20) | N-4 segment_ids uuid | applied | STORY-154 body uses uuid[] |
| EPIC-006 (2026-04-20) | N-7 STORY-152 ui block | applied | Added OverrideTable/OverrideForm components |
| EPIC-006 (2026-04-20) | N-8 STORY-155 400 error | applied | Added 400 to errors list |
| EPIC-006 (2026-04-20) | X-2 STORY-275 CacheEvictionEvent | applied | AC-002 now writes batched roll-up with reason=manual_purge |
| EPIC-006 (2026-04-20) | N-1/N-2/N-5/N-6/N-10/N-11 minors | deferred | Editorial / product input |
| EPIC-006 (2026-04-20) | X-1/X-3/X-4/X-5/X-6/X-7 cross-epic | deferred | Need new stories / cross-epic coordination |
| EPIC-006 (2026-04-20) | R-1/R-2/R-5/R-6/R-7/R-10 missing refs | deferred | New stories / event catalog work |
| EPIC-006 (2026-04-20) | U-1..U-9 missing features | deferred | Each requires net-new feature; product input |
| EPIC-007 (2026-04-20) | C-1 STORY-173 template field | applied | Now writes DetectionRule.installed_template_id and SafetyRuleVersion.type=template_install |
| EPIC-007 (2026-04-20) | C-2 PiiCategory org-less | deferred | Needs structural choice between PiiCategory.org_id vs new PiiPolicy model |
| EPIC-007 (2026-04-20) | C-3 Request.prompt cleartext | applied | Field now describes the conditional-nullability invariant |
| EPIC-007 (2026-04-20) | C-4 SafetyAllowanceGrant model | deferred | Needs new model; product input |
| EPIC-007 (2026-04-20) | C-5 false_positive field | applied | SafetyEvent.review_status enum now includes false_positive; STORY-167 AC-001 uses it |
| EPIC-007 (2026-04-20) | C-6 STORY-161 status_label | applied | AC-001 now sets Request.status_label = "safety_blocked" |
| EPIC-007 (2026-04-20) | M-1 RedactionVaultEntry lifecycle | applied | Added expires_at, retention_days, rotated_at, cmk_binding_id, deleted_at |
| EPIC-007 (2026-04-20) | M-2 EPIC-007 description | applied | Expanded to enumerate all 13 features + mode statement |
| EPIC-007 (2026-04-20) | M-3 review_status enum | applied | Added description covering unreviewed\|reviewed\|false_positive\|escalated |
| EPIC-007 (2026-04-20) | M-4 mode declarations | applied | Added mode: both to FEAT-069..FEAT-081 |
| EPIC-007 (2026-04-20) | M-5 STORY-164 reviewed_by_user_id | applied | AC-001 now sets review_status, reviewed_at, reviewed_by_user_id |
| EPIC-007 (2026-04-20) | M-6 STORY-174 cache TTL | applied | 60s → 15s + explicit invalidation hooks |
| EPIC-007 (2026-04-20) | M-7 action precedence | applied | FEAT-073 description now declares allow > block > redact > flag |
| EPIC-007 (2026-04-20) | M-8 override matrix | applied | FEAT-074 description now covers any transition with audit reason |
| EPIC-007 (2026-04-20) | M-9 STORY-178 trust_and_safety | applied | Dropped T&S fanout; uses canonical fallback chain |
| EPIC-007 (2026-04-20) | M-10 STORY-157 filter enums | applied | API note pins enum sources |
| EPIC-007 (2026-04-20) | M-11 STORY-166 soft-delete | applied | AC-002 now sets deleted_at and filters from active pickers |
| EPIC-007 (2026-04-20) | M-12 STORY-168 Drafts filter | applied | STORY-165 gains GET endpoint; STORY-168 gains ui block with DraftsFilter |
| EPIC-007 (2026-04-20) | M-13 STORY-171 scope enum | applied | API note pins last_24h\|last_7d\|sample |
| EPIC-007 (2026-04-20) | M-14 STORY-163 CSV guards | applied | AC-001 requires safety.export scope + AuditLog + prompt_redacted-only |
| EPIC-007 (2026-04-20) | m-1 FEAT-070 12 categories | deferred | Needs PII seeding feature (ties to U-5) |
| EPIC-007 (2026-04-20) | m-2 STORY-160 NFRs | applied | Replaced detector boilerplate with config_hot_reload SLA line |
| EPIC-007 (2026-04-20) | m-3 STORY-159 audience resolution | deferred | FEAT-102 dispatch already implicit |
| EPIC-007 (2026-04-20) | m-4 SafetyPosture descriptions | deferred | Ties to U-2 (aggregator spec) |
| EPIC-007 (2026-04-20) | m-5 STORY-183 RBAC | deferred | Needs product input on operator visibility |
| EPIC-007 (2026-04-20) | m-6 template_install enum | applied | STORY-173 AC-001 writes SafetyRuleVersion |
| EPIC-007 (2026-04-20) | m-7 STORY-177 approve Notification | applied | AC-001 now emits Notification to requester |
| EPIC-007 (2026-04-20) | X-1..X-7 cross-epic | deferred | Need coordination |
| EPIC-007 (2026-04-20) | MR-1..MR-5 missing models | deferred | New models needed |
| EPIC-007 (2026-04-20) | U-1..U-8 missing features | deferred | Need new features; product input |
| EPIC-008 (2026-04-20) | C1 BudgetEvent.summary | applied | STORY-198/199 now write BudgetEvent.title (model has title+body, not summary) |
| EPIC-008 (2026-04-20) | C2 Billing.trial_ends_at | applied | Added trial_ends_at, pending_plan, pending_effective_at to Billing; saas-only fields now nullable |
| EPIC-008 (2026-04-20) | C3 AlertEvent.type | applied | STORY-189 AC-001 uses source="budget"; U14 bridge deferred |
| EPIC-008 (2026-04-20) | C4 Request.metadata downgrade | applied | Added Request.downgraded, Request.original_model_id; STORY-190 AC-001 uses them |
| EPIC-008 (2026-04-20) | C5 approval_threshold_pct split | applied | Replaced with waiver_approval_threshold_pct and edit_approval_threshold_pct; STORY-187/197 updated |
| EPIC-008 (2026-04-20) | M1 STORY-189 AlertRule lifecycle | deferred | Needs U14 bridge (new feature); product input |
| EPIC-008 (2026-04-20) | M2 parallel paging surfaces | deferred | Resolved by U14 |
| EPIC-008 (2026-04-20) | M3 "an alert fires" without rule | deferred | Resolved by U14 |
| EPIC-008 (2026-04-20) | M4 BudgetForecast persistence | deferred | Needs new model + worker |
| EPIC-008 (2026-04-20) | M5 Request.cost → Budget.spent pipeline | deferred | Needs new feature (U1) |
| EPIC-008 (2026-04-20) | M6 STORY-188 atomicity | applied | Added transactional NFR + cycle/policy inheritance lines |
| EPIC-008 (2026-04-20) | M7 API path split | deferred | Structural; needs product input |
| EPIC-008 (2026-04-20) | M8 FEAT-091 overlap | deferred | Resolved by M2/U14 |
| EPIC-008 (2026-04-20) | M9 Billing lifecycle | applied | Added pending_plan + pending_effective_at; full PlanChange model still deferred |
| EPIC-008 (2026-04-20) | M10 Request.cost_center | applied | Added Request.cost_center field |
| EPIC-008 (2026-04-20) | M11 STORY-193 UI | applied | Added ui block with WaiverModal |
| EPIC-008 (2026-04-20) | M12 STORY-185 effective_cap | deferred | Needs product input on compute vs persisted |
| EPIC-008 (2026-04-20) | m1 overAllocated camelCase | applied | Now over_allocated |
| EPIC-008 (2026-04-20) | m2..m7, m9, m10 minor | deferred | Editorial / new worker specs |
| EPIC-008 (2026-04-20) | m8 FX override audit magnitude | applied | STORY-202 AC-002 now records prior_rate/override_rate/delta_pct |
| EPIC-008 (2026-04-20) | m11 overage dedup store | applied | Added Budget.last_overage_notified_at |
| EPIC-008 (2026-04-20) | m12 STORY-200 errors list | applied | Populated errors: [401,403,404] |
| EPIC-008 (2026-04-20) | X1..X7 cross-epic | deferred | Need coordination / U14 |
| EPIC-008 (2026-04-20) | U1..U16 uncited-required | deferred | Each requires net-new feature / worker; product input |
| EPIC-009 (2026-04-20) | C1 STORY-237 Incident model | applied | Rewrote ACs to use Incident; added publish AC and publish-gated StatusPageIncident flow |
| EPIC-009 (2026-04-20) | C2 PostMortem API body | applied | POST /api/alerts/:id/post-mortem now takes summary/timeline/impact/root_cause |
| EPIC-009 (2026-04-20) | C3 Slo.org_id nullable | applied | org_id now nullable; added scope_kind (tenant\|platform); STORY-244 AC-002 adds control-plane SLO |
| EPIC-009 (2026-04-20) | C4 AlertTimelineEntry enum | applied | STORY-243 now writes type "escalate" with escalation message |
| EPIC-009 (2026-04-20) | C5 AlertRuleSubscription | deferred | Needs new model; product input |
| EPIC-009 (2026-04-20) | C6 AlertEvent.source | applied (STORY-189) | Set in EPIC-008 pass; other generators deferred |
| EPIC-009 (2026-04-20) | M1 /ack vs /acknowledge | applied | STORY-228 path renamed to /ack to match STORY-234 |
| EPIC-009 (2026-04-20) | M2/M3/M4 STORY-232 coverage | deferred | Needs AlertRule.audience refactor + extra ACs |
| EPIC-009 (2026-04-20) | M5 STORY-237 participants routing | applied | AC-001 now routes through FEAT-102 with canonical audience role |
| EPIC-009 (2026-04-20) | M6 PagerDuty gating | deferred | Needs product input on air-gapped fallback |
| EPIC-009 (2026-04-20) | M7 FEAT-102 in-app inbox | applied | Description updated to include in-app inbox |
| EPIC-009 (2026-04-20) | M8 STORY-238 ActionItem API | applied | Added POST/PATCH endpoints; data_models extended |
| EPIC-009 (2026-04-20) | M9 STORY-237 publish AC | applied | AC-004 covers publish-to-status-page path |
| EPIC-009 (2026-04-20) | M10 release-gate | deferred | Needs new story under FEAT-174 |
| EPIC-009 (2026-04-20) | M11 control-plane SLO | applied | STORY-244 AC-002 defines control-plane-availability |
| EPIC-009 (2026-04-20) | M12 mode declarations | applied | Added mode: both to FEAT-099..FEAT-106 |
| EPIC-009 (2026-04-20) | m1 STORY-228 AuditLog | applied | AC-001/AC-002 now write AuditLog entries |
| EPIC-009 (2026-04-20) | m2..m11 minors | deferred | Editorial/new-story work |
| EPIC-009 (2026-04-20) | X1..X8 cross-epic | deferred | Most tie to C6 / release-gate / worker wiring |
| EPIC-009 (2026-04-20) | U1..U11 missing features | deferred | Net-new features (evaluation worker, dispatch worker, inbound PD receiver, subscription CRUD, platform rule authoring, etc.) |
| EPIC-010 (2026-04-20) | C-1 FEAT-107 mode split | deferred | Structural feature split needed; product input |
| EPIC-010 (2026-04-20) | C-2 CMK revocation contract | applied | STORY-309 AC-001 now mode-gated; NFR aligned with FEAT-133 description |
| EPIC-010 (2026-04-20) | C-3 DR mode gating | deferred | Structural; product input |
| EPIC-010 (2026-04-20) | C-4 IP allowlist triple-storage | applied | Removed ip_allowlist_enabled/ip_cidrs/org_ip_allowlist_mode from ApiAccessConfig; OrgIpAllowlist is canonical |
| EPIC-010 (2026-04-20) | C-5 FEAT-111 citation | applied | FEAT-107 → FEAT-121 |
| EPIC-010 (2026-04-20) | M-1 STORY-263 fallback | applied | Uses mode-aware fallback chain per project.notifications_model |
| EPIC-010 (2026-04-20) | M-2 STORY-296 audience | deferred | Needs product input on saas/self_hosted gating |
| EPIC-010 (2026-04-20) | M-3 STORY-280 audience | applied | AC-002 now cites STORY-263 audience resolution |
| EPIC-010 (2026-04-20) | M-4 ResidencyConfig.mode enum | applied | Description now asserts "always initial" |
| EPIC-010 (2026-04-20) | M-5 org_ip_allowlist_mode | applied | Field removed as part of C-4 |
| EPIC-010 (2026-04-20) | M-6 geoip fail-open | deferred | Product input on default |
| EPIC-010 (2026-04-20) | M-7 RetentionConfig classes | applied | Added audit_logs_days + safety_events_days |
| EPIC-010 (2026-04-20) | M-8 STORY-304 canonical roles | applied | Now resolves via FEAT-102 with role+contact audience |
| EPIC-010 (2026-04-20) | M-9 AuditSink.credentials | applied | Renamed to credentials_ciphertext with KMS description |
| EPIC-010 (2026-04-20) | M-10 ScimConflict model | applied | New model added; STORY-251 data_models extended |
| EPIC-010 (2026-04-20) | m-1..m-9 minors | deferred | Editorial / scope decisions |
| EPIC-010 (2026-04-20) | X-1..X-7 cross-epic | deferred | Need coordination |
| EPIC-010 (2026-04-20) | U-1..U-11 missing features | deferred | Signing-key lifecycle, restore ticket, cancel-delete, break-glass state, etc.; product input |
| EPIC-011 (2026-04-20) | C1 pipeline ordering | deferred | Needs new feature; product input |
| EPIC-011 (2026-04-20) | C2 ProviderHealth per-model | applied | Added nullable model_id; description clarifies scope |
| EPIC-011 (2026-04-20) | C3 STORY-329 dialect shape | applied | AC-002 now routes through FEAT-148 + shapes per STORY-346 |
| EPIC-011 (2026-04-20) | M1 FEAT-051 config-only | applied | STORY-121 AC-002 rewritten in EPIC-005 pass |
| EPIC-011 (2026-04-20) | M2 FEAT-160 move to EPIC-003 | deferred | Structural; product input |
| EPIC-011 (2026-04-20) | M3 FEAT-150..157 split | deferred | Structural epic decision |
| EPIC-011 (2026-04-20) | M4 FEAT-149 vs FEAT-143 overlap | deferred | Needs collapse decision |
| EPIC-011 (2026-04-20) | M5 STORY-323 rejection metadata | deferred | Needs product decision (Request row vs AccessLog) |
| EPIC-011 (2026-04-20) | M6 STORY-322 staged blob | applied | Replaced with FEAT-145 reference |
| EPIC-011 (2026-04-20) | M7 STORY-385 freshness | applied | Added "at most once per bucket" + 5s freshness |
| EPIC-011 (2026-04-20) | M8 STORY-339 /metrics | applied | Public listener now returns 401 without binding the path |
| EPIC-011 (2026-04-20) | M9 STORY-348..371 skeletal | deferred | Needs per-story expansion |
| EPIC-011 (2026-04-20) | m1..m8 minors | deferred | Editorial boilerplate, plus a couple of model-field extensions |
| EPIC-011 (2026-04-20) | X1..X7 cross-epic | deferred | Tied to pipeline ordering / structural items |
| EPIC-011 (2026-04-20) | U1..U9 missing features | deferred | Pipeline ordering, AccessLog, concurrency cap, readiness hydration, etc. |
| EPIC-012 (2026-04-20) | C1 STORY-398 HelpArticlePin | applied | AC-001 writes HelpArticlePin row; data_models extended |
| EPIC-012 (2026-04-20) | C2 STORY-398 view analytics | deferred | Needs new HelpArticleView event model / time-series |
| EPIC-012 (2026-04-20) | C3 STORY-396 TosAcceptance.required_version | applied | Rewrote to create LegalDocument with superseded_by_id linkage |
| EPIC-012 (2026-04-20) | C4 STORY-402 Notification.kind | applied | AC-001/AC-002 split per-mode; covers all 11 enum values |
| EPIC-012 (2026-04-20) | C5 FEAT-167 ambiguity | deferred | Structural; product input |
| EPIC-012 (2026-04-20) | C6 STORY-400 owner_org_id enforcement | applied | AC-001/AC-002 scoped to owner=me; AC-003 forbids cross-tenant |
| EPIC-012 (2026-04-20) | M1 FEAT-167 mode tag | deferred | Ties to C5 |
| EPIC-012 (2026-04-20) | M2 STORY-396 publisher role | applied | Narrative now describes mode-gated publisher |
| EPIC-012 (2026-04-20) | M3 STORY-391 self_hosted host | applied | AC-001 now references mode-correct host + no saas link surface |
| EPIC-012 (2026-04-20) | M4 STORY-391 platform-incident projection | applied | AC-002 rewired to STORY-412 projection |
| EPIC-012 (2026-04-20) | M5 STORY-401 mode cost composition | applied | AC-003 (saas) + AC-004 (self_hosted) |
| EPIC-012 (2026-04-20) | M6 STORY-401 NFR wording | applied | Forecast inputs read from local caches only |
| EPIC-012 (2026-04-20) | M7 PricingQuote.breakdown shape | applied | Description declares keys |
| EPIC-012 (2026-04-20) | M8 air-gapped help stories | deferred | New stories needed |
| EPIC-012 (2026-04-20) | M9 widget URL invariant | applied | STORY-391 AC-003 covers widget URL resolver |
| EPIC-012 (2026-04-20) | M10/M11 STORY-399 UI ambiguity | deferred | Ties to C5 |
| EPIC-012 (2026-04-20) | M12 FEAT-169 coverage | deferred | Needs new stories per source feature |
| EPIC-012 (2026-04-20) | M13 FEAT-162 depends_on FEAT-177 | applied | Added FEAT-177 to FEAT-162 depends_on |
| EPIC-012 (2026-04-20) | M14 STORY-402 depends_on | applied | Added STORY-412, STORY-418 |
| EPIC-012 (2026-04-20) | m1 STORY-389 FEAT-135 ref | applied | AC now cites FEAT-135 |
| EPIC-012 (2026-04-20) | m2 STORY-387 GET /api/residency | applied | Added read endpoint |
| EPIC-012 (2026-04-20) | m3..m9 minors | deferred | Editorial / new stories |
| EPIC-012 (2026-04-20) | X1..X3 cross-epic | deferred | Forecast route / Antirion sub-queue / invitee first-run |
| EPIC-012 (2026-04-20) | U1..U12 missing features | deferred | Partial via M2/C3/M5; rest need new features |
| EPIC-013 (2026-04-20) | C1 operator URL gating on /settings/fleet | deferred | Needs structural decision + STORY-408 extension |
| EPIC-013 (2026-04-20) | C2 STORY-407 saas role | deferred | Ties to C5 OperatorPrincipal |
| EPIC-013 (2026-04-20) | C3 /antirion/* gating | deferred | Needs baseline `installed_on` dimension |
| EPIC-013 (2026-04-20) | C4 FEAT-181/182 mode tag | deferred | Same baseline change |
| EPIC-013 (2026-04-20) | C5 OperatorPrincipal model | deferred | Structural; needs product input |
| EPIC-013 (2026-04-20) | M1 STORY-409 drill-in ref | applied | STORY-413 → STORY-410 |
| EPIC-013 (2026-04-20) | M2 STORY-409 gating ref | applied | STORY-411 → FEAT-171 (STORY-407/408) |
| EPIC-013 (2026-04-20) | M3 FleetDeployment nullability | applied | initiated_by/acting_user_id nullable + actor_type discriminator |
| EPIC-013 (2026-04-20) | M4 PhoneHomeCallLog inspect sample | deferred | Needs payload retention field + product input |
| EPIC-013 (2026-04-20) | M5 FEAT-170 vs FEAT-167 | deferred | Ties to C1 / EPIC-012 C5 |
| EPIC-013 (2026-04-20) | M6 STORY-412 data_models | applied | Added IncidentTimelineEntry |
| EPIC-013 (2026-04-20) | M7 AuditLog data_models gaps | applied | STORY-404/406/416/417 now list AuditLog |
| EPIC-013 (2026-04-20) | M8 PhoneHomeChannel.locked_by_mode | applied | Added field |
| EPIC-013 (2026-04-20) | M9 Org NPS/CSAT fields | applied | Added nps_latest, csat_latest |
| EPIC-013 (2026-04-20) | M10 STORY-425 claimed identifier | deferred | Needs PlatformAdminClaim model |
| EPIC-013 (2026-04-20) | M11 License.grace_window_days | applied | Added field |
| EPIC-013 (2026-04-20) | M12 STORY-423 SSO cross-ref | applied | Step 3 cross-refs FEAT-108 SsoConfig |
| EPIC-013 (2026-04-20) | m1 STORY-409 saas role | deferred | Ties to C5 |
| EPIC-013 (2026-04-20) | m2 STORY-411 EPIC-009 ref | applied | Changed to FEAT-102/FEAT-169 |
| EPIC-013 (2026-04-20) | m3 STORY-411 AC-003 name | applied | Renamed to "self_hosted hides suspend/resume" |
| EPIC-013 (2026-04-20) | m4 CrmOutreach nullability | applied | follow_up_at + follow_up_assignee_user_id nullable |
| EPIC-013 (2026-04-20) | m5 SupportTicket.install_id description | applied | Describes signed customer-install identity |
| EPIC-013 (2026-04-20) | m6 STORY-410 FEAT-120 ref | applied | Changed to AuditLog/FEAT-115 ingestion anchor |
| EPIC-013 (2026-04-20) | m7/m8 model gaps | deferred | Structural (ConfigPropagationNode, WorkerQueue extensions) |
| EPIC-013 (2026-04-20) | m9 STORY-432 AuditLog ref | applied | Added to data_models |
| EPIC-013 (2026-04-20) | m10 STORY-417 actor_type=system | applied | Added NFR to STORY-417 |
| EPIC-013 (2026-04-20) | X1..X8 cross-epic | deferred | Most tie to C5/C3 structural decisions |
| EPIC-013 (2026-04-20) | U1..U12 uncited-but-required | deferred | New features / models; product input |
| Cross-cutting (2026-04-20 answers) | Q1 STORY-018 typed-email confirm | applied | Added AC-003; confirm_email on API body; policy line updated |
| Cross-cutting (2026-04-20 answers) | Q2 STORY-012 role-change notification | applied | Notification + resolved audience list; Notification added to data_models |
| Cross-cutting (2026-04-20 answers) | Q6 FEAT-008 dormancy sweep | applied | Description extended to own the User.status=inactive sweep |
| Cross-cutting (2026-04-20 answers) | Q7 FEAT-021 collapse into FEAT-003 | applied | FEAT-021/STORY-048 deleted; STORY-006 absorbs list + revoke audit |
| Cross-cutting (2026-04-20 answers) | Q11 STORY-035 avatar lifecycle | applied | Size/type/dimension caps, replace-cleanup, DELETE endpoint |
| Cross-cutting (2026-04-20 answers) | Q13 ApiKey.scopes derived | applied | Model column removed; STORY-066 / STORY-323 now compute at auth time |
| Cross-cutting (2026-04-20 answers) | Q13 ApiKey.type=break_glass | applied | Added to enum in ApiKey.type description |
| Cross-cutting (2026-04-20 answers) | Q16 BYOKCredential rate_limit removal | applied | Fields removed; STORY-383 AC-001 uses ProviderRateLimit |
| Cross-cutting (2026-04-20 answers) | Q29 EPIC-014 split | applied | New EPIC-014 "Prompts and model evaluation"; FEAT-058/059 retagged |
| Cross-cutting (2026-04-20 answers) | Q48 AlertRule.channels → audience | applied | Model column renamed; PATCH/POST bodies updated; STORY-223 AC-001 uses canonical roles |
| Cross-cutting (2026-04-20 answers) | Q51 FEAT-107 split-by-mode | applied | Description documents identity (both modes) vs billing (saas-only, 404 in self_hosted) |
| Cross-cutting (2026-04-20 answers) | Q52 FEAT-127 DR role split | applied | STORY-294 split into self_hosted execute + saas request-ticket |
| Cross-cutting (2026-04-20 answers) | Q53 FEAT-131 fail-closed default | applied | STORY-306 AC-002 now rejects on geoip unavailability |
| Cross-cutting (2026-04-20 answers) | Q58 FEAT-160 move to EPIC-003 | applied | epic tag changed; EPIC-011/EPIC-003 features lists updated |
| Cross-cutting (2026-04-20 answers) | Q59 EPIC-015 split | applied | New EPIC-015 "Provider API surface"; FEAT-150..157 retagged |
| Cross-cutting (2026-04-20 answers) | Q71 installed_on baseline dimension | applied | deployment_modes baseline describes the new dimension; FEAT-181/182 use it |
| Cross-cutting (2026-04-20 answers) | Q79 destructive policy additions | applied | Policy line enumerates offboard user, waiver>50%, cycle force-reset |
| Cross-cutting (2026-04-20 answers) | Q80 audience+channel audit sweep | applied | STORY-232 expanded to 7 ACs including audit-of-audience and mode collapse |
| Cross-cutting (2026-04-20 new features) | FEAT-183..200 | applied | 19 new features (see wave 4 commit) with stub stories STORY-442..462 |
| Cross-cutting (2026-04-20 new models) | OperatorPrincipal, PiiPolicy, SafetyAllowanceGrant, AlertRuleSubscription, Invoice, InvoiceLine, InvoiceContest, CreditRequest, HelpArticleView, StatusPageSubscriber, InstallBootstrapIntent, AbuseFlag, AccessLog, OrgSigningSecret, LicenseTier, InstallIdentityKey, TenantSurveyResponse | applied | 17 new models added per wave 3 |
| Cross-cutting (waves 16-19) | C-6 streaming cache replay | applied | STORY-482 defines write-path, SSE replay, TTFT on hit, FEAT-148 degraded path and abort-skip |
| Cross-cutting (waves 16-19) | M-7 STORY-043 quiet hours | applied | NotificationPreference keyed on (scope, user/org, event_type) with sentinel event_type=null; STORY-043 PATCH body carries event_type; resolution walks event row → sentinel → notifications_model default |
| Cross-cutting (waves 16-19) | notifications_model tech_contact | applied | Baseline roster now names tech_contact alongside the five existing Org contacts |
| Cross-cutting (waves 16-19) | SsoConfig.signed_users | applied | Description adds "rolling 30-day count refreshed by FEAT-187" |
| Cross-cutting (waves 16-19) | FEAT-094 cascade asymmetry | applied | Description explicitly separates non-destructive (cascades) from destructive (requires detachment) |
| Cross-cutting (waves 16-19) | FEAT-064 event catalog | applied | Description enumerates canonical event names (session.logout, role.change, safety_policy.change, template.update, nightly.refresh, tenant.suspend, org.residency.pin, byok.rotate) and mandates save-time rejection of unknown events |
| Cross-cutting (waves 16-19) | STORY-223 hot-reload | applied | Ten-second number replaced by config_hot_reload SLA reference |
| Cross-cutting (waves 16-19) | AlertRule.category enum | applied | Canonical category enum documented on model |
| Cross-cutting (waves 16-19) | FEAT-124 outreach export | applied | STORY-281 AC-002 emits a redacted CrmOutreach CSV in saas; omitted in self_hosted |
