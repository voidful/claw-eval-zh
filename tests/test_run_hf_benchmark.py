"""Offline tests for scripts/run_hf_benchmark.py (no model/network)."""
import argparse
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_hf_benchmark as rh  # noqa: E402


def _args(**kw):
    base = dict(
        hf_model="org/model", hf_token=None, serve="router", base_url=None,
        api_key=None, language="tw", suite="all", runs=1, pass_threshold=0.8,
        output_dir="results", timeout_multiplier=1.0, include_unready=False,
        auto_install=False, upload=False, vllm_port=8000, serve_timeout=900.0,
        dry_run=False,
    )
    base.update(kw)
    return argparse.Namespace(**base)


class TestEndpointResolution(unittest.TestCase):
    def test_router_requires_token(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                rh.resolve_endpoint(_args(serve="router", hf_token=None))

    def test_router_with_token(self):
        base_url, key, teardown = rh.resolve_endpoint(_args(serve="router", hf_token="hf_x"))
        self.assertEqual(base_url, rh.HF_ROUTER_BASE_URL)
        self.assertEqual(key, "hf_x")
        self.assertIsNone(teardown)

    def test_endpoint_requires_base_url(self):
        with self.assertRaises(SystemExit):
            rh.resolve_endpoint(_args(serve="endpoint", base_url=None))

    def test_endpoint_mode(self):
        base_url, key, teardown = rh.resolve_endpoint(
            _args(serve="endpoint", base_url="http://x/v1", api_key="k"))
        self.assertEqual(base_url, "http://x/v1")
        self.assertEqual(key, "k")
        self.assertIsNone(teardown)


class TestSuiteResolution(unittest.TestCase):
    def test_skip_unready_filters(self):
        ready = {"task_files", "task_workflow"}
        with mock.patch.object(rh.pf, "ready_task_ids", return_value=ready):
            suite = rh.resolve_suite(_args(suite="skills", include_unready=False))
        self.assertIsNotNone(suite)
        self.assertTrue(set(suite.split(",")).issubset(ready))

    def test_none_when_nothing_ready(self):
        with mock.patch.object(rh.pf, "ready_task_ids", return_value=set()):
            suite = rh.resolve_suite(_args(suite="integrations", include_unready=False))
        self.assertIsNone(suite)

    def test_include_unready_passes_through(self):
        suite = rh.resolve_suite(_args(suite="integrations", include_unready=True))
        self.assertEqual(suite, "integrations")


class TestBuildCmd(unittest.TestCase):
    def test_cmd_has_expected_flags(self):
        cmd = rh.build_benchmark_cmd(
            _args(), base_url="http://x/v1", api_key="k", suite="task_files")
        joined = " ".join(cmd)
        self.assertIn("--model org/model", joined)
        self.assertIn("--base-url http://x/v1", joined)
        self.assertIn("--api-key k", joined)
        self.assertIn("--language tw", joined)
        self.assertIn("--suite task_files", joined)
        self.assertIn("--no-upload", joined)

    def test_upload_flag_toggles_no_upload(self):
        cmd = rh.build_benchmark_cmd(
            _args(upload=True), base_url="http://x/v1", api_key="k", suite="task_files")
        self.assertNotIn("--no-upload", cmd)


if __name__ == "__main__":
    unittest.main()
