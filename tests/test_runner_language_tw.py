"""Runner selects the correct tasks dir for en/zh/tw and --region TW."""
import argparse
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import benchmark as B


class RunnerLanguageTw(unittest.TestCase):
    def _resolve(self, language="en", region=None, tasks_dir=None):
        ns = argparse.Namespace(language=language, region=region, tasks_dir=tasks_dir)
        return B._resolve_tasks_dir(ns, ROOT)

    def test_default_en(self):
        self.assertEqual(self._resolve("en"), ROOT / "tasks")

    def test_zh(self):
        self.assertEqual(self._resolve("zh"), ROOT / "tasks_zh")

    def test_tw(self):
        self.assertEqual(self._resolve("tw"), ROOT / "tasks_tw")

    def test_region_tw_alias(self):
        self.assertEqual(self._resolve("en", region="TW"), ROOT / "tasks_tw")

    def test_tasks_dir_override(self):
        self.assertEqual(self._resolve("tw", tasks_dir="/custom"), Path("/custom"))


if __name__ == "__main__":
    unittest.main()
