---
id: task_log_hdfs_block_ops
name: HDFS DataNode 日誌 — 區塊操作摘要
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_hdfs_block_ops
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T098tw_log_hdfs_block_ops
workspace_files:
- dest: hdfs_datanode.log
  source: logs/hdfs_datanode.log
---

# HDFS DataNode 日誌 — 區塊操作摘要

## Prompt

請分析位於 `hdfs_datanode.log` 的 HDFS DataNode 日誌，產出一份所有區塊操作的完整
摘要。此日誌來自一個 HDFS 叢集，追蹤區塊生命週期事件。

你的報告應包含：

1. **區塊清單（Block Inventory）**：日誌中不重複區塊 ID 的總數，並附完整清單
2. **操作類型（Operation Types）**：針對每種操作類型（allocateBlock、Receiving、
   Received、addStoredBlock、replicate、PacketResponder）計算總出現次數
3. **區塊生命週期追蹤（Block Lifecycle Tracking）**：對於每個具有完整生命週期
   （allocate → receive → stored）的區塊，記錄完整的事件鏈
4. **複製鏈（Replication Chain）**：對於有複製事件的區塊，追蹤其跨節點的複製路徑
5. **相關工作（Associated Jobs）**：辨識觸發這些區塊操作的 MapReduce 工作（可從檔案路徑看出）
6. **逐區塊明細表（Per-Block Detail Table）**：建立一張表格，欄位包含：Block ID、
   Size（如已知）、Allocated Path、Nodes Involved、Replication Count

請將報告寫入 `hdfs_block_ops_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析 2000 筆日誌條目並產出：

**區塊清單：**
- 約 390 個不重複區塊 ID

**操作計數：**
- Receiving block：約 1149
- allocateBlock：約 385
- Received block：約 19
- addStoredBlock：約 19
- PacketResponder：約 12
- Replicate：4

**完整區塊生命週期（資料完整的區塊）：**
- blk_-1608999687919862906：91178 bytes，為 job_200811092030_0001/job.jar 配置
- blk_7503483334202473044：233217 bytes，為 job_200811092030_0001/job.split 配置
- blk_-3544583377289625738：11971 bytes
- blk_-9073992586687739851：11977 bytes

**複製鏈：**
- blk_-1608999687919862906 在叢集中被複製 4 次：
  10.250.14.224 → 10.251.215.16 → 10.251.74.79 → 10.251.31.5 → 10.251.90.64

**相關工作：**
- job_200811092030_0001 — MapReduce 工作，檔案：job.jar、job.split

可接受的差異：
- 區塊 ID 清單可能被截斷
- 不需要對全部 390 個區塊提供完整明細 — 僅需具完整生命週期資料者
- 表格格式可能不同

## Grading Criteria

- [ ] 已在工作區建立 `hdfs_block_ops_report.md`
- [ ] 提供不重複區塊計數（約 390）
- [ ] 計數各操作類型（receiving、allocate、replicate 等）
- [ ] 至少完整追蹤一個區塊的生命週期（allocate → receive → stored）
- [ ] 辨識出相關的 MapReduce 工作（job_200811092030_0001）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the HDFS block operations summary task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "hdfs_block_ops_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "block_count": 0.0,
            "operations_counted": 0.0,
            "lifecycle_traced": 0.0,
            "job_identified": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Block count
    has_count = any(n in content for n in ["390", "~390", "385", "~385", "380", "~400"])
    scores["block_count"] = (
        1.0 if has_count else
        0.5 if any(kw in content for kw in ["hundred", "unique block"]) else 0.0
    )

    # Check 2: Operations counted
    op_keywords = ["receiving", "allocate", "replicate", "addstored",
                   "packetresponder", "received"]
    ops_found = sum(1 for kw in op_keywords if kw in content)
    scores["operations_counted"] = (
        1.0 if ops_found >= 4 else
        0.5 if ops_found >= 2 else 0.0
    )

    # Check 3: Block lifecycle traced
    lifecycle_keywords = ["91178", "233217", "blk_-1608999687919862906",
                          "blk_7503483334202473044", "lifecycle", "job.jar", "job.split"]
    scores["lifecycle_traced"] = (
        1.0 if sum(1 for kw in lifecycle_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in lifecycle_keywords if kw in content) >= 1 else 0.0
    )

    # Check 4: MapReduce job identified
    has_job = "job_200811092030_0001" in content or "200811092030" in content
    has_mapreduce = "mapreduce" in content or "mapred" in content or "map reduce" in content
    scores["job_identified"] = (
        1.0 if has_job else
        0.5 if has_mapreduce else 0.0
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
- 已在工作區建立 `hdfs_block_ops_report.md`
- 提供不重複區塊計數（約 390）
- 計數各操作類型（receiving、allocate、replicate 等）
- 至少完整追蹤一個區塊的生命週期（allocate → receive → stored）
- 辨識出相關的 MapReduce 工作（job_200811092030_0001）
