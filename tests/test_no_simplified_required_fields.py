"""No simplified characters in required user-facing fields (繁體中文 only)."""
from __future__ import annotations

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


def _user_facing(data: dict) -> dict:
    out = {
        "task_name": str(data.get("task_name") or ""),
        "prompt.text": str((data.get("prompt") or {}).get("text") or ""),
        "reference_solution": str(data.get("reference_solution") or ""),
        "judge_rubric": str(data.get("judge_rubric") or ""),
    }
    for i, a in enumerate(data.get("expected_actions") or []):
        out[f"expected_actions[{i}]"] = str(a)
    ua = data.get("user_agent") or {}
    for i, s in enumerate(ua.get("sessions", []) or []):
        if isinstance(s, dict):
            out[f"sessions[{i}]"] = str(s.get("prompt") or "")
    return out


class NoSimplifiedClawTests(unittest.TestCase):
    def test_no_simplified_in_task_yaml_user_fields(self) -> None:
        offenders = []
        for d in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            data = yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8"))
            for field, text in _user_facing(data).items():
                simp = lib_zh.find_simplified(text)
                if simp:
                    offenders.append(f"{d.name}:{field}={''.join(simp)}")
        self.assertEqual(offenders, [], f"simplified found: {offenders[:20]}")


class NoSimplifiedMarkdownTests(unittest.TestCase):
    def test_no_simplified_in_zh_markdown_prose(self) -> None:
        # lib_zh.find_simplified strips code fences/URLs, so bilingual grader
        # regex (which may include simplified) is excluded from this scan.
        offenders = []
        for md in sorted(ZH.glob("*.md")):
            simp = lib_zh.find_simplified(md.read_text(encoding="utf-8"))
            if simp:
                offenders.append(f"{md.stem}={''.join(simp)}")
        self.assertEqual(offenders, [], f"simplified found: {offenders[:20]}")


class DetectorSanityTests(unittest.TestCase):
    """Guard against the validator silently always passing."""

    def test_detector_flags_real_simplified(self) -> None:
        self.assertTrue(lib_zh.find_simplified("这个为对时间会说话"))

    def test_detector_ignores_traditional_and_ambiguous(self) -> None:
        self.assertEqual(lib_zh.find_simplified("這個為對時間會說話"), [])
        self.assertEqual(lib_zh.find_simplified("若干關鍵字、公里、台灣、高峰群組"), [])


if __name__ == "__main__":
    unittest.main()
