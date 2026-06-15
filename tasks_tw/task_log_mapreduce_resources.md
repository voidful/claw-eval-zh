---
id: task_log_mapreduce_resources
name: MapReduce 日誌 — 資源使用率分析
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_mapreduce_resources
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T103tw_log_mapreduce_resources
workspace_files:
- dest: mapreduce.log
  source: logs/hadoop_mapreduce.log
---

# MapReduce 日誌 — 資源使用率分析

## Prompt

請分析位於 `mapreduce.log` 的 Hadoop MapReduce 應用程式日誌，產出一份資源使用率
報告。聚焦於容器（container）配置、排程，以及資源使用型態。

你的報告應包含：

1. **容器清單（Container Inventory）**：列出為此工作配置的所有容器及其 ID
2. **容器配置時間軸（Container Allocation Timeline）**：每個容器在何時被請求與指派？
3. **排程分析（Scheduling Analysis）**：從 RMContainerAllocator 條目追蹤待處理
   （pending）的 map 與 reduce 數量隨時間的變化
4. **Reduce 排程（Reduce Scheduling）**：reduce 的慢啟動（slow start）門檻在何時達到？
   當時的完成百分比為何？
5. **容器重用（Container Reuse）**：是否有容器完成後被重新使用？
6. **資源效率（Resource Efficiency）**：依容器配置與任務完成型態，評估資源效率

請將報告寫入 `mapreduce_resources.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析 RMContainerAllocator 條目並產出：

**容器清單：**
- 使用 13 個不重複容器（container_1445062781478_0011_01_000001 至 000013）
- Application attempt：01

**排程進展：**
- 初始狀態：10 個待處理 map、1 個待處理 reduce
- reduce 慢啟動門檻從 15:38:00 到 15:39:24 反覆「not met」（未達標）
- 首個 map 於 15:39:24 完成（10% complete）— 仍不足以啟動 reduce
- 當 completedMapPercent 達到足夠門檻時，reduce 排程開始
- 15:39:24 記錄了「completedMapPercent 0.1 totalResources 2」

**容器生命週期：**
- 容器約於 15:38:00–15:38:15 配置
- 隨任務完成而釋放容器
- 「Received completed container」條目追蹤容器何時結束

**重點觀察：**
- reduce 任務必須等待足夠多的 map 完成（慢啟動）
- map 任務的完成時間各異（1.5 到 3.5 分鐘）
- 容器周轉：部分容器很快被釋放、其資源迅速被回收

可接受的差異：
- 容器 ID 的列舉方式可能不同
- 時間軸的粒度可能不同
- 資源效率評估帶有主觀性

## Grading Criteria

- [ ] 已在工作區建立 `mapreduce_resources.md`
- [ ] 列出容器（辨識出 13 個容器）
- [ ] 追蹤排程進展（待處理 map/reduce 隨時間的變化）
- [ ] 包含對 reduce 慢啟動門檻的討論
- [ ] 分析容器完成事件

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the MapReduce resource utilization analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "mapreduce_resources.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "containers_listed": 0.0,
            "scheduling_tracked": 0.0,
            "slow_start": 0.0,
            "container_completion": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Containers listed
    has_container = "container_" in content or "container" in content
    has_count = any(n in content for n in ["13 container", "13 unique", "thirteen"])
    scores["containers_listed"] = (
        1.0 if has_container and has_count else
        0.5 if has_container else 0.0
    )

    # Check 2: Scheduling tracked
    sched_keywords = ["pending", "scheduled", "pendingreds", "pendingmaps",
                      "scheduledmaps", "scheduling"]
    scores["scheduling_tracked"] = (
        1.0 if sum(1 for kw in sched_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in sched_keywords if kw in content) >= 1 else 0.0
    )

    # Check 3: Reduce slow start discussed
    slow_start_keywords = ["slow start", "slowstart", "threshold", "reduce.*wait",
                           "completedmappercent", "not met"]
    scores["slow_start"] = (
        1.0 if sum(1 for kw in slow_start_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in slow_start_keywords if kw in content) >= 1 else 0.0
    )

    # Check 4: Container completion analyzed
    completion_keywords = ["completed container", "container released", "received completed",
                           "container finish", "freed"]
    scores["container_completion"] = (
        1.0 if sum(1 for kw in completion_keywords if kw in content) >= 1 else
        0.5 if "complet" in content else 0.0
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
- 已在工作區建立 `mapreduce_resources.md`
- 列出容器（辨識出 13 個容器）
- 追蹤排程進展（待處理 map/reduce 隨時間的變化）
- 包含對 reduce 慢啟動門檻的討論
- 分析容器完成事件
