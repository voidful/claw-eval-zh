---
id: task_ecommerce_basic_kpi
name: 電商基礎 KPI 儀表板
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

我有一個 JSON 檔案 `ecommerce_transactions_2024.json`，包含 2024 年台灣電商平台的交易紀錄。每筆訂單含有：order_id、timestamp、customer_id、customer_city、items（含 product、category、unit_price、quantity、discount_rate、subtotal）、payment_method、status、rating、review 等欄位。

請讀取此檔案，計算以下基礎 KPI，並將結果輸出至 `basic_kpi_report.md`：

1. **訂單總覽**：
   - 總訂單數
   - 總營收（所有訂單的 `total` 欄位加總，單位 TWD）
   - 平均客單價（AOV = 總營收 / 總訂單數）
   - 最高單筆訂單金額

2. **訂單狀態分佈**：
   - 各狀態（completed / pending / cancelled / refunded / returned）的訂單數與佔比（%）

3. **熱賣商品 Top 10**：
   - 依販售總數量排行，列出前 10 名商品（product 欄位），顯示商品名稱與總銷售數量

4. **城市訂單排行 Top 10**：
   - 依訂單數量排行（customer_city 欄位），列出前 10 名城市

5. **支付方式分佈**：
   - 各支付方式（payment_method）的使用次數與佔比

6. **評分統計**：
   - 有評分訂單的平均評分（rating 欄位，僅計算非 null 的訂單）
   - 各評分（1~5 星）的訂單數

---

## Expected Behavior

代理人應執行以下步驟：

1. 讀取並解析 `ecommerce_transactions_2024.json`（注意 items 是巢狀陣列）
2. 加總 `total` 欄位計算總營收（使用訂單級別的 total，非逐項計算）
3. 計算各 status 的出現次數和百分比
4. 展開 items 陣列，按 product 名稱加總 quantity，取 Top 10
5. 按 customer_city 分組計數，取 Top 10
6. 按 payment_method 分組計數
7. 過濾 rating 非 null 的訂單，計算平均與分布

Key expected values（近似）：
- 總訂單數：800
- completed 佔比：~70%
- 台北市 / 新北市 應在城市 Top 5
- 評分平均值：3.5~4.5 之間
- 至少 5 種支付方式

---

## Grading Criteria

- [ ] 輸出檔案 `basic_kpi_report.md` 存在
- [ ] 總訂單數接近 800（±50）
- [ ] 總營收以 TWD 金額呈現（有 NT$ 或 TWD 標示）
- [ ] 各訂單狀態的數量與佔比均有列出（5 種狀態全數出現）
- [ ] 熱賣商品 Top 10 清單存在（至少 8 個商品）
- [ ] 城市排行 Top 10 清單存在（有台灣城市名稱）
- [ ] 支付方式分佈有列出（至少 3 種支付方式）
- [ ] 平均評分數值存在（介於 1~5 之間）
- [ ] 評分分布（1~5 星各自的訂單數）有列出

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "basic_kpi_report.md"
    if not report_path.exists():
        for alt in ["kpi_report.md", "ecommerce_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "order_count_correct": 0.0,
            "revenue_present": 0.0,
            "status_distribution": 0.0,
            "top10_products": 0.0,
            "city_ranking": 0.0,
            "payment_methods": 0.0,
            "rating_average": 0.0,
            "rating_distribution": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Order count near 800
    order_nums = re.findall(r'\b(7\d{2}|8\d{2})\b', content)
    scores["order_count_correct"] = 1.0 if any(750 <= int(n) <= 850 for n in order_nums) else 0.0

    # Revenue with TWD marker
    has_revenue = bool(re.search(r'(?:NT\$|TWD|NTD|元)\s*[\d,]+|[\d,]+\s*(?:元|TWD)', content))
    scores["revenue_present"] = 1.0 if has_revenue else 0.0

    # Status distribution (5 statuses)
    statuses = ["completed", "pending", "cancelled", "refunded", "returned"]
    found_status = sum(1 for s in statuses if s in content_lower)
    scores["status_distribution"] = 1.0 if found_status >= 4 else (0.5 if found_status >= 2 else 0.0)

    # Top 10 products (table rows or list items)
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
    list_items = re.findall(r'^\s*\d+[.)]\s+.{5,}', content, re.MULTILINE)
    scores["top10_products"] = 1.0 if (len(table_rows) >= 8 or len(list_items) >= 8) else (
        0.5 if (len(table_rows) >= 4 or len(list_items) >= 4) else 0.0)

    # City ranking (TW city names)
    tw_cities = ["台北", "新北", "台中", "高雄", "台南", "桃園", "新竹", "基隆", "嘉義", "彰化"]
    found_cities = sum(1 for c in tw_cities if c in content)
    scores["city_ranking"] = 1.0 if found_cities >= 4 else (0.5 if found_cities >= 2 else 0.0)

    # Payment methods (at least 3)
    payment_terms = ["credit", "line pay", "apple pay", "bank", "cash", "信用卡", "銀行", "轉帳", "jko", "街口"]
    found_pay = sum(1 for p in payment_terms if p in content_lower)
    scores["payment_methods"] = 1.0 if found_pay >= 3 else (0.5 if found_pay >= 1 else 0.0)

    # Rating average (number between 1 and 5)
    rating_matches = re.findall(r'(?:rating|評分|平均).{0,30}([1-5]\.\d+)', content_lower)
    if not rating_matches:
        rating_matches = re.findall(r'\b([3-5]\.\d{1,2})\b', content)
    scores["rating_average"] = 1.0 if rating_matches else 0.0

    # Rating distribution (numbers for 1~5 stars)
    star_mentions = re.findall(r'[1-5]\s*(?:star|星|分)[^:]*:?\s*(\d+)', content_lower)
    scores["rating_distribution"] = 1.0 if len(star_mentions) >= 3 else (0.5 if len(star_mentions) >= 1 else 0.0)

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

### Criterion 1: Data Accuracy (Weight: 35%)

**Score 1.0**: Order count is exactly 800 (or very close). Revenue total is calculated from actual `total` fields. AOV = Revenue / Orders is correctly computed. All numbers are internally consistent.
**Score 0.75**: Most numbers correct; one metric has a minor error.
**Score 0.5**: Some numbers correct but key figures (revenue, order count) have significant errors.
**Score 0.25**: Numbers appear estimated rather than calculated from data.
**Score 0.0**: Data not read or all values fabricated.

### Criterion 2: Coverage Completeness (Weight: 30%)

**Score 1.0**: All 6 sections are present with complete data. All 5 order statuses shown. Top 10 lists have exactly 10 entries. Rating distribution shows all 5 star levels.
**Score 0.75**: 5 sections complete; one section missing or partial.
**Score 0.5**: 3-4 sections present; others missing.
**Score 0.25**: Only 1-2 sections completed.
**Score 0.0**: Report missing or essentially empty.

### Criterion 3: JSON Handling (Weight: 20%)

**Score 1.0**: Correctly handles nested items array for product counts. Properly handles null ratings (excludes them from average). Uses order-level `total` field rather than re-summing items.
**Score 0.75**: Mostly correct with one data handling issue.
**Score 0.5**: Some issues with nested structure or null handling.
**Score 0.25**: Significant data handling errors.
**Score 0.0**: Failed to parse JSON correctly.

### Criterion 4: Report Format (Weight: 15%)

**Score 1.0**: Well-structured Markdown with headers, formatted tables, percentages clearly labeled, units shown (TWD).
**Score 0.75**: Good format with minor issues.
**Score 0.5**: Adequate content but poorly formatted.
**Score 0.25**: Minimal structure.
**Score 0.0**: Unusable format.

---

## Additional Notes

This task tests:
- Basic JSON parsing including nested arrays
- Simple aggregation (sum, count, mean)
- Handling null/optional fields (rating is null for many orders)
- Ranking and Top-N selection
- Markdown report generation with tables

Designed as an **easy** task: no time-series analysis, no statistical modeling, no multi-file joins. Just read, count, aggregate, and format.
