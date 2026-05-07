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
└── gw_epic_00008_budgets-and-cost-control/
    ├── EPIC.md                        # epic-level narrative
    └── gw_feature_00081_org-and-team-budget-overview/
        ├── FEATURE.md                 # feature-level narrative
        └── gw_story_00183_view-org-wide-budget-health/
            └── STORY.md               # story-level: ACs, API, UI, data models, NFRs
```

Three semantic levels exist (`epic → feature → story`), each on its own
folder. Files are named `EPIC.md`, `FEATURE.md`, `STORY.md` so an editor's
tab title matches the role of the file. Every folder name is
`<id>_<kebab-slug>`; both halves of the folder name are validated.

## 2. Frontmatter contract

Every file starts with a YAML frontmatter block delimited by `---`. The
schema at [`_schema.json`](./_schema.json) enforces:

- `id` matches `^gw_(epic|feature|story|policy|glossary)_[0-9]{5}$`
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

## 3. CLI usage

The blessed way to mutate frontmatter is the
[`tools/req/req`](../../tools/req/req) CLI. Every subcommand is idempotent.

```bash
# Validate every file. Exits non-zero on any failure.
tools/req/req validate

# Regenerate _index.json + the <!-- generated --> child blocks.
tools/req/req index

# Create a new epic.
tools/req/req new epic --title "Audit and compliance"

# Create a feature under an epic.
tools/req/req new feature --parent gw_epic_00008 --title "FX rates"

# Create a story under a feature.
tools/req/req new story --parent gw_feature_00091 --title "FX refresh cadence"

# Move a story under a different feature.
tools/req/req mv gw_story_00200 --to gw_feature_00091

# Atomically rename slug + title.
tools/req/req rename gw_story_00200 --title "Daily FX refresh"

# Per-discipline status shorthand.
tools/req/req status gw_story_00200 backend=in_progress qa=blocked

# Generic frontmatter update (dotted keys allowed).
tools/req/req update gw_story_00200 release=v1.1 status.docs=done

# Print the minimal LLM reading set for a node (parent chain, depends_on,
# related, also_under, inherited policies, glossary terms cited in body).
tools/req/req context gw_story_00183

# Visualize a node's neighborhood.
tools/req/req graph gw_feature_00081 --depth 3

# List release: mvp items by epic.
tools/req/req mvp
```

## 4. Inheritance model

Every feature and story **silently** inherits the two baselines:

- [`_policies/non_functional_baseline.md`](_policies/non_functional_baseline.md)
- [`_policies/ui_baseline.md`](_policies/ui_baseline.md)

You don't list them in `inherits_policies` unless you also want to be
explicit. Deviations only appear via `overrides:`:

```yaml
overrides:
  - policy: gw_policy_00002         # non_functional_baseline
    key:    performance_slo
    reason: streaming endpoint relaxes p99 to 25ms
```

`req context <id>` exposes the inherited set automatically, so an LLM can
read the right set of policies without you having to repeat them on every
story.

## 5. Querying `_index.json`

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

# Fan-out from a single feature.
jq '.edges
    | map(select(.from == "gw_feature_00081"))' \
   docs/requirements/_index.json

# How many features per epic?
jq '.nodes
    | to_entries
    | map(select(.value.type == "feature"))
    | group_by(.value.parent)
    | map({parent: .[0].value.parent, count: length})' \
   docs/requirements/_index.json
```

## 6. For AI agents

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
- **`req new` allocates ids for you.** Don't pick numeric ids manually —
  the CLI scans the tree (and the legacy YAML) so it never collides.

## 7. Migration helper

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
