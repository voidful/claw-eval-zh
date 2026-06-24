---
id: task_ecommerce_json_anomaly_detection
name: 電商詐欺與異常偵測
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

Using the e-commerce transaction data in `ecommerce_transactions_2024.json` (~637KB, 800 orders), build a **fraud detection and anomaly analysis** system. Write your findings to `anomaly_detection_report.md`.

### Analysis Requirements:

1. **Statistical Anomaly Detection**:
   - Calculate mean and standard deviation of order totals
   - Flag orders where total > mean + 2σ as "high-value anomalies"
   - Flag orders with discount_rate > 0.25 on items > NT$10,000 as "suspicious discounts"
   - Flag customers with > 3 orders in 24 hours as "velocity anomalies"
   - Compute the anomaly score: `anomaly_score = (value_zscore + discount_zscore + velocity_zscore) / 3`

2. **Customer Risk Scoring**:
   - For each customer_id, calculate:
     - Total spend
     - Order count
     - Refund rate (refunded_orders / total_orders)
     - Average rating given
     - Discount usage frequency
   - Risk score = weighted combination:
     - 0.3 × refund_rate_normalized + 0.25 × (1 - avg_rating/5) + 0.25 × discount_frequency + 0.2 × velocity_score
   - List top 20 highest-risk customers

3. **Product-Level Analysis**:
   - Which products have the highest refund rate?
   - Which product-discount combinations are most suspicious?
   - Calculate the "return on discount" for each category:
     - ROD = (discounted_revenue - refund_amount) / full_price_revenue

4. **Temporal Patterns**:
   - Identify unusual ordering patterns:
     - Late-night orders (23:00-05:00) with high values
     - Weekend bulk orders
     - Month-end spikes
   - Calculate hour-of-day distribution of anomalous orders vs normal orders

5. **City-Based Analysis**:
   - Which cities have the highest refund rates?
   - Which cities show suspicious discount patterns?
   - Are there geographic clusters of anomalies?

6. **Payment Method Risk**:
   - Refund rate by payment method
   - Average time-to-refund by payment method
   - Which payment methods are over-represented in high-value anomalies?

7. **Executive Summary**:
   - Total potential fraud loss (sum of flagged order values)
   - Number and percentage of suspicious orders
   - Top 5 recommended actions to reduce fraud
   - Monitoring rules to implement

---

## Expected Behavior

The agent should:

1. Parse the nested JSON structure (800 orders with nested items)
2. Compute statistical thresholds (mean, std of order totals)
3. Implement multiple anomaly detection criteria
4. Build customer profiles from order history
5. Calculate risk scores using the specified formula
6. Cross-reference anomalies across dimensions (time, geography, product)
7. Produce actionable recommendations

Key expected outputs:
- Order value mean: ~NT$15,000-25,000 range (due to electronics)
- About 5-10% of orders should be flagged as anomalous
- Refund rate: ~12% (7% refunded + 5% returned = 12%)
- High-value anomalies: orders > mean + 2σ (probably > NT$50,000)
- Some customers will have multiple orders (check velocity)
- Electronics category likely has highest refund value

---

## Grading Criteria

- [ ] Report file `anomaly_detection_report.md` is created
- [ ] Statistical thresholds (mean ± 2σ) are computed
- [ ] High-value anomalies are identified with list
- [ ] Customer risk scoring is implemented
- [ ] Top-20 risky customers are listed
- [ ] Product refund analysis is present
- [ ] Temporal pattern analysis is included
- [ ] City-based analysis is performed
- [ ] Payment method risk comparison
- [ ] Executive summary with actionable recommendations
- [ ] All anomaly counts are based on actual data

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the anomaly detection task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "anomaly_detection_report.md"
    if not report_path.exists():
        alternatives = ["anomaly_report.md", "fraud_report.md", "report.md", "detection_report.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "statistical_thresholds": 0.0,
            "anomaly_identification": 0.0,
            "customer_risk_scoring": 0.0,
            "product_analysis": 0.0,
            "temporal_patterns": 0.0,
            "geographic_analysis": 0.0,
            "payment_risk": 0.0,
            "executive_summary": 0.0,
            "data_driven": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Statistical thresholds
    stat_patterns = [r'mean|平均|μ', r'standard\s*deviation|標準差|σ', r'2σ|2\s*sigma|兩倍標準差']
    stat_found = sum(1 for p in stat_patterns if re.search(p, content_lower))
    has_threshold_values = bool(re.search(r'(?:NT\$|TWD|元)\s*[\d,]+', content))
    scores["statistical_thresholds"] = 1.0 if (stat_found >= 2 and has_threshold_values) else (0.5 if stat_found >= 1 else 0.0)

    # Anomaly identification
    anomaly_patterns = [r'anomal|異常', r'flag|標記|標示', r'suspicious|可疑', r'fraud|詐欺|欺詐']
    anom_found = sum(1 for p in anomaly_patterns if re.search(p, content_lower))
    # Should list specific orders or counts
    has_specifics = bool(re.search(r'ORD-\d+|order.id|訂單.*\d+', content_lower))
    scores["anomaly_identification"] = 1.0 if (anom_found >= 3 and has_specifics) else (0.5 if anom_found >= 2 else 0.0)

    # Customer risk scoring
    risk_patterns = [r'risk\s*score|風險.*分數|風險評分', r'customer|客戶|顧客', r'top.?20|前.*20', r'refund\s*rate|退款率']
    risk_found = sum(1 for p in risk_patterns if re.search(p, content_lower))
    has_customer_ids = bool(re.search(r'C\d{5}', content))
    scores["customer_risk_scoring"] = 1.0 if (risk_found >= 3 and has_customer_ids) else (0.5 if risk_found >= 2 else 0.0)

    # Product analysis
    prod_patterns = [r'product|商品|產品', r'refund.*rate|退貨率|退款率', r'category|類別', r'discount.*return|折扣.*效益']
    prod_found = sum(1 for p in prod_patterns if re.search(p, content_lower))
    scores["product_analysis"] = 1.0 if prod_found >= 3 else (0.5 if prod_found >= 1 else 0.0)

    # Temporal patterns
    time_patterns = [r'hour|小時|時段', r'night|夜間|深夜|late', r'weekend|週末|假日', r'pattern|模式|分佈']
    time_found = sum(1 for p in time_patterns if re.search(p, content_lower))
    scores["temporal_patterns"] = 1.0 if time_found >= 3 else (0.5 if time_found >= 1 else 0.0)

    # Geographic analysis
    geo_patterns = [r'city|城市|地區', r'台北|新北|台中|高雄|台南', r'geographic|地理', r'cluster|群聚']
    geo_found = sum(1 for p in geo_patterns if re.search(p, content_lower))
    scores["geographic_analysis"] = 1.0 if geo_found >= 3 else (0.5 if geo_found >= 1 else 0.0)

    # Payment risk
    pay_patterns = [r'payment|付款|支付', r'credit.card|信用卡', r'line.pay|jko|apple.pay', r'method|方式']
    pay_found = sum(1 for p in pay_patterns if re.search(p, content_lower))
    scores["payment_risk"] = 1.0 if pay_found >= 3 else (0.5 if pay_found >= 1 else 0.0)

    # Executive summary
    exec_patterns = [r'executive|摘要|總結', r'recommend|建議|行動', r'monitor|監控', r'potential.*loss|潛在.*損失']
    exec_found = sum(1 for p in exec_patterns if re.search(p, content_lower))
    scores["executive_summary"] = 1.0 if exec_found >= 3 else (0.5 if exec_found >= 1 else 0.0)

    # Data-driven (check that numbers are reasonable)
    # Should reference ~800 orders
    order_count_match = re.search(r'(\d+)\s*(?:orders?|筆|訂單)', content_lower)
    if order_count_match:
        count = int(order_count_match.group(1))
        scores["data_driven"] = 1.0 if 700 <= count <= 900 else (0.5 if 500 <= count <= 1200 else 0.0)
    else:
        # Check for other signs of real data usage
        has_real_data = len(re.findall(r'C\d{5}', content)) >= 3 or len(re.findall(r'ORD-2024-\d+', content)) >= 3
        scores["data_driven"] = 0.7 if has_real_data else 0.3

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

### Criterion 1: Anomaly Detection Methodology (Weight: 30%)

**Score 1.0**: Statistical thresholds are correctly computed (mean ± 2σ for order values). Multiple detection methods applied (value-based, velocity-based, discount-based). Anomaly scores combine multiple signals. False positive consideration is discussed.
**Score 0.75**: Good methodology with one detection method missing.
**Score 0.5**: Basic anomaly detection but missing multi-signal approach.
**Score 0.25**: Superficial anomaly identification without statistical backing.
**Score 0.0**: No anomaly detection methodology.

### Criterion 2: Customer Profiling Accuracy (Weight: 25%)

**Score 1.0**: Customer profiles correctly aggregate order history. Risk scoring formula is properly implemented with correct weights. Top-20 list shows actual high-risk patterns (high refund rate, heavy discount usage). Customer IDs are real from the data.
**Score 0.75**: Mostly correct profiling with minor aggregation errors.
**Score 0.5**: Some profiling done but risk formula incomplete.
**Score 0.25**: Customer analysis attempted but largely incorrect.
**Score 0.0**: No customer analysis.

### Criterion 3: Multi-Dimensional Analysis (Weight: 25%)

**Score 1.0**: Analysis crosses temporal, geographic, product, and payment dimensions. Identifies meaningful correlations (e.g., "late-night electronics orders with high discounts have 3x refund rate"). Patterns are specific and verifiable from data.
**Score 0.75**: Good multi-dimensional analysis with minor gaps.
**Score 0.5**: Analysis covers 2-3 dimensions but lacks cross-correlation.
**Score 0.25**: Single-dimension analysis only.
**Score 0.0**: No dimensional analysis.

### Criterion 4: Actionability (Weight: 20%)

**Score 1.0**: Recommendations are specific and implementable (e.g., "flag orders > NT$50,000 with >20% discount for manual review", "require phone verification for >3 orders/day"). Includes monitoring rules with specific thresholds. Quantifies potential fraud reduction.
**Score 0.75**: Good recommendations with minor gaps in specificity.
**Score 0.5**: General recommendations without specific thresholds.
**Score 0.25**: Vague suggestions.
**Score 0.0**: No actionable output.

---

## Additional Notes

This task tests:
- Nested JSON parsing (items within orders, optional fields)
- Statistical computation (mean, std, z-scores, percentiles)
- Customer-level aggregation from order-level data
- Multi-criteria anomaly scoring
- Cross-dimensional pattern recognition
- Domain knowledge: fraud detection in e-commerce
- Handling Chinese text in product names and cities
- Null handling (rating/review are null for many orders)

Key challenges for weaker models:
- The JSON has nested items arrays — must flatten correctly for product analysis
- refund_amount only exists for refunded/returned orders (optional field)
- Customer aggregation requires grouping by customer_id across 800 orders
- Some customers may appear only once (can't compute meaningful velocity)
- Anomaly thresholds must be computed from the data, not assumed
