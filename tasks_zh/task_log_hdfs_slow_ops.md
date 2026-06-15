---
id: task_log_hdfs_slow_ops
name: HDFS DataNode 日誌 — 慢速操作偵測
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_hdfs_slow_ops
source_benchmark: pinchbench
claw_eval_id: P097zh_log_hdfs_slow_ops
workspace_files:
- dest: hdfs_datanode.log
  source: logs/hdfs_datanode.log
---

# HDFS DataNode 日誌 — 慢速操作偵測

## Prompt

請分析位於 `hdfs_datanode.log` 的 HDFS DataNode 日誌，找出耗時超出預期的操作。此
日誌記錄了帶有時間戳的區塊接收、配置與複製。

你的報告應包含：

1. **區塊生命週期時序（Block Lifecycle Timing）**：對於同時有「Receiving block」與
   「Received block」條目的區塊，計算經過時間
2. **配置到接收時序（Allocation-to-Receive Timing）**：對於同時有「allocateBlock」與
   第一筆「Receiving block」條目的區塊，計算延遲
3. **複製時序（Replication Timing）**：複製請求在區塊配置後多快發出？
4. **最慢的操作（Slowest Operations）**：依經過時間排名前 5 慢的區塊操作
5. **區塊大小與時間的相關性（Block Size vs Time Correlation）**：較大的區塊是否耗時較長？
   在兩者皆可取得時，將區塊大小與傳輸時間相關聯
6. **效能總結（Performance Summary）**：對此期間叢集效能的整體評估

請將報告寫入 `hdfs_slow_ops_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應從 `YYMMDD HHMMSS` 日誌格式解析時間戳並計算：

**區塊生命週期：**
- 此日誌僅涵蓋約 28 秒（203518 到 203546）
- 多數區塊操作在 1-3 秒內完成
- 已確認且附大小的區塊接收：91178 bytes、233217 bytes、11971 bytes、11977 bytes

**重點觀察：**
- blk_-1608999687919862906（91178 bytes）：於 203518 配置、203518 首次接收、203519 確認（約 1 秒）
- blk_7503483334202473044（233217 bytes）：於 203520 配置、203521 確認（約 1 秒）
- blk_-3544583377289625738（11971 bytes）：於 203522-203523 確認
- 區塊操作非常快速 — 與健康叢集在正常負載下的表現相符

**複製：**
- blk_-1608999687919862906 有 4 筆複製請求，分別於 203521、203524、203527、203530 發出
- 各複製躍程（hop）之間約間隔 3 秒

**效能：**
- 所有操作皆在 1-3 秒內完成 — 未偵測到慢速操作
- 此快照期間叢集表現良好

可接受的差異：
- 時間戳解析度為 1 秒，故部分時序分析將為概略值
- 配對開始/結束事件的不同做法皆屬有效
- 區塊大小相關性分析可能因資料不足而無法得出有意義結論

## Grading Criteria

- [ ] 已在工作區建立 `hdfs_slow_ops_report.md`
- [ ] 至少為一個區塊計算其生命週期時序
- [ ] 在有資料時將區塊大小與操作時間相關聯
- [ ] 正確辨識日誌的時間範圍（約 28 秒）
- [ ] 提供效能評估

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the HDFS slow operation detection task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "hdfs_slow_ops_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "lifecycle_timing": 0.0,
            "size_correlation": 0.0,
            "time_range": 0.0,
            "performance_assessment": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Block lifecycle timing calculated
    has_timing = any(kw in content for kw in ["1 second", "2 second", "3 second",
                                                "elapsed", "duration", "latency",
                                                "took", "completed in"])
    has_block = "blk_" in content or "blk-" in content or "block" in content
    scores["lifecycle_timing"] = (
        1.0 if has_timing and has_block else
        0.5 if has_timing or has_block else 0.0
    )

    # Check 2: Block sizes mentioned
    sizes = ["91178", "233217", "11971", "11977"]
    sizes_found = sum(1 for s in sizes if s in content)
    has_correlation = any(kw in content for kw in ["size", "bytes", "larger", "smaller"])
    scores["size_correlation"] = (
        1.0 if sizes_found >= 2 and has_correlation else
        0.5 if sizes_found >= 1 else 0.0
    )

    # Check 3: Time range identified
    has_28s = any(kw in content for kw in ["28 second", "~28", "30 second",
                                            "half a minute", "less than a minute"])
    has_timestamps = "203518" in content or "20:35:18" in content or "20:35" in content
    scores["time_range"] = (
        1.0 if has_28s or has_timestamps else
        0.5 if any(kw in content for kw in ["short", "brief", "seconds"]) else 0.0
    )

    # Check 4: Performance assessment
    perf_keywords = ["healthy", "normal", "fast", "no slow", "performing well",
                     "efficient", "optimal", "good performance"]
    scores["performance_assessment"] = (
        1.0 if sum(1 for kw in perf_keywords if kw in content) >= 1 else 0.0
    )

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

## LLM Judge Rubric

依下列評分標準逐項評估（每項 0.0–1.0，最後取平均）：
- 已在工作區建立 `hdfs_slow_ops_report.md`
- 至少為一個區塊計算其生命週期時序
- 在有資料時將區塊大小與操作時間相關聯
- 正確辨識日誌的時間範圍（約 28 秒）
- 提供效能評估
