---
id: task_microservice_incident_analysis
name: 微服務日誌事故根因分析
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

I have a microservice application log file `microservice_app.log` (~1.2MB) containing 8000+ entries from a distributed system with services: api-gateway, auth-service, order-service, payment-service, inventory-service, notification-service, user-service, and cache-layer.

The log format is: `[timestamp] [LEVEL] [service] [request_id] message`

Please perform a comprehensive incident analysis and write a detailed report to `incident_report.md`. Your analysis must include:

1. **Error Rate Analysis**:
   - Calculate overall error rate (ERROR entries / total entries)
   - Calculate error rate per service
   - Identify the service with the highest error rate
   - Calculate error rate by hour — find peak error hours

2. **Incident Categorization**:
   - Group all ERROR entries by error type (TimeoutError, DatabaseError, CircuitBreakerOpen, OutOfMemoryError, RateLimitExceeded, etc.)
   - Count occurrences of each error type
   - Identify the top 3 most critical error patterns

3. **Cascading Failure Detection**:
   - Find instances where one service's error triggers errors in dependent services (use request_id correlation)
   - Identify the "root cause" service — which service's failures most often precede failures in other services?
   - Map the failure propagation chain (Service A → Service B → Service C)

4. **Performance Degradation Timeline**:
   - Analyze WARN entries for "Slow response" patterns
   - Calculate p50, p95, p99 latency from the latency values in log messages
   - Identify time windows where latency spikes occur
   - Correlate latency spikes with error rate increases

5. **Resource Exhaustion Patterns**:
   - Track "connection pool" warnings/errors over time
   - Track "memory pressure" and "OutOfMemoryError" patterns
   - Identify if there's a gradual resource leak pattern

6. **Recommendations**:
   - Based on the analysis, provide specific actionable recommendations
   - Prioritize by impact (which fix would reduce the most errors)
   - Suggest monitoring alerts that should be set up

---

## Expected Behavior

The agent should:

1. Read the entire 1.2MB log file (8000+ entries)
2. Parse the structured log format correctly
3. Calculate:
   - Overall error rate: ~12% (ERROR level entries)
   - Per-service error rates (each service should have different rates)
   - Hourly error distribution
4. Categorize errors by type from the message field
5. Attempt request_id correlation (shared request_ids across services indicate cascading failures)
6. Extract latency values from log messages using regex
7. Track resource metrics (connection pool, memory) over time
8. Write a structured report with data-driven recommendations

Key expected findings:
- ~960 ERROR entries out of 8000 total (~12%)
- CircuitBreakerOpen and TimeoutError should be the most common severe errors
- Connection pool exhaustion (DatabaseError) should correlate with TimeoutErrors
- Peak error periods should be identifiable from hourly analysis
- Some request_ids should appear in multiple services (cascading)

---

## Grading Criteria

- [ ] Report file `incident_report.md` is created
- [ ] Error rate per service is calculated with actual percentages
- [ ] Error categorization by type with counts is present
- [ ] Cascading failure analysis (request_id correlation) is attempted
- [ ] Latency percentiles (p50, p95, p99) are calculated
- [ ] Timeline/hourly analysis is included
- [ ] Resource exhaustion patterns are identified
- [ ] Actionable recommendations are provided
- [ ] Data is from actual log parsing (not fabricated)
- [ ] Numbers are internally consistent (parts add up to total)

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the microservice incident analysis task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "incident_report.md"
    if not report_path.exists():
        alternatives = ["incident_analysis.md", "report.md", "analysis.md", "log_analysis.md"]
        for alt in alternatives:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "error_rate_analysis": 0.0,
            "error_categorization": 0.0,
            "cascading_failures": 0.0,
            "latency_analysis": 0.0,
            "timeline_analysis": 0.0,
            "resource_patterns": 0.0,
            "recommendations": 0.0,
            "data_consistency": 0.0,
            "completeness": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding='utf-8')
    content_lower = content.lower()

    # Check error rate analysis
    # Should have percentage values and per-service breakdown
    services = ['api-gateway', 'auth-service', 'order-service', 'payment-service', 'inventory-service', 'notification-service', 'user-service', 'cache-layer']
    services_found = sum(1 for s in services if s in content_lower or s.replace('-', '_') in content_lower)
    has_percentages = len(re.findall(r'\d+\.?\d*%', content)) >= 5
    scores["error_rate_analysis"] = 1.0 if (services_found >= 6 and has_percentages) else (0.5 if services_found >= 3 else 0.0)

    # Check error categorization
    error_types = ['timeouterror', 'databaseerror', 'circuitbreakeropen', 'outofmemoryerror', 'ratelimitexceeded', 'connectionrefusederror', 'validationerror', 'authorizationerror']
    errors_found = sum(1 for e in error_types if e.lower() in content_lower or e.replace('error', ' error').lower() in content_lower)
    has_counts = bool(re.search(r'(?:count|次|occurrences?).*\d+|\d+.*(?:times|次|occurrences?)', content_lower))
    scores["error_categorization"] = 1.0 if (errors_found >= 5 and has_counts) else (0.5 if errors_found >= 3 else 0.0)

    # Check cascading failure analysis
    cascade_patterns = [r'cascad', r'propagat', r'chain', r'連鎖', r'request.?id', r'correlat', r'downstream', r'root\s*cause']
    cascade_found = sum(1 for p in cascade_patterns if re.search(p, content_lower))
    scores["cascading_failures"] = 1.0 if cascade_found >= 3 else (0.5 if cascade_found >= 1 else 0.0)

    # Check latency analysis
    latency_patterns = [r'p50|p95|p99|percentile|百分位', r'latency|延遲|響應時間', r'\d+\s*ms']
    latency_found = sum(1 for p in latency_patterns if re.search(p, content_lower))
    scores["latency_analysis"] = 1.0 if latency_found >= 2 else (0.5 if latency_found >= 1 else 0.0)

    # Check timeline/hourly analysis
    time_patterns = [r'hour|小時|時段', r'peak|尖峰|高峰', r'timeline|時間線']
    has_timeline = sum(1 for p in time_patterns if re.search(p, content_lower))
    # Check for actual time references
    has_time_values = bool(re.search(r'\d{1,2}:\d{2}|\d{1,2}\s*(?:時|hour|am|pm)', content_lower))
    scores["timeline_analysis"] = 1.0 if (has_timeline >= 2 and has_time_values) else (0.5 if has_timeline >= 1 else 0.0)

    # Check resource patterns
    resource_patterns = [r'connection\s*pool|連線池', r'memory|記憶體|heap', r'exhausti|耗盡|leak|洩漏', r'capacity|容量']
    resource_found = sum(1 for p in resource_patterns if re.search(p, content_lower))
    scores["resource_patterns"] = 1.0 if resource_found >= 3 else (0.5 if resource_found >= 1 else 0.0)

    # Check recommendations
    rec_patterns = [r'recommend|建議|suggestion', r'alert|監控|monitor', r'priorit|優先']
    rec_found = sum(1 for p in rec_patterns if re.search(p, content_lower))
    # Should have multiple bullet points or numbered items
    has_items = len(re.findall(r'^\s*[-*\d]', content, re.MULTILINE)) >= 5
    scores["recommendations"] = 1.0 if (rec_found >= 2 and has_items) else (0.5 if rec_found >= 1 else 0.0)

    # Data consistency check - numbers should be reasonable
    # Total entries should be around 8000
    total_match = re.search(r'(?:total|共|總)\s*(?:entries|筆|條)?\s*:?\s*(\d[\d,]*)', content_lower)
    if total_match:
        total = int(total_match.group(1).replace(',', ''))
        scores["data_consistency"] = 1.0 if 7000 <= total <= 9000 else (0.5 if 5000 <= total <= 12000 else 0.0)
    else:
        # Check if error count is reasonable (~960)
        error_match = re.search(r'error.*?(\d{3,4})|(\d{3,4}).*?error', content_lower)
        if error_match:
            val = int(error_match.group(1) or error_match.group(2))
            scores["data_consistency"] = 1.0 if 800 <= val <= 1200 else 0.5
        else:
            scores["data_consistency"] = 0.0

    # Completeness - report should be substantial
    word_count = len(content.split())
    has_tables = len(re.findall(r'^\|', content, re.MULTILINE)) >= 6
    scores["completeness"] = 1.0 if (word_count >= 500 and has_tables) else (0.5 if word_count >= 200 else 0.0)

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

### Criterion 1: Analytical Depth (Weight: 35%)

**Score 1.0**: Analysis demonstrates genuine log parsing — correct error counts, proper service breakdown, actual request_id correlation, and plausible latency percentiles derived from data. All numbers are internally consistent.
**Score 0.75**: Most analysis is data-driven with one or two areas where values seem estimated rather than calculated.
**Score 0.5**: Some analysis is clearly from the data but other sections appear to be generic/templated rather than specific to this log file.
**Score 0.25**: Analysis is mostly generic with few data-specific findings.
**Score 0.0**: Analysis is entirely fabricated or template-based without actual log parsing.

### Criterion 2: Root Cause Identification (Weight: 30%)

**Score 1.0**: Correctly identifies cascading failure patterns, correlates errors across services using request_ids, identifies the primary failing service, and explains the propagation mechanism with evidence.
**Score 0.75**: Good root cause analysis with minor gaps in correlation evidence.
**Score 0.5**: Identifies some patterns but doesn't fully connect the dots between services.
**Score 0.25**: Mentions root cause concept but analysis is superficial.
**Score 0.0**: No root cause analysis or completely incorrect conclusions.

### Criterion 3: Actionable Recommendations (Weight: 20%)

**Score 1.0**: Recommendations are specific (e.g., "increase connection pool from 100 to 200"), prioritized by impact, and directly tied to findings. Includes monitoring thresholds.
**Score 0.75**: Good recommendations but missing prioritization or specifics.
**Score 0.5**: Generic recommendations that could apply to any system.
**Score 0.25**: Vague recommendations with no connection to findings.
**Score 0.0**: No recommendations provided.

### Criterion 4: Report Structure (Weight: 15%)

**Score 1.0**: Well-organized with clear sections, data tables, timeline visualization, and executive summary. Easy to navigate and act upon.
**Score 0.75**: Good structure with minor formatting issues.
**Score 0.5**: Contains analysis but poorly organized.
**Score 0.25**: Disorganized or incomplete.
**Score 0.0**: No report or unusable format.

---

## Additional Notes

This task tests:
- Parsing a large (1.2MB) semi-structured log file
- Multi-dimensional analysis (by service, by time, by error type)
- Correlation analysis (shared request_ids across service failures)
- Statistical computation (percentiles from extracted values)
- Pattern recognition (resource exhaustion trends, cascading failures)
- Practical incident response skills (prioritized recommendations)

The log file has:
- 8 different services
- 4 log levels (INFO 60%, WARN 20%, ERROR 12%, DEBUG 8%)
- Structured messages with extractable metrics (latency, connection counts, memory %)
- Request IDs that span multiple services
- Stack traces for 30% of errors
