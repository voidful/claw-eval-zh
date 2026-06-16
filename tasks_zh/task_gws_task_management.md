---
id: task_gws_task_management
name: GWS 任務管理
category: integrations
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
source_task_id: task_gws_task_management
source_benchmark: pinchbench
claw_eval_id: P147zh_gws_task_management
workspace_files: []
grading_weights:
  automated: 0.6
  llm_judge: 0.4
prerequisites:
- npm:@juppytt/fws
- cli:gws
---

# GWS 任務管理

## Prompt

你可以透過 `gws` CLI 工具操作一個 Google Workspace 帳號（用 `gws --help` 查看用法）。

請根據你收件匣中的內容來管理你的任務：

1. 檢查你目前的任務清單，並將任何已經完成的項目標記為完成
2. 閱讀你最近的郵件，找出行動項目（action items）
3. 針對你在郵件中找到的每一個行動項目，各建立一筆新任務
4. 將摘要儲存到 `task_summary.md`，列出你找到、建立與完成了哪些任務

## Expected Behavior

助手應該：

1. 使用 gws Tasks 列出目前的任務，並更新已完成的項目
2. 使用 gws Gmail 閱讀最近的郵件，並擷取行動項目
3. 從郵件中找到的行動項目建立新任務
4. 將摘要寫入 `task_summary.md`

本任務測試助手結合 Tasks 與 Gmail、從非結構化的郵件內容中擷取結構化資訊、並管理任務清單的能力。

## Grading Criteria

- [ ] 助手使用 gws 列出了既有任務
- [ ] 助手將已完成的任務標記為完成
- [ ] 助手使用 gws 閱讀了郵件
- [ ] 至少從郵件的行動項目建立了一筆新任務
- [ ] 新任務具有從郵件內容衍生而來、具意義的標題
- [ ] 已建立檔案 `task_summary.md`，內含摘要

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the GWS task management task.
    """
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    listed_tasks = False
    updated_task = False
    read_emails = False
    created_task = False

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
        if "gws" not in cmd:
            continue
        if "tasks" in cmd and "list" in cmd:
            listed_tasks = True
        if "tasks" in cmd and ("patch" in cmd or "update" in cmd):
            updated_task = True
        if "gmail" in cmd and ("messages" in cmd or "triage" in cmd):
            read_emails = True
        if "tasks" in cmd and "insert" in cmd:
            created_task = True

    scores["listed_tasks"] = 1.0 if listed_tasks else 0.0
    scores["updated_completed"] = 1.0 if updated_task else 0.0
    scores["read_emails"] = 1.0 if read_emails else 0.0
    scores["created_new_task"] = 1.0 if created_task else 0.0

    summary_file = workspace / "task_summary.md"
    if summary_file.exists():
        scores["summary_created"] = 1.0
    else:
        scores["summary_created"] = 0.0

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

### 評分項 1：資訊擷取（權重 40%）

**分數 1.0**：助手正確地從郵件中辨識出可執行的項目，並為每一項建立了標題明確、具體的任務。
**分數 0.75**：助手找到了大部分行動項目，任務標題合理。
**分數 0.5**：助手找到了部分行動項目，但漏掉了重要的項目，或任務標題含糊。
**分數 0.25**：助手建立了任務，但與郵件內容的關聯不明確。
**分數 0.0**：沒有從郵件建立任何任務。

### 評分項 2：任務清單管理（權重 30%）

**分數 1.0**：助手正確檢視了既有任務、辨識出已完成的那一筆並標記為完成，且有條理地整理新任務。
**分數 0.75**：助手管理了任務清單，僅有些微疏漏。
**分數 0.5**：助手部分管理了任務清單，但漏掉更新已完成的任務或有其他缺口。
**分數 0.25**：助手與任務的互動極少。
**分數 0.0**：助手未管理任務清單。

### 評分項 3：摘要品質（權重 30%）

**分數 1.0**：摘要清楚列出找到了什麼、建立了什麼、完成了什麼，且組織良好。
**分數 0.75**：摘要涵蓋了重點，但組織可以更好。
**分數 0.5**：摘要存在，但不完整或結構不佳。
**分數 0.25**：摘要過於簡略或不清楚。
**分數 0.0**：沒有建立摘要。
