---
id: task_calendar
name: 建立行事曆會議邀請（台灣職場）
category: productivity
grading_type: automated
timeout_seconds: 120
language: zh
locale: zh-TW
region: TW
source_task_id: task_calendar
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T002tw_calendar
workspace_files: []
---

# 建立行事曆會議邀請（台灣職場）

## Prompt

請幫我安排下週二下午 3 點（時區 Asia/Taipei）與同事王志明
（zhiming.wang@example.com.tw）的會議。標題訂為「專案同步會議」，並在說明
（description）中備註要討論 Q1 的產品 roadmap（藍圖）。

請產生一個 .ics 行事曆檔案來表示這個會議；時間請使用台灣時區，不要使用美國時區。

## Expected Behavior

助手應該：
1. 正確解析「下週二」的日期，並把時間設為下午 3:00（15:00）
2. 使用台灣時區（Asia/Taipei），不得使用美國時區
3. 產生 .ics 檔案，內含與會者 zhiming.wang@example.com.tw、標題「專案同步會議」
4. 在說明中提到 Q1 roadmap（藍圖）

## Grading Criteria

- [ ] 建立了 .ics 行事曆檔案
- [ ] 日期為下週二
- [ ] 時間為下午 3:00（15:00）
- [ ] 與會者包含 zhiming.wang@example.com.tw
- [ ] 標題為「專案同步會議」
- [ ] 說明提到 roadmap（藍圖）
- [ ] 使用台灣時區，未使用美國時區

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Calendar grader (Taiwan scenario + Asia/Taipei timezone)."""
    from pathlib import Path
    import re
    from datetime import datetime, timedelta
    workspace = Path(workspace_path)
    ics = list(workspace.glob("*.ics"))
    keys = ["file_created", "date_correct", "time_correct", "attendee_present",
            "title_correct", "description_present", "timezone_not_us"]
    if not ics:
        return {k: 0.0 for k in keys}
    c = ics[0].read_text(encoding="utf-8", errors="ignore")
    scores = {"file_created": 1.0}
    scores["attendee_present"] = 1.0 if re.search(
        r'ATTENDEE.*(zhiming\.wang@example\.com\.tw|@example\.com\.tw)', c, re.I) else 0.0
    scores["title_correct"] = 1.0 if re.search(
        r'SUMMARY.*(專案同步|Project Sync)', c, re.I) else 0.0
    scores["description_present"] = 1.0 if re.search(
        r'DESCRIPTION.*(roadmap|藍圖|路線圖|規劃|藍圖)', c, re.I) else 0.0
    scores["time_correct"] = 1.0 if re.search(r'DTSTART.*T1500\d{2}', c) else 0.0
    today = datetime.now()
    days = (1 - today.weekday()) % 7 or 7
    nt = (today + timedelta(days=days)).strftime("%Y%m%d")
    scores["date_correct"] = 1.0 if nt in c else 0.0
    # Taiwan timezone: must NOT reference a US timezone; bonus if Asia/Taipei present
    us = re.search(r'America/|US/|EST|EDT|PST|PDT', c)
    scores["timezone_not_us"] = 1.0 if not us else 0.0
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
