"""Official-schema export candidate generates and self-validates (offline)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import export_official_claw_eval_candidate as E
import yaml


class OfficialExportCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "cand"
        cls.rc = E.main(["--validate", "--out", str(cls.out)])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_validate_passes(self):
        self.assertEqual(self.rc, 0)

    def test_manifest_and_count(self):
        man = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(man["official_compatible"])
        self.assertGreaterEqual(man["task_count"], 143)

    def test_entrypoint_relocated(self):
        d = yaml.safe_load((self.out / "tasks" / "T053tw_csv_stock_trend" / "task.yaml").read_text(encoding="utf-8"))
        for c in d["scoring_components"]:
            self.assertNotIn("entrypoint", c.get("check", {}))
        self.assertEqual(d["metadata"].get("grader_entrypoint"), "grader.py")
        self.assertEqual(d["prompt"]["language"], "zh")
        self.assertEqual(d["metadata"]["locale"], "zh-TW")

    def test_grader_copied(self):
        self.assertTrue((self.out / "tasks" / "T053tw_csv_stock_trend" / "grader.py").exists())


if __name__ == "__main__":
    unittest.main()
