---
id: task_gws_email_triage
name: |
  GWS 郵件分類整理（Triage）
category: integrations
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
region: TW
source_task_id: task_gws_email_triage
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T145tw_gws_email_triage
workspace_files: []
grading_weights:
  automated: 0.5
  llm_judge: 0.5
prerequisites:
- npm:@juppytt/fws
- cli:gws
---

# GWS 郵件分類整理（Triage）


## Prompt

你可以透過 gws CLI 工具操作一個 Google Workspace 帳號（用 `gws --help` 查看
用法）。

你的收件匣有數封未讀郵件，請整理（triage）它們：
1. 檢查未讀郵件
2. 逐封閱讀，理解內容與緊急程度
3. 針對最緊急的一封郵件，草擬一封回覆（存成草稿，不要寄出）
4. 建立一份分類報告，存到 triage_report.md，列出每封郵件的優先級（P0–P3）、
   分類與建議動作，並依優先級排序（最緊急在前）

## Expected Behavior

助手應該：
1. 探索並使用 gws 的 Gmail 指令來列出與閱讀郵件
2. 分析郵件內容、寄件人與緊急程度
3. 找出最緊急的一封並建立草稿回覆
4. 把結構化的分類報告寫入 triage_report.md

本任務測試助手能否探索並使用 gws CLI 完成多步驟郵件流程：列出、閱讀、草擬、
彙整。注意：gws 指令、triage_report.md 檔名與 P0–P3 標記都不可更改。

## Grading Criteria

- [ ] 助手用 gws 列出未讀郵件
- [ ] 助手用 gws 閱讀個別郵件
- [ ] 助手為最緊急郵件建立草稿回覆
- [ ] 工作區建立了檔案 triage_report.md
- [ ] 報告涵蓋所有未讀郵件
- [ ] 每封郵件都標了優先級（P0–P3）
- [ ] 每封郵件都有建議動作
- [ ] 報告依優先級排序

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the GWS email triage task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    used_list = False
    used_get = False
    used_draft = False

    def extract_commands(transcript):
        """Extract shell commands from transcript, handling multiple tool call formats."""
        cmds = []
        for event in transcript:
            if event.get("type") != "message":
                continue
            msg = event.get("message", {})
            for item in msg.get("content", []):
                t = item.get("type", "")
                if t in ("tool_use", "toolCall"):
                    cmd = (
                        item.get("input", {}).get("command", "")
                        or item.get("arguments", {}).get("command", "")
                        or item.get("params", {}).get("command", "")
                    )
                    if cmd:
                        cmds.append(cmd)
        return cmds

    for cmd in extract_commands(transcript):
        if "gws" in cmd and ("triage" in cmd or "messages list" in cmd):
            used_list = True
        if "gws" in cmd and "messages get" in cmd:
            used_get = True
        if "gws" in cmd and "drafts create" in cmd:
            used_draft = True

    scores["listed_emails"] = 1.0 if used_list else 0.0
    scores["read_messages"] = 1.0 if used_get else 0.0
    scores["created_draft"] = 1.0 if used_draft else 0.0

    report_file = workspace / "triage_report.md"
    if report_file.exists():
        scores["report_created"] = 1.0
        content = report_file.read_text().lower()

        has_priorities = bool(re.search(r'p[0-3]', content))
        scores["priorities_assigned"] = 1.0 if has_priorities else 0.0

        p0_pos = content.find("p0")
        p3_pos = content.find("p3")
        if p0_pos >= 0 and p3_pos >= 0:
            scores["sorted_by_priority"] = 1.0 if p0_pos < p3_pos else 0.0
        else:
            scores["sorted_by_priority"] = 0.5
    else:
        scores["report_created"] = 0.0
        scores["priorities_assigned"] = 0.0
        scores["sorted_by_priority"] = 0.0

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

### 評分項 1：GWS CLI 探索與使用（權重 30%）
- 1.0：流暢探索並使用 gws Gmail 指令（list、get、drafts），參數正確
- 0.75：使用正確，但參數有小問題或有多餘呼叫
- 0.5：用了部分指令，但語法卡頓或漏掉關鍵指令
- 0.25：幾乎沒用 gws CLI 或指令錯誤
- 0.0：完全沒用 gws CLI

### 評分項 2：分類品質（權重 40%）
- 1.0：所有郵件優先級正確、分類準確、建議具體可執行
- 0.75：多數正確，僅少量誤判，建議合理
- 0.5：部分正確但有明顯判斷錯誤，建議籠統
- 0.25：優先級多半錯誤或缺失
- 0.0：沒有做有意義的分類

### 評分項 3：草稿回覆品質（權重 30%）
- 1.0：草稿針對正確的緊急郵件，回覆專業並切合情境
- 0.75：針對正確郵件、回覆合理，但語氣或內容可再加強
- 0.5：有草稿但對象較不恰當，或內容籠統
- 0.25：有草稿但格式錯誤或內容不相關
- 0.0：沒有建立草稿
