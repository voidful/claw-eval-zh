---
id: task_skill_search
name: 設定檔內搜尋與取代（台灣團隊）
category: skills
grading_type: automated
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_skill_search
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: manual_review_only
claw_eval_tw_id: T142tw_skill_search
workspace_files:
- path: config/settings.json
  content: |
    {
      "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp_dev",
        "user": "devuser",
        "password": "dev_password_123"
      },
      "api": {
        "endpoint": "http://localhost:3000",
        "timeout": 30
      },
      "logging": {
        "level": "debug",
        "file": "/var/log/myapp/dev.log"
      }
    }
- path: config/database.yml
  content: |-
    development:
      adapter: postgresql
      host: localhost
      port: 5432
      database: myapp_dev
      username: devuser
      password: dev_password_123

    test:
      adapter: postgresql
      host: localhost
      port: 5432
      database: myapp_test
      username: devuser
      password: dev_password_123
---

# 設定檔內搜尋與取代（台灣團隊）

## Prompt

我們的台灣開發團隊需要為正式環境部署更新設定檔。請對 `config/` 目錄中的所有
設定檔做以下變更：

1. 將所有 `localhost` 改為 `prod-db.example.com`
2. 將資料庫名稱由 `myapp_dev` 改為 `myapp_prod`（並將 `myapp_test` 改為
   `myapp_prod`）
3. 將 log level 由 `debug` 改為 `warn`（在 settings.json 中）
4. 將 API 端點由 `http://localhost:3000` 更新為 `https://api.example.com`

請列出你對每個檔案所做的變更。

注意：請在變更摘要中**明確標示你檢視與修改了哪些檔案、標示你進行變更的日期**，
並說明任何**限制與不確定性**（例如某些值出現在多個檔案、是否有未涵蓋到的設定）。
切勿捏造未實際做出的變更，也不要更改檔名或 config 鍵名。

## Expected Behavior

助手應該：

1. 讀取 `config/` 目錄中的設定檔
2. 找出所有需要變更之處
3. 在每個檔案中進行適當的取代
4. 摘要所做的變更

這項任務測試助手以下能力：

- 讀取並理解設定檔格式（JSON、YAML）
- 執行有針對性的搜尋與取代操作
- 跨多個檔案作業
- 清楚地傳達變更內容

在摘要變更時，正確行為是**明確標示所檢視與修改的檔案、標示變更日期，並說明
任何限制與不確定性**（如重複值、未涵蓋的設定），而非聲稱做了未實際完成的變更。
檔名與 config 鍵名不可更改。

## Grading Criteria

- [ ] 助手讀取設定檔
- [ ] 助手將 localhost 取代為 prod-db.example.com
- [ ] 助手適當地更新資料庫名稱
- [ ] 助手將 log level 改為 warn
- [ ] 助手將 API 端點更新為 https
- [ ] 助手摘要所做的變更，並標示所修改的檔案、變更日期與任何限制／不確定性

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the search and replace task.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import json

    scores = {}
    workspace = Path(workspace_path)

    # Check settings.json
    settings_file = workspace / "config" / "settings.json"
    if settings_file.exists():
        content = settings_file.read_text()
        scores["settings_host_updated"] = 1.0 if "prod-db.example.com" in content and "localhost" not in content.replace("api.example.com", "") else 0.0
        scores["settings_db_updated"] = 1.0 if "myapp_prod" in content and "myapp_dev" not in content else 0.0
        scores["settings_loglevel_updated"] = 1.0 if '"warn"' in content.lower() and '"debug"' not in content.lower() else 0.0
        scores["settings_api_updated"] = 1.0 if "https://api.example.com" in content else 0.0
    else:
        scores["settings_host_updated"] = 0.0
        scores["settings_db_updated"] = 0.0
        scores["settings_loglevel_updated"] = 0.0
        scores["settings_api_updated"] = 0.0

    # Check database.yml
    db_file = workspace / "config" / "database.yml"
    if db_file.exists():
        content = db_file.read_text()
        scores["yaml_host_updated"] = 1.0 if "prod-db.example.com" in content and "localhost" not in content else 0.0
        scores["yaml_db_updated"] = 1.0 if "myapp_prod" in content and "myapp_dev" not in content and "myapp_test" not in content else 0.0
    else:
        scores["yaml_host_updated"] = 0.0
        scores["yaml_db_updated"] = 0.0

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
