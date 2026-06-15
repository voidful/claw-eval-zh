"""Pass@k / Pass^k (Pass^3) metric tests."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib_passk import (  # noqa: E402
    aggregate_passk,
    compute_task_passk,
    pass_at_k,
    pass_hat_k,
    run_passes,
)


class RunPassTests(unittest.TestCase):
    def test_conditions(self) -> None:
        self.assertTrue(run_passes(0.8, "success", False, 0.8))
        self.assertFalse(run_passes(0.79, "success", False, 0.8))
        self.assertFalse(run_passes(0.99, "success", True, 0.8))   # timed out
        self.assertFalse(run_passes(0.99, "error", False, 0.8))    # not success


class Pass3Tests(unittest.TestCase):
    def _trials(self, *scores, status="success", timed_out=False):
        return [{"score": s, "status": status, "timed_out": timed_out} for s in scores]

    def test_pass3_all_three_pass(self) -> None:
        r = compute_task_passk(self._trials(0.9, 0.85, 0.95), 0.8)
        self.assertTrue(r["pass_at_k"])
        self.assertTrue(r["pass_k"])      # pass^3 == True (all 3 pass)
        self.assertEqual(r["k"], 3)

    def test_pass3_one_fails(self) -> None:
        r = compute_task_passk(self._trials(0.9, 0.4, 0.95), 0.8)
        self.assertTrue(r["pass_at_k"])   # pass@3 True (>=1)
        self.assertFalse(r["pass_k"])     # pass^3 False (not all)

    def test_pass3_timeout_breaks_consistency(self) -> None:
        trials = self._trials(0.9, 0.9) + [{"score": 0.99, "status": "timeout", "timed_out": True}]
        r = compute_task_passk(trials, 0.8)
        self.assertTrue(r["pass_at_k"])
        self.assertFalse(r["pass_k"])

    def test_pass_at_k_and_hat_k_helpers(self) -> None:
        self.assertTrue(pass_at_k([False, True, False]))
        self.assertFalse(pass_at_k([False, False, False]))
        self.assertTrue(pass_hat_k([True, True, True]))
        self.assertFalse(pass_hat_k([True, True, False]))


class AggregateTests(unittest.TestCase):
    def test_rates_and_categories(self) -> None:
        per_task = {
            "a": {"category": "coding",
                  "trials": [{"score": 0.9, "status": "success", "timed_out": False}] * 3},
            "b": {"category": "coding",
                  "trials": [{"score": 0.9, "status": "success", "timed_out": False},
                             {"score": 0.2, "status": "success", "timed_out": False},
                             {"score": 0.9, "status": "success", "timed_out": False}]},
        }
        agg = aggregate_passk(per_task, 0.8)
        self.assertEqual(agg["pass_at_k_rate"], 1.0)   # both pass@3
        self.assertEqual(agg["pass_k_rate"], 0.5)      # only "a" passes^3
        self.assertEqual(agg["per_category"]["coding"]["per_category_pass_k"], 0.5)
        self.assertIn("per_category_average_score", agg["per_category"]["coding"])


if __name__ == "__main__":
    unittest.main()
