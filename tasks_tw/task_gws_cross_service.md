---
id: task_gws_cross_service
name: |
  GWS 跨服務工作流程
category: integrations
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
region: TW
source_task_id: task_gws_cross_service
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T146tw_gws_cross_service
workspace_files: []
grading_weights:
  automated: 0.6
  llm_judge: 0.4
prerequisites:
- npm:@juppytt/fws
- cli:gws
---

# GWS 跨服務工作流程


## Prompt

你可以透過 `gws` CLI 工具操作一個 Google Workspace 帳號（用 `gws --help` 查看用法）。

你收到一封來自 alice@example.com.tw、關於「Q3 Planning Meeting」的郵件。請完成以下事項：

1. 找到並閱讀那封郵件，取得會議細節
2. 根據你在郵件中找到的內容，建立一筆行事曆事件
3. 在 Drive 中找到「Q3 Planning Agenda」文件，並分享給 bob@example.com.tw（reader 讀取權限）
4. 把你所做的事情寫成摘要，儲存到 `actions.md`

## Expected Behavior

助手應該：

1. 搜尋或列出 Gmail 郵件，找到 Alice 寄來的 Q3 Planning 郵件
2. 閱讀郵件內容以取得會議細節
3. 使用 gws Calendar 建立一筆事件，包含正確的摘要（summary）、時間與與會者
4. 使用 gws Drive 找到該議程文件，並為 bob@example.com.tw 新增一項權限
5. 把已完成的動作寫成摘要，存到 actions.md

本任務測試助手在單一工作流程中協調 Gmail、Calendar 與 Drive 的能力。

## Grading Criteria

- [ ] 助手找到並閱讀了 Q3 Planning 郵件
- [ ] 已建立行事曆事件，且摘要相關
- [ ] 行事曆事件具有開始時間
- [ ] 在 Drive 中找到「Q3 Planning Agenda」文件
- [ ] 已在該文件上為 bob@example.com.tw 建立權限
- [ ] 已建立檔案 actions.md，內含所採取動作的摘要

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the GWS cross-service workflow task.
    """
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    read_email = False
    created_event = False
    found_file = False
    shared_file = False

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
        if "messages get" in cmd or "messages list" in cmd or "+triage" in cmd:
            read_email = True
        if "events insert" in cmd or "events create" in cmd:
            created_event = True
        if "files list" in cmd or "files get" in cmd:
            found_file = True
        if "permissions create" in cmd:
            shared_file = True

    scores["read_email"] = 1.0 if read_email else 0.0
    scores["created_event"] = 1.0 if created_event else 0.0
    scores["found_drive_file"] = 1.0 if found_file else 0.0
    scores["shared_file"] = 1.0 if shared_file else 0.0

    actions_file = workspace / "actions.md"
    if actions_file.exists():
        scores["actions_summary"] = 1.0
    else:
        scores["actions_summary"] = 0.0

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

### 評分項 1：跨服務協調（權重 50%）

分數 1.0：助手在 Gmail、Calendar 與 Drive 之間流暢地操作，從一個服務擷取資訊並用於另一個服務。整個工作流程合乎邏輯且有效率。
分數 0.75：助手使用了全部三項服務，但有些許效率不佳或服務之間的銜接有缺漏。
分數 0.5：助手正確使用了三項服務中的兩項，但未能在它們之間串接資料。
分數 0.25：助手嘗試使用這些服務，但大多數操作都不順利。
分數 0.0：助手未能跨多項服務使用 gws。

### 評分項 2：任務完整度（權重 50%）

分數 1.0：四個步驟全部正確完成：閱讀郵件、以正確細節建立事件、把文件分享給 bob、寫出摘要。
分數 0.75：四個步驟中正確完成三個。
分數 0.5：四個步驟中正確完成兩個。
分數 0.25：正確完成一個步驟。
分數 0.0：沒有完成任何步驟。
