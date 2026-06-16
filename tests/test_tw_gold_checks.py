"""Gold calibration: deterministic TW graders score gold cases within bounds.

CI-safe: no LLM, no network. Reuses run_tw_gold_checks.run().
"""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_tw_gold_checks as G


class TwGoldChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ok, cls.results = G.run()

    def test_overall_pass(self):
        failed = [f"{r['task_id']}/{c}" for r in self.results if r["type"] == "deterministic"
                  for c, cc in r["cases"].items() if not cc["passed"]]
        self.assertTrue(self.ok, f"gold check failures: {failed}")

    def test_at_least_10_gold_tasks(self):
        self.assertGreaterEqual(len(self.results), 10)

    def test_each_task_has_pass_and_fail(self):
        for r in self.results:
            if r["type"] != "deterministic":
                continue
            self.assertIn("pass", r["cases"], r["task_id"])
            self.assertIn("fail", r["cases"], r["task_id"])

    def test_pass_beats_fail(self):
        for r in self.results:
            if r["type"] != "deterministic":
                continue
            self.assertGreater(r["cases"]["pass"]["mean"], r["cases"]["fail"]["mean"], r["task_id"])


if __name__ == "__main__":
    unittest.main()
