# EPIC-001 Identity and access — Audit

Source: `docs/requirements.yaml` (24,172 lines, snapshot at commit `c6cf1ca`). Epic declared at line 75; features FEAT-001..FEAT-012 at lines 323–453; stories STORY-001..STORY-034 at lines 2141–3679; models referenced live at lines 20712–24171.

## Summary

| Severity | Count |
| --- | --- |
| Critical | 5 |
| Major | 9 |
| Minor | 11 |
| Cross-epic | 4 |
| Missing / dangling references | 3 |

All five critical findings and most of the majors are data-model contradictions — fields or enum values named by acceptance criteria that do not exist on the referenced model, or descriptions of the role hierarchy that disagree with the stored enum. No story in the epic contains a broken `depends_on` link; all intra-epic story refs resolve.

---

## Critical findings (blocking / contradicts baseline)

### C-1. FEAT-012 describes a tenant role set that contradicts FEAT-005, STORY-011 and the `User.role` enum

- FEAT-012 description (`docs/requirements.yaml:447`):
  > "Built-in tenant roles are owner, admin, member and viewer in both deployment modes."
- FEAT-005 description (`docs/requirements.yaml:372`):
  > "Six-tier role hierarchy with inherited scopes."
- STORY-011 non_functional (`docs/requirements.yaml:2713`):
  > "Role hierarchy owner (6) > admin (5) > developer (4) > analyst (3) > viewer (2) > service (1)"
- `User.role` enum (`docs/requirements.yaml:20795`):
  > "owner|admin|developer|analyst|viewer|service"

FEAT-012 introduces a fourth tenant role `member` that exists nowhere else and drops `developer`, `analyst` and `service`. Every other FEAT and STORY in the epic — STORY-005 (`default role "developer"`, line 2402), STORY-007 (`I pick role "developer"`, line 2503), STORY-011 and STORY-012 — uses the six-tier list. If FEAT-012 is canonical, role pickers, SSO JIT defaults, invite forms and existing AuditLog examples are all wrong; if FEAT-005 / the enum is canonical, FEAT-012's description is wrong.

Fix: rewrite FEAT-012 to list the six built-in roles `owner|admin|developer|analyst|viewer|service` and remove the invented `member` role. If a simplified four-role model is intended, update FEAT-005, STORY-005, STORY-007, STORY-011, STORY-012 and `User.role` in one pass.

### C-2. `platform admin` role is required by FEAT-012 and baseline but absent from `User.role` enum

- FEAT-012 (`docs/requirements.yaml:447`):
  > "The platform admin role is a reserved built-in that exists only in self_hosted mode, cannot be granted to an ordinary workspace member…"
- `project.deployment_modes` baseline (`docs/requirements.yaml:36`):
  > "the same platform-operator surfaces are visible only to principals holding the platform admin role on that install."
- `User.role` enum (`docs/requirements.yaml:20795`): `owner|admin|developer|analyst|viewer|service` — no `platform_admin`.

FEAT-012 says platform admin is a held role but there is no value in `User.role` to hold it. Mode-gated rejection logic (`role API … rejected … in saas mode`) cannot be implemented against a missing enum value.

Fix: add `platform_admin` to `User.role` (gated to `self_hosted` installs), or move the role to a separate `PlatformAdminGrant` table, and reference that in FEAT-012 and EPIC-013.

### C-3. STORY-023 sets `User.status = "locked"` but `locked` is not a value of that enum

- STORY-023 AC-001 (`docs/requirements.yaml:3305`):
  > "The User.status is set to 'locked'"
- `User.status` enum (`docs/requirements.yaml:20798`):
  > "active|pending|flagged|inactive|offboarded"

A write of `"locked"` would fail any enum constraint. The baseline `non_functional` for STORY-023 requires "Lock decisions must be race-free under concurrent login attempts", which implies an atomic status write — impossible against the current enum.

Fix: either add `locked` to `User.status`, or model locked-out state via `User.locked_until` alone (which already exists and already drives AC-001's "sign-in attempts return 423"), and remove the `User.status = locked` assignment from STORY-023/024.

### C-4. STORY-026 writes a `User.is_service_account` field that does not exist

- STORY-026 AC-001 (`docs/requirements.yaml:3444`):
  > "A User row with is_service_account=true is created"
- `User` model (`docs/requirements.yaml:20762–20847`): no `is_service_account` field. Service accounts are expected to be `User.role = "service"` per the enum (`docs/requirements.yaml:20795`).

Fix: rewrite STORY-026 AC-001 to "A User row with role='service' is created" and drop the imaginary flag. Same correction applies to STORY-029 ("The service account User row is soft-deleted" at line 3520 — `User.status` has no `soft-deleted` value; use `offboarded` or add an explicit status).

### C-5. FEAT-009 promises user-notification on lockout; STORY-023 does not deliver it and violates the canonical `notifications_model`

- FEAT-009 description (`docs/requirements.yaml:417`):
  > "lock accounts after a configurable threshold, notify the user and allow admin unlock"
- STORY-023 ACs (`docs/requirements.yaml:3297–3319`): no notification recipients cited; only `AuditLog` and `LoginAttempt` writes.
- STORY-024 AC-001 (`docs/requirements.yaml:3367`):
  > "The affected user receives an email stating the account was unlocked"
- `project.notifications_model` (`docs/requirements.yaml:37–38`):
  > "Stories cite these roles instead of inventing local language, and acceptance criteria name the audience per deployment mode. … Every audit record on a notification-bearing event records the resolved audience list and the channel attempt."

Neither STORY-023 nor STORY-024 cites the canonical audience roles `(a)` acting principal or `(b)` owning principal, neither names channels, and neither captures the audience list in the audit record. STORY-023 omits the notification entirely while FEAT-009's description promises one.

Fix: add an AC to STORY-023 that emits a `user.locked` notification to the acting principal (the locked user) via FEAT-102 channel routing, with fallback rules per `notifications_model`. Restate STORY-024's "the affected user" as "acting principal (the target user)". Require the `AuditLog` entry on both stories to record the resolved audience list.

---

## Major findings (inconsistency / broken ref)

### M-1. STORY-015 AC-004 and STORY-017 cover the same delete-team scenario, with divergent API contracts

- STORY-015 AC-004 (`docs/requirements.yaml:2896–2904`) blocks delete on active keys; STORY-015 API includes `DELETE /api/teams/:id` with no body (`docs/requirements.yaml:2944`).
- STORY-017 (`docs/requirements.yaml:2996–3066`) is a full "Delete a team" story; its API requires a `confirm_slug` body (`docs/requirements.yaml:3047–3049`).

Two stories define the same endpoint and the same guard with different request shapes. STORY-015's AC-004 is the duplicate.

Fix: remove AC-004 and the `DELETE /api/teams/:id` block from STORY-015, keeping STORY-017 as the single source for team deletion.

### M-2. `Role` has no `org_id` and no built-in/custom marker, yet FEAT-012 and STORY-032/033 require both

- `Role` model (`docs/requirements.yaml:21007–21021`): `id, name (unique), level, scopes, description`. `name` is globally unique and there is no `org_id`, no `is_builtin`, no `created_by_user_id`.
- STORY-032 (`docs/requirements.yaml:3583–3613`) creates custom roles — with a global `unique` name, two orgs cannot each create a "DataTeam" role.
- STORY-033 AC-002 (`docs/requirements.yaml:3635–3641`) requires a built-in flag:
  > "Built-in roles not editable … The editor is read-only with 'Built-in roles cannot be edited'"
  but the model has nothing to distinguish built-in from custom.

Fix: add `Role.org_id (FK:Org, nullable — null = global built-in)`, `Role.builtin (bool)`, and scope `Role.name` uniqueness to `(org_id, name)`. Update FEAT-012 data_model list.

### M-3. Stories call the role's permission collection `permissions`; the model field is `scopes`

- `Role.scopes` (`docs/requirements.yaml:21018`): `type: json`.
- STORY-031 AC-001 (`docs/requirements.yaml:3577`):
  > "grouped permissions"
- STORY-032 AC-002 (`docs/requirements.yaml:3605`):
  > "I try to add the 'org.delete' permission"
- STORY-033 AC-001 (`docs/requirements.yaml:3632`):
  > "The Role.permissions array is updated"

`Role.permissions` does not exist. The stories consistently use "permissions" while the model exposes `scopes`; pick one name and use it everywhere.

Fix: rename `Role.scopes` to `Role.permissions` (recommended, since "permissions" is the vocabulary used in three stories, FEAT-005 title, and the user-facing role editor) and update STORY-011's scope-check wording accordingly.

### M-4. STORY-022 writes to `AlertEvent` without an `AlertRule`, which `AlertEvent.rule_id` forbids

- STORY-022 AC-001 (`docs/requirements.yaml:3242`):
  > "An AlertEvent of severity 'warn' is generated for the security oncall"
- `AlertEvent.rule_id` (`docs/requirements.yaml:22219–22220`): `type: FK:AlertRule` (not nullable).

Manual user-flagging does not fire an `AlertRule`; there is no seeded rule listed for "user flagged" in EPIC-009. The write either violates the FK or silently requires an invisible system rule.

Fix: either (a) seed an `AlertRule` of kind `user.flagged` and reference it by id in STORY-022, or (b) model user-flagging as a direct `Notification` / `AuditLog` emission rather than an `AlertEvent`. Option (b) is cleaner.

### M-5. `SsoConfig` has no SLO / back-channel logout endpoint, yet FEAT-010 / STORY-025 require one

- `SsoConfig` fields (`docs/requirements.yaml:22302–22340`): `enabled, provider, type, entity_id, acs_url, idp_metadata_url, last_sync_at, signed_users, domains, require_for_domains, jit_mode, default_role`. No `slo_url`, no `back_channel_logout_url`, no `signing_cert`.
- STORY-025 AC-001 (`docs/requirements.yaml:3410`):
  > "A SAML LogoutRequest is sent to the IdP"
- STORY-025 non_functional (`docs/requirements.yaml:3427`):
  > "SAML LogoutRequest signature validated before session revocation"

No field holds the IdP's SLO endpoint or the signing certificate used to validate the receipt.

Fix: add `SsoConfig.slo_url (string, nullable)`, `SsoConfig.back_channel_logout_url (string, nullable)` and `SsoConfig.signing_cert (text, nullable)`, then reference these in STORY-025.

### M-6. FEAT-009 lockout policy has no model to store it

- STORY-023 AC-001 (`docs/requirements.yaml:3300–3306`):
  > "The org lockout policy is 5 failures in 15 minutes … locked_until is set to now + policy.lockout_minutes"
- STORY-023 non_functional (`docs/requirements.yaml:3342`):
  > "Thresholds configurable via org-level policy with safe defaults"
- `SessionPolicy` (`docs/requirements.yaml:23151–23162`) holds only `idle_timeout_minutes` and `absolute_max_hours` — no lockout threshold, no failure-window, no lockout-minutes.

The lockout policy is referenced but has no home.

Fix: extend `SessionPolicy` with `lockout_threshold (int)`, `lockout_window_minutes (int)` and `lockout_duration_minutes (int)` — or introduce a dedicated `LockoutPolicy` model — and reference it in STORY-023/024.

### M-7. STORY-026/030 describe a "human owner" link on service-account Users with no corresponding User field

- STORY-026 AC-001 (`docs/requirements.yaml:3442`):
  > "I click 'New service account' and enter a name and human owner"
- STORY-027 AC-001 (`docs/requirements.yaml:3470`):
  > "I see name, human owner, team, last_used_at and status per row"
- STORY-030 AC-001 (`docs/requirements.yaml:3553`):
  > "I see human owner, team, created_by, created_at and last 24h request count"
- `User` model (`docs/requirements.yaml:20762–20847`): no `human_owner_user_id`, no `created_by_user_id`, no `created_at` (there is `joined_at`), and service-account fields `last_used_at` surface via `last_active_at` / `last_seen_at`.

Three stories pivot on a column that isn't declared.

Fix: add `User.human_owner_user_id (FK:User, nullable)` and `User.created_by_user_id (FK:User, nullable)` to represent service-account ownership. Rename `joined_at` → `created_at` or add `created_at` explicitly. Reconcile `last_used_at` with `last_active_at`.

### M-8. STORY-019 talks about "service keys" but `ApiKey.type` does not include `service`-keys-per-user semantics unambiguously

- STORY-018 AC-001 (`docs/requirements.yaml:3086`):
  > "All owned ApiKeys with type 'user' are revoked"
- STORY-019 AC-001 (`docs/requirements.yaml:3127`):
  > "All 4 ApiKey.owner_user_id point at the target"
- `ApiKey.type` enum (`docs/requirements.yaml:21098`):
  > "service|user|ephemeral"

STORY-018 revokes only `type='user'`, STORY-019 transfers "service keys" but does not state the filter. A user can own type=`service` and type=`user` keys; STORY-019's 4-key scenario does not show the filter, so an implementation could transfer ephemeral keys too.

Fix: in STORY-019 AC-001, state `ApiKey.owner_user_id where ApiKey.type = 'service' AND revoked_at IS NULL` explicitly.

### M-9. STORY-017 declares `Project` guard in precondition but has no AC for it

- STORY-017 AC-001 given (`docs/requirements.yaml:3010`):
  > "A Team has no members, no active ApiKeys and no active Projects"
- AC-002 tests ApiKeys, AC-003 tests members — no AC tests Projects.
- `Project.team_id` (`docs/requirements.yaml:22094`) is **not nullable**, so deleting a Team while a Project references it would break referential integrity.

Missing negative-case AC.

Fix: add AC-005 "Block delete when team has active Projects": "I see 'Team has N active projects — move or archive them first' and the Team is not deleted."

---

## Minor findings (wording, duplication, style)

### m-1. `STORY-002` non_functional is boilerplate unrelated to trust-device

`docs/requirements.yaml:2262–2263` lists "Membership and role changes are audited" for a story about trusting a browser. Replace with trust-device-specific guarantees (cookie flags: `HttpOnly; Secure; SameSite=Lax; domain-scoped`, fingerprint-stability notes, 30-day max, revocation on password change).

### m-2. STORY-022 `depends_on: STORY-018` is illogical

Flagging a user does not require offboarding them (`docs/requirements.yaml:3231`). Either drop the dependency or replace with `STORY-011` (role scopes define who can flag).

### m-3. STORY-029 has no `depends_on`

Deleting a service account (`docs/requirements.yaml:3504–3536`) implicitly requires it to exist (STORY-026) and be credential-free (STORY-028). Add `depends_on: [STORY-026, STORY-028]`.

### m-4. STORY-003 request-body / AC terminology inconsistency with the Login screen

STORY-003 AC-001 says "I click 'Forgot?' on the password field" (`docs/requirements.yaml:2281`) but the API path is `/api/auth/password/reset`. "Forgot?" link needs a screen/component named so the UI spec lines up with STORY-001's `LoginPage`.

### m-5. `UserPrefs.reduced_motion` is referenced in the ui_baseline but UserPrefs is only bound to EPIC-002

`project.ui_baseline` (`docs/requirements.yaml:8`) expects every screen to respect `UserPrefs.reduced_motion`, yet the EPIC-001 Login and Teams & Users screens do not enumerate UserPrefs in `data_models`. Either the baseline covers this implicitly (then fine) or each EPIC-001 screen should declare `UserPrefs` in `data_models`. Recommend the former and remove the nagging gap — but note explicitly in FEAT-001's ui_references.

### m-6. Role-change notification audience is not named in STORY-012

`docs/requirements.yaml:2725–2776` — a role change is a high-impact identity event, yet no audience is notified (only `AuditLog`). The canonical `notifications_model` (baseline line 37–38) suggests the acting principal (actor), the owning principal (target user) and `Org.security_contact` should all receive the event. Add an AC.

### m-7. STORY-018 offboarding does not guard against removing the last `owner`

`docs/requirements.yaml:3067–3108`. STORY-012 AC-003 prevents demoting the last owner, but STORY-018 offers no parallel guard — offboarding the sole owner leaves a workspace permanently ownerless. Add "Block offboarding when target is the only remaining `owner`".

### m-8. STORY-018 lacks typed confirmation even though offboarding is irreversible

`docs/requirements.yaml:3083` — "I click 'Offboard' on the user and confirm". The `project.destructive_action_confirmation_policy` list (`docs/requirements.yaml:5`) enumerates specific high-impact actions but does not include user offboarding; however, offboarding revokes sessions, revokes all user-type ApiKeys and transitions status to `offboarded` — functionally irreversible. Either enumerate "offboard user" in the policy, or require typing the target's email to confirm in STORY-018.

### m-9. STORY-030 mentions `last_used_at` but service-account activity is stored on ApiKey / Request

`docs/requirements.yaml:3553` — "I see human owner, team, created_by, created_at and last 24h request count". User has `last_active_at` and `last_seen_at`, not `last_used_at`. Either map to `last_active_at` or compute from `Request` rollup.

### m-10. STORY-011 non_functional quotes the six-tier hierarchy inline instead of pointing at `Role.level`

`docs/requirements.yaml:2713`. Duplicating the hierarchy in prose invites the same drift that produced finding C-1. Replace with "Levels per `Role.level`; writes gated by level".

### m-11. Priority tagging inconsistency on session revocation

FEAT-003 is P0 (`docs/requirements.yaml:350`) but FEAT-010 SAML SLO is P1 (`docs/requirements.yaml:431`). If a workspace enforces SSO (`Org.sso_enforced=true`), FEAT-003's "sign-out everywhere" is ineffective against the IdP until FEAT-010 ships. Either upgrade FEAT-010 to P0 for SSO-enforced orgs or document the release-ordering constraint in FEAT-003's description.

---

## Cross-epic issues

### X-1. `notifications_model` audience roles reference `Org` contact fields that are not on `Org`

- `project.notifications_model` (`docs/requirements.yaml:37`):
  > "the org-scoped contact fields on Org (security_contact, billing_contact, finance_contact, privacy_officer, primary_contact)"
- `Org` model (`docs/requirements.yaml:20713–20756`) has `billing_contact`, `tech_contact`, `security_contact` — and no `finance_contact`, `privacy_officer`, `primary_contact`.

Any EPIC-001 story that tries to follow `notifications_model` cannot resolve the missing fields. Two EPIC-001 stories — STORY-024 (unlock notification) and candidate future ACs for STORY-012/STORY-018 — require this. Add `finance_contact`, `privacy_officer`, `primary_contact` to `Org` (primarily an EPIC-010 / FEAT-107 fix, but flagged here because this epic's notification ACs depend on it).

### X-2. STORY-020 (admin resets MFA) straddles EPIC-001 / EPIC-002 with no declared link

`docs/requirements.yaml:3144–3169`. The admin reset of `MfaFactor` lives in FEAT-007 (User offboarding, EPIC-001) but the model and user-self-manage flow are in FEAT-015 (Personal security and MFA, EPIC-002). Add a narrative cross-reference to FEAT-015 and describe whether this action produces an `mfa.reset` `NotificationPreference`-resolved notification to the target user.

### X-3. STORY-018 / STORY-019 implicitly depend on EPIC-003 (`ApiKey` lifecycle)

`docs/requirements.yaml:3077–3143`. Revocation of user-type keys and transfer of service keys are described without referencing EPIC-003's revocation/transfer flows (FEAT-024/FEAT-025 area). Add explicit cross-epic references so rollout can sequence correctly.

### X-4. STORY-022 fires into EPIC-009 with no declared link

`docs/requirements.yaml:3240–3242`. Flag action creates an `AlertEvent`, which is an EPIC-009 construct. There is no cross-reference to the alert-rule catalog / subscription surface that owns the event class. Add a cross-epic reference to FEAT-099 area and see finding M-4 for model correctness.

---

## Mode-availability errors (saas vs self_hosted vs EPIC-013)

- **E-1 (minor).** EPIC-013 surfaces platform-operator capability and reads deployment-mode config. EPIC-001 features other than FEAT-012 do not declare mode availability, in accordance with the baseline rule "features that differ … declare mode availability explicitly". FEAT-009's lockout-notify step (finding C-5) will need mode-aware fallback language when added — specifically the acting-principal notification is tenant-identical across modes, but the admin-notification fallback differs. Call this out when writing the new AC.
- **E-2 (minor).** FEAT-012 is the only EPIC-001 feature that correctly declares mode behavior (`docs/requirements.yaml:447`). No mode-availability error found within its text; the critical findings against it (C-1, C-2) are data-model, not mode, issues.

No direct contradictions with EPIC-013 were found.

---

## Role / scope mismatches

- **R-1.** `STORY-022` attributes the generated `AlertEvent` to "security oncall" (`docs/requirements.yaml:3242`), which is not a canonical role in `project.notifications_model`. Replace with `Org.security_contact` (falling back to `Org.owner` in saas / platform admin in self_hosted).
- **R-2.** `STORY-024` says "Only roles owner/admin may unlock accounts" (`docs/requirements.yaml:3393`) which is consistent with the hierarchy, but does not state whether `developer` / `analyst` / `viewer` / `service` are denied. Make the deny-list explicit so that this story is testable without inferring from STORY-011.

---

## Data-model mismatches (consolidated)

Already covered in Critical C-3 (`User.status = locked`), C-4 (`User.is_service_account`), Major M-2 (`Role` missing `org_id`, `builtin`), M-3 (`Role.permissions` vs `scopes`), M-5 (`SsoConfig` missing SLO fields), M-6 (no lockout-policy model), M-7 (`User` missing service-account ownership fields), and M-9 (`User.last_used_at`).

One additional standalone mismatch:

- **D-1.** `STORY-029` uses "soft-deleted" for a service-account User (`docs/requirements.yaml:3520`). `User.status` has no `soft-deleted` / `deleted` value. Use `offboarded` to match the existing enum.

---

## Missing / dangling references

Per the supplementary check: verify every `FEAT-XXX` and `STORY-XXX` id referenced in EPIC-001 actually exists.

### Cited-but-undefined (a)

**None.** All 12 features (FEAT-001..FEAT-012) and all 34 stories (STORY-001..STORY-034) listed under EPIC-001 are defined at the expected locations. Every intra-epic `depends_on` (grepped at `docs/requirements.yaml:2141–3679`) resolves to a defined story in the same epic. No acceptance criterion text embeds a dangling `FEAT-` or `STORY-` literal.

### Implied-but-undeclared dependency features (b)

The following epic-001 stories materially depend on features in other epics but declare no cross-reference:

| Citing line | Citing id | Implied dependency | Why |
| --- | --- | --- | --- |
| `docs/requirements.yaml:3085` | STORY-018 | FEAT-022/FEAT-024 (EPIC-003: API keys lifecycle) | "All owned ApiKeys with type 'user' are revoked" requires ApiKey revocation endpoints. |
| `docs/requirements.yaml:3127` | STORY-019 | FEAT-022 area (EPIC-003: API key ownership/transfer) | Key owner reassignment relies on ApiKey.owner_user_id mutation flows owned by EPIC-003. |
| `docs/requirements.yaml:3160` | STORY-020 | FEAT-015 (EPIC-002: Personal security and MFA) | Resetting another user's MfaFactor rows is the admin mirror of the personal-security story; neither story cross-references the other. |
| `docs/requirements.yaml:3242` | STORY-022 | FEAT-099 area (EPIC-009: Alerts) | `AlertEvent` cannot be written without a declared `AlertRule` — see M-4. |
| `docs/requirements.yaml:3367` | STORY-024 | FEAT-102 (EPIC-009: Notification-channels routing) | "The affected user receives an email" is vacuous unless FEAT-102 routing resolves the user's preferred channel. |
| `docs/requirements.yaml:3419` | STORY-025 | FEAT-102 + EPIC-010 SsoConfig surfaces | SLO receipt ingestion needs webhook/back-channel wiring that is cross-epic. |
| `docs/requirements.yaml:3445` | STORY-026 | FEAT-022 (EPIC-003: ApiKey issuance) | "An initial credential is issued and shown once" is an ApiKey issuance, owned by EPIC-003. |

Recommend: add an explicit `related_features` or `cross_epic_refs` list to each of the above stories, naming the feature id it couples to.

### Epic-scope promises absent from the features list (c)

Epic scope (`docs/requirements.yaml:77`): "Sign-in, sessions, user invites, roles, teams, offboarding."

All six promised surfaces have at least one dedicated feature. The epic over-delivers (FEAT-008 activity/flagging, FEAT-009 lockout, FEAT-010 SAML SLO, FEAT-011 service accounts, FEAT-012 custom roles) — none of these is promised by the description but they are consistent with the epic's stated intent. No missing feature found against the scope line.

---

## Categories reported clean

- **Contradictions with `performance_slo` / `availability_slo`:** none found. EPIC-001 stories are control-plane operations (sign-in, admin actions) not gateway hot-path, so the 250µs / 10k rps targets do not apply. No story implies mutable in-memory state on a gateway node that would break `statelessness`.
- **Contradictions with `multi_region_and_dr`:** none found.
- **Contradictions with `tenant_isolation`:** none found. `Session`, `TrustedBrowser`, `LoginAttempt`, `PasswordResetToken` correctly omit `org_id` because they are partitioned by `user_id`, which transitively partitions by `User.org_id`.
- **Contradictions with `config_hot_reload`:** the recurring `non_functional` line "Revocations and role changes propagate to every node within the config-reload SLA" is consistent with the 30-second baseline target.
- **Contradictions with `destructive_action_confirmation_policy`:** the enumerated list (line 5) does not explicitly name `offboard user`, `reset MFA`, or `delete service account` — see minor m-8. Within the stories, typed-confirmation is used consistently for team delete, service-account delete and MFA reset.

---

## Suggested remediation ordering

1. Fix C-1 / C-2 / C-3 / C-4 / C-5 (data-model + FEAT-012 role definition + lockout notification) — these unblock the rest of the epic and EPIC-013.
2. Fix X-1 by adding the three missing `Org` contact fields (upstream of FEAT-107 but blocks several notification ACs here).
3. Fix M-1 (duplicate delete-team), M-2/M-3 (Role model), M-5 (SsoConfig SLO), M-6 (lockout policy).
4. Fix M-7 / M-8 / M-9 (service-account modelling).
5. Close minors m-1 through m-11 in one editorial pass.
