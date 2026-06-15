---
id: task_workflow
name: 多步驟 API 工作流程
category: skills
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
source_task_id: task_workflow
source_benchmark: pinchbench
claw_eval_id: P140zh_workflow
workspace_files:
- path: config.json
  content: |-
    {
      "api": {
        "endpoint": "https://api.example.com/v2/data",
        "method": "GET",
        "headers": {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        "timeout": 30
      },
      "project": {
        "name": "DataFetcher",
        "version": "1.0.0",
        "description": "Automated data fetching utility"
      }
    }
---

# 多步驟 API 工作流程

## Prompt

請讀取 config.json、擷取其中的 API 端點、建立一個 Python 腳本來呼叫它，並在
NOTES.md 中記錄這整個過程。

## Expected Behavior

助手應該：

1. 從工作區讀取 `config.json` 檔案
2. 解析 JSON 並擷取 API 端點 URL
3. 建立一個 Python 腳本，能夠：
   - 讀取設定檔
   - 對該端點發出 HTTP 請求
   - 妥善處理錯誤
   - 印出或回傳回應
4. 建立一個 `NOTES.md` 檔案，記錄：
   - 做了哪些事
   - 腳本如何運作
   - 如何使用
   - 任何關於設定的重要細節

這項任務測試多步驟協調、檔案讀取、程式碼產製與文件撰寫的能力。

## Grading Criteria

- [ ] 成功讀取檔案 `config.json`
- [ ] 已建立 Python 腳本檔案（任何 .py 檔名）
- [ ] 腳本含有效的 Python 語法
- [ ] 腳本會讀取／解析 JSON
- [ ] 腳本含 HTTP 請求程式碼
- [ ] 已建立檔案 `NOTES.md`
- [ ] 腳本品質與完整性（LLM 評審）
- [ ] 文件清晰度與實用性（LLM 評審）
- [ ] 過程說明品質（LLM 評審）
- [ ] 整體任務完成度（LLM 評審）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the automated portion of the workflow task (50% of total).

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re
    import ast
    import json

    scores = {}
    workspace = Path(workspace_path)

    # Check if agent read config.json (from transcript)
    read_config = False
    for event in transcript:
        if event.get("type") != "message":
            continue
        msg = event.get("message", {})
        if msg.get("role") == "assistant":
            for item in msg.get("content", []):
                if item.get("type") == "toolCall":
                    tool_name = item.get("name", "")
                    # Support both "params" (Cursor/Windsurf) and "arguments" (OpenClaw/Claude Code)
                    params = item.get("params", item.get("arguments", {}))
                    if tool_name.lower() in ["read_file", "readfile", "read"]:
                        # Support multiple param formats across different agents:
                        # - files: ["config.json"] (Cursor, Windsurf)
                        # - path/file_path/file: "config.json" (OpenClaw, Claude Code)
                        files = params.get("files", [])
                        path_candidates = [
                            params.get("path", ""),
                            params.get("file_path", ""),
                            params.get("file", ""),
                        ]
                        if any("config.json" in str(f) for f in files) or any(
                            "config.json" in str(path) for path in path_candidates if path
                        ):
                            read_config = True
                            break

    scores["read_config"] = 1.0 if read_config else 0.0

    # Find Python script file
    py_files = list(workspace.glob("*.py"))

    if not py_files:
        scores["script_created"] = 0.0
        scores["valid_syntax"] = 0.0
        scores["parses_json"] = 0.0
        scores["has_http_request"] = 0.0
    else:
        scores["script_created"] = 1.0

        # Read the first Python file found
        script_content = py_files[0].read_text()

        # Check for valid Python syntax
        try:
            ast.parse(script_content)
            scores["valid_syntax"] = 1.0
        except SyntaxError:
            scores["valid_syntax"] = 0.0
            scores["parses_json"] = 0.0
            scores["has_http_request"] = 0.0
            scores["notes_created"] = 0.0
            return scores

        # Check for JSON parsing
        json_patterns = [
            r'import\s+json',
            r'from\s+json\s+import',
            r'json\.load',
            r'json\.loads',
        ]
        if any(re.search(pattern, script_content) for pattern in json_patterns):
            scores["parses_json"] = 1.0
        else:
            scores["parses_json"] = 0.0

        # Check for HTTP request
        http_patterns = [
            r'import\s+requests',
            r'from\s+requests\s+import',
            r'import\s+urllib',
            r'from\s+urllib',
            r'requests\.get',
            r'requests\.post',
            r'urllib\.request',
            r'urlopen',
        ]
        if any(re.search(pattern, script_content, re.IGNORECASE) for pattern in http_patterns):
            scores["has_http_request"] = 1.0
        else:
            scores["has_http_request"] = 0.0

    # Check if NOTES.md exists
    notes_file = workspace / "NOTES.md"
    if notes_file.exists():
        scores["notes_created"] = 1.0
    else:
        scores["notes_created"] = 0.0

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

### 評分項 1：腳本品質與功能（權重 30%）

**1.0 分**：Python 腳本結構良好，能正確讀取 config.json、擷取端點、發出 HTTP 請求
並妥善處理錯誤，且含有實用的註解。程式碼遵循最佳實務。

**0.75 分**：腳本可運作，僅有小瑕疵。能讀取設定並發出請求，但可能缺乏完整的錯誤
處理，或有小幅程式碼品質問題。

**0.5 分**：腳本具備基本功能，但有明顯問題。可能有不完整的錯誤處理、結構不佳，或
缺少重要功能。

**0.25 分**：腳本撰寫不佳或勉強可運作。在邏輯、結構或錯誤處理上有重大問題。

**0.0 分**：腳本無法運作、缺漏，或完全未達需求。

### 評分項 2：文件品質（權重 30%）

**1.0 分**：NOTES.md 完整、組織良好，清楚說明做了哪些事、腳本如何運作，以及如何
使用。包含關於設定結構的相關細節，以及所做的任何假設。

**0.75 分**：文件良好，涵蓋大部分重點。在說明或組織上有小幅缺漏。

**0.5 分**：有基本文件，但缺乏細節或清晰度。漏掉關於使用方式或實作的重要資訊。

**0.25 分**：文件不佳。資訊極少或說明不清。

**0.0 分**：文件缺漏或完全不足。

### 評分項 3：流程理解（權重 25%）

**1.0 分**：明顯看出助手理解了這個多步驟工作流程。正確地從設定中擷取端點、建立
適當的腳本，並合乎邏輯地記錄過程。展現良好的決策。

**0.75 分**：理解良好，僅有小瑕疵。流程大致正確，僅在邏輯或執行上有小幅缺漏。

**0.5 分**：部分理解。助手完成了部分步驟，但漏掉了各步驟間的連結，或做出可議的
決策。

**0.25 分**：理解不佳。助手在這個工作流程上有困難，或在流程上犯了重大錯誤。

**0.0 分**：看不出對任務需求有任何理解。

### 評分項 4：整體完整性（權重 15%）

**1.0 分**：所有需求皆達成。讀取設定、擷取端點、建立可運作的腳本、提供完整文件。
任務完全完成。

**0.75 分**：達成大部分需求，僅有小幅遺漏。任務大致完成。

**0.5 分**：達成部分需求，但有重大缺漏。任務部分完成。

**0.25 分**：達成極少需求。任務僅勉強嘗試。

**0.0 分**：任務未完成或完全失敗。
