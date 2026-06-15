---
id: task_sanity
name: 健全性檢查
category: productivity
grading_type: automated
timeout_seconds: 60
language: zh
locale: zh-TW
region: TW
source_task_id: task_sanity
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: language_polish
claw_eval_tw_id: T001tw_sanity
workspace_files: []
---

# 健全性檢查

## Prompt

請回覆「你好，我已準備好了！」以確認你可以正常回應。

## Expected Behavior

助手應該：
1. 回覆一句問候或確認訊息
2. 證明自己能夠處理並回應簡單指令

這是一個基礎的健全性檢查，用來確認評測系統運作正常。評分只看「是否有任何
助手回應」，不檢查精確字串。

## Grading Criteria

- [ ] 助手成功回應（任何回應都算）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the sanity check task - just verify the agent responded.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    scores = {}
    
    # Check if there's any assistant response in the transcript
    has_response = False
    for entry in transcript:
        if entry.get("type") == "message":
            message = entry.get("message", {})
            if message.get("role") == "assistant":
                # Check if assistant has any content
                content = message.get("content", [])
                if content and len(content) > 0:
                    has_response = True
                    break
    
    scores["agent_responded"] = 1.0 if has_response else 0.0
    
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
