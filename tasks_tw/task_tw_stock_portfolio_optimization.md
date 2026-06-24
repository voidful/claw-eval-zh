---
id: task_tw_stock_portfolio_optimization
name: 台灣股市投資組合最佳化
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

使用 `tw_stock_2024.csv`（50檔台灣股票的 2024 年日線資料），請建立一個**現代投資組合理論 (Modern Portfolio Theory)** 的分析，並找出最佳投資組合配置。將結果寫入 `portfolio_optimization_report.md`。

### 分析要求：

1. **報酬率與風險矩陣**：
   - 計算每檔股票的日報酬率序列
   - 計算 50×50 的相關性矩陣（取前 20 檔最活躍股票）
   - 計算共變異數矩陣

2. **效率前緣 (Efficient Frontier) 模擬**：
   - 從 50 檔中選出前 15 檔（依夏普比率排序）
   - 隨機生成 5000 組投資組合權重（權重和 = 1，每檔 0% ~ 40%）
   - 計算每組的：年化報酬率、年化波動率、夏普比率
   - 找出：最大夏普比率組合 (Tangency Portfolio)
   - 找出：最小波動率組合 (Minimum Variance Portfolio)

3. **最佳組合細節**：
   - 列出最大夏普比率組合的每檔股票及其權重
   - 列出最小波動率組合的每檔股票及其權重
   - 計算兩個組合的：預期年報酬、年波動率、夏普比率、最大回撤

4. **風險預算分析 (Risk Budgeting)**：
   - 計算最佳組合中每檔股票對總風險的貢獻度（Marginal Risk Contribution）
   - 公式：$RC_i = w_i \cdot \frac{(\Sigma \mathbf{w})_i}{\sqrt{\mathbf{w}^T \Sigma \mathbf{w}}}$
   - 識別風險集中度是否過高（單一股票貢獻 > 30%）

5. **回測驗證 (Backtesting)**：
   - 將資料分為前 200 天（訓練）和後 52 天（測試）
   - 用訓練期數據找最佳組合
   - 計算測試期的實際表現
   - 與加權指數（50檔等權重）比較

6. **結論與建議**：
   - 最終推薦組合（考慮風險預算調整後）
   - 預期年化報酬率與風險
   - 再平衡頻率建議
   - 投資限制與免責聲明

---

## Expected Behavior

The agent should:

1. Read the entire 823KB CSV (12,600 rows)
2. Compute daily returns for all 50 stocks
3. Select top 15 by Sharpe ratio
4. Generate random portfolios (Monte Carlo simulation)
5. Identify optimal portfolios
6. Perform risk decomposition
7. Conduct a simple backtest

Expected computational approach:
- Daily returns: (close_t / close_{t-1}) - 1
- Annualized return: mean(daily_returns) × 252
- Annualized vol: std(daily_returns) × √252
- Sharpe: (annualized_return - 0.016) / annualized_vol
- Portfolio return: sum(weights × individual_returns)
- Portfolio vol: √(w^T × Σ × w)

Key expected outputs:
- Tangency portfolio Sharpe should be > individual stock max Sharpe (diversification benefit)
- Min-variance portfolio vol should be < any individual stock vol
- Risk contributions should sum to 100%
- Backtest should show whether optimization outperforms equal-weight

---

## Grading Criteria

- [ ] Report file `portfolio_optimization_report.md` is created
- [ ] Individual stock returns and volatility are calculated
- [ ] Correlation matrix for top stocks is computed
- [ ] Monte Carlo simulation with 5000 portfolios is performed
- [ ] Tangency (max Sharpe) portfolio is identified with weights
- [ ] Minimum variance portfolio is identified with weights
- [ ] Risk contribution analysis is included
- [ ] Backtest comparison (optimized vs equal-weight) is performed
- [ ] All calculations are internally consistent
- [ ] Report includes investment disclaimer

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the portfolio optimization task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "portfolio_optimization_report.md"
    if not report_path.exists():
        alternatives = ["portfolio_report.md", "optimization_report.md", "report.md", "mpt_report.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "individual_metrics": 0.0,
            "correlation_matrix": 0.0,
            "monte_carlo": 0.0,
            "tangency_portfolio": 0.0,
            "min_variance_portfolio": 0.0,
            "risk_contribution": 0.0,
            "backtest": 0.0,
            "consistency": 0.0,
            "disclaimer": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Individual metrics
    metric_patterns = [r'年化報酬|annualized?\s*return', r'年化波動|annualized?\s*volatil', r'sharpe|夏普']
    has_metrics = sum(1 for p in metric_patterns if re.search(p, content_lower))
    # Should have multiple percentage values
    pct_count = len(re.findall(r'-?\d+\.?\d*%', content))
    scores["individual_metrics"] = 1.0 if (has_metrics >= 3 and pct_count >= 15) else (0.5 if has_metrics >= 1 else 0.0)

    # Correlation matrix
    corr_patterns = [r'相關性|correlat', r'matrix|矩陣', r'共變異|covariance']
    corr_found = sum(1 for p in corr_patterns if re.search(p, content_lower))
    # Check for matrix-like data
    has_matrix = bool(re.search(r'(?:0\.\d+\s+){3,}', content)) or bool(re.search(r'\|.*0\.\d+.*\|', content))
    scores["correlation_matrix"] = 1.0 if (corr_found >= 2 and has_matrix) else (0.5 if corr_found >= 1 else 0.0)

    # Monte Carlo simulation
    mc_patterns = [r'monte\s*carlo|蒙地卡羅', r'5000|五千', r'random|隨機', r'simulation|模擬']
    mc_found = sum(1 for p in mc_patterns if re.search(p, content_lower))
    scores["monte_carlo"] = 1.0 if mc_found >= 2 else (0.5 if mc_found >= 1 else 0.0)

    # Tangency portfolio
    tang_patterns = [r'tangency|最大.*sharpe|max.*sharpe|最佳.*夏普', r'weight|權重|配置']
    tang_found = sum(1 for p in tang_patterns if re.search(p, content_lower))
    # Should have specific weight allocations
    has_weights = bool(re.search(r'\d+\.?\d*%.*\d+\.?\d*%.*\d+\.?\d*%', content))
    scores["tangency_portfolio"] = 1.0 if (tang_found >= 2 and has_weights) else (0.5 if tang_found >= 1 else 0.0)

    # Min variance portfolio
    minvar_patterns = [r'minimum\s*variance|最小.*波動|min.*var|最低.*風險']
    has_minvar = any(re.search(p, content_lower) for p in minvar_patterns)
    scores["min_variance_portfolio"] = 1.0 if has_minvar else 0.0

    # Risk contribution
    risk_patterns = [r'risk\s*(?:contribut|budget)|風險.*貢獻|風險.*預算', r'marginal|邊際']
    risk_found = sum(1 for p in risk_patterns if re.search(p, content_lower))
    scores["risk_contribution"] = 1.0 if risk_found >= 1 else 0.0

    # Backtest
    bt_patterns = [r'backtest|回測|驗證', r'train|訓練|in.sample', r'test|測試|out.of.sample', r'equal.weight|等權|比較']
    bt_found = sum(1 for p in bt_patterns if re.search(p, content_lower))
    scores["backtest"] = 1.0 if bt_found >= 3 else (0.5 if bt_found >= 2 else 0.0)

    # Internal consistency
    # Check that portfolio weights sum to ~100% (look for weight listings)
    weight_matches = re.findall(r'(\d+\.?\d*)%', content)
    if len(weight_matches) > 10:
        scores["consistency"] = 0.7  # Has numbers, hard to verify sums automatically
    else:
        scores["consistency"] = 0.3

    # Disclaimer
    discl_patterns = [r'免責|disclaimer|不構成.*建議|僅供參考|past.*performance.*not', r'風險提醒|注意事項']
    has_discl = any(re.search(p, content_lower) for p in discl_patterns)
    scores["disclaimer"] = 1.0 if has_discl else 0.0

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

### Criterion 1: Mathematical Rigor (Weight: 35%)

**Score 1.0**: Portfolio optimization is correctly implemented — covariance matrix computed from returns, portfolio variance uses matrix multiplication (w^T Σ w), Sharpe ratio correctly annualized. Risk contributions sum to total portfolio risk. All formulas are applied correctly.
**Score 0.75**: Mostly correct math with one formula error.
**Score 0.5**: Some correct calculations but key aspects wrong (e.g., portfolio vol computed as weighted avg of individual vols instead of using covariance).
**Score 0.25**: Major mathematical errors throughout.
**Score 0.0**: No quantitative optimization performed.

### Criterion 2: Optimization Quality (Weight: 30%)

**Score 1.0**: Monte Carlo generates diverse portfolios within constraints. Tangency portfolio is clearly superior (higher Sharpe than any single stock). Min-variance portfolio has lower vol than individual stocks. Results demonstrate diversification benefit.
**Score 0.75**: Optimization performed with minor issues (e.g., constraints not fully enforced).
**Score 0.5**: Optimization attempted but results are implausible (e.g., negative Sharpe for "optimal" portfolio).
**Score 0.25**: Superficial optimization; results may be fabricated.
**Score 0.0**: No optimization performed.

### Criterion 3: Backtesting Validity (Weight: 20%)

**Score 1.0**: Proper train/test split. In-sample optimization applied to out-of-sample data. Results compared fairly with benchmark. Acknowledges limitations (short test period, no transaction costs).
**Score 0.75**: Backtest performed with minor methodology issues.
**Score 0.5**: Backtest mentioned but not properly implemented.
**Score 0.25**: Cursory backtest with no meaningful comparison.
**Score 0.0**: No backtesting performed.

### Criterion 4: Practical Value (Weight: 15%)

**Score 1.0**: Recommendations are actionable with specific weights, rebalancing schedule, and constraints. Risk budget analysis provides insight into concentration risk. Disclaimer is appropriate.
**Score 0.75**: Good practical advice with minor omissions.
**Score 0.5**: Generic advice not tied to specific analysis results.
**Score 0.25**: Vague or no practical guidance.
**Score 0.0**: No actionable output.

---

## Additional Notes

This task tests:
- Large file processing (823KB CSV → 12,600 rows)
- Matrix operations (correlation matrix, covariance matrix)
- Monte Carlo simulation (random weight generation)
- Portfolio theory (efficient frontier, tangency portfolio)
- Risk decomposition (marginal risk contribution)
- Time-series splitting for backtesting
- Financial domain expertise (Sharpe ratio, annualized metrics)

This is one of the most computationally intensive tasks. The agent must:
1. Handle 50 stocks × 252 days = 12,600 data points
2. Compute a 15×15 covariance matrix
3. Generate 5000 random portfolio weight vectors
4. Track the minimum variance and maximum Sharpe points
5. Perform matrix multiplication for portfolio variance

Weaker models may struggle with:
- Correctly implementing portfolio variance (need matrix math, not simple weighted average)
- Constraint handling (weights sum to 1, each between 0-40%)
- Backtesting methodology (avoiding look-ahead bias)
- Large computation without running out of context
