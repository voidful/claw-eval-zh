---
id: task_tw_stock_factor_backtest
name: 台灣股市多因子策略回測
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

使用 `tw_stock_2024.csv`（50檔台灣股票 2024 年日線資料），進行一個**多因子量化策略回測**。將結果寫入 `factor_backtest_report.md`。

### 策略設計與回測要求：

1. **因子計算**（對每檔股票）：
   - **動量因子 (Momentum)**：過去 20 日累計報酬率
   - **均值回歸因子 (Mean Reversion)**：(現價 - MA20) / MA20（偏離度）
   - **波動率因子 (Volatility)**：過去 20 日報酬率標準差
   - **成交量因子 (Volume)**：過去 5 日平均成交量 / 過去 20 日平均成交量（量能比）

2. **策略邏輯**（每月初重新調整一次，共 11 次調整）：
   - 每月第一個交易日，計算所有 50 檔股票的 4 個因子值
   - 將因子標準化（Z-score）
   - 綜合分數 = 0.3×動量 + 0.2×(−均值回歸) + 0.3×(−波動率) + 0.2×成交量
   - 買入：分數排名前 10 的股票（等權重，每檔 10%）
   - 賣出：持有一個月後換股

3. **回測計算**：
   - 從第 2 個月開始回測（第 1 個月用於計算因子）
   - 計算每月的投資組合報酬率
   - 計算累計報酬率曲線
   - Benchmark：50 檔等權重的 Buy & Hold

4. **績效指標**：
   - 年化報酬率
   - 年化波動率
   - 夏普比率（Rf = 1.6%）
   - 最大回撤 (MDD)
   - 勝率（多少個月跑贏 benchmark）
   - 資訊比率 (IR) = 超額報酬 / 追蹤誤差
   - Calmar Ratio = 年化報酬 / |最大回撤|

5. **因子分析**：
   - 計算每個因子的 IC (Information Coefficient)：因子值與下月報酬的相關性
   - 哪個因子最有預測力？
   - 因子之間的相關性（會不會多重共線性？）
   - 長短組合 (Long-Short)：前 10 名做多 vs 後 10 名做空，超額報酬多少？

6. **換手率分析**：
   - 每月換了幾檔股票？
   - 平均換手率是多少？
   - 若加入 0.3% 交易成本（單邊），淨報酬如何？

7. **結論**：
   - 策略是否有效？（打敗 benchmark？）
   - 哪些因子貢獻最大？
   - 策略的主要風險是什麼？
   - 可能的改進方向

---

## Expected Behavior

The agent should:

1. Read all 12,600 rows of stock data
2. Reshape into per-stock time series
3. Calculate 4 factors at each month start (11 rebalance dates)
4. Standardize factors using Z-score
5. Rank stocks by composite score
6. Calculate monthly portfolio returns for top-10 stocks
7. Compare against equal-weight benchmark
8. Compute comprehensive performance metrics

Key computational requirements:
- 20-day momentum: product of (1+r) for last 20 days, minus 1
- Mean reversion: (price - SMA20) / SMA20
- Volatility: rolling 20-day std of daily returns
- Volume ratio: SMA5(volume) / SMA20(volume)
- Z-score: (x - mean) / std across 50 stocks at each point
- Monthly portfolio return: average of 10 stocks' monthly returns

Expected output characteristics:
- Strategy should show differentiated performance vs benchmark
- IC values typically range from -0.2 to +0.2 for factors
- Average monthly turnover should be 40-80% (since selecting new top 10 each month)
- Transaction costs will eat into excess returns significantly

---

## Grading Criteria

- [ ] Report file `factor_backtest_report.md` is created
- [ ] All 4 factors are computed correctly
- [ ] Z-score standardization is applied
- [ ] Monthly rebalancing is implemented (11 periods)
- [ ] Top-10 selection per month with equal weights
- [ ] Performance metrics calculated (Sharpe, MDD, IR, Calmar)
- [ ] Benchmark comparison is present
- [ ] Factor IC analysis is included
- [ ] Turnover and transaction cost impact analyzed
- [ ] Conclusions are data-driven (not generic)

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the multi-factor backtest task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "factor_backtest_report.md"
    if not report_path.exists():
        alternatives = ["backtest_report.md", "factor_report.md", "report.md", "strategy_report.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "factor_calculation": 0.0,
            "standardization": 0.0,
            "rebalancing": 0.0,
            "performance_metrics": 0.0,
            "benchmark_comparison": 0.0,
            "factor_ic": 0.0,
            "turnover_analysis": 0.0,
            "transaction_costs": 0.0,
            "conclusions": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Factor calculation
    factor_patterns = [r'momentum|動量', r'mean\s*reversion|均值回歸', r'volatil|波動率', r'volume|成交量|量能']
    factors_found = sum(1 for p in factor_patterns if re.search(p, content_lower))
    scores["factor_calculation"] = 1.0 if factors_found >= 4 else (0.5 if factors_found >= 2 else 0.0)

    # Standardization
    std_patterns = [r'z.score|z分數|標準化', r'standardiz|正規化', r'mean.*std|平均.*標準差']
    std_found = sum(1 for p in std_patterns if re.search(p, content_lower))
    scores["standardization"] = 1.0 if std_found >= 1 else 0.0

    # Rebalancing
    rebal_patterns = [r'rebalanc|再平衡|換股|調整', r'month|月', r'top.10|前.?10|排名前']
    rebal_found = sum(1 for p in rebal_patterns if re.search(p, content_lower))
    scores["rebalancing"] = 1.0 if rebal_found >= 2 else (0.5 if rebal_found >= 1 else 0.0)

    # Performance metrics
    perf_patterns = [r'sharpe|夏普', r'(?:mdd|max.*drawdown|最大回撤)', r'年化報酬|annualized?\s*return',
                     r'calmar', r'information\s*ratio|資訊比率|ir\b']
    perf_found = sum(1 for p in perf_patterns if re.search(p, content_lower))
    scores["performance_metrics"] = 1.0 if perf_found >= 4 else (0.7 if perf_found >= 3 else (0.3 if perf_found >= 1 else 0.0))

    # Benchmark comparison
    bench_patterns = [r'benchmark|基準|對照', r'equal.weight|等權', r'buy.*hold|買入持有', r'outperform|超越|跑贏']
    bench_found = sum(1 for p in bench_patterns if re.search(p, content_lower))
    scores["benchmark_comparison"] = 1.0 if bench_found >= 2 else (0.5 if bench_found >= 1 else 0.0)

    # Factor IC
    ic_patterns = [r'ic\b|information\s*coefficient|資訊係數', r'predict|預測力', r'correlat|相關性']
    ic_found = sum(1 for p in ic_patterns if re.search(p, content_lower))
    scores["factor_ic"] = 1.0 if ic_found >= 2 else (0.5 if ic_found >= 1 else 0.0)

    # Turnover analysis
    turn_patterns = [r'turnover|換手率|周轉率', r'換.*檔|replaced|changed']
    turn_found = sum(1 for p in turn_patterns if re.search(p, content_lower))
    scores["turnover_analysis"] = 1.0 if turn_found >= 1 else 0.0

    # Transaction costs
    cost_patterns = [r'transaction\s*cost|交易成本|手續費', r'0\.3%|0\.003', r'淨報酬|net\s*return']
    cost_found = sum(1 for p in cost_patterns if re.search(p, content_lower))
    scores["transaction_costs"] = 1.0 if cost_found >= 2 else (0.5 if cost_found >= 1 else 0.0)

    # Conclusions
    concl_patterns = [r'結論|conclusion', r'有效|effective', r'改進|improve', r'風險|risk']
    concl_found = sum(1 for p in concl_patterns if re.search(p, content_lower))
    has_substance = len(content.split()) >= 500
    scores["conclusions"] = 1.0 if (concl_found >= 3 and has_substance) else (0.5 if concl_found >= 1 else 0.0)

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

### Criterion 1: Quantitative Strategy Implementation (Weight: 35%)

**Score 1.0**: All 4 factors correctly computed (20-day momentum, mean reversion ratio, rolling volatility, volume ratio). Z-score normalization properly applied across stocks. Composite score formula matches specification (0.3/0.2/0.3/0.2 weights with correct signs). Monthly rebalancing correctly selects top-10 and calculates equal-weight returns.
**Score 0.75**: Strategy mostly correct with one minor implementation error.
**Score 0.5**: Some factors and rebalancing correct but key elements missing.
**Score 0.25**: Strategy partially implemented with major errors.
**Score 0.0**: No quantitative strategy implemented.

### Criterion 2: Backtest Rigor (Weight: 30%)

**Score 1.0**: Monthly returns correctly computed without look-ahead bias. Benchmark is fairly constructed (equal-weight buy-and-hold). Performance metrics (Sharpe, MDD, IR, Calmar) use correct formulas. Transaction costs properly deducted. Results are plausible for the data.
**Score 0.75**: Mostly rigorous with one methodology issue.
**Score 0.5**: Some backtest elements correct but significant methodology gaps.
**Score 0.25**: Backtest attempted but fundamentally flawed.
**Score 0.0**: No backtest performed.

### Criterion 3: Factor Analysis Quality (Weight: 20%)

**Score 1.0**: IC values computed for each factor. Factor correlations examined. Clear identification of which factors have predictive power. Long-short spread calculated. Results are internally consistent.
**Score 0.75**: Good factor analysis with minor omissions.
**Score 0.5**: Basic factor analysis without depth.
**Score 0.25**: Superficial factor mention without quantitative analysis.
**Score 0.0**: No factor analysis.

### Criterion 4: Practical Considerations (Weight: 15%)

**Score 1.0**: Discusses turnover impact, transaction costs, strategy capacity, risk of overfitting, and specific improvement suggestions. Acknowledges limitations (short backtest period, no tail risk modeling).
**Score 0.75**: Good practical discussion with minor omissions.
**Score 0.5**: Some practical considerations mentioned.
**Score 0.25**: Generic investment caveat only.
**Score 0.0**: No practical considerations.

---

## Additional Notes

This task tests:
- Large dataset processing (823KB, 12,600 rows)
- Time-series factor calculation (rolling windows)
- Cross-sectional standardization (Z-score across stocks)
- Multi-period strategy simulation (monthly rebalancing)
- Performance attribution and factor analysis
- Transaction cost modeling
- Quantitative finance domain knowledge

This is the most demanding quantitative task. Key challenges:
- Must maintain proper alignment between dates across stocks
- Factor signs matter (negative volatility means LOW vol is good)
- Z-score must be computed cross-sectionally (across 50 stocks) not time-series
- Monthly returns must aggregate daily returns correctly
- Look-ahead bias must be avoided (factors computed on day T predict returns from day T+1)
- IC calculation requires factor-return correlation for each month

Weak models will likely:
- Confuse time-series vs cross-sectional standardization
- Make look-ahead bias errors
- Incorrectly compute monthly returns from daily data
- Skip the transaction cost analysis
- Provide generic conclusions not tied to computed results
