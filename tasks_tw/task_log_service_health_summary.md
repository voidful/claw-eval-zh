---
id: task_log_service_health_summary
name: Microservice 服務健康摘要報告
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
source_benchmark: benchmark_v1
---
## Prompt

你有一份微服務應用的日誌檔案 `microservice_app.log`（~1.2MB，8000+ 行），格式為：

```
[timestamp] [LEVEL] [service] [request_id] message
```

服務清單：api-gateway、auth-service、order-service、payment-service、inventory-service、notification-service、user-service、cache-layer

請分析此日誌並輸出 `service_health_summary.md`，報告需包含以下內容：

1. **各服務日誌條數統計**：每個服務的總日誌條數，以及 INFO / WARN / ERROR / DEBUG 各自的數量與佔比（%）
2. **各服務錯誤率**：每個服務的錯誤率 = ERROR 條數 / 該服務總條數，以百分比呈現
3. **Queue Depth 統計**：從 WARN 訊息中找出包含 `queue depth=` 字樣的紀錄，提取每個服務的最大 queue depth 值與平均 queue depth 值
4. **HTTP Status Code 分布**：從 INFO 訊息中統計出現最多的 3 種 HTTP status code（如 200、404、500 等）
5. **服務健康狀況總表**：以 Markdown 表格呈現，欄位包含：服務名稱、總條數、錯誤率、最大 Queue Depth、健康狀態（錯誤率 < 5% 為 🟢 健康，5%~15% 為 🟡 警告，> 15% 為 🔴 危險）

---

## Expected Behavior

代理人應執行以下步驟：

1. 逐行讀取 `microservice_app.log`，解析 timestamp、LEVEL、service 欄位
2. 用 groupby 統計每個服務的每種 log level 數量
3. 計算錯誤率 = ERROR / total per service
4. 用 regex 從 WARN 訊息中提取 `queue depth=\d+` 的數值，分服務統計最大/平均
5. 從 INFO 訊息中提取 `status=\d+`，統計全局 Top 3 status code
6. 輸出格式完整的 Markdown 報告

Key expected values（近似）：
- 總日誌條數約 8,000~9,000 行
- 8 個服務均應出現在報告中
- 整體錯誤率約 10~15%
- Queue depth 最大值可能達 80~100

---

## Grading Criteria

- [ ] 輸出檔案 `service_health_summary.md` 存在
- [ ] 報告中出現所有 8 個服務名稱
- [ ] 每個服務有 INFO/WARN/ERROR/DEBUG 的佔比或數量
- [ ] 每個服務有錯誤率數值（百分比格式）
- [ ] Queue depth 統計出現（最大值或平均值）
- [ ] HTTP status code Top 3 被列出（如 200、500 等）
- [ ] 報告包含 Markdown 表格（至少 8 行資料行）
- [ ] 表格中有健康狀態標示（🟢/🟡/🔴 或文字等價）
- [ ] 數字合理（錯誤率介於 0%~100%，不出現負數）

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "service_health_summary.md"
    if not report_path.exists():
        for alt in ["health_summary.md", "service_summary.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "all_services_mentioned": 0.0,
            "log_level_breakdown": 0.0,
            "error_rate_present": 0.0,
            "queue_depth_stats": 0.0,
            "http_status_codes": 0.0,
            "has_markdown_table": 0.0,
            "health_status_labels": 0.0,
            "data_reasonableness": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # All 8 services mentioned
    services = ["api-gateway", "auth-service", "order-service", "payment-service",
                "inventory-service", "notification-service", "user-service", "cache-layer"]
    found = sum(1 for s in services if s in content_lower or s.replace("-", "_") in content_lower)
    scores["all_services_mentioned"] = round(min(found / 8.0, 1.0), 2)

    # Log level breakdown
    levels = ["info", "warn", "error", "debug"]
    found_levels = sum(1 for lv in levels if lv in content_lower)
    scores["log_level_breakdown"] = 1.0 if found_levels >= 3 else (0.5 if found_levels >= 2 else 0.0)

    # Error rate (percentage values present)
    pct_vals = re.findall(r'\d+\.?\d*\s*%', content)
    scores["error_rate_present"] = 1.0 if len(pct_vals) >= 5 else (0.5 if len(pct_vals) >= 2 else 0.0)

    # Queue depth stats
    qd_pattern = bool(re.search(r'queue\s*depth|depth\s*=\s*\d+|佇列深度', content_lower))
    scores["queue_depth_stats"] = 1.0 if qd_pattern else 0.0

    # HTTP status codes
    status_codes = re.findall(r'\b(2\d{2}|4\d{2}|5\d{2})\b', content)
    unique_codes = len(set(status_codes))
    scores["http_status_codes"] = 1.0 if unique_codes >= 2 else (0.5 if unique_codes >= 1 else 0.0)

    # Markdown table (pipe-separated rows)
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
    scores["has_markdown_table"] = 1.0 if len(table_rows) >= 8 else (0.5 if len(table_rows) >= 3 else 0.0)

    # Health status labels
    health_labels = bool(re.search(r'🟢|🟡|🔴|健康|警告|危險|healthy|warning|critical|danger', content))
    scores["health_status_labels"] = 1.0 if health_labels else 0.0

    # Data reasonableness: error rate values between 0 and 100
    all_pct = [float(v.replace('%', '').strip()) for v in re.findall(r'\d+\.?\d*\s*%', content) if float(v.replace('%', '').strip()) <= 100]
    scores["data_reasonableness"] = 1.0 if len(all_pct) >= 5 else (0.5 if len(all_pct) >= 2 else 0.0)

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

### Criterion 1: Log Parsing Coverage (Weight: 30%)

**Score 1.0**: All 8 services are correctly identified with accurate per-level counts. Error rates are computed from actual log data (values consistent with ~10-15% overall error rate).
**Score 0.75**: 6-7 services covered, minor counting discrepancies.
**Score 0.5**: 4-5 services covered or significant counting errors.
**Score 0.25**: Fewer than 4 services or counts clearly fabricated.
**Score 0.0**: No actual log parsing performed.

### Criterion 2: Queue Depth & HTTP Status Analysis (Weight: 25%)

**Score 1.0**: Queue depth correctly extracted from WARN messages with per-service max and average. Top 3 HTTP status codes correctly counted from log data.
**Score 0.75**: One of the two analyses is correct; the other has minor issues.
**Score 0.5**: Queue depth or status codes mentioned but values seem estimated.
**Score 0.25**: Minimal extraction with only partial values.
**Score 0.0**: Neither analysis performed.

### Criterion 3: Health Dashboard Quality (Weight: 30%)

**Score 1.0**: Well-formatted table with all 8 services, correct health status labels based on error rate thresholds, easy to read.
**Score 0.75**: Table present but missing 1-2 services or threshold logic slightly off.
**Score 0.5**: Table present but poorly formatted or missing health labels.
**Score 0.25**: Some tabular data but not a proper dashboard.
**Score 0.0**: No table or unusable format.

### Criterion 4: Report Clarity (Weight: 15%)

**Score 1.0**: Report is clearly sectioned, uses proper Markdown headers, numbers are internally consistent (parts sum to totals).
**Score 0.75**: Good structure with minor inconsistencies.
**Score 0.5**: Adequate content but disorganized.
**Score 0.25**: Hard to read or navigate.
**Score 0.0**: Unstructured or empty.

---

## Additional Notes

This task tests:
- Large log file parsing with regex
- Per-service grouping and aggregation
- Conditional counting (log levels per service)
- Numeric extraction from unstructured text (queue depth values)
- Threshold-based classification (health status)
- Markdown table generation

Designed as an **easy** task: no cross-service correlation, no time-series analysis, no complex formulas. A model just needs to read, count, and format.
