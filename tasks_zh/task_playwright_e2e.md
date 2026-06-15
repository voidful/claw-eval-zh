---
id: task_playwright_e2e
name: Playwright E2E 表單測試
category: coding
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
source_task_id: task_playwright_e2e
source_benchmark: pinchbench
claw_eval_id: P031zh_playwright_e2e
workspace_files:
- source: form.html
  dest: form.html
---

# Playwright E2E 表單測試

## Prompt

工作區中有一個檔案 `form.html`，它是一個以純 HTML、CSS 與 JavaScript（無任何
框架）打造、自我完整（self-contained）的三步驟註冊表單。你的任務：

1. 仔細閱讀 `form.html`，以了解表單結構與導覽方式
2. 撰寫一支 Playwright 端對端（end-to-end）測試腳本，儲存為 `test_form.py`
3. 腳本應使用 `playwright.sync_api`（Python 同步 API）
4. 依序走過全部 3 個步驟：
   - 步驟 1：填寫個人資訊（full name、email、phone）
   - 步驟 2：填寫地址細節（street、city、state 下拉選單、ZIP code）
   - 步驟 3：確認 review 摘要顯示正確資料，然後送出
5. 送出後，確認成功面板（success panel）可見，且包含一組 submission ID
6. 在每個步驟，驗證 UI 狀態（正確的步驟可見、進度條已更新）
7. 為選擇器（selector）互動加入重試邏輯——若某個選擇器失敗，最多重試 3 次，
   並在每次之間短暫延遲
8. 將最終成功狀態的螢幕截圖儲存為 `success.png`

該表單會驗證輸入（必填欄位、email 格式、5 位數 ZIP）——請提供能通過驗證的資料。

請盡可能使用 `data-testid` 選擇器——它們是最具韌性的選擇器策略。

## Expected Behavior

助手應該：

1. 閱讀 `form.html` 並分析 DOM 結構，留意 `data-testid` 屬性、表單驗證規則與
   步驟導覽邏輯
2. 使用 `playwright.sync_api` 搭配 `sync_playwright` context manager 建立
   `test_form.py`
3. 啟動 Chromium 瀏覽器（headless 模式）
4. 以 `file://` URL 開啟本機的 `form.html` 檔案
5. 以有效的測試資料填寫步驟 1 的欄位（fullname、email、phone）
6. 點擊「Next」，確認步驟 2 為 active 且步驟 1 已隱藏
7. 以有效資料填寫步驟 2 的欄位（street、city、state 下拉選單、zip）
8. 點擊「Next」，確認步驟 3 顯示 review 摘要
9. 斷言（assert）review 中的值與輸入的內容相符
10. 點擊「Submit Registration」
11. 確認成功面板可見且包含一組 submission ID
12. 擷取螢幕截圖並儲存為 `success.png`
13. 加入重試／等待邏輯，避免不穩定（flaky）的選擇器使測試立即失敗
14. 使用正確的 Playwright 慣用法：`page.locator()`、`data-testid` 選擇器、
    `expect()` 斷言

## Grading Criteria

- [ ] 已在工作區建立檔案 `test_form.py`
- [ ] 檔案包含有效的 Python 語法
- [ ] 腳本從 `playwright.sync_api` 匯入
- [ ] 腳本引用 `form.html` 以開啟表單
- [ ] 腳本跨多個步驟填寫欄位（至少 5 次不同的欄位互動）
- [ ] 腳本包含重試或明確的等待邏輯
- [ ] 腳本包含用於狀態驗證的 assertion／expect 呼叫
- [ ] 腳本將螢幕截圖儲存為 `success.png`

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the Playwright E2E test task based on file creation and code quality.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re
    import ast

    scores = {}
    workspace = Path(workspace_path)

    # Check if test_form.py exists
    script_file = workspace / "test_form.py"

    if not script_file.exists():
        scores["file_created"] = 0.0
        scores["valid_python"] = 0.0
        scores["imports_playwright"] = 0.0
        scores["references_form_html"] = 0.0
        scores["fills_multiple_fields"] = 0.0
        scores["has_retry_or_wait"] = 0.0
        scores["has_assertions"] = 0.0
        scores["saves_screenshot"] = 0.0
        return scores

    scores["file_created"] = 1.0

    # Read file content
    content = script_file.read_text()

    # Check for valid Python syntax
    try:
        ast.parse(content)
        scores["valid_python"] = 1.0
    except SyntaxError:
        scores["valid_python"] = 0.0
        scores["imports_playwright"] = 0.0
        scores["references_form_html"] = 0.0
        scores["fills_multiple_fields"] = 0.0
        scores["has_retry_or_wait"] = 0.0
        scores["has_assertions"] = 0.0
        scores["saves_screenshot"] = 0.0
        return scores

    # Check for Playwright import
    pw_patterns = [
        r'from\s+playwright\.sync_api\s+import',
        r'from\s+playwright\.async_api\s+import',
        r'from\s+playwright\s+import',
        r'import\s+playwright',
    ]
    if any(re.search(p, content) for p in pw_patterns):
        scores["imports_playwright"] = 1.0
    else:
        scores["imports_playwright"] = 0.0

    # Check for form.html reference
    form_patterns = [
        r'form\.html',
        r'form_html',
    ]
    if any(re.search(p, content, re.IGNORECASE) for p in form_patterns):
        scores["references_form_html"] = 1.0
    else:
        scores["references_form_html"] = 0.0

    # Check for multiple field fills using AST to count actual method calls
    # This avoids penalizing DRY code with helper functions
    try:
        tree = ast.parse(content)
        fill_methods = {'fill', 'type', 'select_option', 'check', 'click', 'press'}
        fill_calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Handle method calls (obj.fill(), obj.type(), etc.)
                if isinstance(node.func, ast.Attribute) and node.func.attr in fill_methods:
                    fill_calls.append(node.func.attr)
        
        fill_count = len(fill_calls)
        if fill_count >= 10:
            scores["fills_multiple_fields"] = 1.0
        elif fill_count >= 5:
            scores["fills_multiple_fields"] = 0.75
        elif fill_count >= 3:
            scores["fills_multiple_fields"] = 0.5
        else:
            scores["fills_multiple_fields"] = 0.0
    except Exception:
        # Fall back to regex if AST parsing fails
        fill_patterns = [
            r'\.fill\s*\(',
            r'\.type\s*\(',
            r'\.select_option\s*\(',
            r'\.check\s*\(',
            r'\.click\s*\(',
            r'\.press\s*\(',
        ]
        fill_count = sum(len(re.findall(p, content)) for p in fill_patterns)
        if fill_count >= 10:
            scores["fills_multiple_fields"] = 1.0
        elif fill_count >= 5:
            scores["fills_multiple_fields"] = 0.75
        elif fill_count >= 3:
            scores["fills_multiple_fields"] = 0.5
        else:
            scores["fills_multiple_fields"] = 0.0

    # Check for retry or wait logic
    retry_patterns = [
        r'retry',
        r'attempt',
        r'max_retries',
        r'max_attempts',
        r'tries',
        r'wait_for',
        r'wait_for_selector',
        r'wait_for_timeout',
        r'time\.sleep',
        r'expect\s*\(',
        r'to_be_visible',
        r'to_be_hidden',
    ]
    retry_count = sum(1 for p in retry_patterns if re.search(p, content, re.IGNORECASE))
    if retry_count >= 3:
        scores["has_retry_or_wait"] = 1.0
    elif retry_count >= 1:
        scores["has_retry_or_wait"] = 0.5
    else:
        scores["has_retry_or_wait"] = 0.0

    # Check for assertions
    assert_patterns = [
        r'assert\s+',
        r'expect\s*\(',
        r'to_be_visible',
        r'to_have_text',
        r'to_contain_text',
        r'to_have_value',
        r'is_visible\s*\(',
        r'inner_text\s*\(',
        r'text_content\s*\(',
    ]
    assert_count = sum(1 for p in assert_patterns if re.search(p, content))
    if assert_count >= 4:
        scores["has_assertions"] = 1.0
    elif assert_count >= 2:
        scores["has_assertions"] = 0.75
    elif assert_count >= 1:
        scores["has_assertions"] = 0.5
    else:
        scores["has_assertions"] = 0.0

    # Check for screenshot
    screenshot_patterns = [
        r'screenshot\s*\(',
        r'success\.png',
    ]
    if any(re.search(p, content) for p in screenshot_patterns):
        scores["saves_screenshot"] = 1.0
    else:
        scores["saves_screenshot"] = 0.0

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

### 評分項 1：多步驟導覽（權重 30%）

**1.0 分**：腳本正確地依序走過全部 3 個表單步驟。每次步驟轉換都很明確——填寫
欄位、點擊 Next，並在繼續前確認新步驟為 active。以 `select_option` 處理 state
下拉選單。有測試返回（back）導覽，或至少未使其失效。

**0.75 分**：全部 3 個步驟皆正確導覽，但有些微問題（例如轉換之間沒有明確的等待，
或以 click 而非 select_option 處理 state 下拉選單）。

**0.5 分**：3 個步驟中有 2 個處理正確，或 3 個皆有嘗試但欄位名稱錯誤、或缺少
能通過驗證的資料。

**0.25 分**：僅處理 1 個步驟，或導覽邏輯有根本性瑕疵。

**0.0 分**：未嘗試任何有意義的步驟導覽。

### 評分項 2：Review 資料斷言（權重 25%）

**1.0 分**：腳本驗證步驟 3 的 review 摘要顯示步驟 1 與步驟 2 中輸入的確切資料。
以文字內容斷言檢查至少 3 個 review 欄位（name、email、address）。

**0.75 分**：以正確的斷言驗證 2 個以上的 review 欄位。

**0.5 分**：檢查 review 步驟為可見，但未驗證具體的資料值。

**0.25 分**：review 斷言極少或不正確。

**0.0 分**：未嘗試任何 review 驗證。

### 評分項 3：錯誤處理與重試（權重 25%）

**1.0 分**：實作了具可設定最大嘗試次數（3 次以上）的重試包裝，捕捉特定的
Playwright 例外（TimeoutError 或類似者），在每次重試之間加入延遲，並有適當的
清理（在 finally 區塊中呼叫 browser.close）。

**0.75 分**：具備重試邏輯（2 次以上嘗試）與基本的錯誤捕捉。清理方面有小缺漏。

**0.5 分**：使用 Playwright 內建的等待（wait_for_selector、expect），但沒有自訂
的重試迴圈。

**0.25 分**：錯誤處理極少——只有基本的 try/except，沒有重試。

**0.0 分**：完全沒有錯誤處理。

### 評分項 4：程式碼品質與最佳實務（權重 20%）

**1.0 分**：程式碼整潔、組織良好。一致地使用 `data-testid` 選擇器。為 playwright
使用適當的 context manager。以函式／類別封裝可重複使用的邏輯。變數命名有意義。
註解說明了不顯而易見的選擇。

**0.75 分**：程式碼品質良好，僅有些微風格問題。大致使用 data-testid 選擇器。

**0.5 分**：可運作但組織不佳。混用了良好與脆弱的選擇器。沒有輔助函式。

**0.25 分**：程式碼凌亂、硬編碼數值、整支使用脆弱的 CSS／XPath 選擇器。

**0.0 分**：程式碼無法運作或難以理解。
