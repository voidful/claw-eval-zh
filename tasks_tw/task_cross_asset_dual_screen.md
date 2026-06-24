---
id: task_cross_asset_dual_screen
name: 跨檔案雙重篩選：基本面 × 技術面整合選股
category: cross_file_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/csvs/tw_stock_2024.csv
    dest: tw_stock_2024.csv
  - source: tw/markdown/tw_semiconductor_analysis_2024.md
    dest: tw_semiconductor_analysis_2024.md
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v1
---
## Prompt

我有兩個資料檔案：
1. `tw_stock_2024.csv`：50 檔台股 2024 年全年日線價格資料（252 交易日）
2. `tw_semiconductor_analysis_2024.md`：30 家台灣半導體公司的基本面分析報告（含財務指標、風險指標等）

請同時讀取這兩個檔案，透過股票代號（ticker）將它們 Join，進行「基本面 × 技術面」雙重篩選，將結果輸出至 `dual_screen_report.md`。

---

### 第一步：從 Markdown 萃取基本面分數

從 `tw_semiconductor_analysis_2024.md` 萃取每家公司的以下指標，用於計算基本面分數：
- ROE（股東權益報酬率）
- 營收成長率（YoY Growth）
- Sharpe 比率
- 最大回撤（MDD，負值）
- 毛利率（Gross Margin）
- FCF（自由現金流）

套用以下**多因子評分模型**計算每家公司的基本面分數 F_score：

$$F\_score = 0.25 \times ROE_{norm} + 0.20 \times Growth_{norm} + 0.20 \times Sharpe_{norm} + 0.15 \times (1 - MDD_{norm}) + 0.10 \times Margin_{norm} + 0.10 \times FCF_{norm}$$

其中每個因子使用 **Min-Max 正規化**：
$$X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}$$

注意：MDD 的正規化方向——MDD 越小（越負）風險越高，所以計算 `(1 - MDD_norm)` 讓「回撤小的公司」得分更高。

---

### 第二步：從 CSV 計算技術面分數

從 `tw_stock_2024.csv` 提取這 30 家公司（依股票代號對應）的**最後一個交易日**技術指標，計算技術面分數 T_score（0~4 分，每滿足一個條件 +1 分）：

- **條件 1（RSI）**：RSI(14) < 35（超賣，計算方式：用最後 15 日收盤價計算 14 日 RSI）
  ```
  RSI = 100 - 100 / (1 + RS)
  RS = 14日平均漲幅 / 14日平均跌幅
  ```
- **條件 2（MACD）**：MACD Histogram 由負轉正（最後 5 日內出現 DIF > Signal 的交叉）
  ```
  DIF = EMA(12) - EMA(26)，Signal = EMA(9) of DIF
  ```
- **條件 3（均線趨勢）**：MA5 > MA20（短線均線在長線均線之上，多頭排列）
- **條件 4（布林位置）**：收盤價低於布林中軌（MA20 < 收盤價的情況，取近 20 日 SMA 和 2 倍標準差計算）
  - 實際條件：收盤價 < 布林下軌 + (布林中軌 - 布林下軌) × 0.3

---

### 第三步：建立雙重篩選矩陣

- **象限劃分**（以中位數為分界）：
  - **明星股（Star）**：F_score > 中位數 且 T_score > 中位數（基本面強 + 技術面強）
  - **潛力股（Value）**：F_score > 中位數 且 T_score ≤ 中位數（基本面強但技術面弱）
  - **動能股（Momentum）**：F_score ≤ 中位數 且 T_score > 中位數（技術面強但基本面弱）
  - **迴避（Avoid）**：F_score ≤ 中位數 且 T_score ≤ 中位數

---

### 第四步：「明星股」的風險調整權重

對明星股象限中的股票，計算建議投資組合權重（風險平價法）：

```
每檔股票年化波動率 σ_i = 日報酬率標準差 × √252（從 CSV 計算）
風險平價權重 w_i = (1 / σ_i) / Σ(1 / σ_j)（對所有明星股 j 加總）
```

---

### 輸出報告 `dual_screen_report.md` 需包含：

1. 資料 Join 摘要（30 家公司中有幾家成功與 CSV 對應，哪些未匹配）
2. 基本面分數表（30 家公司的 F_score，含各因子正規化值）
3. 技術面分數表（30 家公司的 T_score，含各條件是否滿足）
4. 雙重篩選矩陣（2×2 象限，各象限的股票清單）
5. 明星股投資組合（股票代號、名稱、F_score、T_score、建議權重%）
6. 與單一篩選比較：純基本面 Top 5 vs 純技術面 Top 5 vs 雙重篩選明星股的比較
7. 風險提示與免責聲明

---

## Expected Behavior

代理人應執行以下步驟：

1. 解析 44KB Markdown，提取 30 家公司的 ROE/Growth/Sharpe/MDD/Margin/FCF
2. 對 6 個因子分別做 Min-Max 正規化（注意 MDD 方向）
3. 套用加權公式計算 F_score（0~1 之間）
4. 讀取 CSV，Pivot 成寬表格，提取 30 家公司中在 CSV 內的股票（可能有幾家不在 CSV 的 50 檔中）
5. 計算每家股票最後一日的 RSI(14)、MACD histogram 符號、MA5 vs MA20、布林位置
6. 計算 T_score（0~4 整數）
7. 按 F_score 和 T_score 的中位數劃分四象限
8. 對明星股計算年化波動率和風險平價權重
9. 撰寫完整報告

Key expected challenges：
- Markdown 的 30 家公司中，部分可能不在 CSV 的 50 檔股票內（需說明未匹配情況）
- EMA 計算需要遞推（不能用簡單移動平均代替）
- MDD 正規化方向容易搞錯（MDD 是負值，更負 = 更差）
- 風險平價權重必須加總為 100%

---

## Grading Criteria

- [ ] 輸出檔案 `dual_screen_report.md` 存在
- [ ] 同時讀取了兩個輸入檔案（MD + CSV）
- [ ] 基本面分數表有 F_score 數值（基於 Markdown 資料）
- [ ] 多因子公式的權重 0.25/0.20/0.20/0.15/0.10/0.10 有被應用
- [ ] Min-Max 正規化被使用
- [ ] 技術面分數表有 T_score（0~4 整數值）
- [ ] RSI、MACD、均線、布林四個條件有被評估
- [ ] 四象限分類（明星/潛力/動能/迴避）存在
- [ ] 明星股有風險平價建議權重（加總應接近 100%）
- [ ] 有與單一篩選的比較段落
- [ ] 有免責聲明

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "dual_screen_report.md"
    if not report_path.exists():
        for alt in ["dual_screen.md", "screening_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "two_files_used": 0.0,
            "fundamental_scores": 0.0,
            "formula_weights_correct": 0.0,
            "normalization_used": 0.0,
            "technical_scores": 0.0,
            "four_quadrants": 0.0,
            "star_portfolio_weights": 0.0,
            "comparison_section": 0.0,
            "disclaimer": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Two files used
    has_csv = bool(re.search(r'tw_stock_2024|csv|price|收盤|close', content_lower))
    has_md = bool(re.search(r'semiconductor|半導體|markdown|md|roe|sharpe', content_lower))
    scores["two_files_used"] = 1.0 if (has_csv and has_md) else (0.5 if (has_csv or has_md) else 0.0)

    # Fundamental scores (F_score values between 0 and 1)
    f_scores = re.findall(r'(?:f_?score|基本面分數|fundamental).{0,50}(0\.\d{2,4})', content_lower)
    if not f_scores:
        f_scores = re.findall(r'\b0\.\d{2,4}\b', content)
    scores["fundamental_scores"] = 1.0 if len(f_scores) >= 10 else (0.5 if len(f_scores) >= 3 else 0.0)

    # Formula weights (0.25, 0.20, 0.15, 0.10)
    w25 = bool(re.search(r'0\.25', content))
    w20 = bool(re.search(r'0\.20|0\.2\b', content))
    w15 = bool(re.search(r'0\.15', content))
    w10 = bool(re.search(r'0\.10|0\.1\b', content))
    found_weights = sum([w25, w20, w15, w10])
    scores["formula_weights_correct"] = 1.0 if found_weights >= 3 else (0.5 if found_weights >= 2 else 0.0)

    # Normalization
    has_norm = bool(re.search(r'min.?max|正規化|normali[zs]', content_lower))
    scores["normalization_used"] = 1.0 if has_norm else 0.0

    # Technical scores (T_score 0-4 integers)
    t_score_vals = re.findall(r'(?:t_?score|技術面分數).{0,50}([0-4])', content_lower)
    if not t_score_vals:
        t_score_vals = re.findall(r'\b[0-4]\b', content)
    has_rsi = bool(re.search(r'rsi', content_lower))
    has_macd = bool(re.search(r'macd', content_lower))
    has_ma = bool(re.search(r'ma5|ma20|均線', content_lower))
    tech_indicators = sum([has_rsi, has_macd, has_ma])
    scores["technical_scores"] = 1.0 if (tech_indicators >= 3 and len(t_score_vals) >= 5) else (
        0.5 if tech_indicators >= 2 else 0.0)

    # Four quadrants
    quadrant_kws = ["明星", "star", "潛力", "value", "動能", "momentum", "迴避", "avoid"]
    found_q = sum(1 for kw in quadrant_kws if kw.lower() in content_lower)
    scores["four_quadrants"] = 1.0 if found_q >= 4 else (0.5 if found_q >= 2 else 0.0)

    # Star portfolio weights (percentages summing near 100%)
    pct_vals = re.findall(r'(\d+\.?\d*)\s*%', content)
    float_pcts = [float(v) for v in pct_vals if 0 < float(v) <= 100]
    has_weight_section = bool(re.search(r'權重|weight|配置|allocation', content_lower))
    scores["star_portfolio_weights"] = 1.0 if (has_weight_section and len(float_pcts) >= 5) else (
        0.5 if has_weight_section else 0.0)

    # Comparison section
    has_comparison = bool(re.search(r'比較|comparison|vs|純基本面|純技術面|single.*screen', content_lower))
    scores["comparison_section"] = 1.0 if has_comparison else 0.0

    # Disclaimer
    has_disclaimer = bool(re.search(r'免責|disclaimer|不構成|僅供參考|past.*performance|風險提示', content_lower))
    scores["disclaimer"] = 1.0 if has_disclaimer else 0.0

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

### Criterion 1: Cross-File Data Integration (Weight: 30%)

**Score 1.0**: Successfully reads and parses both files. Stock tickers correctly matched between CSV and Markdown (using 4-digit codes). Unmatched tickers explicitly reported. No data from one file fabricated to fill gaps from the other.
**Score 0.75**: Both files read; 1-2 ticker matching errors (e.g., wrong code for a company).
**Score 0.5**: Only one file fully processed; the other partially parsed or approximated.
**Score 0.25**: Both files mentioned but data integration is superficial (no actual ticker join).
**Score 0.0**: Only one file used; the other ignored.

### Criterion 2: Fundamental Scoring Accuracy (Weight: 25%)

**Score 1.0**: All 6 factors extracted from Markdown and correctly normalized (Min-Max). MDD direction correctly handled (1 - MDD_norm). Weights sum to 1.0 (0.25+0.20+0.20+0.15+0.10+0.10). F_scores are between 0 and 1.
**Score 0.75**: Formula correct but 1-2 factors have extraction errors or MDD direction wrong.
**Score 0.5**: Formula partially implemented (3-4 factors); others estimated or missing.
**Score 0.25**: Scoring attempted but formula weights clearly wrong or normalization missing.
**Score 0.0**: No fundamental scoring from actual data.

### Criterion 3: Technical Scoring & Quadrant Analysis (Weight: 25%)

**Score 1.0**: All 4 technical conditions evaluated on last trading day using correct formulas (RSI with gain/loss averaging, EMA-based MACD, proper Bollinger calculation). T_score correctly assigned 0-4. Quadrant split uses median as threshold.
**Score 0.75**: 3 of 4 conditions correctly computed; quadrant split applied.
**Score 0.5**: 2 conditions computed; others estimated or wrong formula (e.g., SMA instead of EMA for MACD).
**Score 0.25**: Technical analysis attempted but formulas largely incorrect.
**Score 0.0**: No technical scoring.

### Criterion 4: Portfolio Construction & Comparison (Weight: 20%)

**Score 1.0**: Risk parity weights computed (1/σ_i normalized). Weights sum to 100%. Comparison table shows pure fundamental vs pure technical vs dual-screen clearly differentiates the approaches. Risk disclaimer is appropriate.
**Score 0.75**: Weights computed but don't exactly sum to 100% (minor rounding). Comparison present but brief.
**Score 0.5**: Star portfolio identified but weights not computed via risk parity formula. Comparison superficial.
**Score 0.25**: Only lists star stocks without weights; no comparison.
**Score 0.0**: No portfolio construction or comparison.

---

## Additional Notes

This is the **hardest task** in the benchmark set. It requires:

1. **Cross-format data join**: Matching company names/tickers between Markdown prose/tables and CSV headers
2. **Two complex calculation pipelines**: Multi-factor fundamental scoring + multi-indicator technical scoring
3. **Data reconciliation**: Some of the 30 semiconductor companies in the MD may not be in the 50-stock CSV (need to handle gracefully)
4. **Correct formula implementations**: EMA (recursive, not SMA), RSI (Wilder's smoothing), Bollinger bands
5. **Portfolio theory**: Risk parity weighting (not equal weight, not score-proportional)

Key failure modes for weak models:
- Using full-year average return as "normal return" (look-ahead)
- Using SMA instead of EMA for MACD (common shortcut)
- Getting MDD normalization direction wrong (forgetting the 1 - MDD_norm inversion)
- Not summing weights to 100% in risk parity
- Only reading one file and ignoring the join requirement

Strong models will: correctly handle the ticker mapping, explicitly document which companies were matched/unmatched, use proper EMA calculation, and produce internally consistent scores.
