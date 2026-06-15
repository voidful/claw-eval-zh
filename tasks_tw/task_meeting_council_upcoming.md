---
id: task_meeting_council_upcoming
name: |
  市議會逐字稿 — 擷取後續事件與截止期限
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_upcoming
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T112tw_meeting_council_upcoming
workspace_files:
- source: meetings/2026-04-02-tampa-city-council-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 市議會逐字稿 — 擷取後續事件與截止期限


## Prompt

我手邊有一份 2026 年 4 月 2 日舉行的 Tampa City Council 會議逐字稿，存放在 `transcript.md`。請幫我產生 `upcoming_events.md`，依時間先後列出所有後續事件、截止期限與未來日期。請包含日期、事件、負責方，以及狀態（confirmed/proposed/tentative）。最後以一個**「What to watch」**重點區段作結。

## Expected Behavior

關鍵項目：April 16（Veterans Committee、第 26-28 項、$650K 重新分配）、April 20（East Tampa Town Hall，地點 Fair Oaks）、May 7（倫理報告、LDC 更新）、May 15（Fire Station 24 GMP）、August 3/10/17（預算工作坊）、March 1 2027（容量費開始）、September 2027（Fire Station 24 完工）、September 2028（Rome Yard Phase 4）、March 2030（費用全面分階段到位）、下週（HART Board）、約 60 天內（Rome Yard 交割）。

## Grading Criteria

- [ ] 已建立報告檔案 upcoming_events.md
- [ ] 已辨識 April 16 的各項目
- [ ] April 20 East Tampa Town Hall
- [ ] May 7 倫理報告
- [ ] Fire Station 24 GMP（May 15）
- [ ] 預算工作坊（August）
- [ ] March 2027 容量費
- [ ] September 2028 Rome Yard
- [ ] 依時間先後組織
- [ ] 重點區段

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    scores = {}
    workspace = Path(workspace_path)
    report_path = workspace / "upcoming_events.md"
    if not report_path.exists():
        for alt in ["events.md", "deadlines.md", "upcoming.md", "timeline.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in ["report_created", "april_16_items", "april_20_townhall", "may_7_ethics", "fire_station_gmp", "budget_workshops", "march_2027_fees", "rome_yard_sept2028", "chronological", "highlights_section"]}
    scores["report_created"] = 1.0
    content = report_path.read_text()
    cl = content.lower()
    scores["april_16_items"] = 1.0 if (re.search(r'april\s*16', cl) and re.search(r'(?:veteran|26|27|28|annex)', cl)) else 0.0
    scores["april_20_townhall"] = 1.0 if (re.search(r'april\s*20', cl) and re.search(r'(?:east\s*tampa|town\s*hall|fair\s*oaks)', cl)) else 0.0
    scores["may_7_ethics"] = 1.0 if (re.search(r'may\s*7', cl) and re.search(r'(?:ethic|conflict|ldc)', cl)) else 0.0
    scores["fire_station_gmp"] = 1.0 if (re.search(r'(?:may\s*15|gmp)', cl) and re.search(r'(?:fire\s*station|station\s*24)', cl)) else 0.0
    scores["budget_workshops"] = 1.0 if (re.search(r'august\s*(?:3|10|17)', cl) and re.search(r'(?:budget|workshop)', cl)) else 0.0
    scores["march_2027_fees"] = 1.0 if (re.search(r'march.*2027', cl) and re.search(r'(?:capacity|fee|water)', cl)) else 0.0
    scores["rome_yard_sept2028"] = 1.0 if (re.search(r'(?:september|sept).*28', cl) and re.search(r'(?:rome|phase\s*4|completion)', cl)) else 0.0
    scores["chronological"] = 1.0 if len(re.findall(r'(april|may|june|august|september|march)\s*\d{0,4}', cl)) >= 4 else 0.0
    scores["highlights_section"] = 1.0 if re.search(r'(?:watch|highlight|key|significant|important)', cl) else 0.0
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

### 評分項 1：完整度（權重 35%）
**1.0 分**：12 項以上事件。**0.75 分**：9-11 項。**0.5 分**：5-8 項。**0.0 分**：完全沒有。

### 評分項 2：準確度（權重 25%）
**1.0 分**：所有日期皆正確。**0.5 分**：有若干錯誤。**0.0 分**：錯誤。

### 評分項 3：背景脈絡（權重 25%）
**1.0 分**：每一事件皆有清楚的背景脈絡。**0.5 分**：基本。**0.0 分**：完全沒有。

### 評分項 4：優先排序（權重 15%）
**1.0 分**：重點整理有效。**0.5 分**：薄弱。**0.0 分**：完全沒有。
