---
id: task_ecommerce_basket_association
name: 電商購物籃關聯規則挖掘
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

我有一個電商交易資料 `ecommerce_transactions_2024.json`（800 筆訂單），每筆訂單包含一個 `items` 陣列，每個商品項目有 `product`（商品名稱）和 `category`（商品類別）欄位。

請進行購物籃關聯規則挖掘，找出「哪些商品或類別常常一起被購買」，並將結果輸出至 `basket_association_report.md`。

### 第一步：資料準備

- 解析每筆訂單的 `items` 陣列
- 對同一訂單中的商品進行**去重**（同一訂單同一類別只計一次）
- 建立兩個分析層級：
  1. **類別層級**：使用 `category` 欄位
  2. **商品層級**：使用 `product` 欄位

### 第二步：計算關聯指標

對所有有序商品對 (A → B)，計算三個指標：

```
Support(A→B)    = 同時包含 A 和 B 的訂單數 / 總訂單數
Confidence(A→B) = 同時包含 A 和 B 的訂單數 / 包含 A 的訂單數
Lift(A→B)       = Confidence(A→B) / (包含 B 的訂單數 / 總訂單數)
```

注意：A→B 和 B→A 是**不同的規則**，Confidence 不對稱，應分開計算。

### 第三步：找出強關聯規則

- **類別層級**：找出 Support ≥ 0.01（至少出現在 1% 訂單中）的所有類別對，按 Lift 降序排列，取 Top 15
- **商品層級**：找出 Support ≥ 0.005 的所有商品對，按 Lift 降序排列，取 Top 10

### 第四步：計算交叉銷售潛力

對 Top 15 類別關聯對，計算：

```
交叉銷售潛力分數 = Lift × Support × 全體訂單平均金額（TWD）
```

此分數代表推薦成功時每筆訂單平均可增加的期望價值。

### 輸出報告 `basket_association_report.md` 需包含：

1. 資料概覽（總訂單數、唯一商品類別數、唯一商品數）
2. Top 15 類別關聯規則表（A→B、Support、Confidence、Lift、交叉銷售潛力分數）
3. Top 10 商品名稱關聯規則表（商品A→商品B、Support、Confidence、Lift）
4. 交叉銷售潛力分析（哪些類別組合最值得推薦，原因說明）
5. 至少 3 條基於數據的行銷應用建議

---

## Expected Behavior

代理人應執行以下步驟：

1. 讀取 JSON，展開每筆訂單的 items 陣列
2. 按訂單 ID 建立「商品集合」（同訂單同類別去重）
3. 雙重迴圈計算所有有序對 (A, B) 的共現次數
4. 套用公式計算 Support（比例，0~1）、Confidence（條件概率）、Lift
5. 過濾 Support 閾值，按 Lift 降序取 Top N
6. 計算全體訂單平均金額，套用交叉銷售潛力公式
7. 撰寫報告含所有五個部分

Key expected values（近似）：
- 商品類別數：7~10 種（electronics, clothing, food, home, sports, beauty, books, toys）
- 類別關聯的 Lift > 1 表示正相關，強關聯 Lift 可達 1.5~3.0
- Confidence 強關聯通常 > 0.25
- Support 以小數呈現（如 0.05，不是 5%）

---

## Grading Criteria

- [ ] 輸出檔案 `basket_association_report.md` 存在
- [ ] 資料概覽有總訂單數（接近 800）
- [ ] Support、Confidence、Lift 三個指標都有出現
- [ ] Top 15 類別關聯規則表有 ≥ 8 筆規則
- [ ] Top 10 商品關聯規則表有 ≥ 5 筆規則
- [ ] Lift 值合理（有 Lift > 1.0 的規則，值介於 0.5~10）
- [ ] Support 以比例（0~1）呈現而非原始計數
- [ ] 交叉銷售潛力有金額數字（TWD）
- [ ] 至少 3 條行銷建議與關聯規則結果相關
- [ ] 報告含 Markdown 表格（至少兩個）

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "basket_association_report.md"
    if not report_path.exists():
        for alt in ["association_report.md", "basket_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "data_overview": 0.0,
            "three_metrics_present": 0.0,
            "category_rules_table": 0.0,
            "product_rules_table": 0.0,
            "lift_values_valid": 0.0,
            "support_as_ratio": 0.0,
            "cross_sell_potential": 0.0,
            "marketing_suggestions": 0.0,
            "has_tables": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Data overview (order count near 800)
    order_nums = re.findall(r'\b([6-9]\d{2}|[1-9]\d{3})\b', content)
    scores["data_overview"] = 1.0 if any(700 <= int(n) <= 900 for n in order_nums) else (
        0.5 if len(order_nums) >= 1 else 0.0)

    # Three metrics present
    metrics = ["support", "confidence", "lift"]
    found_met = sum(1 for m in metrics if m in content_lower)
    scores["three_metrics_present"] = 1.0 if found_met == 3 else (0.5 if found_met >= 2 else 0.0)

    # Category rules table (at least 8 data rows)
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
    scores["category_rules_table"] = 1.0 if len(table_rows) >= 10 else (0.5 if len(table_rows) >= 5 else 0.0)

    # Product rules table (presence check)
    product_kws = ["electronics", "clothing", "food", "home", "sports", "beauty", "books", "toys",
                   "電子", "服飾", "食品", "居家", "運動", "美妝", "書籍", "玩具"]
    found_cats = sum(1 for kw in product_kws if kw in content_lower)
    scores["product_rules_table"] = 1.0 if found_cats >= 5 else (0.5 if found_cats >= 2 else 0.0)

    # Lift values valid (> 1.0 exists, all between 0.1 and 15)
    lift_vals = re.findall(r'\b([0-9]\.\d{2,4})\b', content)
    float_lifts = [float(v) for v in lift_vals if 0.1 <= float(v) <= 15]
    has_above_one = any(v > 1.0 for v in float_lifts)
    scores["lift_values_valid"] = 1.0 if (has_above_one and len(float_lifts) >= 5) else (
        0.5 if has_above_one else 0.0)

    # Support as ratio (values between 0 and 1 with 3+ decimal places)
    support_vals = re.findall(r'\b0\.\d{3,4}\b', content)
    scores["support_as_ratio"] = 1.0 if len(support_vals) >= 5 else (0.5 if len(support_vals) >= 2 else 0.0)

    # Cross-sell potential (TWD amounts)
    has_cross = bool(re.search(r'交叉銷售|cross.?sell', content_lower))
    has_money = bool(re.search(r'(?:NT\$|TWD|元)\s*[\d,]+|[\d,]+\s*(?:元|TWD)', content))
    scores["cross_sell_potential"] = 1.0 if (has_cross and has_money) else (0.5 if has_cross else 0.0)

    # Marketing suggestions (3+ actionable items)
    mkt_lines = [ln for ln in content.split('\n')
                 if re.search(r'建議|推薦|促銷|組合|recommend|strategy|campaign', ln, re.IGNORECASE)
                 and len(ln.strip()) > 15]
    scores["marketing_suggestions"] = 1.0 if len(mkt_lines) >= 3 else (0.5 if len(mkt_lines) >= 1 else 0.0)

    # Tables
    scores["has_tables"] = 1.0 if len(table_rows) >= 10 else (0.5 if len(table_rows) >= 4 else 0.0)

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

### Criterion 1: Metric Calculation Correctness (Weight: 40%)

**Score 1.0**: Support is a proportion (0~1). Confidence correctly computed as conditional probability (asymmetric: A→B ≠ B→A). Lift = Confidence / P(B) correctly derived. Multiple rules show Lift > 1 indicating genuine co-purchase patterns.
**Score 0.75**: Two of three metrics correct; one has minor formula deviation.
**Score 0.5**: Support as raw count instead of proportion, or Lift formula wrong.
**Score 0.25**: Only one metric computed; others missing.
**Score 0.0**: No metric calculation or all values identical/zero.

### Criterion 2: Rule Discovery Completeness (Weight: 25%)

**Score 1.0**: Both category-level (≥ 10 rules) and product-level (≥ 5 rules) tables present. Support filtering applied. Rules sorted by Lift. A→B and B→A treated as separate rules.
**Score 0.75**: Both levels present but rule counts slightly below target.
**Score 0.5**: Only one level (category or product) completed.
**Score 0.25**: Both levels attempted but fewer than 3 rules each.
**Score 0.0**: No association rules found.

### Criterion 3: Cross-Sell Potential Analysis (Weight: 20%)

**Score 1.0**: Formula correctly applied: Lift × Support × avg_order_value. Values are in TWD and plausible. Clear identification of top cross-sell category pairs with business rationale.
**Score 0.75**: Formula mostly correct but avg_order_value slightly off or analysis brief.
**Score 0.5**: Cross-sell section present but formula not explicitly used; values seem estimated.
**Score 0.25**: Only mentions cross-sell concept without computation.
**Score 0.0**: No cross-sell analysis.

### Criterion 4: Marketing Recommendations (Weight: 15%)

**Score 1.0**: ≥ 3 specific recommendations citing actual Lift values from the analysis (e.g., "electronics 購買者推薦 home，Lift=2.1，可設計組合優惠"). Recommendations are directly actionable.
**Score 0.75**: 3 recommendations tied to data but less specific.
**Score 0.5**: Generic cross-sell suggestions not grounded in specific Lift results.
**Score 0.25**: Vague mentions of recommendation systems.
**Score 0.0**: No marketing recommendations.

---

## Additional Notes

This task tests:
- Nested JSON flattening (items array per order)
- Set operations (deduplication within orders)
- Combinatorial pairwise counting (O(k²) per order where k = items)
- Conditional probability computation
- Asymmetric rule understanding (A→B ≠ B→A)
- Business metric formulation (cross-sell potential)

Key challenges:
- Same category appearing multiple times in one order: must deduplicate BEFORE computing co-occurrence
- With ~8 categories, category-level has only 56 directed pairs — all should be computable
- With 100+ unique products, product-level has thousands of pairs — needs Support threshold filtering
- The `items` field in JSON uses `category` (not `type` or `kind`) — need to read the actual schema
- A→B and B→A distinction: many models treat them as equal, losing the directionality of Confidence
