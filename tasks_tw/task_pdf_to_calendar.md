---
id: task_pdf_to_calendar
name: 大學行事曆 PDF 轉 ICS 匯入（中興大學 114 學年度）
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
- source: tw/docs/nchu_114_calendar.pdf
  dest: school-calendar.pdf
---

# 大學行事曆 PDF 轉 ICS 匯入（中興大學 114 學年度）

## Prompt

我家小朋友（大學生）學校寄來「國立中興大學 114 學年度行事曆」的 PDF，已放在工作區的
`school-calendar.pdf`（中英雙語版）。我想把上面的重要日期全部匯入手機的行事曆 App，
可以麻煩你幫我整理嗎？

請從這份 PDF 擷取所有重要日期與活動，並在工作區建立一個名為 `school-calendar.ics`
的 ICS（iCalendar）檔案，內含所有活動。

每一筆活動請做到：
- SUMMARY 要與行事曆上的活動名稱相符、具描述性（中文或中英皆可）
- 使用正確的日期；跨多天的活動請用 DTSTART 與 DTEND
- 設為整日活動（使用 DATE 格式，而非 DATETIME）

備註：
- 這是以**民國紀年**標示的學年行事曆。114 學年度第 1 學期為 2025 年 8 月至 2026 年 1 月，
  第 2 學期為 2026 年 2 月至 7 月。請把民國年正確換算成西元年（**114 年 = 2025、
  115 年 = 2026**），不要把月／日對應錯年份。
- 行事曆為中英雙語，活動名稱可沿用原文（中文或英文皆可），以免日期對不上。

## Expected Behavior

助手應該：
1. 讀取並從 PDF 中擷取文字（中英雙語的學年行事曆）
2. 將每一筆有日期的重要記事解析為結構化活動，並正確把民國年換算成西元年
3. 寫出一個有效、內含所有活動的 ICS 檔案 `school-calendar.ics`

關鍵事件與正確日期（民國114學年度＝2025–2026）：
- 2025-09-08 全校學生開學、開始上課（註冊日）
- 2025-10-06 中秋節（放假）
- 2025-10-10 國慶日（放假）
- 2025-11-01 校慶
- 2025-12-22 第 1 學期期末考試（12/22–12/26）
- 2025-12-29 寒假開始
- 2026-01-01 元旦（放假）
- 2026-02-23 第 2 學期開學、開始上課（註冊日）
- 2026-02-28 和平紀念日（放假）
- 2026-04-04 兒童節（放假）、2026-04-05 清明節（放假）
- 2026-05-01 勞動節（放假）
- 2026-05-30 畢業典禮
- 2026-06-08 第 2 學期期末考試（6/8–6/12）
- 2026-06-19 端午節（放假）

備註：輸出檔名 `school-calendar.ics` 不可更改；日期須與 PDF 內容一致，且民國年已正確
換算為西元年。

## Grading Criteria

- [ ] 已在 `school-calendar.ics` 建立 ICS 檔案
- [ ] ICS 檔案有效（包含 VCALENDAR、VEVENT 區塊）
- [ ] 至少擷取出 10 筆活動
- [ ] 包含第 1 學期開學／上課活動（2025-09-08）
- [ ] 包含中秋節活動（2025-10-06）
- [ ] 包含國慶日活動（2025-10-10）
- [ ] 包含第 1 學期期末考試（2025-12-22）
- [ ] 包含寒假開始（2025-12-29）
- [ ] 包含元旦（2026-01-01）
- [ ] 包含第 2 學期開學／上課（2026-02-23）
- [ ] 包含和平紀念日（2026-02-28）
- [ ] 包含畢業典禮（2026-05-30）
- [ ] 包含端午節（2026-06-19）
- [ ] 民國年已正確換算為西元年（114 年→2025、115 年→2026）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """T003 中興大學 114 學年度行事曆 → ICS grader（台灣在地版）。

    檢查 agent 產出的 school-calendar.ics 是否含正確的西元日期；重點在民國年→西元年
    換算（114=2025、115=2026）。以日期為主要訊號（PDF 內各日期幾乎一對一對應到單一
    事件），輔以結構檢查。僅用標準函式庫。
    """
    from pathlib import Path

    ws = Path(workspace_path)
    ics = ws / "school-calendar.ics"
    if not ics.exists():
        cands = sorted(ws.glob("**/*.ics"))
        ics = cands[0] if cands else None

    # (check_name, ISO 日期) — 取自 PDF 之實際重要記事
    KEY = [
        ("fall_classes_begin", "2025-09-08"),
        ("mid_autumn", "2025-10-06"),
        ("national_day", "2025-10-10"),
        ("fall_final_exam", "2025-12-22"),
        ("winter_break", "2025-12-29"),
        ("new_year_day", "2026-01-01"),
        ("spring_classes_begin", "2026-02-23"),
        ("peace_memorial", "2026-02-28"),
        ("graduation", "2026-05-30"),
        ("dragon_boat", "2026-06-19"),
    ]
    scores = {"ics_created": 0.0, "ics_valid": 0.0, "min_events": 0.0}
    for name, _ in KEY:
        scores[name] = 0.0
    if not ics or not ics.exists():
        return scores

    text = ics.read_text(encoding="utf-8", errors="ignore")
    up = text.upper()
    scores["ics_created"] = 1.0
    scores["ics_valid"] = 1.0 if ("VCALENDAR" in up and "VEVENT" in up) else 0.0
    n = up.count("BEGIN:VEVENT")
    scores["min_events"] = 1.0 if n >= 10 else round(min(n, 10) / 10.0, 2)

    for name, iso in KEY:
        compact = iso.replace("-", "")          # 20250908
        scores[name] = 1.0 if (compact in text or iso in text) else 0.0
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
