# EPIC-003 audit — API keys and provider credentials

Scope: `docs/requirements.yaml` EPIC-003 (line 106) covering FEAT-022..FEAT-028 and STORY-049..STORY-069, cross-referenced against the project baseline (lines 1–73), the models section (line 20712+), EPIC-010 (FEAT-130, FEAT-133), EPIC-011 (FEAT-138, FEAT-140, FEAT-160, FEAT-161) and EPIC-013 (FEAT-179).

Read-only audit. No changes to `requirements.yaml` are proposed here — only findings.

---

## Summary

EPIC-003 is structurally in place: a key-lifecycle feature (FEAT-022), a scopes/limits editor (FEAT-023), usage/anomaly signals (FEAT-024), BYOK provider credentials (FEAT-025), expiry/auto-revocation (FEAT-026), elevated-scope approvals (FEAT-027) and a leak emergency response (FEAT-028). However, the epic has real integrity problems:

- **Enum drift** in `KeyAnomaly.kind` and `BYOKCredential.status` — stories create values that the model never declares.
- **A duplicate/conflicting specification** of the API-key expiry reminder cadence between STORY-062 and STORY-064.
- **Two different scope taxonomies** in use for ApiKey (domain-scope strings like `chat.completions` vs. coarse `read`/`write`).
- **A BYOK rotation model that contradicts its own non-functional promise** — the model has no successor/grace fields yet every BYOK story claims "zero-downtime rotation with grace overlap".
- **Security-baseline narrowing** — STORY-056 conditions BYOK secret encryption on "residency region supports it", which is weaker than the project security baseline and does not match FEAT-133.
- **Notifications-model drift** in several stories that talk about "owner and admins" rather than the canonical `Resource.owner_user_id` / `Org.*_contact` / platform-operator taxonomy from line 37.
- **A broken inbound cross-reference**: FEAT-041 (EPIC-004) claims it drives "FEAT-022 signals" — anomaly detectors belong to FEAT-024.

None of the findings block the epic from being buildable, but several will cause silent divergence between what the data model allows and what stories assume at runtime. The Critical list should be closed before the first EPIC-003 story is pulled into a sprint.

---

## Critical

### C1. `KeyAnomaly.kind` enum does not include `"leak"` (docs/requirements.yaml:21156-21158, 5189)

Model definition:

> `docs/requirements.yaml:21156-21158`
> ```
> - name: kind
>   type: string
>   description: geo|spike|ua
> ```

STORY-067 uses it:

> `docs/requirements.yaml:5189`
> "A KeyAnomaly of type "leak" is recorded on the matching ApiKey"

**Problem.** The only feature that actually creates `KeyAnomaly` values other than `geo|spike|ua` is the leak-response flow in FEAT-028. The model enum contradicts the story, which means either the enum is stale or the leak event needs its own row type. Implementations will either silently accept any string (defeating the enum) or reject "leak" and crash the leak-response job.

**Suggested fix.** Extend `KeyAnomaly.kind` description to `geo|spike|ua|leak` at `docs/requirements.yaml:21158`. Alternatively introduce a separate `KeyLeakEvent` entity — but given STORY-055 and STORY-067 both use `KeyAnomaly`, the enum extension is the least invasive resolution.

### C2. `BYOKCredential.status` has no declared enum and stories use four disjoint taxonomies (docs/requirements.yaml:21187-21188, 4828, 4837, 4924, 4972, 4981)

Model:

> `docs/requirements.yaml:21187-21188`
> ```
> - name: status
>   type: string
> ```

Stories use incompatible values:

- STORY-056 AC-001: status `"active"` (`docs/requirements.yaml:4764-4766`)
- STORY-057 AC-001/AC-002: values `"active"` and `"degraded"` (`docs/requirements.yaml:4828, 4837`)
- STORY-059 AC-001: "status (healthy|expiring|invalid)" (`docs/requirements.yaml:4924`)
- STORY-061 AC-001/AC-002: `"overdue"` and `"healthy"` (`docs/requirements.yaml:4972, 4981`)

**Problem.** Four parallel status vocabularies (`active/revoked`, `active/degraded`, `healthy/expiring/invalid`, `overdue/healthy`) are used interchangeably. Any UI that implements STORY-059's filter will not recognise `degraded` from STORY-057, and the policy-overdue state from STORY-061 is orthogonal to STORY-057's probe state.

**Suggested fix.** At `docs/requirements.yaml:21188` declare an explicit enum, e.g. `active|degraded|overdue|invalid|revoked`, and rewrite STORY-059's display set to render each value. Decide whether probe-health (`degraded`), policy-overdue (`overdue`) and credential-validity (`invalid`) are three independent fields or one status with a precedence rule, and state that explicitly.

### C3. STORY-062 and STORY-064 are duplicates with conflicting cadences (docs/requirements.yaml:4989-5036, 5082-5113)

STORY-062:

> `docs/requirements.yaml:5005-5007`
> "A subsequent run at 3 days sends a second reminder with severity "high""

combined with AC-001 specifying "An ApiKey has expires_at in 14 days" — i.e. reminders at **T-14d and T-3d**.

STORY-064:

> `docs/requirements.yaml:5096-5097`
> "The scheduler crosses 30, 14, 7 or 1 day before expiry"

**Problem.** Both stories sit under FEAT-026 and both claim to be the canonical expiry-reminder story. They disagree on the cadence (14/3 vs. 30/14/7/1) and both write `ApiKeyExpiryNotice` rows, which means the dedupe key must somehow disambiguate between two cadences that target the same key. STORY-062 is also listed by FEAT-026 as its entry point while STORY-064 re-defines it.

**Suggested fix.** Pick one cadence and delete the other. The 30/14/7/1 cadence from STORY-064 is more defensible operationally; STORY-062 should either be deleted or rewritten as "surface 'expires in Nd' on the key list" so it covers only the UI pill at AC-002 and stops specifying a cadence.

### C4. FEAT-041 cross-references FEAT-022 when it should cite FEAT-024 (docs/requirements.yaml:749)

> `docs/requirements.yaml:749`
> "description: Configure the anomaly detectors that drive FEAT-022 signals — list, set thresholds, enable/disable by category."

**Problem.** FEAT-022 is "API key lifecycle" (create/rotate/revoke) and has no anomaly signals. FEAT-024 is "API key usage and anomalies" and owns `KeyAnomaly`. Any reader tracing "which feature configures the detectors that fire on an API key" will land on the wrong feature.

**Suggested fix.** At `docs/requirements.yaml:749` change the reference from FEAT-022 to FEAT-024.

---

## Major

### M1. BYOK rotation promises zero-downtime grace overlap but the model has no successor/grace fields (docs/requirements.yaml:21171-21208, 4857, 4907, 4930, 4954, 4988)

Non-functional text on every BYOK story:

> `docs/requirements.yaml:4857, 4907, 4930, 4954, 4988`
> "Provider credentials decrypt only at outbound-call time; rotation is zero-downtime with grace overlap"

But `BYOKCredential` only has `rotated_at` and `rotate_policy_days` at `docs/requirements.yaml:21189-21194`. No `successor_id`, no `grace_ends_at`, no dual-ciphertext field — unlike `ApiKey` which has `successor_id` (`docs/requirements.yaml:21131`) and `rotation_grace_ends` (`docs/requirements.yaml:21128`).

**Problem.** "Grace overlap" is unrealisable against the schema — STORY-056 AC-002 says "The new secret replaces the old", which is a hard swap. During the swap there is no second credential available for in-flight outbound requests.

**Suggested fix.** Add `successor_id: FK:BYOKCredential (nullable)` and `rotation_grace_ends: timestamp (nullable)` to `BYOKCredential` at `docs/requirements.yaml:21205` (before `relations:`). Update STORY-056 AC-002 to describe creating a successor credential and overlapping until `rotation_grace_ends`.

### M2. FEAT-023 description promises TTL edit but STORY-053 API does not expose it (docs/requirements.yaml:555, 4636-4648)

FEAT-023 description:

> `docs/requirements.yaml:555`
> "Edit scopes, allowed models, rate limits, IP allowlist, and TTL for a key."

STORY-053 API body:

> `docs/requirements.yaml:4639-4648`
> ```
> request:
>   body:
>     scopes: [string]
>     models: [string]
>     rate_limit_rpm: int
>     rate_limit_tpm: int
>     ip_allowlist: [string]
> ```

**Problem.** No `ttl_days` / `expires_at` in the PATCH body and no acceptance criterion covering TTL extension/shortening. Editing TTL is the most security-sensitive edit (extending past `key_max_ttl_days` in `ApiAccessConfig` at `docs/requirements.yaml:22403`) and is simply missing.

**Suggested fix.** Add `expires_at: timestamp` (or `ttl_days: int`) to the PATCH body at `docs/requirements.yaml:4648`, and add an AC covering "cannot extend past `ApiAccessConfig.key_max_ttl_days`".

### M3. BYOKCredential has `name` but STORY-060 edits `label` (docs/requirements.yaml:21181-21182, 4933-4947)

Model:

> `docs/requirements.yaml:21181-21182`
> ```
> - name: name
>   type: string
> ```

Story:

> `docs/requirements.yaml:4933-4947`
> "Edit a BYOK credential label … BYOKCredential.label is updated"

STORY-059 at `docs/requirements.yaml:4924` also says "I see each credential with label, provider, last_rotated_at…".

**Problem.** The field is `name` in the schema. Stories use `label` as if it were a defined field. Implementations either alias the two names or add `label` and leave `name` unused.

**Suggested fix.** Pick one. Rename `BYOKCredential.name` to `BYOKCredential.label` at `docs/requirements.yaml:21181`, or update STORY-059/STORY-060 to use `name`. `label` reads more like a display concept than a stable identifier — prefer `label` for the BYOK case.

### M4. BYOKCredential field is `rotated_at`; stories use `last_rotated_at` (docs/requirements.yaml:21192, 4924, 4968, 4981)

Model:

> `docs/requirements.yaml:21192-21194`
> ```
> - name: rotated_at
>   type: timestamp
>   nullable: true
> ```

Stories:

> `docs/requirements.yaml:4924` "label, provider, last_rotated_at, status"
> `docs/requirements.yaml:4968` "rotate_policy_days 90 and last_rotated_at 95 days ago"
> `docs/requirements.yaml:4981` "last_rotated_at is updated"

**Suggested fix.** Rename the model field to `last_rotated_at` at `docs/requirements.yaml:21192`, or update every story reference. `last_rotated_at` is unambiguous (it's the most recent rotation); `rotated_at` reads like "has ever been rotated".

### M5. Scope taxonomy drift — STORY-049 uses domain scopes, STORY-052/065 use coarse `read`/`write` (docs/requirements.yaml:4419, 4581, 5126-5128)

STORY-049 AC-001:

> `docs/requirements.yaml:4419`
> 'scopes ["chat.completions", "embeddings"]'

STORY-052 AC-001 (filter):

> `docs/requirements.yaml:4581`
> 'I filter by team "copilot", scope "read"'

STORY-065 AC-001:

> `docs/requirements.yaml:5126-5128`
> 'My ApiKey has scope "read" … I request scope "write" with reason and duration'

**Problem.** The project has two scope systems inside one field. The base taxonomy is routes (`chat.completions`, `embeddings`, `cache.read`). The elevated-scope story talks about access levels (`read`/`write`). A key with `chat.completions` cannot meaningfully be elevated to "write"; the store stores an unconstrained `json` blob so nothing catches the inconsistency.

**Suggested fix.** Commit to the domain-scope vocabulary (`chat.completions`, `embeddings`, `cache.read`, `files.write`, etc.) and rewrite STORY-065 AC-001 to read: "My ApiKey has `chat.completions` — I request `cache.write` for reason X and duration Y". Also rewrite STORY-052's filter example.

### M6. FEAT-027 elevated-scope state has no home in the data model (docs/requirements.yaml:21099-21100, 5150-5165)

`ApiKey` stores:

> `docs/requirements.yaml:21099-21100`
> ```
> - name: scopes
>   type: json
> ```

STORY-066 AC-001/AC-002:

> `docs/requirements.yaml:5155-5157, 5163-5165`
> "The ApiKey's effective scope is elevated until the expiry … The ApiKey returns to its base scope"

**Problem.** `ApiKey.scopes` is a single json column. There is nowhere to record **both** base scope and the time-bounded elevated overlay. When the elevation expires, which value is the "base" to revert to? The Approval record captures the request but not the base-scope snapshot. This is the same class of problem as the BYOK grace overlap — stories assume a dual-state representation that the schema does not model.

**Suggested fix.** Either (a) add `ApiKey.base_scopes: json` plus `ApiKey.elevated_scopes: json (nullable)` and `ApiKey.elevated_until: timestamp (nullable)` at `docs/requirements.yaml:21099`, or (b) state explicitly in STORY-066 that the base scope is the Approval's `context.base_scopes` snapshot. Option (a) is cleaner; option (b) is cheaper.

### M7. FEAT-025 is P0 but its entry story STORY-056 is P1 (docs/requirements.yaml:575, 4755)

> `docs/requirements.yaml:575` "priority: P0" (FEAT-025)
> `docs/requirements.yaml:4755` "priority: P1" (STORY-056 "Register and rotate a BYOK provider credential")

**Problem.** You cannot ship a P0 feature whose primary story is P1 — STORY-057..061 all `depends_on` STORY-056. Either the feature is not actually P0 or STORY-056 is mispriced.

**Suggested fix.** Raise STORY-056 to P0 at `docs/requirements.yaml:4755`. BYOK credentialling is genuinely P0 for the gateway to serve a BYOK-enabled org at all.

### M8. STORY-056 narrows the project security baseline on CMK (docs/requirements.yaml:4807, 33, 1675)

Story non-functional:

> `docs/requirements.yaml:4807`
> "Secret encrypted at rest with workspace CMK when residency region supports it"

Project security baseline:

> `docs/requirements.yaml:33`
> "Secrets live in the configured KMS (with FEAT-133 CMK where enabled) and never appear in logs, telemetry or persisted payloads."

FEAT-133 (CMK):

> `docs/requirements.yaml:1675`
> "Bring-your-own CMK setup, revocation, and multi-CMK per data class … In self_hosted mode there is no Antirion envelope key — the install's own KMS is the root of trust, revocation strictly fails closed with no Antirion-side unwrap path".

**Problem.** The story's conditional ("when residency region supports it") invents a notion — region-dependent CMK availability — that FEAT-133 never describes. Read literally, if the residency region "does not support" CMK, STORY-056 allows secrets to be stored under the platform KMS only. That may be correct (baseline says "KMS (with FEAT-133 CMK where enabled)"), but the phrasing reads like a weaker guarantee. Worse, it conflicts with FEAT-133's self_hosted fail-closed policy: if the BYOK flow silently falls back to platform KMS when CMK is unavailable, FEAT-133's "revocation strictly fails closed" guarantee breaks for BYOK data.

**Suggested fix.** At `docs/requirements.yaml:4807` restate as "Secret stored in the configured KMS and wrapped with the workspace CMK when FEAT-133 CMK is active for the `byok_credential` data class; if the CMK is revoked, outbound calls using this credential fail closed per FEAT-133." Remove the "residency region supports it" condition.

### M9. Expiry-warning stories drift from `notifications_model` (docs/requirements.yaml:37-38, 5005-5006, 5097-5099, 4973)

Canonical audience taxonomy:

> `docs/requirements.yaml:37`
> "(a) the acting principal (user_id), (b) the owning principal on the resource (Resource.owner_user_id or Team.owner), (c) the org-scoped contact fields on Org (security_contact, billing_contact, finance_contact, privacy_officer, primary_contact), (d) the platform operator …"

Divergences in EPIC-003:

> `docs/requirements.yaml:5005-5006` "An email is sent to the key owner and to every user with role admin or owner"
> `docs/requirements.yaml:5098` "A warning email is sent to the owner and admins at each checkpoint"
> `docs/requirements.yaml:4973` "An alert is raised to the security contact"

**Problem.** None of these use the canonical role citations. "Every user with role admin or owner" is an ad-hoc audience that does not appear in the notifications_model. STORY-061 ("security contact") is close but drops the saas/self_hosted fallback clause that FEAT-025/FEAT-028 siblings carry.

**Suggested fix.** Rewrite each as `Resource.owner_user_id` plus `Org.security_contact` with the canonical fallback clause — the pattern used correctly at STORY-069 (`docs/requirements.yaml:5250`) and STORY-305 (`docs/requirements.yaml:15181-15183`).

### M10. STORY-053 AC-002 uses "SafetyEvent or AuditLog" disjunctively (docs/requirements.yaml:4635)

> `docs/requirements.yaml:4635`
> "A SafetyEvent or AuditLog entry records the allowlist violation"

**Problem.** `SafetyEvent` is for content-safety signals (PII, prompt injection, jailbreak per EPIC-007). An IP-allowlist violation is an access-control event, not a safety event. "Or" leaves the implementation free to write neither or either.

**Suggested fix.** At `docs/requirements.yaml:4635` change to "An AuditLog entry with action `apikey.ip_allowlist.violation` is recorded".

### M11. STORY-323 (edge auth) does not describe dual-hash matching during rotation grace (docs/requirements.yaml:15873-15933, 21131, 21128)

STORY-050 guarantees:

> `docs/requirements.yaml:4524-4525`
> "Both successor and predecessor hashes are stored; authorization compares against both during grace"

STORY-323 (FEAT-138 edge auth) walks through missing/valid/wrong-scope/revoked cases at `docs/requirements.yaml:15881-15916` but never mentions the `rotating` status or grace-window dual-lookup.

**Problem.** The edge is where the dual-hash logic has to live; omitting it from STORY-323 means the grace-window guarantee in STORY-050 is unimplementable by any reader who only looks at EPIC-011.

**Suggested fix.** Add an AC to STORY-323 at `docs/requirements.yaml:15916`: "Key in `rotating` status — both predecessor `secret_hash` and successor `secret_hash` are valid until `rotation_grace_ends`; after that, only the successor is."

---

## Minor

### m1. FEAT-022 description lists lifecycle actions but FEAT-022 also contains STORY-052 (list) (docs/requirements.yaml:541, 547)

> `docs/requirements.yaml:541`
> "Create, rotate with grace window, and revoke gateway API keys."

STORY-052 is "List API keys with filters". Either the description should mention list/browse, or STORY-052 should move to a "surfaces" feature. Very low priority — description strings rarely bite implementations.

### m2. FEAT-025 description lists only register/rotate but FEAT-025 contains test/delete/list/label/policy stories (docs/requirements.yaml:574, 577-582)

> `docs/requirements.yaml:574`
> "Register and rotate upstream provider credentials used for outbound calls."

Same pattern as m1 — the description under-sells the feature's six stories.

### m3. STORY-055 references an "anomaly ticker" that is never defined elsewhere (docs/requirements.yaml:4732)

> `docs/requirements.yaml:4732`
> "It appears in the anomaly ticker and the key's detail panel"

No other file or feature defines an "anomaly ticker" surface. It is not in EPIC-004 (observability) or EPIC-009 (alerts).

**Suggested fix.** Either drop "anomaly ticker" (keep only "the key's detail panel"), or declare the ticker as a UI element on the Gateway overview (FEAT-029) or on the key list (FEAT-022).

### m4. STORY-067 AC does not encode the self_hosted air-gapped 404 behaviour from FEAT-028's description (docs/requirements.yaml:608, 5181-5199)

FEAT-028 description (line 608) says:

> "air-gapped installs must leave it disabled — in that case STORY-067's endpoint returns 404 and the feature degrades to manual revocation via FEAT-022"

STORY-067's ACs (lines 5181-5199) only cover "valid signed" and "invalid signature" — no AC covers the air-gapped / self_hosted-disabled path. Readers implementing the story from ACs alone will miss the 404.

**Suggested fix.** Add an AC to STORY-067: "Air-gapped or disabled inbound endpoint — the endpoint returns 404 and no state is written."

### m5. STORY-068 omits the AuditLog entries that STORY-069 promises (docs/requirements.yaml:5216-5231, 5253)

STORY-068 walks through auto-revoke and successor-mint but lists only `ApiKey` and `KeyAnomaly` in `data_models` (line 5227-5228) and has no explicit audit AC. STORY-069 carries the audit (line 5253) but depends on STORY-068. This is consistent, but anyone reading STORY-068 in isolation will implement revoke + rotate without emitting audit rows. Minor — follow-on audit in STORY-069 saves it.

### m6. STORY-051 revoke uses single-click confirm; destructive policy is silent on individual key revoke (docs/requirements.yaml:5, 4542)

Project policy (line 5) enumerates "rotate org secret" as typed-name but does not mention individual-key revoke. STORY-051 uses a simple click-confirm with reason — arguably fine, since per-key revocation is the recovery action, not the destructive one. Flagging for awareness only.

### m7. FEAT-027 Approval.kind `"key-elevated-scope"` is shared with FEAT-160 break-glass creation (docs/requirements.yaml:5130, 17598, 22628)

Both features create `Approval` rows with `kind="key-elevated-scope"`:

> `docs/requirements.yaml:5130` (FEAT-027, STORY-065) — elevate scope on an **existing** ApiKey
> `docs/requirements.yaml:17598` (FEAT-160, STORY-377) — create a **new** break-glass ApiKey

**Problem.** Two different semantics share one discriminator. Approvers on the review surface see a mixed queue, and the Approval's `target_id` distinguishes the two only by whether the referenced ApiKey already exists.

**Suggested fix.** Introduce a second Approval kind, e.g. `break-glass-key-create`, at `docs/requirements.yaml:22628` and update STORY-377 at `docs/requirements.yaml:17598` to use it.

### m8. `STORY-065` and `STORY-066` do not cite a notifications audience (docs/requirements.yaml:5114-5172)

Every other approval-bearing story in the file names the audience (e.g. STORY-377 names Org.security_contact + Antirion trust_and_safety). STORY-065/066 emit no notification at all. Either the elevation flow genuinely has no notifications (unlikely, since it's a privilege change) or the audience AC is missing.

**Suggested fix.** Add a notification AC to STORY-066 mirroring STORY-377 at `docs/requirements.yaml:17599-17600`.

### m9. FEAT-028 does not declare a top-level `mode:` key (docs/requirements.yaml:605-613, 36)

Per project baseline (line 36): "Every feature that differs in scope, availability or data shape between the two modes declares its mode availability explicitly in its description." FEAT-028 declares mode differences in its description prose (line 608) but does not add a `mode: both` key. Other EPICs (EPIC-013 features, lines 2013, 2024, 2033, …) use an explicit `mode:` key. Inconsistent but within the letter of the baseline (description is the declaration).

---

## Cross-epic issues

### X1. BYOK residency + CMK wrapping collision with EPIC-010 (docs/requirements.yaml:4807, 1675, 33)

Covered in detail as M8. The cross-epic impact is that FEAT-133's "CMK per data class" concept is not wired to BYOK explicitly — BYOK is not listed as one of the data classes that CMK can wrap. EPIC-010 FEAT-133 should enumerate BYOK secret material as a CMK-wrappable class.

**Suggested fix.** Add "BYOK credential ciphertext" to the FEAT-133 data-class enumeration at `docs/requirements.yaml:1675` (or in the CMK model fields).

### X2. FEAT-130 residency enforcement does not cover BYOK at-rest storage region (docs/requirements.yaml:1653-1656, 21171-21208)

FEAT-130 (STORY-305) enforces residency at outbound-call time only. The BYOK ciphertext is stored in the org's region via `Org.region`, but neither STORY-056 nor FEAT-130 explicitly says "BYOK ciphertext must be stored in the residency region". Today this is implicit through Postgres placement; tomorrow when BYOK is replicated for read-locality it will silently cross the boundary.

**Suggested fix.** Add an AC to STORY-056 or a bullet to STORY-305: "BYOK credential ciphertext is stored only in the ResidencyConfig region".

### X3. FEAT-138 edge auth does not acknowledge the `rotating` state nor the elevated-scope overlay

Covered as M11 (rotation) and M6 (elevated scope). Whichever representation EPIC-003 picks for elevated scope, FEAT-138 STORY-323 has to match it.

### X4. FEAT-102 notification drift in EPIC-003 stories

STORY-061, STORY-062, STORY-064 bypass FEAT-102's canonical notification channel routing by specifying audiences in free-text (`admins`, `key owner`) rather than roles. Covered as M9; the cross-epic impact is that FEAT-102's `NotificationPreference` resolution machinery will receive audiences it cannot resolve.

### X5. `Org.owner` is referenced in STORY-069 (and many other stories) but does not exist as an Org field (docs/requirements.yaml:20713-20761, 5250)

STORY-069 AC-001:

> `docs/requirements.yaml:5250`
> "when security_contact is unset the notification falls back to Org.owner in saas and platform admin in self_hosted"

`Org` model (lines 20713-20761) has `billing_contact`, `tech_contact`, `security_contact` but no `owner` / `owner_user_id` / `primary_contact` / `finance_contact` / `privacy_officer` — all of which `notifications_model` (line 37) and many stories reference.

**Suggested fix.** Add `owner_user_id: FK:User`, `primary_contact: string`, `finance_contact: string`, `privacy_officer: string` to the `Org` model at `docs/requirements.yaml:20756`. This is a global fix, not EPIC-003-local; flagged here because STORY-069 is the EPIC-003 touchpoint.

---

## Missing / dangling references

This section enumerates every FEAT/STORY id cited by EPIC-003 content (feature/story text, ACs, dependencies, description prose) and verifies it exists. It also flags implied dependencies the narrative assumes but never declares, and features the epic's scope promises but omits.

### a) Cited ids with no definition

None. Every FEAT-xxx and STORY-xxx explicitly named inside EPIC-003's feature descriptions, stories and ACs resolves to a real entry:

| Cited id | Citing line(s) | Definition line |
| --- | --- | --- |
| FEAT-022 | `requirements.yaml:608, 749` | `requirements.yaml:538` (definition). Note: `:749` is a broken reference to the wrong feature — see C4, not a dangling one. |
| FEAT-179 | `requirements.yaml:608, 5252` | `requirements.yaml:2099` |
| STORY-011 (dep from STORY-049) | `requirements.yaml:4411` | `requirements.yaml:2674` |
| STORY-049 | `requirements.yaml:544, 4485, 4535, 4616, 4672` | `requirements.yaml:4402` |
| STORY-050 | `requirements.yaml:545, 5103` | `requirements.yaml:4476` |
| STORY-051..069 | per feature stories list | `requirements.yaml:4526–5232` |
| STORY-054 (dep from STORY-055) | `requirements.yaml:4722` | `requirements.yaml:4663` |
| STORY-056 (dep from STORY-057, 058) | `requirements.yaml:4818, 4867` | `requirements.yaml:4748` |
| STORY-062 (dep from STORY-063) | `requirements.yaml:5045` | `requirements.yaml:4989` |
| STORY-065 (dep from STORY-066) | `requirements.yaml:5147` | `requirements.yaml:5114` |
| STORY-067 (dep from STORY-068) | `requirements.yaml:5214` | `requirements.yaml:5173` |
| STORY-068 (dep from STORY-069) | `requirements.yaml:5241` | `requirements.yaml:5205` |

### b) Implied dependencies not declared

- **STORY-065** and **STORY-066** (FEAT-027, elevated scope) do not declare `depends_on: [STORY-049]` but AC-001 requires "My ApiKey has scope 'read'" — i.e. an ApiKey must exist. Add `depends_on: [STORY-049]` at `requirements.yaml:5122` and `requirements.yaml:5148`.
- **STORY-067..069** (FEAT-028, leak response) do not declare `depends_on: [STORY-049]` but auto-revoke/auto-rotate assume an ApiKey exists. Add `depends_on: [STORY-049]` at `requirements.yaml:5180`.
- **STORY-056** (FEAT-025, BYOK register) does not declare `depends_on: [STORY-225 or analogous]` against provider model setup; probably out of scope here, but worth flagging that `BYOKCredential.provider_id` references `Provider` without a story wire-up dependency. Likely covered transitively by EPIC-005.
- **STORY-323..326** (FEAT-138) logically depend on the existence of ApiKey (STORY-049) but declare no `depends_on` — not an EPIC-003 fix, but it is the reason M11 exists.

### c) Scope promises absent from the features list

EPIC-003 description at `requirements.yaml:108` reads: "Gateway key lifecycle with scopes, limits, rotation, audit; BYOK for upstream providers." The features list covers every clause (lifecycle → FEAT-022, scopes/limits → FEAT-023, rotation → FEAT-022, audit → handled transitively by AuditLog entries in every story, BYOK → FEAT-025). No scope promise is orphaned.

However the epic implicitly promises and **does not feature** two capabilities that appear in stories:

- **Elevated-scope state representation on ApiKey** (needed by STORY-066). No feature owns the new ApiKey fields. Either FEAT-023 should absorb it or a new feature is warranted.
- **BYOK rotation policy management** (needed by STORY-061 which uses `rotate_policy_days`). FEAT-025 covers the enforcement loop, but no story actually sets or edits `rotate_policy_days` on a credential. STORY-060 edits label only. This is a genuine gap: the rotation policy is observable but not editable.

**Suggested fix.** Add a story under FEAT-025 covering "Set rotation policy on a BYOK credential" with a PATCH body containing `rotate_policy_days`.

### d) Features referenced but typed incorrectly

- **FEAT-041** (`requirements.yaml:749`) cites FEAT-022 but means FEAT-024 — covered as C4. This is an *external* reference to EPIC-003 that is broken.

---

## Appendix — structural integrity spot-check

Every `ApiKey.status` value used in EPIC-003 stories maps to the enum `active|rotating|revoked|expired` at `requirements.yaml:21113-21114`. `AuditLog.actor_type` value `"system"` used by STORY-063 matches the enum `user|sso|system|service` at `requirements.yaml:22526`. `Approval.kind` value `"key-elevated-scope"` used by STORY-065 matches the enum at `requirements.yaml:22628`. `KeyAnomaly.kind` value `"geo"` used by STORY-055 matches; value `"leak"` used by STORY-067 does not (C1). No other enum mismatches were found inside EPIC-003.
