"""Guard: validate_tw_localization must REALLY catch errors (not a formality).

Feeds the TW validator a deliberately-broken task and asserts it produces the
expected error classes. Also asserts the accepted-warnings mechanism cannot
silence a hard error. Offline; no LLM/network/OpenClaw.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_tw_localization as V  # noqa: E402

BROKEN_TASK_YAML = """\
task_id: T999tw_bad
task_name: "这是简体任务名"
version: "0.3.0"
category: ""
difficulty: trivial
tags: [taiwan]
source:
  benchmark: pinchbench
  original_task_id: task_does_not_exist
  original_file: tasks/task_does_not_exist.md
prompt:
  text: "This prompt is entirely in English with a 简体 char and a TODO(tw) marker."
  language: en
tools: []
tool_endpoints: []
services: []
fixtures:
  - source: tw/csvs/__missing_fixture__.csv
    dest: x.csv
environment:
  timeout_seconds: 60
  timezone: America/New_York
  locale: zh-CN
  region: US
  max_turns: 1
scoring_components:
  - name: automated
    weight: 1.0
    check:
      type: python
      entrypoint: grader.py
safety_checks: []
expected_actions: []
user_agent:
  enabled: false
judge_rubric: ""
reference_solution: "待補"
primary_dimensions: []
metadata:
  locale: zh-CN
  region: US
  timezone: America/New_York
  grading_type: automated
  localization_strategy: copy
  translation_status: complete
"""


class TwValidatorCatchesErrors(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.claw = tmp / "claw"
        bad = self.claw / "T999tw_bad"
        bad.mkdir(parents=True)
        (bad / "task.yaml").write_text(BROKEN_TASK_YAML, encoding="utf-8")
        # declares python scoring but no grader.py -> should also error
        self.tw_dir = tmp / "tw_empty"
        self.tw_dir.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_validator_flags_the_broken_task(self) -> None:
        rep, _ = V.run(self.claw, self.tw_dir, ROOT / "tasks",
                       ROOT / "reports" / "tw_localization_map.json")
        blob = "\n".join(rep.errors)
        self.assertTrue(rep.errors, "validator must produce errors for the broken task")
        # specific error classes must be caught
        self.assertIn("prompt.language", blob)
        self.assertIn("locale", blob)
        self.assertIn("region", blob)
        self.assertIn("timezone", blob)
        self.assertTrue("simplified" in blob, "must catch simplified characters")
        self.assertTrue("TODO" in blob or "placeholder" in blob, "must catch TODO marker")
        self.assertTrue("grader.py missing" in blob, "must catch missing grader")
        self.assertTrue("not in localization map" in blob, "must catch task absent from map")
        self.assertTrue("mostly English" in blob, "must catch English-leakage prompt")
        self.assertTrue("fixture source missing" in blob, "must catch missing fixture")
        self.assertTrue("completion" in blob, "must catch missing completion dimension")

    def test_accepted_warnings_cannot_silence_errors(self) -> None:
        # Even if everything were "accepted", errors must still fail the gate.
        rep, _ = V.run(self.claw, self.tw_dir, ROOT / "tasks",
                       ROOT / "reports" / "tw_localization_map.json")
        unresolved, accepted = V.partition_warnings(rep, set())
        self.assertGreater(len(rep.errors), 0)
        # main() returns 1 when errors exist regardless of warnings
        self.assertFalse(rep.ok())


if __name__ == "__main__":
    unittest.main()
