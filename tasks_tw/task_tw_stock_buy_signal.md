---
id: task_tw_stock_buy_signal
name: 台灣股市買入訊號分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 300
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
source_benchmark: new_benchmark_files
---
## Prompt

我有一個 CSV 檔案 `tw_stock_2024.csv`，包含 2024 年台灣股市 50 檔個股的每日交易資料。欄位為：date, ticker, name, open, high, low, close, volume, turnover。共 252 個交易日 × 50 檔股票。

請對這些資料進行完整的量化選股分析，找出「值得買入」的個股，並將結果寫入 `buy_signal_report.md`。

你的分析必須包含以下步驟與內容：

1. **技術面計算**（每檔股票）：
   - 計算 5日、20日、60日 移動平均線（MA5, MA20, MA60）
   - 計算 14日 RSI 指標
   - 計算 MACD（DIF = EMA12 - EMA26, Signal = EMA9(DIF), Histogram = DIF - Signal）
   - 計算 20日布林通道（上軌、中軌、下軌）

2. **風險指標計算**：
   - 計算每檔股票的年化報酬率
   - 計算年化波動率（日報酬率標準差 × √252）
   - 計算夏普比率（假設無風險利率 = 1.6%）
   - 計算最大回撤 (Maximum Drawdown)

3. **買入訊號判定**（以最後一個交易日為基準）：
   - 條件 A：RSI < 35（超賣）
   - 條件 B：MACD 柱狀圖由負轉正（近 5 日內出現黃金交叉）
   - 條件 C：收盤價 > MA60 且 MA5 > MA20（多頭排列形成中）
   - 條件 D：收盤價在布林下軌附近（< 下軌 + (中軌-下軌)*0.2）
   - 條件 E：夏普比率 > 0.8 且最大回撤 < -25%（風險可控）
   
   滿足 ≥ 3 個條件者為「強力推薦」，滿足 2 個為「建議觀望」。

4. **報告內容**：
   - 完整的計算過程說明
   - 所有 50 檔股票的風險指標摘要表
   - 買入推薦清單（包含滿足哪些條件）
   - 風險最低的前 10 檔股票排名（依夏普比率排序）
   - 整體市場趨勢總結

---

## Expected Behavior

The agent should:

1. Read and parse the 823KB CSV file completely (12,600 rows)
2. Group data by ticker (50 stocks × 252 days each)
3. For each stock, calculate:
   - Moving averages (MA5, MA20, MA60) using pandas rolling
   - RSI(14) using the standard gain/loss averaging method
   - MACD using EMA calculations
   - Bollinger Bands (20-day SMA ± 2σ)
4. Calculate risk metrics:
   - Annualized return from daily returns
   - Annualized volatility = daily_std × √252
   - Sharpe ratio = (annualized_return - 0.016) / annualized_volatility
   - Maximum drawdown from cumulative returns
5. Apply the 5 buy signal conditions to the last trading day
6. Write a comprehensive markdown report

Key verification points:
- Report should list all 50 stocks with their metrics
- Buy signal determination should be based on actual last-day values
- Sharpe ratios should range roughly from -1 to +3
- Maximum drawdowns should be negative values (typically -10% to -40%)
- At least a few stocks should qualify as "strongly recommended"

---

## Grading Criteria

- [ ] Report file `buy_signal_report.md` is created
- [ ] All 50 stocks are analyzed (none missing)
- [ ] Moving averages (MA5, MA20, MA60) are calculated correctly
- [ ] RSI(14) is calculated for each stock
- [ ] MACD components (DIF, Signal, Histogram) are present
- [ ] Annualized return and volatility are computed
- [ ] Sharpe ratio is correctly calculated (with Rf=1.6%)
- [ ] Maximum drawdown is calculated
- [ ] Buy signal conditions are applied and stocks are classified
- [ ] Risk ranking (top 10 by Sharpe) is included
- [ ] Summary table of all 50 stocks is present

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the Taiwan stock buy signal analysis task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check if report exists
    report_path = workspace / "buy_signal_report.md"
    if not report_path.exists():
        alternatives = ["buy_signal.md", "stock_analysis.md", "report.md", "analysis_report.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "all_stocks_analyzed": 0.0,
            "moving_averages": 0.0,
            "rsi_calculated": 0.0,
            "macd_calculated": 0.0,
            "annualized_metrics": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "buy_signals": 0.0,
            "risk_ranking": 0.0,
            "summary_table": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Check all 50 stocks analyzed (spot check key tickers)
    key_tickers = ['2330', '2317', '2454', '2382', '2881', '2603', '3008', '2912', '3661', '6669']
    tickers_found = sum(1 for t in key_tickers if t in content)
    scores["all_stocks_analyzed"] = min(tickers_found / 7.0, 1.0)

    # Check moving averages
    ma_patterns = [r'ma\s*5', r'ma\s*20', r'ma\s*60', r'移動平均', r'moving\s*average']
    ma_found = sum(1 for p in ma_patterns if re.search(p, content_lower))
    scores["moving_averages"] = 1.0 if ma_found >= 3 else (0.5 if ma_found >= 1 else 0.0)

    # Check RSI
    rsi_patterns = [r'rsi', r'相對強弱', r'relative\s*strength']
    has_rsi = any(re.search(p, content_lower) for p in rsi_patterns)
    # Check for actual RSI values (numbers between 0-100)
    has_rsi_values = bool(re.search(r'rsi.*?\d{1,2}\.\d', content_lower)) or bool(re.search(r'\d{1,2}\.\d.*rsi', content_lower))
    scores["rsi_calculated"] = 1.0 if (has_rsi and has_rsi_values) else (0.5 if has_rsi else 0.0)

    # Check MACD
    macd_patterns = [r'macd', r'dif', r'signal', r'histogram', r'柱狀圖']
    macd_found = sum(1 for p in macd_patterns if re.search(p, content_lower))
    scores["macd_calculated"] = 1.0 if macd_found >= 3 else (0.5 if macd_found >= 1 else 0.0)

    # Check annualized metrics
    annual_patterns = [r'年化報酬', r'annualized?\s*return', r'年化波動', r'annualized?\s*volatil']
    annual_found = sum(1 for p in annual_patterns if re.search(p, content_lower))
    # Also check for percentage values
    has_pct_values = len(re.findall(r'-?\d+\.\d+%', content)) > 10
    scores["annualized_metrics"] = 1.0 if (annual_found >= 2 and has_pct_values) else (0.5 if annual_found >= 1 else 0.0)

    # Check Sharpe ratio
    sharpe_patterns = [r'sharpe', r'夏普']
    has_sharpe = any(re.search(p, content_lower) for p in sharpe_patterns)
    # Check for 1.6% risk-free rate mention
    has_rf = bool(re.search(r'1\.6%|0\.016|無風險|risk.free', content_lower))
    scores["sharpe_ratio"] = 1.0 if (has_sharpe and has_rf) else (0.7 if has_sharpe else 0.0)

    # Check max drawdown
    mdd_patterns = [r'最大回撤', r'max(?:imum)?\s*drawdown', r'mdd']
    has_mdd = any(re.search(p, content_lower) for p in mdd_patterns)
    has_mdd_values = bool(re.search(r'-\d+\.\d+%', content))
    scores["max_drawdown"] = 1.0 if (has_mdd and has_mdd_values) else (0.5 if has_mdd else 0.0)

    # Check buy signal analysis
    signal_patterns = [r'買入', r'buy\s*signal', r'推薦', r'recommend', r'強力推薦', r'觀望']
    signal_found = sum(1 for p in signal_patterns if re.search(p, content_lower))
    # Check for condition references
    condition_patterns = [r'條件\s*[a-e]', r'condition\s*[a-e]', r'rsi\s*<\s*3[05]', r'黃金交叉', r'golden\s*cross', r'多頭排列']
    cond_found = sum(1 for p in condition_patterns if re.search(p, content_lower))
    scores["buy_signals"] = 1.0 if (signal_found >= 2 and cond_found >= 2) else (0.5 if signal_found >= 1 else 0.0)

    # Check risk ranking
    rank_patterns = [r'排名', r'rank', r'前\s*10', r'top\s*10']
    has_ranking = any(re.search(p, content_lower) for p in rank_patterns)
    scores["risk_ranking"] = 1.0 if has_ranking else 0.0

    # Check summary table (has markdown table with multiple rows)
    table_rows = re.findall(r'^\|.*\|$', content, re.MULTILINE)
    scores["summary_table"] = 1.0 if len(table_rows) >= 20 else (0.5 if len(table_rows) >= 5 else 0.0)

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

### Criterion 1: Computational Accuracy (Weight: 35%)

**Score 1.0**: All technical indicators (MA, RSI, MACD, Bollinger) and risk metrics (Sharpe, MDD, annualized vol) are calculated with correct formulas. Values are plausible given the data (e.g., RSI 0-100, Sharpe typically -2 to +3, MDD negative).
**Score 0.75**: Most calculations correct; one or two minor formula errors or implausible values.
**Score 0.5**: Some calculations correct but several have formula errors (e.g., wrong RSI method, Sharpe without √252 adjustment).
**Score 0.25**: Major calculation errors; formulas largely wrong or values fabricated.
**Score 0.0**: No calculations performed or all values are clearly fabricated.

### Criterion 2: Buy Signal Logic (Weight: 30%)

**Score 1.0**: All 5 buy conditions are correctly defined and applied to each stock's latest data. Classification (推薦/觀望) is consistent with the conditions met. The logic is transparent and verifiable.
**Score 0.75**: Buy conditions mostly correct with minor logic errors in one condition.
**Score 0.5**: Some conditions applied correctly but others are wrong or missing.
**Score 0.25**: Buy signal logic is present but largely incorrect or inconsistently applied.
**Score 0.0**: No buy signal analysis or completely fabricated recommendations.

### Criterion 3: Data Completeness (Weight: 20%)

**Score 1.0**: All 50 stocks are processed. The summary table includes every stock. No data is skipped or truncated.
**Score 0.75**: 40-49 stocks processed; minor omissions.
**Score 0.5**: 25-39 stocks processed; significant portions of data missing.
**Score 0.25**: Fewer than 25 stocks; most data missing.
**Score 0.0**: Data not read or fewer than 5 stocks analyzed.

### Criterion 4: Report Quality (Weight: 15%)

**Score 1.0**: Well-structured report with clear sections, formatted tables, methodology explanation, and actionable investment insights with caveats.
**Score 0.75**: Good structure with minor formatting issues.
**Score 0.5**: Report contains analysis but is poorly organized.
**Score 0.25**: Minimal structure; hard to follow.
**Score 0.0**: No report or report is empty.

---

## Additional Notes

This task tests:
- Handling a large CSV file (823KB, 12,600 rows)
- Complex multi-step financial calculations (EMA, RSI, MACD, Bollinger)
- Risk-adjusted return metrics (Sharpe, Sortino, MDD)
- Multi-condition logic evaluation per stock
- Generating comprehensive analysis output

The CSV uses Traditional Chinese stock names. The agent must:
1. Read ALL 12,600 rows (not just a sample)
2. Correctly implement EMA (not SMA) for MACD
3. Use the proper RSI formula (average gain / average loss, not simple difference)
4. Apply conditions to the LAST trading day's values specifically
