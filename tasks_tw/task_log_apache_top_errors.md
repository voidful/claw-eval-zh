---
id: task_log_apache_top_errors
name: Apache 錯誤日誌 — 排序最常見的錯誤類型
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_apache_top_errors
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T080tw_log_apache_top_errors
workspace_files:
- dest: apache_error.log
  source: logs/apache_error.log
---

# Apache 錯誤日誌 — 排序最常見的錯誤類型

## Prompt

請分析位於 `apache_error.log` 的 Apache 錯誤日誌，並將所有 `[error]` 等級的條目依錯誤類型分類。請忽略 `[notice]` 等級的條目。

請產生一份由最常見到最不常見的錯誤類型排名清單。對於每一種錯誤類型，請提供：

1. 該錯誤類別的描述性名稱
2. 出現次數的精確計數
3. 一則範例日誌行
4. 簡短說明此錯誤的成因，以及它是否代表資安疑慮

請把你的發現寫到 `error_types_report.json`，以如下結構的 JSON 物件呈現：

```json
{
  "total_errors": 753,
  "error_types": [
    {
      "rank": 1,
      "category": "Descriptive name",
      "count": 224,
      "example": "One example log line",
      "explanation": "What causes this and security implications"
    }
  ]
}
```

請聚焦於面向用戶端的錯誤（即帶有 `[client ...]` 者），但同時也納入伺服器內部錯誤（例如 `mod_jk` 初始化失敗與 `env.createBean2()` 工廠錯誤）。

## Expected Behavior

助手應解析所有 `[error]` 等級的行，並依錯誤訊息樣式分組。預期的主要錯誤類別為：

| 排名 | 錯誤類型 | 計數 |
|---|---|---|
| 1 | Directory index forbidden by rule | ~224 |
| 2 | File does not exist（各種路徑） | ~200+ |
| 3 | script not found or unable to stat | ~66+ |
| 4 | mod_jk child init failures | ~48 |
| 5 | jk2_init() Can't find child in scoreboard | ~30+ |
| 6 | env.createBean2() Factory errors | ~12 |
| 7 | config.update() errors | ~12 |
| 8 | Invalid method in request | ~17 |
| 9 | request failed: URI too long | ~3 |

`[error]` 行的總數為 753。助手對子類別的分組方式可以不同（例如把所有「File does not exist」變體合併，或依路徑分開）。兩種做法皆可接受。

可接受的變化：
- 視分組策略而定，計數可能有 ±10 的差異
- 類別命名可有所不同
- 將「File does not exist」條目再細分子組可接受

## Grading Criteria

- [ ] 已在工作區建立 `error_types_report.json`
- [ ] 已將「Directory index forbidden」判定為最常見的用戶端錯誤（~224）
- [ ] 已找出並計數「File does not exist」錯誤
- [ ] 已將「Invalid method in request」判定為一個獨立的錯誤類型
- [ ] 分析中納入了伺服器內部錯誤（mod_jk、env.createBean2）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Apache error log top errors ranking task."""
    from pathlib import Path
    import json

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "error_types_report.json"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "directory_forbidden_top": 0.0,
            "file_not_exist_counted": 0.0,
            "invalid_method_identified": 0.0,
            "internal_errors_included": 0.0,
        }

    scores["output_created"] = 1.0

    try:
        data = json.loads(report_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return {
            "output_created": 1.0,
            "directory_forbidden_top": 0.0,
            "file_not_exist_counted": 0.0,
            "invalid_method_identified": 0.0,
            "internal_errors_included": 0.0,
        }

    # Flatten all text for scanning
    full_text = json.dumps(data).lower()

    # Check 1: Directory index forbidden identified as top/most frequent
    error_types = data.get("error_types", [])
    top_entry = error_types[0] if error_types else {}
    top_category = str(top_entry.get("category", "")).lower()
    top_count = top_entry.get("count", 0)
    scores["directory_forbidden_top"] = (
        1.0 if ("directory" in top_category or "forbidden" in top_category or "index" in top_category)
              and 200 <= top_count <= 250
        else 0.5 if "directory" in full_text and "forbidden" in full_text
        else 0.0
    )

    # Check 2: File does not exist errors counted
    scores["file_not_exist_counted"] = (
        1.0 if "file does not exist" in full_text or "file not found" in full_text
        else 0.0
    )

    # Check 3: Invalid method identified
    scores["invalid_method_identified"] = (
        1.0 if "invalid method" in full_text
        else 0.0
    )

    # Check 4: Server-internal errors included (mod_jk or createBean)
    has_mod_jk = "mod_jk" in full_text or "jk2_init" in full_text
    has_bean = "createbean" in full_text or "factory" in full_text or "config.update" in full_text
    scores["internal_errors_included"] = (
        1.0 if has_mod_jk and has_bean else
        0.5 if has_mod_jk or has_bean else 0.0
    )

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

依下列評分標準逐項評估（每項 0.0–1.0，最後取平均）：
- 已在工作區建立 `error_types_report.json`
- 已將「Directory index forbidden」判定為最常見的用戶端錯誤（~224）
- 已找出並計數「File does not exist」錯誤
- 已將「Invalid method in request」判定為一個獨立的錯誤類型
- 分析中納入了伺服器內部錯誤（mod_jk、env.createBean2）
