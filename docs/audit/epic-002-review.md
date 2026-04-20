# EPIC-002 Personal account — Audit

Read-only audit of `docs/requirements.yaml` at `EPIC-002` (line 92) and its features `FEAT-013` through `FEAT-021` and stories `STORY-035` through `STORY-048`. Baseline references (`project.non_functional_baseline`, `project.ui_baseline`, `project.notifications_model`, `project.destructive_action_confirmation_policy`) and the `models:` section (line 20712+) were cross-checked, as well as `EPIC-001` identity stories for overlap.

## Summary

| Severity | Count |
| --- | --- |
| Critical | 4 |
| Major | 9 |
| Minor | 8 |
| Cross-epic | 3 |
| Missing / dangling references | 6 |

Top themes:
1. `FEAT-020` (Personal account deletion) references fields that do not exist in the data model (`User.status="pending_deletion"`, `PersonalToken.status`).
2. `FEAT-015` (Personal security and MFA) depends on a recovery-code concept with no backing model and a primary-factor flag absent from `MfaFactor`.
3. `FEAT-021` (Active sessions browser) is a near-duplicate of `FEAT-003`/`STORY-006`.
4. Destructive-action confirmation pattern for personal account deletion diverges from `project.destructive_action_confirmation_policy`.

## Critical findings

### C-1. `User.status="pending_deletion"` is not a valid enum value
- Location: `docs/requirements.yaml:4280` (STORY-046 AC-001), reinforced by `docs/requirements.yaml:4343` (STORY-047 AC-001).
- Quote: `- The User.status becomes "pending_deletion"` and later `- User.status returns to "active"`.
- Problem: `User.status` enum is defined at `docs/requirements.yaml:20798` as `active|pending|flagged|inactive|offboarded`. `pending_deletion` is not in this enum. STORY-047 then tries to return it to `active`, which is only coherent if `pending_deletion` was valid to begin with. This is a hard data-model mismatch that will fail schema validation at implementation time.
- Fix: Either (a) extend the `User.status` enum at `docs/requirements.yaml:20798` to include `pending_deletion`, or (b) change STORY-046/047 to drive status off `AccountDeletionRequest.status` (which already supports `pending|cancelled|completed` at line 22800) and leave `User.status="active"` until cutover.

### C-2. `PersonalToken` has no `status` field; STORY-046/047 depend on one
- Location: `docs/requirements.yaml:4281` (STORY-046 AC-001) and `docs/requirements.yaml:4344` (STORY-047 AC-001).
- Quote: `- My personal tokens are marked as rotating and will be revoked at cutover` / `- My tokens and keys are restored to "active"`.
- Problem: The `PersonalToken` model at `docs/requirements.yaml:21022`–`21044` has fields `id, user_id, name, token_hash, scopes, created_at, last_used_at` — no `status`. The `rotating/active/revoked` vocabulary only exists on `ApiKey.status` (line 21112). STORY-046/047 cannot implement the stated behaviour against the current model.
- Fix: Add `status` (enum `active|rotating|revoked`) to `PersonalToken`, or rewrite the AC to say the tokens are hard-deleted at cutover and no reversible "rotating" intermediate state exists (STORY-047 then restores nothing). Pick one and apply it to both stories.

### C-3. Recovery codes referenced without a data model
- Location: `docs/requirements.yaml:3928`–`3935` (STORY-039 AC-001), API path at `docs/requirements.yaml:3947`, and the FEAT-015 description at `docs/requirements.yaml:476`.
- Quote (FEAT-015): `Change password, manage MFA factors, recovery codes, trusted browsers.` — (STORY-039): `A new set of 10 codes is generated and shown once` and `- Old codes are invalidated`.
- Problem: No `RecoveryCode` model exists (`grep -i recovery_code` over the full file returns zero hits in `models:`). STORY-039 `data_models` lists only `User, MfaFactor, TrustedBrowser`. There is nowhere to store the hashed, single-use codes that the non-functional note at `docs/requirements.yaml:3968` ("recovery codes stored hashed and single-use") requires.
- Fix: Add a `RecoveryCode` model to `models:` with at minimum `id (uuid, pk), user_id (FK:User), code_hash (string, unique), consumed_at (timestamp, nullable), created_at (timestamp)`; list it in `STORY-039.data_models`; update STORY-039 AC wording to say "All prior unused `RecoveryCode` rows are marked consumed and 10 new `RecoveryCode` rows are created."

### C-4. `FEAT-021`/`STORY-048` duplicates `FEAT-003`/`STORY-006`
- Locations: `FEAT-021` at `docs/requirements.yaml:531`–`537`, `STORY-048` at `docs/requirements.yaml:4370`–`4401`; overlapped by `FEAT-003` at `docs/requirements.yaml:346`–`355` and `STORY-006` at `docs/requirements.yaml:2417`–`2464`.
- Quote (STORY-006 AC-002): `- I click "Revoke" on a non-current session in Account -> Active sessions` — (STORY-048 AC-002): `- I click "Revoke"` ... `- The session is revoked and disappears from the list`.
- Problem: `STORY-006` (EPIC-001) already owns "revoke an individual session" and "sign out everywhere else", explicitly under *Account → Active sessions*. `STORY-048` adds nothing except listing sessions with device/location/last-active — information that is structurally the same panel. Two separately-numbered features in two epics describe the same surface, which will cause divergent specs and split ownership.
- Fix: Collapse `FEAT-021` into `FEAT-003` (move STORY-048 list AC into STORY-006 as a new AC, delete FEAT-021 from `EPIC-002.features` at `docs/requirements.yaml:104` and from the features block at line 531). If the intent is to keep "view" separate from "revoke", at minimum cross-reference STORY-006 from STORY-048 via `depends_on` and limit STORY-048 to the read-only list AC.

## Major findings

### M-1. `EmailVerificationToken.used_at` mismatch vs. `consumed_at`
- Location: `docs/requirements.yaml:3792` (STORY-036 AC-001).
- Quote: `- The EmailVerificationToken is marked used`.
- Problem: `EmailVerificationToken` at `docs/requirements.yaml:22714`–`22716` defines `consumed_at` (nullable timestamp). Saying "marked used" is ambiguous and nudges implementers toward a `used_at` field that does not exist. The non-Personal-Account `PasswordResetToken` model (line 20927) does use `used_at`, which makes the ambiguity worse.
- Fix: Change the AC wording at 3792 to `- The EmailVerificationToken.consumed_at is set to now`, so it maps unambiguously to the model.

### M-2. `MfaFactor` has no `primary` field; two stories require it
- Location: `docs/requirements.yaml:3985`–`3986` (STORY-040 AC-001) and `docs/requirements.yaml:4016` (STORY-041 AC-001).
- Quote (STORY-040): `- The list shows the new factor with a "primary" toggle` — (STORY-041): `- I have two MfaFactor rows, one primary`.
- Problem: `MfaFactor` at `docs/requirements.yaml:20930`–`20950` has fields `id, user_id, kind, label, secret_hash, created_at` — no `is_primary` or `primary`. There is no way to determine the primary factor or enforce "cannot remove primary while a non-primary exists" without it.
- Fix: Add `is_primary: bool` to `MfaFactor` (unique-one-per-user), or remove the "primary toggle" / "primary/non-primary" language from STORY-040 and STORY-041 and replace it with creation-order semantics keyed off `created_at`.

### M-3. STORY-040 says "type" where model says `kind`
- Location: `docs/requirements.yaml:3994` (STORY-040 AC-002).
- Quote: `- A new MfaFactor of type "webauthn" is created`.
- Problem: `MfaFactor.kind` is the enum field (line 20938). Using "type" colloquially in AC risks an implementer adding a `type` column or renaming `kind`.
- Fix: Change to `- A new MfaFactor with kind "webauthn" is created`.

### M-4. STORY-035 "photo" vs. `User.avatar_url`
- Location: `docs/requirements.yaml:3744`–`3750` (STORY-035 photo upload API) and the FEAT-013 description at `docs/requirements.yaml:457`.
- Quote: `POST /api/users/me/photo` returning `photo_url: string`; FEAT description lists "photo".
- Problem: `User` model has `avatar_url` (line 20791), not `photo_url`. The API response field name contradicts the model field name.
- Fix: Either rename the response field to `avatar_url` to match the model, or rename the model field to `photo_url`. The rest of the codebase likely standardises on `avatar_*` (see `User.avatar_hue` at line 20787), so prefer response-side rename.

### M-5. `NotificationPreference` row-shape contradicts "per event-channel pair"
- Location: `docs/requirements.yaml:4113` (STORY-043 AC-001).
- Quote: `- My NotificationPreference for that event-channel pair is stored`.
- Problem: The model at `docs/requirements.yaml:21045`–`21072` stores a single row per `(scope, user_id|org_id, event_type)` with `channels: json` — i.e. one row per event, channels folded into the JSON payload. There is no "event-channel pair" row. AC language implies a different shape from the model.
- Fix: Reword AC-001 to `- My NotificationPreference row for event "audit.weekly" has the "email" entry removed from its channels array`. Apply the same change anywhere a "pair" is implied.

### M-6. Destructive-action confirmation for personal account deletion diverges from policy
- Location: policy at `docs/requirements.yaml:5`; flow at `docs/requirements.yaml:4277` (STORY-046 AC-001) and `docs/requirements.yaml:4340` (STORY-047 AC-001).
- Quote (policy): `High-impact destructive actions (delete project, delete org, delete alert rule with active fires, delete model with live traffic, delete team, purge cache, rotate org secret) require the user to type the target's name or slug to confirm.` — (STORY-046): `- I confirm with my password or MFA and check the consequences box`.
- Problem: Deleting your own account is at least as high-impact as "delete team" (listed). The policy does not list it explicitly, and STORY-046 uses a password/MFA + checkbox confirmation instead of type-the-target-name. This creates an unowned confirmation pattern that bypasses the baseline rule.
- Fix: Either (a) extend the policy at line 5 to enumerate "delete personal account" and specify the confirmation UX, or (b) align STORY-046 AC-001 with the existing rule (require typing the account handle or email in addition to password/MFA). Recommendation: (b), because the password/MFA check serves auth re-verification, not destructive-confirmation; both are appropriate.

### M-7. Password change produces no notification to the acting principal
- Location: `docs/requirements.yaml:3877`–`3898` (STORY-038).
- Problem: `project.notifications_model` (line 37) defines audience role (a) = acting principal. Password change is a classic sensitive-event notification, and peer stories in this feature do emit it (e.g. STORY-041 AC-001 at line 4021 "An email notifies me the factor was removed"). STORY-038 has no such AC. Mode-availability for the notification is also unstated.
- Fix: Add an AC: `- An "account.password_changed" notification is delivered to the acting principal via the channels resolved by FEAT-102; an AuditLog entry with action "user.password_changed" is written.` Apply in both modes; no self_hosted/saas variance is needed because this is a tenant-scoped event on role (a).

### M-8. STORY-044 data export: mode availability and audience unstated
- Location: `docs/requirements.yaml:4143`–`4207` (STORY-044); baseline mode rule at `docs/requirements.yaml:36`; notifications audience rule at `docs/requirements.yaml:37`–`38`.
- Problem: FEAT-018 at `docs/requirements.yaml:503`–`511` has no mode-availability declaration. Personal data export touches compliance/DPO workflows, which the notifications model explicitly collapses differently across modes (the `dpo` Antirion-staff sub-queue exists only in saas). The baseline at line 36 says every feature whose scope, availability or data shape differs between modes must declare it. STORY-044 notifies only the acting principal and never references the platform operator or `dpo` audience.
- Fix: Add a one-line `mode_availability` note in FEAT-018 description ("both modes"), add an AC: `- On completion, an audit record is written naming the resolved audience list (acting principal in both modes; Antirion dpo sub-queue in saas only) per project.notifications_model.`

### M-9. FEAT-014 description restates `project.ui_baseline` instead of deviating
- Location: `docs/requirements.yaml:467`.
- Quote: `Theme, density, reduced motion, compact numbers, week start. Accessibility (WCAG 2.1 AA) and loading/empty/error-state rendering are workspace-wide defaults defined in project.ui_baseline rather than per-feature stories.`
- Problem: `project.ui_baseline` explicitly says at line 7 "Individual stories only restate these when they deviate." FEAT-014 restates the baseline without deviating, which is against the baseline directive and makes the feature description noisy. STORY-037 correctly does not restate.
- Fix: Trim the FEAT-014 description to `Theme, density, reduced motion, compact numbers, week start.` — drop the trailing sentence.

## Minor findings

### m-1. Routing convention inconsistency: `/api/account/*` vs `/api/users/me/*`
- Locations: STORY-044 uses `/api/account/data-exports` (`docs/requirements.yaml:4184`), STORY-045 uses `/api/account/login-history` (line 4246), STORY-046/047 use `/api/account/deletion` (lines 4304, 4357). Other stories in the same epic (STORY-035, 037, 038, 039, 042, 043) use `/api/users/me/...`.
- Problem: Two URL shapes for the same resource scope ("my own account") inside one epic.
- Fix: Pick one convention and apply across all stories. Recommendation: `/api/users/me/...` because the User model is the anchor and this matches the rest of the epic.

### m-2. `FEAT-016` title uses "Personal access tokens", model is `PersonalToken`
- Locations: `docs/requirements.yaml:487` (feature title), `docs/requirements.yaml:21022` (model).
- Problem: Minor naming drift; readers searching for "PersonalAccessToken" will not find a model.
- Fix: Either rename the feature to "Personal tokens" or rename the model to `PersonalAccessToken` (more descriptive; preferred).

### m-3. STORY-042 does not enforce scope-inheritance claim
- Location: `docs/requirements.yaml:4095` ("Tokens inherit the user's role and scopes").
- Problem: AC-001 allows picking any `["read"]` scope with no check against `User.role`. The non-functional claim is not enforced by an AC or by a model constraint.
- Fix: Add an AC: `- Submitting a scope the acting principal does not hold returns 403 and no PersonalToken is created.`

### m-4. STORY-042 lacks a "list tokens" AC
- Location: `docs/requirements.yaml:4038`–`4096`.
- Problem: Feature description says "Create, list and revoke" but only create and revoke are ACed. Peer feature FEAT-022 (API keys) has list stories.
- Fix: Add an AC for listing, including masked prefix and last-used rendering.

### m-5. STORY-035 has no handle-collision / email-collision AC
- Location: `docs/requirements.yaml:3689`–`3716`.
- Problem: `User.email` and `User.handle` are `unique: true` (lines 20773, 20776). Profile edit is the main surface that can provoke collisions, and no AC covers it. 409 is also not in the error list at line 3742.
- Fix: Add AC for `409 conflict — handle already in use` and include 409 in the `errors` array for the PATCH endpoint.

### m-6. STORY-036 success page tells signed-in user to "sign in"
- Location: `docs/requirements.yaml:3793`.
- Quote: `- I see a success page with a link to sign in`.
- Problem: The email-change flow is initiated by an already signed-in user. Suggesting "sign in" is confusing unless the verification link is opened in a different browser; the AC does not distinguish. The FEAT-003 sign-out-on-password-change pattern (STORY-038) does revoke other sessions, but email change does not.
- Fix: Clarify: `- I see a success page confirming the change; if I opened the link in a signed-out browser, the page offers a "Sign in" shortcut.`

### m-7. FEAT-019 description misses `user_agent`
- Location: `docs/requirements.yaml:515`.
- Quote: `Show the authenticated user their own recent successful and failed sign-in attempts with IP, device and location.`
- Problem: `LoginAttempt.user_agent` exists at `docs/requirements.yaml:22735`. Description omits it; STORY-045 AC-001 at line 4224 also omits it.
- Fix: Either add `user_agent` to the description and AC, or drop `user_agent` from the model if not surfaced anywhere. Recommendation: include it — it is useful for spotting rogue sign-ins.

### m-8. STORY-043 quiet-hours semantics ambiguous between per-event and global
- Location: `docs/requirements.yaml:4115`–`4122` and model at `docs/requirements.yaml:21067`–`21072`.
- Problem: The API body at line 4127 sends a single `quiet_hours_start/end` pair, suggesting a global user-level setting, but the model stores quiet hours on each `NotificationPreference` row (per-event). The story implies global; the model supports per-event.
- Fix: Either collapse quiet hours to a single row (`scope=user, event_type=null` sentinel, unique per user) or make the API body a per-event override. Then make STORY-043 AC-002 explicit about which it is.

## Cross-epic issues

### X-1. `STORY-048` vs. `STORY-006` (EPIC-001 overlap) — see C-4
- Already covered in Critical findings. Repeating here for cross-epic visibility. Lines: `docs/requirements.yaml:531` (FEAT-021), `docs/requirements.yaml:4370` (STORY-048), `docs/requirements.yaml:346` (FEAT-003), `docs/requirements.yaml:2417` (STORY-006).

### X-2. `STORY-039` "Clear trusted browsers" overlaps `STORY-002` scope
- Locations: STORY-039 AC-002 at `docs/requirements.yaml:3937`–`3944`; STORY-002 at `docs/requirements.yaml:2215`–`2261` (trust a device).
- Problem: `TrustedBrowser` lifecycle is created in STORY-002 (EPIC-001 / FEAT-001) but cleared in STORY-039 (EPIC-002 / FEAT-015). No story covers individual trusted-browser revocation (only "clear all"), nor a list view. This is a partial split across epics that leaves gaps.
- Fix: Add to STORY-039 (or a new story under FEAT-021 if kept) an AC for listing trusted browsers with device/expires-at and revoking individually. Reference `STORY-002` via `depends_on` so the create/consume/revoke triple lives under one feature.

### X-3. `STORY-045` login history depends on `STORY-023` mechanics
- Locations: STORY-045 at `docs/requirements.yaml:4208`–`4260`; `STORY-023` at `docs/requirements.yaml:3286`–`3343` (writes `LoginAttempt`).
- Problem: STORY-045 has no `depends_on: [STORY-023]`, even though `LoginAttempt` rows are written exclusively by the lockout/login-record path introduced in FEAT-009. Implementation ordering risk: FEAT-019 could ship against an empty table.
- Fix: Add `depends_on: - STORY-023` in STORY-045 to make the dependency explicit.

---

## Missing / dangling references

This section enumerates every FEAT/STORY id cited by `EPIC-002` or its features/stories, (a) dangling cites with no definition, (b) dependencies implied by narrative but never declared, (c) features the epic scope promises but are absent from the features list.

### (a) Cited feature/story ids with no definition
All explicit cites resolve. Verified against the stories/features index:

- `EPIC-002.features` (`docs/requirements.yaml:96`–`105`) cites `FEAT-013..FEAT-021`. Each is defined: `FEAT-013` at 454, `FEAT-014` at 464, `FEAT-015` at 473, `FEAT-016` at 485, `FEAT-017` at 494, `FEAT-018` at 503, `FEAT-019` at 512, `FEAT-020` at 521, `FEAT-021` at 531.
- `FEAT-013..021.stories` cite `STORY-035..048`. Each is defined between lines 3680 and 4401.
- `STORY-036.depends_on` → `STORY-035` (exists at 3680). ✓
- `STORY-038.depends_on` → `STORY-001` (exists at 2141). ✓
- `STORY-041.depends_on` → `STORY-040` (exists at 3969). ✓
- `STORY-047.depends_on` → `STORY-046` (exists at 4261). ✓

No dangling cites inside the epic's own scope.

### (b) Dependencies implied by narrative but never declared

These stories lean on capabilities that live in other features, but do not list them under `depends_on`. Implementation will pick the stories up in an order that can produce empty-shell rendering or duplicated mechanics.

1. **STORY-038 → FEAT-003 / STORY-006** (session revocation).
   - Citing line: `docs/requirements.yaml:3888` — `- All other Sessions are revoked`.
   - Missing dep: the revoke-other-sessions path is STORY-006 AC-003 in EPIC-001. STORY-038 has only `depends_on: - STORY-001`.
   - Fix: add `- STORY-006` to STORY-038's `depends_on`.

2. **STORY-039 → STORY-002** (TrustedBrowser create-path).
   - Citing line: `docs/requirements.yaml:3939` — `- I have 3 trusted browsers`.
   - Missing dep: `TrustedBrowser` rows are created only by the "Trust this device" flow in STORY-002 (`docs/requirements.yaml:2215`). Without it, STORY-039 AC-002 always finds zero rows.
   - Fix: add `- STORY-002` to STORY-039's `depends_on`.

3. **STORY-043 → FEAT-102** (notification-channels routing).
   - Citing line: `docs/requirements.yaml:4113` (`NotificationPreference for that event-channel pair`).
   - Missing dep: `project.notifications_model` at line 38 states channel resolution is delivered by `FEAT-102`. `FEAT-102` exists at `docs/requirements.yaml:1363`. STORY-043 never declares the link.
   - Fix: add an explicit reference (either in STORY-043's narrative or via a `depends_on` that names a FEAT-102 story) so the channel-resolution surface is wired.

4. **STORY-044 → FEAT-102** (email channel) and **→ FEAT-167** (worker fleet health).
   - Citing lines: `docs/requirements.yaml:4161` (`ready by email within 24 hours`) and the `DataExportJob.status` lifecycle which is produced by workers.
   - Missing deps: `FEAT-102` (exists at 1363) owns email delivery; `FEAT-167` (exists at 1983) is cited by the non-functional baseline at line 18 as the worker-fleet health surface that this export job depends on.
   - Fix: list the governing stories as `depends_on` or note the dependencies in STORY-044's narrative.

5. **STORY-044 → FEAT-179** (saas phone-home policy gating).
   - Citing line: baseline at `docs/requirements.yaml:38` references `FEAT-179` for the saas-only `dpo` sub-queue collapse rule. `FEAT-179` exists at line 2099.
   - Missing dep: if a data-export event fan-out is supposed to hit the saas `dpo` sub-queue (see M-8), STORY-044 needs to cite FEAT-179 as the opt-in gate.
   - Fix: reference FEAT-179 from STORY-044's mode-availability clause once M-8 is applied.

6. **STORY-045 → STORY-023** (LoginAttempt writes).
   - Citing line: `docs/requirements.yaml:4224` — `- I see the last 30 LoginAttempt rows`.
   - Missing dep: `LoginAttempt` rows are produced only by the sign-in path hardened in STORY-023 (`docs/requirements.yaml:3286`). Already captured under X-3 as an explicit dependency-add.
   - Fix: add `- STORY-023` to STORY-045's `depends_on`.

### (c) Features the epic scope promises but are absent from the features list

The scope line for `EPIC-002` at `docs/requirements.yaml:94` is: `Per-user profile, preferences, security, tokens, and notification settings.` Every one of those five categories has a corresponding feature (FEAT-013, FEAT-014, FEAT-015, FEAT-016, FEAT-017). However, downstream feature descriptions and baseline rules commit to capabilities that no feature in the list actually covers:

1. **Owner hand-off is promised by FEAT-020 but not covered by any story.**
   - Citing line: `docs/requirements.yaml:524` — `Let a user request deletion of their personal account with a grace window, owner hand-off, and cancellation path.`
   - What exists: STORY-046 (request), STORY-047 (cancel). No story implements the hand-off — STORY-046 AC-002 only *blocks* the sole-owner case.
   - Fix: add a story to FEAT-020 that lets the leaving user nominate another user to be promoted to owner as part of the deletion flow, or change FEAT-020's description to say "Deletion is blocked for the sole owner; owner hand-off is owned by FEAT-005/FEAT-012" and cross-reference.

2. **Trusted-browser list and individual revocation are implied by FEAT-015 but unstoried.**
   - Citing line: `docs/requirements.yaml:476` — `Change password, manage MFA factors, recovery codes, trusted browsers.`
   - What exists: STORY-039 AC-002 covers only "Clear all". No list view, no individual revoke.
   - Fix: add an AC (or a new story under FEAT-015) that lists `TrustedBrowser` rows with device/location/expires-at and supports individual deletion.

3. **Personal-token listing is promised by FEAT-016 but absent.**
   - Citing line: `docs/requirements.yaml:488` — `Create, list and revoke personal CLI tokens bound to the user's role.`
   - What exists: STORY-042 covers create and revoke. No list AC. Already captured as m-4.
   - Fix: add a list AC (or dedicated story) covering masked prefix, last-used, and creation time rendering.

---

## Empty-category disclosures

- BROKEN REFERENCES (FEAT/STORY/MODEL ids referenced but missing or mis-named): None found among `FEAT-013..021` / `STORY-035..048`. Every `data_models` entry resolves to a model in the `models:` section. Field-level naming mismatches are captured in C-1, C-2, M-1, M-4.
- MODE-AVAILABILITY ERRORS asserting wrong deployment mode: None found. The only mode-related issue is the *absence* of explicit declarations for FEAT-018 (see M-8); no feature makes a wrong saas/self_hosted claim.
- ROLE/SCOPE MISMATCHES (acting principal vs owner vs platform operator): None found. Every story acts on "me" (acting principal role (a) per line 37). STORY-046 correctly pulls in owning principals for notification (`each workspace owner`, line 4282). No story confuses platform operator with tenant roles.
