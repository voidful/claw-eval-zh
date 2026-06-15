---
id: task_test_generation
name: 測試產生
category: coding
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_test_generation
source_benchmark: pinchbench
claw_eval_id: P034zh_test_generation
workspace_files:
- source: order_processor.py
  dest: order_processor.py
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 測試產生

## Prompt

工作區中的 `order_processor.py` 包含一個用於電子商務訂單流程的 `OrderProcessor`
類別。請為這個模組撰寫一套完整的測試，並將它儲存為工作區中的
`test_order_processor.py`。

需求：

1. 使用 `pytest` 作為測試框架
2. 測試 `OrderProcessor` 的每一個 public 方法
3. 包含針對邊界情況的測試：空訂單、數量為零的品項、未知的地區、優惠券疊加
   （coupon stacking）行為、缺貨品項
4. 測試在輸入無效時會拋出 `InvalidOrderError`
5. 使用 fixture 或 factory helper，以避免重複的測試設定
6. 力求高分支覆蓋率——測試每個條件判斷的兩側

請勿修改 `order_processor.py`。

## Expected Behavior

助手應該：

1. 閱讀 `order_processor.py`，了解所有 public 方法、類別常數與例外型別
2. 以 pytest 風格的測試建立 `test_order_processor.py`
3. 涵蓋全部 7 個 public 方法：`validate_order`、`calculate_subtotal`、
   `apply_discount`、`calculate_tax`、`check_stock`、`estimate_delivery`、
   `process_order`
4. 為每個方法測試正常路徑（happy path）與錯誤路徑（error path）
5. 使用 `pytest.raises` 進行例外測試
6. 使用 fixture 或輔助函式來消除重複的測試資料
7. 撰寫實際針對原始模組執行時能通過的測試

## Grading Criteria

- [ ] 已在工作區建立檔案 `test_order_processor.py`
- [ ] 檔案包含有效的 Python 語法
- [ ] 檔案匯入 pytest
- [ ] 檔案從 order_processor 模組匯入
- [ ] 測試涵蓋 validate_order（包含例外情況）
- [ ] 測試涵蓋 calculate_subtotal
- [ ] 測試涵蓋 apply_discount（級距與優惠券）
- [ ] 測試涵蓋 calculate_tax
- [ ] 測試涵蓋 check_stock
- [ ] 測試涵蓋 estimate_delivery
- [ ] 測試涵蓋 process_order（整合測試）
- [ ] 測試實際執行時能通過

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    import ast
    import subprocess
    import sys

    scores = {
        "file_created": 0.0,
        "valid_python": 0.0,
        "imports_pytest": 0.0,
        "imports_module": 0.0,
        "tests_validate_order": 0.0,
        "tests_calculate_subtotal": 0.0,
        "tests_apply_discount": 0.0,
        "tests_calculate_tax": 0.0,
        "tests_check_stock": 0.0,
        "tests_estimate_delivery": 0.0,
        "tests_process_order": 0.0,
        "tests_pass": 0.0,
    }

    workspace = Path(workspace_path)
    test_file = workspace / "test_order_processor.py"
    source_file = workspace / "order_processor.py"

    if not test_file.exists():
        return scores
    scores["file_created"] = 1.0

    content = test_file.read_text(encoding="utf-8")

    try:
        ast.parse(content)
        scores["valid_python"] = 1.0
    except SyntaxError:
        return scores

    # Check imports
    if re.search(r"import\s+pytest|from\s+pytest\s+import", content):
        scores["imports_pytest"] = 1.0

    if re.search(r"from\s+order_processor\s+import|import\s+order_processor", content):
        scores["imports_module"] = 1.0

    # Check coverage of each method by looking for method name references in test functions
    method_checks = {
        "tests_validate_order": [r"validate_order", r"InvalidOrderError"],
        "tests_calculate_subtotal": [r"calculate_subtotal"],
        "tests_apply_discount": [r"apply_discount"],
        "tests_calculate_tax": [r"calculate_tax"],
        "tests_check_stock": [r"check_stock"],
        "tests_estimate_delivery": [r"estimate_delivery"],
        "tests_process_order": [r"process_order"],
    }

    for score_key, patterns in method_checks.items():
        if any(re.search(p, content) for p in patterns):
            scores[score_key] = 1.0

    # Try to actually run the tests
    if source_file.exists():
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short", "-q"],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=30,
            )
            # Parse pytest output for pass/fail counts
            output = result.stdout + result.stderr
            passed_match = re.search(r"(\d+)\s+passed", output)
            failed_match = re.search(r"(\d+)\s+failed", output)

            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            total = passed + failed

            if total > 0:
                pass_rate = passed / total
                if pass_rate == 1.0:
                    scores["tests_pass"] = 1.0
                elif pass_rate >= 0.8:
                    scores["tests_pass"] = 0.75
                elif pass_rate >= 0.5:
                    scores["tests_pass"] = 0.5
                else:
                    scores["tests_pass"] = 0.25
        except (subprocess.TimeoutExpired, Exception):
            scores["tests_pass"] = 0.0

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

### 評分項 1：邊界情況覆蓋（權重 35%）

**1.0 分**：測試涵蓋所有重要的邊界情況：空的 items 清單、數量為零、負價格、
未知地區（0% 稅）、所有 discount 級距與邊界、優惠券代碼（SAVE20、WELCOME10、
無效／None）、優惠券與級距不可疊加、空的倉庫庫存、部分庫存、priority 對 standard
配送、加拿大對美國地區。

**0.75 分**：涵蓋大多數邊界情況（上述 8 項以上）。邊界測試有些微缺漏。

**0.5 分**：涵蓋數個邊界情況，但遺漏了重要情境，如 discount 級距邊界或優惠券
疊加行為。

**0.25 分**：僅有基本的正常路徑測試，加上 1～2 個邊界情況。

**0.0 分**：沒有任何有意義的邊界情況測試。

### 評分項 2：測試組織與可讀性（權重 25%）

**1.0 分**：測試以邏輯方式分組（依方法或功能）。測試名稱清楚、具描述性，且遵循
一致的慣例（例如 `test_<method>_<scenario>`）。測試類別或模組層級的組織整潔。
容易理解每個測試在驗證什麼。

**0.75 分**：組織良好，僅在命名或分組上有些微不一致。

**0.5 分**：測試可運作但組織不佳——全部攤平成一份清單，名稱不清楚。

**0.25 分**：雜亂無章、難以理解、結構不一致。

**0.0 分**：沒有任何有意義的組織。

### 評分項 3：fixture 與輔助函式的運用（權重 20%）

**1.0 分**：使用 `@pytest.fixture` 進行共用的測試設定（例如範例訂單、預先載入
庫存的 processor 實例）。以輔助函式或 parametrize 裝飾器減少重複。沒有複製貼上的
測試資料區塊。

**0.75 分**：有使用部分 fixture，但偶有重複。

**0.5 分**：fixture 使用極少——多數測試以行內方式建構資料，但無過度重複。

**0.25 分**：測試之間大量重複，沒有 fixture 或輔助函式。

**0.0 分**：每個測試都完全自我包含，且設定重複。

### 評分項 4：斷言品質（權重 20%）

**1.0 分**：斷言具體且有意義——檢查確切的值、對浮點數使用 `pytest.approx`、驗證
字典的鍵與值、對例外使用帶 match 樣式的 `pytest.raises`。在適當情況下，每個測試
有多個斷言以驗證完整行為。

**0.75 分**：斷言良好，僅有些微缺漏（例如缺少浮點數容差、raises 沒有 match 樣式）。

**0.5 分**：基本斷言能確認行為，但缺乏精確度（例如只檢查真假值，而非具體的值）。

**0.25 分**：斷言薄弱——多半在檢查型別或是否存在，而非值。

**0.0 分**：沒有有意義的斷言，或只有瑣碎的 `assert True` 檢查。
