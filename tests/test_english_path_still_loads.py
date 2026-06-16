"""The original English PinchBench path must remain intact."""
from __future__ import annotations

import logging
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

logging.disable(logging.CRITICAL)
from lib_tasks import TaskLoader  # noqa: E402
import benchmark as B  # noqa: E402

TASKS_EN = ROOT / "tasks"


class EnglishPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = TaskLoader(TASKS_EN).load_all_tasks()
        cls.by_id = {t.task_id: t for t in cls.tasks}

    def test_english_tasks_load(self) -> None:
        self.assertGreaterEqual(len(self.tasks), 143)
        self.assertIn("task_sanity", self.by_id)

    def test_english_prompt_is_not_translated(self) -> None:
        # The English source must still be English (untouched).
        sanity = self.by_id["task_sanity"]
        self.assertIn("Hello", sanity.prompt)
        self.assertFalse(any("一" <= c <= "鿿" for c in sanity.prompt))

    def test_resolve_tasks_dir_defaults_to_english(self) -> None:
        import argparse
        ns = argparse.Namespace(tasks_dir=None, language="en")
        self.assertEqual(B._resolve_tasks_dir(ns, ROOT), TASKS_EN)
        ns_zh = argparse.Namespace(tasks_dir=None, language="zh")
        self.assertEqual(B._resolve_tasks_dir(ns_zh, ROOT), ROOT / "tasks_zh")

    def test_weather_grader_still_runs_on_english(self) -> None:
        # The original automated check still grades an English workspace.
        import tempfile
        from lib_grading import grade_task
        w = self.by_id["task_weather"]
        with tempfile.TemporaryDirectory() as d:
            Path(d, "weather.py").write_text(
                "import requests\n"
                "def main():\n"
                "    try:\n"
                "        print(requests.get('https://wttr.in/San_Francisco').text)\n"
                "    except Exception as e:\n"
                "        print(e)\n",
                encoding="utf-8")
            result = grade_task(
                task=w,
                execution_result={"status": "success", "transcript": [], "workspace": d},
                skill_dir=ROOT,
            )
        self.assertGreater(result.score, 0.5)


if __name__ == "__main__":
    unittest.main()
