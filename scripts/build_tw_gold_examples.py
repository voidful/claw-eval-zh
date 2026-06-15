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
ACTION_PASS = ("行動項目：\n- 林佳蓉 6/30 完成 API 文件\n- 王志明 與通路確認報價\n"
               "- 陳怡君 安排產品發表會（活動）\n- 張家豪 改版官網\n- 黃淑芬 整理回饋並發內部公告\n"
               "- 李俊賢 資安稽核\n")
ACTION_PARTIAL = "行動項目：\n- 林佳蓉 完成文件\n- 王志明 確認報價\n（缺活動與公告標註、其餘負責人）"
VOTES_PASS = ("預算案：12 票贊成 0 反對 通過。\n道路拓寬案：林議員利益迴避，10 比 1 通過。\n"
              "公園命名案：全體一致通過。\n清運費調整：完成一讀。\n都市更新案：延期保留。\n"
              "社福補助：7 比 5 通過。\n")
VOTES_PARTIAL = "預算案 12 比 0 通過。公園命名案一致通過。（其餘議案未整理）"
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

    # 8. meeting action items
    write_case("task_meeting_tech_action_items", "pass", {"action_items.md": ACTION_PASS})
    write_case("task_meeting_tech_action_items", "partial", {"action_items.md": ACTION_PARTIAL})
    write_case("task_meeting_tech_action_items", "fail", {"x.txt": "n/a"})
    expected("task_meeting_tech_action_items", {"pass": {"min_mean": 0.9}, "partial": {"min_mean": 0.2, "max_mean": 0.8},
                                                "fail": {"max_mean": 0.05}})

    # 9. council votes
    write_case("task_meeting_council_votes", "pass", {"votes_report.md": VOTES_PASS})
    write_case("task_meeting_council_votes", "partial", {"votes_report.md": VOTES_PARTIAL})
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
