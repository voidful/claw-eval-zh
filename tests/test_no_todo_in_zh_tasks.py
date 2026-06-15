"""No TODO / placeholder markers in required fields of complete tasks."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lib_zh  # noqa: E402

CLAW = ROOT / "tasks_claw_eval_zh"
ZH = ROOT / "tasks_zh"

# Placeholder markers (bare "TODO" excluded; task_todo_list_cleanup is a real task).
TODO_RE = re.compile(
    r"TODO\(zh\)|\bTBD\b|\bTRANSLATE\b|\bPLACEHOLDER\b|待翻譯|待翻译|待補|待补|\bFIXME\b",
    re.IGNORECASE,
)


class NoTodoTests(unittest.TestCase):
    def test_no_todo_in_task_yaml(self) -> None:
        offenders = []
        for d in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            data = yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8"))
            fields = {
                "task_name": data.get("task_name") or "",
                "prompt.text": (data.get("prompt") or {}).get("text") or "",
                "reference_solution": data.get("reference_solution") or "",
                "judge_rubric": data.get("judge_rubric") or "",
            }
            for field, text in fields.items():
                if TODO_RE.search(str(text)):
                    offenders.append(f"{d.name}:{field}")
        self.assertEqual(offenders, [], f"TODO markers found: {offenders}")

    def test_no_todo_in_zh_markdown(self) -> None:
        offenders = []
        for md in sorted(ZH.glob("*.md")):
            prose = lib_zh.strip_noncjk_spans(md.read_text(encoding="utf-8"))
            if TODO_RE.search(prose):
                offenders.append(md.stem)
        self.assertEqual(offenders, [], f"TODO markers found: {offenders}")

    def test_all_tasks_marked_complete(self) -> None:
        scaffolds = []
        for d in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            data = yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8"))
            if (data.get("metadata") or {}).get("translation_status") != "complete":
                scaffolds.append(d.name)
        self.assertEqual(scaffolds, [], f"non-complete tasks: {scaffolds}")


if __name__ == "__main__":
    unittest.main()
