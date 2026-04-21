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
