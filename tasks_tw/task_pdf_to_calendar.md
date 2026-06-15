---
id: task_pdf_to_calendar
name: PDF 學校行事曆轉 ICS 匯入
category: productivity
grading_type: automated
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_pdf_to_calendar
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T003tw_pdf_to_calendar
workspace_files:
- source: school-calendar.pdf
  dest: school-calendar.pdf
---

# PDF 學校行事曆轉 ICS 匯入

## Prompt

我家小朋友學校寄來一份學年度行事曆 PDF，已經放在工作區的 `school-calendar.pdf`。
我想把上面的活動全部匯入手機的行事曆 App，可以麻煩你幫我整理嗎？

請從這份 PDF 擷取所有日期與活動，並在工作區建立一個名為 `school-calendar.ics`
的 ICS（iCalendar）檔案，內含所有活動。

每一筆活動請做到：
- SUMMARY 要與 PDF 上的活動名稱相符、具描述性
- 使用正確的日期；跨多天的活動請用 DTSTART 與 DTEND
- 設為整日活動（使用 DATE 格式，而非 DATETIME）

備註：這份 PDF 是英文版的學校行事曆，活動名稱請沿用原文（例如 First Day of
School、Labor Day），不用翻成中文，以免日期對不上。

## Expected Behavior

助手應該：
1. 讀取並從 PDF 中擷取文字
2. 將每一筆有日期的項目解析為結構化活動
3. 寫出一個有效、內含所有活動的 ICS 檔案

備註：檔名 `school-calendar.pdf` 與輸出檔名 `school-calendar.ics` 不可更改；
活動名稱與日期皆以 PDF 原始內容為準（英文活動名、原始學年度日期）。

## Grading Criteria

- [ ] 已在 `school-calendar.ics` 建立 ICS 檔案
- [ ] ICS 檔案有效（包含 VCALENDAR、VEVENT 區塊）
- [ ] 至少擷取出 10 筆活動
- [ ] 包含開學日（First Day of School）活動（2026 年 8 月 3 日）
- [ ] 包含學期最後一日（Last Day of School）活動（2027 年 5 月 21 日）
- [ ] 包含勞動節（Labor Day）活動（2026 年 9 月 7 日）
- [ ] 包含聖誕假期（Christmas Break）活動（2026 年 12 月）
- [ ] 包含春假（Spring Break）活動（2027 年 4 月）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the PDF-to-calendar task.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    ics_path = workspace / "school-calendar.ics"

    if not ics_path.exists():
        return {
            "file_created": 0.0,
            "valid_ics": 0.0,
            "min_events": 0.0,
            "first_day_of_school": 0.0,
            "last_day_of_school": 0.0,
            "labor_day": 0.0,
            "christmas_break": 0.0,
            "spring_break": 0.0,
        }

    scores["file_created"] = 1.0
    content = ics_path.read_text()

    # Valid ICS structure
    has_vcalendar = "BEGIN:VCALENDAR" in content and "END:VCALENDAR" in content
    has_vevents = content.count("BEGIN:VEVENT") >= 1
    scores["valid_ics"] = 1.0 if has_vcalendar and has_vevents else 0.0

    # At least 10 events
    event_count = content.count("BEGIN:VEVENT")
    scores["min_events"] = 1.0 if event_count >= 10 else round(event_count / 10, 1)

    # First Day of School - August 3, 2026
    scores["first_day_of_school"] = 1.0 if "20260803" in content else 0.0

    # Last Day of School - May 21, 2027
    scores["last_day_of_school"] = 1.0 if "20270521" in content else 0.0

    # Labor Day - September 7, 2026
    scores["labor_day"] = 1.0 if "20260907" in content else 0.0

    # Christmas Break - December 21, 2026
    scores["christmas_break"] = 1.0 if "20261221" in content else 0.0

    # Spring Break - April 5, 2027
    scores["spring_break"] = 1.0 if "20270405" in content else 0.0

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
