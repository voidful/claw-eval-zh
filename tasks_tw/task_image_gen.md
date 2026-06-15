---
id: task_image_gen
name: |
  AI 影像生成
category: skills
grading_type: hybrid
timeout_seconds: 120
language: zh
locale: zh-TW
region: TW
source_task_id: task_image_gen
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T143tw_image_gen
workspace_files: []
---

# AI 影像生成


## Prompt

請生成一張影像：一個友善的機器人坐在溫馨的咖啡店裡讀書。請把它存為目前目錄下的
「robot_cafe.png」。

## Expected Behavior

助手應該：

1. 使用 generate_image 工具（或同等的 AI 影像生成能力）來建立一張符合描述的
   影像
2. 提供一段具描述性的 prompt，捕捉關鍵元素：機器人、咖啡店場景、溫馨氛圍、讀書
3. 把生成的影像存到指定檔名「robot_cafe.png」
4. 確認生成成功，並描述所建立的內容

本任務測試助手以下能力：

- 妥善運用 AI 影像生成工具
- 從自然語言描述構思有效的影像 prompt
- 處理生成內容的檔案輸出操作
- 向使用者清楚傳達結果

## Grading Criteria

- [ ] 助手使用了影像生成工具
- [ ] 生成的 prompt 包含 robot
- [ ] 生成的 prompt 包含 coffee shop 或 cafe 場景
- [ ] 生成的 prompt 包含 reading 或 book
- [ ] 影像檔以正確的檔名儲存
- [ ] 助手確認生成成功

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the AI image generation task.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path

    scores = {
        "used_image_tool": 0.0,
        "prompt_has_robot": 0.0,
        "prompt_has_cafe": 0.0,
        "prompt_has_book": 0.0,
        "file_saved": 0.0,
        "confirmed_generation": 0.0,
    }

    generated_prompt = ""
    used_tool = False

    for event in transcript:
        if event.get("type") != "message":
            continue
        msg = event.get("message", {})

        if msg.get("role") == "assistant":
            for item in msg.get("content", []):
                if item.get("type") == "toolCall":
                    tool_name = item.get("name", "")
                    params = item.get("params", {})

                    # Check for image generation tool
                    if tool_name in ["generate_image", "generateImage", "image_generation"]:
                        used_tool = True
                        generated_prompt = params.get("prompt", "").lower()

                        # Check path parameter for correct filename
                        path = params.get("path", "")
                        if "robot_cafe.png" in path or path.endswith("robot_cafe.png"):
                            scores["file_saved"] = 1.0

                # Check text content for confirmation
                if item.get("type") == "text":
                    text = item.get("text", "").lower()
                    if any(phrase in text for phrase in [
                        "generated",
                        "created the image",
                        "image has been",
                        "successfully created",
                        "saved the image",
                        "here's the image",
                        "image is ready",
                    ]):
                        scores["confirmed_generation"] = 1.0

    scores["used_image_tool"] = 1.0 if used_tool else 0.0

    # Check prompt content
    if generated_prompt:
        if "robot" in generated_prompt:
            scores["prompt_has_robot"] = 1.0

        if any(term in generated_prompt for term in ["coffee", "cafe", "café", "cozy", "shop"]):
            scores["prompt_has_cafe"] = 1.0

        if any(term in generated_prompt for term in ["book", "reading", "read"]):
            scores["prompt_has_book"] = 1.0

    # Also check if file exists in workspace
    workspace = Path(workspace_path)
    if (workspace / "robot_cafe.png").exists():
        scores["file_saved"] = 1.0

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

### 評分項 1：影像品質與相關性（權重 40%）

1.0 分：生成的影像清楚呈現一個機器人在咖啡店場景中讀書。整體場景感覺溫馨，且
所有要求的元素皆齊備並融合良好。

0.75 分：影像含有大部分元素（機器人、咖啡店、書），但有一項元素較不突出，或
溫馨氛圍未完全捕捉。

0.5 分：影像含有機器人與另一項要求的元素，但缺少場景的關鍵面向。

0.25 分：影像僅與需求略有關聯，缺少多項關鍵元素。

0.0 分：未生成影像，或影像與需求完全無關。

### 評分項 2：Prompt 構思（權重 30%）

1.0 分：助手構思了一段有效、詳盡的 prompt，捕捉所有元素：友善的機器人、溫馨的
咖啡店氛圍、讀書。可能包含有助益的藝術細節。

0.75 分：prompt 含所有主要元素，但可以更具描述性或更詳盡。

0.5 分：prompt 捕捉了部分元素，但漏掉需求中的重要細節。

0.25 分：prompt 過於含糊，或漏掉多項關鍵元素。

0.0 分：未提供 prompt，或 prompt 完全離題。

### 評分項 3：任務執行（權重 30%）

1.0 分：助手正確使用影像生成工具、存為正確的檔名，並清楚傳達結果。

0.75 分：助手完成任務，僅有小瑕疵（例如檔名略有不同、確認訊息極少）。

0.5 分：助手生成了影像，但在儲存或確認結果上有問題。

0.25 分：助手有嘗試，但未能妥善完成任務。

0.0 分：助手未嘗試生成影像，或完全失敗。
