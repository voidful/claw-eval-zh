#!/usr/bin/env python3
"""Validate / lint claw-eval-zh tasks (Phase 2: Traditional-Chinese enforcement).

Checks Claw-Eval-style tasks under tasks_claw_eval_zh/<id>/ (task.yaml + grader.py)
and the generated PinchBench markdown under tasks_zh/<id>.md.

Beyond structural checks, it enforces Traditional Chinese on user-facing fields:
  * no simplified characters (OpenCC if available, else curated set — lib_zh)
  * no English leakage on prose fields that must be Chinese
  * no TODO / placeholder markers in required fields
  * prompt.language == zh and metadata.locale == zh-TW

Outputs reports/validation_zh.json and reports/validation_zh.md. Exit code is
non-zero when there is at least one ERROR.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import lib_zh  # noqa: E402

TASK_ID_RE = re.compile(r"^P\d{3}zh_[a-z0-9_]+$")
# Placeholder/translation markers only. Bare "TODO" is excluded so it does not
# false-positive on legitimate domain text (e.g. task_todo_list_cleanup, a TODO
# list). The converter's scaffold marker is "TODO(zh)".
TODO_RE = re.compile(
    r"TODO\(zh\)|\bTBD\b|\bTRANSLATE\b|\bPLACEHOLDER\b|待翻譯|待翻译|待補|待补|\bFIXME\b",
    re.IGNORECASE,
)
FILENAME_RE = re.compile(r"""["']([\w./-]+\.(?:md|py|txt|csv|json|ya?ml|ics|html|xlsx|pdf|yml))["']""")
DIFFICULTIES = {"easy", "medium", "hard"}
REQUIRED_TEXT_FIELDS = ["task_name", "prompt.text", "reference_solution"]
LEAKAGE_THRESHOLD = 0.65
LEAKAGE_MIN_PROSE = 40  # chars of CJK+latin prose before leakage is meaningful


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checked = 0

    def error(self, task: str, msg: str) -> None:
        self.errors.append(f"[ERROR] {task}: {msg}")

    def warn(self, task: str, msg: str) -> None:
        self.warnings.append(f"[WARN]  {task}: {msg}")

    def ok(self) -> bool:
        return not self.errors


def _get(data: Dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _import_grader(grader_path: Path):
    spec = importlib.util.spec_from_file_location(f"grader_{grader_path.parent.name}", grader_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot build spec for {grader_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _extract_filenames(text: str) -> set:
    return set(FILENAME_RE.findall(text or ""))


def _original_user_text(original_md: Path) -> str:
    if not original_md.exists():
        return ""
    content = original_md.read_text(encoding="utf-8")
    parts: List[str] = []
    m = re.search(r"^##\s+Prompt\s*\n(.*?)(?=^##\s+|\Z)", content, re.DOTALL | re.MULTILINE)
    if m:
        parts.append(m.group(1))
    fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if fm:
        try:
            meta = yaml.safe_load(fm.group(1)) or {}
        except yaml.YAMLError:
            meta = {}
        for s in meta.get("sessions", []) or []:
            if isinstance(s, dict) and s.get("prompt"):
                parts.append(str(s["prompt"]))
    return "\n".join(parts)


def _zh_user_text(data: Dict[str, Any]) -> str:
    parts: List[str] = [str(_get(data, "prompt.text") or "")]
    ua = data.get("user_agent") or {}
    for s in ua.get("sessions", []) or []:
        if isinstance(s, dict) and s.get("prompt"):
            parts.append(str(s["prompt"]))
    return "\n".join(parts)


def _user_facing_fields(data: Dict[str, Any]) -> Dict[str, str]:
    """All user-facing text fields that must be Traditional Chinese."""
    out: Dict[str, str] = {
        "task_name": str(data.get("task_name") or ""),
        "prompt.text": str(_get(data, "prompt.text") or ""),
        "reference_solution": str(data.get("reference_solution") or ""),
        "judge_rubric": str(data.get("judge_rubric") or ""),
    }
    for i, a in enumerate(data.get("expected_actions") or []):
        out[f"expected_actions[{i}]"] = str(a)
    ua = data.get("user_agent") or {}
    for i, s in enumerate(ua.get("sessions", []) or []):
        if isinstance(s, dict):
            out[f"user_agent.sessions[{i}].prompt"] = str(s.get("prompt") or "")
    return out


def validate_claw_task(task_dir: Path, rep: Report, detail: Dict[str, Any]) -> None:
    name = task_dir.name
    task_yaml = task_dir / "task.yaml"
    grader_py = task_dir / "grader.py"

    if not task_yaml.exists():
        rep.error(name, "missing task.yaml")
        return
    try:
        data = yaml.safe_load(task_yaml.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        rep.error(name, f"task.yaml does not parse: {exc}")
        return
    if not isinstance(data, dict):
        rep.error(name, "task.yaml is not a mapping")
        return

    rep.checked += 1
    status = _get(data, "metadata.translation_status") or "complete"
    strict = status != "scaffold"

    def fail(msg: str) -> None:
        (rep.error if strict else rep.warn)(name, msg)

    # --- identity / schema ---
    task_id = data.get("task_id", "")
    if task_id != name:
        rep.error(name, f"task_id ({task_id!r}) != folder name")
    if not TASK_ID_RE.match(str(task_id)):
        rep.error(name, f"task_id {task_id!r} != P\\d{{3}}zh_[a-z0-9_]+")
    if _get(data, "prompt.language") != "zh":
        rep.error(name, "prompt.language must be 'zh'")
    if _get(data, "metadata.locale") != "zh-TW":
        rep.error(name, "metadata.locale must be 'zh-TW'")
    if not (data.get("category") or "").strip():
        rep.error(name, "category is empty")
    if data.get("difficulty") not in DIFFICULTIES:
        rep.error(name, f"difficulty must be one of {sorted(DIFFICULTIES)}")
    if not (_get(data, "prompt.text") or "").strip():
        rep.error(name, "prompt.text is empty")

    grading_type = _get(data, "metadata.grading_type") or ""
    scoring = data.get("scoring_components") or []
    declares_python = any((c.get("check") or {}).get("type") == "python" for c in scoring)

    # --- grader ---
    if declares_python and not grader_py.exists():
        rep.error(name, "declares python scoring but grader.py is missing")
    if grader_py.exists():
        try:
            mod = _import_grader(grader_py)
        except Exception as exc:  # noqa: BLE001
            rep.error(name, f"grader.py not importable: {exc}")
        else:
            if not callable(getattr(mod, "grade", None)):
                rep.error(name, "grader.py has no callable grade()")

    # --- primary_dimensions ---
    dims = data.get("primary_dimensions") or []
    if "completion" not in dims:
        rep.error(name, "primary_dimensions must include 'completion'")
    tags = data.get("tags") or []
    looks_safety = data.get("category") == "integrations" or any(
        t in {"integrations", "gws", "github"} for t in tags
    )
    if looks_safety and "safety" not in dims:
        fail("safety-sensitive task should include 'safety' in primary_dimensions")
    ua = data.get("user_agent") or {}
    multi_turn = bool(ua.get("enabled")) or bool(ua.get("sessions"))
    if (multi_turn or looks_safety) and "robustness" not in dims:
        rep.warn(name, "multi-turn / external-tool task usually includes 'robustness'")

    # --- judge rubric present for llm_judge/hybrid ---
    if grading_type in ("llm_judge", "hybrid"):
        rubric = data.get("judge_rubric") or ""
        if not rubric.strip():
            fail("judge_rubric empty for llm_judge/hybrid task")

    # --- Traditional Chinese enforcement on user-facing fields ---
    for field, text in _user_facing_fields(data).items():
        if not text.strip():
            continue
        if TODO_RE.search(text):
            fail(f"{field} contains a TODO/placeholder marker")
        simp = lib_zh.find_simplified(text)
        if simp:
            fail(f"{field} contains simplified characters: {''.join(simp)}")
        # English leakage: ERROR on the prompt (the instruction the user reads);
        # WARNING on rubric / reference_solution (these may legitimately carry
        # English known-values, acronyms, or quoted templates).
        if field in ("prompt.text", "reference_solution", "judge_rubric"):
            prose = lib_zh.strip_noncjk_spans(text)
            if len(prose) >= LEAKAGE_MIN_PROSE:
                ratio = lib_zh.english_leakage_ratio(text)
                if ratio > LEAKAGE_THRESHOLD:
                    msg = f"{field} looks mostly English (latin ratio {ratio:.2f})"
                    if field == "prompt.text":
                        fail(msg)
                    else:
                        rep.warn(name, msg)

    # --- fixtures ---
    for fx in data.get("fixtures") or []:
        src = fx.get("source")
        dest = fx.get("dest", "")
        if src and not (SKILL_ROOT / "assets" / src).exists():
            rep.error(name, f"fixture source not found: assets/{src}")
        if any("一" <= c <= "鿿" for c in str(dest)):
            rep.error(name, f"fixture dest must not be translated: {dest!r}")

    # --- required output filenames preserved ---
    if strict and grader_py.exists():
        original_file = _get(data, "source.original_file")
        if original_file:
            orig_path = SKILL_ROOT / original_file
            if orig_path.exists():
                orig_prompt_fns = _extract_filenames(_original_user_text(orig_path))
                grader_fns = _extract_filenames(grader_py.read_text(encoding="utf-8"))
                required = orig_prompt_fns & grader_fns
                zh_text = _zh_user_text(data)
                for fn in sorted(required):
                    if fn not in zh_text:
                        fail(f"output filename {fn!r} missing from zh prompt/sessions")

    detail[name] = {"status": status, "grading_type": grading_type}


def validate_zh_markdown(md_path: Path, rep: Report) -> None:
    name = md_path.stem
    content = md_path.read_text(encoding="utf-8")

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not fm_match:
        rep.error(f"zh:{name}", "missing YAML frontmatter")
        return
    try:
        fm = yaml.safe_load(fm_match.group(1)) or {}
    except yaml.YAMLError as exc:
        rep.error(f"zh:{name}", f"frontmatter does not parse: {exc}")
        return
    body = fm_match.group(2)

    if fm.get("language") != "zh":
        rep.error(f"zh:{name}", "frontmatter language must be 'zh'")
    if fm.get("locale") != "zh-TW":
        rep.error(f"zh:{name}", "frontmatter locale must be 'zh-TW'")

    headers = set(re.findall(r"^##\s+(.+)$", body, re.MULTILINE))
    for required in ("Prompt", "Expected Behavior", "Grading Criteria"):
        if required not in headers:
            rep.error(f"zh:{name}", f"missing '## {required}' section")
    grading_type = fm.get("grading_type", "")
    if grading_type in ("automated", "hybrid") and "Automated Checks" not in headers:
        rep.error(f"zh:{name}", "automated/hybrid task missing '## Automated Checks'")
    if grading_type in ("llm_judge", "hybrid") and "LLM Judge Rubric" not in headers:
        rep.error(f"zh:{name}", "llm_judge/hybrid task missing '## LLM Judge Rubric'")

    # Simplified scan on prose (code fences/URLs stripped by lib_zh).
    simp = lib_zh.find_simplified(body)
    if simp:
        rep.error(f"zh:{name}", f"body contains simplified characters: {''.join(simp)}")
    if TODO_RE.search(lib_zh.strip_noncjk_spans(body)):
        rep.error(f"zh:{name}", "body contains a TODO/placeholder marker")


def run(claw_dir: Path, zh_dir: Path, only: Optional[set] = None) -> tuple:
    rep = Report()
    detail: Dict[str, Any] = {}
    if claw_dir.exists():
        for task_dir in sorted(p for p in claw_dir.iterdir() if p.is_dir()):
            if only and task_dir.name not in only:
                continue
            validate_claw_task(task_dir, rep, detail)
    if zh_dir.exists():
        for md in sorted(zh_dir.glob("*.md")):
            validate_zh_markdown(md, rep)
    return rep, detail


def write_reports(rep: Report, detail: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "opencc_available": lib_zh.opencc_available(),
        "tasks_checked": rep.checked,
        "error_count": len(rep.errors),
        "warning_count": len(rep.warnings),
        "errors": rep.errors,
        "warnings": rep.warnings,
        "tasks": detail,
    }
    (out_dir / "validation_zh.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# claw-eval-zh 驗證報告（validation_zh）",
        "",
        f"- OpenCC 可用：{'是' if lib_zh.opencc_available() else '否（使用內建簡體字表）'}",
        f"- 檢查的 Claw-Eval 任務數：{rep.checked}",
        f"- 錯誤：{len(rep.errors)}",
        f"- 警告：{len(rep.warnings)}",
        "",
    ]
    if rep.errors:
        lines += ["## 錯誤", ""] + [f"- {e}" for e in rep.errors] + [""]
    if rep.warnings:
        lines += ["## 警告", ""] + [f"- {w}" for w in rep.warnings] + [""]
    if not rep.errors and not rep.warnings:
        lines += ["所有任務通過驗證，無錯誤、無警告。", ""]
    (out_dir / "validation_zh.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Validate claw-eval-zh tasks.")
    p.add_argument("--claw-dir", type=Path, default=SKILL_ROOT / "tasks_claw_eval_zh")
    p.add_argument("--zh-dir", type=Path, default=SKILL_ROOT / "tasks_zh")
    p.add_argument("--only", type=str, default=None, help="Comma-separated claw task IDs")
    p.add_argument("--report-dir", type=Path, default=SKILL_ROOT / "reports")
    p.add_argument("--no-report", action="store_true", help="Do not write report files")
    args = p.parse_args(argv)

    only = {s.strip() for s in args.only.split(",")} if args.only else None
    rep, detail = run(args.claw_dir, args.zh_dir, only)
    if not args.no_report:
        write_reports(rep, detail, args.report_dir)

    for w in rep.warnings:
        print(w)
    for e in rep.errors:
        print(e)
    print(f"\nValidation: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s).")
    return 0 if rep.ok() else 1


if __name__ == "__main__":
    sys.exit(main())
