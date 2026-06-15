---
id: task_meeting_tech_action_items
name: 台灣公司產品會議：擷取行動項目
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_tech_action_items
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: new_tw_variant
claw_eval_tw_id: T115tw_meeting_tech_action_items
workspace_files:
- source: tw/meetings/tw_tech_product_meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台灣公司產品會議：擷取行動項目

## Prompt

工作區裡有一份會議逐字稿 meeting_transcript.md（虛構台灣軟體公司「鼎峰科技」的產品
行銷會議）。請閱讀逐字稿，擷取所有**行動項目（action items）**，並寫入 action_items.md。

每個行動項目請包含：負責人、要做的事、以及期限（若逐字稿有提到）。也請特別標出與
「活動／發表會」及「對內公告」相關的行動項目。

## Expected Behavior

助手應從逐字稿擷取至少 6 個行動項目與其負責人：
- 林佳蓉：6/30 前完成新版 API 文件
- 王志明：下週五前與通路夥伴確認新版報價
- 陳怡君：7/10 前確認產品發表會（活動）場地與議程
- 張家豪：6 月底前改版官網 messaging 與產品頁
- 黃淑芬：本週內整理客戶回饋並發出內部公告（announcement）
- 李俊賢：7/15 前完成資安稽核與滲透測試
並把結果整理成清楚的 action_items.md。

## Grading Criteria

- [ ] 建立報告檔案 action_items.md
- [ ] 至少擷取 5 個行動項目
- [ ] 至少正確標出 3 位負責人（林佳蓉/王志明/陳怡君/張家豪/黃淑芬/李俊賢）
- [ ] 標出與活動／發表會相關的行動項目
- [ ] 標出與對內公告相關的行動項目

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW tech-meeting action-items grader (fixed fictional transcript)."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    report = workspace / "action_items.md"
    if not report.exists():
        for alt in ["actions.md", "action-items.md", "meeting_actions.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in ["report_created", "min_action_items", "owners_identified",
                                 "events_actions", "announcement_actions"]}
    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")
    markers = re.findall(r'(?:行動項目|待辦|action item|^\s*[-*]\s|^\s*\d+[.)]\s)', c, re.MULTILINE | re.IGNORECASE)
    scores["min_action_items"] = 1.0 if len(markers) >= 5 else (0.5 if len(markers) >= 3 else 0.0)
    owners = ["林佳蓉", "王志明", "陳怡君", "張家豪", "黃淑芬", "李俊賢"]
    oc = sum(1 for o in owners if o in c)
    scores["owners_identified"] = 1.0 if oc >= 3 else (0.5 if oc >= 2 else 0.0)
    scores["events_actions"] = 1.0 if re.search(r'發表會|活動|展會', c) else 0.0
    scores["announcement_actions"] = 1.0 if re.search(r'公告|announcement|通知各部門|對內通知', c) else 0.0
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

### 評分項 1：行動項目完整度（權重 50%）
- 1.0：擷取 6 個行動項目，負責人、事項、期限正確
- 0.5：擷取多數但有遺漏或負責人錯置
- 0.0：嚴重遺漏或錯誤
### 評分項 2：分類標註（權重 30%）
- 1.0：正確標出活動／發表會與對內公告相關項目
- 0.5：標出其一
- 0.0：未標
### 評分項 3：可讀性（權重 20%）
- 1.0：條列清楚、含負責人與期限
- 0.0：雜亂
