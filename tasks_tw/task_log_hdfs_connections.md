---
id: task_log_hdfs_connections
name: HDFS DataNode 日誌 — 連線型態分析
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_hdfs_connections
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T096tw_log_hdfs_connections
workspace_files:
- dest: hdfs_datanode.log
  source: logs/hdfs_datanode.log
---

# HDFS DataNode 日誌 — 連線型態分析

## Prompt

請分析位於 `hdfs_datanode.log` 的 HDFS DataNode 日誌，產出一份關於節點之間連線與
通訊型態的報告。此日誌包含 DataNode、FSNamesystem 與 PacketResponder 元件的條目。

你的報告應包含：

1. **網路拓撲（Network Topology）**：列出日誌中出現的所有不重複 IP 位址，並依其角色
   分類（來源、目的地，或兩者皆是）
2. **子網分析（Subnet Analysis）**：依子網（subnet）將 IP 分組（例如 10.250.x.x 與
   10.251.x.x）。每個子網有多少節點？
3. **最活躍的節點（Most Active Nodes）**：依出現頻率（作為來源或目的地）排名前 10 的 IP
4. **通訊型態（Communication Patterns）**：哪些節點對之間通訊最頻繁？
5. **DataNode 與 NameSystem**：將活動拆分 — 哪些來自 DataNode 操作、哪些來自
   FSNamesystem 操作？
6. **叢集規模推估（Cluster Size Estimate）**：依觀察到的 IP，推估叢集規模

請將報告寫入 `hdfs_connections_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析 2000 筆日誌條目並產出：

**網路拓撲：**
- 觀察到 202 個不重複 IP 位址
- IP 落在 10.250.x.x 與 10.251.x.x 範圍（私有網路）
- 所有節點皆使用通訊埠 50010（HDFS DataNode 資料傳輸埠）

**子網分析：**
- 10.250.x.x 子網 — 包含部分最活躍的節點
- 10.251.x.x 子網 — 包含其他 DataNode 叢集成員
- 此分割顯示這是多機架（multi-rack）的 HDFS 佈署

**最活躍的節點：**
- 10.250.19.102 — 極為活躍（在許多區塊傳輸中作為來源出現）
- 10.250.10.6、10.251.215.16、10.250.14.224 — 也相當活躍

**元件活動：**
- DataNode$DataXceiver：區塊接收操作（約 1149 筆）
- FSNamesystem：區塊配置與儲存追蹤（約 400+ 筆）
- DataNode$PacketResponder：附帶大小的區塊接收確認

可接受的差異：
- 確切的 IP 計數與排名可能因解析方式而異
- 子網分組的粒度可能不同
- 叢集規模推估將為概略值

## Grading Criteria

- [ ] 已在工作區建立 `hdfs_connections_report.md`
- [ ] 列出或計數不重複 IP（約 202）
- [ ] 依子網將 IP 分組（10.250.x.x 與 10.251.x.x）
- [ ] 辨識出最活躍的節點
- [ ] 區分 DataNode 與 FSNamesystem 的活動

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the HDFS connection pattern analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "hdfs_connections_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "ips_listed": 0.0,
            "subnets_grouped": 0.0,
            "active_nodes": 0.0,
            "components_separated": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: IPs listed/counted
    has_count = any(n in content for n in ["202", "200", "~200", "over 200"])
    has_ips = "10.250" in content and "10.251" in content
    scores["ips_listed"] = (
        1.0 if has_count and has_ips else
        0.5 if has_ips else 0.0
    )

    # Check 2: Subnets grouped
    subnet_keywords = ["subnet", "10.250", "10.251", "rack", "network segment",
                       "address range", "ip range"]
    scores["subnets_grouped"] = (
        1.0 if "10.250" in content and "10.251" in content and
              sum(1 for kw in subnet_keywords if kw in content) >= 2 else
        0.5 if "10.250" in content and "10.251" in content else 0.0
    )

    # Check 3: Active nodes identified
    active_ips = ["10.250.19.102", "10.251.215.16", "10.250.14.224", "10.250.10.6"]
    ips_found = sum(1 for ip in active_ips if ip in content)
    scores["active_nodes"] = (
        1.0 if ips_found >= 2 else
        0.5 if ips_found >= 1 else 0.0
    )

    # Check 4: Components separated
    component_keywords = ["dataxceiver", "dataxeceiver", "fsnamesystem",
                          "packetresponder", "namenode", "datanode"]
    scores["components_separated"] = (
        1.0 if sum(1 for kw in component_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in component_keywords if kw in content) >= 1 else 0.0
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
- 已在工作區建立 `hdfs_connections_report.md`
- 列出或計數不重複 IP（約 202）
- 依子網將 IP 分組（10.250.x.x 與 10.251.x.x）
- 辨識出最活躍的節點
- 區分 DataNode 與 FSNamesystem 的活動
