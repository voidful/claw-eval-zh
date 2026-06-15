"""tasks_zh covers the full manifest and loads as Traditional Chinese."""
from __future__ import annotations

import logging
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

logging.disable(logging.CRITICAL)
from lib_tasks import TaskLoader  # noqa: E402

TASKS = ROOT / "tasks"
TASKS_ZH = ROOT / "tasks_zh"


def has_chinese(text: str) -> bool:
    return any("一" <= ch <= "鿿" for ch in text)


def _manifest_ids(path: Path) -> set:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    ids = set(data.get("run_first", []) or [])
    for arr in (data.get("categories", {}) or {}).values():
        ids.update(arr or [])
    return ids


class FullCoverageTests(unittest.TestCase):
    def test_zh_covers_full_manifest(self) -> None:
        en_ids = _manifest_ids(TASKS / "manifest.yaml")
        zh_files = {p.stem for p in TASKS_ZH.glob("*.md")}
        missing = en_ids - zh_files
        self.assertEqual(missing, set(), f"tasks_zh missing: {sorted(missing)}")
        self.assertEqual(len(zh_files), len(en_ids))

    def test_zh_manifest_preserves_ordering_keys(self) -> None:
        en = yaml.safe_load((TASKS / "manifest.yaml").read_text(encoding="utf-8"))
        zh = yaml.safe_load((TASKS_ZH / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(zh.get("run_first"), en.get("run_first"))
        self.assertEqual(list(zh.get("categories", {}).keys()),
                         list(en.get("categories", {}).keys()))
        # category membership identical (full coverage)
        for cat, ids in en["categories"].items():
            self.assertEqual(zh["categories"][cat], ids)


class ZhTaskLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = TaskLoader(TASKS_ZH).load_all_tasks()
        cls.by_id = {t.task_id: t for t in cls.tasks}

    def test_loads_all(self) -> None:
        self.assertEqual(len(self.tasks), len(list(TASKS_ZH.glob("*.md"))))
        self.assertIn("task_sanity", self.by_id)

    def test_sample_prompts_are_chinese(self) -> None:
        sample = [
            "task_sanity", "task_weather", "task_csv_stock_trend",
            "task_blog", "task_calendar", "task_log_apache_top_errors",
            "task_meeting_tldr", "task_summary", "task_files", "task_stock",
        ]
        for tid in sample:
            self.assertIn(tid, self.by_id, tid)
            self.assertTrue(has_chinese(self.by_id[tid].prompt), f"{tid} prompt not Chinese")

    def test_frontmatter_locale(self) -> None:
        for tid in ("task_sanity", "task_weather"):
            t = self.by_id[tid]
            self.assertEqual(t.frontmatter.get("language"), "zh")
            self.assertEqual(t.frontmatter.get("locale"), "zh-TW")
            self.assertEqual(t.frontmatter.get("source_benchmark"), "pinchbench")


if __name__ == "__main__":
    unittest.main()
