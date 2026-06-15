---
id: task_log_mapreduce_slow_tasks
name: MapReduce 日誌 — 慢速任務辨識
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_mapreduce_slow_tasks
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T102tw_log_mapreduce_slow_tasks
workspace_files:
- dest: mapreduce.log
  source: logs/hadoop_mapreduce.log
---

# MapReduce 日誌 — 慢速任務辨識

## Prompt

請分析位於 `mapreduce.log` 的 Hadoop MapReduce 應用程式日誌，找出最慢的 map 與
reduce 任務。比較各任務的完成時間以找出落後者（straggler）。

你的報告應包含：

1. **任務完成時間（Task Completion Times）**：對每個已完成的任務，計算從容器（container）
   指派到任務完成的時間
2. **最快與最慢（Fastest vs Slowest）**：辨識最快與最慢的 map 任務，以及 reduce 任務的時序
3. **落後者分析（Straggler Analysis）**：是否有任務明顯比平均耗時更長？量化其偏差
4. **重試影響（Retry Impact）**：對於被重試的任務（attempt > 0），重試時間與原始嘗試相比如何？
5. **Reduce 階段時序（Reduce Phase Timing）**：reduce 任務相對於各 map 完成是在何時開始？耗時多久？
6. **瓶頸辨識（Bottleneck Identification）**：關鍵路徑（critical path）為何？哪些任務決定了整體工作時長？

請將報告寫入 `slow_tasks_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應擷取任務完成時間戳並計算：

**Map 任務完成（依順序）：**
1. m_000009：完成於 15:39:24（最先）
2. m_000005：完成於 15:40:28
3. m_000003：完成於 15:40:32
4. m_000000：完成於 15:40:34
5. m_000001：完成於 15:40:50
6. m_000002：完成於 15:40:50
7. m_000004：完成於 15:40:50
8. m_000008：完成於 15:40:52
9. m_000007：完成於 15:41:12（重試 — _1 次嘗試）
10. m_000006：完成於 15:41:25（重試 — _1 次嘗試，最慢/最後）

**Reduce 任務：**
- r_000000：完成於 15:42:46

**重點發現：**
- m_000009 最先完成於 15:39:24 — 工作開始後約 1.5 分鐘
- m_000006 最後完成於 15:41:25 — 工作開始後約 3.5 分鐘（它是重試）
- 被重試的任務（m_000006、m_000007）最慢，因為必須重新啟動
- 首個與最後 map 之間的時間跨度：約 2 分鐘
- reduce 在足夠多的 map 完成後才開始，約 1.3 分鐘後結束

可接受的差異：
- 確切時長取決於以哪個時間戳作為開始基準
- 對「任務開始」的不同定義皆可接受
- 落後者的判定門檻可能不同

## Grading Criteria

- [ ] 已在工作區建立 `slow_tasks_report.md`
- [ ] 列出個別任務的完成時間
- [ ] 辨識出最快與最慢的 map 任務
- [ ] 將被重試的任務（m_000006、m_000007）標記為較慢
- [ ] 另行分析 reduce 任務的時序

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the MapReduce slow task identification task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "slow_tasks_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "completion_times": 0.0,
            "fastest_slowest": 0.0,
            "retries_flagged": 0.0,
            "reduce_timing": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Task completion times listed
    task_ids = ["m_000009", "m_000005", "m_000003", "m_000000", "m_000006"]
    tasks_found = sum(1 for t in task_ids if t in content)
    scores["completion_times"] = (
        1.0 if tasks_found >= 4 else
        0.5 if tasks_found >= 2 else 0.0
    )

    # Check 2: Fastest and slowest identified
    has_fastest = any(kw in content for kw in ["fastest", "first to complete",
                                                 "earliest", "quickest"])
    has_slowest = any(kw in content for kw in ["slowest", "last to complete",
                                                 "longest", "straggler"])
    scores["fastest_slowest"] = (
        1.0 if has_fastest and has_slowest else
        0.5 if has_fastest or has_slowest else 0.0
    )

    # Check 3: Retried tasks flagged
    has_retry = any(kw in content for kw in ["retry", "retried", "reattempt",
                                               "second attempt", "_1"])
    has_slow_retry = any(kw in content for kw in ["m_000006", "m_000007"])
    scores["retries_flagged"] = (
        1.0 if has_retry and has_slow_retry else
        0.5 if has_retry else 0.0
    )

    # Check 4: Reduce timing analyzed
    has_reduce = "r_000000" in content or "reduce" in content
    has_reduce_time = any(t in content for t in ["15:42", "42:46"])
    scores["reduce_timing"] = (
        1.0 if has_reduce and has_reduce_time else
        0.5 if has_reduce else 0.0
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
- 已在工作區建立 `slow_tasks_report.md`
- 列出個別任務的完成時間
- 辨識出最快與最慢的 map 任務
- 將被重試的任務（m_000006、m_000007）標記為較慢
- 另行分析 reduce 任務的時序
