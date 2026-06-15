---
id: task_log_ssh_user_activity
name: SSH 認證日誌 — 使用者登入活動報告
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_ssh_user_activity
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T093tw_log_ssh_user_activity
workspace_files:
- dest: auth.log
  source: logs/openssh_auth.log
---

# SSH 認證日誌 — 使用者登入活動報告

## Prompt

請分析位於 `auth.log` 的 OpenSSH 認證日誌，並產生一份以使用者為核心的活動報告。對於日誌中提到的每個使用者名稱（無論有效或無效），請摘要其認證活動。

你的報告應包含：

1. **所有被嘗試的使用者名稱（All Usernames Attempted）**：列出日誌中出現的每個使用者名稱（包含有效的系統使用者與無效／不存在的使用者）
2. **有效 vs 無效使用者（Valid vs Invalid Users）**：將每個使用者名稱分類為有效（被系統接受）或無效（因不存在而被拒絕）
3. **各使用者摘要（Per-User Summary）**：對每個使用者名稱，列出：嘗試次數、來源 IP、成功／失敗、第一次與最後一次嘗試的時間戳記
4. **最常被鎖定的使用者（Most Targeted Users）**：依失敗嘗試次數排序使用者名稱
5. **使用者名稱樣態（Username Patterns）**：攻擊者是否在使用字典？有哪些常見樣態（admin、root、test、服務帳號）？
6. **使用者風險評估（User Risk Assessment）**：哪些使用者名稱若真實存在，會帶來最大的資安風險？

請把報告寫到 `user_activity_report.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應找出：

**無效使用者（依頻率前列）：**
- admin（18 次嘗試）、oracle（6）、support（5）、test（4）、inspur（3）、0（3）、matlab（3）、webmaster（2）、guest（2）、1234（2）等

**有效使用者：**
- fztu —— 唯一一個成功登入的使用者
- root —— 很可能是一個被鎖定的有效使用者（請檢查是「Failed password for root」還是「Failed password for invalid user root」）

**使用者名稱樣態：**
- 常見服務帳號：admin、oracle、support、webmaster
- 預設憑證：test、guest、1234、0
- 應用程式專屬：matlab、inspur
- 這顯然是使用常見使用者名稱清單的字典攻擊

**風險評估：**
- 「admin」與「root」風險最高——一旦遭洩漏即可取得完整系統存取權
- 「oracle」顯示攻擊者知道這很可能是一台執行資料庫的 Linux 伺服器
- 像「0」與「1234」這類數字使用者名稱顯示為自動化／腳本化攻擊

可接受的變化：
- 有效與無效使用者的區分取決於對「invalid user」訊息的解析
- 部分使用者名稱可能模稜兩可
- 風險評估語言會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `user_activity_report.md`
- [ ] 已同時列出有效與無效的使用者名稱
- [ ] 已找出最常被鎖定的使用者名稱（admin）
- [ ] 已分析使用者名稱樣態（字典攻擊、常見預設值）
- [ ] 已對最危險的使用者名稱提供風險評估

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the SSH user activity report task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "user_activity_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "usernames_listed": 0.0,
            "admin_targeted": 0.0,
            "patterns_analyzed": 0.0,
            "risk_assessment": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Both valid and invalid usernames listed
    invalid_users = ["admin", "oracle", "support", "test", "webmaster", "guest"]
    valid_users = ["fztu"]
    invalid_found = sum(1 for u in invalid_users if u in content)
    valid_found = sum(1 for u in valid_users if u in content)
    scores["usernames_listed"] = (
        1.0 if invalid_found >= 3 and valid_found >= 1 else
        0.5 if invalid_found >= 2 else 0.0
    )

    # Check 2: Admin identified as most targeted
    scores["admin_targeted"] = (
        1.0 if "admin" in content and any(kw in content for kw in
            ["most", "top", "highest", "18", "target"]) else
        0.5 if "admin" in content else 0.0
    )

    # Check 3: Username patterns analyzed
    pattern_keywords = ["dictionary", "common", "default", "service account",
                        "automated", "wordlist", "brute", "pattern"]
    scores["patterns_analyzed"] = (
        1.0 if sum(1 for kw in pattern_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in pattern_keywords if kw in content) >= 1 else 0.0
    )

    # Check 4: Risk assessment
    risk_keywords = ["risk", "danger", "critical", "compromise", "privilege",
                     "escalat", "root access", "full access"]
    scores["risk_assessment"] = (
        1.0 if sum(1 for kw in risk_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in risk_keywords if kw in content) >= 1 else 0.0
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
- 已在工作區建立 `user_activity_report.md`
- 已同時列出有效與無效的使用者名稱
- 已找出最常被鎖定的使用者名稱（admin）
- 已分析使用者名稱樣態（字典攻擊、常見預設值）
- 已對最危險的使用者名稱提供風險評估
