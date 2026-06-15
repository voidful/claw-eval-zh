---
id: task_iterative_code_refine
name: 迭代式程式碼改進
category: coding
grading_type: automated
timeout_seconds: 300
language: zh
locale: zh-TW
source_task_id: task_iterative_code_refine
source_benchmark: pinchbench
claw_eval_id: P040zh_iterative_code_refine
workspace_files: []
multi_session: true
sessions:
- id: initial_implementation
  prompt: |
    請建立一個名為 calculator.py 的 Python 腳本，實作一個簡單計算機，包含以下函式：
    1. add(a, b) —— 回傳 a + b
    2. subtract(a, b) —— 回傳 a - b
    3. multiply(a, b) —— 回傳 a * b
    4. divide(a, b) —— 回傳 a / b（暫時不做錯誤處理）

    請把檔案儲存為工作區裡的 calculator.py。
- id: add_error_handling
  prompt: |
    我發現 divide 函式沒有處理除以 0 的情況。請更新 calculator.py：
    1. 讓 divide(a, b) 在 b 為 0 時拋出 ValueError，訊息為 "Cannot divide by zero"
    2. 新增 power(a, b) 函式，回傳 a ** b
    3. 新增 modulo(a, b) 函式，回傳 a % b（同樣處理除以 0 的情況）

    請保留所有既有函式，只新增上述改進。
- id: final_review
  new_session: true
  prompt: |
    請讀取工作區裡的 calculator.py，確認它具備下列特性：
    1. 函式：add、subtract、multiply、divide、power、modulo
    2. divide 與 modulo 都在除以 0 時拋出 ValueError
    3. 所有函式都能正確運作

    然後把驗證結果寫入 review.txt，說明有哪些函式、以及是否具備錯誤處理。
---

# 迭代式程式碼改進

## Prompt

本任務為多輪任務，請見 frontmatter 的 `sessions` 欄位。

## Expected Behavior

這是一個多輪任務（見 frontmatter 的 sessions）。助手應該：
1. 第 1 輪：建立 calculator.py，含 add、subtract、multiply、divide 函式
   （divide 先不做錯誤處理）
2. 第 2 輪：修改 calculator.py，讓 divide 在除以 0 時拋出 ValueError
   ("Cannot divide by zero")，新增 power 與 modulo（modulo 也處理除以 0），
   並保留既有函式
3. 第 3 輪（全新 session）：讀取 calculator.py，驗證 6 個函式與錯誤處理是否
   齊全，並把驗證結果寫入 review.txt

注意：calculator.py、review.txt、以及所有函式名與 "Cannot divide by zero"
字串都不可更改。

## Grading Criteria

- [ ] calculator.py 存在且含 add、subtract、multiply 函式
- [ ] calculator.py 的 divide 在除以 0 時拋出 ValueError
- [ ] calculator.py 含 power 函式
- [ ] calculator.py 的 modulo 在除以 0 時拋出 ValueError
- [ ] review.txt 存在且提及全部 6 個函式
- [ ] review.txt 提及錯誤處理 / ValueError

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the iterative code refinement task.

    Checks calculator.py for required functions and error handling,
    and review.txt for verification content.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    # --- Check calculator.py ---
    calc_file = workspace / "calculator.py"
    calc_content = ""
    if calc_file.exists():
        calc_content = calc_file.read_text()

    # Basic functions
    has_add = bool(re.search(r'def\s+add\s*\(', calc_content))
    has_subtract = bool(re.search(r'def\s+subtract\s*\(', calc_content))
    has_multiply = bool(re.search(r'def\s+multiply\s*\(', calc_content))
    has_basic = sum([has_add, has_subtract, has_multiply])
    scores["basic_functions"] = has_basic / 3.0

    # Divide with error handling
    has_divide = bool(re.search(r'def\s+divide\s*\(', calc_content))
    has_divide_error = has_divide and bool(re.search(r'ValueError.*divide.*zero|Cannot divide by zero', calc_content, re.IGNORECASE))
    scores["divide_error_handling"] = 1.0 if has_divide_error else (0.5 if has_divide else 0.0)

    # Power function
    has_power = bool(re.search(r'def\s+power\s*\(', calc_content))
    scores["power_function"] = 1.0 if has_power else 0.0

    # Modulo with error handling
    has_modulo = bool(re.search(r'def\s+modulo\s*\(', calc_content))
    has_modulo_error = has_modulo and bool(re.search(r'ValueError.*zero|Cannot divide by zero', calc_content, re.IGNORECASE))
    scores["modulo_error_handling"] = 1.0 if has_modulo_error else (0.5 if has_modulo else 0.0)

    # --- Check review.txt ---
    review_file = workspace / "review.txt"
    review_content = ""
    if review_file.exists():
        review_content = review_file.read_text().lower()

    # Review mentions all functions
    review_mentions = sum([
        "add" in review_content,
        "subtract" in review_content,
        "multiply" in review_content,
        "divide" in review_content,
        "power" in review_content,
        "modulo" in review_content,
    ])
    scores["review_functions"] = review_mentions / 6.0

    # Review mentions error handling
    review_mentions_errors = bool(re.search(r'error|valueerror|zero|handling', review_content, re.IGNORECASE))
    scores["review_error_handling"] = 1.0 if review_mentions_errors else 0.0

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
