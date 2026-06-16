"""Offline TW runner smoke test (no OpenClaw / model / network)."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import smoke_tw_runner_load as S


class TwRunnerSmokeOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = S.check()

    def test_resolution(self):
        self.assertEqual(self.out["resolve"]["tw"], "tasks_tw")
        self.assertEqual(self.out["resolve"]["region_TW"], "tasks_tw")
        self.assertEqual(self.out["resolve"]["en"], "tasks")

    def test_counts_match(self):
        self.assertEqual(self.out["counts"]["tw"], self.out["counts"]["en"])
        self.assertGreaterEqual(self.out["counts"]["tw"], 147)

    def test_manifest_full(self):
        self.assertEqual(self.out["manifest_missing"], [])

    def test_passk(self):
        self.assertEqual(self.out["passk"]["pass_at_k_rate"], 1.0)
        self.assertEqual(self.out["passk"]["pass_k_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
