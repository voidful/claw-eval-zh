"""tasks_tw covers the full original manifest."""
import unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"
TW = ROOT / "tasks_tw"


def manifest_ids(p):
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    ids = set(d.get("run_first", []) or [])
    for arr in (d.get("categories", {}) or {}).values():
        ids.update(arr or [])
    return ids


class TwManifestCoverage(unittest.TestCase):
    def test_full_coverage(self):
        en = manifest_ids(TASKS / "manifest.yaml")
        have = {p.stem for p in TW.glob("*.md")}
        self.assertEqual(en - have, set(), f"missing: {sorted(en-have)}")
        self.assertEqual(len(have), len(en))

    def test_manifest_preserves_structure(self):
        en = yaml.safe_load((TASKS / "manifest.yaml").read_text(encoding="utf-8"))
        tw = yaml.safe_load((TW / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(tw.get("run_first"), en.get("run_first"))
        self.assertEqual(list(tw.get("categories", {})), list(en.get("categories", {})))


if __name__ == "__main__":
    unittest.main()
