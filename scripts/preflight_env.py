#!/usr/bin/env python3
"""Preflight environment check for claw-eval-zh / Taiwan benchmark.

Reports, per task, whether the execution environment is ready to actually run it
(OpenClaw runtime + any mock server / CLI / API key the task needs) and, on
request, auto-installs the parts that are installable (the ``fws`` mock server).

It is offline and deterministic: it only inspects PATH + environment variables
and the task frontmatter — it never calls a model or the network (except the
optional ``--install`` step, which shells out to ``npm``).

Requirement model (data-driven from each task's ``prerequisites``):
  - every task needs the OpenClaw runtime (``openclaw``);
  - ``npm:@juppytt/fws``  -> needs the ``fws`` mock-server binary;
  - ``cli:<name>``        -> needs the ``<name>`` CLI (e.g. ``gws``, ``gh``);
  - the image-generation task needs ``OPENROUTER_API_KEY`` (its image tool).

Used both as a CLI and as a library by ``run_hf_benchmark.py``.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from lib_fws import is_fws_task
from lib_tasks import Task, TaskLoader

SKILL_ROOT = Path(__file__).resolve().parent.parent

# The agent runtime every task needs.
RUNTIME_BIN = "openclaw"

# HuggingFace token env names accepted for the router serving mode.
HF_TOKEN_ENVS = ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACEHUB_API_TOKEN")

# How to obtain each missing dependency (shown to the user).
FIX_HINTS: Dict[str, str] = {
    RUNTIME_BIN: "安裝 OpenClaw CLI（agent 執行器）：見 https://openclaw.ai 或專案 README",
    "fws": "npm install -g @juppytt/fws   （GWS/GitHub 本地 mock 伺服器，無需真實憑證）",
    "gws": "安裝 Google Workspace CLI（gws）：見 @juppytt/fws README 的 gws 章節",
    "gh": "安裝 GitHub CLI：brew install gh（或 apt/dnf install gh）",
    "OPENROUTER_API_KEY": "export OPENROUTER_API_KEY=...（task_image_gen 的 generate_image 影像工具用）",
}


def _which(name: str) -> bool:
    return shutil.which(name) is not None


def _has_env(name: str) -> bool:
    return bool(os.environ.get(name))


def task_requirements(task: Task) -> Dict[str, List[str]]:
    """Return {"bins": [...], "envs": [...]} a task needs beyond the runtime."""
    bins: List[str] = []
    envs: List[str] = []
    for p in task.frontmatter.get("prerequisites") or []:
        spec = str(p)
        if spec.startswith("npm:"):
            if "fws" in spec:
                bins.append("fws")
        elif spec.startswith("cli:"):
            bins.append(spec.split(":", 1)[1].strip())
    # Image-generation task needs its own image API key (separate from the
    # chat model that drives the agent).
    blob = f"{task.task_id} {task.prompt} {task.expected_behavior}".lower()
    if "generate_image" in blob or "image_gen" in task.task_id:
        envs.append("OPENROUTER_API_KEY")
    # De-dup, stable order.
    bins = list(dict.fromkeys(bins))
    envs = list(dict.fromkeys(envs))
    return {"bins": bins, "envs": envs}


def evaluate_task(task: Task, runtime_ok: bool) -> Dict[str, Any]:
    """Compute readiness of a single task against the current environment."""
    req = task_requirements(task)
    missing: List[str] = []
    if not runtime_ok:
        missing.append(RUNTIME_BIN)
    for b in req["bins"]:
        if not _which(b):
            missing.append(b)
    for e in req["envs"]:
        if not _has_env(e):
            missing.append(e)
    return {
        "task_id": task.task_id,
        "category": task.category,
        "needs_fws": is_fws_task(task.frontmatter),
        "requires": req["bins"] + req["envs"],
        "missing": missing,
        "ready": not missing,
    }


def evaluate(tasks: List[Task]) -> List[Dict[str, Any]]:
    runtime_ok = _which(RUNTIME_BIN)
    return [evaluate_task(t, runtime_ok) for t in tasks]


def load_tasks(language: str) -> List[Task]:
    sub = {"en": "tasks", "zh": "tasks_zh", "tw": "tasks_tw"}.get(language, "tasks")
    loader = TaskLoader(SKILL_ROOT / sub)
    return loader.load_all_tasks()


def filter_suite(tasks: List[Task], suite: str) -> List[Task]:
    """Mirror benchmark.py --suite: 'all', a category, or comma-separated ids."""
    if suite in ("all", "automated-only", ""):
        return tasks
    wanted = {s.strip() for s in suite.split(",") if s.strip()}
    by_id = [t for t in tasks if t.task_id in wanted]
    if by_id:
        return by_id
    return [t for t in tasks if t.category in wanted]


def ready_task_ids(language: str, suite: str = "all") -> List[str]:
    """Task ids whose environment is ready (used by run_hf_benchmark)."""
    tasks = filter_suite(load_tasks(language), suite)
    return [r["task_id"] for r in evaluate(tasks) if r["ready"]]


def install_fws() -> bool:
    """Install the fws mock server via npm. Returns True on success."""
    if _which("fws"):
        return True
    if not _which("npm"):
        print("  ✗ npm 不存在，無法自動安裝 fws；請先安裝 Node.js/npm", file=sys.stderr)
        return False
    print("  → npm install -g @juppytt/fws ...")
    res = subprocess.run(
        ["npm", "install", "-g", "@juppytt/fws"],
        capture_output=True, text=True, check=False,
    )
    if res.returncode != 0:
        print(f"  ✗ fws 安裝失敗：{res.stderr.strip()[:300]}", file=sys.stderr)
        return False
    print("  ✓ fws 安裝完成")
    return True


def report(results: List[Dict[str, Any]], serve: Optional[str] = None,
           token_ok: Optional[bool] = None) -> None:
    ready = [r for r in results if r["ready"]]
    not_ready = [r for r in results if not r["ready"]]
    print(f"\n就緒：{len(ready)}/{len(results)} 個任務可直接執行。")
    if serve is not None:
        model_state = "OK" if token_ok else "缺 token / 端點未就緒"
        print(f"模型端點（serve={serve}）：{model_state}")
    if not_ready:
        print(f"\n尚未就緒（{len(not_ready)}）—— 缺少項目與補法：")
        miss_index: Dict[str, List[str]] = {}
        for r in not_ready:
            for m in r["missing"]:
                miss_index.setdefault(m, []).append(r["task_id"])
        for dep, tids in sorted(miss_index.items()):
            print(f"\n  ● 缺 {dep}（{len(tids)} 個任務）")
            print(f"      補法：{FIX_HINTS.get(dep, '（請參考文件）')}")
            preview = ", ".join(tids[:6]) + (" ..." if len(tids) > 6 else "")
            print(f"      影響：{preview}")
    else:
        print("\n全部任務就緒。")


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="claw-eval-zh 執行環境前置檢查")
    p.add_argument("--language", choices=["en", "zh", "tw"], default="tw",
                   help="任務語言層：en/zh/tw（預設 tw）")
    p.add_argument("--suite", default="all",
                   help="'all'、類別名稱（如 integrations），或逗號分隔的 task id")
    p.add_argument("--install", action="store_true",
                   help="自動安裝可安裝的前置（目前為 fws mock 伺服器）")
    p.add_argument("--json", action="store_true", help="輸出 JSON")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    if args.install:
        any_needs_fws = any(
            "fws" in evaluate_task(t, True)["requires"]
            for t in filter_suite(load_tasks(args.language), args.suite)
        )
        if any_needs_fws:
            install_fws()
    tasks = filter_suite(load_tasks(args.language), args.suite)
    results = evaluate(tasks)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        report(results)
    # Exit 0 always: this is a report, not a gate (run_hf_benchmark decides).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
