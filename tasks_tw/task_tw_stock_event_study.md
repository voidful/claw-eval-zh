---
id: task_tw_stock_event_study
name: 台股事件研究：台積電衝擊的溢出效應分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/csvs/tw_stock_2024.csv
    dest: tw_stock_2024.csv
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v1
---
## Prompt

我有一個 CSV 檔案 `tw_stock_2024.csv`，包含 2024 年台灣股市 50 檔個股的每日交易資料（欄位：date, ticker, name, open, high, low, close, volume, turnover）。共 252 個交易日 × 50 檔股票。

請對台積電（ticker: 2330）的大波動事件進行「事件研究（Event Study）」，分析其對其他 49 檔股票的溢出效應，將結果輸出至 `event_study_report.md`。

### 第一步：識別事件日

- 計算台積電（2330）每個交易日的日報酬率：`r_t = (close_t - close_{t-1}) / close_{t-1}`
- **上漲事件日**：台積電日報酬率 ≥ +3% 的交易日
- **下跌事件日**：台積電日報酬率 ≤ -3% 的交易日
- 列出所有事件日清單（日期、報酬率、事件類型）

### 第二步：計算累積異常報酬（CAR）

對每個事件日，對其他 49 檔股票計算事件窗口內的 CAR：

**估計窗口**（Estimation Window）：事件日前第 30 日到前第 3 日，共 27 個交易日
```
正常日報酬（Normal Return） = 估計窗口內該股票的平均日報酬率
```

**事件窗口**：事件日前 2 日（T-2）到後 5 日（T+5），共 8 個交易日
```
異常報酬（AR_t） = 實際日報酬率_t - 正常日報酬
CAR = Σ AR_t（對事件窗口內所有 t 加總）
```

**重要**：估計窗口不可包含事件窗口（避免 Look-ahead Bias）。

### 第三步：跨事件日聚合

對每檔股票，計算：
- **上漲事件的平均 CAR**：所有台積電上漲事件的 CAR 平均值
- **下跌事件的平均 CAR**：所有台積電下跌事件的 CAR 平均值

分類：
- **高度溢出股票**：|上漲事件平均 CAR| > 2% 或 |下跌事件平均 CAR| > 2%
- **低相關股票**：|上漲事件平均 CAR| < 0.5% 且 |下跌事件平均 CAR| < 0.5%

### 第四步：溢出效應時間衰退分析

對「高度溢出股票」群組，計算不同事件窗口終點的累積 CAR：
- **T+1 CAR**：僅加總 T-2 到 T+1 的 AR（4 天）
- **T+3 CAR**：加總 T-2 到 T+3 的 AR（6 天）
- **T+5 CAR**：加總 T-2 到 T+5 的 AR（8 天，即完整窗口）

觀察 CAR 是否在 T+3 或 T+5 時收斂（溢出效應是否消退？）

### 輸出報告 `event_study_report.md` 需包含：

1. 台積電事件日清單（日期、報酬率、事件類型、共幾個上漲/下跌事件）
2. 各股票平均 CAR 排行表（分上漲/下跌事件分別排序，取 Top 10 & Bottom 10）
3. 高度溢出 vs 低相關股票分類結果
4. T+1 / T+3 / T+5 的 CAR 收斂分析（溢出效應半衰期）
5. 投資策略建議（如何利用溢出效應進行順勢操作或反向套利）

---

## Expected Behavior

代理人應執行以下步驟：

1. 讀取 12,600 行 CSV，以 ticker 分組建立每檔股票的時序
2. 計算台積電日報酬率，篩選 ≥+3% 和 ≤-3% 的事件日
3. 對每個事件日，對每檔其他股票：
   - 定位估計窗口（T-30 到 T-3 的日期）
   - 計算估計窗口均值作為正常報酬
   - 計算事件窗口（T-2 到 T+5）的 AR
   - 加總得 CAR
4. 跨事件日取平均 CAR（每檔股票有多個事件日的 CAR，取均值）
5. 按閾值分類股票
6. 計算 T+1/T+3/T+5 三個截點的 CAR 收斂情況
7. 撰寫報告含所有五個部分

Key expected values（近似）：
- 台積電 2024 年 ±3% 的事件日約 10~25 天
- 高度溢出股票可能集中在半導體供應鏈相關股票
- 溢出效應通常在 T+3 到 T+5 之間收斂（CAR 不再顯著增加）
- 低相關股票可能是防禦性類股（如食品、生技）

---

## Grading Criteria

- [ ] 輸出檔案 `event_study_report.md` 存在
- [ ] 台積電事件日清單存在（有日期和報酬率數字）
- [ ] ±3% 門檻被正確應用（有提及 3% 或 0.03）
- [ ] CAR 計算有估計窗口和事件窗口的區分
- [ ] 避免 Look-ahead Bias（估計窗口不包含事件窗口）
- [ ] 各股票的平均 CAR 值有列出（有 % 數字）
- [ ] 高度溢出股票和低相關股票分類存在
- [ ] T+1、T+3、T+5 三個時點的 CAR 收斂數字存在
- [ ] 有投資策略建議段落
- [ ] 報告含 Markdown 表格（至少 2 個）

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "event_study_report.md"
    if not report_path.exists():
        for alt in ["event_report.md", "spillover_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "event_days_listed": 0.0,
            "threshold_applied": 0.0,
            "estimation_window_used": 0.0,
            "no_lookahead_bias": 0.0,
            "car_values_present": 0.0,
            "spillover_classification": 0.0,
            "time_decay_analysis": 0.0,
            "investment_strategy": 0.0,
            "has_tables": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Event days listed (dates + return values)
    date_pattern = re.findall(r'2024-\d{2}-\d{2}', content)
    scores["event_days_listed"] = 1.0 if len(date_pattern) >= 5 else (0.5 if len(date_pattern) >= 2 else 0.0)

    # 3% threshold
    has_threshold = bool(re.search(r'3\s*%|0\.03|±3|plus.?3|minus.?3', content_lower))
    scores["threshold_applied"] = 1.0 if has_threshold else 0.0

    # Estimation window mentioned
    est_window = bool(re.search(r'估計窗口|estimation.?window|normal.?return|正常報酬|T-\d{2}', content_lower))
    scores["estimation_window_used"] = 1.0 if est_window else 0.0

    # No look-ahead bias (estimation window before event window)
    no_bias = bool(re.search(r'look.?ahead|前瞻偏誤|避免|T-30|T-3|estimation.*before|窗口.*不重疊', content_lower))
    scores["no_lookahead_bias"] = 1.0 if no_bias else 0.5

    # CAR values present
    car_vals = re.findall(r'CAR|累積異常報酬|cumulative.*abnormal', content, re.IGNORECASE)
    pct_vals = re.findall(r'-?\d+\.?\d*\s*%', content)
    scores["car_values_present"] = 1.0 if (len(car_vals) >= 3 and len(pct_vals) >= 10) else (
        0.5 if len(car_vals) >= 1 else 0.0)

    # Spillover classification
    has_high_spillover = bool(re.search(r'高度溢出|high.*spillover|high.*car|溢出股票', content_lower))
    has_low_corr = bool(re.search(r'低相關|low.*corr|low.*car|低溢出', content_lower))
    scores["spillover_classification"] = 1.0 if (has_high_spillover and has_low_corr) else (
        0.5 if (has_high_spillover or has_low_corr) else 0.0)

    # Time decay (T+1, T+3, T+5)
    t1 = bool(re.search(r'T\+1|t\s*\+\s*1', content))
    t3 = bool(re.search(r'T\+3|t\s*\+\s*3', content))
    t5 = bool(re.search(r'T\+5|t\s*\+\s*5', content))
    scores["time_decay_analysis"] = 1.0 if (t1 and t3 and t5) else (0.5 if sum([t1, t3, t5]) >= 2 else 0.0)

    # Investment strategy
    strategy_kws = ["策略", "建議", "套利", "順勢", "逆勢", "strategy", "recommend", "arbitrage", "momentum", "contrarian"]
    found_strat = sum(1 for kw in strategy_kws if kw.lower() in content_lower)
    scores["investment_strategy"] = 1.0 if found_strat >= 2 else (0.5 if found_strat >= 1 else 0.0)

    # Tables
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
    scores["has_tables"] = 1.0 if len(table_rows) >= 8 else (0.5 if len(table_rows) >= 3 else 0.0)

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

---

## LLM Judge Rubric

### Criterion 1: Event Study Methodology (Weight: 40%)

**Score 1.0**: Correct event day identification (±3% threshold on 2330 returns). Estimation window strictly before event window (no look-ahead bias). CAR correctly computed as sum of abnormal returns (actual minus normal). Normal return correctly estimated from pre-event data only.
**Score 0.75**: Methodology mostly correct; estimation window slightly overlaps event window, or threshold applied to price instead of return.
**Score 0.5**: CAR computed but normal return uses full-period average (introduces look-ahead bias). Or estimation window not clearly separated.
**Score 0.25**: Event days identified but no abnormal return calculation.
**Score 0.0**: No event study methodology applied.

### Criterion 2: Cross-Stock Analysis (Weight: 25%)

**Score 1.0**: All 49 other stocks have average CAR computed for both up and down events. High-spillover (|avg CAR| > 2%) and low-correlation (|avg CAR| < 0.5%) stocks correctly classified. Top 10 CAR rankings make intuitive sense (semiconductor supply chain stocks likely high-spillover).
**Score 0.75**: Most stocks analyzed; classification thresholds correctly applied but 1-2 edge cases wrong.
**Score 0.5**: CAR computed for some stocks (20-40) but not all 49. Classification applied.
**Score 0.25**: Only a few stocks analyzed; cross-stock pattern not captured.
**Score 0.0**: No cross-stock analysis.

### Criterion 3: Time Decay Analysis (Weight: 20%)

**Score 1.0**: T+1, T+3, T+5 CAR values computed for high-spillover group. Clear trend shown (whether spillover persists or decays). Inference made about "half-life" of spillover effect with specific window values.
**Score 0.75**: T+1/T+3/T+5 values present but trend interpretation is missing.
**Score 0.5**: Only one or two time points computed; incomplete decay analysis.
**Score 0.25**: Time decay mentioned conceptually without actual computation.
**Score 0.0**: No time decay analysis.

### Criterion 4: Investment Strategy Quality (Weight: 15%)

**Score 1.0**: Strategy is specific and data-grounded: "買入 A、B 股（高正向溢出）在台積電上漲後 T+1 進場" or "避開 C、D 股（高負向溢出）在台積電大跌日". Strategy accounts for risk (not all spillovers are reliable).
**Score 0.75**: Strategy references spillover findings but lacks specific timing or stock selection.
**Score 0.5**: Generic momentum or contrarian strategy without tying to specific CAR findings.
**Score 0.25**: Vague strategy suggestions.
**Score 0.0**: No investment strategy.

---

## Additional Notes

This task tests:
- Event study methodology (academic finance technique)
- Look-ahead bias avoidance (estimation window must precede event window)
- Multi-event aggregation (computing mean CAR across multiple event days)
- Time-window slicing and alignment across 50 stocks × multiple events
- Classification based on statistical thresholds
- Quantitative strategy design

Key challenges (this is a HARD task):
- Look-ahead bias is the #1 failure mode: using full-period return as "normal" contaminates results
- Aligning estimation window requires finding T-30 to T-3 trading days (not calendar days)
- If a stock has insufficient data for the estimation window (e.g., event near start of year), must handle gracefully
- Cross-event aggregation: 49 stocks × N events = many CAR values to average
- T+1/T+3/T+5 requires partial window summation (not full 8-day window each time)
- Weak models will likely use the overall return average as "normal return" — check if they acknowledge this limitation
