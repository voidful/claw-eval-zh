---
id: task_ecommerce_json_analytics
name: 電商 JSON 交易分析
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
source_benchmark: new_benchmark_files
---
## Prompt

I have a JSON file `ecommerce_transactions_2024.json` (~637KB) containing 800 e-commerce transactions from a Taiwanese online shopping platform for 2024. Each transaction includes: order_id, timestamp, customer_id, customer_city, items (with product, category, unit_price, quantity, discount_rate, subtotal), payment_method, status, rating, review, and optionally refund info.

Please perform a comprehensive business analytics report and write the results to `ecommerce_analytics_report.md`. Your analysis must include:

1. **Revenue Analytics**:
   - Total revenue, average order value (AOV), median order value
   - Monthly revenue trend (identify growth/decline patterns)
   - Revenue by category (electronics, clothing, food, home, sports, beauty, books, toys)
   - Revenue by city — top 5 cities and their share

2. **Customer Behavior Analysis**:
   - Customer segmentation by order frequency (1 order, 2-3 orders, 4+ orders)
   - Average basket size (items per order)
   - Most popular product combinations (items frequently bought together)
   - Payment method distribution and average transaction by payment type

3. **Performance Metrics**:
   - Order completion rate (completed / total)
   - Cancellation rate and refund rate
   - Average rating and rating distribution (1-5 stars)
   - NPS estimation (% 5-star - % 1-2 star among rated orders)
   - Refund reasons breakdown

4. **Discount Effectiveness**:
   - What percentage of orders used discounts?
   - Average discount rate when applied
   - Does discount correlate with higher order value?
   - Does discount correlate with higher/lower ratings?

5. **Seasonal Patterns**:
   - Identify peak shopping months
   - Day-of-week patterns (which day has highest orders?)
   - Hour-of-day patterns
   - Category-specific seasonality (e.g., do electronics peak in November?)

6. **Cohort Analysis**:
   - Compute monthly retention (how many customers from month M also order in month M+1)
   - Identify highest-value customers (top 10 by total spend)
   - City-based spending patterns

7. **Executive Summary**:
   - Key findings (3-5 bullet points)
   - Strategic recommendations
   - Risk areas (high refund categories, declining segments)

---

## Expected Behavior

The agent should:

1. Parse the full 637KB JSON file (800 transactions with nested items)
2. Flatten item-level data for product analysis
3. Perform all calculations correctly:
   - Revenue calculations should handle the nested items structure
   - Discount rate is per-item, not per-order
   - Ratings are only present for some completed orders
   - Timestamps are ISO format and need date extraction

Key expected values (approximate):
- 800 total orders
- ~70% completion rate (based on status distribution)
- Average basket size ~1.5-2 items per order
- Most revenue from electronics category (high-value items)
- Taipei/New Taipei should be top cities
- Rating distribution skewed positive (mostly 4-5 stars)

---

## Grading Criteria

- [ ] Report file `ecommerce_analytics_report.md` is created
- [ ] Revenue total and AOV are calculated correctly
- [ ] Monthly revenue trend is shown
- [ ] Category breakdown with revenue figures
- [ ] Customer segmentation is performed
- [ ] Completion/cancellation/refund rates are accurate
- [ ] Rating analysis with distribution
- [ ] Discount effectiveness analysis present
- [ ] Seasonal/temporal patterns identified
- [ ] Executive summary with recommendations
- [ ] All calculations use actual JSON data (not fabricated)

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the e-commerce JSON analytics task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "ecommerce_analytics_report.md"
    if not report_path.exists():
        alternatives = ["analytics_report.md", "ecommerce_report.md", "report.md", "analysis.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "revenue_analysis": 0.0,
            "category_breakdown": 0.0,
            "customer_analysis": 0.0,
            "completion_rates": 0.0,
            "rating_analysis": 0.0,
            "discount_analysis": 0.0,
            "seasonal_patterns": 0.0,
            "executive_summary": 0.0,
            "data_accuracy": 0.0,
            "report_quality": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Revenue analysis
    has_revenue = bool(re.search(r'(?:total|總)\s*(?:revenue|營收|收入)', content_lower))
    has_aov = bool(re.search(r'(?:aov|average\s*order|平均訂單|客單價)', content_lower))
    # Should have TWD amounts in millions or thousands
    has_amounts = bool(re.search(r'(?:NT\$|TWD|元|NTD)\s*[\d,]+|[\d,]+\s*(?:元|TWD)', content))
    scores["revenue_analysis"] = 1.0 if (has_revenue and has_aov and has_amounts) else (0.5 if has_revenue else 0.0)

    # Category breakdown
    categories = ['electronics', 'clothing', 'food', 'home', 'sports', 'beauty', 'books', 'toys',
                  '電子', '服飾', '食品', '居家', '運動', '美妝', '書籍', '玩具']
    cats_found = sum(1 for c in categories if c in content_lower)
    scores["category_breakdown"] = 1.0 if cats_found >= 6 else (0.5 if cats_found >= 3 else 0.0)

    # Customer analysis
    customer_patterns = [r'customer|顧客|客戶', r'segment|分群|分類', r'frequency|頻率|次數', r'basket|購物車|商品數']
    cust_found = sum(1 for p in customer_patterns if re.search(p, content_lower))
    scores["customer_analysis"] = 1.0 if cust_found >= 3 else (0.5 if cust_found >= 1 else 0.0)

    # Completion rates
    rate_patterns = [r'(?:completion|完成)\s*rate|完成率', r'(?:cancel|取消)\s*rate|取消率', r'(?:refund|退款)\s*rate|退款率']
    rates_found = sum(1 for p in rate_patterns if re.search(p, content_lower))
    has_rate_values = len(re.findall(r'\d+\.?\d*%', content)) >= 3
    scores["completion_rates"] = 1.0 if (rates_found >= 2 and has_rate_values) else (0.5 if rates_found >= 1 else 0.0)

    # Rating analysis
    rating_patterns = [r'rating|評分|評價|星', r'distribution|分布|分佈', r'nps|net\s*promoter|淨推薦']
    rating_found = sum(1 for p in rating_patterns if re.search(p, content_lower))
    scores["rating_analysis"] = 1.0 if rating_found >= 2 else (0.5 if rating_found >= 1 else 0.0)

    # Discount analysis
    discount_patterns = [r'discount|折扣|優惠', r'correlat|相關|關聯', r'effective|效果|成效']
    disc_found = sum(1 for p in discount_patterns if re.search(p, content_lower))
    scores["discount_analysis"] = 1.0 if disc_found >= 2 else (0.5 if disc_found >= 1 else 0.0)

    # Seasonal patterns
    season_patterns = [r'season|季節', r'month|月', r'peak|尖峰|高峰', r'day.of.week|星期|週']
    season_found = sum(1 for p in season_patterns if re.search(p, content_lower))
    scores["seasonal_patterns"] = 1.0 if season_found >= 3 else (0.5 if season_found >= 1 else 0.0)

    # Executive summary
    summary_patterns = [r'(?:executive\s*)?summary|摘要|總結', r'recommend|建議', r'finding|發現', r'risk|風險']
    summary_found = sum(1 for p in summary_patterns if re.search(p, content_lower))
    scores["executive_summary"] = 1.0 if summary_found >= 3 else (0.5 if summary_found >= 1 else 0.0)

    # Data accuracy - check that order count is around 800
    order_match = re.search(r'(?:total|共|總)\s*(?:orders?|訂單|筆)\s*:?\s*(\d+)|(\d+)\s*(?:orders?|訂單|筆)', content_lower)
    if order_match:
        count = int(order_match.group(1) or order_match.group(2))
        scores["data_accuracy"] = 1.0 if 750 <= count <= 850 else (0.5 if 500 <= count <= 1000 else 0.0)
    else:
        scores["data_accuracy"] = 0.3  # Can't verify but might still be correct

    # Report quality
    word_count = len(content.split())
    has_tables = len(re.findall(r'^\|', content, re.MULTILINE)) >= 8
    has_sections = len(re.findall(r'^#{1,3}\s', content, re.MULTILINE)) >= 5
    scores["report_quality"] = 1.0 if (word_count >= 800 and has_tables and has_sections) else (0.5 if word_count >= 300 else 0.0)

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

### Criterion 1: Analytical Accuracy (Weight: 35%)

**Score 1.0**: Revenue calculations correctly sum nested item subtotals. Rates (completion, refund) match the actual status distribution. Category revenues are properly aggregated from item-level data. All percentages add up correctly.
**Score 0.75**: Most calculations correct; one area has minor errors.
**Score 0.5**: Some calculations correct but key metrics (e.g., revenue, AOV) have errors.
**Score 0.25**: Major calculation errors or obvious data fabrication.
**Score 0.0**: No actual data analysis performed.

### Criterion 2: Business Insight Quality (Weight: 30%)

**Score 1.0**: Provides genuine insights beyond simple statistics: identifies actionable patterns (e.g., "Electronics drive 60% of revenue but have highest refund rate"), makes specific recommendations tied to data, identifies risks and opportunities.
**Score 0.75**: Good insights with mostly data-driven recommendations.
**Score 0.5**: Basic observations but limited actionable insight.
**Score 0.25**: Generic observations not specific to this dataset.
**Score 0.0**: No insights or purely fabricated analysis.

### Criterion 3: JSON Data Handling (Weight: 20%)

**Score 1.0**: Correctly handles the nested JSON structure (transactions → items array). Properly handles null values (rating/review are null for many orders). Handles optional refund fields. Extracts timestamps correctly.
**Score 0.75**: Mostly correct with minor data handling issues.
**Score 0.5**: Some JSON structure mishandling (e.g., counting items wrong, ignoring null ratings).
**Score 0.25**: Major data structure misunderstanding.
**Score 0.0**: Failed to parse JSON or used wrong data.

### Criterion 4: Completeness (Weight: 15%)

**Score 1.0**: All 7 required analysis sections are present and thorough. Each section has quantitative data supporting conclusions.
**Score 0.75**: 5-6 sections complete.
**Score 0.5**: 3-4 sections complete.
**Score 0.25**: 1-2 sections only.
**Score 0.0**: Report missing or nearly empty.

---

## Additional Notes

This task tests:
- Parsing a large nested JSON file (637KB, 800 orders with nested items arrays)
- Handling null/optional fields (rating, review, refund_amount)
- Multi-level aggregation (order-level vs item-level metrics)
- Business analytics skills (AOV, NPS, cohort analysis, discount effectiveness)
- Temporal analysis from ISO timestamps
- Chinese text handling (city names, product names, reviews)
- Writing actionable business recommendations

The JSON has:
- 800 transactions with 1-5 items each (~1,400 total items)
- 18 Taiwan cities as customer locations
- 7 payment methods
- 5 order statuses (completed ~70%, pending ~10%, cancelled ~8%, refunded ~7%, returned ~5%)
- Ratings (1-5) only for ~40% of completed orders
- Chinese product names and reviews
