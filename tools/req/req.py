#!/usr/bin/env python3
"""
Antirion requirements graph — single-file CLI.

Subcommands: validate | index | new | mv | rename | status | update | context | graph | mvp

The graph lives under docs/requirements/. Every node is a Markdown file
(EPIC.md / FEATURE.md / STORY.md / a policy or glossary file) starting with a
YAML frontmatter block delimited by `---`. The schema is docs/requirements/_schema.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

try:
    from jsonschema import Draft202012Validator
    HAVE_JSONSCHEMA = True
except ImportError:  # pragma: no cover - tested in CI
    HAVE_JSONSCHEMA = False

try:
    from ruamel.yaml import YAML as RuamelYAML
    HAVE_RUAMEL = True
except ImportError:
    HAVE_RUAMEL = False


# ---------------------------------------------------------------------------
# Constants and conventions
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
REQ_ROOT = REPO_ROOT / "docs" / "requirements"
SCHEMA_PATH = REQ_ROOT / "_schema.json"
INDEX_PATH = REQ_ROOT / "_index.json"

_ULID_BODY = r"[0-9A-HJKMNP-TV-Z]{26}"
ID_RE = re.compile(rf"^gw_(epic|feature|story|policy|glossary)_({_ULID_BODY})$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FOLDER_RE = re.compile(rf"^(gw_(?:epic|feature|story|policy|glossary)_{_ULID_BODY})_([a-z0-9-]+)$")
AC_HEADING_RE = re.compile(r"^### AC-\d{3} — .+")

# Order is a per-parent integer rank. Default sparse step lets us insert ~7
# nested midpoints before exhausting a gap; if a gap collapses, run
# `req rebalance <parent>` to space siblings out again.
DEFAULT_ORDER_STEP = 100

VALID_TYPES = ("epic", "feature", "story", "policy", "glossary")
VALID_RELEASES = ("mvp", "v1.1", "v2.0", "backlog")
VALID_LIFECYCLES = ("active", "retired", "deferred", "cancelled")
VALID_DISCIPLINES = ("backend", "frontend", "infra", "docs", "qa")
VALID_DISCIPLINE_STATES = (
    "not_started", "in_progress", "review", "done", "blocked", "n_a",
)

EXPECTED_FILENAME = {
    "epic": "EPIC.md",
    "feature": "FEATURE.md",
    "story": "STORY.md",
}

REQUIRED_HEADINGS = {
    "epic": [
        "# {title}",
        "## Summary",
        "## Features",
        "## Notes",
    ],
    "feature": [
        "# {title}",
        "## Summary",
        "## Stories",
        "## Notes",
    ],
    "story": [
        "# {title}",
        "## Narrative",
        "## Acceptance Criteria",
        "## API",
        "## UI",
        "## Data Models",
        "## Non-Functional Requirements",
        "## Notes",
        "## Open Questions",
    ],
}

GENERATED_BLOCK_START = "<!-- generated:children:start -->"
GENERATED_BLOCK_END = "<!-- generated:children:end -->"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Node:
    id: str
    type: str
    path: Path
    frontmatter: Dict[str, Any]
    body: str

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title", ""))

    @property
    def parent(self) -> Optional[str]:
        return self.frontmatter.get("parent")


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

FM_DELIM = "---"

def parse_file(path: Path) -> Tuple[Dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith(FM_DELIM + "\n") and not text.startswith(FM_DELIM + "\r\n"):
        raise ValueError(f"{path}: missing leading '---' frontmatter")
    rest = text[len(FM_DELIM) + 1 :]
    end = rest.find("\n" + FM_DELIM + "\n")
    if end == -1:
        # Try CRLF tolerance.
        end = rest.find("\n" + FM_DELIM + "\r\n")
        if end == -1:
            raise ValueError(f"{path}: missing closing '---' frontmatter")
    fm_text = rest[:end]
    body = rest[end + len("\n" + FM_DELIM + "\n") :]
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"{path}: invalid YAML frontmatter: {e}") from e
    if not isinstance(fm, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping, got {type(fm).__name__}")
    return fm, body


def write_file(path: Path, frontmatter: Dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_text = dump_yaml(frontmatter)
    if not body.endswith("\n"):
        body = body + "\n"
    text = f"{FM_DELIM}\n{fm_text}{FM_DELIM}\n{body}"
    path.write_text(text, encoding="utf-8")


def dump_yaml(data: Dict[str, Any]) -> str:
    """Stable YAML dump with sort_keys=False; uses ruamel when available for fidelity."""
    if HAVE_RUAMEL:
        from io import StringIO
        y = RuamelYAML()
        y.default_flow_style = False
        y.allow_unicode = True
        y.indent(mapping=2, sequence=4, offset=2)
        buf = StringIO()
        y.dump(data, buf)
        return buf.getvalue()
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )


# ---------------------------------------------------------------------------
# Slug, ID, counter helpers
# ---------------------------------------------------------------------------

def slugify(title: str, max_len: int = 60) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "untitled"


# Lazy import: the ULID generator lives in tools/req/_ulid.py. We avoid a
# package-level import at module top because tools/req's __init__.py would
# shadow it under some pytest collection modes.
def _import_ulid():
    import importlib.util
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("_req_ulid", here / "_ulid.py")
    assert spec and spec.loader, "could not load _ulid.py"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_id(kind: str) -> str:
    """Allocate a new id for `kind` using a real ULID (timestamp + random)."""
    if kind not in VALID_TYPES:
        raise ValueError(f"invalid kind: {kind}")
    return f"gw_{kind}_{_import_ulid().ulid_now()}"


def parse_id(node_id: str) -> Tuple[str, str]:
    """Return (kind, ulid_body) for a node id."""
    m = ID_RE.match(node_id)
    if not m:
        raise ValueError(f"invalid id: {node_id}")
    return m.group(1), m.group(2)


def folder_name(node_id: str, slug: str) -> str:
    return f"{node_id}_{slug}"


def order_for_new_child(parent_id: Optional[str], nodes: Optional[Dict[str, "Node"]] = None) -> int:
    """Pick an integer order that places this node after every existing sibling.
    If there are no siblings, returns DEFAULT_ORDER_STEP. Always non-negative."""
    if nodes is None:
        nodes = load_tree()
    siblings = [n for n in nodes.values() if n.frontmatter.get("parent") == parent_id]
    if not siblings:
        return DEFAULT_ORDER_STEP
    max_order = max(int(s.frontmatter.get("order") or 0) for s in siblings)
    return max_order + DEFAULT_ORDER_STEP


def order_between(left_order: int, right_order: int) -> int:
    """Midpoint integer order strictly between left and right, or raise if gap collapsed."""
    if right_order - left_order < 2:
        raise ValueError(
            f"order gap collapsed (between {left_order} and {right_order}); "
            f"run `req rebalance <parent>` to space siblings out again"
        )
    return (left_order + right_order) // 2


# ---------------------------------------------------------------------------
# Tree loading
# ---------------------------------------------------------------------------

def iter_node_files(root: Optional[Path] = None) -> Iterable[Path]:
    if root is None:
        root = REQ_ROOT
    if not root.exists():
        return
    for path in sorted(root.rglob("*.md")):
        if path.name.startswith("."):
            continue
        # README is documentation, not a node.
        if path.name == "README.md" and path.parent == root:
            continue
        yield path


def load_tree(root: Optional[Path] = None) -> Dict[str, Node]:
    if root is None:
        root = REQ_ROOT
    nodes: Dict[str, Node] = {}
    for path in iter_node_files(root):
        fm, body = parse_file(path)
        nid = fm.get("id")
        if not isinstance(nid, str):
            raise ValueError(f"{path}: frontmatter missing 'id'")
        if nid in nodes:
            raise ValueError(f"duplicate id {nid} in {path} and {nodes[nid].path}")
        node = Node(id=nid, type=fm.get("type", ""), path=path, frontmatter=fm, body=body)
        nodes[nid] = node
    return nodes


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class Validator:
    nodes: Dict[str, Node] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    schema: Optional[Dict[str, Any]] = None

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def load(self) -> None:
        self.nodes = load_tree()
        if SCHEMA_PATH.exists():
            self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def run(self) -> int:
        self.load()
        self.check_schema()
        self.check_id_format_and_filename()
        self.check_folder_id_consistency()
        self.check_release_enum()
        self.check_references()
        self.check_dag()
        self.check_body_headings()
        self.check_index_freshness()
        for e in self.errors:
            print("error: " + e, file=sys.stderr)
        return 0 if not self.errors else 1

    def check_schema(self) -> None:
        if self.schema is None:
            self.err(f"schema file missing: {SCHEMA_PATH}")
            return
        if not HAVE_JSONSCHEMA:
            self.err("jsonschema package not installed; run: pip install -r tools/req/requirements.txt")
            return
        validator = Draft202012Validator(self.schema)
        for node in self.nodes.values():
            for e in validator.iter_errors(node.frontmatter):
                path = "/".join(str(p) for p in e.absolute_path) or "<root>"
                self.err(f"{node.path}: schema [{path}]: {e.message}")

    def check_id_format_and_filename(self) -> None:
        seen: Dict[str, Path] = {}
        for node in self.nodes.values():
            m = ID_RE.match(node.id)
            if not m:
                self.err(f"{node.path}: id {node.id!r} does not match ^gw_(epic|feature|story|policy|glossary)_[0-9]{{5}}$")
                continue
            if node.id in seen and seen[node.id] != node.path:
                self.err(f"duplicate id {node.id} in {node.path} and {seen[node.id]}")
            seen[node.id] = node.path
            if m.group(1) != node.type:
                self.err(f"{node.path}: id type {m.group(1)!r} != frontmatter type {node.type!r}")
            expected = EXPECTED_FILENAME.get(node.type)
            if expected and node.path.name != expected:
                self.err(f"{node.path}: filename should be {expected}")

    def check_folder_id_consistency(self) -> None:
        for node in self.nodes.values():
            if node.type in ("policy", "glossary"):
                # No folder requirement; lives directly under _policies/ or _glossary/.
                bucket = "_policies" if node.type == "policy" else "_glossary"
                if node.path.parent.name != bucket:
                    self.err(f"{node.path}: {node.type} files must live under {bucket}/")
                continue
            folder = node.path.parent
            m = FOLDER_RE.match(folder.name)
            if not m:
                self.err(f"{node.path}: folder name {folder.name!r} must be <id>_<kebab-slug>")
                continue
            folder_id, slug = m.group(1), m.group(2)
            if folder_id != node.id:
                self.err(f"{node.path}: folder id {folder_id} does not match frontmatter id {node.id}")
            if not SLUG_RE.match(slug):
                self.err(f"{node.path}: slug {slug!r} not valid kebab-case ASCII")
            if len(slug) > 60:
                self.err(f"{node.path}: slug longer than 60 chars: {slug!r}")
            # parent folder check
            parent = node.frontmatter.get("parent")
            if parent:
                parent_dir = folder.parent
                pm = FOLDER_RE.match(parent_dir.name)
                if not pm or pm.group(1) != parent:
                    self.err(
                        f"{node.path}: declared parent {parent} does not match enclosing folder "
                        f"{parent_dir.name!r}"
                    )

    def check_release_enum(self) -> None:
        for node in self.nodes.values():
            r = node.frontmatter.get("release")
            if r is None:
                continue
            if r not in VALID_RELEASES:
                self.err(f"{node.path}: release {r!r} not in {VALID_RELEASES}")

    def check_references(self) -> None:
        ref_keys = ("parent", "also_under", "depends_on", "related",
                    "supersedes", "superseded_by", "inherits_policies")
        for node in self.nodes.values():
            for key in ref_keys:
                val = node.frontmatter.get(key)
                if val is None:
                    continue
                ids = [val] if isinstance(val, str) else list(val)
                for ref in ids:
                    if ref not in self.nodes:
                        self.err(f"{node.path}: {key} references unknown id {ref!r}")
            for ov in node.frontmatter.get("overrides") or []:
                if isinstance(ov, dict):
                    p = ov.get("policy")
                    if p and p not in self.nodes:
                        self.err(f"{node.path}: overrides[].policy unknown id {p!r}")

    def check_dag(self) -> None:
        graph: Dict[str, List[str]] = {
            nid: list(self.nodes[nid].frontmatter.get("depends_on") or [])
            for nid in self.nodes
        }
        # detect any cycle via DFS
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {nid: WHITE for nid in graph}
        parent: Dict[str, Optional[str]] = {nid: None for nid in graph}

        def dfs(start: str) -> None:
            stack: List[Tuple[str, int]] = [(start, 0)]
            while stack:
                node_id, idx = stack[-1]
                if idx == 0:
                    color[node_id] = GRAY
                neighbors = graph.get(node_id, [])
                if idx < len(neighbors):
                    nxt = neighbors[idx]
                    stack[-1] = (node_id, idx + 1)
                    if nxt not in graph:
                        continue  # missing-ref reported elsewhere
                    if color[nxt] == GRAY:
                        # reconstruct cycle path
                        cycle = [nxt]
                        cur = node_id
                        while cur is not None and cur != nxt:
                            cycle.append(cur)
                            cur = parent[cur]
                        cycle.append(nxt)
                        cycle.reverse()
                        self.err("depends_on cycle: " + " -> ".join(cycle))
                        return
                    if color[nxt] == WHITE:
                        parent[nxt] = node_id
                        stack.append((nxt, 0))
                else:
                    color[node_id] = BLACK
                    stack.pop()

        for nid in graph:
            if color[nid] == WHITE:
                dfs(nid)

    def check_body_headings(self) -> None:
        for node in self.nodes.values():
            if node.type not in REQUIRED_HEADINGS:
                continue
            required = [h.format(title=node.title) for h in REQUIRED_HEADINGS[node.type]]
            body_lines = node.body.splitlines()
            present_indexes: List[int] = []
            for needle in required:
                # allow whitespace normalization on title heading
                idx = -1
                for i, line in enumerate(body_lines):
                    if needle.startswith("# ") and not needle.startswith("## "):
                        if line.strip() == needle.strip():
                            idx = i
                            break
                    else:
                        if line.strip() == needle:
                            idx = i
                            break
                if idx < 0:
                    self.err(f"{node.path}: missing required heading {needle!r}")
                    return  # short-circuit per file is fine; collect more errors anyway
                present_indexes.append(idx)
            if present_indexes != sorted(present_indexes):
                self.err(f"{node.path}: required headings present but in wrong order")
            if node.type == "story":
                ac_section = self._slice_section(body_lines, "## Acceptance Criteria")
                for line in ac_section:
                    if line.startswith("### ") and not AC_HEADING_RE.match(line):
                        self.err(f"{node.path}: AC heading {line.strip()!r} must match '### AC-XYZ — <scenario>'")

    def _slice_section(self, lines: List[str], heading: str) -> List[str]:
        try:
            start = lines.index(heading)
        except ValueError:
            return []
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## ") and lines[j] != heading:
                end = j
                break
        return lines[start + 1 : end]

    def check_index_freshness(self) -> None:
        regenerated = build_index(self.nodes)
        if not INDEX_PATH.exists():
            self.err(f"{INDEX_PATH} missing — run: tools/req/req index")
            return
        try:
            current = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.err(f"{INDEX_PATH}: {e}")
            return
        # Strip generated_at from comparison so timestamp drift isn't a failure.
        a = dict(current)
        b = dict(regenerated)
        a.pop("generated_at", None)
        b.pop("generated_at", None)
        if a != b:
            self.err(f"{INDEX_PATH} stale — run: tools/req/req index")


# ---------------------------------------------------------------------------
# Index generation
# ---------------------------------------------------------------------------

def build_index(nodes: Dict[str, Node]) -> Dict[str, Any]:
    children: Dict[str, List[str]] = {nid: [] for nid in nodes}
    for n in nodes.values():
        p = n.frontmatter.get("parent")
        if p and p in children:
            children[p].append(n.id)
    edges: List[Dict[str, str]] = []
    out_nodes: Dict[str, Any] = {}
    for n in nodes.values():
        fm = n.frontmatter
        out_nodes[n.id] = {
            "id": n.id,
            "type": n.type,
            "title": fm.get("title"),
            "path": str(n.path.relative_to(REPO_ROOT)),
            "lifecycle": fm.get("lifecycle"),
            "release": fm.get("release"),
            "order": fm.get("order"),
            "parent": fm.get("parent"),
            "also_under": fm.get("also_under") or [],
            "depends_on": fm.get("depends_on") or [],
            "related": fm.get("related") or [],
            "status": fm.get("status"),
            "owners": fm.get("owners") or [],
            "tags": fm.get("tags") or [],
            "deployment_modes": fm.get("deployment_modes"),
            "installed_on": fm.get("installed_on"),
            "children": sorted(children.get(n.id, [])),
        }
        if fm.get("parent"):
            edges.append({"type": "parent", "from": n.id, "to": fm["parent"]})
        for x in fm.get("also_under") or []:
            edges.append({"type": "also_under", "from": n.id, "to": x})
        for x in fm.get("depends_on") or []:
            edges.append({"type": "depends_on", "from": n.id, "to": x})
        for x in fm.get("related") or []:
            edges.append({"type": "related", "from": n.id, "to": x})
        if fm.get("superseded_by"):
            edges.append({"type": "superseded_by", "from": n.id, "to": fm["superseded_by"]})
    edges.sort(key=lambda e: (e["type"], e["from"], e["to"]))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator_version": "1",
        "nodes": dict(sorted(out_nodes.items())),
        "edges": edges,
    }


def cmd_index(args: argparse.Namespace) -> int:
    nodes = load_tree()
    idx = build_index(nodes)
    INDEX_PATH.write_text(
        json.dumps(idx, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    # Also rewrite generated children blocks in EPIC.md / FEATURE.md
    rewrite_generated_blocks(nodes)
    print(f"wrote {INDEX_PATH.relative_to(REPO_ROOT)} ({len(nodes)} nodes)")
    return 0


def rewrite_generated_blocks(nodes: Dict[str, Node]) -> None:
    children: Dict[str, List[Node]] = {}
    for n in nodes.values():
        p = n.frontmatter.get("parent")
        if p:
            children.setdefault(p, []).append(n)
    for parent_id, kids in children.items():
        parent = nodes.get(parent_id)
        if parent is None or parent.type not in ("epic", "feature"):
            continue
        kids.sort(key=lambda n: (n.frontmatter.get("order") or 0, n.id))
        lines = []
        for k in kids:
            life = k.frontmatter.get("lifecycle", "active")
            tag = "" if life == "active" else f" _({life})_"
            rel = os.path.relpath(k.path, parent.path.parent)
            lines.append(f"- [{k.id}]({rel}) — {k.title}{tag}")
        body = parent.body
        new_block = (
            GENERATED_BLOCK_START + "\n"
            + ("\n".join(lines) if lines else "_(no children)_")
            + "\n" + GENERATED_BLOCK_END
        )
        if GENERATED_BLOCK_START in body and GENERATED_BLOCK_END in body:
            new_body = re.sub(
                re.escape(GENERATED_BLOCK_START)
                + r"[\s\S]*?"
                + re.escape(GENERATED_BLOCK_END),
                new_block,
                body,
                count=1,
            )
        else:
            # Inject under '## Stories' or '## Features' if present
            heading = "## Stories" if parent.type == "feature" else "## Features"
            if heading in body:
                # insert directly after heading line
                pieces = body.split(heading, 1)
                new_body = pieces[0] + heading + "\n\n" + new_block + "\n" + pieces[1].lstrip("\n")
            else:
                new_body = body.rstrip() + "\n\n" + new_block + "\n"
        if new_body != body:
            write_file(parent.path, parent.frontmatter, new_body)
            parent.body = new_body


# ---------------------------------------------------------------------------
# Validate command
# ---------------------------------------------------------------------------

def cmd_validate(args: argparse.Namespace) -> int:
    v = Validator()
    return v.run()


# ---------------------------------------------------------------------------
# new / mv / rename / status / update / context / graph / mvp
# ---------------------------------------------------------------------------

def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def initial_status_block() -> Dict[str, str]:
    return {d: "not_started" for d in VALID_DISCIPLINES}


def cmd_new(args: argparse.Namespace) -> int:
    kind = args.kind
    if kind not in VALID_TYPES:
        print(f"error: unknown type {kind}", file=sys.stderr)
        return 2
    title = args.title
    nid = make_id(kind)
    slug = slugify(title)
    nodes = load_tree() if kind in ("feature", "story") else {}
    if kind == "epic":
        folder = REQ_ROOT / folder_name(nid, slug)
        path = folder / "EPIC.md"
        order = args.order if args.order is not None else order_for_new_child(None, load_tree())
        fm = {
            "id": nid, "type": "epic", "title": title,
            "lifecycle": "active",
            "created": today(), "updated": today(),
            "release": args.release or "backlog",
            "order": order,
            "owners": [], "tags": [],
        }
        body = epic_body(title)
    elif kind == "feature":
        if not args.parent:
            print("error: feature requires --parent <epic-id>", file=sys.stderr)
            return 2
        parent_node = nodes.get(args.parent)
        if not parent_node or parent_node.type != "epic":
            print(f"error: parent {args.parent} is not an epic in tree", file=sys.stderr)
            return 2
        folder = parent_node.path.parent / folder_name(nid, slug)
        path = folder / "FEATURE.md"
        order = args.order if args.order is not None else order_for_new_child(args.parent, nodes)
        fm = {
            "id": nid, "type": "feature", "title": title,
            "lifecycle": "active",
            "created": today(), "updated": today(),
            "parent": args.parent,
            "release": args.release or "backlog",
            "order": order,
            "status": initial_status_block(),
            "deployment_modes": ["saas", "self_hosted"],
            "installed_on": "tenant_install",
            "owners": [], "tags": [],
        }
        body = feature_body(title)
    elif kind == "story":
        if not args.parent:
            print("error: story requires --parent <feature-id>", file=sys.stderr)
            return 2
        parent_node = nodes.get(args.parent)
        if not parent_node or parent_node.type != "feature":
            print(f"error: parent {args.parent} is not a feature in tree", file=sys.stderr)
            return 2
        folder = parent_node.path.parent / folder_name(nid, slug)
        path = folder / "STORY.md"
        order = args.order if args.order is not None else order_for_new_child(args.parent, nodes)
        fm = {
            "id": nid, "type": "story", "title": title,
            "lifecycle": "active",
            "created": today(), "updated": today(),
            "parent": args.parent,
            "release": args.release or "backlog",
            "order": order,
            "status": initial_status_block(),
            "narrative": {"as_a": "TBD", "i_want": "TBD", "so_that": "TBD"},
            "owners": [], "tags": [],
        }
        body = story_body(title, fm["narrative"])
    else:
        print("error: 'new' supports only epic|feature|story", file=sys.stderr)
        return 2
    if path.exists():
        print(f"error: {path} already exists", file=sys.stderr)
        return 2
    write_file(path, fm, body)
    print(f"created {path.relative_to(REPO_ROOT)} ({nid}, order={order})")
    return 0


def cmd_rebalance(args: argparse.Namespace) -> int:
    """Re-space order values for all children of a parent so future midpoint
    inserts have room. Stable sort by current order, then assign step*1, step*2..."""
    nodes = load_tree()
    parent = args.parent
    parent_node = nodes.get(parent) if parent else None
    if parent and parent_node is None:
        print(f"error: unknown parent {parent}", file=sys.stderr)
        return 2
    siblings = [n for n in nodes.values() if n.frontmatter.get("parent") == parent]
    siblings.sort(key=lambda n: (int(n.frontmatter.get("order") or 0), n.id))
    if not siblings:
        print(f"no children of {parent}; nothing to rebalance")
        return 0
    step = args.step
    for i, n in enumerate(siblings, start=1):
        new_order = i * step
        fm, body = parse_file(n.path)
        if int(fm.get("order") or 0) == new_order:
            continue
        fm["order"] = new_order
        fm["updated"] = today()
        write_file(n.path, fm, body)
    print(f"rebalanced {len(siblings)} children of {parent or '<root>'} (step={step})")
    return 0


def epic_body(title: str) -> str:
    return f"""# {title}

## Summary

TBD.

## Features

{GENERATED_BLOCK_START}
_(no children)_
{GENERATED_BLOCK_END}

## Notes

TBD.
"""


def feature_body(title: str) -> str:
    return f"""# {title}

## Summary

TBD.

## Stories

{GENERATED_BLOCK_START}
_(no children)_
{GENERATED_BLOCK_END}

## Notes

TBD.
"""


def story_body(title: str, narrative: Dict[str, str]) -> str:
    return f"""# {title}

## Narrative

As a {narrative['as_a']}, I want {narrative['i_want']} so that {narrative['so_that']}.

## Acceptance Criteria

### AC-001 — TBD

**Given:**

- TBD

**When:**

- TBD

**Then:**

- TBD

## API

_None._

## UI

_None._

## Data Models

_None._

## Non-Functional Requirements

_Inherits non_functional_baseline._

## Notes

_None._

## Open Questions

_None._
"""


def cmd_mv(args: argparse.Namespace) -> int:
    nodes = load_tree()
    node = nodes.get(args.id)
    if node is None:
        print(f"error: unknown id {args.id}", file=sys.stderr)
        return 2
    new_parent = nodes.get(args.to)
    if new_parent is None:
        print(f"error: unknown new parent {args.to}", file=sys.stderr)
        return 2
    expected_parent_type = {"feature": "epic", "story": "feature"}.get(node.type)
    if expected_parent_type and new_parent.type != expected_parent_type:
        print(f"error: parent must be a {expected_parent_type}", file=sys.stderr)
        return 2
    new_dir = new_parent.path.parent / node.path.parent.name
    if new_dir.exists():
        print(f"error: target dir already exists: {new_dir}", file=sys.stderr)
        return 2
    new_dir.parent.mkdir(parents=True, exist_ok=True)
    node.path.parent.rename(new_dir)
    new_path = new_dir / node.path.name
    fm, body = parse_file(new_path)
    fm["parent"] = args.to
    fm["updated"] = today()
    write_file(new_path, fm, body)
    print(f"moved {args.id} -> parent {args.to}")
    return 0


def cmd_rename(args: argparse.Namespace) -> int:
    nodes = load_tree()
    node = nodes.get(args.id)
    if node is None:
        print(f"error: unknown id {args.id}", file=sys.stderr)
        return 2
    new_slug = slugify(args.title)
    new_folder = node.path.parent.parent / folder_name(node.id, new_slug)
    if new_folder == node.path.parent:
        # only title change
        fm, body = parse_file(node.path)
        fm["title"] = args.title
        fm["updated"] = today()
        write_file(node.path, fm, body)
    else:
        if new_folder.exists():
            print(f"error: folder already exists: {new_folder}", file=sys.stderr)
            return 2
        node.path.parent.rename(new_folder)
        new_path = new_folder / node.path.name
        fm, body = parse_file(new_path)
        fm["title"] = args.title
        fm["updated"] = today()
        write_file(new_path, fm, body)
    print(f"renamed {args.id} -> {args.title!r}")
    return 0


def _set_dotted(target: Dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur: Any = target
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def _coerce_value(raw: str) -> Any:
    # Try int / yaml load
    if raw == "":
        return ""
    try:
        return yaml.safe_load(raw)
    except Exception:
        return raw


def cmd_update(args: argparse.Namespace) -> int:
    nodes = load_tree()
    node = nodes.get(args.id)
    if node is None:
        print(f"error: unknown id {args.id}", file=sys.stderr)
        return 2
    fm, body = parse_file(node.path)
    for assignment in args.assignments:
        if "=" not in assignment:
            print(f"error: assignment {assignment!r} must be key=value", file=sys.stderr)
            return 2
        key, value = assignment.split("=", 1)
        _set_dotted(fm, key.strip(), _coerce_value(value.strip()))
    fm["updated"] = today()
    write_file(node.path, fm, body)
    print(f"updated {args.id}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    # status <id> backend=done frontend=in_progress
    rewritten: List[str] = []
    for assignment in args.assignments:
        if "=" not in assignment:
            print(f"error: assignment {assignment!r} must be discipline=state", file=sys.stderr)
            return 2
        d, s = assignment.split("=", 1)
        d = d.strip()
        s = s.strip()
        if d not in VALID_DISCIPLINES:
            print(f"error: discipline {d!r} not in {VALID_DISCIPLINES}", file=sys.stderr)
            return 2
        if s not in VALID_DISCIPLINE_STATES:
            print(f"error: state {s!r} not in {VALID_DISCIPLINE_STATES}", file=sys.stderr)
            return 2
        rewritten.append(f"status.{d}={s}")
    args.assignments = rewritten
    return cmd_update(args)


def cmd_context(args: argparse.Namespace) -> int:
    nodes = load_tree()
    node = nodes.get(args.id)
    if node is None:
        print(f"error: unknown id {args.id}", file=sys.stderr)
        return 2
    seen: List[str] = []

    def add(n: Node) -> None:
        rel = str(n.path.relative_to(REPO_ROOT))
        if rel not in seen:
            seen.append(rel)

    add(node)
    cur = node
    while cur.frontmatter.get("parent"):
        cur = nodes.get(cur.frontmatter["parent"])
        if cur is None:
            break
        add(cur)
    for key in ("depends_on", "related", "also_under"):
        for ref in node.frontmatter.get(key) or []:
            n2 = nodes.get(ref)
            if n2:
                add(n2)
    inherited = node.frontmatter.get("inherits_policies")
    if inherited is None and node.type in ("feature", "story"):
        # implicit inheritance unless overridden
        for pid, n2 in nodes.items():
            if n2.type == "policy" and n2.frontmatter.get("title", "") in (
                "Non-functional baseline", "UI baseline"
            ):
                add(n2)
    elif isinstance(inherited, list):
        for pid in inherited:
            n2 = nodes.get(pid)
            if n2:
                add(n2)
    # glossary terms cited in body (very simple match by title)
    for n2 in nodes.values():
        if n2.type == "glossary":
            t = n2.frontmatter.get("title", "")
            if t and (t.lower() in node.body.lower()):
                add(n2)
    for r in seen:
        print(r)
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    nodes = load_tree()
    node = nodes.get(args.id)
    if node is None:
        print(f"error: unknown id {args.id}", file=sys.stderr)
        return 2
    depth = args.depth
    print(f"{node.id} — {node.title}")
    # parents
    cur = node
    indent = ""
    parents: List[Node] = []
    while cur.frontmatter.get("parent"):
        nxt = nodes.get(cur.frontmatter["parent"])
        if nxt is None:
            break
        parents.append(nxt)
        cur = nxt
    for p in reversed(parents[:depth]):
        print(f"  ^ {p.id} — {p.title}")
    # children
    children = [n for n in nodes.values() if n.frontmatter.get("parent") == node.id]
    children.sort(key=lambda n: (n.frontmatter.get("order") or 0, n.id))
    for c in children[: 32]:
        print(f"  v {c.id} — {c.title}")
    # depends
    for d in node.frontmatter.get("depends_on") or []:
        n2 = nodes.get(d)
        print(f"  <- {d}" + (f" — {n2.title}" if n2 else ""))
    # blocks (reverse depends_on)
    blockers = [n.id for n in nodes.values() if node.id in (n.frontmatter.get("depends_on") or [])]
    for b in blockers:
        n2 = nodes.get(b)
        print(f"  -> {b}" + (f" — {n2.title}" if n2 else ""))
    return 0


def cmd_mvp(args: argparse.Namespace) -> int:
    nodes = load_tree()
    by_epic: Dict[str, List[Node]] = {}
    for n in nodes.values():
        if n.frontmatter.get("release") != "mvp":
            continue
        if n.type == "epic":
            ekey = n.id
        else:
            cur = n
            while cur.frontmatter.get("parent"):
                cur = nodes.get(cur.frontmatter["parent"])
                if cur is None:
                    break
            ekey = cur.id if cur and cur.type == "epic" else "(orphan)"
        by_epic.setdefault(ekey, []).append(n)
    for ekey in sorted(by_epic.keys()):
        epic = nodes.get(ekey)
        title = epic.title if epic else ekey
        print(f"=== {ekey} — {title}")
        items = sorted(by_epic[ekey], key=lambda n: (n.frontmatter.get("order") or 0, n.id))
        for n in items:
            print(f"  [{n.type[0].upper()}] {n.id} — {n.title}")
    return 0


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="req", description="Antirion requirements graph CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("validate", help="run all validators; exits non-zero on failure")
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("index", help="regenerate _index.json and child blocks")
    sp.set_defaults(func=cmd_index)

    sp = sub.add_parser("new", help="create a new node (epic|feature|story)")
    sp.add_argument("kind", choices=["epic", "feature", "story"])
    sp.add_argument("--title", required=True)
    sp.add_argument("--parent")
    sp.add_argument("--release", choices=list(VALID_RELEASES))
    sp.add_argument("--order", type=int)
    sp.set_defaults(func=cmd_new)

    sp = sub.add_parser("mv", help="move a feature or story under a new parent")
    sp.add_argument("id")
    sp.add_argument("--to", required=True, dest="to")
    sp.set_defaults(func=cmd_mv)

    sp = sub.add_parser("rename", help="rename slug + title atomically")
    sp.add_argument("id")
    sp.add_argument("--title", required=True)
    sp.set_defaults(func=cmd_rename)

    sp = sub.add_parser("status", help="shorthand for status.<discipline>=<state>")
    sp.add_argument("id")
    sp.add_argument("assignments", nargs="+")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("update", help="atomic frontmatter edit (dotted keys allowed)")
    sp.add_argument("id")
    sp.add_argument("assignments", nargs="+")
    sp.set_defaults(func=cmd_update)

    sp = sub.add_parser("context", help="print minimal LLM reading set for an id")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_context)

    sp = sub.add_parser("graph", help="print neighborhood of an id (parents/children/deps)")
    sp.add_argument("id")
    sp.add_argument("--depth", type=int, default=3)
    sp.set_defaults(func=cmd_graph)

    sp = sub.add_parser("mvp", help="list release: mvp items by epic")
    sp.set_defaults(func=cmd_mvp)

    sp = sub.add_parser("rebalance", help="re-space order values for a parent's children")
    sp.add_argument("parent", nargs="?", default=None,
                    help="parent id; omit to rebalance the top-level epics")
    sp.add_argument("--step", type=int, default=DEFAULT_ORDER_STEP)
    sp.set_defaults(func=cmd_rebalance)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
