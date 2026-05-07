# Antirion requirements graph

This directory holds the Antirion product requirements as a graph of nested
Markdown files. The migration from the legacy `docs/requirements.yaml`
monolith proceeds in two passes:

| Pass | Scope                                                  | Status                       |
|------|--------------------------------------------------------|------------------------------|
| 1    | Schema, tooling, policies, glossary, **EPIC-008 only** | ✅ this PR                   |
| 2    | Remaining 14 epics                                      | pending; opens after pass 1 lands |

Until pass 2 lands, every epic *other than* EPIC-008 still lives in
`docs/requirements.yaml`. **Do not delete the legacy YAML.** Cross-epic
references that originate inside EPIC-008 and point at IDs that haven't been
migrated yet are recorded under each node's **Notes** section as
`External cross-epic references (will move to frontmatter once their epic
is migrated in pass 2)` — they will move back into frontmatter once those
ids exist in the tree.

---

## 1. Folder shape

```
docs/requirements/
├── README.md                          # this file
├── _schema.json                       # JSON Schema draft 2020-12 — frontmatter contract
├── _index.json                        # generated, committed; rebuild with `req index`
├── _policies/                         # cross-cutting policies (cited by every feature/story)
│   ├── ui_baseline.md
│   ├── non_functional_baseline.md
│   ├── notifications_model.md
│   ├── destructive_action_confirmation.md
│   └── deployment_modes.md
├── _glossary/                         # short term entries (paragraph + cite source)
│   └── …
└── gw_epic_01K9DT8DR0M1FET9FEG4MR6F0S_budgets-and-cost-control/
    ├── EPIC.md                        # epic-level narrative
    └── gw_feature_01K9DYE3303ZBCMT6S2DCWEBVQ_org-and-team-budget-overview/
        ├── FEATURE.md                 # feature-level narrative
        └── gw_story_01K9DYE3303ZBCMT…_view-org-wide-budget-health/
            └── STORY.md               # story-level: ACs, API, UI, data models, NFRs
```

Three semantic levels exist (`epic → feature → story`), each on its own
folder. Files are named `EPIC.md`, `FEATURE.md`, `STORY.md` so an editor's
tab title matches the role of the file. Every folder name is
`<id>_<kebab-slug>`; both halves of the folder name are validated.

## 2. Identity and ordering

**IDs are ULIDs.** Each node id is `gw_<type>_<26-char Crockford base32>`
— a real ULID for nodes created post-migration, and a deterministic
synthetic ULID for nodes converted from `docs/requirements.yaml` (the
randomness portion is the first 80 bits of `sha256(legacy_id)`, the
timestamp portion is `MIGRATION_BASE_MS + 60_000 * legacy_seq`, so id
sort order matches the legacy YAML's numeric order). IDs are immutable
once allocated. Adding or deleting a node never triggers renumbering of
other nodes.

**`order` is a per-parent integer with sparse step.** New nodes default
to `max_sibling_order + 100`. To insert between two siblings with orders
`A` and `B`, set the new order to `(A + B) // 2`. After roughly seven
nested midpoint inserts in the same gap the integer space collapses;
when that happens, `req rebalance <parent>` re-spaces every child by
`step` (default 100) in stable order. Order has meaning only relative to
siblings — there is no global order.

## 3. Frontmatter contract

Every file starts with a YAML frontmatter block delimited by `---`. The
schema at [`_schema.json`](./_schema.json) enforces:

- `id` matches `^gw_(epic|feature|story|policy|glossary)_[0-9A-HJKMNP-TV-Z]{26}$`
- `type` matches the file (`epic` ↔ EPIC.md, `feature` ↔ FEATURE.md, …)
- `parent` resolves to a node of the appropriate type (epic for features,
  feature for stories) **and** equals the enclosing folder's id
- `release ∈ {mvp, v1.1, v2.0, backlog}`
- `lifecycle ∈ {active, retired, deferred, cancelled}`
- `status` is a per-discipline block (`backend`, `frontend`, `infra`,
  `docs`, `qa`), each one of `not_started | in_progress | review | done |
  blocked | n_a`
- Optional graph edges: `also_under`, `depends_on`, `related`,
  `supersedes`, `superseded_by`, `inherits_policies`, `overrides`

Body markdown also has required headings — see the brief or
`tools/req/req.py REQUIRED_HEADINGS`.

## 4. CLI usage

The blessed way to mutate frontmatter is the
[`tools/req/req`](../../tools/req/req) CLI. Every subcommand is idempotent.
The IDs in the examples below abbreviate ULIDs to the prefix for readability;
in practice you'd paste the full 26-character ULID.

```bash
# Validate every file. Exits non-zero on any failure.
tools/req/req validate

# Regenerate _index.json + the <!-- generated --> child blocks.
tools/req/req index

# Create a new epic. The CLI mints a fresh ULID and picks an order.
tools/req/req new epic --title "Audit and compliance"

# Create a feature under an epic.
tools/req/req new feature --parent gw_epic_01K9DT8…M6F0S --title "FX rates"

# Create a story under a feature.
tools/req/req new story --parent gw_feature_01K9DZ0D106BQ4Y5P2K0CY0RM4 \
    --title "FX refresh cadence"

# Insert a new story between two existing siblings (orders 200 and 300).
tools/req/req new story --parent gw_feature_01K9DZ0D…CY0RM4 \
    --title "Quarterly FX rebase" --order 250

# Re-space children of a parent when an order gap collapses.
tools/req/req rebalance gw_feature_01K9DZ0D…CY0RM4 --step 100

# Move a story under a different feature.
tools/req/req mv gw_story_01K9DZ0D… --to gw_feature_01K9DZ0D…

# Atomically rename slug + title.
tools/req/req rename gw_story_01K9DZ0D… --title "Daily FX refresh"

# Per-discipline status shorthand.
tools/req/req status gw_story_01K9DZ0D… backend=in_progress qa=blocked

# Generic frontmatter update (dotted keys allowed).
tools/req/req update gw_story_01K9DZ0D… release=v1.1 status.docs=done

# Print the minimal LLM reading set for a node (parent chain, depends_on,
# related, also_under, inherited policies, glossary terms cited in body).
tools/req/req context gw_story_01K9DZ0D…

# Visualize a node's neighborhood.
tools/req/req graph gw_feature_01K9DZ0D… --depth 3

# List release: mvp items by epic.
tools/req/req mvp
```

## 5. Inheritance model

Every feature and story **silently** inherits the two baselines:

- [`_policies/non_functional_baseline.md`](_policies/non_functional_baseline.md)
- [`_policies/ui_baseline.md`](_policies/ui_baseline.md)

You don't list them in `inherits_policies` unless you also want to be
explicit. Deviations only appear via `overrides:`:

```yaml
overrides:
  - policy: gw_policy_01K9DT8DR…   # non_functional_baseline (look up the full ULID in _index.json)
    key:    performance_slo
    reason: streaming endpoint relaxes p99 to 25ms
```

`req context <id>` exposes the inherited set automatically, so an LLM can
read the right set of policies without you having to repeat them on every
story.

## 6. Querying `_index.json`

`_index.json` is the on-disk projection of the graph (nodes + edges). It
is regenerated by `req index` and committed so consumers don't have to
read 900 files. Examples with `jq`:

```bash
# All MVP stories, sorted by order.
jq -r '.nodes
       | to_entries[]
       | select(.value.type == "story" and .value.release == "mvp")
       | .value
       | "\(.order)\t\(.id)\t\(.title)"' \
   docs/requirements/_index.json | sort -n

# Fan-out from a single feature (replace the ULID with the one you care about).
jq '.edges
    | map(select(.from == "gw_feature_01K9DYE3303ZBCMT6S2DCWEBVQ"))' \
   docs/requirements/_index.json

# Resolve a title to its ULID (you almost always start here).
jq -r '.nodes
       | to_entries[]
       | select(.value.title | test("Org and team budget"; "i"))
       | "\(.value.id)\t\(.value.title)"' \
   docs/requirements/_index.json

# How many features per epic?
jq '.nodes
    | to_entries
    | map(select(.value.type == "feature"))
    | group_by(.value.parent)
    | map({parent: .[0].value.parent, count: length})' \
   docs/requirements/_index.json
```

## 7. For AI agents

If you are an LLM-based assistant adding to or editing the graph:

- **Always go through the CLI**, never edit frontmatter by hand. The CLI
  is the only blessed mutation path; it stamps `updated:` and re-runs the
  validator on the next commit.
- **Read context with `req context <id>`** before editing. It returns the
  short list of files an LLM should load to understand a node — its
  parent chain, depends_on/related/also_under, inherited policies, and
  glossary terms cited in its body.
- **Never duplicate baseline content**. If your behaviour matches the
  non-functional or UI baseline, omit it. If it deviates, add a single
  entry to `overrides:` instead of redefining the whole field.
- **Run `tools/req/req validate` before pushing.** The pre-commit hook
  and CI both run it; failing locally first saves a round-trip.
- **`req new` allocates ids for you.** ULIDs are minted from the system
  clock + cryptographic randomness; never type one by hand. Use
  `_index.json` (or `req mvp` / `req graph`) to look up the id of a node
  you want to reference.
- **Use `req rebalance <parent>` if you hit `order gap collapsed`.** That
  error means the parent's children are packed too tight for another
  midpoint insert; `rebalance` re-spaces them and you can retry.

## 8. Migration helper

`tools/req/migrate_epic.py` is the script that converted EPIC-008. It is
deterministic and stays in the repo so pass 2 can run it on each
remaining epic, item by item:

```bash
python tools/req/migrate_epic.py EPIC-009     # one epic at a time
python tools/req/migrate_epic.py --all        # everything left in YAML
python tools/req/migrate_epic.py --dry-run EPIC-010
```

The helper records every manual-review note (self-edges in `depends_on`,
external cross-epic refs deferred to body) on stdout when it runs.
