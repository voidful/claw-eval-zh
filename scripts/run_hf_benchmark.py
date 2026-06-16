#!/usr/bin/env python3
"""One-command benchmark runner for a HuggingFace model id.

Goal: "just give a HuggingFace model id and the whole suite runs".

It wires a HF model into the existing OpenClaw benchmark by resolving an
OpenAI-compatible endpoint (which ``benchmark.py`` already supports via
``--base-url``/``--api-key`` -> a ``custom`` OpenClaw provider) and then runs
``benchmark.py`` for you. It also runs the preflight check, can auto-install the
``fws`` mock server, and by default only runs tasks whose environment is ready
(so missing infra never pollutes the score as "0% fail").

Serving modes (``--serve``):
  router    HF Inference Router (https://router.huggingface.co/v1) — no GPU,
            needs an HF token. This is the "just a model id" path. (default)
  local     Launch a local vLLM OpenAI server for the model (needs GPU + vllm).
  endpoint  Use your own OpenAI-compatible endpoint (--base-url/--api-key),
            e.g. a TGI / dedicated HF Inference Endpoint.

Examples:
  python scripts/run_hf_benchmark.py --hf-model Qwen/Qwen2.5-7B-Instruct
  python scripts/run_hf_benchmark.py --hf-model meta-llama/Llama-3.3-70B-Instruct \\
         --suite integrations --auto-install
  python scripts/run_hf_benchmark.py --hf-model my/model --serve local
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import preflight_env as pf

SKILL_ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = SKILL_ROOT / "scripts" / "benchmark.py"
HF_ROUTER_BASE_URL = "https://router.huggingface.co/v1"


def _resolve_token(explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit
    for name in pf.HF_TOKEN_ENVS:
        if os.environ.get(name):
            return os.environ[name]
    return None


def _wait_for_endpoint(base_url: str, timeout_s: float) -> bool:
    """Poll <base_url>/models until it answers or the timeout elapses."""
    url = base_url.rstrip("/") + "/models"
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310 (local/trusted)
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(2)
    return False


def resolve_endpoint(args: argparse.Namespace) -> Tuple[str, str, Optional[Callable[[], None]]]:
    """Return (base_url, api_key, teardown) for the chosen serving mode."""
    if args.serve == "endpoint":
        if not args.base_url:
            sys.exit("✗ --serve endpoint 需要 --base-url")
        return args.base_url, (args.api_key or _resolve_token(args.hf_token) or "EMPTY"), None

    if args.serve == "router":
        token = _resolve_token(args.hf_token)
        if not token:
            sys.exit("✗ --serve router 需要 HF token：設 --hf-token 或 "
                     "export HF_TOKEN=...（HuggingFace Inference Router）")
        return (args.base_url or HF_ROUTER_BASE_URL), token, None

    # local vLLM
    import shutil
    if not (shutil.which("vllm") or _module_exists("vllm")):
        sys.exit("✗ --serve local 需要安裝 vLLM：pip install vllm（且需 GPU）")
    base_url = f"http://127.0.0.1:{args.vllm_port}/v1"
    print(f"🚀 啟動本地 vLLM：{args.hf_model} on :{args.vllm_port} ...")
    cmd = [sys.executable, "-m", "vllm.entrypoints.openai.api_server",
           "--model", args.hf_model, "--host", "127.0.0.1", "--port", str(args.vllm_port)]
    proc = subprocess.Popen(cmd)

    def teardown() -> None:
        print("🛑 關閉本地 vLLM ...")
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()

    if not _wait_for_endpoint(base_url, timeout_s=args.serve_timeout):
        teardown()
        sys.exit(f"✗ vLLM 在 {args.serve_timeout}s 內未就緒")
    print("✅ 本地 vLLM 就緒")
    return base_url, "EMPTY", teardown


def _module_exists(name: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(name) is not None


def resolve_suite(args: argparse.Namespace) -> Optional[str]:
    """Decide the --suite value, honoring --skip-unready. None => abort."""
    if args.include_unready:
        return args.suite
    ready = set(pf.ready_task_ids(args.language, args.suite))
    requested = pf.filter_suite(pf.load_tasks(args.language), args.suite)
    requested_ids = [t.task_id for t in requested]
    run_ids = [tid for tid in requested_ids if tid in ready]
    skipped = [tid for tid in requested_ids if tid not in ready]
    if skipped:
        print(f"⏭️  跳過 {len(skipped)} 個環境未就緒的任務（不計入分數）："
              f"{', '.join(skipped[:8])}{' ...' if len(skipped) > 8 else ''}")
        print("    （用 scripts/preflight_env.py 看缺什麼；或加 --include-unready 強制執行）")
    if not run_ids:
        return None
    return ",".join(run_ids)


def build_benchmark_cmd(args: argparse.Namespace, base_url: str, api_key: str,
                        suite: str) -> List[str]:
    cmd = [
        sys.executable, str(BENCHMARK),
        "--model", args.hf_model,
        "--base-url", base_url,
        "--api-key", api_key,
        "--language", args.language,
        "--suite", suite,
        "--runs", str(args.runs),
        "--pass-threshold", str(args.pass_threshold),
        "--output-dir", args.output_dir,
        "--timeout-multiplier", str(args.timeout_multiplier),
    ]
    if not args.upload:
        cmd.append("--no-upload")
    return cmd


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="用一個 HuggingFace model id 跑 claw-eval-zh 全套任務",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--hf-model", required=True,
                   help="HuggingFace model id，例如 Qwen/Qwen2.5-7B-Instruct")
    p.add_argument("--hf-token", default=None,
                   help="HF token（或設環境變數 HF_TOKEN）；router 模式必需")
    p.add_argument("--serve", choices=["router", "local", "endpoint"], default="router",
                   help="模型服務方式（預設 router：HF Inference Router，免 GPU）")
    p.add_argument("--base-url", default=None, help="自訂 OpenAI 相容端點（endpoint 模式）")
    p.add_argument("--api-key", default=None, help="端點 API key（覆寫）")
    p.add_argument("--language", choices=["en", "zh", "tw"], default="tw",
                   help="任務語言層（預設 tw 台灣在地版）")
    p.add_argument("--suite", default="all",
                   help="'all'、類別名稱，或逗號分隔 task id（預設 all）")
    p.add_argument("--runs", type=int, default=1, help="每題執行次數（pass@k/pass^k）")
    p.add_argument("--pass-threshold", type=float, default=0.8, help="pass 門檻（預設 0.8）")
    p.add_argument("--output-dir", default="results", help="結果輸出目錄")
    p.add_argument("--timeout-multiplier", type=float, default=1.0, help="逾時倍率")
    p.add_argument("--include-unready", action="store_true",
                   help="不要跳過環境未就緒的任務（預設會跳過以免污染分數）")
    p.add_argument("--auto-install", action="store_true",
                   help="自動安裝可安裝的前置（fws mock 伺服器）")
    p.add_argument("--upload", action="store_true", help="上傳結果（預設不上傳）")
    p.add_argument("--vllm-port", type=int, default=8000, help="本地 vLLM 連接埠")
    p.add_argument("--serve-timeout", type=float, default=900.0,
                   help="等待本地 vLLM 就緒的秒數")
    p.add_argument("--dry-run", action="store_true",
                   help="只印出計畫與將執行的指令，不啟動模型、不執行 benchmark")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    # 1) Preflight + optional auto-install.
    if args.auto_install:
        pf.install_fws()
    tasks = pf.filter_suite(pf.load_tasks(args.language), args.suite)
    results = pf.evaluate(tasks)
    token_ok = (args.serve != "router") or bool(_resolve_token(args.hf_token))
    pf.report(results, serve=args.serve, token_ok=token_ok)

    # 2) Decide which tasks to run.
    suite = resolve_suite(args)
    if suite is None:
        print("\n✗ 沒有任何環境就緒的任務可跑。請依上面的補法安裝後再試，"
              "或加 --include-unready 強制執行。")
        return 2

    # 3) Dry-run: show the plan and exit (no model, no network).
    if args.dry_run:
        base_url = args.base_url or (HF_ROUTER_BASE_URL if args.serve == "router" else "<vllm>")
        key_display = "<token>" if args.serve == "router" else (args.api_key or "EMPTY")
        cmd = build_benchmark_cmd(args, base_url, key_display, suite)
        n = len(suite.split(","))
        print(f"\n[dry-run] serve={args.serve} base_url={base_url}")
        print(f"[dry-run] 將執行 {n} 個任務（language={args.language}）")
        print("[dry-run] 指令：\n  " + " ".join(cmd))
        return 0

    # 4) Resolve endpoint (may start a local server) and run.
    base_url, api_key, teardown = resolve_endpoint(args)
    cmd = build_benchmark_cmd(args, base_url, api_key, suite)
    print(f"\n▶️  執行 benchmark（serve={args.serve}, base_url={base_url}）")
    try:
        proc = subprocess.run(cmd, check=False)
        return proc.returncode
    finally:
        if teardown:
            teardown()


if __name__ == "__main__":
    raise SystemExit(main())
