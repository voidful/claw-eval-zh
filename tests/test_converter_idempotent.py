"""The converter is deterministic / idempotent."""
from __future__ import annotations

import logging
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

logging.disable(logging.CRITICAL)
import convert_pinchbench_to_claw_eval_zh as C  # noqa: E402

TASKS = "task_sanity,task_weather,task_csv_stock_trend,task_calendar"


def _convert(tmp: Path):
    return C.convert([
        "--write", "--overwrite", "--tasks", TASKS,
        "--out-zh", str(tmp / "tasks_zh"),
        "--out-claw", str(tmp / "tasks_claw_eval_zh"),
        "--coverage-out", str(tmp / "reports" / "coverage.json"),
        "--manual-review-out", str(tmp / "reports" / "manual.json"),
    ])


def _snapshot(tmp: Path) -> dict:
    out = {}
    for p in sorted(tmp.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(tmp))] = p.read_text(encoding="utf-8")
    return out


class IdempotentTests(unittest.TestCase):
    def test_two_runs_identical(self) -> None:
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            _convert(Path(d1))
            _convert(Path(d2))
            s1, s2 = _snapshot(Path(d1)), _snapshot(Path(d2))
            self.assertEqual(set(s1), set(s2), "file sets differ")
            diffs = [k for k in s1 if s1[k] != s2[k]]
            self.assertEqual(diffs, [], f"non-deterministic files: {diffs}")

    def test_rewrite_same_dir_no_change(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _convert(tmp)
            before = _snapshot(tmp)
            _convert(tmp)  # second run over the same dir
            after = _snapshot(tmp)
            diffs = [k for k in before if before.get(k) != after.get(k)]
            self.assertEqual(diffs, [], f"rewrite changed files: {diffs}")

    def test_id_mapping_stable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            summary = _convert(Path(d))
            self.assertEqual(summary["id_map"]["task_sanity"], "P001zh_sanity")
            self.assertTrue(summary["id_map"]["task_weather"].endswith("zh_weather"))


if __name__ == "__main__":
    unittest.main()
