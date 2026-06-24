---
id: task_log_capacity_planning
name: 微服務容量規劃分析
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

我有一份微服務應用日誌 `microservice_app.log`（~1.2MB，8000+ 行），格式為：

```
[timestamp] [LEVEL] [service] [request_id] message
```

請進行容量規劃分析，並輸出報告 `capacity_planning_report.md`，包含以下內容：

### 第一步：每小時請求量統計

- 從 INFO/WARN/ERROR 日誌中統計每個服務每小時的請求數
- 找出每個服務的「峰值小時」（請求量最高的 1 小時）及峰值請求數
- 計算每個服務的「平均每小時請求數」

### 第二步：佇列使用率萃取

- 從 WARN 訊息中找出包含 `Request queue depth=X | max=Y` 格式的紀錄
- 計算每筆紀錄的使用率 = X / Y × 100%
- 統計每個服務的：平均佇列使用率、最大佇列使用率

### 第三步：負載趨勢判斷

- 將日誌的整體時間範圍對半切分為「前半段」與「後半段」
- 比較每個服務在前後半段的平均每小時請求數
- 判定趨勢：
  - 後半段平均 > 前半段平均 × 1.1 → **增長（Growing）**
  - 後半段平均 < 前半段平均 × 0.9 → **下降（Declining）**
  - 否則 → **穩定（Stable）**

### 第四步：容量建議

使用以下公式計算每個服務的「建議容量倍數」：

```
建議容量倍數 = max(最大佇列使用率, 峰值RPS / 平均RPS) / 0.70

若服務趨勢為「增長」，建議容量倍數額外 × 1.2（安全係數）
```

- 建議容量倍數 < 1.0：當前容量充足
- 建議容量倍數 ≥ 1.0 且 < 1.5：建議近期擴容
- 建議容量倍數 ≥ 1.5：需要立即擴容

### 輸出報告 `capacity_planning_report.md` 需包含：

1. 各服務每小時請求量摘要表（峰值小時、峰值請求數、平均每小時請求數）
2. 各服務佇列使用率統計表（平均使用率%、最大使用率%）
3. 各服務負載趨勢判斷結果
4. 容量建議表（建議容量倍數、擴容優先級）
5. 優先處理清單（建議容量倍數最高的前 3 個服務）

---

## Expected Behavior

代理人應執行以下步驟：

1. 解析 log 的時間戳記格式（ISO 8601 格式）
2. 按「服務 × 小時」分組統計請求數
3. 用 regex 提取 `queue depth=(\d+)` 和 `max=(\d+)`，計算使用率
4. 計算整體時間範圍，對半切分，比較前後段均值
5. 套用容量公式，增長服務乘以 1.2
6. 按建議容量倍數排序，輸出 Top 3 優先清單

Key expected patterns in log：
- 時間戳記格式：`2024-11-15T00:00:09.472Z`
- WARN 格式：`Request queue depth=94 | max=500 | endpoint=...`
- 8 個不同服務名稱
- 日誌橫跨多個小時

---

## Grading Criteria

- [ ] 輸出檔案 `capacity_planning_report.md` 存在
- [ ] 報告有每小時請求量統計（有小時格式的時間標記）
- [ ] 報告有 queue depth 使用率的計算結果（有百分比數字）
- [ ] 正確提取 `depth=X` 與 `max=Y` 的數值
- [ ] 報告有前後半段的負載趨勢判斷（增長/穩定/下降）
- [ ] 報告有 target utilization = 70% 的概念應用
- [ ] 報告有建議容量倍數的數值
- [ ] 有優先處理清單（前 3 名需擴容服務）
- [ ] 至少識別出 5 個以上服務名稱
- [ ] 報告含 Markdown 表格（至少兩個表格）

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "capacity_planning_report.md"
    if not report_path.exists():
        for alt in ["capacity_report.md", "planning_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "hourly_stats": 0.0,
            "queue_utilization": 0.0,
            "depth_values_extracted": 0.0,
            "trend_analysis": 0.0,
            "target_utilization": 0.0,
            "capacity_multiplier": 0.0,
            "priority_list": 0.0,
            "service_coverage": 0.0,
            "has_tables": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Hourly stats (time references)
    has_hourly = bool(re.search(r'\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}|每小時|hourly|per.?hour', content_lower))
    scores["hourly_stats"] = 1.0 if has_hourly else 0.0

    # Queue utilization (percentage values)
    pct_vals = re.findall(r'\d+\.?\d*\s*%', content)
    scores["queue_utilization"] = 1.0 if len(pct_vals) >= 5 else (0.5 if len(pct_vals) >= 2 else 0.0)

    # Depth values extracted
    depth_extracted = bool(re.search(r'depth\s*[=:]\s*\d+|queue.*?\d+\s*/\s*\d+', content_lower))
    scores["depth_values_extracted"] = 1.0 if depth_extracted else 0.0

    # Trend analysis
    trend_kws = ["增長", "穩定", "下降", "growing", "stable", "declining", "increasing", "decreasing"]
    found_trends = sum(1 for kw in trend_kws if kw.lower() in content_lower)
    scores["trend_analysis"] = 1.0 if found_trends >= 2 else (0.5 if found_trends >= 1 else 0.0)

    # Target utilization 70%
    has_70pct = bool(re.search(r'70\s*%|target.{0,20}70|0\.7\b', content_lower))
    scores["target_utilization"] = 1.0 if has_70pct else 0.5

    # Capacity multiplier (decimal numbers like 1.4x)
    multipliers = re.findall(r'\b([1-9]\.\d+)\s*[xX倍]?\b', content)
    scores["capacity_multiplier"] = 1.0 if len(multipliers) >= 3 else (0.5 if len(multipliers) >= 1 else 0.0)

    # Priority list
    has_priority = bool(re.search(r'優先|priority|top.?3|前三|立即擴容|immediate', content_lower))
    scores["priority_list"] = 1.0 if has_priority else 0.0

    # Service coverage
    services = ["api-gateway", "auth-service", "order-service", "payment-service",
                "inventory-service", "notification-service", "user-service", "cache-layer"]
    found_svc = sum(1 for s in services if s in content_lower or s.replace("-", "_") in content_lower)
    scores["service_coverage"] = 1.0 if found_svc >= 6 else (0.5 if found_svc >= 3 else 0.0)

    # Tables
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
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

### Criterion 1: Log Parsing & Metric Extraction (Weight: 35%)

**Score 1.0**: Correctly parses timestamps to hour buckets. Per-service hourly request counts are accurate. Queue depth extracted correctly from `depth=X | max=Y` pattern. Utilization = X/Y × 100% computed for all services with WARN messages.
**Score 0.75**: Hourly parsing mostly correct; queue depth extraction has minor issues.
**Score 0.5**: One of the two extractions (hourly or queue depth) is correct; the other is estimated.
**Score 0.25**: Only service names identified; no meaningful numeric extraction.
**Score 0.0**: No log parsing performed.

### Criterion 2: Trend Analysis & Capacity Formula (Weight: 35%)

**Score 1.0**: Correct time-range bisection for front/back half comparison. 1.1/0.9 thresholds correctly applied for trend classification. Capacity formula used correctly: max(utilization, peak/avg) / 0.70, with ×1.2 for growing services.
**Score 0.75**: Trend direction correct but capacity formula missing the ×1.2 safety factor.
**Score 0.5**: Trend analysis attempted but method is coarse (e.g., only comparing endpoints not averages). Capacity formula partially correct.
**Score 0.25**: Only qualitative trend descriptions; no quantitative formula.
**Score 0.0**: No trend or capacity analysis.

### Criterion 3: Report Structure (Weight: 20%)

**Score 1.0**: All 5 required sections present with proper Markdown tables. Priority list clearly identifies top 3 services with specific multiplier values and urgency levels.
**Score 0.75**: 4 sections complete; one missing or incomplete.
**Score 0.5**: 2-3 sections present; tables poorly formatted.
**Score 0.25**: Only narrative text; no structured tables.
**Score 0.0**: Report missing or empty.

### Criterion 4: Actionability (Weight: 10%)

**Score 1.0**: Each service has a specific capacity recommendation (e.g., "scale to 1.8x current capacity"). Priority list is ordered by urgency with rationale.
**Score 0.75**: Recommendations present but lacking specific multiplier values.
**Score 0.5**: Generic advice (e.g., "consider scaling") without data backing.
**Score 0.0**: No actionable recommendations.

---

## Additional Notes

This task tests:
- ISO 8601 timestamp parsing and hourly bucketing
- Regex extraction of structured values from WARN messages
- Time-series bisection for trend analysis
- Engineering capacity formula application
- Translating data into operational recommendations

Key challenges:
- Log timestamps are in `2024-11-15T00:00:09.472Z` format — need proper ISO parsing
- `depth=94 | max=500` — the `|` character in log messages can confuse simple string splitting
- Half-split requires first determining the full time range of the log file
- Growth safety factor (×1.2) is easily overlooked
- Some services may have zero WARN messages — need to handle gracefully (utilization = 0%)
