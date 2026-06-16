---
id: task_gh_issue_triage
name: GitHub Issue 分流
category: skills
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
source_task_id: task_gh_issue_triage
source_benchmark: pinchbench
claw_eval_id: P144zh_gh_issue_triage
workspace_files: []
grading_weights:
  automated: 0.5
  llm_judge: 0.5
prerequisites:
- npm:@juppytt/fws
- cli:gh
---

# GitHub Issue 分流

## Prompt

你可透過 `gh` CLI 工具存取一個 GitHub 儲存庫（使用方式請見 `gh --help`）。此儲存庫
為 `testuser/my-project`。

請檢視開啟中的 issue 與 pull request：

1. 列出所有開啟中的 issue 與 PR
2. 逐一閱讀以理解其內容
3. 針對最關鍵的 issue，留下一則評論，內含你的分析與建議的後續步驟
4. 建立一份分流報告，存為 `triage_report.md`，內含每個項目的優先級、分類與建議
   行動，並依優先級排序

## Expected Behavior

助手應該：

1. 使用 gh CLI 列出並閱讀 issue 與 PR
2. 分析每個項目的急迫性與影響
3. 在最關鍵的 issue 上留下評論
4. 將一份結構化的分流報告寫入 `triage_report.md`

這項任務測試助手使用 gh CLI 進行多步驟 GitHub 工作流程的能力：列出、閱讀、評論與
綜整。

## Grading Criteria

- [ ] 助手使用 gh 列出 issue
- [ ] 助手使用 gh 列出或檢視 PR
- [ ] 助手閱讀個別的 issue／PR 以理解內容
- [ ] 助手在最關鍵的 issue 上留下評論
- [ ] 已在工作區建立檔案 `triage_report.md`
- [ ] 報告中包含所有開啟中的項目
- [ ] 每個項目皆被指派優先級
- [ ] 報告依優先級排序

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the GitHub issue triage task.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    listed_issues = False
    viewed_pr = False
    read_detail = False
    commented = False

    def extract_commands(transcript):
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
        if "gh" in cmd and ("issue list" in cmd or "api" in cmd and "issues" in cmd):
            listed_issues = True
        if "gh" in cmd and ("pr list" in cmd or "pr view" in cmd or "pulls" in cmd):
            viewed_pr = True
        if "gh" in cmd and ("issue view" in cmd or "issues/" in cmd):
            read_detail = True
        if "gh" in cmd and ("comment" in cmd or "comments" in cmd) and ("-f" in cmd or "--body" in cmd or "-X POST" in cmd):
            commented = True

    scores["listed_issues"] = 1.0 if listed_issues else 0.0
    scores["viewed_prs"] = 1.0 if viewed_pr else 0.0
    scores["read_detail"] = 1.0 if read_detail else 0.0
    scores["commented"] = 1.0 if commented else 0.0

    report_file = workspace / "triage_report.md"
    if report_file.exists():
        scores["report_created"] = 1.0
        content = report_file.read_text().lower()
        has_priorities = bool(re.search(r'(p[0-3]|critical|high|medium|low|urgent)', content))
        scores["priorities_assigned"] = 1.0 if has_priorities else 0.0
    else:
        scores["report_created"] = 0.0
        scores["priorities_assigned"] = 0.0

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

### 評分項 1：gh CLI 使用（權重 30%）

**1.0 分**：助手流暢地使用 gh CLI，以正確的參數列出、檢視並評論 issue／PR。

**0.75 分**：助手正確使用 gh CLI，僅有小幅參數問題。

**0.5 分**：助手使用了部分 gh 指令，但在語法上有困難。

**0.25 分**：助手幾乎沒有使用 gh CLI。

**0.0 分**：助手完全沒有使用 gh CLI。

### 評分項 2：分流品質（權重 40%）

**1.0 分**：所有項目皆正確排定優先級，分析準確且建議具體。

**0.75 分**：多數項目正確排定優先級，分析合理。

**0.5 分**：部分項目有排定優先級，但判斷上有明顯錯誤。

**0.25 分**：優先級指派多半不正確或缺漏。

**0.0 分**：未進行有意義的分流。

### 評分項 3：評論品質（權重 30%）

**1.0 分**：在正確的 issue 上留下評論，分析具洞見，且後續步驟具可執行性。

**0.75 分**：評論針對正確的 issue，建議合理。

**0.5 分**：有建立評論，但針對的 issue 較不恰當，或內容空泛。

**0.25 分**：有建立評論，但內容無關。

**0.0 分**：未建立評論。
