# Deferred Follow-ups

Items surfaced during the EPIC-001..013 audit pass that were not applied to `docs/requirements.yaml` because they require product input, propose net-new features, or conflict with other findings.

Each entry: brief description, source audit citation, reason deferred.

## Items

### EPIC-001

- **m-4 STORY-003 "Forgot?" component naming** — audit wants a named screen/component for the Forgot-password link on the Login screen. Needs design input to confirm the component tree. (docs/audit/epic-001-review.md §m-4)
- **m-6 STORY-012 role-change notification audience** — audit suggests notifying actor + target + Org.security_contact on role changes. Needs product input on canonical audience list for role-change events. (docs/audit/epic-001-review.md §m-6)
- **m-8 STORY-018 typed confirmation on offboard** — audit suggests either adding "offboard user" to destructive_action_confirmation_policy or requiring email-typed confirmation. Needs product policy decision. (docs/audit/epic-001-review.md §m-8)
- **m-11 FEAT-010 priority vs FEAT-003** — audit flags that SSO SLO at P1 undermines FEAT-003 sign-out-everywhere at P0 when Org.sso_enforced=true. Priority tradeoff needs product input. (docs/audit/epic-001-review.md §m-11)
- **X-2 STORY-020 cross-epic reference to FEAT-015** — audit suggests adding a `related_features` list; no such field in the current schema. Needs cross-epic linkage convention. (docs/audit/epic-001-review.md §X-2)
- **X-3 STORY-018/019 cross-epic references to EPIC-003** — same issue as X-2. (docs/audit/epic-001-review.md §X-3)

### EPIC-002

- **C-4 FEAT-021/STORY-048 duplication of FEAT-003/STORY-006** — audit recommends collapsing FEAT-021 into FEAT-003 and moving STORY-048 list AC into STORY-006. Partial fix applied (depends_on added); full collapse requires product decision on feature ownership. (docs/audit/epic-002-review.md §C-4)
- **m-8 STORY-043 quiet-hours semantics** — single global user-level setting vs per-event overrides. Model and API disagree; needs product input. (docs/audit/epic-002-review.md §m-8)
- **(b)3 STORY-043 → FEAT-102 dependency** — canonical channel routing link not declarable without cross-epic reference field. (docs/audit/epic-002-review.md §(b)3)
- **(b)4/5 STORY-044 → FEAT-102 / FEAT-167 / FEAT-179 dependencies** — same linkage convention gap. (docs/audit/epic-002-review.md §(b)4-5)
- **(c)2 FEAT-015 trusted-browser list & individual revoke** — audit suggests a new story or AC to list/revoke TrustedBrowser rows individually. Needs product input. (docs/audit/epic-002-review.md §(c)2)

### EPIC-003

- **m7 Approval.kind shared between FEAT-027 and FEAT-160** — audit wants a separate Approval.kind for break-glass key creation vs elevated-scope grant. Belongs in the EPIC-011 pass. (docs/audit/epic-003-review.md §m7)
- **X1 FEAT-133 BYOK data class enumeration** — add BYOK credential ciphertext as a CMK-wrappable data class in FEAT-133. Deferred to EPIC-010 pass. (docs/audit/epic-003-review.md §X1)
- **(c) BYOK rotation policy edit story** — `rotate_policy_days` observable but not editable; needs a new story under FEAT-025. Product input required. (docs/audit/epic-003-review.md §(c))

### EPIC-004

- **C1 conflict FEAT-041 citation** — EPIC-003 audit proposed FEAT-024; EPIC-004 audit proposed FEAT-033. Applied later (more specific) fix to FEAT-033. Flagging in case reviewers disagree. (docs/audit/epic-003-review.md §C4 + docs/audit/epic-004-review.md §C1)
- **M2 FEAT-031 tools/flags drill-in** — add ACs surfacing per-request tool invocation list and safety/pii flag rationale. Needs product input on drawer UI. (docs/audit/epic-004-review.md §M2)
- **M6 FEAT-033 to EPIC-009 alerts integration** — add a story bridging Anomaly → Alert / AlertEvent. Needs product input. (docs/audit/epic-004-review.md §M6)
- **m1 non_functional copy-paste drift** — broad editorial pass to prune per-story NFR lists that inherit inapplicable constraints. Deferred; out of scope for the targeted-fix round. (docs/audit/epic-004-review.md §m1)

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

