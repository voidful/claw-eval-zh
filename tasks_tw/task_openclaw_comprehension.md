---
id: task_openclaw_comprehension
name: |
  OpenClaw 報告閱讀理解
category: analysis
grading_type: automated
timeout_seconds: 300
language: zh
locale: zh-TW
region: TW
source_task_id: task_openclaw_comprehension
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T044tw_openclaw_comprehension
workspace_files:
- source: OpenClaw Agent Use Cases and Gap Analysis for PinchBench.pdf
  dest: openclaw_report.pdf
---

# OpenClaw 報告閱讀理解


## Prompt

工作區裡有一份關於 OpenClaw agent 使用案例的研究報告，檔名為 `openclaw_report.pdf`。
請從中擷取數項資訊，並寫入 `answer.txt`。請回答下列問題，每行一個答案：

1. 在過濾之前，公開登錄處（registry）中有多少個社群打造的技能（skill）？
2. 在過濾掉垃圾內容、重複項、非英文、加密貨幣／金融／交易，以及惡意內容後，還剩下多少個技能？
3. 數量最多的技能類別是哪一個，有多少個技能？（格式：「Category Name: count」）
4. 數量第二多的技能類別是哪一個，有多少個技能？（格式：「Category Name: count」）
5. 定義一個 OpenClaw 技能的檔案，其檔名為何？
6. OpenClaw 的 gateway 對外提供哪一種類型的 API？
7. 技能登錄處的資料是在哪一天收集的？
8. 這篇論文提出多少個新的 benchmark 任務？（只要數字）

請只根據報告內容作答；若某項資訊報告中找不到，請如實說明，不要臆測。

## Expected Behavior

助手應該：

1. 讀取並解析 PDF 檔 `openclaw_report.pdf`
2. 找到技能生態系統的統計區段，辨識出總共 5,705 個、過濾後 2,999 個技能
3. 找到技能類別表格，辨識出「AI & LLMs」（287）為最多、「Search & Research」（253）為第二多
4. 找出技能是由 `SKILL.md` 檔案定義的
5. 辨識出 gateway 使用「typed WebSocket API」
6. 找出資料收集日期為 February 7, 2026
7. 算出提出了 6 個 benchmark 任務
8. 把所有答案寫入 `answer.txt`，每行一個

## Grading Criteria

- [ ] 助手讀取了 PDF 檔
- [ ] 已建立輸出檔 answer.txt
- [ ] 技能總數（5705）正確
- [ ] 過濾後技能數（2999）正確
- [ ] 最多的類別（AI & LLMs: 287）正確
- [ ] 第二多的類別（Search & Research: 253）正確
- [ ] 辨識出技能檔名（SKILL.md）
- [ ] 辨識出 API 類型（typed WebSocket）
- [ ] 資料收集日期（February 7, 2026）正確
- [ ] 提出的任務數（6）正確

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)
    answer_file = workspace / "answer.txt"

    if not answer_file.exists():
        return {
            "file_created": 0.0,
            "total_skills_correct": 0.0,
            "filtered_skills_correct": 0.0,
            "top_category_correct": 0.0,
            "second_category_correct": 0.0,
            "skill_filename_correct": 0.0,
            "api_type_correct": 0.0,
            "date_correct": 0.0,
            "proposed_tasks_correct": 0.0,
        }

    scores["file_created"] = 1.0
    content = answer_file.read_text().strip()
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    full_text = content.lower()

    # Helper to extract numbers from text.
    # Strips leading list markers ("1. ", "2) ", etc.) so that agents which
    # number their answers ("1. 5705") don't have the line prefix returned
    # instead of the actual value.
    def extract_number(text):
        cleaned = re.sub(r'^\s*\d+[.)]\s+', '', text)
        numbers = re.findall(r'[\d,]+', cleaned)
        for n in numbers:
            val = int(n.replace(',', ''))
            if val > 0:
                return val
        return None

    # Line 1: Total skills (5705)
    line1 = lines[0] if len(lines) >= 1 else ""
    total = extract_number(line1)
    scores["total_skills_correct"] = 1.0 if total == 5705 else 0.0

    # Line 2: Filtered skills (2999)
    line2 = lines[1] if len(lines) >= 2 else ""
    filtered = extract_number(line2)
    scores["filtered_skills_correct"] = 1.0 if filtered == 2999 else 0.0

    # Line 3: Top category (AI & LLMs: 287)
    line3 = lines[2].lower() if len(lines) >= 3 else ""
    has_ai_llm = "ai" in line3 and "llm" in line3
    has_287 = extract_number(line3) == 287
    scores["top_category_correct"] = 1.0 if (has_ai_llm and has_287) else (0.5 if has_ai_llm or has_287 else 0.0)

    # Line 4: Second category (Search & Research: 253)
    line4 = lines[3].lower() if len(lines) >= 4 else ""
    has_search_research = "search" in line4 and "research" in line4
    has_253 = extract_number(line4) == 253
    scores["second_category_correct"] = 1.0 if (has_search_research and has_253) else (0.5 if has_search_research or has_253 else 0.0)

    # Line 5: Skill filename (SKILL.md)
    line5 = lines[4] if len(lines) >= 5 else ""
    scores["skill_filename_correct"] = 1.0 if "skill.md" in line5.lower() else 0.0

    # Line 6: API type (typed WebSocket)
    line6 = lines[5].lower() if len(lines) >= 6 else ""
    has_websocket = "websocket" in line6 or "web socket" in line6
    has_typed = "typed" in line6
    scores["api_type_correct"] = 1.0 if (has_websocket and has_typed) else (0.5 if has_websocket else 0.0)

    # Line 7: Date (February 7, 2026)
    line7 = lines[6].lower() if len(lines) >= 7 else ""
    date_patterns = [
        r"february\s+7[,\s]+2026",
        r"feb\.?\s+7[,\s]+2026",
        r"2026[-/]02[-/]07",
        r"02[-/]07[-/]2026",
        r"7\s+february[,\s]+2026",
        r"7\s+feb\.?[,\s]+2026",
    ]
    scores["date_correct"] = 1.0 if any(re.search(pattern, line7) for pattern in date_patterns) else 0.0

    # Line 8: Proposed tasks count (6)
    line8 = lines[7] if len(lines) >= 8 else ""
    task_count = extract_number(line8)
    scores["proposed_tasks_correct"] = 1.0 if task_count == 6 else 0.0

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
