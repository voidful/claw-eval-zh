---
id: task_tw_stock_correlation_sector
name: 台股相關性分析與板塊識別
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
source_benchmark: benchmark_v1
---
## Prompt

我有一個 CSV 檔案 `tw_stock_2024.csv`，包含 2024 年台灣股市 50 檔個股的每日交易資料。欄位為：date, ticker, name, open, high, low, close, volume, turnover。共 252 個交易日 × 50 檔股票（共 12,600 行）。

請計算股票相關性並識別板塊，將結果輸出至 `correlation_sector_report.md`。

### 第一步：計算日報酬率與相關性矩陣

- 計算每檔股票的日報酬率：`r_t = (close_t - close_{t-1}) / close_{t-1}`
- 計算 50×50 的皮爾森相關性矩陣
- 計算整體統計：相關性矩陣的平均值、最高值（排除對角線）、最低值

### 第二步：板塊識別（閾值聚類法）

使用以下步驟識別自然板塊：
1. 找出所有相關性 > 0.6 的股票對（A, B）
2. 用連接成分（connected components）方法：若 A 與 B 相關 > 0.6，且 B 與 C 相關 > 0.6，則 A/B/C 屬同一板塊
3. 識別出 3~6 個板塊，並根據股票代號（如 2330 台積電屬半導體）為板塊命名
4. 計算每個板塊的「板塊內平均相關性」

### 第三步：季度報酬率與板塊輪動

- 將 2024 年分為四季：Q1（1-3月）、Q2（4-6月）、Q3（7-9月）、Q4（10-12月）
- 計算每個板塊在每季的平均累積報酬率 = (季末最後一個收盤 / 季初第一個收盤) - 1
- 找出每季「表現最佳板塊」與「表現最差板塊」

### 第四步：最佳分散化股票對

- 找出相關性最低的 5 組股票對（相關係數最接近 0 或最負）
- 列出每對的股票代號、股票名稱、相關係數

### 輸出報告 `correlation_sector_report.md` 需包含：

1. 相關性矩陣摘要（平均、最高、最低相關性）
2. 板塊識別結果表（板塊名稱、成員股票代號、板塊內平均相關性）
3. 季度板塊輪動分析表（Q1~Q4 × 各板塊的累積報酬率）
4. Top 5 最低相關性股票對（含相關係數）
5. 投資洞察：如何運用分散化降低組合風險

---

## Expected Behavior

代理人應執行以下步驟：

1. 讀取全部 12,600 行 CSV 資料
2. Pivot 成寬表格（日期 × 股票），計算每列 pct_change()
3. 呼叫 `.corr()` 或 numpy corrcoef 計算 50×50 相關性矩陣
4. 過濾相關性 > 0.6 的對，執行 BFS/DFS 或 union-find 分群
5. 計算季度報酬：按季度切割日期，取首尾收盤價差
6. 展平相關性矩陣，排除對角線，排序取最低 5 對
7. 撰寫報告含所有五個部分

Key expected values：
- 相關性矩陣平均值通常 0.2~0.5
- 應識別出至少 3 個板塊（半導體、金融、傳產等）
- 最低相關性股票對的係數可能 < 0.2 甚至為負值
- 季度輪動表應有 4×3 以上的數值矩陣

---

## Grading Criteria

- [ ] 輸出檔案 `correlation_sector_report.md` 存在
- [ ] 相關性矩陣摘要有數值（最高/最低/平均相關係數）
- [ ] 識別出至少 3 個板塊並列出成員股票
- [ ] 板塊成員有台股代碼（4 位數字）
- [ ] Q1/Q2/Q3/Q4 四季報酬率數字均有出現
- [ ] 有板塊輪動描述（哪季哪板塊最佳/最差）
- [ ] 有至少 5 組最低相關性股票對，含相關係數
- [ ] 最低相關性對的係數 < 0.4（合理範圍）
- [ ] 有投資洞察或分散化建議段落
- [ ] 報告含 Markdown 表格（至少兩個）

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "correlation_sector_report.md"
    if not report_path.exists():
        for alt in ["sector_report.md", "correlation_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "correlation_summary": 0.0,
            "sector_identification": 0.0,
            "stock_codes_listed": 0.0,
            "quarterly_returns": 0.0,
            "rotation_analysis": 0.0,
            "low_corr_pairs": 0.0,
            "low_corr_values_reasonable": 0.0,
            "investment_insight": 0.0,
            "has_tables": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Correlation summary (decimal values)
    corr_vals = re.findall(r'\b0\.\d{2,4}\b', content)
    scores["correlation_summary"] = 1.0 if len(corr_vals) >= 5 else (0.5 if len(corr_vals) >= 2 else 0.0)

    # Sector identification
    sector_kws = ["板塊", "族群", "類股", "sector", "cluster", "group",
                  "半導體", "金融", "傳產", "電子", "科技", "生技"]
    found_sec = sum(1 for kw in sector_kws if kw in content)
    scores["sector_identification"] = 1.0 if found_sec >= 3 else (0.5 if found_sec >= 1 else 0.0)

    # Stock codes (4-digit TW codes)
    codes = re.findall(r'\b\d{4}\b', content)
    unique_codes = len(set(codes))
    scores["stock_codes_listed"] = 1.0 if unique_codes >= 8 else (0.5 if unique_codes >= 3 else 0.0)

    # Quarterly returns (Q1~Q4 + percentage values)
    has_quarters = bool(re.search(r'Q[1-4]|第[一二三四]季', content))
    has_pcts = len(re.findall(r'-?\d+\.?\d*\s*%', content)) >= 4
    scores["quarterly_returns"] = 1.0 if (has_quarters and has_pcts) else (0.5 if has_quarters else 0.0)

    # Rotation analysis
    rotation_kws = ["輪動", "領漲", "最佳", "最差", "rotation", "outperform", "best", "worst"]
    found_rot = sum(1 for kw in rotation_kws if kw.lower() in content_lower)
    scores["rotation_analysis"] = 1.0 if found_rot >= 2 else (0.5 if found_rot >= 1 else 0.0)

    # Low correlation pairs (5 pairs)
    pair_pattern = re.findall(r'\d{4}.{1,10}\d{4}', content)
    scores["low_corr_pairs"] = 1.0 if len(pair_pattern) >= 5 else (0.5 if len(pair_pattern) >= 2 else 0.0)

    # Low correlation values reasonable (< 0.4)
    small_corr = [float(v) for v in re.findall(r'\b(0\.[0-3]\d{1,3}|-0\.\d{2,4})\b', content)]
    scores["low_corr_values_reasonable"] = 1.0 if len(small_corr) >= 3 else (0.5 if len(small_corr) >= 1 else 0.0)

    # Investment insight
    insight_kws = ["分散", "建議", "策略", "組合", "diversif", "portfolio", "strategy", "hedge"]
    found_ins = sum(1 for kw in insight_kws if kw.lower() in content_lower)
    scores["investment_insight"] = 1.0 if found_ins >= 2 else (0.5 if found_ins >= 1 else 0.0)

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

### Criterion 1: Correlation Matrix Accuracy (Weight: 35%)

**Score 1.0**: Daily returns correctly computed with pct_change. Correlation matrix summary values (avg, max, min) are plausible (avg ~0.3-0.5 for TW stocks). Values within [-1, 1].
**Score 0.75**: Correlation computed but summary statistics have minor errors.
**Score 0.5**: Correlation computed from prices rather than returns, or values seem off.
**Score 0.25**: Correlation mentioned but no actual matrix computed.
**Score 0.0**: No correlation analysis.

### Criterion 2: Sector Clustering Quality (Weight: 30%)

**Score 1.0**: At least 3 sectors identified with >0.6 threshold logic. Each sector lists member tickers. Sector names are reasonable (e.g., 半導體 for 2330/2454). Intra-sector correlation > threshold.
**Score 0.75**: 2-3 sectors identified; naming or membership has minor issues.
**Score 0.5**: Sectors identified but logic is ad-hoc (not threshold-based); members unclear.
**Score 0.25**: Sectors mentioned without actual clustering.
**Score 0.0**: No sector identification.

### Criterion 3: Seasonal Rotation Analysis (Weight: 20%)

**Score 1.0**: Q1-Q4 returns computed for each sector. Best/worst sector per quarter clearly identified. Rotation narrative explains the pattern.
**Score 0.75**: All 4 quarters present but best/worst identification is missing for some quarters.
**Score 0.5**: Partial quarterly data (2-3 quarters); rotation analysis incomplete.
**Score 0.25**: Only annual returns; no quarterly breakdown.
**Score 0.0**: No seasonal analysis.

### Criterion 4: Diversification Insight (Weight: 15%)

**Score 1.0**: 5 low-correlation pairs listed with actual coefficient values. Investment rationale explains why low correlation improves diversification (portfolio variance formula context).
**Score 0.75**: 3-4 pairs with coefficients; rationale is adequate.
**Score 0.5**: Some pairs listed but coefficients missing or too high (>0.5).
**Score 0.25**: Mentions diversification without specific pairs.
**Score 0.0**: No diversification analysis.

---

## Additional Notes

This task tests:
- Large CSV reshaping (long → wide format)
- Pairwise correlation computation
- Graph-theoretic connected components for clustering
- Quarterly time-series aggregation
- Financial domain knowledge (sector classification by ticker)

Key challenges:
- CSV is in long format (one row per stock per day) — needs pivot before correlation
- First day of pct_change is NaN — must drop NA rows
- Connected components algorithm is not in Python stdlib — needs BFS/DFS implementation
- Quarterly boundaries: need to find first/last trading day of each quarter
- TW tickers starting with 2xxx are electronics; 28xx are financials — helps naming sectors
