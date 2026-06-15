#!/usr/bin/env python3
"""Replay the deterministic TW graders against gold_tw/ and assert thresholds.

For each task with expected_scores.json cases, loads the Taiwan grader, runs
grade(transcript, case_dir) on each case workspace, computes the mean component
score, and checks it against the case's min_mean / max_mean. NO LLM, NO network.

Writes reports/tw_gold_check_report.{json,md}. Exit non-zero on any mismatch.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "gold_tw"
MAP = {r["task_id"]: r for r in json.loads(
    (ROOT / "reports" / "tw_localization_map.json").read_text(encoding="utf-8"))["items"]}


def load_grader(task_id: str):
    cid = MAP[task_id]["claw_eval_tw_id"]
    p = ROOT / "tasks_claw_eval_tw" / cid / "grader.py"
    spec = importlib.util.spec_from_file_location(f"gold_{cid}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def mean(scores: dict) -> float:
    vals = [float(v) for v in scores.values() if isinstance(v, (int, float))]
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def run():
    results = []
    ok = True
    for task_dir in sorted(p for p in GOLD.iterdir() if p.is_dir()):
        task_id = task_dir.name
        exp_file = task_dir / "expected_scores.json"
        if not exp_file.exists():
            continue
        exp = json.loads(exp_file.read_text(encoding="utf-8"))
        cases = exp.get("cases", {})
        if not cases:
            results.append({"task_id": task_id, "type": "llm_judge_calibration",
                            "status": "skipped(no deterministic score)", "cases": {}})
            continue
        grader = load_grader(task_id)
        case_results = {}
        for case, bounds in cases.items():
            cdir = task_dir / case
            transcript = []
            tj = cdir / "transcript.json"
            if tj.exists():
                transcript = json.loads(tj.read_text(encoding="utf-8"))
            scores = grader.grade(transcript, str(cdir))
            mscore = mean(scores)
            passed = True
            if "min_mean" in bounds and mscore < bounds["min_mean"]:
                passed = False
            if "max_mean" in bounds and mscore > bounds["max_mean"]:
                passed = False
            case_results[case] = {"mean": mscore, "bounds": bounds, "passed": passed,
                                  "breakdown": scores}
            ok = ok and passed
        results.append({"task_id": task_id, "type": "deterministic", "cases": case_results})
    return ok, results


def write_reports(ok: bool, results: list, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    total = sum(len(r["cases"]) for r in results if r["type"] == "deterministic")
    failed = sum(1 for r in results if r["type"] == "deterministic"
                 for c in r["cases"].values() if not c["passed"])
    payload = {"overall_pass": ok, "deterministic_cases": total, "failed_cases": failed,
               "results": results}
    (out_dir / "tw_gold_check_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# 台灣 gold check 報告（tw_gold_check_report）", "",
             f"- 整體結果：{'✅ PASS' if ok else '❌ FAIL'}",
             f"- deterministic 案例數：{total}（失敗 {failed}）", "",
             "| task | case | mean | bounds | pass |", "|---|---|---|---|---|"]
    for r in results:
        if r["type"] != "deterministic":
            lines.append(f"| {r['task_id']} | (llm_judge) | – | – | n/a |")
            continue
        for case, c in r["cases"].items():
            lines.append(f"| {r['task_id']} | {case} | {c['mean']} | {c['bounds']} | "
                         f"{'✅' if c['passed'] else '❌'} |")
    (out_dir / "tw_gold_check_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Run TW gold checks.")
    p.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    p.add_argument("--no-report", action="store_true")
    args = p.parse_args(argv)
    ok, results = run()
    if not args.no_report:
        write_reports(ok, results, args.report_dir)
    for r in results:
        if r["type"] != "deterministic":
            print(f"  {r['task_id']}: llm_judge calibration (no deterministic score)")
            continue
        for case, c in r["cases"].items():
            flag = "OK " if c["passed"] else "FAIL"
            print(f"  [{flag}] {r['task_id']}/{case}: mean={c['mean']} bounds={c['bounds']}")
    print(f"\nGold checks: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
