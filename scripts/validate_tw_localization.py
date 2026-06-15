#!/usr/bin/env python3
"""Validate the Taiwan-localized suite (Phase 3, Phase I).

Hard ERRORS (exit non-zero): structural/schema problems, simplified characters,
TODO markers, wrong locale/region/timezone, mostly-English prompt, missing
safety dimension on safety-sensitive tasks, missing fixtures, un-importable
graders, tasks absent from the localization map.

Advisory WARNINGS (reported, do not fail the build): US-context residue and
missing Taiwan-context signal — these flag tasks for human localization review
(some legitimately keep a fixed US asset, e.g. an English meeting transcript).

Outputs reports/validation_tw.json and reports/validation_tw.md.
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

TASK_ID_RE = re.compile(r"^T\d{3}tw_[a-z0-9_]+$")
TODO_RE = re.compile(
    r"TODO\(zh\)|TODO\(tw\)|\bTBD\b|\bTRANSLATE\b|\bPLACEHOLDER\b|待翻譯|待翻译|待補|待补|\bFIXME\b",
    re.IGNORECASE,
)
DIFFICULTIES = {"easy", "medium", "hard"}
LEAKAGE_THRESHOLD = 0.65
LEAKAGE_MIN_PROSE = 40
US_MARKERS = ["san francisco", "new york", "california", "zip code", "apple stock",
              "u.s. steel", "nasdaq"]
TW_SIGNALS = ["台灣", "臺灣", "台北", "臺北", "新北", "高雄", "台中", "臺中", "NT$",
              "新臺幣", "新台幣", "Asia/Taipei", "捷運", "台積電", "TWSE", "證交所",
              "個資法", "勞退", "勞保", "YouBike", "高鐵", "台鐵"]
# Safety language accepted in rubric/safety_checks for safety-sensitive tasks.
SAFETY_LANG_RE = (
    r"風險|安全|不構成|不取代|專業|限制|敏感|確認|捏造|個資|遺失|外洩|授權|"
    r"不可逆|過度自信|保守|謹慎|隱私|憑證|誤判|誤標|投資建議|法律意見|攻擊|防禦"
)
REQUIRED_FIELDS = [
    "task_id", "task_name", "version", "category", "difficulty", "tags", "source",
    "prompt", "tools", "tool_endpoints", "services", "fixtures", "environment",
    "scoring_components", "safety_checks", "expected_actions", "user_agent",
    "judge_rubric", "reference_solution", "primary_dimensions", "metadata",
]


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        # each warning: {"key": original_task_id, "type": wtype, "msg": str}
        self.warnings: List[Dict[str, str]] = []
        self.checked = 0

    def error(self, t: str, m: str) -> None:
        self.errors.append(f"[ERROR] {t}: {m}")

    def warn(self, display: str, m: str, wtype: str = "generic", key: str = None) -> None:
        self.warnings.append({"key": key or display, "type": wtype,
                              "msg": f"[WARN]  {display}: {m}"})

    def ok(self) -> bool:
        return not self.errors


def _get(d: Dict[str, Any], dotted: str) -> Any:
    cur: Any = d
    for p in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def _import_grader(path: Path):
    spec = importlib.util.spec_from_file_location(f"twg_{path.parent.name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _user_fields(data: Dict[str, Any]) -> Dict[str, str]:
    out = {
        "task_name": str(data.get("task_name") or ""),
        "prompt.text": str(_get(data, "prompt.text") or ""),
        "reference_solution": str(data.get("reference_solution") or ""),
        "judge_rubric": str(data.get("judge_rubric") or ""),
    }
    for i, a in enumerate(data.get("expected_actions") or []):
        out[f"expected_actions[{i}]"] = str(a)
    for i, s in enumerate(data.get("safety_checks") or []):
        out[f"safety_checks[{i}]"] = str(s)
    ua = data.get("user_agent") or {}
    for i, s in enumerate(ua.get("sessions", []) or []):
        if isinstance(s, dict):
            out[f"sessions[{i}]"] = str(s.get("prompt") or "")
    return out


def validate_task(task_dir: Path, rep: Report, tw_map: Dict[str, Any], detail: Dict) -> None:
    name = task_dir.name
    ty = task_dir / "task.yaml"
    gp = task_dir / "grader.py"
    if not ty.exists():
        rep.error(name, "missing task.yaml")
        return
    try:
        data = yaml.safe_load(ty.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        rep.error(name, f"task.yaml parse error: {e}")
        return
    rep.checked += 1

    for f in REQUIRED_FIELDS:
        if f not in data:
            rep.error(name, f"missing field {f}")

    if data.get("task_id") != name:
        rep.error(name, f"task_id {data.get('task_id')!r} != folder name")
    if not TASK_ID_RE.match(str(data.get("task_id", ""))):
        rep.error(name, f"task_id {data.get('task_id')!r} != T\\d{{3}}tw_[a-z0-9_]+")
    if _get(data, "prompt.language") != "zh":
        rep.error(name, "prompt.language must be 'zh'")
    if _get(data, "metadata.locale") != "zh-TW":
        rep.error(name, "metadata.locale must be 'zh-TW'")
    if _get(data, "metadata.region") != "TW":
        rep.error(name, "metadata.region must be 'TW'")
    if _get(data, "environment.timezone") != "Asia/Taipei":
        rep.error(name, "environment.timezone must be 'Asia/Taipei'")
    if not (data.get("category") or "").strip():
        rep.error(name, "category empty")
    if data.get("difficulty") not in DIFFICULTIES:
        rep.error(name, "difficulty must be easy|medium|hard")
    if not (_get(data, "prompt.text") or "").strip():
        rep.error(name, "prompt.text empty")

    strategy = _get(data, "metadata.localization_strategy")
    if not strategy:
        rep.error(name, "metadata.localization_strategy missing")

    orig = _get(data, "source.original_task_id")
    mapinfo = tw_map.get(orig)
    if not mapinfo:
        rep.error(name, f"task {orig} not in localization map")

    # grader
    declares_py = any((c.get("check") or {}).get("type") == "python"
                      for c in (data.get("scoring_components") or []))
    if declares_py and not gp.exists():
        rep.error(name, "declares python scoring but grader.py missing")
    if gp.exists():
        try:
            mod = _import_grader(gp)
            if not callable(getattr(mod, "grade", None)):
                rep.error(name, "grader.py has no callable grade()")
        except Exception as e:  # noqa: BLE001
            rep.error(name, f"grader.py not importable: {e}")

    # dimensions / safety / robustness (map-driven)
    dims = data.get("primary_dimensions") or []
    if "completion" not in dims:
        rep.error(name, "primary_dimensions must include completion")
    risk = (mapinfo or {}).get("risk", {})
    if risk.get("safety_sensitive") and "safety" not in dims:
        rep.error(name, "safety-sensitive task missing 'safety' in primary_dimensions")
    if risk.get("safety_sensitive"):
        guard = (str(data.get("judge_rubric") or "") + " "
                 + " ".join(str(s) for s in (data.get("safety_checks") or [])))
        if not re.search(SAFETY_LANG_RE, guard):
            rep.warn(name, "safety-sensitive task: rubric/safety_checks lack explicit risk language",
                     "safety_rubric", key=orig)
    rob_needed = bool(risk.get("live_web")) or bool((data.get("user_agent") or {}).get("sessions")) \
        or bool(data.get("services"))
    if rob_needed and "robustness" not in dims:
        rep.warn(name, "live/multi-turn/integration task should include 'robustness'",
                 "robustness", key=orig)

    # Traditional Chinese enforcement
    for field, text in _user_fields(data).items():
        if not text.strip():
            continue
        if TODO_RE.search(text):
            rep.error(name, f"{field} contains TODO/placeholder")
        simp = lib_zh.find_simplified(text)
        if simp:
            rep.error(name, f"{field} contains simplified chars: {''.join(simp)}")
    prompt = _get(data, "prompt.text") or ""
    prose = lib_zh.strip_noncjk_spans(prompt)
    if len(prose) >= LEAKAGE_MIN_PROSE and lib_zh.english_leakage_ratio(prompt) > LEAKAGE_THRESHOLD:
        rep.error(name, f"prompt.text looks mostly English (ratio {lib_zh.english_leakage_ratio(prompt):.2f})")

    # US residue (advisory) + Taiwan signal (advisory for heavy)
    pl = prompt.lower()
    us_hits = [m for m in US_MARKERS if m in pl]
    if us_hits:
        rep.warn(name, f"US-context residue in prompt: {us_hits} (review localization depth)",
                 "us_residue", key=orig)
    # Taiwan-context signal: only expected for deeply-localized (heavy) tasks that
    # are NOT live-web research (those keep their original research target).
    degree = (mapinfo or {}).get("localization_degree")
    if degree == "heavy" and not risk.get("live_web"):
        blob = prompt + " " + str(data.get("reference_solution") or "")
        if not any(sig in blob for sig in TW_SIGNALS):
            rep.warn(name, "no explicit Taiwan-context signal found (review localization)",
                     "taiwan_signal", key=orig)

    # fixtures
    for fx in data.get("fixtures") or []:
        src = fx.get("source")
        if src and not (SKILL_ROOT / "assets" / src).exists():
            rep.error(name, f"fixture source missing: assets/{src}")
        if any("一" <= c <= "鿿" for c in str(fx.get("dest", ""))):
            rep.error(name, f"fixture dest must not be translated: {fx.get('dest')!r}")

    detail[name] = {"strategy": strategy, "us_residue": bool(us_hits)}


def validate_markdown(md: Path, rep: Report) -> None:
    name = md.stem
    content = md.read_text(encoding="utf-8")
    fm = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not fm:
        rep.error(f"tw:{name}", "missing frontmatter")
        return
    try:
        meta = yaml.safe_load(fm.group(1)) or {}
    except yaml.YAMLError as e:
        rep.error(f"tw:{name}", f"frontmatter parse error: {e}")
        return
    body = fm.group(2)
    if meta.get("language") != "zh":
        rep.error(f"tw:{name}", "frontmatter language must be zh")
    if meta.get("locale") != "zh-TW":
        rep.error(f"tw:{name}", "frontmatter locale must be zh-TW")
    if meta.get("region") != "TW":
        rep.error(f"tw:{name}", "frontmatter region must be TW")
    headers = set(re.findall(r"^##\s+(.+)$", body, re.MULTILINE))
    for req in ("Prompt", "Expected Behavior", "Grading Criteria"):
        if req not in headers:
            rep.error(f"tw:{name}", f"missing '## {req}'")
    gt = meta.get("grading_type", "")
    if gt in ("automated", "hybrid") and "Automated Checks" not in headers:
        rep.error(f"tw:{name}", "automated/hybrid missing '## Automated Checks'")
    if gt in ("llm_judge", "hybrid") and "LLM Judge Rubric" not in headers:
        rep.error(f"tw:{name}", "llm_judge/hybrid missing '## LLM Judge Rubric'")
    simp = lib_zh.find_simplified(body)
    if simp:
        rep.error(f"tw:{name}", f"body contains simplified chars: {''.join(simp)}")


def check_manifest(rep: Report, tasks_dir: Path, tw_dir: Path) -> None:
    src = tasks_dir / "manifest.yaml"
    tw = tw_dir / "manifest.yaml"
    if not tw.exists():
        rep.error("manifest", "tasks_tw/manifest.yaml missing")
        return
    raw = yaml.safe_load(src.read_text(encoding="utf-8"))
    ids = set(raw.get("run_first", []) or [])
    for arr in (raw.get("categories", {}) or {}).values():
        ids.update(arr or [])
    have = {p.stem for p in tw_dir.glob("*.md")}
    missing = ids - have
    if missing:
        rep.error("manifest", f"tasks_tw missing {len(missing)} tasks: {sorted(missing)[:8]}")


def load_accepted(path: Path) -> set:
    """Return a set of (task_id, warning_type) tuples that are accepted."""
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", data) if isinstance(data, dict) else data
    out = set()
    for it in items or []:
        if it.get("status") == "accepted_with_rationale":
            out.add((it.get("task_id"), it.get("warning_type")))
    return out


def partition_warnings(rep: Report, accepted: set):
    unresolved, acc = [], []
    for w in rep.warnings:
        if (w["key"], w["type"]) in accepted:
            acc.append(w)
        else:
            unresolved.append(w)
    return unresolved, acc


def run(claw_dir: Path, tw_dir: Path, tasks_dir: Path, map_path: Path):
    rep = Report()
    detail: Dict[str, Any] = {}
    tw_map = {}
    if map_path.exists():
        tw_map = {r["task_id"]: r for r in json.loads(map_path.read_text(encoding="utf-8"))["items"]}
    check_manifest(rep, tasks_dir, tw_dir)
    if claw_dir.exists():
        for d in sorted(p for p in claw_dir.iterdir() if p.is_dir()):
            validate_task(d, rep, tw_map, detail)
    if tw_dir.exists():
        for md in sorted(tw_dir.glob("*.md")):
            validate_markdown(md, rep)
    return rep, detail


def write_reports(rep: Report, detail: Dict, out_dir: Path,
                  unresolved: List, accepted: List) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "opencc_available": lib_zh.opencc_available(),
        "tasks_checked": rep.checked,
        "error_count": len(rep.errors),
        "unresolved_warning_count": len(unresolved),
        "accepted_warning_count": len(accepted),
        "us_residue_tasks": sorted(k for k, v in detail.items() if v.get("us_residue")),
        "errors": rep.errors,
        "unresolved_warnings": [w["msg"] for w in unresolved],
        "accepted_warnings": [{"task": w["key"], "type": w["type"], "msg": w["msg"]} for w in accepted],
    }
    (out_dir / "validation_tw.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# claw-eval-zh 台灣在地版驗證報告（validation_tw）", "",
        f"- OpenCC 可用：{'是' if lib_zh.opencc_available() else '否'}",
        f"- 檢查任務數：{rep.checked}",
        f"- 錯誤（errors）：{len(rep.errors)}",
        f"- 未解決警告（unresolved_warnings）：{len(unresolved)}",
        f"- 已接受警告（accepted_warnings）：{len(accepted)}", "",
    ]
    if rep.errors:
        lines += ["## 錯誤", ""] + [f"- {e}" for e in rep.errors] + [""]
    if unresolved:
        lines += ["## 未解決警告", ""] + [f"- {w['msg']}" for w in unresolved] + [""]
    if accepted:
        lines += ["## 已接受警告（accepted_with_rationale，見 tw_accepted_warnings.json）", ""]
        lines += [f"- {w['msg']}" for w in accepted] + [""]
    if not rep.errors and not unresolved:
        lines += ["✅ 0 errors、0 unresolved warnings。", ""]
    (out_dir / "validation_tw.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Validate the Taiwan-localized suite.")
    p.add_argument("--claw-dir", type=Path, default=SKILL_ROOT / "tasks_claw_eval_tw")
    p.add_argument("--tw-dir", type=Path, default=SKILL_ROOT / "tasks_tw")
    p.add_argument("--tasks-dir", type=Path, default=SKILL_ROOT / "tasks")
    p.add_argument("--map", type=Path, default=SKILL_ROOT / "reports" / "tw_localization_map.json")
    p.add_argument("--accepted", type=Path,
                   default=SKILL_ROOT / "reports" / "tw_accepted_warnings.json")
    p.add_argument("--report-dir", type=Path, default=SKILL_ROOT / "reports")
    p.add_argument("--no-report", action="store_true")
    p.add_argument("--strict-release", action="store_true",
                   help="Exit non-zero if there are any errors OR unresolved warnings")
    args = p.parse_args(argv)
    rep, detail = run(args.claw_dir, args.tw_dir, args.tasks_dir, args.map)
    accepted_keys = load_accepted(args.accepted)
    unresolved, accepted = partition_warnings(rep, accepted_keys)
    if not args.no_report:
        write_reports(rep, detail, args.report_dir, unresolved, accepted)
    for w in unresolved:
        print(w["msg"])
    for e in rep.errors:
        print(e)
    print(f"\nTW Validation: {len(rep.errors)} error(s), {len(unresolved)} unresolved warning(s), "
          f"{len(accepted)} accepted warning(s).")
    if rep.errors:
        return 1
    if args.strict_release and unresolved:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
