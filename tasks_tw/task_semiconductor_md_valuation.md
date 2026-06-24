---
id: task_semiconductor_md_valuation
name: 台灣半導體產業鏈估值與選股模型
category: markdown_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/markdown/tw_semiconductor_analysis_2024.md
    dest: tw_semiconductor_analysis_2024.md
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: new_benchmark_files
---
## Prompt

我有一份台灣半導體產業鏈的深度分析報告 `tw_semiconductor_analysis_2024.md`（含表格與公式），包含 30 家公司的：
- 財務指標（營收、毛利率、營業利益率、淨利率、EPS、ROE）
- 月度報酬率數據
- 風險指標（VaR、最大回撤、Beta、Sharpe、Sortino）
- 技術指標（MA、RSI、MACD、布林通道位置）
- 季度數據追蹤
- 現金流量表

請根據報告中的數據，建立一個**綜合估值模型**，從這 30 檔股票中選出最值得投資的個股。將結果寫入 `valuation_model_report.md`。

### 具體任務：

1. **萃取數據**：從 Markdown 表格中正確擷取所有 30 家公司的財務數據和風險指標。

2. **多因子評分模型**（請實作以下計算）：
   
   對每檔股票計算綜合分數：
   $$Score_i = 0.25 \cdot ROE_{norm} + 0.20 \cdot Growth_{norm} + 0.20 \cdot Sharpe_{norm} + 0.15 \cdot (1 - MDD_{norm}) + 0.10 \cdot Margin_{norm} + 0.10 \cdot FCF_{norm}$$
   
   其中各因子使用 min-max normalization：
   $$X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}$$

3. **風險調整排名**：
   - 排除 Beta > 1.5 的高風險股票
   - 排除最大回撤 > -30% 的股票
   - 將剩餘股票依綜合分數排序

4. **產業鏈配置建議**：
   - 從 IC設計、晶圓代工、封測、PCB/基板、設備/材料、系統代工 各選出最佳標的
   - 建議投資組合權重（考慮分散風險）
   - 計算建議組合的預期 Sharpe Ratio

5. **估值合理性檢查**：
   - 使用報告中的 EPS 與市場合理本益比（IC設計 15-25x，代工 20-30x，封測 12-18x）估算合理價
   - 標示目前低估/高估的股票

6. **輸出格式**：
   - 完整的評分表（30檔股票全列出）
   - 最終推薦清單（Top 5）含推薦理由
   - 風險提醒

---

## Expected Behavior

The agent should:

1. Parse the Markdown file and extract tabular data (financial metrics, risk indicators)
2. Handle multiple tables with different structures
3. Implement the multi-factor scoring formula with proper normalization
4. Apply exclusion criteria (Beta > 1.5, MDD > -30%)
5. Perform arithmetic calculations on extracted values
6. Generate a ranked list with justification

Key challenges:
- The Markdown contains LaTeX math formulas — agent must understand the scoring formula
- Multiple tables with different column structures
- Some data requires cross-referencing between tables (e.g., EPS from section 2 + Sharpe from section 4)
- FCF data is in a separate appendix table
- Growth rate (YoY) needs to be parsed from "+XX.X%" format

Expected output characteristics:
- All 30 stocks should be scored
- Top performers likely: 台積電 (high ROE + growth), 世芯-KY (high growth), 廣達 (AI trend), 力旺 (high margin)
- High-beta or high-MDD stocks should be excluded from final recommendations
- Portfolio suggestion should have reasonable weights (no single stock > 30%)

---

## Grading Criteria

- [ ] Report file `valuation_model_report.md` is created
- [ ] All 30 stocks are extracted and scored
- [ ] Multi-factor scoring formula is correctly implemented
- [ ] Min-max normalization is applied
- [ ] Beta and MDD exclusion criteria applied
- [ ] Scores are ranked and top picks identified
- [ ] Industry diversification in portfolio suggestion
- [ ] Valuation reasonableness check (P/E based) is included
- [ ] Calculations are traceable (show intermediate values)
- [ ] Final recommendation includes risk warnings

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the semiconductor valuation model task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "valuation_model_report.md"
    if not report_path.exists():
        alternatives = ["valuation_report.md", "report.md", "stock_valuation.md", "investment_report.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "data_extraction": 0.0,
            "scoring_formula": 0.0,
            "normalization": 0.0,
            "exclusion_criteria": 0.0,
            "ranking": 0.0,
            "portfolio_allocation": 0.0,
            "valuation_check": 0.0,
            "industry_diversity": 0.0,
            "risk_disclosure": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Check data extraction (key tickers should appear)
    key_tickers = ['2330', '2454', '3034', '2379', '3661', '3443', '2317', '2382', '6669', '3037',
                   '8046', '3711', '2303', '2345', '3529', '6488', '2325', '6239', '5274', '2458']
    tickers_found = sum(1 for t in key_tickers if t in content)
    scores["data_extraction"] = 1.0 if tickers_found >= 15 else (0.7 if tickers_found >= 10 else (0.3 if tickers_found >= 5 else 0.0))

    # Check scoring formula
    formula_patterns = [r'score', r'分數|評分', r'0\.2[05]|0\.15|0\.10', r'weight|權重']
    formula_found = sum(1 for p in formula_patterns if re.search(p, content_lower))
    scores["scoring_formula"] = 1.0 if formula_found >= 3 else (0.5 if formula_found >= 2 else 0.0)

    # Check normalization
    norm_patterns = [r'normali[zs]', r'正規化|標準化', r'min.max', r'x.?min|x.?max']
    norm_found = sum(1 for p in norm_patterns if re.search(p, content_lower))
    scores["normalization"] = 1.0 if norm_found >= 2 else (0.5 if norm_found >= 1 else 0.0)

    # Check exclusion criteria
    excl_patterns = [r'beta\s*>\s*1\.5', r'排除|exclude|filter', r'(?:mdd|回撤|drawdown)\s*>\s*-?30', r'高風險']
    excl_found = sum(1 for p in excl_patterns if re.search(p, content_lower))
    scores["exclusion_criteria"] = 1.0 if excl_found >= 2 else (0.5 if excl_found >= 1 else 0.0)

    # Check ranking
    rank_patterns = [r'排名|rank', r'top\s*[5-9]|前\s*[5-9]', r'推薦|recommend']
    rank_found = sum(1 for p in rank_patterns if re.search(p, content_lower))
    # Should have numbered list or ranked table
    has_ranked_data = bool(re.search(r'[#1-5]|第[一二三四五]', content))
    scores["ranking"] = 1.0 if (rank_found >= 2 and has_ranked_data) else (0.5 if rank_found >= 1 else 0.0)

    # Check portfolio allocation
    portfolio_patterns = [r'portfolio|投資組合|配置', r'weight|權重|比例', r'%.*%.*%']
    port_found = sum(1 for p in portfolio_patterns if re.search(p, content_lower))
    scores["portfolio_allocation"] = 1.0 if port_found >= 2 else (0.5 if port_found >= 1 else 0.0)

    # Check valuation (P/E based)
    val_patterns = [r'p/?e|本益比|per', r'合理價|fair\s*value|target', r'低估|高估|undervalue|overvalue']
    val_found = sum(1 for p in val_patterns if re.search(p, content_lower))
    scores["valuation_check"] = 1.0 if val_found >= 2 else (0.5 if val_found >= 1 else 0.0)

    # Check industry diversity
    industries = ['ic設計|ic design|fabless', '晶圓代工|foundry', '封測|封裝|osat', 'pcb|基板|substrate',
                  '設備|材料|equipment', '系統|代工|ems|odm']
    ind_found = sum(1 for p in industries if re.search(p, content_lower))
    scores["industry_diversity"] = 1.0 if ind_found >= 5 else (0.5 if ind_found >= 3 else 0.0)

    # Risk disclosure
    risk_patterns = [r'風險|risk', r'注意|caution|caveat', r'過去.*不代表|past.*not.*guarantee', r'僅供參考|不構成.*建議']
    risk_found = sum(1 for p in risk_patterns if re.search(p, content_lower))
    scores["risk_disclosure"] = 1.0 if risk_found >= 2 else (0.5 if risk_found >= 1 else 0.0)

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

### Criterion 1: Data Extraction Accuracy (Weight: 30%)

**Score 1.0**: All financial data, risk indicators, and technical metrics are correctly extracted from the Markdown tables. Values match the source document. Cross-references between tables are handled correctly.
**Score 0.75**: Most data extracted correctly; 1-2 values misread from tables.
**Score 0.5**: Some data extracted but significant portions missed or misread.
**Score 0.25**: Major data extraction errors; many values wrong.
**Score 0.0**: Data not extracted from the file or entirely fabricated.

### Criterion 2: Model Implementation (Weight: 30%)

**Score 1.0**: Multi-factor scoring formula is correctly implemented with proper normalization. Weights match the specification (0.25/0.20/0.20/0.15/0.10/0.10). Factor selection and calculation are sound. Results are reproducible.
**Score 0.75**: Formula mostly correct with minor weight or normalization errors.
**Score 0.5**: Formula partially implemented but missing factors or wrong normalization.
**Score 0.25**: Scoring attempted but methodology is fundamentally flawed.
**Score 0.0**: No quantitative scoring model implemented.

### Criterion 3: Investment Logic (Weight: 25%)

**Score 1.0**: Exclusion criteria properly applied. Portfolio diversification is thoughtful (not all in one sector). Valuation check uses reasonable P/E ranges by sector. Risk-return tradeoff is well-articulated.
**Score 0.75**: Good investment logic with minor gaps.
**Score 0.5**: Basic investment reasoning but missing key considerations.
**Score 0.25**: Investment recommendations without quantitative backing.
**Score 0.0**: No investment logic or contradictory recommendations.

### Criterion 4: Professional Quality (Weight: 15%)

**Score 1.0**: Report reads like a professional investment research note. Has disclaimer, methodology section, clear data presentation, and actionable conclusions. Tables are well-formatted.
**Score 0.75**: Good quality with minor presentation issues.
**Score 0.5**: Adequate but not professional grade.
**Score 0.25**: Poorly formatted or disorganized.
**Score 0.0**: Unusable output.

---

## Additional Notes

This task tests:
- Parsing complex Markdown with multiple table formats and LaTeX math
- Extracting numerical data from formatted tables (percentages, decimals, Chinese characters)
- Implementing a mathematical formula from LaTeX notation
- Cross-referencing data between different sections of a document
- Financial domain knowledge (P/E valuation, portfolio theory)
- Generating a structured investment analysis output

Key challenges for weaker models:
- The Markdown file is 44KB with many tables — must read completely
- LaTeX formulas define the scoring model — must interpret correctly
- Data is spread across multiple sections requiring cross-referencing
- Financial metrics have specific meaning (negative MDD is normal, higher Sharpe is better)
- Some values need sign handling (MDD is negative, but "worse" = more negative)
