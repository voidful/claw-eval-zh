"""Offline tests for scripts/preflight_env.py (no openclaw/fws/model needed)."""
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import preflight_env as pf  # noqa: E402
from lib_fws import is_fws_task  # noqa: E402


class TestRequirements(unittest.TestCase):
    def _task(self, tid):
        return {t.task_id: t for t in pf.load_tasks("tw")}[tid]

    def test_gh_triage_requires_fws_and_gh(self):
        req = pf.task_requirements(self._task("task_gh_issue_triage"))
        self.assertIn("fws", req["bins"])
        self.assertIn("gh", req["bins"])

    def test_pure_file_task_has_no_extra_reqs(self):
        req = pf.task_requirements(self._task("task_files"))
        self.assertEqual(req["bins"], [])
        self.assertEqual(req["envs"], [])


class TestDataFixRegression(unittest.TestCase):
    """The localized fws tasks must keep prerequisites so fws starts."""

    def test_localized_fws_tasks_trigger_fws(self):
        for lang in ("zh", "tw"):
            tasks = {t.task_id: t for t in pf.load_tasks(lang)}
            t = tasks["task_gh_issue_triage"]
            self.assertTrue(t.frontmatter.get("prerequisites"),
                            f"{lang} lost prerequisites")
            self.assertTrue(is_fws_task(t.frontmatter),
                            f"{lang} fws task no longer triggers fws")


class TestEvaluate(unittest.TestCase):
    def test_ready_when_all_present(self):
        task = {t.task_id: t for t in pf.load_tasks("tw")}["task_gh_issue_triage"]
        with mock.patch.object(pf, "_which", return_value=True), \
                mock.patch.object(pf, "_has_env", return_value=True):
            res = pf.evaluate_task(task, runtime_ok=True)
        self.assertTrue(res["ready"])
        self.assertEqual(res["missing"], [])

    def test_missing_runtime_and_bins(self):
        task = {t.task_id: t for t in pf.load_tasks("tw")}["task_gh_issue_triage"]
        with mock.patch.object(pf, "_which", return_value=False), \
                mock.patch.object(pf, "_has_env", return_value=False):
            res = pf.evaluate_task(task, runtime_ok=False)
        self.assertFalse(res["ready"])
        self.assertIn("openclaw", res["missing"])
        self.assertIn("fws", res["missing"])
        self.assertIn("gh", res["missing"])

    def test_ready_task_ids_subset(self):
        ids = pf.ready_task_ids("tw", "skills")
        all_ids = [t.task_id for t in pf.filter_suite(pf.load_tasks("tw"), "skills")]
        self.assertTrue(set(ids).issubset(set(all_ids)))


class TestFilterSuite(unittest.TestCase):
    def test_all(self):
        tasks = pf.load_tasks("tw")
        self.assertEqual(len(pf.filter_suite(tasks, "all")), len(tasks))

    def test_category(self):
        tasks = pf.load_tasks("tw")
        got = pf.filter_suite(tasks, "skills")
        self.assertTrue(got)
        self.assertTrue(all(t.category == "skills" for t in got))

    def test_comma_ids(self):
        tasks = pf.load_tasks("tw")
        got = pf.filter_suite(tasks, "task_files,task_workflow")
        self.assertEqual({t.task_id for t in got}, {"task_files", "task_workflow"})


if __name__ == "__main__":
    unittest.main()
