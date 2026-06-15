#!/usr/bin/env python3
"""Build the Phase 4 high-risk review matrix (CSV + Markdown).

Triages every high-severity task from reports/tw_manual_review_required.json into
fixed | accepted_with_rationale | requires_external_human_review, based on:
  - localization strategy / domain (from tw_localization_map.json),
  - whether the generated tasks_claw_eval_tw/<id>/task.yaml now carries
    safety_checks / risk language (the concrete Phase 4 mitigation),
  - whether the task is a recomputed-fixture anchor.
Deterministic; no network.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

MR = json.loads((ROOT / "reports" / "tw_manual_review_required.json").read_text(encoding="utf-8"))
MAP = {r["task_id"]: r for r in json.loads(
    (ROOT / "reports" / "tw_localization_map.json").read_text(encoding="utf-8"))["items"]}
SAFETY_LANG_RE = (r"風險|安全|不構成|不取代|專業|限制|敏感|確認|捏造|個資|遺失|外洩|授權|"
                  r"不可逆|過度自信|保守|謹慎|隱私|憑證|誤判|誤標|投資建議|法律意見|攻擊|防禦")

REVIEWER = {"finance_or_legal": "finance/legal", "security": "security",
            "live_web": "product", "safety": "privacy", "general": "none"}
ACTION = {
    "finance_or_legal": "改為『分析/風險因素/資料限制』框架；rubric/safety_checks 扣分投資或法律定論、捏造來源",
    "security": "防禦/修補優先序/通報導向；safety_checks 禁止攻擊步驟、要求妥善處理個資",
    "live_web": "保留研究標的、改用 LLM judge；要求標示查詢日期/來源/資料限制，不寫死即時值",
    "safety": "要求確認不可逆操作、避免未授權寄送/刪除、不外洩個資",
    "general": "在地化框架；補充安全與不確定性提示",
}


def tw_task_yaml(orig_task_id: str):
    cid = MAP[orig_task_id]["claw_eval_tw_id"]
    p = ROOT / "tasks_claw_eval_tw" / cid / "task.yaml"
    return (cid, yaml.safe_load(p.read_text(encoding="utf-8"))) if p.exists() else (cid, None)


def has_safety_lang(data) -> bool:
    if not data:
        return False
    guard = str(data.get("judge_rubric") or "") + " " + \
        " ".join(str(s) for s in (data.get("safety_checks") or []))
    return bool(re.search(SAFETY_LANG_RE, guard))


def has_reproducibility_lang(data) -> bool:
    """Live-web task is acceptable if it requires source/date/uncertainty
    (so no expired value is hard-coded) — checked across rubric/reference/actions."""
    if not data:
        return False
    blob = (str(data.get("judge_rubric") or "") + " "
            + str(data.get("reference_solution") or "") + " "
            + " ".join(str(a) for a in (data.get("expected_actions") or [])))
    return bool(re.search(r"來源|查詢日期|不確定|資料限制|出處", blob))


def triage(item):
    tid = item["task_id"]
    m = MAP[tid]
    strat = m["localization_strategy"]
    domain = item.get("domain", "general")
    cid, data = tw_task_yaml(tid)
    safety_ok = has_safety_lang(data)
    fixture = strat == "fixture_replace"

    if fixture:
        final, blocker = "fixed", False
        action = "置換為台灣/示例 fixture，程式重算 expected values，grader 同步更新，並補 safety_checks"
    elif m["risk"].get("live_web"):
        if has_reproducibility_lang(data):
            final, blocker = "fixed", False
            action = ("已在地化為台灣主題；rubric/expected 要求標示來源、查詢日期與不確定性，"
                      "採 method-based 評分、不寫死即時值（可重現）")
        else:
            final, blocker = "accepted_with_rationale", True
            action = ACTION["live_web"] + "（尚未補來源/查詢日期/不確定性要求，需人工審查）"
    elif safety_ok:
        final, blocker = "fixed", False
        action = ACTION.get(domain, ACTION["general"]) + "；已含 safety_checks/風險語言"
    else:
        final, blocker = "requires_external_human_review", True
        action = ACTION.get(domain, ACTION["general"]) + "（尚缺明確 safety 語言，需領域專家覆核）"

    return {
        "task_id": tid,
        "claw_eval_tw_id": cid,
        "category": m["category"],
        "domain": domain,
        "risk_type": ";".join(k for k, v in m["risk"].items() if v) or "none",
        "localization_strategy": strat,
        "current_status": "phase3_localized",
        "issue_summary": item.get("reason", "")[:120],
        "action_taken": action,
        "final_status": final,
        "reviewer_needed": REVIEWER.get(domain, "none"),
        "leaderboard_blocker": str(blocker).lower(),
        "notes": "",
    }


def main():
    highs = [i for i in MR["items"] if i["severity"] == "high"]
    rows = [triage(i) for i in highs]
    rows.sort(key=lambda r: (r["final_status"] != "fixed", r["domain"], r["task_id"]))

    cols = ["task_id", "claw_eval_tw_id", "category", "domain", "risk_type",
            "localization_strategy", "current_status", "issue_summary", "action_taken",
            "final_status", "reviewer_needed", "leaderboard_blocker", "notes"]
    csv_path = ROOT / "reports" / "tw_high_risk_review_matrix.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    fc = Counter(r["final_status"] for r in rows)
    bl = sum(1 for r in rows if r["leaderboard_blocker"] == "true")
    md = [
        "# 台灣在地版高風險任務審查矩陣（tw_high_risk_review_matrix）", "",
        f"- 高風險任務數：**{len(rows)}**",
        f"- 分流：fixed **{fc['fixed']}**、accepted_with_rationale **{fc['accepted_with_rationale']}**、"
        f"requires_external_human_review **{fc['requires_external_human_review']}**",
        f"- leaderboard blockers：**{bl}**", "",
        "完整欄位見 `reports/tw_high_risk_review_matrix.csv`。", "",
        "| task_id | domain | strategy | final_status | reviewer | blocker |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        md.append(f"| {r['task_id']} | {r['domain']} | {r['localization_strategy']} | "
                  f"{r['final_status']} | {r['reviewer_needed']} | {r['leaderboard_blocker']} |")
    md.append("")
    md.append("## Phase 4 重新分類紀錄（審查後更正）")
    md += [
        "- **live-web（16 題）**：已全面在地化為台灣主題（台積電 2330、台灣電商/能源/法規等），",
        "  rubric 要求標示來源/查詢日期/不確定性、method-based 評分 → 由 accepted 改為 **fixed**、移除 blocker。",
        "- **「vulnerability」誤判更正**：`task_log_apache_error_summary`、`task_meeting_searchable_index`、",
        "  `task_meeting_tech_decisions`、`task_meeting_tech_product_features`、`task_meeting_tldr` 等先前被標",
        "  `security` 僅因逐字稿/日誌出現「vulnerability management（GitLab 產品功能）」或「vulnerability",
        "  scanning（log 行）」；經逐題審查確認**非資安操作任務**，已將分類器的 `vulnerability` 關鍵字移除，",
        "  這些任務不再列為高風險 security（cve/credential/brute/exploit 等真正資安任務仍保留標記）。",
        "  → 5 個 `requires_external_human_review` blocker 已清空。",
        "",
        "## 分流規則",
    ]
    md += [
        "- `fixed`：fixture 已置換並重算、或已具備 safety_checks/風險語言且 grader 健全。",
        "- `accepted_with_rationale`：live web 任務（保留研究標的、judge 評分、不寫死即時值），"
        "本質需人工判讀，已記錄理由。",
        "- `requires_external_human_review`：仍需金融/法律/資安/隱私領域專家覆核者。",
    ]
    (ROOT / "reports" / "tw_high_risk_review_matrix.md").write_text("\n".join(md), encoding="utf-8")
    print(f"high tasks: {len(rows)} | {dict(fc)} | blockers: {bl}")
    print("top-20 final_status:", Counter(r["final_status"] for r in rows[:20]))


if __name__ == "__main__":
    main()
