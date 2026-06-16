"""Every task is in the localization map with a strategy."""
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import yaml
MAP = ROOT / "reports" / "tw_localization_map.json"
VALID = {"copy", "language_polish", "context_replace", "fixture_replace",
         "new_tw_variant", "manual_review_only"}


class TwMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MAP.read_text(encoding="utf-8"))
        cls.items = {r["task_id"]: r for r in cls.m["items"]}

    def test_count(self):
        self.assertEqual(self.m["total_tasks"], 143)
        self.assertEqual(len(self.items), 143)

    def test_every_entry_has_strategy(self):
        for tid, r in self.items.items():
            self.assertIn(r.get("localization_strategy"), VALID, tid)
            self.assertIn("manual_review", r)
            self.assertIn("risk", r)

    def test_every_manifest_task_in_map(self):
        man = yaml.safe_load((ROOT / "tasks" / "manifest.yaml").read_text(encoding="utf-8"))
        ids = set(man.get("run_first", []) or [])
        for arr in (man.get("categories", {}) or {}).values():
            ids.update(arr or [])
        self.assertEqual(ids - set(self.items), set())


if __name__ == "__main__":
    unittest.main()
