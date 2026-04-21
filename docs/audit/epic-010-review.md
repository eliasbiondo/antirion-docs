# EPIC-010 Workspace administration — requirements.yaml review

Scope: EPIC-010 (line 226) and its 28 features FEAT-107..FEAT-134 (lines 1419..1687), covering stories STORY-247..STORY-311 (lines 12917..15337). Cross-referenced against the project baseline (lines 1..73), the models section (lines 20712..end), and EPIC-001 (identity), EPIC-003 (keys/BYOK), EPIC-007 (safety/redaction), EPIC-008 (billing), EPIC-012 (platform foundations), EPIC-013 (platform operator).

## Summary

EPIC-010 is the largest epic in the spec and its internal cohesion is already high — feature/story numbering is consecutive, mode-availability text is present on the features that need it, and the destructive-action confirmation policy is applied in most of the danger-zone stories. The issues below are concentrated in three areas:

1. **Data-model drift** — several stories refer to fields, enums, and shapes that do not exist on the models they cite (AlertRule.owner_user_id, Webhook.owner_user_id, Model.paused, ResidencyConfig.pinned_at / pinned_by / source, the baseline-declared Org contact fields, AuditLog.prev_hash/hash chain).
2. **Cross-reference errors** — FEAT-112 cites a wrong feature/story pair for first-run residency pinning, and FEAT-111 cites a wrong feature as the canonical home of the org IP allowlist.
3. **Mode/role gating missing** — FEAT-107, FEAT-127, and parts of FEAT-119 do not reflect the saas-vs-self_hosted split that is mandatory for surfaces that change between modes.

A standout correctness risk is FEAT-109 STORY-252's SCIM deprovision cascade, which never invalidates active Sessions, TrustedBrowsers, or outstanding Invites for the deprovisioned user — so a user offboarded via IdP can continue to hold an authenticated browser session until its TTL expires.

## Critical

### C-1. FEAT-112 cites the wrong feature and a wrong story for first-run residency pinning

- Location: line 1473.
- Quote: "The region is set once at first-run (FEAT-163/STORY-409) and is immutable for the life of the workspace".
- Problem: FEAT-163 is "Public status page" (line 1942); STORY-409 is "Cross-tenant roster in saas mode" and belongs to FEAT-172 (line 19194..19195). Neither entity has anything to do with residency pinning. The actual first-run residency pinning lives in FEAT-162 "First-run onboarding checklist" STORY-387 "Pin data residency region before any tenant data is written" (line 18011..18087), with the self_hosted variant wired in FEAT-177 STORY-423 (line 20064). Cross-verified against FEAT-177 description at line 2081 ("residency label pinning (feeds FEAT-112)"), which confirms the correct dependency is FEAT-162 (saas) and FEAT-177 (self_hosted).
- Fix: replace "(FEAT-163/STORY-409)" with "(FEAT-162/STORY-387 in saas, FEAT-177/STORY-423 in self_hosted)".

### C-2. Org.owner and three Org contact fields named in the notifications_model do not exist on the Org model

- Locations: baseline notifications_model lines 37..38; Org model lines 20713..20756.
- Quote (baseline): "(c) the org-scoped contact fields on Org (security_contact, billing_contact, finance_contact, privacy_officer, primary_contact)" and "when unset in saas the event falls back to Org.owner".
- Problem: Org.fields contains `security_contact`, `billing_contact`, and a non-baseline `tech_contact`; it has no `finance_contact`, no `privacy_officer`, no `primary_contact`, and no `owner` (the workspace owner is only reachable by a role lookup on User). Stories inside EPIC-010 assume these fields exist and refer to them by name (STORY-263 line 13715 uses Org.security_contact → Org.owner fallback; STORY-285 line 14691 uses Org.privacy_officer → Org.owner fallback; STORY-289 line 14798; STORY-290 line 14825; STORY-300 line 15057; STORY-305 line 15181). FEAT-125/126 descriptions (lines 1604, 1613) also rely on Org.privacy_officer. Without these fields, the notification-routing contract the stories promise cannot be satisfied by queries against the Org row.
- Fix: add `finance_contact`, `privacy_officer`, `primary_contact` (type string, nullable) to the Org model; decide whether `tech_contact` should be removed or added to the baseline roster; add an `owner_user_id: FK:User` or document that Org.owner resolves via User.role="owner".

### C-3. Stories reference model fields that do not exist

- STORY-252 AC-001 (line 13183): "AlertRule.owner_user_id is reassigned to the team lead". AlertRule model (lines 22157..22212) has `team_id` and `oncall_schedule_id` but no `owner_user_id`. The cascade as written cannot execute.
- STORY-300 AC-001 (line 15057): "A notification is delivered to Webhook.owner_user_id and Org.security_contact". Webhook model (lines 22457..22485) has no `owner_user_id` field.
- STORY-276 AC-001 (line 14325): "Model.paused becomes true ... Subsequent requests targeting the model get a 503". Model (lines 21229..21297) has a `status` enum (`enabled|disabled|preview|deprecated|restricted`) but no `paused` bool and no `paused` value in the status enum.
- STORY-256 AC-001 (line 13359): the view must surface "the timestamp it was pinned, the principal who pinned it and the source (first_run or install_config)". ResidencyConfig (lines 22413..22440) has no `pinned_at`, `pinned_by_user_id`, or `source` fields — the "source" value is promised but unstored.
- STORY-266 AC-001 (line 13846): "Each row stores prev_hash and a hash over (prev_hash, payload, signing_key_id)". AuditLog model (lines 22511..22542) has no `prev_hash`, no `hash`, no `signing_key_id`. The tamper-proofing contract has no storage.
- Fix for each: add the missing fields to the relevant model, or rewrite the story to reference fields that actually exist (for example, reassign AlertRule by `team_id` → Team.lead_user_id instead of a per-rule owner).

### C-4. FEAT-133 CMK revocation semantics contradict themselves between the feature description and the story NFRs

- Locations: FEAT-133 description line 1675; STORY-308 line 15266; STORY-309 line 15290; STORY-310 line 15313; STORY-309 AC-001 line 15283.
- Quote (feature): "In saas mode the CMK is a customer KMS key bound into Antirion's envelope encryption; revocation can fall back to Antirion's emergency envelope key to prevent accidental tenant lock-out ... In self_hosted mode there is no Antirion envelope key — ... revocation strictly fails closed".
- Quote (story NFR, repeated on STORY-308/309/310): "CMK revocation fails closed — traffic requiring the revoked key stops rather than falling back to a platform key".
- Quote (STORY-309 AC-001): "Writes fall back to the emergency key or are paused".
- Problem: three different contracts are in the same feature. The description says saas-fallback-permitted, self_hosted-fails-closed; the NFR copy-pasted on every story says fails-closed with no mode distinction; STORY-309 AC-001 says fallback is allowed in every mode. Implementors cannot tell which contract to honor, and the stories' NFR is incompatible with the description in saas mode.
- Fix: keep the description's mode split as the contract. Replace the blanket story NFR with two variants (fails closed in self_hosted; falls back to Antirion emergency envelope key with audit and trust_and_safety notification in saas). Rewrite STORY-309 AC-001 to branch on deployment mode.

### C-5. SCIM deprovision cascade (STORY-252) leaves active sessions, trusted browsers and pending invites untouched

- Location: STORY-252 lines 13160..13195.
- Quote: "All ApiKey rows owned by the user are revoked / PersonalToken rows are revoked / Pending Approval rows assigned to the user are reassigned to the team lead / Active PiiUnredactRequest reveals are expired immediately / UserBudget rows are closed / AlertRule.owner_user_id is reassigned to the team lead".
- Problem: the cascade misses three access paths that the other EPIC-001 features declare exist: `Session` (FEAT-003 / model 20867), `TrustedBrowser` (model 20896 — trusted for up to 30 days of MFA bypass), and pending `Invite` rows (FEAT-004 / model 20951, addressed by email so a deprovisioned address still has a valid invite token in flight). An IdP-driven offboard therefore does not terminate the user's live browser session or trusted-browser record, and does not revoke pending invites that resolve to their email. Security officer's "so_that: no orphan access remains" is not satisfied by the criteria as written.
- Fix: add AC clauses to revoke `Session` rows for the user, delete `TrustedBrowser` rows, and mark any pending `Invite` for the deprovisioned email as `revoked`. Also decide the behavior when `Team.lead_user_id` is null (the reassignment target used throughout this story).

## Major

### M-1. FEAT-107 mixes dual-mode identity with saas-only billing and declares no mode availability

- Locations: FEAT-107 lines 1419..1430; STORY-248 lines 12981..13021; EPIC-008 FEAT-095 line 1293, FEAT-096 line 1303, FEAT-098 line 1322.
- Quote (FEAT-107): "Org name, slug, logo, contacts, timezone; plan, commitment, invoices, payment method."
- Quote (FEAT-095): "Available in saas mode only — Antirion invoices the workspace. In self_hosted mode the Antirion commercial relationship is the license (FEAT-175), not a metered invoice, and every endpoint and screen under this feature returns 404."
- Problem: the plan/commitment/invoices halves of FEAT-107 are saas-only under the rule set that EPIC-008 declares explicitly. FEAT-107 states no mode availability, which violates the deployment_modes rule in the baseline (line 36) that every feature that differs in scope between modes must declare mode availability. STORY-248 (View plan, commitment and invoices) has no mode gate in its AC and calls `/api/billing/contract` and `/api/billing/invoices`, but those endpoints collapse to the license view in self_hosted per FEAT-175.
- Fix: split FEAT-107 into a workspace-identity feature (both modes) and a plan/billing feature (saas only, deferring to FEAT-175 in self_hosted), or add an explicit mode-availability paragraph to FEAT-107 that excludes the billing half from self_hosted and routes self_hosted callers to FEAT-175.

### M-2. ResidencyConfig.migration_ends_at contradicts FEAT-112's "immutable, no migration path"

- Locations: FEAT-112 line 1473; STORY-256 AC-002 line 13369; ResidencyConfig model lines 22413..22440 (field `migration_ends_at` at line 22438).
- Quote (FEAT-112): "immutable for the life of the workspace — there is no migration, rotation or change path".
- Quote (STORY-256 AC-002): "PATCH /api/residency or POST /api/residency/migrate or any variant ... returns 404 — change paths do not exist on this install".
- Problem: ResidencyConfig still declares a `migration_ends_at: timestamp nullable` field. That field has no legitimate use once migration is impossible; reviewers reading the model will infer a migration window exists when the feature says none does.
- Fix: drop `migration_ends_at` from ResidencyConfig. Add the pinning-evidence fields the story asks for (`pinned_at`, `pinned_by_user_id`, `source` in {first_run, install_config}).

### M-3. Dual org-IP-allowlist storage and endpoints

- Locations: FEAT-111 line 1463 claims the canonical org IP allowlist lives in FEAT-107; STORY-254 AC-001 (line 13258..13266) writes to `/api/org/api-access` with `ip_allowlist_enabled` and `ip_cidrs` on ApiAccessConfig (lines 22386..22412); FEAT-121 + STORY-278 (line 14420) write to `/api/org/ip-allowlist` with `cidrs` and `mode` on OrgIpAllowlist (lines 23136..23150).
- Quote (FEAT-111): "The canonical org-level IP allowlist lives in FEAT-107."
- Problem: three contradictions at once. (a) FEAT-107's description (line 1422) does not mention an IP allowlist at all; (b) ApiAccessConfig and OrgIpAllowlist both store it under different field names (`ip_cidrs` vs `cidrs`, plus a separate `mode`/`ip_allowlist_enabled` toggle); (c) two different HTTP endpoints write it. A single edge enforcer cannot resolve which source is authoritative.
- Fix: pick OrgIpAllowlist + `/api/org/ip-allowlist` as the canonical home (matches the dedicated FEAT-121 scope and the `dry-run` mode that ApiAccessConfig does not capture cleanly). Remove `ip_allowlist_enabled` and `ip_cidrs` from ApiAccessConfig. Update FEAT-111's cross-reference to point at FEAT-121 and drop the false claim about FEAT-107.

### M-4. FEAT-127 DR stories put workspace admin/owner on the action path even where the feature description reserves it for Antirion SRE in saas

- Locations: FEAT-127 description line 1623; STORY-292..STORY-296 lines 14856..14971.
- Quote (FEAT-127): "In saas mode Antirion SRE owns backups, quarterly DR drills and the execute-restore action; tenant-visible surfaces are read-only timelines plus a 'request restore' button that opens an Antirion-side ticket."
- Quote (STORY-294 narrative): "as_a: workspace owner / i_want: to trigger a production restore in an emergency / I click 'Restore' and type the org slug and a reason / The restore begins".
- Quote (STORY-296 narrative): "as_a: workspace admin / i_want: to schedule DR drills".
- Problem: the stories do not reflect the saas role split. In saas a workspace owner must only reach a "request restore" ticket surface, and DR drill cadence is set by Antirion SRE, not the tenant. As written, a tenant in saas can trigger execute-restore. The stories also do not mention the request-restore ticket flow at all.
- Fix: rewrite STORY-294 and STORY-296 to declare mode-gated AC pairs: in saas, workspace owner can only submit a restore-request ticket and the AC is "an Antirion-side ticket is opened and platform operator is paged"; in self_hosted, the original execute-restore AC applies. Do the same for drill-scheduling.

### M-5. AuditLog has no hash-chain fields although FEAT-115 STORY-266 and the baseline security clause both require tamper-evidence

- Locations: baseline security line 33 ("Audit log writes are append-only with tamper-evident hashing"); FEAT-115 line 1504; STORY-266 AC-001 lines 13841..13846; AuditLog model lines 22511..22542.
- Quote (STORY-266 AC-001): "Each row stores prev_hash and a hash over (prev_hash, payload, signing_key_id)".
- Problem: AuditLog has fields for `id, org_id, t, actor_user_id, actor_type, action, target_type, target_id, context, ip, user_agent`. There is nowhere to write `prev_hash`, `hash`, or `signing_key_id`. The tamper-evident-hashing baseline requirement has no storage at all.
- Fix: add `prev_hash`, `hash`, `signing_key_id` (nullable on the genesis row) to AuditLog, or declare a sibling model AuditLogHashChain keyed 1:1 to AuditLog.

### M-6. STORY-275 AC-003 "Rotate org signing secret" does not require typed confirmation, which breaks destructive_action_confirmation_policy

- Locations: baseline line 5 ("High-impact destructive actions (... rotate org secret) require the user to type the target's name or slug to confirm"); STORY-275 AC-003 lines 14263..14272; API `/api/danger/secret/rotate` at line 14294.
- Quote (STORY-275 AC-003): "I click 'Rotate signing secret' and confirm / A new signing secret is generated and shown once".
- Problem: the policy lists "rotate org secret" as high-impact and demands typed-slug confirmation. Other actions in the same story (purge caches at AC-002 line 14258) do require the slug; AC-003 omits it. The rotate endpoint body has no `confirm_slug` parameter.
- Fix: add a typed-slug confirm gate to STORY-275 AC-003 and add `confirm_slug: string` to the `/api/danger/secret/rotate` request body.

### M-7. FEAT-131 geoip fail-open default is at odds with the spirit of the fail-closed baseline

- Locations: baseline multi_region_and_dr line 29 ("fails closed rather than crossing a residency boundary"); FEAT-131 line 1660; STORY-306 AC-002 lines 15208..15214.
- Quote (STORY-306 AC-002): "The geoip database is unavailable / A request arrives / The request is allowed and a warning is logged (configurable to fail-closed)".
- Problem: the baseline fail-closed rule is framed around residency, not geo, so this is not a strict contradiction. But a security-boundary policy that defaults open on data-source failure is a footgun — the admin has to know to reconfigure. This pairs awkwardly with FEAT-121's dry-run-to-enforcing path, which is default fail-closed once a CIDR is set.
- Fix: flip the default to fail-closed and offer fail-open as the opt-in, or at least emit an alert on fail-open geoip lookups so a silent degrade is visible.

### M-8. STORY-252 reassignment targets Team.lead_user_id without a null fallback

- Location: STORY-252 lines 13180..13183 ("Pending Approval rows assigned to the user are reassigned to the team lead ... AlertRule.owner_user_id is reassigned to the team lead").
- Problem: Team.lead_user_id is nullable (line 20995). If the deprovisioned user's team has no lead, the cascade has no defined target. The cascade is also running for users not assigned to a team (User.team_id nullable at line 20770). Behavior is unspecified for either case.
- Fix: declare a fallback chain — team lead, else Org.owner, else platform admin (in self_hosted) / trust_and_safety (in saas) — and add an AC that records the resolved target.

## Minor

### m-1. Copy-paste NFR "SCIM and provisioning operations are idempotent and safe to replay" applied to stories unrelated to SCIM

Examples: STORY-277 (audit log viewer, line 14418), STORY-293 (DR test restore, line 14900), STORY-307 (DLP export to S3, line 15240), STORY-311 (tenant-isolation tests, line 15336), STORY-302 (management API versioning, line 15119). The NFR is semantically irrelevant in each case and will look suspicious in a diff to implementors. Prune to stories that actually involve SCIM or provisioning.

### m-2. FEAT-131 has no data model for country allowlist/blocklist

STORY-306 references "the blocklist contains 'XX'" and "an allowlist" but the `data_models` slot lists only Request (line 15215..15216). There is no GeoPolicy model in the models section. Either add one or declare that the country lists are carried on an existing model (ApiAccessConfig / OrgIpAllowlist).

### m-3. FEAT-132 has no data model for the customer-S3 DLP export target

STORY-307 only cites Request (line 15237). The "S3 credentials are configured" precondition has no storage; no DlpExportConfig model exists. Either add one, or declare a reuse of AuditSink (which already supports type=s3). If reused, the feature should say so.

### m-4. ResidencyConfig.dpo_contact duplicates the notifications_model's Org.privacy_officer

Line 22435 has `dpo_contact: string` on ResidencyConfig while the baseline audience roster (line 37) names `Org.privacy_officer`. The two are the same person in most deployments. Consolidate onto a single field (Org.privacy_officer as declared in baseline) and update STORY-281..291 references.

### m-5. SsoConfig.signed_users is an undocumented int

Line 22330. No story reads or writes it, its semantics are undocumented, and it has no nullable flag. If it is a dashboard counter, document it; otherwise drop it.

### m-6. FEAT-129 `/api/v1/` versioned paths are not used anywhere else in EPIC-010

STORY-302 AC-001 (line 15114) calls `/api/v1/...` and `/api/v2/...`. Every other EPIC-010 story uses unversioned paths (`/api/org`, `/api/auth/sso`, `/api/residency`, `/api/webhooks`, `/api/audit/sinks`, ...). Either migrate those paths to `/api/v1/...` or clarify that FEAT-129 only governs explicitly versioned surfaces.

### m-7. Invite and Session cascades around SSO-enforced domains are not defined

FEAT-108 (SSO) enforces domains at sign-in. FEAT-004 STORY-007 does not check domain-enforcement at invite time, so an admin can invite `@acme.example` when SSO is enforced for that domain; STORY-008 then says "I set a password (or complete SSO)". If the admin toggles SSO enforcement on between invite creation and acceptance (a race this epic enables), the user accepts with a password in violation of policy. No AC handles this.

### m-8. AuditSink.credentials is `json nullable` with no encryption or at-rest policy

Line 22501..22503. The baseline security clause (line 33) says "Secrets live in the configured KMS (with FEAT-133 CMK where enabled) and never appear in logs, telemetry or persisted payloads". An unflagged json blob called `credentials` invites storing bearer tokens in plaintext. Either rename to `credentials_ciphertext` and link to CMK data-class `all`, or add a non-functional line requiring KMS-wrapped storage.

### m-9. Webhook signature replay-window NFR is declared in FEAT-114 only on STORY-259

Line 13527 non_functional: "5-minute signature replay window". STORY-260 and STORY-261 omit it. The rotation replay window in STORY-259 AC-002 (line 13487) says "previous continues to validate for a 5-minute window" but this is the secret-rotation grace, not the signature replay window. These are two different windows and both are 5 minutes by coincidence; the story should disambiguate to avoid implementors collapsing them.

## Cross-epic

### X-1. FEAT-107 billing vs EPIC-008 FEAT-095/096/098

FEAT-095/096/098 are explicit saas-only and route self_hosted tenants to the license (FEAT-175). FEAT-107 re-exposes plan/commitment/invoices on `Settings -> Plans` without declaring the same mode split. A self_hosted tenant can reach STORY-248 today. Either delete the billing half of FEAT-107 and point at EPIC-008, or add the same 404-in-self_hosted clause.

### X-2. FEAT-127 DR vs EPIC-013 FEAT-170 cluster/fleet health

FEAT-170 (Cluster and fleet health) owns drain/cordon and fleet-wide deploy state in both modes, visible to Antirion staff (saas) or platform admin (self_hosted). FEAT-127 covers backup/restore. The two collide on "trigger production restore": FEAT-170 would normally be the operator surface for any fleet-level action, but FEAT-127 places restore execution on workspace admin in self_hosted. Pick one owner or define the hand-off explicitly (FEAT-170 surfaces the backup roster, FEAT-127 executes against a single Org).

### X-3. FEAT-119 delete-org in self_hosted collides with FEAT-177 install lifecycle

In self_hosted the install is one-tenant-per-install by design; STORY-274 "Delete organization" thereby deletes the sole tenant, which is equivalent to decommissioning the install — but FEAT-177 (install wizard) and FEAT-170 own install-level lifecycle. FEAT-119 does not declare mode availability, does not defer to FEAT-177, and does not say what happens to the install when the sole Org is scheduled_for_deletion. Either block delete-org in self_hosted, or define the install-level consequence.

### X-4. FEAT-109 SCIM cascade vs EPIC-001 FEAT-003 (sessions) and FEAT-004 (invites)

See C-5. The cascade is the integration point between EPIC-010 provisioning and EPIC-001 authentication, and it fails to touch either the Session table that FEAT-003 owns or the Invite table that FEAT-004 owns. SCIM is also silent on TrustedBrowser (FEAT-015 / model 20896). Any fix to C-5 has to be ratified in EPIC-001 as well.

### X-5. FEAT-133 CMK data classes do not cover EPIC-003 BYOKCredential.ciphertext

CmkBinding.data_class is `prompts|responses|audit|cache|all` (line 23801). BYOKCredential.ciphertext (line 21185) stores provider credentials and is not in any of those classes except by the blanket `all`. The most sensitive secrets in the system — upstream provider keys — have no dedicated CMK class and no explicit binding story. Either add `provider_credentials` to the CmkBinding enum, or declare that all BYOK credentials inherit the `all` class and add an AC that proves this binding on rotation.

### X-6. FEAT-113 PII toggle vs EPIC-007 FEAT-070 PII detection

STORY-257 AC-002 (line 13405) lets a compliance officer enable "PII redaction" at the workspace level and promises "Inline redaction runs on every request". FEAT-070 (EPIC-007) owns the PII categories, strictness, and rule surfaces. STORY-257 does not say that enabling this switch is additive to FEAT-070 rules, or what happens if FEAT-070 is disabled but STORY-257 is enabled. Declare the precedence rule, or fold STORY-257's PII switch back into FEAT-070 and keep FEAT-113 on retention only.

### X-7. FEAT-115 audit sink cross-tenant fan-out in saas

STORY-263 AC-002 (line 13715) pages Antirion SRE on audit.sink.degraded. The baseline notifications_model (line 37..38) declares that cross-tenant fan-out to Antirion staff only happens for cross-tenant signals (isolation breaches, abuse heuristics, sustained anomalies). A tenant's broken audit pipe is not a cross-tenant signal — it is a tenant signal — so the "platform operator audience" clause here should re-resolve to platform admin, not Antirion SRE, in self_hosted. STORY-263 already says this, so it is consistent; but the same clause is missing from STORY-280 "Degraded sink" (line 14549), which raises "an Alert with category audit_sink_degraded" without a mode-split audience. Align STORY-280 with STORY-263.

## Missing / dangling references

### Cited ids that resolve to the wrong entity

- FEAT-112 (line 1473) cites `FEAT-163/STORY-409` for first-run residency pinning. FEAT-163 is "Public status page" (line 1942); STORY-409 is the cross-tenant roster story under FEAT-172 (line 19194). Neither touches residency. Correct citation is FEAT-162/STORY-387 (saas) and FEAT-177/STORY-423 (self_hosted). See C-1.
- FEAT-111 (line 1463) cites `FEAT-107` as the canonical home of the org IP allowlist. FEAT-107's description (line 1422) never mentions an IP allowlist. The dedicated surface is FEAT-121 (line 1566). See M-3.

### Fields named in narratives or baseline that do not exist in models

- `Org.owner` — referenced throughout the notifications_model (lines 37..38) and in STORY-263, STORY-285, STORY-289, STORY-300, STORY-305. Not present on Org (lines 20713..20756). Workspace owner is only reachable by `User.role = "owner"` query.
- `Org.privacy_officer`, `Org.finance_contact`, `Org.primary_contact` — referenced by notifications_model and by STORY-285/286/287/289/290/125 description/126 description. Not present on Org.
- `Org.tech_contact` — present on Org (line 20734) but not named in the baseline notifications_model roster. Either it is dead, or the roster is incomplete.
- `AlertRule.owner_user_id` — referenced by STORY-252 (line 13183). Not present on AlertRule (lines 22157..22212).
- `Webhook.owner_user_id` — referenced by STORY-300 (line 15057). Not present on Webhook (lines 22457..22485).
- `Model.paused` — referenced by STORY-276 (line 14325). Not present on Model (lines 21229..21297) and absent from the status enum.
- `ResidencyConfig.pinned_at`, `ResidencyConfig.pinned_by_user_id`, `ResidencyConfig.source` — required by STORY-256 AC-001 (line 13359). Not present on ResidencyConfig (lines 22413..22440).
- `AuditLog.prev_hash`, `AuditLog.hash`, `AuditLog.signing_key_id` — required by STORY-266 AC-001 (line 13846) and by baseline security line 33. Not present on AuditLog (lines 22511..22542).

### Dependency features implied by narrative but never declared as `depends_on`

- FEAT-112 depends operationally on FEAT-162 and FEAT-177 but neither is declared in FEAT-112's depends or in its stories.
- FEAT-109 STORY-252 depends on FEAT-003 (session revocation) and FEAT-004 (invite revocation) but does not declare those dependencies; it only declares `depends_on: STORY-250` (line 13169).
- FEAT-115 STORY-266 depends on the AuditLog data model's hash-chain shape (non-existent), so the story is blocked by a model gap, not by any other story.
- FEAT-127 STORY-294 restore execution depends on FEAT-181 (Antirion inbound support queue) for the "request restore" flow in saas — not declared.
- FEAT-133 depends on EPIC-003 BYOKCredential coverage (see X-5). Not declared.

### Features the epic's scope narrative promises but that are not present

- EPIC-010's epic description (line 228) lists "webhooks" and "audit sinks" as scope items. Both are present (FEAT-114/128 and FEAT-115/123). But the baseline security clause demands tamper-evident hashing of audit writes (line 33) and EPIC-010 is the home for audit viewing (FEAT-120) and export (FEAT-115 STORY-266) — yet the backing model (AuditLog) lacks the fields. The "feature" that implements hash-chain write semantics is implicitly promised and has no home: neither FEAT-115 nor FEAT-120 owns the write-path change; both treat it as a given. Recommend declaring a FEAT for "audit log write path: hash chain and signing key" explicitly.
- "Residency first-run pin evidence" is promised on STORY-256 AC-001 but the pin-write path lives in FEAT-162/STORY-387 and FEAT-177/STORY-423 — the read surface FEAT-112 and the write surface FEAT-162/FEAT-177 are disconnected because FEAT-112 cites the wrong features. This is the C-1 cross-reference fallout.
- "Cross-tenant fan-out gate" (baseline notifications_model line 37..38) is promised as a platform-wide audience router for cross-tenant signals; there is no FEAT in EPIC-010 or EPIC-013 that declares where this routing logic lives or how it differs from FEAT-102 notification-channels routing. STORY-311 AC-001 (line 15331) assumes it exists.

### Stories the epic's scope narrative or feature descriptions require but which are absent

- Per-class retention policy edit UI beyond request_bodies / response_bodies / metadata (FEAT-113 STORY-258 asserts the canonical home for `audit_logs` and `safety_events` retention, but RetentionConfig model has no fields for those classes — only `request_body_days`, `response_body_days`, `metadata_days` at lines 22447..22452). The story-level promise has no persisted field.
- Session and TrustedBrowser revocation on SCIM deprovision — see C-5.
- FEAT-119 "Resume the org delete during the 30-day grace" — STORY-274 says "During grace, any owner can cancel" but there is no AC, API or audit entry for the cancel action. A cancel-delete story is missing.
- FEAT-127 "request restore" saas flow (per the FEAT-127 description) — no STORY covers the tenant-side request-restore-ticket flow; all five stories assume execute-restore is tenant-available.
- FEAT-109 conflict-resolution on SCIM collisions with pending Invite — unspecified.
