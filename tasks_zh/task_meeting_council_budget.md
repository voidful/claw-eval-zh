---
id: task_meeting_council_budget
name: Tampa City Council — 擷取預算討論
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_council_budget
source_benchmark: pinchbench
claw_eval_id: P111zh_meeting_council_budget
workspace_files:
- source: meetings/2026-04-02-tampa-city-council-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# Tampa City Council — 擷取預算討論

## Prompt

我這裡有一份 2026 年 4 月 2 日舉行的 Tampa City Council 會議逐字稿，存放在 `transcript.md`。請產生 `budget_report.md`，擷取所有與預算相關的討論，包含金額、背景脈絡、議會行動與關切事項。最後附上一個**財務彙總（financial summary）**。

## Expected Behavior

關鍵財務項目：Water/Wastewater Capacity Fees（$3B 投資、$170M 補助、目前每單位 $1,020/$1,237、提議 $1,530/$1,847、每年額外 $1.5-2M 收入）、Rome Yard（$94M Phase 4、開發商投資 $3M）、Howard Avenue Annex（總計 $34.2M、已支出 $7M、Phase 2 為 $27.2M）、Fire Station 24（GMP 於 May 15）、$650K gas settlement、Zion Cemetery 請求 $8M、管線計畫每月 $8+$8。

## Grading Criteria

- [ ] 已建立報告檔案 budget_report.md
- [ ] 已辨識容量費金額
- [ ] 已提及 $3 billion 投資
- [ ] 已記下 $1.5-2 million 收入增加
- [ ] 已辨識 Rome Yard $94 million
- [ ] 已辨識 Annex $34.2 million
- [ ] 已記下 $7 million Phase 1
- [ ] 已提及 $650,000 settlement
- [ ] 已掌握 Zion $8 million
- [ ] 已包含財務彙總

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    scores = {}
    workspace = Path(workspace_path)
    report_path = workspace / "budget_report.md"
    if not report_path.exists():
        for alt in ["budget.md", "financial_report.md", "finances.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in ["report_created", "capacity_fee_amounts", "three_billion", "annual_revenue_increase", "rome_yard_94m", "annex_34m", "phase1_7m", "gas_settlement_650k", "zion_8m", "financial_summary"]}
    scores["report_created"] = 1.0
    content = report_path.read_text()
    cl = content.lower()
    scores["capacity_fee_amounts"] = 1.0 if (re.search(r'1[,.]?0[12]0', content) and re.search(r'1[,.]?[58][34]\d', content)) else 0.0
    scores["three_billion"] = 1.0 if re.search(r'(?:\$?3\s*billion|3B)', cl) else 0.0
    scores["annual_revenue_increase"] = 1.0 if (re.search(r'(?:1\.5|two)\s*(?:million|m\b)', cl) and re.search(r'(?:revenue|additional|year)', cl)) else 0.0
    scores["rome_yard_94m"] = 1.0 if re.search(r'(?:\$?94\s*million|94M)', cl) else 0.0
    scores["annex_34m"] = 1.0 if re.search(r'(?:\$?34\.?2?\s*million)', cl) else 0.0
    scores["phase1_7m"] = 1.0 if (re.search(r'(?:\$?7\s*million)', cl) and re.search(r'(?:spent|phase|already)', cl)) else 0.0
    scores["gas_settlement_650k"] = 1.0 if re.search(r'(?:650[,.]?000|\$650)', cl) else 0.0
    scores["zion_8m"] = 1.0 if (re.search(r'zion', cl) and re.search(r'(?:\$?8\s*million)', cl)) else 0.0
    scores["financial_summary"] = 1.0 if re.search(r'(?:financial|fiscal|budget)\s*(?:summary|overview|total)', cl) else 0.0
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

### 評分項 1：財務資料擷取（權重 40%）
**1.0 分**：所有主要金額皆正確擷取。**0.5 分**：部分缺漏。**0.0 分**：完全沒有。

### 評分項 2：背景脈絡（權重 25%）
**1.0 分**：每一項目皆有清楚的背景脈絡。**0.5 分**：部分有。**0.0 分**：完全沒有。

### 評分項 3：周延度（權重 20%）
**1.0 分**：涵蓋所有會議段落。**0.5 分**：僅主要部分。**0.0 分**：不完整。

### 評分項 4：彙總（權重 15%）
**1.0 分**：彙總清楚。**0.5 分**：不完整。**0.0 分**：完全沒有。
