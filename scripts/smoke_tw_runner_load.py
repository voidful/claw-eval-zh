#!/usr/bin/env python3
"""Offline runner smoke for the Taiwan suite — NO OpenClaw, NO model, NO network.

Exercises the pure parts of the pipeline: tasks-dir resolution, task loading,
manifest coverage, pass@k / pass^k aggregation, and the result-metadata shape.
Used by tests/test_tw_runner_smoke_offline.py and as a quick manual check.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
logging.disable(logging.CRITICAL)

import yaml  # noqa: E402
from lib_tasks import TaskLoader  # noqa: E402
import benchmark as B  # noqa: E402
from lib_passk import aggregate_passk  # noqa: E402


def _ns(language="en", region=None, tasks_dir=None):
    return argparse.Namespace(language=language, region=region, tasks_dir=tasks_dir)


def check() -> dict:
    out = {}
    # 1. tasks-dir resolution
    out["resolve"] = {
        "en": B._resolve_tasks_dir(_ns("en"), ROOT).name,
        "zh": B._resolve_tasks_dir(_ns("zh"), ROOT).name,
        "tw": B._resolve_tasks_dir(_ns("tw"), ROOT).name,
        "region_TW": B._resolve_tasks_dir(_ns("en", region="TW"), ROOT).name,
    }
    assert out["resolve"] == {"en": "tasks", "zh": "tasks_zh", "tw": "tasks_tw",
                              "region_TW": "tasks_tw"}, out["resolve"]

    # 2. task loading for all three layers
    out["counts"] = {name: len(TaskLoader(ROOT / d).load_all_tasks())
                     for name, d in (("en", "tasks"), ("zh", "tasks_zh"), ("tw", "tasks_tw"))}
    assert out["counts"]["tw"] == out["counts"]["en"], out["counts"]

    # 3. manifest coverage (tw)
    man = yaml.safe_load((ROOT / "tasks" / "manifest.yaml").read_text(encoding="utf-8"))
    ids = set(man.get("run_first", []) or [])
    for arr in (man.get("categories", {}) or {}).values():
        ids.update(arr or [])
    have = {p.stem for p in (ROOT / "tasks_tw").glob("*.md")}
    out["manifest_missing"] = sorted(ids - have)
    assert not out["manifest_missing"], out["manifest_missing"]

    # 4. pass@k / pass^k aggregation (Pass^3)
    per_task = {
        "t1": {"category": "coding",
               "trials": [{"score": 0.9, "status": "success", "timed_out": False}] * 3},
        "t2": {"category": "coding",
               "trials": [{"score": 0.9, "status": "success", "timed_out": False},
                          {"score": 0.2, "status": "success", "timed_out": False},
                          {"score": 0.9, "status": "success", "timed_out": False}]},
    }
    agg = aggregate_passk(per_task, 0.8)
    out["passk"] = {"pass_at_k_rate": agg["pass_at_k_rate"], "pass_k_rate": agg["pass_k_rate"]}
    assert agg["pass_at_k_rate"] == 1.0 and agg["pass_k_rate"] == 0.5, out["passk"]

    # 5. result-metadata language mapping
    out["meta_lang"] = {
        "tw": B._effective_language(_ns("tw")),
        "region_TW": B._effective_language(_ns("en", region="TW")),
    }
    assert out["meta_lang"] == {"tw": "tw", "region_TW": "tw"}, out["meta_lang"]
    return out


def main(argv=None) -> int:
    argparse.ArgumentParser(description="Offline TW runner smoke.").parse_args(argv)
    out = check()
    print("resolve:", out["resolve"])
    print("counts:", out["counts"])
    print("manifest_missing:", out["manifest_missing"])
    print("passk:", out["passk"])
    print("\nOffline TW runner smoke: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
