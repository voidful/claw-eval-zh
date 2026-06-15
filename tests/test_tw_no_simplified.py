"""No simplified characters in TW user-facing fields."""
import sys, unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lib_zh
CLAW = ROOT / "tasks_claw_eval_tw"; TW = ROOT / "tasks_tw"


def user_fields(d):
    out = [str(d.get("task_name") or ""), str((d.get("prompt") or {}).get("text") or ""),
           str(d.get("reference_solution") or ""), str(d.get("judge_rubric") or "")]
    out += [str(x) for x in (d.get("expected_actions") or [])]
    out += [str(x) for x in (d.get("safety_checks") or [])]
    for s in (d.get("user_agent") or {}).get("sessions", []) or []:
        if isinstance(s, dict):
            out.append(str(s.get("prompt") or ""))
    return "\n".join(out)


class TwNoSimplified(unittest.TestCase):
    def test_task_yaml(self):
        bad = []
        for dd in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            d = yaml.safe_load((dd / "task.yaml").read_text(encoding="utf-8"))
            s = lib_zh.find_simplified(user_fields(d))
            if s:
                bad.append(f"{dd.name}:{''.join(s)}")
        self.assertEqual(bad, [], f"simplified: {bad[:15]}")

    def test_markdown(self):
        bad = []
        for md in sorted(TW.glob("*.md")):
            s = lib_zh.find_simplified(md.read_text(encoding="utf-8"))
            if s:
                bad.append(f"{md.stem}:{''.join(s)}")
        self.assertEqual(bad, [], f"simplified: {bad[:15]}")

    def test_detector_not_trivial(self):
        self.assertTrue(lib_zh.find_simplified("这个为对时"))
        self.assertEqual(lib_zh.find_simplified("這個為對時、台灣、台積電"), [])


if __name__ == "__main__":
    unittest.main()
