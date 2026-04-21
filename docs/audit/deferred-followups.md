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

