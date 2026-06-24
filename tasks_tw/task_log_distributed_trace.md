---
id: task_log_distributed_trace
name: 分散式追蹤鏈路重建與瓶頸識別
category: log_analysis
grading_type: hybrid
timeout_seconds: 600
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

我有一份微服務應用日誌 `microservice_app.log`（~1.2MB，8,000+ 行），格式為：

```
[timestamp] [LEVEL] [service] [request_id] message
```

同一個 `request_id` 可能出現在多個不同的服務日誌中，代表這是一筆跨服務的分散式請求。

請重建分散式調用鏈路，識別瓶頸服務，並輸出報告 `distributed_trace_report.md`。

### 第一步：識別跨服務請求

- 找出所有出現在 **2 個或以上不同服務** 的 request_id（即跨服務請求）
- 統計：跨服務請求總數、跨服務 request_id 佔全部唯一 request_id 的比例

### 第二步：重建每條調用鏈路

對每個跨服務 request_id：
1. 收集所有含該 request_id 的日誌行
2. 按時間戳記升序排序
3. 記錄調用順序（Service A → Service B → Service C ...）
4. 計算「端對端延遲」= 最後一條日誌的時間 - 第一條日誌的時間（毫秒）

### 第三步：延遲統計

- 計算所有跨服務請求的端對端延遲的 **P50、P95、P99**（用線性插值法）
- 找出端對端延遲最長的 **Top 10 請求**（列出 request_id、調用鏈、延遲毫秒數）

### 第四步：服務瓶頸分析

對每個服務，計算：
- **調用次數**：在跨服務請求的調用鏈中出現的次數
- **高延遲關聯次數**：在「端對端延遲 > 5000ms」的鏈路中出現的次數
- **瓶頸貢獻率**：高延遲關聯次數 / 調用次數 × 100%

按瓶頸貢獻率降序排列，識別最可能是瓶頸的服務。

### 第五步：根因服務分析

在含有 ERROR 日誌的跨服務調用鏈中：
- 找出「鏈路中第一個出現 ERROR 的服務」（按時間排序，取最早的 ERROR）
- 統計每個服務「作為鏈路中最先出錯服務」的次數
- 次數最多的服務為「根因服務（Root Cause Service）」

### 輸出報告 `distributed_trace_report.md` 需包含：

1. 跨服務請求統計（跨服務 request_id 數量、佔比）
2. 端對端延遲分布（P50、P95、P99 毫秒數）
3. Top 10 最慢鏈路表（request_id、調用鏈、端對端延遲ms）
4. 各服務瓶頸貢獻率排行表
5. 根因服務分析結果（哪個服務最常是第一個出錯的）
6. 優化建議（針對瓶頸服務和根因服務各提出具體建議）

---

## Expected Behavior

代理人應執行以下步驟：

1. 解析所有 8,000+ 行，提取 timestamp、service、request_id、level、message
2. 用 dict/groupby 把相同 request_id 的日誌行聚合在一起
3. 過濾出跨服務的 request_id（出現服務數 ≥ 2）
4. 對每個 request_id 按時間排序，計算首尾時間差（端對端延遲）
5. 對端對端延遲列表排序，計算 P50/P95/P99（線性插值）
6. 對每條鏈路統計服務出現次數，識別高延遲關聯
7. 在含 ERROR 的鏈路中，找每條鏈路時間最早的 ERROR 行，統計各服務作為根因的次數

Key expected values：
- 跨服務 request_id 數：可能佔全體的 20~50%
- P95 端對端延遲應 > 5000ms（因為有 timeout 錯誤 ~30000ms）
- 根因服務應是依賴最多/錯誤率最高的服務之一
- Top 10 最慢鏈路的延遲可能高達 20,000~30,000ms

---

## Grading Criteria

- [ ] 輸出檔案 `distributed_trace_report.md` 存在
- [ ] 報告有跨服務 request_id 的數量統計
- [ ] P50、P95、P99 端對端延遲均有數值（ms 格式）
- [ ] P50 < P95 < P99（數值順序合理）
- [ ] Top 10 最慢鏈路表有 request_id 和毫秒數值
- [ ] 各服務瓶頸貢獻率排行表存在（至少 5 個服務）
- [ ] 根因服務分析有明確指出最常出錯的服務名稱
- [ ] 根因分析基於「鏈路中第一個 ERROR」邏輯（非僅統計最多 ERROR 的服務）
- [ ] 有針對瓶頸服務的具體優化建議
- [ ] 報告含 Markdown 表格（至少 2 個）

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "distributed_trace_report.md"
    if not report_path.exists():
        for alt in ["trace_report.md", "distributed_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "cross_service_stats": 0.0,
            "latency_percentiles": 0.0,
            "percentile_order_correct": 0.0,
            "top10_slowest": 0.0,
            "bottleneck_table": 0.0,
            "root_cause_analysis": 0.0,
            "first_error_logic": 0.0,
            "optimization_suggestions": 0.0,
            "has_tables": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Cross-service stats (numbers + request_id or cross-service keywords)
    has_cross_stats = bool(
        re.search(r'cross.?service|跨服務|多服務', content_lower) and
        re.search(r'\b\d{2,4}\b', content)
    )
    scores["cross_service_stats"] = 1.0 if has_cross_stats else 0.5

    # Latency percentiles (P50, P95, P99 with ms values)
    p_vals = {}
    for pct in ["p50", "p95", "p99"]:
        match = re.search(rf'{pct}[^\d]*(\d+)', content_lower)
        if match:
            p_vals[pct] = int(match.group(1))
    scores["latency_percentiles"] = 1.0 if len(p_vals) == 3 else (0.5 if len(p_vals) >= 1 else 0.0)

    # Percentile order correct: P50 < P95 < P99
    if len(p_vals) == 3:
        ordered = p_vals["p50"] < p_vals["p95"] < p_vals["p99"]
        scores["percentile_order_correct"] = 1.0 if ordered else 0.0
    else:
        scores["percentile_order_correct"] = 0.0

    # Top 10 slowest (request_id pattern + ms numbers)
    req_ids = re.findall(r'req_\d+', content)
    large_ms = re.findall(r'\b(\d{4,6})\s*ms\b', content)
    scores["top10_slowest"] = 1.0 if (len(req_ids) >= 5 and len(large_ms) >= 5) else (
        0.5 if (len(req_ids) >= 2 or len(large_ms) >= 2) else 0.0)

    # Bottleneck table (service names + percentage values)
    services = ["api-gateway", "auth-service", "order-service", "payment-service",
                "inventory-service", "notification-service", "user-service", "cache-layer"]
    found_svc = sum(1 for s in services if s in content_lower or s.replace("-", "_") in content_lower)
    pct_vals = re.findall(r'\d+\.?\d*\s*%', content)
    scores["bottleneck_table"] = 1.0 if (found_svc >= 5 and len(pct_vals) >= 5) else (
        0.5 if found_svc >= 3 else 0.0)

    # Root cause analysis
    has_root_cause = bool(re.search(r'root.?cause|根因|根本原因', content_lower))
    scores["root_cause_analysis"] = 1.0 if has_root_cause else 0.0

    # First-error logic (not just most errors)
    first_error_logic = bool(
        re.search(r'first.*error|最先.*error|第一.*錯|最早.*錯|鏈路中.*error', content_lower)
    )
    scores["first_error_logic"] = 1.0 if first_error_logic else 0.5

    # Optimization suggestions
    opt_kws = ["優化", "建議", "擴容", "增加", "降低", "optimize", "recommend", "scale", "reduce", "increase"]
    found_opt = sum(1 for kw in opt_kws if kw.lower() in content_lower)
    scores["optimization_suggestions"] = 1.0 if found_opt >= 3 else (0.5 if found_opt >= 1 else 0.0)

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

### Criterion 1: Trace Reconstruction Accuracy (Weight: 35%)

**Score 1.0**: Correctly identifies cross-service request_ids (appearing in 2+ services). End-to-end latency correctly computed as last_timestamp - first_timestamp per request_id. P50/P95/P99 in correct ascending order with plausible values (P99 likely >10,000ms given timeout errors in log).
**Score 0.75**: Trace reconstruction mostly correct; one metric has minor calculation error.
**Score 0.5**: Cross-service requests identified but latency computation is approximate or percentile formula wrong.
**Score 0.25**: request_id grouping attempted but no actual end-to-end latency computed.
**Score 0.0**: No distributed trace analysis performed.

### Criterion 2: Bottleneck Identification Logic (Weight: 30%)

**Score 1.0**: Bottleneck contribution rate = high-latency appearances / total appearances, correctly computed per service. Services ranked correctly. Bottleneck differs from the service with the most errors (demonstrates understanding of the distinction).
**Score 0.75**: Bottleneck logic mostly correct; ranking has minor discrepancies.
**Score 0.5**: Bottleneck analysis present but based on error count rather than latency contribution rate.
**Score 0.25**: Qualitative identification of bottleneck without quantitative contribution rate.
**Score 0.0**: No bottleneck analysis.

### Criterion 3: Root Cause Precision (Weight: 20%)

**Score 1.0**: Root cause correctly identified as the service that is FIRST to error within a trace chain (not the service with the most total errors). Evidence provided (e.g., specific trace showing Service X errored at T1 before Service Y at T2).
**Score 0.75**: Root cause analysis correct methodology but missing chain evidence.
**Score 0.5**: Root cause identified based on total error count (common but incorrect shortcut).
**Score 0.25**: Root cause mentioned without clear methodology.
**Score 0.0**: No root cause analysis.

### Criterion 4: Optimization Recommendations (Weight: 15%)

**Score 1.0**: Specific recommendations for bottleneck service (e.g., "payment-service P95 > 8000ms, increase connection pool") and root cause service (e.g., "add circuit breaker to auth-service"). Each recommendation includes a specific threshold or action.
**Score 0.75**: Recommendations present but missing specificity for one service type.
**Score 0.5**: Generic recommendations applicable to any microservice system.
**Score 0.25**: Vague suggestions without tying to findings.
**Score 0.0**: No recommendations.

---

## Additional Notes

This task tests:
- Large-scale log parsing (8,000+ lines) with groupby on request_id
- Cross-service join logic using shared request_id as key
- Timestamp arithmetic for latency computation
- Percentile calculation (linear interpolation)
- Graph-like chain traversal (ordering events in a request's lifetime)
- Distinguishing "most errors" from "first error in chain" (root cause precision)

Key challenges for weaker models:
- Confusing "service with most errors" with "root cause service" — the root cause is the FIRST in the chain to error
- ISO 8601 timestamp subtraction requires careful parsing
- Some request_ids appear only in one service (not cross-service) — must filter correctly
- P50/P95/P99 via linear interpolation: many models use approximate methods (like just picking the 50th/95th/99th element) — acceptable but note the difference
- Top 10 slowest requires sorting by end-to-end latency, not individual log entry latency

This is a **hard** task because it requires: (1) groupby + join across 8,000 rows, (2) timestamp arithmetic, (3) percentile math, AND (4) conceptually distinguishing bottleneck vs root cause.
