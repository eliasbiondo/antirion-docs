# EPIC-008 "Budgets and cost control" — requirements.yaml review

Scope audited: `docs/requirements.yaml` EPIC-008 (line 191) with features
FEAT-082..FEAT-098 (lines 1161–1328) and stories STORY-184..STORY-222
(lines 10373–11748). Cross-referenced against the project baseline
(lines 1–73), the models section (lines 20712+) and the cross-cutting
epics called out in the brief (EPIC-006, EPIC-009, EPIC-010, EPIC-011).

This is a **read-only** audit; no edits were made to `requirements.yaml`.

---

## Summary

EPIC-008 is the largest non-gateway epic (17 features, 39 stories) and
it is the single load-bearing point of truth for budget counters, policy,
waivers, approvals, forecasts, rollover, multi-currency, projects,
billing, plan lifecycle and finance export. The surface area is wide and
the conceptual split between **budget** (EPIC-008), **billing** (also
EPIC-008 via FEAT-095/096/098), **gateway cost attribution** (EPIC-011
FEAT-141) and **alert rules** (EPIC-009) is only partially clean.

The highest-impact defects concentrate in three areas:

1. **Data-model shape gaps**: the `BudgetEvent` model has no `amount`
   field (so waivers cannot store their own magnitude) and no linkage to
   `Approval`, yet acceptance criteria assume both; `Project` has no
   numeric `budget` field yet STORY-188 assumes one; `UserBudget` has no
   FK to `Budget`; `Org` is missing three of the five contact fields
   (`finance_contact`, `primary_contact`, `privacy_officer`) that the
   project-level `notifications_model` treats as canonical and that
   EPIC-008 stories reference directly.
2. **Identifier breakage**: STORY-187's narrative cites `STORY-088` and
   `STORY-091` as the "direct-waiver" and "Approval-based waiver" stories,
   but those IDs resolve to unrelated observability stories (CSV export
   and request-diff). The baseline `shared_limiters` clause on line 20
   points at `FEAT-139` for "Edge rate limits" but `FEAT-139` in the
   features list is "Retry, timeout and runtime failover" — the real
   edge rate-limits feature is `FEAT-138`. EPIC-008's non-functional
   inheritance (shared-store counters) thus grounds itself on a dangling
   feature id.
3. **Enforcement-semantic drift with EPIC-011 and FEAT-180**: STORY-189
   returns `429 "budget exhausted"` on hard-cap block, while the parallel
   "cap exceeded → fail closed" flow for license violation in FEAT-180
   returns `402 Payment Required`. Two conceptually identical states
   (cap reached, new request rejected) use different status codes,
   which will split client-side retry logic.

Beyond those, there is recurring drift in how self_hosted mode handles
budget notifications (STORY-200 misinterprets `notifications_model`:
budget overages are provider-passthrough cost, not Antirion billing, so
tenant-scoped contacts behave identically per the baseline and the
"Antirion billing has no meaning" clause is wrong), and the cost
attribution contract for cached requests is never spelled out — budgets
and billing both read from `Request.cost`, which already includes
`cache_cost`, but no EPIC-008 story explicitly covers how cache hits
consume budget or reconcile with `EPIC-006` savings analytics.

The sections below enumerate findings by severity, each with a line
number, quoted text, problem, and fix.

---

## Critical

### C1. `BudgetEvent` has no `amount` field — waivers cannot store magnitude

- **Line 22131–22156** (model `BudgetEvent`, fields `type`, `severity`,
  `scope`, `scope_id`, `title`, `body`, `actor_user_id`) and
  **line 10781–10790** (STORY-193 AC-001).
- Quoted (STORY-193 AC-001):

  > When → I grant a waiver of 5000 with reason "incident response"
  > Then → The effective cap for this cycle is raised by 5000
  > A BudgetEvent of type "waiver" is recorded

- **Problem**: `BudgetEvent` has no amount, reason, or target-budget FK.
  The story states the waiver amount must be carried forward so that the
  effective cap rises by `5000`, but the only persistent record is a
  `BudgetEvent` with `title` and `body` strings. There is nowhere to
  durably read "this cycle's total waiver magnitude" in SQL; replay and
  cycle rollover (STORY-199) cannot account for it.
- **Fix**: either (a) add `amount: number`, `reason: string`,
  `budget_id: FK:Budget`, and `approval_id: FK:Approval` fields to
  `BudgetEvent`; or (b) introduce a separate `Waiver` model and store
  the lifecycle event on `BudgetEvent` with `waiver_id`. The EPIC-008
  title and description both promise "Waivers" as a first-class concept,
  so option (b) better matches the stated scope.

### C2. `BudgetEvent` has no `approval_id` — the waiver↔approval link is unrepresentable

- **Line 10905–10907** (STORY-196 AC-001):

  > The Approval status becomes "approved"
  > A BudgetEvent of type "waiver" is created linked to this Approval

- **Line 22618–22661** (model `Approval`): no `target` back-reference
  to `BudgetEvent`, and `target_type`/`target_id` are generic strings.
- **Problem**: "linked to this Approval" cannot be expressed in the
  current schema. `Approval` has `target_type`/`target_id` as opaque
  strings, and `BudgetEvent` has no `approval_id`. Either the query
  "given a BudgetEvent, find the Approval that produced it" or the
  inverse is a scan-and-match, not a join.
- **Fix**: add `approval_id: FK:Approval nullable: true` to
  `BudgetEvent` (see C1). Separately, require `Approval.target_type` to
  enumerate permitted values (budget, budget_policy, waiver, …) rather
  than a free string.

### C3. `Project` has no numeric `budget` field but STORY-188 asserts one

- **Line 22088–22106** (model `Project`, fields `id`, `team_id`, `name`,
  `owner_user_id`, `budget_id`, `created_at`).
- **Line 10587–10589** (STORY-188 AC-001):

  > I assign shares 50/30/20 and save
  > Then → Each Project.budget is 60000 / 36000 / 24000
  > The sum matches the team budget

- **Problem**: `Project` carries only an FK `budget_id` — there is no
  `Project.budget` scalar. The story is either (a) shorthand for "each
  Project's linked Budget has amount …" (which implies one Budget row
  per project created transactionally — never described) or (b) a
  design that stores a denormalised amount on `Project` (absent from
  the model).
- **Fix**: pick one. Either add a `Project.budget_amount: number`
  denormalised column with a rule that keeps it in sync with the linked
  Budget, or rewrite STORY-188 AC-001 to make explicit that allocation
  creates/updates a `Budget` with `scope="project"` per project. The
  second matches the rest of the epic better.

### C4. `UserBudget` has no FK to `Budget` — rollup is unimplementable

- **Line 22109–22130** (model `UserBudget`, fields `user_id`,
  `project_id`, `team_id`, `budget`, `spent`, `allocation_pct`,
  `outlier`).
- **Problem**: `UserBudget` stores a per-user allocation keyed by
  `user_id`/`project_id`/`team_id`, but carries **no FK to the parent
  `Budget` row**. STORY-188 "Allocate project and user budgets" mutates
  a team's allocations and STORY-185 returns `users: [UserBudget]`
  under a team's Budget; neither has a durable reference from the
  allocation row back to its parent envelope. This blocks cycle
  rollover (STORY-199) from correctly resetting per-user `spent`,
  because "which cycle does this UserBudget row belong to?" has no
  answer.
- **Fix**: add `budget_id: FK:Budget` to `UserBudget` and make it the
  canonical parent key; derive `team_id`/`project_id` from the Budget's
  scope rather than duplicating them.

### C5. Baseline `shared_limiters` cites the wrong FEAT id for edge rate limits

- **Line 20** (baseline `non_functional_baseline.shared_limiters`):

  > Edge rate limits (FEAT-139), budget counters (EPIC-008) and provider
  > outbound limiters (FEAT-161) use a shared-store sliding-window
  > implementation …

- **Line 1717–1720**: `FEAT-138 Edge authentication, authorization and
  rate limits`.
- **Line 1727–1730**: `FEAT-139 Retry, timeout and runtime failover`.
- **Problem**: The baseline statement that EPIC-008 inherits its
  counter semantics from — "shared-store sliding window so horizontal
  scaling does not multiply a tenant's effective limit" — cross-refs a
  feature that is about retry and failover, not rate limiting. The
  correct "edge rate limits" feature is FEAT-138. This is not
  cosmetic: STORY-189, STORY-193 and the per-story non_functional
  boilerplate ("budget evaluation is shared-state and survives node
  loss") all derive from this baseline line, and the baseline points
  at the wrong peer.
- **Fix**: change "FEAT-139" to "FEAT-138" in the baseline, or
  swap the IDs of FEAT-138 and FEAT-139 so the title reorder matches
  the baseline citation. The baseline change is smaller and safer.

### C6. STORY-187 cites `STORY-088` and `STORY-091` for waiver paths — those IDs are unrelated

- **Line 10533–10541** (STORY-187 title and narrative):

  > Reconcile direct-waiver and Approval-based budget paths
  > … so_that: small waivers are fast and big waivers are governed
  > i_want: the behavior of direct-waiver (STORY-088) and Approval-based
  > waivers (STORY-091) to be clearly separated by threshold

- **Line 6286–6290**: `STORY-088` is "Export filtered requests to CSV"
  under FEAT-036 (observability).
- **Line 6436–6440**: `STORY-091` is "Compare two requests side-by-side"
  under FEAT-038 (observability).
- **Problem**: Both cited IDs resolve to observability stories with
  nothing to do with budgets. The author likely intended STORY-193
  ("Grant a one-time budget waiver") and STORY-196 ("Approve or reject
  a pending request"). Any downstream tooling that resolves
  dependency graphs from this file will fail or silently mis-wire.
- **Fix**: replace `(STORY-088)` with `(STORY-193)` and `(STORY-091)`
  with `(STORY-196)` in STORY-187's narrative.

### C7. `Org` model is missing three contact fields the baseline declares canonical

- **Line 20732–20737** (Org model): only `billing_contact`,
  `tech_contact`, `security_contact` are defined.
- **Line 37** (baseline `notifications_model`):

  > (c) the org-scoped contact fields on Org (security_contact,
  > billing_contact, finance_contact, privacy_officer, primary_contact)

- EPIC-008 consumers: STORY-192 AC-002 alerts "finance contact"
  (line 10764); STORY-200 AC-001 falls back to `Org.finance_contact`
  (line 11145); STORY-202 AC-003 alerts "finance contact" (line 11252).
  EPIC-010/013 consumers also exist (line 14691 privacy_officer, 19409
  primary_contact, 20466 primary_contact, etc.).
- **Problem**: `finance_contact`, `primary_contact`, `privacy_officer`
  are referenced by name from multiple stories and from the baseline
  audience policy, but the `Org` model declares none of them. Every
  self_hosted fallback ("if not set, fall back to platform admin") is
  structurally unreachable because the field that would be unset does
  not exist.
- **Fix**: extend `Org` with `finance_contact: string`,
  `primary_contact: string`, `privacy_officer: string` (all
  nullable) so the baseline audience list resolves.

---

## Major

### M1. `BudgetPolicy.approval_threshold_pct` is overloaded for two unrelated flows

- **Line 22079–22081**:

  > approval_threshold_pct … Percent increase above which a budget
  > change creates an Approval (default 50).

- **Line 10545–10555** (STORY-187 AC-001/002): the same field gates
  whether a **waiver** goes through Approval.
- **Line 10972–10980** (STORY-197 AC-002): the same field gates
  whether a **budget amount edit** goes through Approval.
- **Problem**: one field, two orthogonal decisions. A workspace that
  wants "edits over 10% need approval, but waivers always need
  approval" cannot express it. This is a quiet semantic collapse.
- **Fix**: split into `edit_approval_threshold_pct` and
  `waiver_approval_threshold_pct` on `BudgetPolicy`; update both
  stories.

### M2. Hard-cap block returns `429` while license violation returns `402` — same concept, two codes

- **Line 10647–10649** (STORY-189 AC-002):

  > The gateway returns 429 with "budget exhausted"
  > A BudgetEvent of type "enforce" is recorded

- FEAT-180 (line 2113) describes license-over-consumption hard-close
  as `402 Payment Required`. The RFC semantics for 429 are
  rate-limit; 402 is the stable "payment/policy gate" code.
- **Problem**: clients that programmatically differentiate retryable
  (429) from non-retryable (402) will treat a blown budget as a
  back-off-and-retry signal, which is wrong — the budget is not going
  to replenish on its own before the cycle rolls.
- **Fix**: return `402 Payment Required` with an error code like
  `budget_exhausted` and a `Retry-After` header only when the cycle
  boundary is within the retry horizon. Align with FEAT-180.

### M3. STORY-189 writes `AlertEvent` directly, bypassing EPIC-009 `AlertRule` lifecycle

- **Line 10638–10640** (STORY-189 AC-001):

  > An AlertEvent of severity "warn" is generated with type "budget.soft"
  > Traffic is not throttled

- EPIC-009 owns `AlertRule` (line 22157) and `AlertEvent` (line 22213)
  and provides lifecycle (FEAT-100), snooze/ack (FEAT-103), runbooks
  (FEAT-101). Budget-originated alerts skip all of this.
- **Problem**: two parallel alerting pipelines — the `BudgetEvent`
  timeline (FEAT-086) and ad-hoc `AlertEvent` writes from budget
  enforcement — with no rule, no cooldown, no snooze semantics. Users
  cannot snooze a noisy "budget.soft" alert using the same machinery
  they use elsewhere.
- **Fix**: either (a) route budget thresholds through an
  automatically-managed `AlertRule` per budget with
  `category="budget"`, so AC-001 becomes "the AlertRule fires" and
  inherits EPIC-009 lifecycle; or (b) duplicate acknowledgement /
  snooze onto `BudgetEvent` and explicitly state that budget signals
  are not in the EPIC-009 inbox. (a) is clearly preferable.

### M4. FEAT-091 "Overage notifications" overlaps EPIC-009 alert rules without a delineation rule

- **Line 1253–1260** (FEAT-091 description):

  > Notify designated recipients when actual spend exceeds the
  > budget, distinct from soft-threshold alerts.

- **Line 11166–11167** (STORY-200 non_functional):

  > Overage notifications are independent from BudgetPolicy
  > soft_alert_pct

- **Problem**: the doc creates three notification surfaces for budget
  state — `AlertEvent` on soft threshold (M3), `BudgetEvent` type
  `overage` (FEAT-091), and potential user-defined `AlertRule` on a
  `budget.*` metric via EPIC-009. None of the three stories declare
  "this is the only source of truth for overage paging"; none cite
  each other. Expect duplicate pages.
- **Fix**: pick one canonical emitter and state the other two are
  derived views. The most natural choice is a system-managed
  `AlertRule` per budget (metric `budget.utilisation_pct`), with
  FEAT-091 acting only as a pre-provisioned default rule set.

### M5. STORY-200 misinterprets `notifications_model` for self_hosted billing fallback

- **Line 11145** (STORY-200 AC-001):

  > In self_hosted mode Org.billing_contact has no meaning against
  > Antirion billing, so the same notification falls back to
  > Org.finance_contact if set else platform admin

- **Line 37** (baseline): "Tenant-scoped roles (a)(b)(c) behave
  identically in both modes."
- **Problem**: the story conflates "Antirion billing the tenant" with
  "the tenant's provider-passthrough budget overage". Budget overages
  are the tenant's own spend against upstream providers, and the
  tenant's own `billing_contact` is the right audience in both modes —
  the baseline states this explicitly. The fallback to
  `finance_contact` and then platform admin is invented by this story
  and inverts the baseline rule.
- **Fix**: drop the self_hosted special case from AC-001. Keep the
  audience as `Budget.owner_user_id` plus `Org.billing_contact`
  in both modes; if the org wants a distinct finance inbox, that is
  solved by introducing `finance_contact` (C7) and letting the tenant
  add it to the audience, not by mode-switching the fallback.

### M6. STORY-200 routes a per-budget event to `trust_and_safety` as an abuse signal — category mismatch

- **Line 11146**:

  > Sustained overage across the tenant roster in saas mode
  > additionally fans out to Antirion trust_and_safety as an
  > abuse-correlation signal; this branch is silently skipped in
  > self_hosted because the tenant set is 1

- **Line 38** (baseline): `trust_and_safety` covers "isolation
  breaches, abuse heuristics, sustained anomalies".
- **Problem**: cost overage is a commercial-health signal, not abuse.
  And "sustained overage across the tenant roster" is an aggregate
  signal that cannot be emitted from a single per-budget AC. This
  re-purposes the T&S queue for renewals/finance work; it belongs in
  the Antirion `renewals` queue (see line 37) or EPIC-013 FEAT-182.
- **Fix**: remove the T&S branch from STORY-200. If a cross-tenant
  cost-anomaly signal is needed, model it as a platform-operator
  FEAT under EPIC-013, not as a branch of a per-budget event.

### M7. `Budget.scope_id` is declared `uuid` but the STORY-186 example uses a slug

- **Line 22022–22024** (`scope_id: uuid, nullable: true`).
- **Line 10483** (STORY-186 AC-001):

  > I pick scope "team", scope_id "copilot", amount 120000, cycle "monthly"

- **Problem**: `copilot` is a team slug, not a UUID. Either the API
  accepts both and resolves slug → UUID before writing (undocumented),
  or the example is inconsistent with the data model. Either way it
  mis-trains readers on the API shape.
- **Fix**: change the example to a real UUID placeholder, or add an
  AC clarifying the slug-resolution contract.

### M8. STORY-186 path `/api/budgets` and STORY-189 path `/api/budgets/teams/:id/policy` split the resource identity

- **Line 10509** (STORY-186): `POST /api/budgets` with
  `scope`/`scope_id` in body.
- **Line 10653** (STORY-189): `PATCH /api/budgets/teams/:id/policy`
  scoped by team.
- **Line 10992** (STORY-197): `PUT /api/budgets/:id` scoped by Budget.
- **Line 11055** (STORY-198): `DELETE /api/budgets/:id` scoped by
  Budget.
- **Problem**: two coordinate systems on the same resource. `teams/:id`
  works only when a Budget is uniquely determined by team-in-cycle
  (STORY-186 AC-002 asserts this) but breaks for scope=project or
  scope=user. The public API gets confusing.
- **Fix**: canonicalise on `/api/budgets/:id` and provide a read-side
  `GET /api/budgets?scope=team&scope_id=:team_id` instead of the
  nested write paths.

### M9. STORY-197 creates Approval `kind="budget-overage"` for a size-increase edit — mis-kinded

- **Line 10978–10980** (STORY-197 AC-002):

  > I change amount from 5000 to 10000
  > Then → An Approval is created with kind "budget-overage"

- **Line 22626–22628** (Approval.kind enum): `budget-overage |
  policy-change | key-elevated-scope | routing-rule-change`.
- **Problem**: a budget amount increase is not an "overage". The
  `Approval.kind` enumeration is the spine of STORY-195's queue
  filter and STORY-196's decision flow; re-using `budget-overage` for
  size edits blurs the distinction and corrupts the queue metrics
  ("how many overages this month?").
- **Fix**: add `budget-change` (or `budget-amount-increase`) to the
  enum and use it here and in waiver-vs-edit flows.

### M10. STORY-190's downgrade targets cite model IDs that do not exist in the canonical catalog

- **Line 10689–10694** (STORY-190 AC-001):

  > A BudgetPolicy with … action "downgrade-model" to "claude-haiku-4-5"
  > A request to "claude-sonnet-4-5" arrives for the team

- The environment block declares `claude-opus-4-7`,
  `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` as canonical IDs;
  `claude-haiku-4-5` and `claude-sonnet-4-5` are not full IDs.
- **Problem**: example strings look like model IDs but don't match
  the IDs that must actually appear in `Model`. This is confusing
  when other stories use real IDs.
- **Fix**: rewrite examples with placeholder names (`model "cheaper"`,
  `model "expensive"`) or with the canonical IDs.

### M11. `Budget.spent` reconciliation with `Request.cost` is nowhere specified

- EPIC-008 FEAT-086 and the per-story non-functional boilerplate say
  "Counter reconciliation runs on a worker cadence; drift between
  live counters and ledger alerts" (e.g. line 10467), but no story
  defines:
  - who writes to `Budget.spent` on each request;
  - whether `cache_cost` (see `Request.cache_cost`, line 21470) is
    deducted from or added to the Budget;
  - whether downgraded requests (STORY-190) debit the original
    requested amount or the served amount (STORY-333 AC-002 says
    `cost reflects the model that actually served the request`, so
    the served amount, but EPIC-008 doesn't cross-reference this).
- **Problem**: the entire epic is ungrounded on how `Request.cost` →
  `Budget.spent` happens. Billing, budget enforcement and EPIC-006
  cache savings analytics all read the same cost source and will
  disagree without an explicit contract.
- **Fix**: add a story under FEAT-086 (or as a new FEAT) that
  specifies the `Request → Budget counter → ledger` pipeline,
  including:
  - which fields of `Request.cost` are summed into `Budget.spent`;
  - the cadence of the reconciliation worker and the drift alert
    threshold;
  - the downgrade accounting rule (served-cost vs requested-cost).

### M12. `Budget.projected` and `Budget.runs_out_on` denormalise a computation that has no persistence contract

- **Line 22029–22044** (Budget fields `projected`, `daily_burn`,
  `burn_7d`, `runs_out_on`).
- **Line 10717–10724** (STORY-191 AC-001): formula
  `spent + (7d_burn * days_left * trend)`.
- **Problem**: four derived fields live on `Budget`, the formula uses
  a `trend` factor that is never defined, and the non-functional
  note says "Projection recomputed at least every hour" (line 10739)
  — but no story owns the worker, the `trend` definition, or the
  atomicity of the four-field write. STORY-192's backtest (MAPE,
  bias) implies the projection is stored historically, but nothing
  does that either (no `BudgetForecast` or `Forecast` model exists).
- **Fix**: either introduce a `BudgetForecast` model with
  `(budget_id, as_of, projected, runs_out_on, trend, method_version)`
  and move the four derived fields off `Budget`, or fully define
  `trend` and the refresh worker in a story under FEAT-085.

### M13. STORY-208 "Edit cascades" claims immediate propagation; baseline gives 30 s

- **Line 11407–11413** (STORY-208 AC-003):

  > A library policy is attached to 5 Budgets
  > … I edit thresholds
  > Then → All attached Budgets immediately see the new policy

- **Line 21** (baseline): routing rules, model catalog, safety **and
  budget policies**, rate limits, alert rules and feature flags
  propagate to every node within 30 seconds.
- **Problem**: AC says "immediately", baseline says "≤ 30s". A test
  written to the AC will flake against the baseline.
- **Fix**: reword AC-003 to "within 30 seconds" or to "is persisted
  and propagated via config_hot_reload" and link the baseline.

---

## Minor

### m1. `per-story non_functional` boilerplate is wrong for non-enforcement stories

Most EPIC-008 stories carry the three-line non_functional block about
shared-limiter 5 ms p95 and counter reconciliation (e.g. STORY-203 line
11279, STORY-214 line 11561, STORY-217 line 11634). That boilerplate is
pasted onto stories that have nothing to do with budget enforcement —
STORY-203 ("Create a project"), STORY-214 ("View invoice history"),
STORY-217 ("Downgrade plan"), STORY-219 ("View plan change history"),
etc. Minor, but it dilutes the signal of the constraint on stories that
actually enforce budgets.

**Fix**: keep the boilerplate only on stories that read or mutate
`Budget.spent` or enforce a `BudgetPolicy`.

### m2. `Budget.owner` vs `Budget.owner_user_id`

- **Line 11144** (STORY-200 AC-001) says "Notifications are sent to
  Budget.owner …"; the model field is `owner_user_id` (line 22060).
- **Fix**: use `Budget.owner_user_id` for clarity.

### m3. Waiver and rollover are high-impact but not gated by typed confirmation

The baseline `destructive_action_confirmation_policy` (line 5) does not
list "grant waiver" or "reset cycle". STORY-193 lets an admin raise a
hard cap with no typed-confirmation step, and STORY-199 zero-outs
`Budget.spent` at cycle roll without any operator confirmation. By
comparison, STORY-218 ("Cancel plan", line 11650) requires typing the
workspace slug.

**Fix**: either extend the baseline policy to list "grant waiver > X%
of budget" and "force reset schedule change mid-cycle" as typed-
confirmation actions, or explicitly state in STORY-193 / STORY-199 that
no typed confirmation is needed and why.

### m4. STORY-202 AC-002 FX override skips audit of the magnitude

- **Line 11241–11244** (STORY-202 AC-002): force-override an FX rate
  writes an `FxRate` row with source "manual" but the AC does not
  record the override percentage or drift from the previous rate in
  AuditLog.
- **Fix**: include the prior rate and delta in the AuditLog entry.

### m5. `UserBudget.outlier` is a flag with no definition

- **Line 22129–22130**: `outlier: bool`. No story, AC, or description
  defines when the flag is set or read.
- **Fix**: either delete the field or add an AC in FEAT-083 / FEAT-085
  that computes it.

### m6. `Project` has no `deleted_at` despite STORY-206 doing a soft delete

- **Line 22088–22106** (Project has no `deleted_at`).
- **Line 11343** (STORY-206 AC-001): "The Project is soft-deleted".
- **Fix**: add `deleted_at: timestamp, nullable: true` to Project, as
  already exists on Budget (line 22066).

### m7. STORY-207 mentions a join table that is not modelled

- **Line 11374**:

  > Project.owner_user_id is updated (and additional owners are
  > recorded in a join table if multiple)

- **Fix**: either define the join table (`ProjectOwner(project_id,
  user_id, added_at)`) or drop the "if multiple" clause and confirm
  single-owner semantics.

### m8. STORY-208 AC-004 contradicts the "immediate cascade" claim for deletion

- **Line 11414–11421**: deletion of an in-use library policy is
  blocked. That is correct behaviour but it cuts against AC-003's
  "immediately see the new policy" framing — the policy is
  effectively a parent of its dependents, not a freely-editable
  value. Document that asymmetry.

### m9. FEAT-097 "Finance export and showback" is declared available in both modes but its stories never adapt

- **Line 1314–1321** (FEAT-097 description: saas includes Antirion plan
  fees; self_hosted is provider-passthrough only).
- **Line 11690–11698** (STORY-220) and **line 11715–11722** (STORY-221):
  neither AC mentions the mode-based differentiation — both read from
  "Billing" as if Antirion plan fees always exist.
- **Fix**: add a self_hosted AC or a "given the install mode is
  self_hosted, the CSV contains only provider-passthrough rows" clause.

### m10. STORY-193 grants a "one-time waiver" but the model has no expiry

- `BudgetEvent` (line 22131) carries only `t` (timestamp). A "waiver
  valid for this cycle" is a claim the data cannot verify.
- **Fix**: add `valid_until: timestamp` to the waiver record (via the
  proposed Waiver model in C1) so cycle rollover can tell a waiver
  from a prior cycle from the current one.

### m11. STORY-196 AC-003 "expired approval" has no UI/AC for bulk cleanup

- **Line 10919–10927**: a single expired approval is rendered with a
  disabled button. There is no AC to expire-out the queue on a
  worker cadence. The baseline `workers` block (line 18) lists many
  cleanup sweeps but does not mention approval expiry.
- **Fix**: add a line to FEAT-087 or a system worker entry that
  transitions `Approval.status` from pending → expired on
  `now() > expires_at`.

---

## Cross-epic

### X1. EPIC-006 (caching) × EPIC-008: cost-attribution contract is shared and undocumented

- `Request.cache_cost` exists (line 21470). EPIC-006 FEAT-066 "Cache
  hit-rate and savings analytics" (line 999) presents "cost saved";
  EPIC-008 FEAT-082 dashboards "total spent" and EPIC-011 FEAT-141
  computes `cost`. Three epics, one number, zero handshake. See M11.
- **Fix**: include a paragraph on "Savings vs. spent reconciliation"
  in both FEAT-066 and FEAT-086, referencing FEAT-141 as the single
  write path for `Request.cost`.

### X2. EPIC-009 (alerts) × EPIC-008: budget signals bypass the alert lifecycle

- STORY-189 writes `AlertEvent` directly; STORY-200 writes
  `BudgetEvent` only. EPIC-009 lifecycle (FEAT-100 ack/resolve,
  FEAT-103 snooze, FEAT-105 on-call escalation) is inapplicable to
  both paths. See M3, M4.
- **Fix**: canonicalise all budget-origin alerting through
  `AlertRule` with category `budget`; budget-specific ACs should add
  acknowledge / snooze / on-call wiring as EPIC-009 provides it.

### X3. EPIC-010 (workspace admin) × EPIC-008: billing contact plumbing is incomplete

- EPIC-010 FEAT-107 (line 1421) owns the org contact fields; EPIC-008
  consumers read contact fields that don't exist on the Org model
  (see C7). The fix lives in FEAT-107, not EPIC-008, but the problem
  is only visible from EPIC-008's stories.
- **Fix**: extend Org per C7 in FEAT-107; this unblocks STORY-192,
  STORY-200, STORY-202.

### X4. EPIC-011 (gateway) × EPIC-008: FEAT-141 is the single writer and is never cited

- FEAT-141 (line 1744) owns cost computation, token counting,
  attribution across org/team/project/user/key, and Idempotency-Key.
  EPIC-008 needs all of that but cites none of it from any story or
  feature description. A reader cannot infer that `Request.cost` is
  written by FEAT-141 and must be read consistently by FEAT-082 /
  FEAT-086 / FEAT-097.
- **Fix**: reference FEAT-141 explicitly in FEAT-082, FEAT-086 and
  FEAT-097 descriptions as the upstream cost source.

### X5. FEAT-151 (Batches) is cited in the brief as "cost attribution" — that's FEAT-141

- **Line 1826–1827** (FEAT-151 description): "Accept batch
  create/status/cancel and attribute cost at batch-item granularity."
- The brief for this audit named FEAT-151 as the cost-attribution
  feature, but the real cross-cut is FEAT-141 (line 1744). FEAT-151
  is in scope only if Batches are used; its cost attribution is a
  thin layer on top of FEAT-141. This is worth noting so future
  readers are not mis-routed.
- **Fix**: nothing to change in the file; noted here for audit
  accuracy.

### X6. EPIC-011 FEAT-139 ID swap (see C5)

Already critical; restated here because its effect on EPIC-008 is
indirect — EPIC-008 inherits counter semantics from the baseline, and
the baseline cites a wrong-titled peer.

### X7. Self_hosted mode: three EPIC-008 features are mode-gated, but `Billing` model is not

- FEAT-095 (line 1294), FEAT-096 (line 1306), FEAT-098 (line 1325)
  all 404 in self_hosted; yet the `Billing` model (line 22587)
  carries Antirion-only fields (`plan`, `contract_start`,
  `contract_end`, `commitment`, `commitment_used`, `next_invoice_at`)
  with no nullability on most of them (e.g. `plan: string` is not
  nullable). FEAT-107 (line 1422) declares Billing as org-scoped
  data; FEAT-175 declares a separate license/entitlement path for
  self_hosted. So self_hosted installs have a half-populated
  `Billing` row whose mandatory fields are semantically empty.
- **Fix**: either mark the Antirion-only `Billing` fields nullable
  and document that they are always null in self_hosted, or split
  `Billing` into `AntirionBilling` (saas only) and a shared
  `FinancialContext` that self_hosted can populate.

---

## Missing / dangling references

A full sweep of every `FEAT-XXX` and `STORY-XXX` id mentioned inside
EPIC-008 text (descriptions, acceptance criteria, dependencies,
cross-references) against the definitions in `requirements.yaml`:

### (a) Cited feature / story with no matching definition

| Citing line | Cited id | Status | Notes |
|---|---|---|---|
| 10538 | `STORY-088` | **Broken** — resolves to an unrelated observability story (CSV export, FEAT-036). See C6. |
| 10538 | `STORY-091` | **Broken** — resolves to a request-compare story (FEAT-038). See C6. |
| 20 (baseline) | `FEAT-139` | **Mis-titled** — EPIC-008 inherits its `shared_limiters` grounding from this baseline line, which names a feature whose actual title is "Retry, timeout and runtime failover". The real edge-rate-limit feature is `FEAT-138`. See C5. |

All intra-EPIC dependency edges (`depends_on`) resolve correctly:

- STORY-185 → STORY-184 ✓
- STORY-187 (no `depends_on` block) — the broken refs above are in
  the narrative, not the dependency list.
- STORY-188 → STORY-185 ✓
- STORY-189 → STORY-185 ✓
- STORY-190 → STORY-189 ✓
- STORY-191 → STORY-185 ✓
- STORY-193 → STORY-189 ✓
- STORY-194 → STORY-184 ✓
- STORY-196 → STORY-195 ✓
- STORY-197 → STORY-188 ✓
- STORY-198 → STORY-197 ✓

All FEAT-175 and FEAT-179 cross-refs in EPIC-008 feature descriptions
resolve:

- FEAT-095 description (line 1294) → FEAT-175 ✓
- FEAT-096 description (line 1306) → FEAT-175 ✓
- FEAT-098 description (line 1325) → FEAT-175 ✓
- STORY-200 AC-001 (line 11146) → FEAT-179 (implicitly via
  trust_and_safety; no direct citation) — see M6.

### (b) Dependency implied by narrative but never declared

| EPIC-008 site | Implied dependency | Declared? |
|---|---|---|
| STORY-184 dashboard roll-up from `Request.cost` (line 10425) | EPIC-011 FEAT-141 (cost writes) | **No** — never cross-referenced from EPIC-008. See X4. |
| STORY-189 hard-cap enforcement at the gateway (line 10647) | EPIC-011 FEAT-138 (edge rate limits) and FEAT-139 (retry/timeout) | **No** — the gateway-side enforcement point is not cited. |
| STORY-185 non-functional `shared limiter store` (line 10466) | `non_functional_baseline.shared_limiters` via the correct FEAT-138 | **Broken** — see C5. |
| STORY-200 notification routing (line 11144) | EPIC-009 FEAT-102 (channels), `notifications_model` | FEAT-102 not cited; audience model partly cited but misapplied (M5). |
| STORY-197 edit-with-approval (line 10979) | EPIC-008 FEAT-087 Approval lifecycle | Not cross-referenced; works only by convention on `Approval.kind`. |

### (c) Scope the epic promises but is absent from the feature list

- **Waiver model**: EPIC-008 description (line 193) promises "waivers"
  as a first-class concept. No `Waiver` model exists; waivers are
  encoded as `BudgetEvent.type="waiver"` with **no amount field**
  (C1) and **no approval linkage** (C2). A dedicated model or
  field-set is absent.
- **Forecast model**: EPIC-008 description promises "forecasts and
  runout projections". No `Forecast` / `BudgetForecast` model
  exists; the derived fields live on `Budget` itself (line 22029–
  22044) with no definition of `trend`, no historical series, and
  STORY-192's backtest has no store to read from. See M12.
- **Enforcement audit**: EPIC-008 description promises "enforcement
  audit". `BudgetEvent.type="enforce"` exists (line 22141) but
  carries no field identifying which request was blocked, nor which
  upstream model was attempted. Enforcement rows cannot be
  post-hoc reconciled against `Request` rows.
- **Project owner join table**: STORY-207 (line 11374) says
  "additional owners are recorded in a join table if multiple". No
  such join table is defined in the models section. See m7.
- **Usage model** (called out in the brief): there is no `Usage`
  model in `requirements.yaml`. `Request` is the durable row and
  `MetricSeries` (line 21518) is the pre-aggregated rollup. If the
  brief's "Usage" means `MetricSeries`, EPIC-008 never reads from
  it by that name.

### (d) Models declared and used consistently (for completeness)

`Budget`, `BudgetPolicy`, `Project`, `UserBudget`, `BudgetEvent`,
`Approval`, `AlertRule`, `AlertEvent`, `Billing`, `FxRate`,
`AuditLog`, `Org`, `Team`, `NotificationPreference`, `Request`,
`Model`, `RoutingRule`, `User`, `SupportTicket` — all defined in
the models section. No EPIC-008 reference points at an undefined
model name.

---

## Appendix — per-feature one-line verdicts

| Feature | Verdict |
|---|---|
| FEAT-082 Org and team budget overview | Core dashboard is sound; M11 (spent pipeline) and C7 (contacts) block clean rollout. |
| FEAT-083 Project/user allocation | Blocked by C3, C4, m6, m7 — model gaps make allocation un-implementable as written. |
| FEAT-084 Budget policies and enforcement | Core flow is sound; M1, M2, M3 need resolution before coding. |
| FEAT-085 Forecasts and runout | Blocked by M12 — no persistence, `trend` undefined. |
| FEAT-086 Waivers and budget events | Blocked by C1, C2 — model has no amount/approval fields. |
| FEAT-087 Approvals | M9, m11 — enum missing a kind, no expiry worker. |
| FEAT-088 Update budget | M9 again; otherwise fine. |
| FEAT-089 Delete budget | OK, with m3 open on typed confirmation policy. |
| FEAT-090 Rollover and reset | M13 (timing wording) and m3 on confirmation. |
| FEAT-091 Overage notifications | M4, M5, M6 — semantics scrambled across modes and alert surfaces. |
| FEAT-092 Multi-currency | M12-adjacent (FX history/backtest needs persistence); otherwise fine. |
| FEAT-093 Project lifecycle | m6, m7 — missing `deleted_at` and join table. |
| FEAT-094 Budget policy library | M13; also contradicts AC-004 deletion block with the "immediate cascade" framing. |
| FEAT-095 Billing operations | Mode-gating is clear; X7 on the `Billing` model needs cleanup. |
| FEAT-096 Plan lifecycle | Mode-gating is clear; X7 applies. |
| FEAT-097 Finance export and showback | m9 — stories don't branch on mode though the feature says they should. |
| FEAT-098 Contract commitment UI | Mode-gated cleanly; relies on `Billing.commitment_used` — see X7. |
