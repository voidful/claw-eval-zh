#!/usr/bin/env python3
"""One-time builder for gold_tw/ — grader-calibration reference cases.

For each representative task it writes pass / partial / fail cases (each case dir
is a workspace; may contain transcript.json) plus expected_scores.json with
mean-score thresholds. run_tw_gold_checks.py replays the deterministic TW graders
against these and asserts the thresholds. Re-runnable; output committed.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "gold_tw"

# Localized meeting transcripts that the council/tech graders read from the
# workspace to derive the expected facts dynamically. The gold cases therefore
# must ship the transcript alongside the agent report.
COUNCIL_TRANSCRIPT = (
    ROOT / "assets" / "tw" / "meetings" / "tw_council_meeting.md").read_text(encoding="utf-8")
TECH_TRANSCRIPT = (
    ROOT / "assets" / "tw" / "meetings" / "tw_tech_product_meeting.md").read_text(encoding="utf-8")

# --- report bodies ---------------------------------------------------------
STOCK_PASS = (
    "# 台積電 2330 2024 趨勢報告\n整體趨勢：看漲。起始價 593.00，結束價 1,075.00，"
    "漲跌幅 +81.28%。\n2024-09-18 至 2024-09-26 連續上漲 6 天；2024-05-27 至 2024-05-31 "
    "連續下跌 4 天。\n全年最高 1,090（2024-11-08），最低 576（2024-01-05）。\n"
    + "".join(f"{m}月 平均 約{600+m*40}\n" for m in range(1, 13))
)
STOCK_PARTIAL = ("整體趨勢：看漲。起始價 593.00，結束價 1,075.00。\n（缺漲跌幅、連漲連跌、"
                 "月度與極值）\n")
VOL_PASS = ("每日報酬率標準差 2.17%，年化波動率 34.5%。波動最劇烈：2024-08-06 +7.98%、"
            "2024-08-05 -9.75%。整體波動偏高，風險需留意。")
VOL_PARTIAL = "每日報酬率標準差約 2.17%。（缺年化波動率與極端日）"
BW_PASS = ("最佳：2024-08-06 +7.98%。最差：2024-08-05 -9.75%。最高收盤 1,090，最低 576。"
           "分析：8 月波動最大。")
BW_PARTIAL = "最佳交易日 2024-08-06。（缺數值與最差日）"
CITIES_PASS = (
    "六都人口≥200萬：新北市、臺中市、高雄市、臺北市、桃園市，共 5 個，總人口 14,427,922。\n"
    "南部≥100萬：高雄市、臺南市。\n臺北市 2,494,813 vs 高雄市 2,738,041，高雄較多。\n"
    "中型 50-100萬：屏東縣、新竹縣、苗栗縣、雲林縣，共 4 個。\n北部共 7 個縣市，新北市、"
    "臺北市、桃園市、新竹縣、新竹市。\n")
CITIES_PARTIAL = "六都：新北市、臺中市、高雄市、臺北市、桃園市，共 5 個。（其餘篩選未做）"
FIN_PASS = ("存貨周轉率 = 營業成本 / 平均存貨 = 84,000,000,000 / 14,000,000,000 = 6.0。"
            "此為示例資料，非投資建議。")
FIN_PARTIAL = "存貨周轉率大約是 6。（未列公式與代入數值，也未聲明）"
ACTION_PASS = (
    "# 鼎峰科技 產品暨行銷週會 行動項目彙整\n\n"
    "（資料來源：本週週會逐字稿；期限以 Asia/Taipei 為準）\n\n"
    "## 行動項目清單\n"
    "1. 行動項目（全體）：各位回去跟自己負責的活動行銷經理確認三場研討會"
    "（COSCUP、DevOpsDays Taipei、Kubernetes Day Taiwan）的贊助承諾，並在對應活動"
    " issue 底下留言回報。負責人：全體；期限：本週內確認。\n"
    "2. 行動項目：戴立安在本週內整理三場活動的分工，並發出一份對內公告，"
    "通知各部門業務與工程同仁。負責人：戴立安；期限：本週內。\n"
    "3. 行動項目：高敏哲在星期二前，為 Plan（規劃）這個 stage 補上一份 top 5 候選清單"
    "（含史詩看板、里程碑燃盡圖）。負責人：高敏哲；期限：星期二前。\n"
    "4. 行動項目（全體）：大家把產品發布試算表的欄位補完，各自檢視並投票選出最終"
    "整體前 5 名（top 5 overall）發布題材，交由公關團隊當匯流大會 keynote 素材。"
    "負責人：全體；期限：這個星期二截止。\n"
    "5. 行動項目：蔡思敏把競品比較試算表改成每個 stage 只列出與該 stage 相關的"
    " tier 1 競爭對手（不再每頁都塞滿六家）。負責人：蔡思敏；期限：本週內。\n"
    "6. 行動項目：在競品比較表新增「鼎峰」自己一列（line item），誠實呈現對手在"
    "某些功能上更好的地方。負責人：蔡思敏；期限：本週內。\n"
    "7. 行動項目：王志明今天下班前（end of day）把訊息架構定稿，以主標語"
    "「更快交付，更低風險」收尾。負責人：王志明；期限：今天下班前。\n"
)
ACTION_PARTIAL = (
    "# 行動項目（草稿）\n\n"
    "- 行動項目：戴立安整理三場研討會（COSCUP、DevOpsDays Taipei、"
    "Kubernetes Day Taiwan）的贊助分工。\n"
    "- 行動項目：高敏哲補一份候選清單。\n"
    "（本草稿尚未整理完，後續其他主題與負責人、各項期限仍待補齊）\n"
)
VOTES_PASS = (
    "# 南港市議會 第 12 屆第 3 次定期會 表決彙整\n\n"
    "（資料來源：本次定期會逐字稿）\n\n"
    "## 各議案表決結果\n"
    "1. 第二案／年度總預算追加案：高文彬 議員 動議、林淑芬 議員 附議，"
    "表決結果 7 票贊成、0 票反對，全體一致通過（7 比 0）。\n"
    "2. 第三案／市民大道道路拓寬工程預算案：卡爾森 議員（蔡明憲）因配偶任職之"
    "公司為承包商，依法辦理利益迴避（abstain），不參與表決；其餘 6 位議員以"
    " 5 比 2 表決通過（高文彬 反對）。\n"
    "3. 第十四、十五案／羅馬倉庫園區 第四期開發契約與容積獎勵案：林淑芬 動議、"
    "陳秀蓮 附議，併案進行記名表決，5 比 2 通過（卡爾森、高文彬 投反對票）。\n"
    "4. 第十九案／公道五路沿線分區變更案（門牌 4102、2707、110 三處）：楊乃文 動議、"
    "韋立群 附議，全體一致、無異議通過。\n"
    "5. 第二十三案／自來水及污水容量費（容量接管費）調整自治條例案：高文彬 動議、"
    "林淑芬 附議，完成一讀（first reading），付委審查後排入二讀。\n"
    "6. 第二十二案／退伍軍人事務諮詢委員會（退輔諮詢委員會）設置自治條例案："
    "因委員資格條文尚有疑義，本案延期、保留至 4 月 16 日 次會 續審。\n"
    "7. 第二十五案／反對中央刪減地方水環境改善前瞻補助 決議文：陳秀蓮 動議、"
    "楊乃文 附議，6 比 1 通過（卡爾森 投反對票／dissent）。\n\n"
    "## 統計摘要\n"
    "本日合計處理表決與議案共 11 件，其中無異議／全體一致通過 4 件、"
    "記名或有反對票通過 3 件、利益迴避案 2 件、一讀 1 件、延期或復議改期 3 件。\n"
)
VOTES_PARTIAL = (
    "# 表決彙整（草稿）\n\n"
    "第二案／年度總預算追加案：7 票贊成、0 票反對，全體一致通過（7 比 0）。\n"
    "第十九案／公道五路分區變更案：全體一致無異議通過。\n"
    "（其餘議案，如道路拓寬利益迴避、羅馬倉庫園區記名表決、容量費一讀、"
    "退輔委員會延期、前瞻補助決議文等，尚未整理；亦缺統計摘要）\n"
)
WEATHER_PASS = ("import requests\n\n\ndef main():\n    try:\n        r = requests.get('https://wttr.in/Taipei?format=j1')\n"
                "        print(r.json())\n    except Exception as e:\n        print('error', e)\n\n\n"
                "if __name__ == '__main__':\n    main()\n")
WEATHER_PARTIAL = "print('Taipei weather')\n"  # valid python, location, but no http/error handling
ICS_PASS = (
    "BEGIN:VCALENDAR\nBEGIN:VEVENT\nSUMMARY:專案同步會議\n"
    "ATTENDEE:mailto:zhiming.wang@example.com.tw\nDESCRIPTION:討論 Q1 roadmap 藍圖\n"
    "DTSTART;TZID=Asia/Taipei:{date}T150000\nDTEND;TZID=Asia/Taipei:{date}T160000\n"
    "END:VEVENT\nEND:VCALENDAR\n")


def _next_tuesday_yyyymmdd() -> str:
    # gold uses a fixed placeholder date pattern; calendar grader checks "next
    # Tuesday" relative to now, so the calendar pass case targets date_correct=partial.
    return "20990106"  # a Tuesday far in the future; date_correct will be 0 (documented)


def write_case(task_id: str, case: str, files: dict, transcript=None):
    d = GOLD / task_id / case
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (d / name).write_text(content, encoding="utf-8")
    if transcript is not None:
        (d / "transcript.json").write_text(json.dumps(transcript, ensure_ascii=False), encoding="utf-8")


def expected(task_id: str, scores: dict, note: str = ""):
    (GOLD / task_id / "expected_scores.json").write_text(
        json.dumps({"task_id": task_id, "cases": scores, "note": note},
                   ensure_ascii=False, indent=2), encoding="utf-8")


ASSISTANT = [{"type": "message", "message": {"role": "assistant",
             "content": [{"type": "text", "text": "你好，我已準備好了！"}]}}]


def main():
    GOLD.mkdir(exist_ok=True)

    # 1. sanity (transcript-based)
    write_case("task_sanity", "pass", {}, transcript=ASSISTANT)
    write_case("task_sanity", "fail", {}, transcript=[])
    expected("task_sanity", {"pass": {"min_mean": 1.0}, "fail": {"max_mean": 0.0}},
             "transcript.json is loaded as the transcript; workspace empty.")

    # 2. weather
    write_case("task_weather", "pass", {"weather.py": WEATHER_PASS})
    write_case("task_weather", "partial", {"weather.py": WEATHER_PARTIAL})
    write_case("task_weather", "fail", {"readme.txt": "nothing"})
    expected("task_weather", {"pass": {"min_mean": 0.95}, "partial": {"min_mean": 0.2, "max_mean": 0.75},
                              "fail": {"max_mean": 0.05}})

    # 3-5. stock trio
    write_case("task_csv_stock_trend", "pass", {"stock_trend_report.md": STOCK_PASS})
    write_case("task_csv_stock_trend", "partial", {"stock_trend_report.md": STOCK_PARTIAL})
    write_case("task_csv_stock_trend", "fail", {"x.txt": "n/a"})
    expected("task_csv_stock_trend", {"pass": {"min_mean": 0.95}, "partial": {"min_mean": 0.25, "max_mean": 0.75},
                                      "fail": {"max_mean": 0.05}})
    write_case("task_csv_stock_volatility", "pass", {"volatility_report.md": VOL_PASS})
    write_case("task_csv_stock_volatility", "partial", {"volatility_report.md": VOL_PARTIAL})
    write_case("task_csv_stock_volatility", "fail", {"x.txt": "n/a"})
    expected("task_csv_stock_volatility", {"pass": {"min_mean": 0.9}, "partial": {"min_mean": 0.2, "max_mean": 0.7},
                                           "fail": {"max_mean": 0.05}})
    write_case("task_csv_stock_best_worst", "pass", {"best_worst_days_report.md": BW_PASS})
    write_case("task_csv_stock_best_worst", "partial", {"best_worst_days_report.md": BW_PARTIAL})
    write_case("task_csv_stock_best_worst", "fail", {"x.txt": "n/a"})
    expected("task_csv_stock_best_worst", {"pass": {"min_mean": 0.9}, "partial": {"min_mean": 0.15, "max_mean": 0.7},
                                           "fail": {"max_mean": 0.05}})

    # 6. cities filter
    write_case("task_csv_cities_filter", "pass", {"cities_filter_report.md": CITIES_PASS})
    write_case("task_csv_cities_filter", "partial", {"cities_filter_report.md": CITIES_PARTIAL})
    write_case("task_csv_cities_filter", "fail", {"x.txt": "n/a"})
    expected("task_csv_cities_filter", {"pass": {"min_mean": 0.9}, "partial": {"min_mean": 0.15, "max_mean": 0.7},
                                        "fail": {"max_mean": 0.05}})

    # 7. financial ratio
    write_case("task_financial_ratio_calculation", "pass", {"inventory_turnover.txt": FIN_PASS})
    write_case("task_financial_ratio_calculation", "partial", {"inventory_turnover.txt": FIN_PARTIAL})
    write_case("task_financial_ratio_calculation", "fail", {"x.txt": "n/a"})
    expected("task_financial_ratio_calculation", {"pass": {"min_mean": 0.9}, "partial": {"min_mean": 0.2, "max_mean": 0.75},
                                                  "fail": {"max_mean": 0.05}})

    # 8. meeting action items (grader reads meeting_transcript.md from workspace)
    write_case("task_meeting_tech_action_items", "pass",
               {"meeting_transcript.md": TECH_TRANSCRIPT, "action_items.md": ACTION_PASS})
    write_case("task_meeting_tech_action_items", "partial",
               {"meeting_transcript.md": TECH_TRANSCRIPT, "action_items.md": ACTION_PARTIAL})
    write_case("task_meeting_tech_action_items", "fail", {"x.txt": "n/a"})
    expected("task_meeting_tech_action_items", {"pass": {"min_mean": 0.9}, "partial": {"min_mean": 0.2, "max_mean": 0.8},
                                                "fail": {"max_mean": 0.05}})

    # 9. council votes (grader reads transcript.md from workspace)
    write_case("task_meeting_council_votes", "pass",
               {"transcript.md": COUNCIL_TRANSCRIPT, "votes_report.md": VOTES_PASS})
    write_case("task_meeting_council_votes", "partial",
               {"transcript.md": COUNCIL_TRANSCRIPT, "votes_report.md": VOTES_PARTIAL})
    write_case("task_meeting_council_votes", "fail", {"x.txt": "n/a"})
    expected("task_meeting_council_votes", {"pass": {"min_mean": 0.9}, "partial": {"min_mean": 0.2, "max_mean": 0.8},
                                            "fail": {"max_mean": 0.05}})

    # 10. calendar (date_correct depends on "now"; pass case targets the other 6 criteria)
    d = _next_tuesday_yyyymmdd()
    write_case("task_calendar", "pass", {"meeting.ics": ICS_PASS.format(date=d)})
    write_case("task_calendar", "fail", {"note.txt": "no ics"})
    expected("task_calendar",
             {"pass": {"min_mean": 0.7}, "fail": {"max_mean": 0.0}},
             "date_correct 依執行當下的『下週二』而定，gold 用固定未來日期，故 pass 門檻設 0.7（其餘 6 項應為 1.0）。")

    # 11. contract_analysis (llm_judge): rubric checklist + reference, no automated score
    cdir = GOLD / "task_contract_analysis"
    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / "judge_checklist.md").write_text(
        "# task_contract_analysis LLM judge 檢核清單（人工/judge 用，非自動評分）\n\n"
        "本任務為 llm_judge，deterministic grader 回傳 {}。以下為參考評分要點：\n\n"
        "- [ ] 是否摘要主要條款（總價 360 萬、付款 30/40/30、6 個月、違約金上限 20%、"
        "責任以合約總價為上限、台北地院管轄）\n"
        "- [ ] 是否指出具體風險／疑義（責任上限、付款比例、個資保密範圍、終止條件）\n"
        "- [ ] 是否明確聲明『非法律意見』並建議諮詢律師\n"
        "- [ ] 是否未捏造合約中沒有的條款或法條（捏造應重扣分）\n"
        "- [ ] 結構清楚、條列分明\n", encoding="utf-8")
    (cdir / "reference_answer.md").write_text(
        "# 參考答案（reference）\n見 tasks_claw_eval_tw/T049tw_contract_analysis/task.yaml 的 "
        "reference_solution；重點：八條條款摘要 + 風險清單 + 需律師確認事項 + 非法律意見聲明。\n",
        encoding="utf-8")
    expected("task_contract_analysis", {}, "llm_judge：無 deterministic 分數；以 judge_checklist.md 校準 rubric。")

    print("gold_tw built for:", sorted(p.name for p in GOLD.iterdir() if p.is_dir()))


if __name__ == "__main__":
    main()
