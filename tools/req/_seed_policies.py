#!/usr/bin/env python3
"""
One-off generator that extracts the policy + glossary seed files from the
project: block in docs/requirements.yaml. Idempotent. Run via:

    python tools/req/_seed_policies.py

Pass-1 only. Pass 2 will continue using these same files. Frontmatter ids
are deterministic synthetic ULIDs (sha256-derived randomness portion +
fixed timestamp portion), so re-running this script regenerates the same
ids byte-for-byte.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY = REPO_ROOT / "docs" / "requirements.yaml"
REQ = REPO_ROOT / "docs" / "requirements"
DATE = "2026-05-07"


def _load_ulid_module():
    spec = importlib.util.spec_from_file_location(
        "_req_ulid", Path(__file__).resolve().parent / "_ulid.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ULID = _load_ulid_module()
# Policies + glossary anchor a few minutes before the migration features so
# they sort first when ordered by id (which is timestamp-prefixed). Same seed
# every run → byte-identical output.
_POLICY_BASE_MS = 1_762_473_540_000   # 1 minute before MIGRATION_BASE_MS
_GLOSSARY_BASE_MS = 1_762_473_530_000  # 30 seconds earlier


def _policy_id(seed: str, slot: int) -> str:
    return f"gw_policy_{_ULID.synthetic_ulid(seed, _POLICY_BASE_MS + slot * 1000)}"


def _glossary_id(seed: str, slot: int) -> str:
    return f"gw_glossary_{_ULID.synthetic_ulid(seed, _GLOSSARY_BASE_MS + slot * 1000)}"


def yaml_dump(data: Dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False, width=2_000_000)


def write_file(path: Path, fm: Dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_text = yaml_dump(fm)
    if not body.endswith("\n"):
        body = body + "\n"
    path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")


def main() -> int:
    raw = yaml.safe_load(LEGACY.read_text(encoding="utf-8"))
    project = raw["project"]
    nfb = project["non_functional_baseline"]
    uib = project["ui_baseline"]
    dac = project["destructive_action_confirmation_policy"]

    policies = REQ / "_policies"
    glossary = REQ / "_glossary"

    # 1. UI baseline -----------------------------------------------------------
    ui_keys_order = ["accessibility", "loading_state", "empty_state", "error_state", "localization"]
    ui_body = ["# UI baseline\n", uib.get("description", "").strip(), ""]
    for k in ui_keys_order:
        if k in uib:
            ui_body.append(f"## {k.replace('_', ' ').title()}")
            ui_body.append("")
            ui_body.append(uib[k].strip())
            ui_body.append("")
    extra = {k: v for k, v in uib.items() if k not in (["description"] + ui_keys_order)}
    if extra:
        ui_body.append("## Other (preserved verbatim)")
        ui_body.append("")
        ui_body.append("```yaml")
        ui_body.append(yaml_dump(extra).rstrip())
        ui_body.append("```")
    write_file(
        policies / "ui_baseline.md",
        {
            "id": _policy_id("ui_baseline", 1),
            "type": "policy",
            "title": "UI baseline",
            "lifecycle": "active",
            "summary": "Cross-cutting UI standards every screen inherits.",
            "created": DATE,
            "updated": DATE,
        },
        "\n".join(ui_body).rstrip() + "\n",
    )

    # 2. Non-functional baseline -----------------------------------------------
    # Notifications_model + deployment_modes are also called out as standalone
    # policies (so individual stories can cite a stable anchor). The full body
    # here keeps them inline so this file remains the canonical reference.
    nfb_keys_order = [
        "deployment_model", "statelessness", "horizontal_scaling", "workers",
        "concurrency_and_backpressure", "shared_limiters", "config_hot_reload",
        "graceful_shutdown", "health_checks", "zero_downtime_deploy",
        "performance_slo", "performance_implementation_notes", "reference_benchmarks",
        "availability_slo", "multi_region_and_dr", "data_durability", "streaming",
        "observability", "security", "tenant_isolation", "portability",
        "deployment_modes", "notifications_model",
    ]
    nfb_body = ["# Non-functional baseline\n", nfb.get("description", "").strip(), ""]
    for k in nfb_keys_order:
        if k in nfb:
            nfb_body.append(f"## {k.replace('_', ' ').title()}")
            nfb_body.append("")
            nfb_body.append(nfb[k].strip())
            nfb_body.append("")
    extra = {k: v for k, v in nfb.items() if k not in (["description"] + nfb_keys_order)}
    if extra:
        nfb_body.append("## Other (preserved verbatim)")
        nfb_body.append("")
        nfb_body.append("```yaml")
        nfb_body.append(yaml_dump(extra).rstrip())
        nfb_body.append("```")
    write_file(
        policies / "non_functional_baseline.md",
        {
            "id": _policy_id("non_functional_baseline", 2),
            "type": "policy",
            "title": "Non-functional baseline",
            "lifecycle": "active",
            "summary": "Cross-cutting non-functional standards every service and story inherits.",
            "created": DATE,
            "updated": DATE,
        },
        "\n".join(nfb_body).rstrip() + "\n",
    )

    # 3. Notifications model ---------------------------------------------------
    write_file(
        policies / "notifications_model.md",
        {
            "id": _policy_id("notifications_model", 3),
            "type": "policy",
            "title": "Notifications model",
            "lifecycle": "active",
            "summary": "Canonical audience roles for every event-notification story.",
            "created": DATE,
            "updated": DATE,
        },
        "# Notifications model\n\n"
        + nfb["notifications_model"].strip()
        + "\n\n_Source: `_policies/non_functional_baseline.md#notifications-model`._\n",
    )

    # 4. Destructive action confirmation ---------------------------------------
    write_file(
        policies / "destructive_action_confirmation.md",
        {
            "id": _policy_id("destructive_action_confirmation", 4),
            "type": "policy",
            "title": "Destructive action confirmation",
            "lifecycle": "active",
            "summary": "Type-to-confirm vs click-to-confirm policy for destructive actions.",
            "created": DATE,
            "updated": DATE,
        },
        "# Destructive action confirmation\n\n" + dac["description"].strip() + "\n",
    )

    # 5. Deployment modes ------------------------------------------------------
    write_file(
        policies / "deployment_modes.md",
        {
            "id": _policy_id("deployment_modes", 5),
            "type": "policy",
            "title": "Deployment modes",
            "lifecycle": "active",
            "summary": "saas vs self_hosted, plus the installed_on dimension.",
            "created": DATE,
            "updated": DATE,
        },
        "# Deployment modes\n\n"
        + nfb["deployment_modes"].strip()
        + "\n\n_Source: `_policies/non_functional_baseline.md#deployment-modes`._\n",
    )

    # ---- Glossary ------------------------------------------------------------
    glossary_entries = [
        {
            "id": _glossary_id("shared_limiters", 1),
            "title": "Shared limiters",
            "summary": "Edge rate limits, budget counters and provider outbound limiters share a sliding-window store so horizontal scaling does not multiply effective limits.",
            "body": (
                "Edge rate limits (FEAT-138), budget counters (EPIC-008) and provider "
                "outbound limiters (FEAT-161) share a sliding-window implementation in a "
                "shared store (Redis), so adding gateway nodes does not multiply a tenant's "
                "effective limit. Idempotency-Key lookup (FEAT-141) is cluster-wide and "
                "survives node loss.\n\n"
                "See `_policies/non_functional_baseline.md#shared-limiters`."
            ),
        },
        {
            "id": _glossary_id("tenant_isolation", 2),
            "title": "Tenant isolation",
            "summary": "Every query partitioned by org_id; per-tenant quotas; continuously verified by FEAT-134.",
            "body": (
                "Every query is partitioned by `org_id`. Per-tenant quotas bound concurrency, "
                "CPU-seconds, queue slots and storage so a noisy tenant cannot degrade others. "
                "Tenant isolation is continuously verified by FEAT-134.\n\n"
                "See `_policies/non_functional_baseline.md#tenant-isolation`."
            ),
        },
        {
            "id": _glossary_id("platform_operator", 3),
            "title": "Platform operator",
            "summary": "The principal class that operates Antirion in saas (Antirion staff) or self_hosted (platform admin role).",
            "body": (
                "The platform-operator audience role resolves to Antirion staff accounts in "
                "saas mode and to principals holding the platform admin role on a self_hosted "
                "install. Platform-operator surfaces are EPIC-013 features.\n\n"
                "See `_policies/notifications_model.md` and `_policies/deployment_modes.md`."
            ),
        },
        {
            "id": _glossary_id("idempotency_key", 4),
            "title": "Idempotency key",
            "summary": "Cluster-wide Idempotency-Key lookup that lets the gateway dedupe retries; FEAT-141.",
            "body": (
                "An optional `Idempotency-Key` header on a gateway request causes the same "
                "response to be replayed for at-most-once semantics across retries. Lookup is "
                "cluster-wide and survives node loss; see FEAT-141 and "
                "`_policies/non_functional_baseline.md#shared-limiters`."
            ),
        },
        {
            "id": _glossary_id("budget_counter", 5),
            "title": "Budget counter",
            "summary": "Per-Budget shared-store counter that the hot path consults before admitting a request; reconciled to the persisted ledger by FEAT-186.",
            "body": (
                "A per-`Budget` counter held in the shared limiter store. Gateway budget "
                "admission (FEAT-187) reads this counter on the hot path; if the hard cap is "
                "reached the request is rejected with HTTP 402 (`error_code=\"budget_exhausted\"`). "
                "Counter write-back (FEAT-186) reconciles live counters against the persisted "
                "Request ledger on a worker cadence and raises `budget.counter.drift` on "
                "deviation.\n\n"
                "See FEAT-186, FEAT-187, FEAT-197 (budget→AlertRule bridge) and "
                "`_policies/non_functional_baseline.md#shared-limiters`."
            ),
        },
    ]

    for g in glossary_entries:
        slug = g["title"].lower().replace(" ", "_")
        write_file(
            glossary / f"{slug}.md",
            {
                "id": g["id"],
                "type": "glossary",
                "title": g["title"],
                "lifecycle": "active",
                "summary": g["summary"],
                "created": DATE,
                "updated": DATE,
            },
            f"# {g['title']}\n\n{g['body']}\n",
        )

    print(f"wrote {len(list(policies.glob('*.md')))} policies and {len(list(glossary.glob('*.md')))} glossary entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
