"""Deeply-localized TW tasks should not retain US context in the prompt.

Anchor tasks (weather, calendar) and fixture_replace tasks must be Taiwan-based.
Other tasks may legitimately keep a fixed US asset; those are reported (warnings)
by the validator, not asserted here.
"""
import json
import unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
CLAW = ROOT / "tasks_claw_eval_tw"
MAP = json.loads((ROOT / "reports" / "tw_localization_map.json").read_text(encoding="utf-8"))
STRAT = {r["task_id"]: r for r in MAP["items"]}
US = ["san francisco", "new york", "u.s. steel", "apple stock", "nasdaq"]


def yaml_for(orig_task_id):
    for d in CLAW.iterdir():
        if d.is_dir():
            data = yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8"))
            if data["source"]["original_task_id"] == orig_task_id:
                return data
    return None


class TwUsResidue(unittest.TestCase):
    def test_anchor_and_fixture_tasks_have_no_us_residue(self):
        must_be_tw = ["task_weather", "task_calendar", "task_csv_stock_trend",
                      "task_csv_stock_volatility", "task_csv_stock_best_worst",
                      "task_financial_ratio_calculation"]
        bad = []
        for tid in must_be_tw:
            d = yaml_for(tid)
            self.assertIsNotNone(d, tid)
            pl = d["prompt"]["text"].lower()
            hits = [m for m in US if m in pl]
            if hits:
                bad.append(f"{tid}:{hits}")
        self.assertEqual(bad, [], f"US residue in must-be-TW tasks: {bad}")


if __name__ == "__main__":
    unittest.main()
