"""
Validator behavioural tests. Each case constructs a tiny tree under self.tmp,
points the validator at it, and checks for the expected error or clean pass.

Compatible with both `pytest` and stdlib `unittest`. CI uses pytest; the bare
`python -m unittest` form works as a fallback for local environments without
pytest installed.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Load tools/req/req.py as a standalone module regardless of pytest's import
# mode. We can't `import req` directly because the parent package
# `tools/req/__init__.py` would shadow `tools/req/req.py` under pytest's
# package-aware collection mode (you'd get the package's empty __init__.py).
_REQ_PATH = Path(__file__).resolve().parents[1] / "req.py"
_spec = importlib.util.spec_from_file_location("_req_under_test", _REQ_PATH)
assert _spec and _spec.loader, f"failed to load {_REQ_PATH}"
req_mod = importlib.util.module_from_spec(_spec)
sys.modules["_req_under_test"] = req_mod
_spec.loader.exec_module(req_mod)

FIXTURES = Path(__file__).parent / "fixtures"


class _Patcher:
    """Save & restore module-level paths so tests can point at a temp tree."""

    def __init__(self, root: Path) -> None:
        self._saved = {
            "REQ_ROOT": req_mod.REQ_ROOT,
            "SCHEMA_PATH": req_mod.SCHEMA_PATH,
            "INDEX_PATH": req_mod.INDEX_PATH,
            "REPO_ROOT": req_mod.REPO_ROOT,
        }
        req_mod.REQ_ROOT = root
        req_mod.SCHEMA_PATH = root / "_schema.json"
        req_mod.INDEX_PATH = root / "_index.json"
        req_mod.REPO_ROOT = root.parent

    def restore(self) -> None:
        for k, v in self._saved.items():
            setattr(req_mod, k, v)


def _refresh_index(root: Path) -> None:
    nodes = req_mod.load_tree(root)
    idx = req_mod.build_index(nodes)
    (root / "_index.json").write_text(
        json.dumps(idx, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="req_test_")
        self.tmp = Path(self._tmp)
        self.root = self.tmp / "requirements"
        shutil.copytree(FIXTURES / "minitree", self.root)
        self.patch = _Patcher(self.root)

    def tearDown(self) -> None:
        self.patch.restore()
        shutil.rmtree(self._tmp, ignore_errors=True)

    # 1. Valid tree --------------------------------------------------------
    def test_valid_tree_passes(self) -> None:
        _refresh_index(self.root)
        v = req_mod.Validator()
        rc = v.run()
        self.assertEqual(rc, 0, msg="errors:\n" + "\n".join(v.errors))

    # 2. Broken cross-ref --------------------------------------------------
    def test_broken_cross_ref(self) -> None:
        target = self.root / "gw_epic_00001_sample" / "gw_feature_00001_alpha" / "FEATURE.md"
        text = target.read_text(encoding="utf-8")
        target.write_text(
            text.replace("tags: []\n", "tags: []\ndepends_on:\n- gw_feature_99999\n"),
            encoding="utf-8",
        )
        _refresh_index(self.root)
        v = req_mod.Validator()
        self.assertNotEqual(v.run(), 0)
        self.assertTrue(any("unknown id 'gw_feature_99999'" in e for e in v.errors), v.errors)

    # 3. Folder/id mismatch ------------------------------------------------
    def test_folder_id_mismatch(self) -> None:
        src = self.root / "gw_epic_00001_sample" / "gw_feature_00001_alpha"
        dst = self.root / "gw_epic_00001_sample" / "gw_feature_00009_alpha"
        src.rename(dst)
        _refresh_index(self.root)
        v = req_mod.Validator()
        self.assertNotEqual(v.run(), 0)
        self.assertTrue(any("folder id" in e for e in v.errors), v.errors)

    # 4. Missing required heading -----------------------------------------
    def test_missing_required_heading(self) -> None:
        target = (
            self.root
            / "gw_epic_00001_sample"
            / "gw_feature_00001_alpha"
            / "gw_story_00001_first"
            / "STORY.md"
        )
        text = target.read_text(encoding="utf-8")
        target.write_text(text.replace("## Open Questions\n", ""), encoding="utf-8")
        _refresh_index(self.root)
        v = req_mod.Validator()
        self.assertNotEqual(v.run(), 0)
        self.assertTrue(any("missing required heading" in e for e in v.errors), v.errors)

    # 5. depends_on cycle --------------------------------------------------
    def test_depends_on_cycle(self) -> None:
        a = self.root / "gw_epic_00001_sample" / "gw_feature_00001_alpha" / "gw_story_00001_first" / "STORY.md"
        b = self.root / "gw_epic_00001_sample" / "gw_feature_00001_alpha" / "gw_story_00002_second" / "STORY.md"
        a.write_text(
            a.read_text(encoding="utf-8").replace(
                "tags: []\n", "tags: []\ndepends_on:\n- gw_story_00002\n"
            ),
            encoding="utf-8",
        )
        b.write_text(
            b.read_text(encoding="utf-8").replace(
                "tags: []\n", "tags: []\ndepends_on:\n- gw_story_00001\n"
            ),
            encoding="utf-8",
        )
        _refresh_index(self.root)
        v = req_mod.Validator()
        self.assertNotEqual(v.run(), 0)
        self.assertTrue(any("cycle" in e for e in v.errors), v.errors)

    # 6. Index freshness ---------------------------------------------------
    def test_index_stale_detected(self) -> None:
        _refresh_index(self.root)
        target = self.root / "gw_epic_00001_sample" / "gw_feature_00001_alpha" / "FEATURE.md"
        target.write_text(
            target.read_text(encoding="utf-8").replace(
                "title: Alpha feature", "title: Alpha feature edited"
            ),
            encoding="utf-8",
        )
        v = req_mod.Validator()
        self.assertNotEqual(v.run(), 0)
        self.assertTrue(any("stale" in e for e in v.errors), v.errors)


if __name__ == "__main__":
    unittest.main()
