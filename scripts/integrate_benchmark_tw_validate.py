#!/usr/bin/env python3
"""Authoritative conformance check for the 38 integrated benchmark tasks.

Verifies each tasks_tw/<id>.md against the schema the PinchBench loader and the
tw validator require. Prints a per-task PASS/FAIL with concrete issues. Exit 0
only if all 38 pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import lib_zh  # noqa: E402
from lib_tasks import TaskLoader  # noqa: E402

TASKS_TW = ROOT / "tasks_tw"
CANON = {"Prompt", "Expected Behavior", "Grading Criteria",
         "Automated Checks", "LLM Judge Rubric", "Additional Notes"}
REQUIRED_SECTIONS = {"Prompt", "Expected Behavior", "Grading Criteria",
                     "Automated Checks", "LLM Judge Rubric"}

NEW_IDS = __import__("integrate_benchmark_tw_manifest").NEW_IDS


def check(task_id: str) -> list[str]:
    issues: list[str] = []
    p = TASKS_TW / f"{task_id}.md"
    if not p.exists():
        return [f"file missing: {p}"]
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return ["no YAML frontmatter"]
    fm_text, body = m.group(1), m.group(2)
    try:
        meta = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        return [f"frontmatter parse error: {e}"]

    if meta.get("id") != task_id:
        issues.append(f"id {meta.get('id')!r} != filename stem {task_id!r}")
    name = str(meta.get("name") or "")
    if not name.strip():
        issues.append("name empty")
    elif not re.search(r"[一-鿿]", name):
        issues.append(f"name has no Chinese (looks untranslated): {name!r}")
    if not str(meta.get("category") or "").strip():
        issues.append("category empty")
    if meta.get("grading_type") != "hybrid":
        issues.append(f"grading_type {meta.get('grading_type')!r} != hybrid")
    if not isinstance(meta.get("timeout_seconds"), int):
        issues.append("timeout_seconds not int")
    gw = meta.get("grading_weights") or {}
    if not (isinstance(gw, dict) and "automated" in gw and "llm_judge" in gw):
        issues.append("grading_weights missing automated/llm_judge")
    else:
        s = float(gw["automated"]) + float(gw["llm_judge"])
        if not (0.99 <= s <= 1.01):
            issues.append(f"grading_weights sum={s} (must be fractions ~1.0, not {gw})")
    if meta.get("language") != "zh":
        issues.append("language != zh")
    if meta.get("locale") != "zh-TW":
        issues.append("locale != zh-TW")
    if meta.get("region") != "TW":
        issues.append("region != TW")

    wf = meta.get("workspace_files")
    if wf is None:
        issues.append("workspace_files key missing")
    else:
        if not isinstance(wf, list):
            issues.append("workspace_files not a list")
        for i, w in enumerate(wf or []):
            if not isinstance(w, dict) or "source" not in w or "dest" not in w:
                issues.append(f"workspace_files[{i}] not a {{source,dest}} dict: {w!r}")
                continue
            src = str(w["source"])
            if not src.startswith("tw/"):
                issues.append(f"workspace_files[{i}] source not under tw/: {src}")
            if not (ROOT / "assets" / src).exists():
                issues.append(f"workspace_files[{i}] asset missing: assets/{src}")
            if any("一" <= c <= "鿿" for c in str(w["dest"])):
                issues.append(f"workspace_files[{i}] dest translated: {w['dest']!r}")

    # body sections
    h2 = [h.strip() for h in re.findall(r"^##\s+(.+)$", body, re.MULTILINE)]
    noncanon = [h for h in h2 if h not in CANON]
    if noncanon:
        issues.append(f"non-canonical ## headers (would split prompt): {noncanon}")
    missing = REQUIRED_SECTIONS - set(h2)
    if missing:
        issues.append(f"missing required sections: {sorted(missing)}")

    # grader
    cm = re.search(r"```python\s*(.*?)\s*```", body, re.DOTALL)
    if not cm:
        issues.append("no ```python grader block")
    else:
        code = cm.group(1)
        try:
            compile(code, f"{task_id}:grader", "exec")
        except SyntaxError as e:
            issues.append(f"grader syntax error: {e}")
        if "def grade(" not in code:
            issues.append("grader has no def grade(")
        if "_GRADE_IMPL = grade" not in code or "return _GRADE_IMPL" not in code:
            issues.append("grader missing bilingual wrapper")

    # simplified chars
    simp = lib_zh.find_simplified(body)
    if simp:
        issues.append(f"simplified chars: {''.join(simp)}")

    # loader integration
    try:
        t = TaskLoader(TASKS_TW).load_task(p)
        if not t.prompt:
            issues.append("loader: empty prompt")
        if not t.expected_behavior:
            issues.append("loader: empty expected_behavior")
        if len(t.grading_criteria) < 6:
            issues.append(f"loader: grading_criteria only {len(t.grading_criteria)} (<6)")
        if not t.automated_checks:
            issues.append("loader: no automated_checks")
    except Exception as e:  # noqa: BLE001
        issues.append(f"loader raised: {e}")

    return issues


def main() -> int:
    fails = 0
    for tid in NEW_IDS:
        iss = check(tid)
        if iss:
            fails += 1
            print(f"FAIL {tid}")
            for i in iss:
                print(f"      - {i}")
        else:
            print(f"PASS {tid}")
    print(f"\n{len(NEW_IDS) - fails}/{len(NEW_IDS)} passed; {fails} failing")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
