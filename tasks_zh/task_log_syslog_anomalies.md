---
id: task_log_syslog_anomalies
name: Linux Syslog — 異常偵測
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_syslog_anomalies
source_benchmark: pinchbench
claw_eval_id: P105zh_log_syslog_anomalies
workspace_files:
- dest: syslog.log
  source: logs/linux_syslog.log
---

# Linux Syslog — 異常偵測

## Prompt

請分析位於 `syslog.log` 的 Linux syslog，找出異常或可疑的條目。此日誌來自一台名為
「combo」、執行 Linux 2.6 核心的伺服器，涵蓋數個月的活動。

你的報告應包含：

1. **日誌總覽（Log Overview）**：總條目數、日期範圍、依量排序的主要服務
2. **安全異常（Security Anomalies）**：顯示潛在攻擊、漏洞利用（exploit）或未授權存取
   嘗試的條目
3. **格式字串攻擊偵測（Format String Attack Detection）**：尋找服務輸入中帶有異常二進位
   內容或漏洞利用酬載（payload）的條目
4. **FTP 異常（FTP Anomalies）**：此日誌有大量 FTP 流量 — 找出任何可疑的 FTP 連線型態
   （爆量、異常來源）
5. **rpc.statd 漏洞利用（rpc.statd Exploitation）**：檢查 rpc.statd 帶有畸形主機名的
   gethostbyname 錯誤（緩衝區溢位嘗試）
6. **異常總結（Anomaly Summary）**：依嚴重性與證據，排名最值得關注的前 5 個異常

請將報告寫入 `syslog_anomalies.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析 5000 筆條目並辨識出：

**日誌總覽：**
- 5000 筆條目，6 月 9 日到 9 月 14 日（依核心版本推斷為 2005 年）
- 主要服務：ftpd（1655）、sshd/pam_unix（1610）、kernel（545）、su/pam_unix（394）

**安全異常：**
1. **rpc.statd 格式字串攻擊**（6 月 13 日約 9 筆）：
   - `gethostbyname error for ^X...%8x%8x...%hn%51859x%hn` — 這是針對 rpc.statd 的
     緩衝區溢位/格式字串漏洞利用嘗試
   - 此酬載含格式字串指定符（%x、%hn），是典型的漏洞利用模式
2. **SSH 暴力破解** — 大量 sshd(pam_unix) 驗證失敗
3. **FTP 洪泛** — 1655 筆 FTP 連線條目，並出現爆量（例如 209.184.7.130 有多筆同時連線）
4. **驗證失敗** — 跨 SSH 與其他服務共 2000+ 筆 pam_unix 驗證失敗條目

**rpc.statd 漏洞利用：**
- 6 月 13 日 11:55:04–11:55:09 共 9 筆
- 畸形主機名含 NOP sled（\220\220\220\220）與格式字串酬載
- 這是一次嘗試遠端程式碼執行（remote code execution）的漏洞利用

可接受的差異：
- 異常的排名可能不同
- 歡迎找出預期之外的額外異常
- 嚴重性評估會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `syslog_anomalies.md`
- [ ] 提供含日期範圍與服務分布的日誌總覽
- [ ] 辨識出 rpc.statd 格式字串攻擊為安全異常
- [ ] 分析 FTP 連線型態
- [ ] 標示出 SSH 驗證失敗

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Linux syslog anomaly detection task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "syslog_anomalies.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "log_overview": 0.0,
            "rpc_statd_attack": 0.0,
            "ftp_analysis": 0.0,
            "ssh_failures": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Log overview
    has_count = any(n in content for n in ["5000", "5,000"])
    has_date = any(d in content for d in ["jun", "june", "sep", "september"])
    scores["log_overview"] = (
        1.0 if has_count and has_date else
        0.5 if has_count or has_date else 0.0
    )

    # Check 2: rpc.statd attack identified
    rpc_keywords = ["rpc.statd", "rpc statd", "gethostbyname", "format string",
                    "buffer overflow", "exploit", "%hn", "nop sled", "\\220"]
    scores["rpc_statd_attack"] = (
        1.0 if sum(1 for kw in rpc_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in rpc_keywords if kw in content) >= 1 else 0.0
    )

    # Check 3: FTP analysis
    ftp_keywords = ["ftpd", "ftp", "1655", "209.184", "connection flood",
                    "burst", "ftp connection"]
    scores["ftp_analysis"] = (
        1.0 if sum(1 for kw in ftp_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in ftp_keywords if kw in content) >= 1 else 0.0
    )

    # Check 4: SSH failures flagged
    ssh_keywords = ["sshd", "ssh", "authentication failure", "brute force",
                    "failed", "pam_unix"]
    scores["ssh_failures"] = (
        1.0 if sum(1 for kw in ssh_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in ssh_keywords if kw in content) >= 1 else 0.0
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
- 已在工作區建立 `syslog_anomalies.md`
- 提供含日期範圍與服務分布的日誌總覽
- 辨識出 rpc.statd 格式字串攻擊為安全異常
- 分析 FTP 連線型態
- 標示出 SSH 驗證失敗
