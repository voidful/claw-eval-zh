#!/usr/bin/env python3
"""Build the Taiwan-localization classification map (Phase 3, Phase B).

Deterministically proposes a localization strategy for every PinchBench task,
so a human can review reports/tw_localization_map.json BEFORE the full Phase D/E
conversion runs. NO files are translated here — this only classifies.

Strategies (see docs/taiwan_localization_policy.md):
  copy | language_polish | context_replace | fixture_replace
  | new_tw_variant | manual_review_only

Usage:
  python scripts/build_tw_localization_map.py            # write the map
  python scripts/build_tw_localization_map.py --dry-run  # print summary only
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("tw-map")

from lib_tasks import Task, TaskLoader  # noqa: E402
import convert_pinchbench_to_claw_eval_zh as C  # noqa: E402

DEGREE = {
    "copy": "none",
    "language_polish": "light",
    "context_replace": "medium",
    "fixture_replace": "heavy",
    "new_tw_variant": "heavy",
    "manual_review_only": "heavy",
}

# Keyword sets are intentionally narrow: broad words ("ratio", bare "security")
# caused false positives (statistical ratios in GDP/density tasks; incidental
# "security" mentions in apache/syslog logs). The two anchor tasks that those
# words targeted (financial_ratio_calculation, cve_security_triage) are handled
# explicitly in ANCHORS, so narrowing here is safe.
FINANCE_KW = ["finance", "financial", "stock", "stocks", "pension", "mortgage",
              "loan", "invoice", "expense", "earnings", "valuation", "revenue"]
LEGAL_KW = ["contract", "legal", "lawsuit", "regulation", "compliance", "gdpr"]
# NOTE (Phase 4 review): "vulnerability" removed — it false-positived on the
# GitLab product feature "vulnerability management" in meeting transcripts and on
# an Apache "vulnerability scanning" log line, none of which are security-
# OPERATIONAL tasks. Genuine security tasks still match via cve/credential/brute/
# exploit/malware (cve_security_triage, apache_critical, ssh_*, syslog_*).
SECURITY_KW = ["cve", "credential", "credentials", "brute", "exploit", "malware"]

# Anchor tasks (Phase F) — deep localization, explicit strategy.
ANCHORS: Dict[str, Dict[str, Any]] = {
    "task_sanity": dict(strategy="language_polish", reason="冒煙測試；只潤飾為台灣自然用語，grader 不變"),
    "task_calendar": dict(strategy="context_replace", grader=True,
                          reason="改台灣工作語境＋Asia/Taipei；若產生 ICS 需檢查非美國時區"),
    "task_weather": dict(strategy="context_replace", grader=True,
                         reason="地點改台北；保留 weather.py 與 wttr.in；grader 檢查 Taipei|台北|臺北"),
    "task_csv_stock_trend": dict(strategy="fixture_replace", fixture=True, grader=True, recalc=True,
                                 reason="改台灣股票/ETF fixture（0050/2330），重算 expected values 與 grader"),
    "task_csv_cities_filter": dict(strategy="fixture_replace", fixture=True, grader=True, recalc=True,
                                   reason="改台灣縣市 fixture（tw_cities.csv），重寫 5 項篩選與 grader（Phase 4）"),
    "task_financial_ratio_calculation": dict(strategy="fixture_replace", fixture=True, grader=True,
                                             recalc=True, safety=True,
                                             reason="改台灣上市櫃公司財報 fixture；rubric 扣分過度推銷/未提醒風險"),
    "task_contract_analysis": dict(strategy="context_replace", safety=True,
                                   reason="繁中合約審閱；不得提供法律定論，rubric 要求列出疑義/風險/需詢問律師"),
    "task_email": dict(strategy="context_replace", safety=True,
                       reason="台灣商務 Email 語氣；rubric 評估是否適合台灣職場"),
    "task_email_reply_drafting": dict(strategy="context_replace", safety=True,
                                      reason="台灣商務回信語氣；保留原信語言處理"),
    "task_subway_navigation": dict(strategy="context_replace",
                                   reason="改台北/高雄捷運；給定固定站點，不依賴即時營運"),
    "task_meeting_council_votes": dict(strategy="new_tw_variant",
                                       reason="改台灣（虛構）地方議會語境；避免捏造真實機關資料"),
    "task_meeting_tech_action_items": dict(strategy="new_tw_variant",
                                           reason="改台灣公司會議語境；評估待辦抽取"),
    "task_meeting_gov_next_steps": dict(strategy="new_tw_variant",
                                        reason="改台灣（虛構）政府會議語境；評估後續步驟抽取"),
    "task_cve_security_triage": dict(strategy="manual_review_only", security=True, safety=True,
                                     reason="保留 CVE 技術語境；加入台灣企業 IT 通報/修補優先；不要求 exploit"),
    "task_byok_best_practices": dict(strategy="manual_review_only", legal=True, safety=True,
                                     reason="可用台灣個資法/資安合規為背景；除非有 frozen reference 否則不宣稱法規細節"),
}


def _kw(task: Task, kws: List[str]) -> bool:
    blob = (task.task_id + " " + task.prompt + " " + task.expected_behavior).lower()
    return any(C._word_match(blob, [k]) for k in kws)


def classify(task: Task) -> Dict[str, Any]:
    tid = task.task_id
    cat = task.category
    safety = C.is_safety_sensitive(task)
    live = C.is_live_web(task)
    ext = C.is_external_service(task)
    finance = _kw(task, FINANCE_KW)
    legal = _kw(task, LEGAL_KW)
    security = _kw(task, SECURITY_KW)

    entry: Dict[str, Any] = {
        "strategy": None, "fixture": False, "grader": False, "recalc": False,
        "safety": safety, "live": live, "legal": legal, "finance": finance,
        "security": security, "reason": "",
    }

    if tid in ANCHORS:
        a = ANCHORS[tid]
        entry.update(strategy=a["strategy"], reason=a.get("reason", ""))
        entry["fixture"] = a.get("fixture", False)
        entry["grader"] = a.get("grader", False)
        entry["recalc"] = a.get("recalc", False)
        entry["safety"] = a.get("safety", safety)
        entry["legal"] = a.get("legal", legal)
        entry["security"] = a.get("security", security)
        entry["anchor"] = True
        return entry

    entry["anchor"] = False
    # General category rules (deterministic).
    if ext:
        entry.update(strategy="context_replace", safety=True,
                     reason="外部服務 / mock；改台灣職場語境，保留 mock 語意")
    elif live:
        entry.update(strategy="manual_review_only",
                     reason="依賴即時網路資料；在地化框架但保留 live，需人工確認可重現性")
    elif cat == "csv_analysis":
        if "stock" in tid:
            entry.update(strategy="fixture_replace", fixture=True, grader=True, recalc=True,
                         reason="股票資料可改台灣標的；需新 fixture 並重算 expected values")
        elif finance:
            entry.update(strategy="copy", safety=True,
                         reason="美國金融資料（如退休金）；保留資料避免重算錯誤，未來可改台灣勞退 fixture（manual review）")
        else:
            entry.update(strategy="copy",
                         reason="全球/科學資料集（GDP/氣溫/壽命/iris/城市/測站）；在地化會破壞 fixture，保留資料、維持繁中 prompt")
    elif cat == "log_analysis":
        entry.update(strategy="copy",
                     reason="技術日誌（IP/timestamp）；在地化會破壞 fixture，保留資料、維持繁中 prompt")
    elif cat == "coding":
        entry.update(strategy="language_polish",
                     reason="技術編碼任務；潤飾為台灣自然用語，程式碼/檔名/指令不動")
    elif cat == "meeting_analysis":
        entry.update(strategy="context_replace",
                     reason="會議分析；prompt 改台灣語境，英文 transcript 為固定 fixture（指示處理原文）")
    elif cat == "writing":
        if tid in ("task_blog", "task_readme_generation", "task_commit_message_writer"):
            entry.update(strategy="language_polish",
                         reason="英文輸出寫作任務；保留英文輸出要求，僅潤飾指令為台灣用語")
        else:
            entry.update(strategy="context_replace",
                         reason="寫作任務改台灣語境")
    elif safety or finance or legal or security:
        entry.update(strategy="context_replace", safety=True,
                     reason="安全敏感領域；改台灣語境並強化 safety rubric")
    elif cat in ("productivity", "memory", "skills", "analysis"):
        entry.update(strategy="context_replace",
                     reason="改台灣語境（地點/人名/公司/格式）；核心資料不變")
    else:
        entry.update(strategy="language_polish", reason="潤飾為台灣自然用語")
    return entry


def severity(entry: Dict[str, Any]) -> str:
    if (entry["safety"] or entry["legal"] or entry["finance"] or entry["security"]
            or entry["live"] or entry["fixture"] or entry["recalc"]):
        return "high"
    if entry["strategy"] in ("context_replace", "new_tw_variant") or entry["grader"]:
        return "medium"
    return "low"


def build_map(tasks: List[Task]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, task in enumerate(tasks):
        e = classify(task)
        claw_id = f"T{i + 1:03d}tw_{C.slugify_task_id(task.task_id)}"
        sev = severity(e)
        mr_required = sev in ("high", "medium") or e["strategy"] == "manual_review_only"
        out.append({
            "task_id": task.task_id,
            "tw_task_id": task.task_id,
            "claw_eval_tw_id": claw_id,
            "source_task_id": task.task_id,
            "source_locale": "zh-TW",
            "target_locale": "zh-TW",
            "category": task.category,
            "grading_type": task.grading_type,
            "localization_strategy": e["strategy"],
            "localization_degree": DEGREE[e["strategy"]],
            "anchor": e["anchor"],
            "taiwan_context": {"timezone": "Asia/Taipei", "region": "TW"},
            "fixture_changes": {"required": e["fixture"], "files": []},
            "grader_changes": {"required": e["grader"] or e["recalc"],
                               "reason": "重算 expected values" if e["recalc"] else (
                                   "新增台灣關鍵詞 regex" if e["grader"] else "")},
            "expected_value_recalculation": {"required": e["recalc"],
                                             "method": "由程式從新 fixture 重算" if e["recalc"] else ""},
            "risk": {
                "safety_sensitive": bool(e["safety"]),
                "live_web": bool(e["live"]),
                "legal_or_financial": bool(e["legal"] or e["finance"]),
                "security_sensitive": bool(e["security"]),
            },
            "manual_review": {"required": mr_required, "severity": sev, "reason": e["reason"]},
        })
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build TW localization map (Phase 3 B).")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--tasks-dir", type=Path, default=SKILL_ROOT / "tasks")
    p.add_argument("--out", type=Path, default=SKILL_ROOT / "reports" / "tw_localization_map.json")
    args = p.parse_args(argv)

    tasks = TaskLoader(args.tasks_dir).load_all_tasks()
    rows = build_map(tasks)

    from collections import Counter
    strat = Counter(r["localization_strategy"] for r in rows)
    deg = Counter(r["localization_degree"] for r in rows)
    sev = Counter(r["manual_review"]["severity"] for r in rows)
    summary = {
        "total_tasks": len(rows),
        "localization_strategy_counts": dict(strat),
        "localization_degree_counts": dict(deg),
        "manual_review_severity_counts": dict(sev),
        "anchor_tasks": [r["task_id"] for r in rows if r["anchor"]],
        "fixture_replace_tasks": [r["task_id"] for r in rows
                                  if r["localization_strategy"] == "fixture_replace"],
        "items": rows,
    }
    logger.info("strategies: %s", dict(strat))
    logger.info("degrees: %s", dict(deg))
    logger.info("review severity: %s", dict(sev))
    logger.info("anchors: %d", len(summary["anchor_tasks"]))
    if not args.dry_run:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("wrote %s", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
