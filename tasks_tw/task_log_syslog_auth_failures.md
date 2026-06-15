---
id: task_log_syslog_auth_failures
name: Linux Syslog — 驗證失敗摘要
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_syslog_auth_failures
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T108tw_log_syslog_auth_failures
workspace_files:
- dest: syslog.log
  source: logs/linux_syslog.log
---

# Linux Syslog — 驗證失敗摘要

## Prompt

請分析位於 `syslog.log` 的 Linux syslog，產出一份所有驗證失敗的完整摘要。此日誌
含有來自多個服務的 PAM 驗證事件。

你的報告應包含：

1. **驗證失敗總數（Total Auth Failures）**：統計跨所有服務的所有驗證失敗條目
2. **依服務分類的失敗（Failures by Service）**：依服務（sshd、ftpd、login、su 等）拆解失敗
3. **依來源分類的失敗（Failures by Source）**：產生最多失敗的前 10 個來源主機/IP
4. **被鎖定的使用者（Targeted Users）**：哪些使用者帳號在失敗的驗證嘗試中被鎖定？
5. **時間性分布（Temporal Distribution）**：多數驗證失敗發生在何時？是否有突增（spike）？
6. **FTP 與 SSH 分析（FTP vs SSH Analysis）**：比較 FTP 與 SSH 的驗證攻擊型態 — 是否為
   相同來源同時攻擊兩者？
7. **建議（Recommendations）**：依失敗型態，提出具體的安全改進建議

請將報告寫入 `auth_failures_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析約 2000+ 筆與 PAM 相關的條目並產出：

**驗證失敗總數：**
- 超過 2000 筆與驗證相關的 PAM 條目
- 主要來源：sshd(pam_unix)（約 1610 筆）、ftpd 連線（約 1655 筆）

**依服務分類的失敗：**
- sshd(pam_unix) — 驗證失敗訊息的主要來源
- ftpd — 大量連線（ftpd 記錄連線，不一定都是明確的失敗）
- su(pam_unix) — 394 筆（多為合法 — cron 的工作階段開啟/關閉）
- login(pam_unix) — 14 筆
- klogind — 46 筆（Kerberos login daemon）

**依來源分類的失敗：**
- SSH 攻擊來自各種遠端主機（pam 條目中的 rhost=）
- FTP 連線集中於特定 IP（例如 209.184.7.130）
- 部分主機同時出現在 SSH 與 FTP 的失敗日誌中

**被鎖定的使用者：**
- root — SSH 暴力破解的主要目標
- 透過 SSH 嘗試各種無效使用者名稱

**時間性分布：**
- 日誌涵蓋 6 月 9 日到 9 月 14 日
- 特定日期可見攻擊突增
- SSH 暴力破解傾向在時間上集中

可接受的差異：
- 確切計數取決於如何定義「驗證失敗」
- FTP 條目可能被歸類為驗證失敗，也可能不被歸類
- 時間性分析的粒度可能不同

## Grading Criteria

- [ ] 已在工作區建立 `auth_failures_report.md`
- [ ] 統計驗證失敗（2000+ 筆與 pam 相關的條目）
- [ ] 依服務拆解失敗（sshd、ftpd、su 等）
- [ ] 列出主要的來源主機
- [ ] 提供安全改進建議

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Linux syslog authentication failure summary task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "auth_failures_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "failures_counted": 0.0,
            "by_service": 0.0,
            "source_hosts": 0.0,
            "recommendations": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Failures counted
    has_count = any(kw in content for kw in ["2000", "2,000", "1610", "1,610",
                                               "1655", "1,655", "thousand"])
    has_failure = "authentication failure" in content or "auth fail" in content or "failed" in content
    scores["failures_counted"] = (
        1.0 if has_count and has_failure else
        0.5 if has_failure else 0.0
    )

    # Check 2: Broken down by service
    services = ["sshd", "ftpd", "ftp", "su(pam", "su ", "login", "klogin", "pam_unix"]
    services_found = sum(1 for s in services if s in content)
    scores["by_service"] = (
        1.0 if services_found >= 3 else
        0.5 if services_found >= 2 else 0.0
    )

    # Check 3: Source hosts listed
    host_indicators = ["rhost", "source", "remote", "ip", "host", "209.184",
                       "sagonet", "iasi", "astral"]
    scores["source_hosts"] = (
        1.0 if sum(1 for kw in host_indicators if kw in content) >= 3 else
        0.5 if sum(1 for kw in host_indicators if kw in content) >= 1 else 0.0
    )

    # Check 4: Recommendations provided
    rec_keywords = ["recommend", "should", "implement", "consider", "disable",
                    "block", "firewall", "fail2ban", "key-based", "rate limit"]
    rec_lines = [l for l in content.split("\n") if any(kw in l for kw in rec_keywords)]
    scores["recommendations"] = (
        1.0 if len(rec_lines) >= 2 else
        0.5 if len(rec_lines) >= 1 else 0.0
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
- 已在工作區建立 `auth_failures_report.md`
- 統計驗證失敗（2000+ 筆與 pam 相關的條目）
- 依服務拆解失敗（sshd、ftpd、su 等）
- 列出主要的來源主機
- 提供安全改進建議
