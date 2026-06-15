---
id: task_csv_stock_trend
name: 蘋果股票 2014 年趨勢分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_stock_trend
source_benchmark: pinchbench
claw_eval_id: P053zh_csv_stock_trend
workspace_files:
- source: csvs/apple_stock_2014.csv
  dest: apple_stock_2014.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 蘋果股票 2014 年趨勢分析

## Prompt

我的工作區裡有一個 CSV 檔案 apple_stock_2014.csv，內含蘋果（AAPL）2014 年
的調整後收盤價（adjusted closing price）。檔案有兩欄：AAPL_x（日期，
YYYY-MM-DD 格式）與 AAPL_y（調整後收盤價），共 240 個交易日。

請分析蘋果股票 2014 年整體價格趨勢，並把結果寫入檔案 stock_trend_report.md。
報告需包含：

- **整體趨勢方向**（看漲 bullish／看跌 bearish／盤整 sideways）
- **起始價**（首個交易日）、**結束價**（最後交易日）與**整體漲跌幅百分比**
- **每月平均價**，呈現全年走勢
- **關鍵趨勢區段**：找出最長的連續上漲天數與連續下跌天數，並附上日期
- **持續性走勢**：指出明顯的持續上漲或下跌時段（如數週的反彈或回落）
- 一段全年價格走勢的**總結**

注意：CSV 檔名、欄名（AAPL_x / AAPL_y）與報告檔名 stock_trend_report.md 都
不可更改。

## Expected Behavior

助手應該：
1. 讀取並解析 CSV 檔案
2. 計算起始價（2014-01-02 為 $77.45）與結束價（2014-12-12 為 $110.03）
3. 計算整體漲跌幅（約 +42.07%）
4. 判定整體趨勢為看漲（明顯上行）
5. 計算每月平均價，呈現上行軌跡
6. 找出最長連續上漲（9 天，2014-08-11 至 2014-08-21）
7. 找出最長連續下跌（5 天，2014-01-27 至 2014-01-31）
8. 指出關鍵轉折（1 月回落、4 月突破、5 月至年底穩步攀升）
9. 寫出結構清晰的 markdown 報告

已知正確值：240 個交易日；起始 $77.45（2014-01-02）、結束 $110.03
（2014-12-12）；整體 +42.07%；趨勢看漲；最長連漲 9 天、最長連跌 5 天。

## Grading Criteria

- [ ] 建立報告檔案 stock_trend_report.md
- [ ] 正確判定整體趨勢為看漲／上行
- [ ] 正確報告起始價（約 $77.45）
- [ ] 正確報告結束價（約 $110.03）
- [ ] 正確計算漲跌幅（約 42%）
- [ ] 包含每月平均價或月度拆解
- [ ] 找出最長連漲（8 月約 9 個連續交易日）
- [ ] 找出最長連跌（1 月底約 5 個連續交易日）
- [ ] 描述關鍵趨勢區段或顯著走勢

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Stock trend analysis grader (trilingual: 繁體 + 简体 + English).

    Numeric expectations (77.45 / 110.03 / 42%) are unchanged from
    PinchBench. Natural-language regex additionally accepts Chinese.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "stock_trend_report.md"
    if not report_path.exists():
        alternatives = [
            "trend_report.md", "report.md", "stock_report.md",
            "analysis.md", "stock_trend.md", "趨勢報告.md", "趋势报告.md",
        ]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0, "trend_direction": 0.0,
            "starting_price": 0.0, "ending_price": 0.0,
            "percentage_change": 0.0, "monthly_breakdown": 0.0,
            "up_streak": 0.0, "down_streak": 0.0, "trend_periods": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    bullish_patterns = [
        r'bullish', r'upward\s*trend', r'positive\s*trend',
        r'strong\s*uptrend', r'significant.*(?:gain|increase|growth|rise)',
        r'看漲', r'看涨', r'多頭', r'多头', r'上升趨勢', r'上升趋势',
        r'明顯上漲', r'明显上涨', r'上漲趨勢', r'上涨趋势', r'牛市',
    ]
    scores["trend_direction"] = 1.0 if any(
        re.search(p, content_lower) for p in bullish_patterns) else 0.0

    scores["starting_price"] = 1.0 if re.search(r'77\.4[45]', content) else 0.0
    scores["ending_price"] = 1.0 if re.search(r'110\.0[23]', content) else 0.0
    pct_patterns = [r'4[12]\.\d+%', r'4[12]\.0\d*%', r'42\.07', r'42%', r'~42']
    scores["percentage_change"] = 1.0 if any(
        re.search(p, content) for p in pct_patterns) else 0.0

    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']
    month_abbrs = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                   'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    month_nums = ['2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06',
                  '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']
    month_count = 0
    for i, (mn, ma, mnum) in enumerate(zip(month_names, month_abbrs, month_nums), start=1):
        cn = "%d月" % i
        if mn in content_lower or ma in content_lower or mnum in content or cn in content:
            month_count += 1
    scores["monthly_breakdown"] = 1.0 if month_count >= 10 else (
        0.5 if month_count >= 6 else 0.0)

    up_streak_patterns = [
        r'(?:9|nine)\s*(?:consecutive|day|trading)',
        r'(?:consecutive|streak).*(?:9|nine)',
        r'aug(?:ust)?.*(?:up|gain|positive).*(?:streak|consecutive)',
        r'(?:up|gain|positive).*(?:streak|consecutive).*aug(?:ust)?',
        r'2014-08-1[1-9].*2014-08-2[01]',
        r'(?:連續|连续|連漲|连涨).*(?:9|九)',
        r'(?:9|九).*(?:連續|连续|天).*(?:上漲|上涨)',
        r'8月.*(?:連續上漲|连续上涨|連漲|连涨)',
        r'(?:連續上漲|连续上涨).*8月',
    ]
    scores["up_streak"] = 1.0 if any(
        re.search(p, content_lower) for p in up_streak_patterns) else 0.0

    down_streak_patterns = [
        r'(?:5|five)\s*(?:consecutive|day|trading).*(?:down|decline|loss|negative|drop)',
        r'(?:down|decline|loss|negative|drop).*(?:5|five)\s*(?:consecutive|day|trading)',
        r'(?:down|decline|loss|negative|drop).*(?:streak|consecutive).*jan(?:uary)?',
        r'jan(?:uary)?.*(?:down|decline|loss|negative|drop).*(?:streak|consecutive)',
        r'2014-01-2[789].*2014-01-3[01]',
        r'(?:連續|连续).*(?:5|五).*(?:下跌)',
        r'(?:5|五).*(?:連續|连续|天).*(?:下跌)',
        r'1月.*(?:連續下跌|连续下跌|連跌|连跌)',
        r'(?:連續下跌|连续下跌).*1月',
    ]
    scores["down_streak"] = 1.0 if any(
        re.search(p, content_lower) for p in down_streak_patterns) else 0.0

    trend_indicators = 0
    if (re.search(r'jan(?:uary)?.*(?:dip|drop|decline|sell-?off|fall)', content_lower)
            or re.search(r'1月.*(?:下跌|回調|回调|拋售|抛售|下挫)', content)):
        trend_indicators += 1
    if (re.search(r'apr(?:il)?.*(?:breakout|rally|surge|jump|spike)', content_lower)
            or re.search(r'4月.*(?:突破|大漲|大涨|反彈|反弹|飆升|飙升)', content)):
        trend_indicators += 1
    if (re.search(r'(?:rally|climb|rise|growth|upward).*(?:may|summer|q[23])', content_lower)
            or re.search(r'(?:5月|夏|三季度|第三季).*(?:上漲|上涨|攀升|爬升)', content)):
        trend_indicators += 1
    if (re.search(r'(?:nov(?:ember)?|q4).*(?:high|peak|rally|climb)', content_lower)
            or re.search(r'(?:11月|12月|四季度|第四季).*(?:新高|高點|高点|峰值)', content)):
        trend_indicators += 1
    scores["trend_periods"] = 1.0 if trend_indicators >= 2 else (
        0.5 if trend_indicators >= 1 else 0.0)

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
- 1.0：所有計算值（起始／結束價、漲跌幅、連漲連跌）數值正確且清楚呈現
- 0.75：大多正確，僅一兩處小誤差
- 0.5：部分正確，但若干關鍵數字錯誤或缺失
- 0.25：僅少數正確，存在重大計算錯誤
- 0.0：沒有正確計算或未嘗試分析

### 評分項 2：趨勢辨識品質（權重 30%）
- 1.0：正確判定看漲，詳述各區段（1 月回落、4 月突破、夏季攀升、年底延續）並附具體日期
- 0.75：正確判定看漲，並合理描述多數主要區段
- 0.5：判定整體方向，但子區段或關鍵轉折分析有限
- 0.25：趨勢判定模糊或部分錯誤，佐證不足
- 0.0：未能判定趨勢或分析完全錯誤

### 評分項 3：報告結構與呈現（權重 20%）
- 1.0：結構清晰、markdown 分段良好，含每月價格表格，由總結到細節邏輯流暢
- 0.75：組織良好、易讀，僅排版小瑕疵
- 0.5：含分析但組織不佳或難以閱讀
- 0.25：雜亂或缺少主要段落
- 0.0：未建立報告或報告為空／不可用

### 評分項 4：完整度（權重 15%）
- 1.0：所有要求項目齊備（整體趨勢、起／結價、漲跌幅、月度拆解、連漲連跌、持續走勢、總結）
- 0.75：大多齊備，僅一兩處小遺漏
- 0.5：遺漏若干要求項目
- 0.25：僅含少數要求項目
- 0.0：報告缺失或幾近空白
