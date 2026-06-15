---
id: task_meeting_council_votes
name: 台灣（虛構）市議會：彙整議案與表決結果
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_votes
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: new_tw_variant
claw_eval_tw_id: T109tw_meeting_council_votes
workspace_files:
- source: tw/meetings/tw_council_meeting.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 台灣（虛構）市議會：彙整議案與表決結果

## Prompt

工作區裡有一份議會逐字稿 transcript.md（虛構的台灣地方議會「南港市議會」定期會）。
請以台灣地方議會的語境閱讀逐字稿，彙整每個議案的**表決結果**，寫入 votes_report.md。

每個議案請列出：議案主題、表決結果（贊成／反對票數、是否一致通過、是否有議員迴避、
是否為一讀、是否延期等）。

## Expected Behavior

助手應彙整七個議案（皆為虛構）：
1. 會議紀錄：全體無異議確認通過
2. 年度總預算案：12 票贊成、0 反對，通過
3. 道路拓寬案：林議員利益迴避，其餘 10 贊成 1 反對，通過
4. 公園命名案：全體一致（unanimous）通過
5. 清運費調整自治條例：完成一讀（first reading）
6. 都市更新案：延期（continued）
7. 社福補助加碼案：7 票贊成、5 反對，通過

## Grading Criteria

- [ ] 建立報告檔案 votes_report.md
- [ ] 正確彙整預算案表決（12 比 0 通過）
- [ ] 標出道路拓寬案有議員利益迴避
- [ ] 標出公園命名案為全體一致通過
- [ ] 標出清運費調整案為一讀
- [ ] 標出都市更新案延期

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW (fictional) council votes grader (fixed transcript)."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    report = workspace / "votes_report.md"
    if not report.exists():
        for alt in ["votes.md", "motions.md", "vote_report.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in ["report_created", "budget_vote", "recuse_item",
                                 "unanimous_item", "first_reading_item", "continued_item"]}
    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")
    scores["budget_vote"] = 1.0 if (re.search(r'預算', c) and re.search(r'12\D{0,6}0|12\s*票', c)) else 0.0
    scores["recuse_item"] = 1.0 if (re.search(r'拓寬|道路', c) and re.search(r'迴避|回避|利益|abstain|recus', c)) else 0.0
    scores["unanimous_item"] = 1.0 if (re.search(r'命名|公園', c) and re.search(r'一致|無異議|unanimou', c)) else 0.0
    scores["first_reading_item"] = 1.0 if (re.search(r'清運|清潔|垃圾', c) and re.search(r'一讀|first read', c)) else 0.0
    scores["continued_item"] = 1.0 if (re.search(r'都更|都市更新', c) and re.search(r'延期|保留|continu|defer', c)) else 0.0
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

### 評分項 1：表決結果正確度（權重 60%）
- 1.0：各議案的票數、迴避、一致、一讀、延期等狀態皆正確
- 0.5：多數正確但有少量錯誤
- 0.0：嚴重錯誤
### 評分項 2：完整度（權重 25%）
- 1.0：七個議案皆涵蓋
- 0.5：遺漏一兩案
- 0.0：多數遺漏
### 評分項 3：呈現（權重 15%）
- 1.0：逐案清楚列出主題與結果
- 0.0：雜亂
