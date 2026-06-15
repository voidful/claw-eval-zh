"""Full schema validation across all tasks_claw_eval_zh folders."""
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

import validate_claw_eval_zh_tasks as V  # noqa: E402

CLAW = ROOT / "tasks_claw_eval_zh"
ZH = ROOT / "tasks_zh"
TASK_ID_RE = re.compile(r"^P\d{3}zh_[a-z0-9_]+$")
REQUIRED = [
    "task_id", "task_name", "version", "category", "difficulty", "tags",
    "source", "prompt", "tools", "tool_endpoints", "services", "fixtures",
    "environment", "scoring_components", "safety_checks", "expected_actions",
    "user_agent", "judge_rubric", "reference_solution", "primary_dimensions",
    "metadata",
]
DIFFICULTIES = {"easy", "medium", "hard"}


def _dirs():
    return sorted(p for p in CLAW.iterdir() if p.is_dir())


class ValidatorTests(unittest.TestCase):
    def test_validator_no_errors(self) -> None:
        rep, _ = V.run(CLAW, ZH)
        self.assertEqual(rep.errors, [], "validator errors:\n" + "\n".join(rep.errors))

    def test_validator_actually_detects_errors(self) -> None:
        # Guard: the validator must FAIL on a deliberately broken task.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "P999zh_bad"
            bad.mkdir()
            (bad / "task.yaml").write_text(
                "task_id: P999zh_bad\nprompt:\n  text: '这是简体 placeholder TODO(zh)'\n"
                "  language: en\nmetadata:\n  locale: zh-CN\n  grading_type: hybrid\n"
                "difficulty: trivial\ncategory: ''\nprimary_dimensions: []\n"
                "scoring_components: []\njudge_rubric: ''\n",
                encoding="utf-8",
            )
            rep, _ = V.run(Path(d), Path(d) / "nope")
            self.assertTrue(len(rep.errors) > 0, "validator should flag the broken task")


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = {d.name: yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8"))
                    for d in _dirs()}

    def test_count_is_full(self) -> None:
        self.assertEqual(len(self.data), len(list(ZH.glob("*.md"))))
        self.assertGreaterEqual(len(self.data), 147)

    def test_required_fields(self) -> None:
        for name, data in self.data.items():
            for f in REQUIRED:
                self.assertIn(f, data, f"{name} missing {f}")

    def test_id_and_locale(self) -> None:
        for name, data in self.data.items():
            self.assertEqual(data["task_id"], name)
            self.assertRegex(data["task_id"], TASK_ID_RE)
            self.assertEqual(data["prompt"]["language"], "zh")
            self.assertEqual(data["metadata"]["locale"], "zh-TW")
            self.assertIn(data["difficulty"], DIFFICULTIES)
            self.assertIn("completion", data["primary_dimensions"])

    def test_scoring_matches_grading_type(self) -> None:
        for name, data in self.data.items():
            gt = data["metadata"]["grading_type"]
            names = {c["name"] for c in data["scoring_components"]}
            if gt == "automated":
                self.assertIn("automated", names, name)
            elif gt == "llm_judge":
                self.assertIn("llm_judge", names, name)
            elif gt == "hybrid":
                self.assertEqual(names, {"automated", "llm_judge"}, name)

    def test_python_components_have_entrypoint(self) -> None:
        for name, data in self.data.items():
            for c in data["scoring_components"]:
                if c["check"].get("type") == "python":
                    self.assertEqual(c["check"].get("entrypoint"), "grader.py", name)

    def test_fixtures_exist_and_dest_not_translated(self) -> None:
        for name, data in self.data.items():
            for fx in data.get("fixtures") or []:
                self.assertTrue((ROOT / "assets" / fx["source"]).exists(),
                                f"{name}: missing assets/{fx['source']}")
                self.assertFalse(any("一" <= c <= "鿿" for c in fx["dest"]), name)


if __name__ == "__main__":
    unittest.main()
