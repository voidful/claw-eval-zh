"""All TW graders import with a callable grade()."""
import importlib.util, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
CLAW = ROOT / "tasks_claw_eval_tw"


class TwGraderImports(unittest.TestCase):
    def test_all_import(self):
        n = 0
        for d in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            spec = importlib.util.spec_from_file_location(f"twg_{d.name}", d / "grader.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertTrue(callable(getattr(m, "grade", None)), d.name)
            n += 1
        self.assertGreaterEqual(n, 147)


if __name__ == "__main__":
    unittest.main()
