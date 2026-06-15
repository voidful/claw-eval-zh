---
id: task_log_mapreduce_jobs
name: MapReduce 日誌 — 工作完成摘要
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_mapreduce_jobs
source_benchmark: pinchbench
claw_eval_id: P100zh_log_mapreduce_jobs
workspace_files:
- dest: mapreduce.log
  source: logs/hadoop_mapreduce.log
---

# MapReduce 日誌 — 工作完成摘要

## Prompt

請分析位於 `mapreduce.log` 的 Hadoop MapReduce 應用程式日誌，產出一份完整的工作
完成摘要。此日誌來自一個 MapReduce v2（YARN）應用程式。

你的報告應包含：

1. **工作識別（Job Identification）**：Job ID、application attempt ID，以及工作名稱/類型
2. **工作組態（Job Configuration）**：OutputCommitter 類型、檔案系統，以及任何其他組態細節
3. **任務摘要（Task Summary）**：map 任務總數、reduce 任務總數，各有多少成功完成
4. **任務完成時間軸（Task Completion Timeline）**：每個任務在何時完成？建立一條按完成順序
   並附時間戳的時間軸
5. **工作時長（Job Duration）**：從開始到結束的工作總執行時間
6. **最終狀態（Final Status）**：工作成功還是失敗？最終的狀態轉換為何？

請將報告寫入 `job_completion_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析 1282 筆日誌條目並產出：

**工作識別：**
- Job ID：job_1445062781478_0011
- Application Attempt：appattempt_1445062781478_0011_000001
- 工作類型：pagerank（可從 history 檔案路徑看出）
- 使用者：msrabi

**組態：**
- OutputCommitter：FileOutputCommitter
- 檔案系統：hdfs://msra-sa-41:9000
- API：mapred newApiCommitter

**任務摘要：**
- 10 個 map 任務（m_000000 至 m_000009），外加 2 次重試（m_000006_1、m_000007_1）
- 1 個 reduce 任務（r_000000）
- 全部 11 個任務皆成功完成（10 map + 1 reduce）
- 共 12 次 map 任務嘗試、1 次 reduce 任務嘗試

**時間軸：**
- 工作開始：15:37:56
- 首個 map 完成：15:39:24（m_000009）
- 最後 map 完成：15:41:25（m_000006）
- reduce 完成：15:42:46（r_000000）
- 工作結束：約 15:42:47

**時長：** 約 5 分鐘（15:37:56 到 15:42:47）

**最終狀態：** SUCCEEDED

可接受的差異：
- 時間軸的格式可能不同
- 時長計算方式可能不同
- 任務編號標記法可能不同

## Grading Criteria

- [ ] 已在工作區建立 `job_completion_report.md`
- [ ] 辨識出 Job ID（job_1445062781478_0011）
- [ ] map 與 reduce 任務計數正確（10 個 map 任務、1 個 reduce 任務）
- [ ] 計算工作時長（約 5 分鐘）
- [ ] 辨識最終狀態為 SUCCEEDED

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the MapReduce job completion summary task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "job_completion_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "job_id": 0.0,
            "task_counts": 0.0,
            "duration": 0.0,
            "final_status": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Job ID identified
    scores["job_id"] = (
        1.0 if "job_1445062781478_0011" in content or "1445062781478_0011" in content else 0.0
    )

    # Check 2: Task counts correct
    has_10_map = any(kw in content for kw in ["10 map", "ten map", "10 mapper"])
    has_1_reduce = any(kw in content for kw in ["1 reduce", "one reduce", "single reduce",
                                                  "1 reducer"])
    scores["task_counts"] = (
        1.0 if has_10_map and has_1_reduce else
        0.5 if has_10_map or has_1_reduce else 0.0
    )

    # Check 3: Duration calculated
    duration_keywords = ["5 minute", "~5 min", "4 minute", "4:51", "4:50",
                         "approximately 5", "about 5", "15:37", "15:42",
                         "nearly 5"]
    scores["duration"] = (
        1.0 if sum(1 for kw in duration_keywords if kw in content) >= 1 else 0.0
    )

    # Check 4: Final status
    scores["final_status"] = (
        1.0 if "succeeded" in content else
        0.5 if "success" in content or "completed" in content else 0.0
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
- 已在工作區建立 `job_completion_report.md`
- 辨識出 Job ID（job_1445062781478_0011）
- map 與 reduce 任務計數正確（10 個 map 任務、1 個 reduce 任務）
- 計算工作時長（約 5 分鐘）
- 辨識最終狀態為 SUCCEEDED
