---
id: task_log_ssh_failed_logins
name: SSH 認證日誌 — 登入失敗分析
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_ssh_failed_logins
source_benchmark: pinchbench
claw_eval_id: P090zh_log_ssh_failed_logins
workspace_files:
- dest: auth.log
  source: logs/openssh_auth.log
---

# SSH 認證日誌 — 登入失敗分析

## Prompt

請分析位於 `auth.log` 的 OpenSSH 認證日誌，並針對登入失敗嘗試產生一份詳盡報告。此日誌來自一台名為「LabSZ」的伺服器，記錄 SSH 認證事件。

你的報告應包含：

1. **概觀（Overview）**：日誌條目總數、日期範圍、登入失敗嘗試總數
2. **密碼失敗嘗試（Failed Password Attempts）**：「Failed password」條目的計數，並依來源 IP 拆分
3. **無效使用者嘗試（Invalid User Attempts）**：使用不存在使用者名稱的嘗試計數，並列出最常被嘗試的前 10 個使用者名稱
4. **主要攻擊 IP（Top Attacking IPs）**：依失敗嘗試次數列出前 10 個來源 IP 及計數
5. **認證方法（Authentication Methods）**：正在嘗試哪些認證方法（password、publickey 等）？
6. **反向 DNS 失敗（Reverse DNS Failures）**：有多少條目顯示「POSSIBLE BREAK-IN ATTEMPT」警告？
7. **總結評估（Summary Assessment）**：此伺服器是否正遭受主動攻擊？這些樣態說明了什麼？

請把報告寫到 `failed_login_report.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應解析這 1500 筆日誌條目，並產生：

**概觀：**
- 1500 筆日誌條目
- 日期：12 月 10 日（時間範圍約 06:55 至 10:59）
- 約 366 筆「Failed password」條目
- 約 100 筆「Invalid user」條目

**主要攻擊 IP：**
- 183.62.140.253 —— 約 307 筆條目（主要攻擊者）
- 187.141.143.180 —— 約 189 筆條目
- 103.99.0.122 —— 約 83 筆條目
- 112.95.230.3 —— 約 54 筆條目
- 5.188.10.180 —— 約 30 筆條目

**最常見的無效使用者名稱：**
- admin（18）、oracle（6）、support（5）、test（4）、inspur（3）、0（3）、matlab（3）、webmaster（2）、guest（2）、1234（2）

**關鍵觀察：**
- 整份日誌中只有 1 次成功登入（使用者「fztu」，來自 119.137.62.142）
- 因反向 DNS 失敗而觸發的 85 次「POSSIBLE BREAK-IN ATTEMPT」警告
- 此伺服器顯然正遭受主動的暴力破解（brute force）攻擊
- 攻擊來自少數幾個各自產生數百次嘗試的 IP

可接受的變化：
- 視解析方式而定，精確計數可能有 ±5 的差異
- 評估語言會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `failed_login_report.md`
- [ ] 已計數失敗嘗試總數（約 366 筆密碼失敗）
- [ ] 已找出主要攻擊 IP（183.62.140.253 為頭號攻擊者）
- [ ] 已列出無效使用者名稱（admin、oracle、support 為主要目標）
- [ ] 已評估此伺服器正遭受暴力破解攻擊

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the SSH failed login analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "failed_login_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "failed_count": 0.0,
            "top_ips": 0.0,
            "invalid_usernames": 0.0,
            "attack_assessment": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Failed attempt count
    has_failed_count = any(n in content for n in ["366", "365", "367", "failed password"])
    scores["failed_count"] = (
        1.0 if has_failed_count else
        0.5 if "failed" in content and any(c.isdigit() for c in content) else 0.0
    )

    # Check 2: Top attacking IPs identified
    top_ips = ["183.62.140.253", "187.141.143.180", "103.99.0.122", "112.95.230.3"]
    ips_found = sum(1 for ip in top_ips if ip in content)
    scores["top_ips"] = (
        1.0 if ips_found >= 3 else
        0.5 if ips_found >= 1 else 0.0
    )

    # Check 3: Invalid usernames listed
    usernames = ["admin", "oracle", "support", "test", "webmaster", "guest"]
    users_found = sum(1 for u in usernames if u in content)
    scores["invalid_usernames"] = (
        1.0 if users_found >= 3 else
        0.5 if users_found >= 1 else 0.0
    )

    # Check 4: Attack assessment
    attack_keywords = ["brute force", "brute-force", "attack", "compromise",
                       "malicious", "automated", "scanning", "dictionary"]
    scores["attack_assessment"] = (
        1.0 if sum(1 for kw in attack_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in attack_keywords if kw in content) >= 1 else 0.0
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
- 已在工作區建立 `failed_login_report.md`
- 已計數失敗嘗試總數（約 366 筆密碼失敗）
- 已找出主要攻擊 IP（183.62.140.253 為頭號攻擊者）
- 已列出無效使用者名稱（admin、oracle、support 為主要目標）
- 已評估此伺服器正遭受暴力破解攻擊
