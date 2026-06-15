---
id: task_clawdhub
name: 建立專案結構
category: skills
grading_type: automated
timeout_seconds: 120
language: zh
locale: zh-TW
source_task_id: task_clawdhub
source_benchmark: pinchbench
claw_eval_id: P141zh_clawdhub
workspace_files: []
---

# 建立專案結構

## Prompt

請為一個名為「datautils」的函式庫建立一個基本的 Python 專案結構。此專案應包含：

1. 一個 `src/datautils/` 套件目錄，內含 `__init__.py` 檔案
2. 一個 `tests/` 目錄，內含 `test_datautils.py` 檔案
3. 一個 `pyproject.toml` 檔案，含基本專案中繼資料（name、version 0.1.0、
   description）
4. 一個 `README.md` 檔案，含標題與簡短說明

請在目前的工作區中建立此專案結構。

## Expected Behavior

助手應該：

1. 建立目錄結構：`src/datautils/`、`tests/`
2. 建立 `src/datautils/__init__.py`，含基本內容
3. 建立 `tests/test_datautils.py`，含一個佔位用的測試
4. 建立 `pyproject.toml`，含妥善的 Python 專案中繼資料
5. 建立 `README.md`，含專案說明文件

這項任務測試助手建立檔案結構，以及理解 Python 專案慣例的能力。

## Grading Criteria

- [ ] 助手已建立 `src/datautils/` 目錄結構
- [ ] 助手已在套件中建立 `__init__.py`
- [ ] 助手已建立含測試檔案的 `tests/` 目錄
- [ ] 助手已建立含正確中繼資料的 `pyproject.toml`
- [ ] 助手已建立 `README.md`
- [ ] 助手已確認建立成功

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the project structure creation task.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    # Check directory structure
    src_datautils = workspace / "src" / "datautils"
    tests_dir = workspace / "tests"

    scores["src_directory_created"] = 1.0 if src_datautils.exists() else 0.0
    scores["tests_directory_created"] = 1.0 if tests_dir.exists() else 0.0

    # Check required files
    init_file = src_datautils / "__init__.py"
    test_file = tests_dir / "test_datautils.py"
    pyproject = workspace / "pyproject.toml"
    readme = workspace / "README.md"

    scores["init_file_created"] = 1.0 if init_file.exists() else 0.0
    scores["test_file_created"] = 1.0 if test_file.exists() else 0.0
    scores["pyproject_created"] = 1.0 if pyproject.exists() else 0.0
    scores["readme_created"] = 1.0 if readme.exists() else 0.0

    # Check pyproject.toml content
    if pyproject.exists():
        content = pyproject.read_text().lower()
        has_name = "datautils" in content
        has_version = "0.1.0" in content or "version" in content
        scores["pyproject_has_metadata"] = 1.0 if (has_name and has_version) else 0.5 if has_name else 0.0
    else:
        scores["pyproject_has_metadata"] = 0.0

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
