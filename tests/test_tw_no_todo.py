"""No TODO/placeholder in TW required fields."""
import re, unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
CLAW = ROOT / "tasks_claw_eval_tw"
TODO = re.compile(r"TODO\(zh\)|TODO\(tw\)|\bTBD\b|\bTRANSLATE\b|\bPLACEHOLDER\b|待翻譯|待翻译|待補|待补", re.I)


class TwNoTodo(unittest.TestCase):
    def test_no_todo(self):
        bad = []
        for dd in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            d = yaml.safe_load((dd / "task.yaml").read_text(encoding="utf-8"))
            for f in ["task_name", "reference_solution", "judge_rubric"]:
                if TODO.search(str(d.get(f) or "")):
                    bad.append(f"{dd.name}:{f}")
            if TODO.search(str((d.get("prompt") or {}).get("text") or "")):
                bad.append(f"{dd.name}:prompt")
        self.assertEqual(bad, [], f"TODO: {bad}")

    def test_all_complete(self):
        for dd in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            d = yaml.safe_load((dd / "task.yaml").read_text(encoding="utf-8"))
            self.assertEqual((d.get("metadata") or {}).get("translation_status"), "complete", dd.name)


if __name__ == "__main__":
    unittest.main()
