---
id: task_log_ssh_unusual_times
name: SSH 驗證日誌 — 異常時段登入偵測
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_ssh_unusual_times
source_benchmark: pinchbench
claw_eval_id: P094zh_log_ssh_unusual_times
workspace_files:
- dest: auth.log
  source: logs/openssh_auth.log
---

# SSH 驗證日誌 — 異常時段登入偵測

## Prompt

請分析位於 `auth.log` 的 OpenSSH 驗證日誌，找出發生在異常時段的登入活動。
假設正常上班時間為伺服器本地時間 08:00–18:00。

你的報告應包含：

1. **每小時分布（Hourly Distribution）**：每個小時的驗證事件計數
2. **非上班時段活動（Off-Hours Activity）**：所有發生在 08:00 之前或 18:00 之後的驗證事件
3. **清晨分析（Early Morning Analysis）**：詳細拆解 06:00–08:00 之間的事件（日誌中最早的時段）
4. **成功登入時點（Successful Logins Timing）**：成功登入發生在什麼時候？是否在上班時間內？
5. **攻擊時點型態（Attack Timing Patterns）**：攻擊者是否偏好特定時段？是否有規律？
6. **時間性風險評估（Temporal Risk Assessment）**：依時點型態判斷，哪些時段應最密切監控？

請將報告寫入 `unusual_hours_report.md`，以結構良好的 markdown 文件呈現。

## Expected Behavior

助手應解析日誌並產出：

**每小時分布：**
- 06:xx — 7 筆（日誌從 06:55 開始）
- 07:xx — 169 筆
- 08:xx — 118 筆
- 09:xx — 676 筆（尖峰小時）
- 10:xx — 530 筆（日誌於 10:59 結束）

**非上班時段活動：**
- 08:00 之前有 7 筆（在 06:55–06:56）
- 所有 08:00 之前的條目皆為攻擊流量（登入失敗、BREAK-IN 警告）

**成功登入時點：**
- 使用者 fztu 於 09:32:20 登入 — 在上班時間內

**攻擊時點型態：**
- 攻擊量從 07:xx 到 09:xx 急遽升高
- 尖峰攻擊量出現在 09:xx，共 676 筆
- 這可能代表攻擊者位於另一個時區，當地 09:00（LabSZ 時間）正是其工作時段
- 清晨的條目（06:55）代表一波攻擊行動的尾聲或起點

可接受的差異：
- 「異常時段」的定義可能不同
- 時區假設可能不同
- 評估用語會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `unusual_hours_report.md`
- [ ] 提供事件的每小時分布
- [ ] 另行標示出非上班時段（08:00 之前）的事件
- [ ] 記下成功登入的時點（09:32:20，在上班時間內）
- [ ] 分析攻擊時點型態

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the SSH unusual hours detection task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "unusual_hours_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "hourly_distribution": 0.0,
            "off_hours_identified": 0.0,
            "successful_timing": 0.0,
            "timing_patterns": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Hourly distribution provided
    hour_markers = ["06:", "07:", "08:", "09:", "10:"]
    alt_markers = ["6 am", "7 am", "8 am", "9 am", "10 am", "6:00", "7:00",
                   "8:00", "9:00", "10:00"]
    all_markers = hour_markers + alt_markers
    hours_found = sum(1 for m in all_markers if m in content)
    scores["hourly_distribution"] = (
        1.0 if hours_found >= 4 else
        0.5 if hours_found >= 2 else 0.0
    )

    # Check 2: Off-hours events identified
    off_hours_keywords = ["before 08", "before 8:00", "early morning",
                          "06:55", "pre-business", "off-hour", "off hour",
                          "unusual hour", "outside business"]
    scores["off_hours_identified"] = (
        1.0 if sum(1 for kw in off_hours_keywords if kw in content) >= 1 else 0.0
    )

    # Check 3: Successful login timing noted
    has_fztu = "fztu" in content
    has_time = "09:32" in content or "9:32" in content
    has_business = any(kw in content for kw in ["business hour", "normal hour",
                                                  "working hour", "during"])
    scores["successful_timing"] = (
        1.0 if has_fztu and (has_time or has_business) else
        0.5 if has_fztu else 0.0
    )

    # Check 4: Timing patterns analyzed
    pattern_keywords = ["peak", "escalat", "increas", "pattern", "trend",
                        "676", "530", "busiest", "most active", "concentrated"]
    scores["timing_patterns"] = (
        1.0 if sum(1 for kw in pattern_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in pattern_keywords if kw in content) >= 1 else 0.0
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
- 已在工作區建立 `unusual_hours_report.md`
- 提供事件的每小時分布
- 另行標示出非上班時段（08:00 之前）的事件
- 記下成功登入的時點（09:32:20，在上班時間內）
- 分析攻擊時點型態
