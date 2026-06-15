#!/usr/bin/env python3
"""Export tasks_claw_eval_tw/ to an *official-schema export CANDIDATE*.

NOT claimed to be official-compatible. This transforms the claw-eval-zh extended
schema toward a shape closer to upstream Claw-Eval, recording every change:
  * check.entrypoint            -> metadata.grader_entrypoint (removed from check)
  * environment.timezone/locale/region -> metadata.* (environment keeps timeout/max_turns)
  * user_agent.mode (non-standard) -> metadata.user_agent_mode (user_agent keeps enabled/sessions)
  * fixtures                     -> kept as a fixture list (paths validated)

Outputs:
  exports/claw_eval_tw_candidate/tasks/<id>/{task.yaml,grader.py}
  exports/claw_eval_tw_candidate/manifest.json
  exports/claw_eval_tw_candidate/README.md
  reports/official_export_candidate_report.json
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tasks_claw_eval_tw"
OUT = ROOT / "exports" / "claw_eval_tw_candidate"


def transform(data: dict) -> dict:
    d = copy.deepcopy(data)
    meta = d.setdefault("metadata", {})

    # 1. check.entrypoint -> metadata.grader_entrypoint
    for comp in d.get("scoring_components", []):
        chk = comp.get("check", {})
        if "entrypoint" in chk:
            meta["grader_entrypoint"] = chk.pop("entrypoint")

    # 2. environment.timezone/locale/region -> metadata
    env = d.get("environment", {})
    for k in ("timezone", "locale", "region"):
        if k in env:
            meta[f"env_{k}" if k != "timezone" else "timezone"] = env.pop(k)

    # 3. user_agent.mode -> metadata
    ua = d.get("user_agent", {})
    if isinstance(ua, dict) and "mode" in ua:
        meta["user_agent_mode"] = ua.pop("mode")

    meta["export_candidate"] = True
    meta["official_compat"] = False
    return d


def validate_task(d: dict, errors: list, name: str):
    if not d.get("task_id"):
        errors.append(f"{name}: missing task_id")
    if not (d.get("prompt") or {}).get("text"):
        errors.append(f"{name}: missing prompt.text")
    if (d.get("prompt") or {}).get("language") != "zh":
        errors.append(f"{name}: prompt.language != zh")
    if (d.get("metadata") or {}).get("locale") != "zh-TW":
        errors.append(f"{name}: metadata.locale != zh-TW")
    if not d.get("category"):
        errors.append(f"{name}: missing category")
    # no leftover entrypoint inside check
    for comp in d.get("scoring_components", []):
        if "entrypoint" in (comp.get("check") or {}):
            errors.append(f"{name}: check.entrypoint not removed")
    for fx in d.get("fixtures") or []:
        if not (ROOT / "assets" / fx["source"]).exists():
            errors.append(f"{name}: fixture missing assets/{fx['source']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Export official Claw-Eval candidate.")
    p.add_argument("--validate", action="store_true", help="Validate outputs; exit non-zero on error")
    p.add_argument("--out", type=Path, default=OUT)
    args = p.parse_args(argv)

    if args.out.exists():
        shutil.rmtree(args.out)
    (args.out / "tasks").mkdir(parents=True, exist_ok=True)

    errors: list = []
    manifest = []
    for tdir in sorted(p for p in SRC.iterdir() if p.is_dir()):
        data = yaml.safe_load((tdir / "task.yaml").read_text(encoding="utf-8"))
        cand = transform(data)
        validate_task(cand, errors, tdir.name)
        odir = args.out / "tasks" / tdir.name
        odir.mkdir(parents=True, exist_ok=True)
        (odir / "task.yaml").write_text(
            yaml.safe_dump(cand, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
        if (tdir / "grader.py").exists():
            shutil.copy2(tdir / "grader.py", odir / "grader.py")
        manifest.append({
            "task_id": cand["task_id"],
            "category": cand.get("category", ""),
            "language": (cand.get("prompt") or {}).get("language", ""),
            "locale": (cand.get("metadata") or {}).get("locale", ""),
            "grading_type": (cand.get("metadata") or {}).get("grading_type", ""),
            "grader_entrypoint": (cand.get("metadata") or {}).get("grader_entrypoint"),
            "fixtures": [fx.get("dest") for fx in cand.get("fixtures") or []],
        })

    (args.out / "manifest.json").write_text(
        json.dumps({"benchmark": "claw-style-taiwan", "export": "official-schema-candidate",
                    "official_compatible": False, "task_count": len(manifest),
                    "tasks": manifest}, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out / "README.md").write_text(
        "# Claw-Eval Taiwan — Official-Schema Export *Candidate*\n\n"
        "> ⚠️ 這是**候選（candidate）**匯出，**並非**官方 Claw-Eval 相容格式，亦未經官方驗證。\n\n"
        "由 `scripts/export_official_claw_eval_candidate.py` 從 `tasks_claw_eval_tw/` 轉出。\n"
        "轉換內容見 `docs/official_claw_eval_export_notes.md` 與 "
        "`reports/official_export_candidate_report.json`。\n\n"
        f"- 任務數：{len(manifest)}\n- 語言：zh（locale zh-TW）\n"
        "- 每個任務：`tasks/<id>/task.yaml`（+ 若有 `grader.py`）。\n", encoding="utf-8")

    report = {"generated_by": "export_official_claw_eval_candidate.py",
              "official_compatible": False, "task_count": len(manifest),
              "errors": errors, "valid": not errors}
    (ROOT / "reports" / "official_export_candidate_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    for e in errors:
        print("[ERROR]", e)
    print(f"\nExported {len(manifest)} tasks -> {args.out} | errors: {len(errors)}")
    if args.validate and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
