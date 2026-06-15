"""TW task.yaml schema validation."""
import re, unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
CLAW = ROOT / "tasks_claw_eval_tw"
RE = re.compile(r"^T\d{3}tw_[a-z0-9_]+$")
REQ = ["task_id", "task_name", "version", "category", "difficulty", "tags", "source",
       "prompt", "tools", "tool_endpoints", "services", "fixtures", "environment",
       "scoring_components", "safety_checks", "expected_actions", "user_agent",
       "judge_rubric", "reference_solution", "primary_dimensions", "metadata"]


def dirs():
    return sorted(p for p in CLAW.iterdir() if p.is_dir())


class TwSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {d.name: yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8")) for d in dirs()}

    def test_count(self):
        self.assertGreaterEqual(len(self.data), 147)

    def test_required_fields(self):
        for n, d in self.data.items():
            for f in REQ:
                self.assertIn(f, d, f"{n} missing {f}")

    def test_id_locale_region_tz(self):
        for n, d in self.data.items():
            self.assertEqual(d["task_id"], n)
            self.assertRegex(d["task_id"], RE)
            self.assertEqual(d["prompt"]["language"], "zh")
            self.assertEqual(d["metadata"]["locale"], "zh-TW")
            self.assertEqual(d["metadata"]["region"], "TW")
            self.assertEqual(d["environment"]["timezone"], "Asia/Taipei")
            self.assertIn(d["difficulty"], {"easy", "medium", "hard"})
            self.assertIn("completion", d["primary_dimensions"])
            self.assertEqual(d["version"], "0.3.0")

    def test_python_entrypoint(self):
        for n, d in self.data.items():
            for c in d["scoring_components"]:
                if c["check"].get("type") == "python":
                    self.assertEqual(c["check"].get("entrypoint"), "grader.py", n)

    def test_fixtures_exist(self):
        for n, d in self.data.items():
            for fx in d.get("fixtures") or []:
                self.assertTrue((ROOT / "assets" / fx["source"]).exists(), f"{n}: {fx['source']}")


if __name__ == "__main__":
    unittest.main()
