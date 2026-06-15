---
id: task_log_mapreduce_timeline
name: MapReduce 日誌 — 工作時間軸視覺化
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_mapreduce_timeline
source_benchmark: pinchbench
claw_eval_id: P104zh_log_mapreduce_timeline
workspace_files:
- dest: mapreduce.log
  source: logs/hadoop_mapreduce.log
---

# MapReduce 日誌 — 工作時間軸視覺化

## Prompt

請分析位於 `mapreduce.log` 的 Hadoop MapReduce 應用程式日誌，為整個工作執行建立
一份詳細的時間軸視覺化。依時間順序呈現所有主要事件。

你的輸出應包含：

1. **事件時間軸（Event Timeline）**：依時間順序列出每個重要事件及其時間戳，包括：
   - 工作初始化事件
   - 容器配置
   - 任務開始與完成
   - 錯誤與警告
   - reduce 階段開始
   - 工作完成
2. **階段圖（Phase Diagram）**：將工作劃分為各階段（初始化、map 階段、shuffle、
   reduce 階段、清理），並附開始/結束時間與時長
3. **甘特式任務檢視（Gantt-Style Task View）**：以文字時間軸呈現每個任務
   （m_000000 至 m_000009、r_000000）及其概略的開始與結束時間
4. **關鍵事件（Critical Events）**：標示出影響最大的事件（錯誤、重試、工作狀態轉換）
5. **併發分析（Concurrency Analysis）**：在每個時間點上，有多少任務平行執行？

請將報告寫入 `mapreduce_timeline.md`，以結構良好的 markdown 文件呈現，並附 ASCII/文字式視覺化。

## Expected Behavior

助手應產出如下的時間軸：

**階段拆解：**
| Phase | Start | End | Duration |
|---|---|---|---|
| Initialization | 15:37:56 | 15:38:00 | ~4s |
| Map Phase | 15:38:00 | 15:41:25 | ~3m 25s |
| Reduce Phase | 15:39:24 | 15:42:46 | ~3m 22s |
| Cleanup | 15:42:46 | 15:42:47 | ~1s |
| **Total** | **15:37:56** | **15:42:47** | **~4m 51s** |

**關鍵事件：**
- 15:37:56 — MRAppMaster 建立
- 15:37:57 — 設定 OutputCommitter（FileOutputCommitter）
- 15:38:00 — 開始容器配置（10 個 map 待處理、1 個 reduce 待處理）
- 15:39:24 — 首個 map 完成（m_000009），Num completed: 1
- 15:40:28–15:40:52 — map 快速完成（任務 2-8）
- 15:40:45 — WARN：區塊 I/O 錯誤（ResponseProcessor、DataStreamer）
- 15:41:12 — m_000007 完成（重試嘗試）
- 15:41:25 — m_000006 完成（重試嘗試，最後一個 map）
- 15:42:46 — r_000000 完成，Num completed: 11
- 15:42:46 — 工作轉換為 SUCCEEDED
- 15:42:47 — 記錄最終統計

**併發：**
- 尖峰：最多達 10 個 map 任務同時執行
- 15:39:24 之後，隨 map 陸續完成，併發度下降

可接受的差異：
- ASCII 視覺化的風格會有所不同
- 並非每筆日誌條目都需放入時間軸 — 主要事件即可
- 階段定義可能略有不同

## Grading Criteria

- [ ] 已在工作區建立 `mapreduce_timeline.md`
- [ ] 依時間順序列出事件並附時間戳
- [ ] 辨識出各階段（init、map、reduce、completion）
- [ ] 嘗試呈現視覺化或結構化的時間軸/甘特圖
- [ ] 標示關鍵事件（首個 map 完成、錯誤、工作成功）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the MapReduce timeline visualization task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "mapreduce_timeline.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "chronological_events": 0.0,
            "phases_identified": 0.0,
            "visual_timeline": 0.0,
            "key_events_highlighted": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Chronological events with timestamps
    timestamps = ["15:37", "15:38", "15:39", "15:40", "15:41", "15:42"]
    ts_found = sum(1 for ts in timestamps if ts in content)
    scores["chronological_events"] = (
        1.0 if ts_found >= 5 else
        0.5 if ts_found >= 3 else 0.0
    )

    # Check 2: Phases identified
    phase_keywords = ["initialization", "init", "map phase", "reduce phase",
                      "shuffle", "cleanup", "completion", "startup"]
    phases_found = sum(1 for kw in phase_keywords if kw in content)
    scores["phases_identified"] = (
        1.0 if phases_found >= 3 else
        0.5 if phases_found >= 2 else 0.0
    )

    # Check 3: Visual/structured timeline attempted
    visual_keywords = ["timeline", "gantt", "---", "===", "|||", "phase",
                       "diagram", "chart", "|", "─", "-"]
    # Check for table-like structures or ASCII art
    lines = content.split("\n")
    table_lines = [l for l in lines if l.count("|") >= 2]
    ascii_lines = [l for l in lines if any(c in l for c in ["─", "━", "═", "▓", "█", "░"])]
    scores["visual_timeline"] = (
        1.0 if len(table_lines) >= 5 or len(ascii_lines) >= 3 else
        0.5 if len(table_lines) >= 2 else 0.0
    )

    # Check 4: Key events highlighted
    key_events = ["mrappmaster", "first map", "succeeded", "warn", "error",
                  "m_000009", "r_000000", "retry", "completed"]
    events_found = sum(1 for kw in key_events if kw in content)
    scores["key_events_highlighted"] = (
        1.0 if events_found >= 4 else
        0.5 if events_found >= 2 else 0.0
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
- 已在工作區建立 `mapreduce_timeline.md`
- 依時間順序列出事件並附時間戳
- 辨識出各階段（init、map、reduce、completion）
- 嘗試呈現視覺化或結構化的時間軸/甘特圖
- 標示關鍵事件（首個 map 完成、錯誤、工作成功）
