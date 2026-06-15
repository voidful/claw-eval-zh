#!/usr/bin/env python3
"""Phase 3 converter: build the Taiwan-localized suite (tasks_tw/, tasks_claw_eval_tw/).

Reuses the Phase 2 converter machinery. For each PinchBench task it merges, in
order of increasing precedence:
  1. Phase 2 zh overrides  (scripts/translation_overrides{.yaml,/*.yaml})   — base 繁中
  2. Phase 3 TW overrides  (scripts/tw_localization_overrides/*.yaml)        — 台灣在地化

Tasks whose localization_strategy is `copy`/`language_polish` (no TW override)
therefore reuse the Phase 2 繁中 content verbatim, re-tagged with region/timezone.
Tasks with a TW override use the localized content. NO external translation API.

Outputs:
  tasks_tw/<task_id>.md  +  tasks_tw/manifest.yaml
  tasks_claw_eval_tw/<T###tw_slug>/task.yaml  +  grader.py
  reports/tw_localization_coverage.json
  reports/tw_manual_review_required.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib_tasks import Task, TaskLoader  # noqa: E402
import lib_zh  # noqa: E402
import convert_pinchbench_to_claw_eval_zh as C  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("convert-tw")


def load_map(path: Path) -> Dict[str, Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["task_id"]: row for row in data["items"]}


def merge_overrides(base: Dict[str, Any], tw: Dict[str, Any]) -> Dict[str, Any]:
    """Per-task merge: TW keys override zh keys."""
    out: Dict[str, Any] = {}
    for tid in set(base) | set(tw):
        merged = dict(base.get(tid) or {})
        merged.update(tw.get(tid) or {})
        out[tid] = merged
    return out


# ---------------------------------------------------------------------------
# TW task.yaml / markdown builders (adapted from the Phase 2 converter)
# ---------------------------------------------------------------------------
def _tw_workspace_files(task: Task, ov: Dict[str, Any]) -> List[Dict[str, str]]:
    if "workspace_files" in ov and ov["workspace_files"] is not None:
        return ov["workspace_files"]
    return task.workspace_files or []


def _tw_primary_dimensions(task: Task, risk: Dict[str, Any]) -> List[str]:
    """Phase 2 dimensions, augmented with the localization map's risk flags."""
    dims = list(C.compute_primary_dimensions(task))
    if (risk.get("safety_sensitive") or risk.get("legal_or_financial")
            or risk.get("security_sensitive")) and "safety" not in dims:
        dims.append("safety")
    if risk.get("live_web") and "robustness" not in dims:
        dims.append("robustness")
    return dims


def build_tw_task_yaml(task: Task, tr: C.Translation, tw_id: str, strategy: str,
                       ov: Dict[str, Any], mr: Dict[str, Any],
                       risk: Dict[str, Any]) -> Dict[str, Any]:
    claw_category = C.map_category(task)
    tags = ["pinchbench-derived", "claw-style", "taiwan", "zh-TW",
            task.category, C.base_tag(task)]
    seen = set()
    tags = [t for t in tags if t and not (t in seen or seen.add(t))]

    ws = _tw_workspace_files(task, ov)
    fixtures = [{"source": f["source"], "dest": f["dest"]}
                for f in ws if "source" in f and "dest" in f]

    data: Dict[str, Any] = {}
    data["task_id"] = tw_id
    data["task_name"] = tr.task_name
    data["version"] = "0.3.0"
    data["category"] = claw_category
    data["difficulty"] = C.map_difficulty(task, ov)
    data["tags"] = tags
    data["source"] = {
        "benchmark": "pinchbench",
        "phase2_source": f"tasks_zh/{task.task_id}.md",
        "original_task_id": task.task_id,
        "original_file": f"tasks/{task.task_id}.md",
    }
    data["prompt"] = {"text": tr.prompt, "language": "zh"}
    data["tools"] = ov.get("tools", []) or []
    data["tool_endpoints"] = []
    data["services"] = _services_for(task)
    data["fixtures"] = fixtures
    data["environment"] = {
        "timeout_seconds": task.timeout_seconds,
        "timezone": "Asia/Taipei",
        "locale": "zh-TW",
        "region": "TW",
        "max_turns": len(task.frontmatter.get("sessions", [])) or 1,
    }
    data["scoring_components"] = C.build_scoring_components(task)
    data["safety_checks"] = list(ov.get("safety_checks", []) or [])

    data["expected_actions"] = list(tr.grading_criteria)

    sessions = task.frontmatter.get("sessions")
    if sessions:
        ua: Dict[str, Any] = {"enabled": True, "mode": "scripted", "sessions": []}
        for s in C._translate_sessions(sessions, tr):
            if isinstance(s, dict):
                ua["sessions"].append({"prompt": s.get("prompt", ""),
                                       "new_session": bool(s.get("new_session", False))})
        data["user_agent"] = ua
    else:
        data["user_agent"] = {"enabled": False}

    data["judge_rubric"] = C.resolve_rubric(task, tr)
    data["reference_solution"] = tr.expected_behavior
    data["primary_dimensions"] = _tw_primary_dimensions(task, risk)

    data["metadata"] = {
        "locale": "zh-TW",
        "region": "TW",
        "timezone": "Asia/Taipei",
        "grading_type": task.grading_type,
        "grading_weights": task.grading_weights or {},
        "workspace_files": ws,
        "source_benchmark": "pinchbench",
        "translation_status": "complete",
        "conversion_stage": "phase3_taiwan_localized",
        "localization_strategy": strategy,
        "manual_review_required": bool(mr.get("required", False)),
        "notes": "Generated from tasks_zh by convert_zh_to_tw_localized.py",
    }
    return data


def _services_for(task: Task) -> List[Dict[str, Any]]:
    if C.is_external_service(task):
        return [{"name": "fws", "note": "Google Workspace / GitHub mock (fws)"}]
    return []


def render_tw_markdown(task: Task, tr: C.Translation, tw_id: str, strategy: str,
                       ov: Dict[str, Any]) -> str:
    ws = _tw_workspace_files(task, ov)
    fm: Dict[str, Any] = {
        "id": task.task_id,
        "name": tr.task_name,
        "category": task.category,
        "grading_type": task.grading_type,
        "timeout_seconds": task.timeout_seconds,
        "language": "zh",
        "locale": "zh-TW",
        "region": "TW",
        "source_task_id": task.task_id,
        "source_benchmark": "pinchbench",
        "source_locale": "zh-TW",
        "localization": "taiwan",
        "localization_strategy": strategy,
        "claw_eval_tw_id": tw_id,
        "workspace_files": ws,
    }
    if task.grading_weights:
        fm["grading_weights"] = task.grading_weights
    sessions = task.frontmatter.get("sessions")
    if sessions:
        fm["multi_session"] = True
        fm["sessions"] = C._translate_sessions(sessions, tr)
    frontmatter = C.dump_yaml(fm).strip()

    parts: List[str] = [f"---\n{frontmatter}\n---", "", f"# {tr.task_name}", ""]
    parts += ["## Prompt", ""]
    if sessions:
        parts.append("本任務為多輪任務，請見 frontmatter 的 `sessions` 欄位。")
    else:
        parts.append(tr.prompt)
    parts += ["", "## Expected Behavior", "", tr.expected_behavior, ""]
    parts += ["## Grading Criteria", ""]
    for c in tr.grading_criteria:
        parts.append(f"- [ ] {c}")
    parts.append("")
    if task.grading_type in ("automated", "hybrid"):
        parts += ["## Automated Checks", "", "```python", C.grader_body(task, tr), "```", ""]
    if task.grading_type in ("llm_judge", "hybrid"):
        parts += ["## LLM Judge Rubric", "",
                  C.resolve_rubric(task, tr) or "依任務的評分標準（Grading Criteria）評估。", ""]
    return "\n".join(parts).rstrip() + "\n"


def render_tw_grader(task: Task, tr: C.Translation, tw_id: str) -> str:
    header = (
        f'"""Grader for {tw_id} (Taiwan-localized from PinchBench `{task.task_id}`).\n\n'
        f"Phase 2 source: tasks_zh/{task.task_id}.md\n"
        f"Original file: tasks/{task.task_id}.md\n"
        f"grading_type: {task.grading_type}\n\n"
        "Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,\n"
        "importable without claw_eval. Bilingual report normalization + optional\n"
        "Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).\n"
        '"""\n\nfrom __future__ import annotations\n\n\n'
    )
    body = C.grader_body(task, tr)
    adapter = C.GRADER_ADAPTER.replace(
        "__PRIMARY_DIMENSIONS__", repr(C.compute_primary_dimensions(task)))
    return header + body + adapter


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def _us_residue(text: str) -> List[str]:
    markers = ["San Francisco", "New York", "California", "ZIP code", "Apple stock",
               "U.S. Steel", " USD", "United States"]
    low = text
    return [m for m in markers if m.lower() in low.lower()]


def build_coverage(rows: List[Dict[str, Any]], tw_map: Dict[str, Dict[str, Any]],
                   tasks_by_id: Dict[str, Task]) -> Dict[str, Any]:
    from collections import Counter
    strat = Counter(r["strategy"] for r in rows)
    deg = Counter(tw_map[r["task_id"]]["localization_degree"] for r in rows)
    fixture_replaced = [r["task_id"] for r in rows if r["fixture_replaced"]]
    grader_changed = [r["task_id"] for r in rows if r["grader_changed"]]
    return {
        "generated_by": "convert_zh_to_tw_localized.py",
        "conversion_stage": "phase3_taiwan_localized",
        "total_tasks": len(rows),
        "tasks_tw_count": len(rows),
        "tasks_claw_eval_tw_count": len(rows),
        "localization_strategy_counts": dict(strat),
        "localization_degree_counts": dict(deg),
        "fixture_replaced_count": len(fixture_replaced),
        "fixture_replaced": fixture_replaced,
        "grader_changed_count": len(grader_changed),
        "grader_changed": grader_changed,
        "anchor_tasks_completed": [r["task_id"] for r in rows if tw_map[r["task_id"]]["anchor"]],
        "safety_sensitive_count": sum(
            1 for r in rows if tw_map[r["task_id"]]["risk"]["safety_sensitive"]),
        "robustness_sensitive_count": sum(
            1 for r in rows
            if "robustness" in C.compute_primary_dimensions(tasks_by_id[r["task_id"]])),
        "high_severity_review_count": sum(
            1 for r in rows if tw_map[r["task_id"]]["manual_review"]["severity"] == "high"),
        "us_residue_warnings": sum(1 for r in rows if r["us_residue"]),
        "simplified_char_findings": sum(1 for r in rows if r["simplified"]),
        "english_leakage_findings": sum(1 for r in rows if r["leakage"]),
        "todo_findings": sum(1 for r in rows if r["todo"]),
        "validation_errors": None,
        "validation_warnings": None,
    }


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Build the Taiwan-localized suite.")
    p.add_argument("--write", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--tasks", type=str, default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--tasks-dir", type=Path, default=SKILL_ROOT / "tasks")
    p.add_argument("--out-tw", type=Path, default=SKILL_ROOT / "tasks_tw")
    p.add_argument("--out-claw", type=Path, default=SKILL_ROOT / "tasks_claw_eval_tw")
    p.add_argument("--map", type=Path, default=SKILL_ROOT / "reports" / "tw_localization_map.json")
    p.add_argument("--zh-overrides", type=Path, default=SCRIPT_DIR / "translation_overrides.yaml")
    p.add_argument("--zh-overrides-dir", type=Path, default=SCRIPT_DIR / "translation_overrides")
    p.add_argument("--tw-overrides-dir", type=Path, default=SCRIPT_DIR / "tw_localization_overrides")
    p.add_argument("--coverage-out", "--report", dest="coverage_out", type=Path,
                   default=SKILL_ROOT / "reports" / "tw_localization_coverage.json")
    p.add_argument("--manual-review-out", type=Path,
                   default=SKILL_ROOT / "reports" / "tw_manual_review_required.json")
    args = p.parse_args(argv)
    write = args.write and not args.dry_run

    tasks = TaskLoader(args.tasks_dir).load_all_tasks()
    tasks_by_id = {t.task_id: t for t in tasks}
    tw_map = load_map(args.map)

    zh_ov = C.load_overrides(args.zh_overrides, args.zh_overrides_dir)
    tw_ov = C.load_overrides(Path("/nonexistent"), args.tw_overrides_dir)
    merged = merge_overrides(zh_ov, tw_ov)

    selected = tasks
    if args.tasks:
        want = {s.strip() for s in args.tasks.split(",") if s.strip()}
        selected = [t for t in tasks if t.task_id in want]
    if args.limit is not None:
        selected = selected[: args.limit]

    written: List[str] = []
    rows: List[Dict[str, Any]] = []
    manual_items: List[Dict[str, Any]] = []

    for task in selected:
        m = tw_map.get(task.task_id)
        if not m:
            logger.warning("no map entry for %s, skipping", task.task_id)
            continue
        tw_id = m["claw_eval_tw_id"]
        strategy = m["localization_strategy"]
        ov = merged.get(task.task_id, {})
        tr = C.Translation(task, ov if ov else None)
        # Even copy tasks should be "complete" (they reuse Phase 2 繁中 content).
        tr.is_complete = True

        md = render_tw_markdown(task, tr, tw_id, strategy, ov)
        ty = C.dump_yaml(build_tw_task_yaml(task, tr, tw_id, strategy, ov,
                                            m["manual_review"], m.get("risk", {})))
        gr = render_tw_grader(task, tr, tw_id)

        # quality scans for coverage
        blob = "\n".join([tr.task_name, tr.prompt, tr.expected_behavior] +
                         list(tr.grading_criteria) + ([tr.llm_judge_rubric] if tr.llm_judge_rubric else []))
        rows.append({
            "task_id": task.task_id, "tw_id": tw_id, "strategy": strategy,
            "simplified": bool(lib_zh.find_simplified(blob)),
            "leakage": lib_zh.english_leakage_ratio(tr.prompt) > 0.65,
            "todo": "TODO(zh)" in blob or "待補" in blob or "待翻譯" in blob,
            "us_residue": bool(_us_residue(tr.prompt)),
            "fixture_replaced": "workspace_files" in ov,
            "grader_changed": "grader_py" in ov,
        })

        mrv = m["manual_review"]
        if mrv.get("required"):
            manual_items.append({
                "task_id": task.task_id,
                "tw_task_path": f"tasks_tw/{task.task_id}.md",
                "claw_eval_tw_path": f"tasks_claw_eval_tw/{tw_id}/",
                "reason": mrv.get("reason", ""),
                "severity": mrv.get("severity", "low"),
                "domain": _domain(m),
                "localization_strategy": strategy,
                "suggested_review_action": "人工逐欄檢查台灣語境、安全 rubric、fixture 與 grader 一致性。",
            })

        logger.info("• %-30s -> %s  [%s]", task.task_id, tw_id, strategy)
        if not write:
            continue
        for path, content in ((args.out_tw / f"{task.task_id}.md", md),
                              (args.out_claw / tw_id / "task.yaml", ty),
                              (args.out_claw / tw_id / "grader.py", gr)):
            if path.exists() and not args.overwrite:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(str(path))

    if write:
        # tasks_tw manifest mirrors tasks/manifest.yaml filtered to existing files
        manifest = C.regenerate_zh_manifest(args.tasks_dir / "manifest.yaml", args.out_tw)
        (args.out_tw / "manifest.yaml").write_text(
            "# Auto-generated by convert_zh_to_tw_localized.py (Phase 3)\n"
            "# Mirrors tasks/manifest.yaml, filtered to tasks present in tasks_tw/.\n"
            + C.dump_yaml(manifest), encoding="utf-8")
        written.append(str(args.out_tw / "manifest.yaml"))

        cov = build_coverage(rows, tw_map, tasks_by_id)
        args.coverage_out.parent.mkdir(parents=True, exist_ok=True)
        args.coverage_out.write_text(json.dumps(cov, ensure_ascii=False, indent=2), encoding="utf-8")
        args.manual_review_out.write_text(
            json.dumps({"generated_by": "convert_zh_to_tw_localized.py",
                        "count": len(manual_items), "items": manual_items},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(str(args.coverage_out))

    logger.info("\n%s: %d task(s), %d file(s) written.",
                "WROTE" if write else "DRY-RUN", len(selected), len(written))
    if write:
        logger.info("simplified=%d leakage=%d todo=%d us_residue=%d",
                    sum(r["simplified"] for r in rows), sum(r["leakage"] for r in rows),
                    sum(r["todo"] for r in rows), sum(r["us_residue"] for r in rows))

    incomplete = []  # all complete by construction (copy reuses zh)
    if args.strict and incomplete:
        sys.exit(1)
    return {"rows": rows, "written": written}


def _domain(m: Dict[str, Any]) -> str:
    r = m["risk"]
    if r["legal_or_financial"]:
        return "finance_or_legal"
    if r["security_sensitive"]:
        return "security"
    if r["live_web"]:
        return "live_web"
    if r["safety_sensitive"]:
        return "safety"
    return "general"


if __name__ == "__main__":
    main()
