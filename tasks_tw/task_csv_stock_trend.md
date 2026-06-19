---
id: task_csv_stock_trend
name: 台積電（2330）2024 股價趨勢分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_stock_trend
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: fixture_replace
claw_eval_tw_id: T053tw_csv_stock_trend
workspace_files:
- source: tw/csvs/tw_stock_2330_2024.csv
  dest: tw_stock_2330_2024.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台積電（2330）2024 股價趨勢分析

## Prompt

我的工作區裡有一個 CSV 檔案 tw_stock_2330_2024.csv，內含台積電（2330）2024 年的
每日收盤價。資料來自臺灣證券交易所（TWSE）公開資料。檔案有兩欄：date（日期，
YYYY-MM-DD 格式）與 close（收盤價，新臺幣 NT$），共 242 個交易日。

請分析台積電 2024 年整體股價趨勢，並把結果寫入檔案 stock_trend_report.md。報告需包含：

- **整體趨勢方向**（看漲 bullish／看跌 bearish／盤整 sideways）
- **起始價**（首個交易日）、**結束價**（最後交易日）與**整體漲跌幅百分比**
- **每月平均收盤價**，呈現全年走勢
- **關鍵趨勢區段**：最長連續上漲天數與最長連續下跌天數，並附日期
- **全年最高與最低收盤價**及其日期
- 一段全年走勢的**總結**

注意：CSV 檔名、欄名（date / close）與報告檔名 stock_trend_report.md 不可更改。
所有金額以新臺幣（NT$）計。

## Expected Behavior

助手應該讀取並分析 CSV，得出（已由程式從 TWSE 真實資料驗算）：
- 242 個交易日；起始價 NT$593.00（2024-01-02）、結束價 NT$1,075.00（2024-12-31）
- 整體漲跌幅約 +81.28%，趨勢明顯看漲（bullish）
- 每月平均收盤價由 1 月約 604 一路上升至 12 月約 1070
- 最長連續上漲 6 天（2024-09-18 至 2024-09-26）
- 最長連續下跌 4 天（2024-05-27 至 2024-05-31）
- 全年最高收盤價 NT$1,090.00（2024-11-08）、最低 NT$576.00（2024-01-05）
並輸出結構清晰的 markdown 報告。

## Grading Criteria

- [ ] 建立報告檔案 stock_trend_report.md
- [ ] 正確判定整體趨勢為看漲／上行
- [ ] 正確報告起始價（約 NT$593）
- [ ] 正確報告結束價（約 NT$1,075）
- [ ] 正確計算漲跌幅（約 81%）
- [ ] 包含每月平均價或月度拆解
- [ ] 找出最長連漲（約 6 個連續交易日，9 月）
- [ ] 找出最長連跌（約 4 個連續交易日，5 月底）
- [ ] 描述全年最高／最低或關鍵走勢

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """2330 2024 trend grader. Values recomputed from real TWSE fixture."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    report = workspace / "stock_trend_report.md"
    if not report.exists():
        for alt in ["trend_report.md", "report.md", "stock_report.md",
                    "analysis.md", "趨勢報告.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in ["report_created", "trend_direction", "starting_price",
                                 "ending_price", "percentage_change", "monthly_breakdown",
                                 "up_streak", "down_streak", "extremes"]}
    scores = {"report_created": 1.0}
    content = report.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()
    bull = [r'bullish', r'upward', r'看漲', r'看涨', r'多頭', r'多头',
            r'上升趨勢', r'上升趋势', r'明顯上漲', r'明显上涨', r'牛市', r'大漲', r'大涨']
    scores["trend_direction"] = 1.0 if any(re.search(p, cl) for p in bull) else 0.0
    scores["starting_price"] = 1.0 if re.search(r'593(\.0+)?', content) else 0.0
    scores["ending_price"] = 1.0 if re.search(r'1[,]?075(\.0+)?', content) else 0.0
    scores["percentage_change"] = 1.0 if re.search(r'8[01]\.\d|81\.28|81\s*%|~?\s*81', content) else 0.0
    months = 0
    for i in range(1, 13):
        if ("%d月" % i) in content or ("2024-%02d" % i) in content:
            months += 1
    scores["monthly_breakdown"] = 1.0 if months >= 10 else (0.5 if months >= 6 else 0.0)
    up = [r'(?:6|六)\s*(?:天|個交易日|consecutive|day)',
          r'(?:連續|连续|consecutive).*(?:6|六)', r'9月.*(?:連續上漲|连续上涨|連漲)',
          r'2024-09-1[89].*2024-09-2[0-6]']
    scores["up_streak"] = 1.0 if any(re.search(p, cl) for p in up) else 0.0
    down = [r'(?:4|四)\s*(?:天|個交易日|consecutive|day).*(?:下跌|down|decline)',
            r'(?:下跌|down|decline).*(?:4|四)\s*(?:天|consecutive)',
            r'5月.*(?:連續下跌|连续下跌|連跌)', r'2024-05-2[7-9].*2024-05-3[01]']
    scores["down_streak"] = 1.0 if any(re.search(p, cl) for p in down) else 0.0
    ext = 0
    if re.search(r'1[,]?090', content):
        ext += 1
    if re.search(r'576', content):
        ext += 1
    scores["extremes"] = 1.0 if ext >= 2 else (0.5 if ext == 1 else 0.0)
    return scores


# --- Bilingual report normalization (中文 report -> English keywords) ---
# See docs/claw_eval_zh_schema.md §8 and scripts/lib_zh.py. The English-only
# path is unchanged (no CJK in reports -> direct passthrough, no shadow copy).
try:
    from lib_zh import normalize_zh_to_en as _zh_normalize
except Exception:  # noqa: BLE001
    def _zh_normalize(_text):
        return _text

_GRADE_IMPL = grade


def grade(transcript, workspace_path):  # noqa: F811
    """Shadow-normalize Chinese report text, then run the original grade()."""
    import shutil
    import tempfile
    from pathlib import Path as _P

    text_exts = (".md", ".txt", ".rst", ".markdown")
    ws = workspace_path
    try:
        src = _P(workspace_path)
        if src.exists() and src.is_dir():
            needs = False
            for f in src.rglob("*"):
                if f.is_file() and f.suffix.lower() in text_exts:
                    try:
                        if any("一" <= c <= "鿿" for c in f.read_text(encoding="utf-8")):
                            needs = True
                            break
                    except (OSError, UnicodeDecodeError):
                        pass
            if needs:
                shadow = _P(tempfile.mkdtemp(prefix="cez_ws_")) / "ws"
                shutil.copytree(src, shadow, dirs_exist_ok=True)
                for f in shadow.rglob("*"):
                    if f.is_file() and f.suffix.lower() in text_exts:
                        try:
                            f.write_text(
                                _zh_normalize(f.read_text(encoding="utf-8")),
                                encoding="utf-8",
                            )
                        except (OSError, UnicodeDecodeError):
                            pass
                ws = str(shadow)
    except Exception:  # noqa: BLE001
        ws = workspace_path
    return _GRADE_IMPL(transcript, ws)

```

## LLM Judge Rubric

### 評分項 1：資料分析準確度（權重 35%）
- 1.0：起始/結束價、漲跌幅、連漲連跌、最高最低等數值正確且清楚呈現
- 0.5：部分正確，若干關鍵數字錯誤或缺失
- 0.0：未正確計算或未嘗試
### 評分項 2：趨勢辨識品質（權重 30%）
- 1.0：正確判定看漲並描述各區段（年初低點、年中攀升、年末高檔）附日期
- 0.5：判定整體方向但子區段分析有限
- 0.0：未能判定或完全錯誤
### 評分項 3：報告結構（權重 20%）
- 1.0：markdown 分段清楚、含每月價格、由總結到細節
- 0.5：含分析但組織不佳
- 0.0：報告缺失或不可用
### 評分項 4：完整度（權重 15%）
- 1.0：所有要求項目齊備
- 0.5：遺漏若干項目
- 0.0：幾近空白
