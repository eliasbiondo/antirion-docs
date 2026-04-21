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
