---
id: task_log_hdfs_storage
name: HDFS DataNode 日誌 — 儲存與容量分析
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_hdfs_storage
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T099tw_log_hdfs_storage
workspace_files:
- dest: hdfs_datanode.log
  source: logs/hdfs_datanode.log
---

# HDFS DataNode 日誌 — 儲存與容量分析

## Prompt

請分析位於 `hdfs_datanode.log` 的 HDFS DataNode 日誌，產出一份以儲存（storage）為
重點的分析。檢視區塊大小、跨節點的資料分布，以及儲存型態。

你的報告應包含：

1. **資料量（Data Volume）**：所有已確認區塊接收（大小已知者）所儲存的總位元組數
2. **區塊大小分布（Block Size Distribution）**：列出所有已知區塊大小，計算最小/最大/平均/中位數
3. **依節點的資料分布（Data Distribution by Node）**：對每個確認接收區塊的節點
   （PacketResponder「Received」條目），統計其儲存的位元組總數
4. **儲存路徑分析（Storage Path Analysis）**：使用了哪些儲存路徑？（從 allocateBlock 的檔案路徑擷取）
5. **複製係數（Replication Factor）**：依同一區塊被多少節點接收，推算有效複製係數為何？
6. **容量規劃（Capacity Planning）**：依觀察到的資料寫入速率，推估 1 小時類似活動所需的儲存空間

請將報告寫入 `hdfs_storage_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析日誌並計算：

**已確認的區塊大小：**
- blk_-1608999687919862906：91,178 bytes（被 3+ 個節點接收）
- blk_7503483334202473044：233,217 bytes（被 3 個節點接收）
- blk_-3544583377289625738：11,971 bytes（被 3 個節點接收）
- blk_-9073992586687739851：11,977 bytes（被 3 個節點接收）

**區塊大小統計：**
- 最小：11,971 bytes（約 12 KB）
- 最大：233,217 bytes（約 228 KB）
- 平均：約 87,086 bytes（約 85 KB）
- 已確認資料總量：每個副本約 348,343 bytes

**複製係數：**
- 每個已確認區塊皆被 3 個節點接收 → 複製係數為 3
- 這是標準的 HDFS 預設複製設定

**儲存路徑：**
- `/mnt/hadoop/mapred/system/job_200811092030_0001/` — MapReduce 工作的暫存目錄
- 檔案：job.jar、job.split

**容量規劃：**
- 約 28 秒的活動產生了約 390 筆區塊配置
- 若每個區塊平均約 85 KB、複製係數為 3，則約為每分鐘 100 MB 的原始儲存
- 1 小時推估：約 6 GB（概略）

可接受的差異：
- 在已確認大小有限的情況下，容量推估將相當粗略
- 外推（extrapolation）的做法會有所不同
- 統計應僅以已確認大小為基礎

## Grading Criteria

- [ ] 已在工作區建立 `hdfs_storage_report.md`
- [ ] 列出已知的區塊大小（91178、233217、11971、11977）
- [ ] 計算區塊大小統計（最小、最大、平均）
- [ ] 辨識出複製係數（3）
- [ ] 從日誌擷取儲存路徑

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the HDFS storage and capacity analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "hdfs_storage_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "block_sizes_listed": 0.0,
            "statistics_calculated": 0.0,
            "replication_factor": 0.0,
            "storage_paths": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Block sizes listed
    sizes = ["91178", "233217", "11971", "11977"]
    sizes_found = sum(1 for s in sizes if s in content)
    scores["block_sizes_listed"] = (
        1.0 if sizes_found >= 3 else
        0.5 if sizes_found >= 1 else 0.0
    )

    # Check 2: Statistics calculated
    stat_keywords = ["min", "max", "mean", "median", "average", "total",
                     "distribution", "range"]
    scores["statistics_calculated"] = (
        1.0 if sum(1 for kw in stat_keywords if kw in content) >= 3 else
        0.5 if sum(1 for kw in stat_keywords if kw in content) >= 1 else 0.0
    )

    # Check 3: Replication factor identified
    has_replication = any(kw in content for kw in ["replication factor",
                                                     "replication of 3",
                                                     "factor of 3",
                                                     "3 replicas",
                                                     "three replicas",
                                                     "3 copies",
                                                     "three copies",
                                                     "replicated 3",
                                                     "3 nodes"])
    scores["replication_factor"] = 1.0 if has_replication else 0.0

    # Check 4: Storage paths extracted
    has_path = any(p in content for p in ["/mnt/hadoop", "job_200811092030",
                                           "mapred/system", "job.jar", "job.split"])
    scores["storage_paths"] = 1.0 if has_path else 0.0

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
- 已在工作區建立 `hdfs_storage_report.md`
- 列出已知的區塊大小（91178、233217、11971、11977）
- 計算區塊大小統計（最小、最大、平均）
- 辨識出複製係數（3）
- 從日誌擷取儲存路徑
