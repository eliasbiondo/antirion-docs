# EPIC-013 — Platform operator administration — requirements review

Read-only audit of `docs/requirements.yaml` scoped to EPIC-013 (line 304) and
its features FEAT-170 through FEAT-182 plus STORY-403 through STORY-441.
Cross-referenced against `project.deployment_modes` and
`project.notifications_model` (both load-bearing), `project.non_functional_baseline.tenant_isolation`,
the `models:` section, and EPIC-004, EPIC-007, EPIC-009, EPIC-010, EPIC-012.

Line numbers refer to `docs/requirements.yaml` at the commit being reviewed.

## Summary

EPIC-013 is the only surface-group in the document that must gate on both
deployment mode and role at the edge, and most features get the narrative
right. The bulk of the defects are shape-level: the data models that the
epic writes to (`Org`, `AuditLog`, `SupportTicket`, `License`, `PlatformIncident`,
`LicenseIncident`) are missing fields the stories assume, and a few
cross-story links are wrong (one broken STORY-id, one overloaded path,
one feature whose `mode:` tag contradicts its description). The load-bearing
notifications contract in `project.notifications_model` names org-contact
fields (`primary_contact`, `finance_contact`, `privacy_officer`, `Org.owner`)
that are not on the `Org` model — every EPIC-013 story that routes to those
contacts inherits that gap.

Severities used below:

- **Critical**: data-model/contract mismatches that block implementation, privileged-action audit coverage gaps, broken mode/role gating.
- **Major**: broken intra-epic references, drafting contradictions between `mode:` field and description, unstated pre-conditions.
- **Minor**: naming inconsistencies, missing but non-blocking fields, local drafting issues.
- **Cross-epic**: issues that show up in EPIC-013 but are really attributes of another epic's data or features.

## Critical

### C1. `AuditLog.org_id` is non-nullable, so no operator-plane (cross-tenant) audit record has a home

*Citing lines*: STORY-408 AC-002 line 19164 (`"operator.access_denied"`),
STORY-410 AC-002 line 19281 (`"operator.tenant_view"`), STORY-411 AC-001
line 19330 (`"tenant.suspended" ... on both the operator-plane and
tenant-plane audit stores`), STORY-412 AC-001 line 19410, STORY-417 AC-001
line 19728 (`"release.auto_rollback"`), STORY-430/431/432 (phone-home audits),
STORY-433/435 (license incident audits).

*Model*: `AuditLog` at line 22511; `org_id: FK:Org` at line 22517 with no
`nullable: true`.

*Problem*: The baseline's tenant-isolation contract says every query is
partitioned by `org_id`. Every EPIC-013 audit event is, by construction,
either operator-plane (saas Antirion staff action against any tenant or
none) or platform-admin action against the install. In saas mode an
Antirion-staff principal has no tenant `Org` to attach to, and in
self_hosted mode a cross-install operator action has no natural `Org`
either. The current shape forces operator audit into a tenant row, which
either (a) silently breaks FK integrity or (b) routes operator actions
into a chosen tenant's audit stream — which violates tenant isolation
from the other direction. STORY-411 explicitly asks for writes to
"both the operator-plane and tenant-plane audit stores" but no operator-plane
store is modelled.

*Fix*: Either make `AuditLog.org_id` nullable and add `actor_plane: enum[tenant, operator]`
so operator-plane rows are first-class, or introduce a separate
`OperatorAuditLog` model with `install_id` and actor identity, and have
EPIC-013 stories write to it explicitly. Either way, update the stories
listed above to name the destination store instead of the generic
"AuditLog" and declare where the dual-write in STORY-411 AC-001 actually
lands.

### C2. `Org` is missing `state` / suspension field — STORY-411 depends on it

*Citing lines*: STORY-411 AC-001 lines 19328, 19330 (`Org X flips to state
"suspended"`); line 19338 (`Org X flips to state "active"`); component
states `active`, `suspended` at lines 19356–19357.

*Model*: `Org` at line 20713 has no `state` field. Closest neighbour is
`scheduled_for_deletion` (a timestamp — different concept).

*Problem*: Suspension is the headline commercial lever in EPIC-013 but
the target model cannot hold the state. Gateway key evaluation at the
edge (line 19328: "its gateway keys return 403 with a suspension body")
has no field to read. This is a hard blocker for FEAT-172/STORY-411.

*Fix*: Add `Org.state: enum[active, suspended, pending_deletion]` with
`suspension_reason`, `suspended_at`, `suspended_by_user_id`. Alternatively,
model suspension as its own table (`TenantSuspension`) linked by
`org_id` with first-class open/closed lifecycle.

### C3. `Org` is missing `primary_contact`, `finance_contact`, `privacy_officer`, and `owner` fields that the notifications_model and EPIC-013 require

*Citing lines*: `project.notifications_model` line 37–38 names
`security_contact, billing_contact, finance_contact, privacy_officer,
primary_contact`. EPIC-013 routes notifications to these fields at
STORY-412 AC-001 line 19409 (`Org.primary_contact`), STORY-417 AC-001
line 19726, STORY-422 AC-002 lines 20023–20024 (`Org.primary_contact`,
`Org.owner`), STORY-434 AC-001 line 19466 (`Org.primary_contact`),
STORY-436 AC-001 line 20525 (`primary_contact`), STORY-439 AC-001
line 20629 (`primary_contact, billing_contact, security_contact,
privacy_officer`).

*Model*: `Org` at line 20713 declares only `billing_contact`, `tech_contact`,
`security_contact`. No `primary_contact`, no `finance_contact`, no
`privacy_officer`, and no `owner` / `owner_user_id` field at all, despite
dozens of fallbacks across the document expressed as
"falling back to `Org.owner` in saas and platform admin in self_hosted".

*Problem*: Every EPIC-013 notification audience resolver in saas mode
reads a field that does not exist. Without it the notifications_model's
"tenant-scoped roles (a)(b)(c) behave identically in both modes" clause
cannot be implemented for EPIC-013's audiences.

*Fix*: Add `Org.owner_user_id: FK:User`, `Org.primary_contact: string`,
`Org.finance_contact: string`, `Org.privacy_officer: string` to the
`Org` model, and either reuse the existing `security_contact` and
`billing_contact` strings or upgrade all contact fields to
`FK:User | string` uniformly. This belongs in EPIC-010 / `models` but
EPIC-013 is the loudest caller.

### C4. No principal model distinguishes "Antirion staff" from a tenant `User` in saas mode

*Citing lines*: EPIC-013 description line 306 ("Antirion staff in the
saas managed offering"), STORY-407 AC-001 line 19100 (`my_roles
including "platform admin" only if I qualify`), STORY-412 AC-001
line 19410 ("acting operator (Antirion staff id in saas, platform
admin in self_hosted)"), FEAT-181 and FEAT-182 ("Antirion-staff
console only").

*Model*: `User` at line 20762 is tenant-scoped (belongs_to `Org`).
There is no `is_antirion_staff` field, no separate `Staff` / `OperatorPrincipal`
model, and no documented discriminator for how the bootstrap returns
`my_roles` for a saas operator.

*Problem*: Edge gating (STORY-408) cannot identify the saas operator
without this. STORY-407 conflates "holds platform admin" with "is
Antirion staff" — but per EPIC-013's description and
`project.deployment_modes`, the role `platform admin` is defined to
exist only in self_hosted. In saas a different principal must grant
visibility; nothing defines it.

*Fix*: Either promote "Antirion staff" to its own role string in a
designated Antirion-staff tenant Org in saas, or add an explicit
`OperatorPrincipal` model and state clearly in FEAT-171 how saas resolves
the operator identity. STORY-407 AC-001 should then stop returning
`"platform admin"` in saas and return the saas-specific role name.

### C5. STORY-422 AC-002 points to the wrong STORY id when delegating suspension

*Citing lines*: STORY-422 AC-002 line 20026 — "For suspend actions,
STORY-414 is invoked inline with the flag id as the reason."

*Problem*: STORY-414 is "Schedule a maintenance window with advance
notice" (feature FEAT-173). The actual suspend flow lives in STORY-411
"Suspend or resume a tenant with audit and notice" (feature FEAT-172).
The delegation as written wires abuse triage into the maintenance-window
form — meaningless.

*Fix*: Replace `STORY-414` with `STORY-411`.

### C6. STORY-407 and STORY-425 collide on `/api/bootstrap`

*Citing lines*: STORY-407 AC-001 line 19100 (`GET /api/bootstrap` returns
`deployment_mode` and `my_roles`); STORY-425 AC-001 line 20147
("POST the token plus a chosen email and password to `/api/bootstrap`").

*Problem*: Two different responsibilities are collapsed into one path —
shell bootstrap (read-only, authenticated) and install-time admin
bootstrap (one-shot, token-authed, writes a `User`). This is a
permissions and semantics collision, not a stylistic one.

*Fix*: Rename the install endpoint to `/api/operator/install/bootstrap`
(matching the rest of `/operator/*`) or reserve `/api/bootstrap` for
install only and move the shell endpoint to `/api/session/bootstrap`.
Update both stories and STORY-423's step 4 narrative accordingly.

### C7. Phone-home "security" channel promises a signal (tenant-isolation breaches) that cannot originate in self_hosted

*Citing lines*: FEAT-179 description line 2102 —
"security (trust_and_safety signals — key-leak events, tenant-isolation
breaches, break-glass usage)".

*Problem*: `project.notifications_model` at line 38 says
"Cross-tenant signals (isolation breaches, abuse heuristics, sustained
anomalies) always reach Antirion trust_and_safety in saas and are
silently dropped in self_hosted because the set of tenants is 1."
FEAT-179 then lists "tenant-isolation breaches" as a self_hosted
outbound channel payload. These two contracts disagree: either the
self_hosted install forwards isolation-breach events as
intra-install signals (and the baseline language should be
softened), or the security channel in self_hosted carries key-leak
and break-glass events only (and FEAT-179 should drop the
tenant-isolation line from its channel list, since isolation in a
1-tenant install is a synthetic concept per FEAT-134).

*Fix*: Remove `tenant-isolation breaches` from the "security" channel
description in FEAT-179, or extend `project.notifications_model` to
carve out an explicit self_hosted exception for this channel.

### C8. `License` has no `tier` field but FEAT-179 / FEAT-180 default on it

*Citing lines*: FEAT-179 description lines 2102–2103 ("self_hosted
defaults channels off for the ENTERPRISE license tier and on for the
CLOUD-ASSIST license tier"). FEAT-180 description line 2113
("soft-grace window (default 14 days, configurable per license tier at
issue time)").

*Model*: `License` at line 23501 has `features: string[]` but no `tier`
field.

*Problem*: Two named features branch behaviour on `License.tier` that
isn't in the model. The phone-home default resolution in STORY-430 and
the grace window in STORY-433/435 therefore have no input to read.

*Fix*: Add `License.tier: enum[enterprise, cloud_assist]` (and define
the canonical set) or store tier as a member of `features[]` with a
prefix (e.g., `tier:enterprise`) and document that convention in FEAT-175.

### C9. `SupportTicket` is missing fields FEAT-181 and STORY-436/438/441 depend on

*Citing lines*: STORY-436 AC-002 lines 20531–20534 ("I set severity
and assignee", "the ticket state becomes 'triaged', the SLA timer
starts per severity"); STORY-436 non_functional line 20552 ("Tickets
originating from self_hosted installs carry the install id on
SupportTicket"); STORY-438 AC-001 lines 20599–20605 ("severity-1
ticket", "reassigned to the on-call escalation group"); STORY-441
AC-001 line 20696 ("any open severity-1 support tickets").

*Model*: `SupportTicket` at line 23266 declares `status` in
`{open, in_progress, waiting, resolved, closed}` and `priority` in
`{low, normal, high, urgent}`. There is no `severity`, no `assignee_user_id`,
no `install_id`, no `sla_due_at`, no `triaged_at`, and no
state named `triaged` or `awaiting_customer` even though
STORY-436 `ui.states` uses `new/triaged/awaiting_customer/resolved`
and STORY-437 AC-001 transitions to `awaiting_customer`.

*Problem*: The whole FEAT-181 lifecycle is described on fields the model
does not carry. Either the stories or the model is wrong.

*Fix*: Add to `SupportTicket`: `severity: enum[sev1, sev2, sev3]`,
`assignee_user_id: FK:User (nullable)`, `install_id: string (nullable)`,
`triaged_at: timestamp (nullable)`, `sla_due_at: timestamp (nullable)`,
and extend `status` to include `new`, `triaged`, `awaiting_customer`.
Reconcile with FEAT-164 (which already creates `SupportTicket` from the
tenant side) so the new columns are optional there.

## Major

### M1. FEAT-172 description says "saas mode only" but `mode: both`

*Citing lines*: FEAT-172 description line 2032
("Available in saas mode only; in self_hosted the view degenerates to
a single-row read-only summary"); FEAT-172 `mode: both` at line 2033.

*Problem*: The two lines disagree about whether FEAT-172 is
mode-exclusive. The narrative that follows makes clear the feature *is*
available in both modes, just degenerate in self_hosted. The
leading sentence "Available in saas mode only" is wrong.

*Fix*: Change the first sentence to "Available in both modes; in
self_hosted the view degenerates to a single-row read-only summary of
the local install." (`mode: both` is correct.)

### M2. FEAT-181 and FEAT-182 `mode: saas` is too narrow to capture the feature's location

*Citing lines*: FEAT-181 line 2124 `mode: saas`; description at line
2123 says "in self_hosted mode the feature is installed only on
Antirion's own operator console and is never rendered on customer
installs". FEAT-182 is the same pattern at line 2134 / 2133.

*Problem*: The `mode:` field is supposed to be a machine-readable gate.
If a tool reads it to know whether to render a feature in self_hosted,
it will wrongly conclude the surface is absent even on Antirion's own
install. The correct encoding is that the feature is present on the
Antirion-operated console in both modes, and never on a customer install.

*Fix*: Either add a new dimension (`installed_on: antirion_console` vs
`installed_on: every_install`) and set `mode: both, installed_on: antirion_console`
on FEAT-181/FEAT-182, or make the mode tag an enum that includes
`antirion_staff_console_only`. Until then, at minimum extend the
description to say "mode: saas means 'runs on the saas-operated console',
not 'only exists when the local install is saas'." See also the
`/antirion/*` routes in STORY-436, STORY-439, STORY-441 which carry the
same distinction and are not declared in FEAT-171's gating contract.

### M3. STORY-403 narrative names a tenant role ("workspace owner") as the EPIC-013 persona

*Citing lines*: STORY-403 line 18778 — "as_a: SRE or workspace owner".

*Problem*: EPIC-013 description (line 306) and STORY-408 (line 19148)
both state operator surfaces are invisible to tenant roles. "workspace
owner" is a tenant role. Naming it here implies a workspace owner can
reach `/settings/fleet`, which the same epic's STORY-408 explicitly
forbids. Even as shorthand it contradicts the epic's gating promise.

*Fix*: Change the persona to the canonical one: "platform operator
(Antirion SRE in saas, platform admin in self_hosted)".

### M4. `/antirion/*` paths are not declared in FEAT-171's gating contract

*Citing lines*: STORY-436 line 20523 (`/antirion/support/queue`),
STORY-439 line 20625 (`/antirion/crm/orgs/:id`), STORY-441 line 20693
(`/antirion/crm/pipeline`).

*Problem*: FEAT-171 and STORY-407/STORY-408 only gate the `/operator/*`
and `/api/operator/*` namespaces. The Antirion-staff console uses
`/antirion/*`, which is a completely separate namespace with no
declared gating. In self_hosted mode those paths must not exist at all
on a customer install (FEAT-181 / FEAT-182 description). STORY-408
AC-001 would not catch a leaked `/antirion/crm` handler because the
AC only probes `/operator/*`.

*Fix*: In FEAT-171 (and STORY-407/408) add an explicit rule that both
`/operator/*` AND `/antirion/*` are gated identically, and that
`/antirion/*` additionally requires the Antirion-staff principal (not
merely platform admin) and is 404 on any install that is not the
Antirion-operated console.

### M5. `PlatformIncident` has no timeline table but STORY-412 AC-002 posts timeline updates

*Citing lines*: STORY-412 AC-002 line 19412–19420 (`POST
/api/operator/incidents/:id/timeline` with body `{state, body}`);
`PlatformIncident` model at line 23424 has no `timeline` /
`IncidentTimelineEntry` storage.

*Problem*: Timeline entries are mutable history; storing them
inside the PlatformIncident row conflicts with its ("append-only"-style)
`state` field. The state transitions are also part of the timeline but
currently overwrite each other on the single row.

*Fix*: Introduce `IncidentTimelineEntry` with `incident_id`, `state`,
`body`, `actor_user_id`, `at`, and reference it from PlatformIncident
via a has_many.

### M6. `LicenseIncident` has no `renewal_id` / `renewal_confirmation_id` field for the renewal-in-flight shield

*Citing lines*: STORY-435 AC-002 line 20501 — "An AuditLog
'license.incident.shielded' records the renewal id and the shield
expiry." FEAT-180 description line 2113 describes the shield.

*Model*: `LicenseIncident` at line 24109 has `shield_expires_at` but
no renewal reference.

*Problem*: The story says the audit records the renewal id, but the
incident itself does not carry it; any later reconciliation with
Antirion renewals has no join key.

*Fix*: Add `LicenseIncident.renewal_confirmation_id: string (nullable)`
and optionally `shielded_by_user_id`.

### M7. STORY-410 has no self_hosted branch, but the endpoint exists in both modes

*Citing lines*: STORY-410 AC-001 line 19268 — opens
`TenantDetailDrawer`; STORY-410 non_functional line 19310 — "Tenant-originated
audit visibility is mandatory — the tenant's owner can see which operator
viewed them and when".

*Problem*: In self_hosted the "tenant" is the install itself; the
"tenant's owner" collapses to platform admin, who is the same principal
doing the viewing. STORY-409 AC-002 handles the degenerate case of the
roster, but STORY-410 does not say how the drill-in degenerates — whether
the audit visibility rule still applies (self-audit), or whether the
tenant-plane audit write from FEAT-120 is skipped.

*Fix*: Add a self_hosted branch scenario to STORY-410 that states
either (a) the drill-in is a no-op because the operator already has
the native tenant admin view, or (b) the operator.tenant_view audit is
still written to evidence the mode-agnostic operator-read contract.

### M8. Residency pinning step in STORY-423 is not cross-linked from FEAT-112

*Citing lines*: FEAT-112 description line 1473 — "The region is set once at
first-run (FEAT-163/STORY-409)"; STORY-423 AC-002 step 5 line 20094 —
"Step 5 pins a residency label that is written into ResidencyConfig
and is immutable for the install".

*Problem*: FEAT-112 thinks first-run residency pinning is the job of
FEAT-163 (public status page) and STORY-409 (saas tenant roster).
Neither defines residency pinning. EPIC-013's actual pinning path is
FEAT-177 / STORY-423 step 5 (self_hosted) and by implication FEAT-107
signup (saas). The FEAT-112 pointer is broken in both the FEAT id and
the STORY id.

*Fix*: Update FEAT-112 to say "set once at first-run (FEAT-177/STORY-423
in self_hosted; FEAT-107 in saas)". This is an EPIC-010 edit; called
out here because the dangling pointer is the EPIC-013 reader's
first source of confusion.

### M9. STORY-423 AC-001 (503 pre-wizard) does not reconcile with STORY-408 (operator routes return 404)

*Citing lines*: STORY-423 AC-001 line 20081 — "The gateway responds
503 with a body pointing at /operator/install"; STORY-408 AC-001
line 19155 — "Every /operator/* route returns 404 rather than 403 so
existence is not disclosed".

*Problem*: A fresh install needs `/operator/install` reachable *before*
any principal can have "platform admin" (because STORY-425 creates the
first one). STORY-408's 404-for-tenant-principals rule must not apply
before the wizard completes, or it applies but the wizard's own routes
are carved out. This carve-out is not stated.

*Fix*: In FEAT-171/STORY-408 call out that `/operator/install/*` and
`/api/operator/install/*` are reachable to the unauthenticated
bootstrap principal pre-completion, and flip to the general
platform-admin-or-404 rule once `InstallState.status = complete`.

### M10. STORY-413 title says "routing and budgets" but AC reads from routing only

*Citing lines*: STORY-413 title line 19467 — "Compute affected tenants
from routing and budgets"; AC-001 line 19483 — "derived from the last
24h of routing traffic that touches that component in that region".

*Problem*: The AC has no "budgets" input; the title says there is.
Either the title is aspirational or the AC is incomplete.

*Fix*: Drop "and budgets" from the title, or add an acceptance
criterion that folds budget-override-active tenants into the
affected set.

### M11. `PlatformIncident.created_by_user_id` is FK:User but in saas the actor is Antirion staff

*Citing lines*: `PlatformIncident` at line 23451
`created_by_user_id: FK:User`.

*Problem*: Related to C4. In saas the incident is declared by an Antirion
staff principal whose `User` row is, per the current model, tenant-scoped.
Either the foreign key will point at a User in an Antirion-internal
Org (never documented), or the field will be null in saas and the audit
trail is broken.

*Fix*: Tied to C4 — once the operator-principal concept is modelled,
change `created_by_user_id` to a generic `actor_ref` or add
`created_by_staff_id: FK:OperatorPrincipal (nullable)`.

## Minor

### m1. STORY-409 AC-001 says "I hold platform admin" in saas mode

*Citing lines*: STORY-409 AC-001 lines 19207–19209
(`given: - The deployment mode is saas; - I hold platform admin`).

*Problem*: Per EPIC-013 line 306, the saas operator is Antirion staff;
"platform admin" is the self_hosted role. The narrative elsewhere
distinguishes them. This AC uses the self_hosted role string in a
saas scenario.

*Fix*: In saas `given`, replace "I hold platform admin" with "I am
signed in as Antirion staff" (or the equivalent saas role name resolved
in C4).

### m2. `License.state = "revoked"` has no story

*Citing lines*: `License.state` enum at line 23521 includes `revoked`,
but no EPIC-013 story describes how a license gets revoked or what the
operator sees.

*Problem*: `revoked` will be dead code in every surface that reads
`License.state`.

*Fix*: Either drop `revoked` from the enum or add a story — likely on
FEAT-175 — that explains Antirion-originated revocation (phone-home
"license" channel command) and its audit contract.

### m3. STORY-420 AC-002 expiry fail-closed does not define what counts as "new tenant writes"

*Citing lines*: STORY-420 AC-002 line 19920 — "New tenant writes are
rejected with 402 'license_expired'. Read-only and operator-license
surfaces remain available."

*Problem*: The distinction between "write" and "read-only" is not defined
for gateway traffic; a `POST /v1/chat/completions` is idempotent-but-side-effecting
(metered). This interacts with FEAT-141 cost metering. Without a
definition, STORY-434 AC-001 (hard-close returns 402 for new tenant
requests) and STORY-420 AC-002 (write-vs-read) could disagree.

*Fix*: Explicitly state that gateway traffic counts as a tenant-write
for license-enforcement purposes; "read-only" refers only to the
operator plane.

### m4. STORY-410 says "FEAT-120" for the tenant-plane audit emission

*Citing lines*: STORY-410 AC-002 line 19282 — "The tenant's own audit
log records a matching 'operator_accessed' entry per FEAT-120."

*Problem*: FEAT-120 is "Audit log viewer" (read path), not the
emission contract. The emission contract lives in FEAT-115 (audit
sinks) and in the general `AuditLog` model.

*Fix*: Change the reference to "the AuditLog (FEAT-115 ingestion,
FEAT-120 viewer)" or just "the tenant's AuditLog".

### m5. STORY-405 "QueueHealthTable" reads `WorkerQueue` but the story asks for fields not on the model

*Citing lines*: STORY-405 AC-001 line 18936 — "I see a row per
WorkerQueue with name, depth, oldest_job_age_sec, consumer count,
DLQ depth, retry count, p95_ms and status".

*Model*: `WorkerQueue` at line 23336 has `name`, `description`, `depth`,
`oldest_job_age_sec`, `success_rate_1h`, `p95_ms`, `status`,
`last_updated_at`. No `consumer_count`, `dlq_depth`, `retry_count`.

*Fix*: Add `consumer_count`, `dlq_depth`, `retry_count` to `WorkerQueue`
or treat them as computed/derived and call that out in the
`non_functional` section.

### m6. `FleetReplica` has no `version_applied_at` but STORY-406 sorts by `applied_at`

*Citing lines*: STORY-406 AC-002 line 19034 — "I can sort by applied_at
or filter to only 'pending' or 'failed'".

*Model*: `ConfigPropagation.node_states` is a free-form json blob
described as `{state, applied_at, error}`. That is serviceable for
this sort but makes the sort server-side implementation implicit and
brittle.

*Fix*: Either normalize `ConfigPropagation.node_states` into a
`ConfigPropagationNode` table (replica_id, state, applied_at, error)
or document the json shape in the model description.

### m7. STORY-430 UI state `forced_on_saas` is not referenced by any API or model field

*Citing lines*: STORY-430 `ui.states` line 20334 — `forced_on_saas`.
`PhoneHomeChannel` at line 24067 has `enabled` and `air_gapped` booleans
but no "forced" marker.

*Fix*: Either add `PhoneHomeChannel.locked_by_mode: bool` or derive
`forced_on_saas` from `deployment_mode == saas`.

### m8. STORY-406 "operational alert per EPIC-009" does not name a feature

*Citing lines*: STORY-406 non_functional line 19081 — "A propagation
that breaches the 30-second SLA raises its own operational alert per
EPIC-009".

*Fix*: Pin the reference to FEAT-099 (alert rules) or FEAT-106 (SLO)
so the alert rule's home is explicit.

### m9. STORY-425 AC-001 "User is created with role platform admin" does not cite FEAT-012's reserved-role rule

*Citing lines*: STORY-425 AC-001 line 20149 — "A User is created with
role platform admin"; FEAT-012 description line 447 — "platform admin
role is a reserved built-in that exists only in self_hosted mode".

*Fix*: Add a scenario or non_functional line that FEAT-012's
reserved-role API path is bypassed here and records an audit marker,
or that STORY-425 is the single exception to FEAT-012's "cannot be
granted through normal role management" rule. The current text leaves
FEAT-012 and STORY-425 in apparent conflict.

## Cross-epic

### X1. `Org` contact-field gap is an EPIC-010 deficiency that propagates into EPIC-013

See C3. The fix belongs in EPIC-010 (and `models.Org`). Every
EPIC-013 story that routes to `primary_contact`, `finance_contact`,
`privacy_officer`, or `Org.owner` depends on it.

### X2. Operator-plane audit logging needs a non-tenant `AuditLog` shape

See C1. Touches EPIC-010 (FEAT-115 Audit log sinks, FEAT-120 viewer,
FEAT-134 tenant-isolation) and EPIC-013 (every story that writes an
"operator.*" AuditLog).

### X3. FEAT-112 (EPIC-010) points at the wrong first-run feature/story for residency pinning

See M8. Edit lives on FEAT-112 but the dangling pointer is EPIC-013's
first encounter with the misnamed reference.

### X4. FEAT-164 (EPIC-012) → FEAT-181 (EPIC-013) handoff references `install_id` and redaction profile on `SupportTicket` but the model does not carry them

See C9 and STORY-436 non_functional line 20552
("Tickets originating from self_hosted installs carry the install id
on SupportTicket and the redaction profile applied by FEAT-179").
Edit lives across EPIC-012 (FEAT-164), EPIC-013 (FEAT-181), and
`models.SupportTicket`.

### X5. `project.non_functional_baseline.deployment_modes` says every feature that differs by mode declares its mode availability explicitly, but FEAT-181 / FEAT-182 use a mode tag that cannot express "Antirion console only across both modes"

See M2. The baseline contract itself needs a second dimension. This is
a `project.non_functional_baseline` upgrade, not purely an EPIC-013 fix.

### X6. Phone-home "security" channel payload list includes cross-tenant events that the notifications_model silently drops in self_hosted

See C7. Edit lives between `project.notifications_model` and
FEAT-179's channel description.

### X7. EPIC-007 cross-tenant abuse heuristic source is implicit

*Citing lines*: STORY-422 AC-001 line 20013 — "A queue of abuse flags
is shown with tenant, rule, first-seen, last-seen and severity".
EPIC-007 features FEAT-069..FEAT-081 do not declare a cross-tenant
abuse-heuristic producer that writes these flags.

*Problem*: STORY-422 is a consumer with no declared producer. The
concept is hinted in `project.notifications_model` ("abuse heuristics
... reach Antirion trust_and_safety in saas") but no feature in
EPIC-007 owns the producer, and EPIC-013 does not redeclare it as part
of FEAT-176's scope.

*Fix*: Either extend FEAT-176 description to say it owns the producer,
or add a dedicated feature in EPIC-007 for cross-tenant abuse
heuristics with an `AbuseFlag` model and a producer loop, and wire
STORY-422's `GET /api/operator/abuse/flags` into it.

### X8. EPIC-009 operator alert routing is assumed by STORY-417 but never defined as a channel type

*Citing lines*: STORY-417 AC-001 line 19725 — "The platform operator
audience — Antirion SRE in saas, platform admin in self_hosted — is
paged at severity 'crit' with the offending metric sample".
`project.notifications_model` ends (d) and (e) with "Delivery channels
per role are resolved by FEAT-102 notification-channels routing for
user-addressable roles and by the platform operator's configured
paging integration for (d) and (e)".

*Problem*: No feature in EPIC-009 (FEAT-099..FEAT-106) or elsewhere
defines "the platform operator's configured paging integration".
FEAT-102 is the generic channels feature; it does not distinguish the
operator page from tenant notifications.

*Fix*: Add a feature or extend FEAT-102 to describe the operator-paging
channel (PagerDuty or equivalent), its configuration surface in
EPIC-013 (likely a small addition to FEAT-170 or a new FEAT) and how
it resolves the Antirion-staff sub-queue identifiers
(`trust_and_safety`, `support`, `sre`, `dpo`, `renewals`, `legal`).

## Missing / dangling references

- **STORY-414** cited by **STORY-422 AC-002** at line 20026 — the
  reference is to the *wrong* existing story (STORY-414 is maintenance
  scheduling). Intended target is STORY-411. See C5. Listing this
  here because any tooling that resolves the link will silently return
  the wrong scope.

- **FEAT-163 / STORY-409** cited by **FEAT-112 description** at line
  1473 as the residency-pinning anchor — both ids exist but neither
  owns residency pinning (FEAT-163 is the public status page;
  STORY-409 is the saas tenant roster). See M8 / X3.

- **FEAT-120** cited by **STORY-410 AC-002** at line 19282 as the
  emission anchor for "operator_accessed" tenant-plane audit entries.
  FEAT-120 exists but is the *viewer*, not the ingestion contract.
  See m4.

- **"operator paging integration"** cited by
  `project.notifications_model` line 38 and assumed by STORY-417
  AC-001. No feature owns this in EPIC-009 or EPIC-013. See X8.

- **"Antirion staff" principal** assumed by EPIC-013 description line
  306, STORY-407 AC-001 line 19100 and FEAT-181 / FEAT-182
  descriptions. No model, role, or feature defines how the principal
  is identified in saas. See C4.

- **"break-glass" operator access** cited by FEAT-179 description line
  2102 as a security-channel payload type. No feature in EPIC-013
  defines a break-glass flow for Antirion staff reading a tenant
  workspace or for platform admin reading a specific Org. FEAT-176 is
  the closest but its stories do not cover break-glass. Either name
  the missing feature or drop the reference.

- **Cross-tenant abuse-heuristic producer** assumed by FEAT-176 /
  STORY-422 and by `project.notifications_model`. No feature in
  EPIC-007 owns a producer. See X7.

- **`install_id` on `SupportTicket`** assumed by STORY-436
  non_functional line 20552. Field is absent from `models.SupportTicket`.
  See C9.

- **`License.tier`** assumed by FEAT-179 description line 2103 and
  FEAT-180 description line 2113. Field is absent from `models.License`.
  See C8.

- **`Org.state`** assumed by STORY-411 AC-001/AC-002 and by the
  component states at lines 19356–19357. Field is absent from
  `models.Org`. See C2.

- **`Org.primary_contact`, `Org.finance_contact`, `Org.privacy_officer`,
  `Org.owner`** assumed by `project.notifications_model` and by
  numerous EPIC-013 stories. Fields are absent from `models.Org`. See
  C3.

- **`PlatformIncident` timeline storage** assumed by STORY-412 AC-002.
  No timeline table is modelled. See M5.

- **`LicenseIncident.renewal_confirmation_id` / renewal id** assumed by
  STORY-435 AC-002. No field is modelled. See M6.

- **`SupportTicket.severity`, `.assignee_user_id`, `.sla_due_at`,
  `.triaged_at`** assumed by STORY-436 / STORY-438 / STORY-441. Fields
  absent. See C9.

- **`PhoneHomeChannel.locked_by_mode`** implied by STORY-430 UI state
  `forced_on_saas`. Field absent. See m7.

- **`WorkerQueue.consumer_count`, `.dlq_depth`, `.retry_count`**
  rendered by STORY-405 AC-001. Fields absent from `models.WorkerQueue`.
  See m5.

- **`ConfigPropagationNode` normalisation** implied by STORY-406
  AC-002's per-replica sort/filter. Currently represented as a free
  `json` blob. See m6.
