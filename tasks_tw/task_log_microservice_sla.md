---
id: task_log_microservice_sla
name: 微服務 SLA 達成率報告
category: log_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/logs/microservice_app.log
    dest: microservice_app.log
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: new_benchmark_files
---
## Prompt

Using the microservice application log `microservice_app.log` (~1.2MB, 8000+ entries), generate a comprehensive **SLA (Service Level Agreement) Compliance Report**. Write the results to `sla_compliance_report.md`.

The SLA requirements are:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Availability | 99.9% | % of requests without 5xx errors |
| Latency P95 | < 2000ms | 95th percentile of response time |
| Latency P99 | < 5000ms | 99th percentile of response time |
| Error Rate | < 1% | % of requests returning errors |
| Circuit Breaker | < 5 trips/hour | Circuit breaker activations per hour |

### Required Analysis:

1. **Per-Service SLA Metrics**:
   - For each of the 8 services, calculate:
     - Availability (1 - error_rate)
     - P50, P95, P99 latency (extract from log message latency values)
     - Error rate (ERROR entries / total entries for that service)
     - Number of circuit breaker activations
   - Flag services that VIOLATE any SLA

2. **Time-Window Analysis** (hourly buckets):
   - For each hour in the log timespan, compute:
     - Request count
     - Error count and error rate
     - Average and P95 latency
   - Identify hours that breached SLA
   - Calculate "SLA breach duration" (consecutive hours violating)

3. **Error Budget Calculation**:
   - Monthly error budget = (1 - SLA_target) × total_requests
   - For 99.9% availability: budget = 0.1% of requests allowed to fail
   - How much error budget has been consumed?
   - At current error rate, when will the budget be exhausted?

4. **Dependency Health Map**:
   - Which services depend on which? (infer from cascading errors)
   - Create a health score per service: `health = availability × (1 - p95_violation_rate)`
   - Identify the weakest link in the chain

5. **SLA Violation Incidents**:
   - List each discrete incident (consecutive period where SLA was breached)
   - For each incident: start time, duration, affected services, root cause category, impact (requests affected)

6. **Executive Dashboard** (summary table):
   - All 8 services, all SLA metrics, PASS/FAIL for each
   - Overall system SLA status
   - Trend indicator (improving/degrading)

---

## Expected Behavior

The agent should:

1. Parse all 8000+ log entries
2. Extract latency values from INFO messages (format: `latency=XXXms`)
3. Count errors by service and by hour
4. Compute percentile latencies correctly
5. Apply SLA thresholds to determine compliance
6. Calculate error budgets mathematically

Key expected findings:
- Some services will be SLA-compliant, others will not
- Error rate varies significantly by service
- Circuit breaker trips should be countable from "CircuitBreakerOpen" messages
- The overall system error rate (~12%) far exceeds the 1% SLA target
- But per-service rates may vary (some above, some below threshold)
- P95 latency should be derivable from the latency values in log messages

---

## Grading Criteria

- [ ] Report file `sla_compliance_report.md` is created
- [ ] Per-service metrics calculated for all 8 services
- [ ] Latency percentiles (P50, P95, P99) computed from actual log data
- [ ] Error rate per service calculated
- [ ] Hourly breakdown with SLA breach identification
- [ ] Error budget calculation is present and mathematically sound
- [ ] SLA pass/fail determination for each service
- [ ] Executive summary dashboard table
- [ ] Incident list with timestamps
- [ ] Health map or dependency analysis attempted

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the SLA compliance report task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "sla_compliance_report.md"
    if not report_path.exists():
        alternatives = ["sla_report.md", "compliance_report.md", "report.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "per_service_metrics": 0.0,
            "latency_percentiles": 0.0,
            "error_rates": 0.0,
            "hourly_analysis": 0.0,
            "error_budget": 0.0,
            "sla_determination": 0.0,
            "executive_dashboard": 0.0,
            "incidents": 0.0,
            "dependency_analysis": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Per-service metrics
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service',
                'inventory-service', 'notification-service', 'user-service', 'cache-layer']
    services_found = sum(1 for s in services if s in content_lower or s.replace('-', '_') in content_lower)
    scores["per_service_metrics"] = 1.0 if services_found >= 7 else (0.7 if services_found >= 5 else (0.3 if services_found >= 3 else 0.0))

    # Latency percentiles
    lat_patterns = [r'p50|p95|p99|percentile|百分位', r'\d+\s*ms', r'latency|延遲|回應時間']
    lat_found = sum(1 for p in lat_patterns if re.search(p, content_lower))
    # Should have specific ms values
    ms_values = re.findall(r'(\d+)\s*ms', content)
    has_reasonable_latency = any(100 < int(v) < 30000 for v in ms_values) if ms_values else False
    scores["latency_percentiles"] = 1.0 if (lat_found >= 2 and has_reasonable_latency) else (0.5 if lat_found >= 1 else 0.0)

    # Error rates
    has_error_rate = bool(re.search(r'error\s*rate|錯誤率', content_lower))
    has_rate_values = len(re.findall(r'\d+\.?\d*%', content)) >= 8
    scores["error_rates"] = 1.0 if (has_error_rate and has_rate_values) else (0.5 if has_error_rate else 0.0)

    # Hourly analysis
    hourly_patterns = [r'hour|小時|時段', r'bucket|區間', r'breach|違反|超標']
    hourly_found = sum(1 for p in hourly_patterns if re.search(p, content_lower))
    has_time_data = bool(re.search(r'\d{1,2}:\d{2}|\d{1,2}\s*[時h]', content_lower))
    scores["hourly_analysis"] = 1.0 if (hourly_found >= 2 and has_time_data) else (0.5 if hourly_found >= 1 else 0.0)

    # Error budget
    budget_patterns = [r'error\s*budget|錯誤預算', r'budget.*consumed|消耗|使用', r'exhaust|耗盡']
    budget_found = sum(1 for p in budget_patterns if re.search(p, content_lower))
    scores["error_budget"] = 1.0 if budget_found >= 2 else (0.5 if budget_found >= 1 else 0.0)

    # SLA determination
    sla_patterns = [r'pass|fail|通過|未通過|合格|不合格|✓|✗|❌|✅', r'99\.9%|sla\s*target|目標']
    sla_found = sum(1 for p in sla_patterns if re.search(p, content_lower))
    scores["sla_determination"] = 1.0 if sla_found >= 2 else (0.5 if sla_found >= 1 else 0.0)

    # Executive dashboard (table with all services)
    table_rows = re.findall(r'^\|.*\|$', content, re.MULTILINE)
    has_dashboard = len(table_rows) >= 10  # At least 8 services + header + separator
    scores["executive_dashboard"] = 1.0 if has_dashboard else (0.5 if len(table_rows) >= 5 else 0.0)

    # Incidents
    incident_patterns = [r'incident|事件', r'duration|持續|期間', r'start.*time|開始時間', r'affected|影響']
    inc_found = sum(1 for p in incident_patterns if re.search(p, content_lower))
    scores["incidents"] = 1.0 if inc_found >= 3 else (0.5 if inc_found >= 1 else 0.0)

    # Dependency analysis
    dep_patterns = [r'depend|依賴', r'health.*score|健康.*分數', r'chain|鏈', r'weakest|最弱']
    dep_found = sum(1 for p in dep_patterns if re.search(p, content_lower))
    scores["dependency_analysis"] = 1.0 if dep_found >= 2 else (0.5 if dep_found >= 1 else 0.0)

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

### Criterion 1: SLA Measurement Accuracy (Weight: 35%)

**Score 1.0**: All SLA metrics are correctly computed from the log data. Error rates match actual ERROR entry counts. Latency percentiles are computed from extracted values. Circuit breaker counts match "CircuitBreakerOpen" occurrences. Availability calculation is mathematically correct.
**Score 0.75**: Most metrics correct; one area has calculation errors.
**Score 0.5**: Some metrics computed from data, others appear estimated.
**Score 0.25**: Metrics mostly fabricated or grossly inaccurate.
**Score 0.0**: No actual SLA measurement performed.

### Criterion 2: SLA Framework Application (Weight: 30%)

**Score 1.0**: Correctly applies SLA thresholds, calculates error budgets, identifies breach windows, and provides clear PASS/FAIL determinations. Error budget projection (when exhausted) is mathematically sound.
**Score 0.75**: Framework mostly correct with minor threshold application errors.
**Score 0.5**: Basic SLA concepts applied but error budget or breach detection is wrong.
**Score 0.25**: SLA concepts mentioned but not properly applied.
**Score 0.0**: No SLA framework applied.

### Criterion 3: Operational Intelligence (Weight: 20%)

**Score 1.0**: Identifies dependency chains between services, correlates failures, provides health scoring, and identifies the weakest link with evidence. Incident timeline shows clear start/end of degradation periods.
**Score 0.75**: Good operational insight with minor gaps.
**Score 0.5**: Some operational analysis but limited correlation.
**Score 0.25**: Superficial operational observations.
**Score 0.0**: No operational analysis.

### Criterion 4: Reporting Quality (Weight: 15%)

**Score 1.0**: Executive-ready dashboard with clear visual indicators (✓/✗), organized sections, actionable incident list, and trend analysis. Could be presented to management.
**Score 0.75**: Good reporting with minor presentation issues.
**Score 0.5**: Adequate content but not executive-ready format.
**Score 0.25**: Poorly formatted or incomplete.
**Score 0.0**: Unusable output.

---

## Additional Notes

This task tests:
- Large log file parsing (1.2MB)
- SLA/SRE domain knowledge
- Statistical computation (percentiles from extracted latency values)
- Threshold-based compliance determination
- Error budget mathematics
- Service dependency inference
- Professional report generation with pass/fail indicators

The key distinction from task_microservice_incident_analysis:
- This task focuses on SLA compliance (structured metrics against thresholds)
- The other focuses on incident root cause (forensic investigation)
- Both use the same log file but require different analytical approaches
