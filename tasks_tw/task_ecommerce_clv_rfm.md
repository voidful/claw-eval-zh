---
id: task_ecommerce_clv_rfm
name: 電商顧客 RFM 分群與 CLV 估算
category: json_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/json/ecommerce_transactions_2024.json
    dest: ecommerce_transactions_2024.json
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v1
---
## Prompt

我有一個電商交易資料檔案 `ecommerce_transactions_2024.json`，包含 2024 年全年 800 筆訂單記錄，每筆含有 customer_id、timestamp、total 等欄位。

請完成以下顧客分析，並將結果輸出至 `clv_rfm_report.md`：

### 第一步：計算每位顧客的 RFM 指標

以資料集中**最後一筆訂單的日期**作為基準日，計算每位顧客的：
- **Recency (R)**：距基準日最後一次下單的天數（天數越少越新鮮）
- **Frequency (F)**：顧客的總訂單數
- **Monetary (M)**：顧客的總消費金額（TWD，使用訂單的 `total` 欄位）

### 第二步：RFM Quintile 評分（各指標獨立評分 1~5 分）

將所有顧客依各指標分為 5 個分位：
- **R 分**：Recency 天數越少，給分越高（5 分最新鮮，1 分最久遠）
- **F 分**：Frequency 越高，給分越高（5 分最高頻）
- **M 分**：Monetary 越高，給分越高（5 分最高消費）

RFM 綜合分數 = R 分 + F 分 + M 分（範圍 3~15）

### 第三步：顧客族群分類

依照 RFM 綜合分數分群：
- **Champion**：≥ 13 分
- **Loyal**：10~12 分
- **Potential**：7~9 分
- **At-Risk**：5~6 分
- **Lost**：≤ 4 分

### 第四步：計算每位顧客的 CLV

使用以下公式：
```
CLV = (M / F) × 年化購買頻率 × 留存年數
年化購買頻率 = F / (資料涵蓋月數 / 12)
留存年數 = 1 / churn_rate，churn_rate = 0.20（留存年數 = 5 年）
```

### 輸出報告 `clv_rfm_report.md` 需包含：
1. RFM 分群摘要表（各群：人數、平均 R/F/M 值、平均 CLV）
2. 各群顧客人數（可用表格或文字呈現）
3. Top 20 高 CLV 顧客清單（顧客ID、RFM 綜合分數、族群、CLV 金額）
4. 每個族群至少一條具體的行銷行動建議

---

## Expected Behavior

代理人應執行以下步驟：

1. 解析 JSON，提取 customer_id、timestamp、total 欄位
2. 按 customer_id 聚合計算 R/F/M 三項指標
3. 對三個指標分別用分位數（20th/40th/60th/80th percentile）切分為 5 分
4. Recency 評分方向需反向（天數多的給低分）
5. 計算綜合分數並套用分群閾值
6. 計算 CLV：先算資料涵蓋的月數（約 12 個月），年化頻率 = F / 1，留存年數 = 5
7. 按 CLV 降序輸出 Top 20 清單
8. 撰寫各族群行銷建議

Key expected values：
- 顧客總數（唯一 customer_id 數）約 300~600 人
- Champion 群佔比通常 10~20%
- Top CLV 顧客的 CLV 值應顯著高於平均（3 倍以上）

---

## Grading Criteria

- [ ] 輸出檔案 `clv_rfm_report.md` 存在
- [ ] 報告包含五個 RFM 族群（Champion/Loyal/Potential/At-Risk/Lost）
- [ ] 報告呈現 Recency、Frequency、Monetary 三個指標的計算結果
- [ ] Top 20 顧客清單存在（有顧客 ID 和數值）
- [ ] CLV 計算有出現有意義的數值（非零、非 NaN）
- [ ] 各族群有人數或百分比說明
- [ ] 有行銷建議段落（至少提及 2 個不同族群的建議）
- [ ] RFM 綜合分數範圍合理（3~15 分之間有提及）
- [ ] 報告含 Markdown 表格（至少 5 行資料行）
- [ ] Recency 反向評分概念有被提及或正確應用

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "clv_rfm_report.md"
    if not report_path.exists():
        for alt in ["rfm_report.md", "customer_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "rfm_segments_present": 0.0,
            "rfm_metrics_present": 0.0,
            "top20_list": 0.0,
            "clv_values": 0.0,
            "segment_counts": 0.0,
            "marketing_suggestions": 0.0,
            "has_table": 0.0,
            "score_range_mentioned": 0.0,
            "customer_ids_present": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # RFM segments
    segments = ["champion", "loyal", "potential", "at-risk", "lost"]
    found_seg = sum(1 for s in segments if s in content_lower)
    scores["rfm_segments_present"] = 1.0 if found_seg >= 4 else (0.5 if found_seg >= 2 else 0.0)

    # RFM metric names
    metrics = ["recency", "frequency", "monetary"]
    found_met = sum(1 for m in metrics if m in content_lower)
    scores["rfm_metrics_present"] = 1.0 if found_met == 3 else (0.5 if found_met >= 2 else 0.0)

    # Top 20 list (customer IDs like C12345)
    cust_ids = re.findall(r'C\d{4,6}', content)
    scores["top20_list"] = 1.0 if len(cust_ids) >= 15 else (0.5 if len(cust_ids) >= 5 else 0.0)

    # CLV values (large numbers suggesting TWD amounts)
    clv_nums = re.findall(r'\b\d{4,8}\b', content)
    scores["clv_values"] = 1.0 if len(clv_nums) >= 10 else (0.5 if len(clv_nums) >= 3 else 0.0)

    # Segment counts (numbers near segment names)
    count_pattern = re.findall(r'(\d+)\s*(?:人|位|customers?|名)', content)
    scores["segment_counts"] = 1.0 if len(count_pattern) >= 3 else (0.5 if len(count_pattern) >= 1 else 0.0)

    # Marketing suggestions
    marketing_kws = ["建議", "行銷", "促銷", "優惠", "活動", "campaign", "recommend", "strategy", "voucher"]
    found_mkt = sum(1 for kw in marketing_kws if kw in content_lower)
    scores["marketing_suggestions"] = 1.0 if found_mkt >= 3 else (0.5 if found_mkt >= 1 else 0.0)

    # Markdown table
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
    scores["has_table"] = 1.0 if len(table_rows) >= 5 else (0.5 if len(table_rows) >= 2 else 0.0)

    # Score range mentioned (3~15)
    range_mentioned = bool(re.search(r'3\s*[~～\-]\s*15|score.*15|15.*score', content_lower))
    scores["score_range_mentioned"] = 1.0 if range_mentioned else 0.5

    # Customer IDs present
    scores["customer_ids_present"] = 1.0 if len(cust_ids) >= 5 else 0.0

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

### Criterion 1: RFM Calculation Correctness (Weight: 35%)

**Score 1.0**: R/F/M all correctly computed. Quintile scoring properly applied. Recency is correctly inversely scored (fewer days = higher score). Segment thresholds match specification.
**Score 0.75**: Two of three metrics correct; one has minor formula error.
**Score 0.5**: Metrics computed but quintile scoring or direction is wrong.
**Score 0.25**: Only one metric correct; others missing or wrong.
**Score 0.0**: No RFM computation or results completely fabricated.

### Criterion 2: CLV Formula Application (Weight: 30%)

**Score 1.0**: CLV formula correctly applied: (M/F) × annualized_frequency × retention_years. churn_rate=0.20 → retention=5 years clearly used. Values are plausible (top CLV >> average CLV).
**Score 0.75**: Formula mostly correct but one parameter slightly off (e.g., retention not annualized properly).
**Score 0.5**: CLV computed but formula simplified (e.g., CLV = M only, ignoring frequency and retention).
**Score 0.25**: CLV mentioned but not actually calculated from data.
**Score 0.0**: No CLV calculation or all values zero.

### Criterion 3: Report Completeness (Weight: 20%)

**Score 1.0**: All 4 required sections present: summary table, group counts, Top 20 list, marketing suggestions per segment.
**Score 0.75**: 3 sections complete; one missing.
**Score 0.5**: 2 sections complete.
**Score 0.25**: Only scattered numbers, no structured sections.
**Score 0.0**: Report empty or missing.

### Criterion 4: Marketing Insight Quality (Weight: 15%)

**Score 1.0**: Each segment has a specific, actionable recommendation (e.g., "Champion 群推 VIP 會員計畫", "At-Risk 群發送挽回折扣碼"). Recommendations differ by segment.
**Score 0.75**: 2-3 segments have specific suggestions; others are generic.
**Score 0.5**: Generic marketing suggestions not tied to specific segments.
**Score 0.25**: Vague mentions of marketing without actionable content.
**Score 0.0**: No marketing recommendations.

---

## Additional Notes

This task tests:
- JSON parsing and cross-order aggregation by customer_id
- Time-based calculations (recency from timestamps)
- Quintile-based scoring with directional logic
- CLV formula with multiple parameters
- Customer segmentation and labeling
- Marketing strategy recommendation per segment

Key challenges:
- Recency direction: fewer days = HIGHER score (easy to reverse)
- Annualization: need to first determine data coverage span (~12 months)
- CLV formula has three multiplied components — easy to omit one
- Some customers appear only once: F=1, so CLV = M × 1 × 5 = 5M (need to handle correctly)
