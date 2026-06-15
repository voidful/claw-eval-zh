---
id: task_calendar
name: 行事曆事件建立
category: productivity
grading_type: automated
timeout_seconds: 120
language: zh
locale: zh-TW
source_task_id: task_calendar
source_benchmark: pinchbench
claw_eval_id: P002zh_calendar
workspace_files: []
---

# 行事曆事件建立

## Prompt

你沒有存取真實行事曆的權限。請改以在工作區（workspace）中撰寫一個 ICS
（iCalendar）檔案的方式，模擬建立一筆行事曆事件。請依照下方說明操作，並把它
當成使用者的需求來處理。

使用者需求：請在下週二（next Tuesday）下午 3 點安排一場會議，與會者為
john@example.com。標題設為「Project Sync」，並加上一段備註，說明要討論
Q1 roadmap。

## Expected Behavior

助手應該以在工作區中產生一個 ICS（iCalendar）檔案的方式來模擬行事曆建立
（不存取任何外部行事曆）。助手需要：

1. 根據目前日期解析相對日期「next Tuesday（下週二）」
2. 將時間設定為下午 3:00（15:00）
3. 包含與會者的電子郵件地址
4. 設定事件標題／摘要（summary）
5. 加入一段提及 Q1 roadmap 的描述（description）

其他做法（例如建立其他結構化資料檔）也可以接受，但 ICS 格式最具可攜性、也最
容易測試。請勿提及缺少行事曆整合一事；請把這項任務視為一次建立檔案的模擬。

## Grading Criteria

- [ ] 已建立事件檔案（ICS 或同等格式）
- [ ] 日期設為從執行日起算的下週二
- [ ] 時間設為下午 3:00（15:00）
- [ ] 已包含與會者 john@example.com
- [ ] 標題／摘要為「Project Sync」
- [ ] 描述中提及 Q1 roadmap

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the calendar task based on ICS file creation and content.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re
    from datetime import datetime, timedelta

    scores = {}
    workspace = Path(workspace_path)

    # Find any .ics file in workspace
    ics_files = list(workspace.glob("*.ics"))

    if not ics_files:
        # No ICS file found
        scores["file_created"] = 0.0
        scores["date_correct"] = 0.0
        scores["time_correct"] = 0.0
        scores["attendee_present"] = 0.0
        scores["title_correct"] = 0.0
        scores["description_present"] = 0.0
        return scores

    scores["file_created"] = 1.0

    # Read the ICS file content
    ics_content = ics_files[0].read_text()

    # Check for attendee
    if re.search(r'ATTENDEE.*john@example\.com', ics_content, re.IGNORECASE):
        scores["attendee_present"] = 1.0
    else:
        scores["attendee_present"] = 0.0

    # Check for title
    if re.search(r'SUMMARY.*Project Sync', ics_content, re.IGNORECASE):
        scores["title_correct"] = 1.0
    else:
        scores["title_correct"] = 0.0

    # Check for description mentioning roadmap
    if re.search(r'DESCRIPTION.*roadmap', ics_content, re.IGNORECASE):
        scores["description_present"] = 1.0
    else:
        scores["description_present"] = 0.0

    # Check for time (3:00 PM = 15:00, allow any seconds value)
    if re.search(r'DTSTART.*T1500\d{2}', ics_content):
        scores["time_correct"] = 1.0
    else:
        scores["time_correct"] = 0.0

    # Check for date (next Tuesday)
    # Require exact next-Tuesday date
    today = datetime.now()
    days_ahead = (1 - today.weekday()) % 7  # Tuesday is 1
    if days_ahead == 0:
        days_ahead = 7
    next_tuesday = today + timedelta(days=days_ahead)

    # Format: YYYYMMDD
    expected_date = next_tuesday.strftime("%Y%m%d")
    if expected_date in ics_content:
        scores["date_correct"] = 1.0
    else:
        scores["date_correct"] = 0.0

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
