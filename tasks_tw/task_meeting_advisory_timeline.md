---
id: task_meeting_advisory_timeline
name: |
  NTIA 諮詢委員會時間軸與期限
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_advisory_timeline
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T123tw_meeting_advisory_timeline
workspace_files:
- source: meetings/2012-05-30-meeting-transcript-ntia-csmac.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# NTIA 諮詢委員會時間軸與期限


## Prompt

我手上有一份美國政府諮詢委員會的會議逐字稿，存放在 `meeting-transcript.md`。這是商務部頻譜管理諮詢委員會（Commerce Spectrum Management Advisory Committee, CSMAC）於 2012 年 5 月 30 日召開的會議。

請幫我分析這份逐字稿，把所有關於時間軸、期限、時程與里程碑的內容，整理成一份結構化報告，存成 `timeline.md`。報告請涵蓋：

- **依時間順序排列的時間軸**：列出所有提及的日期、期限與里程碑（包含過去與未來）
- **工作小組（working group）期限**：各工作小組預計何時交付成果
- **下次會議資訊**：日期、地點、形式
- **歷史背景參照**：提及的過往事件及其日期，用以提供脈絡
- **轉換時程**：政府機關表示他們搬遷或轉換所需的時間長度

每一筆時間軸項目都請註明日期（或時間範圍）、所指事項、是誰提到的，以及任何附帶的條件或註記。

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿
2. 擷取所有時間相關的參照（明確日期、相對時間範圍、持續期間）
3. 依時間順序加以組織
4. 區分過去事件、目前狀態與未來期限

預期的關鍵時間軸項目：

**歷史／過去：**
- June 2010：總統關於 500 MHz 頻譜目標的備忘錄
- 會議前約 2.5 年（約 2009 年底／2010 年初）：歐巴馬政府確立 500 MHz 重新分配目標
- June 2010 備忘錄後 6 個月內：NTIA／各機關辨識出 115 MHz 的頻譜
- October 1, 2011：1755-1850 報告的期限（「臭名昭著的 10 月 1 日」）
- 約 2001：先前搬遷（1710-1755）的初步成本估算約 $900 million
- 過往經驗：1710-1755 MHz 頻段在 5 年內清空（主要為微波系統）
- 過去：政府與業界在 5 GHz Wi-Fi 上的合作努力

**目前（截至 2012 年 5 月 30 日）：**
- 會議日期：May 30, 2012
- 500 MHz 與 Sharing 兩個子委員會在工作小組階段暫停運作
- 已提交 T-Mobile/CTIA STA 申請，以進行頻段量測
- 工作小組邀請函將於下週內寄出

**未來期限：**
- 約下週：NTIA 將寄出工作小組邀請函、敲定共同主席
- 約 10 天：委員會共同主席就收尾計畫回報（Tramont 的提案）
- September 2012：工作小組 1（氣象衛星，1695-1710）的目標完成時間
- July 24, 2012：下次 CSMAC 會議於 Boulder, Colorado（下午場次）
- July 25-26, 2012：ISART 會議於 ITS 舉行，主題為頻譜共享（緊接 CSMAC 會議之後）
- January 2013：工作小組 2-5（1755-1850 頻段）的目標完成時間
- 5 年期程：執法機關退出 1755-1780 MHz（第一階段）
- 10 年期程：機關全面轉出該頻段（如報告所述）
- 10 年目標：500 MHz 頻譜重新分配（出自 2010 年備忘錄）

## Grading Criteria

- [ ] 已建立 `timeline.md` 檔案
- [ ] 提及 June 2010 的總統備忘錄
- [ ] 提及 October 2011 的報告期限
- [ ] 記載下次 CSMAC 會議（July 24, Boulder, CO）
- [ ] 提及氣象衛星工作小組的 September 2012 目標
- [ ] 提及其餘工作小組的 January 2013 目標
- [ ] 提及 10 年的轉換期程
- [ ] 記載緊接 CSMAC 會議之後的 ISART 會議
- [ ] 時間軸依時間順序組織

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the timeline extraction task.

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

    report_path = workspace / "timeline.md"
    if not report_path.exists():
        alternatives = ["timeline_report.md", "deadlines.md", "milestones.md", "schedule.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "presidential_memo": 0.0,
            "october_report": 0.0,
            "next_meeting": 0.0,
            "september_target": 0.0,
            "january_target": 0.0,
            "ten_year_transition": 0.0,
            "isart_meeting": 0.0,
            "chronological_order": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # June 2010 Presidential memorandum
    memo_patterns = [
        r'(?:june|jun).*2010.*(?:president|memorandum|memo)',
        r'(?:president|memorandum|memo).*(?:june|jun).*2010',
        r'2010.*(?:president|memorandum|memo).*(?:500|spectrum)',
    ]
    scores["presidential_memo"] = 1.0 if any(re.search(p, content_lower) for p in memo_patterns) else 0.0

    # October 2011 report deadline
    oct_patterns = [
        r'october.*(?:2011|1st|first).*(?:report|deadline)',
        r'(?:report|deadline).*october.*(?:2011|1st)',
        r'october 1.*(?:2011)?.*(?:report|deadline|infamous)',
        r'infamous.*october',
    ]
    scores["october_report"] = 1.0 if any(re.search(p, content_lower) for p in oct_patterns) else 0.0

    # Next meeting (July 24, Boulder)
    meeting_patterns = [
        r'july.*24.*(?:boulder|colorado)',
        r'boulder.*(?:colorado|co).*july',
        r'next.*meeting.*(?:july|boulder)',
        r'july 24',
    ]
    scores["next_meeting"] = 1.0 if any(re.search(p, content_lower) for p in meeting_patterns) else 0.0

    # September 2012 weather satellite target
    sept_patterns = [
        r'september.*(?:2012)?.*(?:weather|satellite|1695|complete|target|deadline)',
        r'(?:weather|satellite|1695).*september',
        r'(?:working group 1|wg.?1).*september',
        r'(?:earlier|shorter).*(?:date|time).*(?:september|sept)',
    ]
    scores["september_target"] = 1.0 if any(re.search(p, content_lower) for p in sept_patterns) else 0.0

    # January 2013 target for remaining working groups
    jan_patterns = [
        r'january.*(?:2013|next year).*(?:working group|complete|target|wrap|result)',
        r'(?:working group|1755).*january',
        r'january.*next year',
        r'wrap.*(?:up|issue).*january',
    ]
    scores["january_target"] = 1.0 if any(re.search(p, content_lower) for p in jan_patterns) else 0.0

    # 10-year transition timeframe
    ten_year_patterns = [
        r'ten.?year.*(?:transition|relocat|move|plan|time)',
        r'10.?year.*(?:transition|relocat|move|plan|time)',
        r'(?:transition|relocat|move).*ten.?year',
        r'(?:transition|relocat|move).*10.?year',
    ]
    scores["ten_year_transition"] = 1.0 if any(re.search(p, content_lower) for p in ten_year_patterns) else 0.0

    # ISART meeting
    isart_patterns = [
        r'isart.*(?:meeting|conference|its|spectrum sharing)',
        r'(?:following|after|next).*(?:two|2).*days.*(?:isart|its)',
        r'isart',
    ]
    scores["isart_meeting"] = 1.0 if any(re.search(p, content_lower) for p in isart_patterns) else 0.0

    # Chronological organization (check for year-ordered entries)
    years_found = []
    for match in re.finditer(r'20[01]\d', content):
        years_found.append(int(match.group()))
    if len(years_found) >= 3:
        # Check if years appear in roughly increasing order
        ordered_count = sum(1 for i in range(len(years_found) - 1)
                          if years_found[i] <= years_found[i + 1])
        ratio = ordered_count / (len(years_found) - 1) if len(years_found) > 1 else 0
        scores["chronological_order"] = 1.0 if ratio >= 0.6 else (0.5 if ratio >= 0.4 else 0.0)
    else:
        # Check for date-like patterns suggesting some ordering
        has_dates = bool(re.search(r'\d{4}', content))
        scores["chronological_order"] = 0.5 if has_dates else 0.0

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

### 評分項 1：時間軸項目的完整性（權重 35%）

**1.0 分**：擷取出所有主要時間軸項目——歷史參照（2010 備忘錄、October 2011 報告、先前 1710-1755 搬遷、5 GHz Wi-Fi 前例、2001 成本估算）、目前狀態項目，以及未來期限（September、January、下次會議、10 年計畫）。至少有 10 筆不同的時間軸項目。

**0.75 分**：擷取出多數項目，僅有一兩項遺漏。

**0.5 分**：記載主要期限，但缺少歷史脈絡或次要項目。

**0.25 分**：僅擷取最明顯的期限。

**0.0 分**：幾乎沒有或完全沒有時間軸項目。

### 評分項 2：日期與時間範圍的準確性（權重 25%）

**1.0 分**：所有日期、期間與相對時間範圍都準確取自逐字稿。沒有捏造的日期。

**0.75 分**：多數日期正確，僅有一處小錯。

**0.5 分**：部分日期正確，但有數處不準確。

**0.25 分**：多處日期錯誤或捏造日期。

**0.0 分**：日期大多不正確。

### 評分項 3：脈絡與歸屬（權重 20%）

**1.0 分**：每筆項目都包含是誰提到的、所指事項，以及任何條件或相依關係。發言者歸屬正確。

**0.75 分**：多數項目脈絡良好，僅有少許缺漏。

**0.5 分**：提供部分脈絡，但歸屬不一致。

**0.25 分**：脈絡或歸屬極少。

**0.0 分**：完全沒有提供脈絡。

### 評分項 4：組織與可用性（權重 20%）

**1.0 分**：時間軸依時間順序（或依過去／現在／未來邏輯）清楚組織，易於瀏覽，格式清晰，可區分日期與描述。

**0.75 分**：組織良好，僅有少許問題。

**0.5 分**：有一些組織，但難以追隨時序。

**0.25 分**：組織不佳。

**0.0 分**：沒有有意義的組織。
