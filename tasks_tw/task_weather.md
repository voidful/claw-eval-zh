---
id: task_weather
name: 天氣腳本編寫（台北）
category: coding
grading_type: automated
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_weather
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T027tw_weather
workspace_files: []
---

# 天氣腳本編寫（台北）

## Prompt

請編寫一個名為 weather.py 的 Python 腳本：使用 wttr.in API 取得台北市（Taipei）的
天氣資料，並印出一段易讀的天氣摘要。請加入基本的網路錯誤處理。

wttr.in 的 JSON 介面為 https://wttr.in/Taipei?format=j1，簡易文字介面為
https://wttr.in/Taipei?format=3。

## Expected Behavior

助手應該：
1. 建立一個名為 weather.py 的檔案
2. 寫出向 wttr.in 發出 HTTP 請求的 Python 程式碼（地點為台北 Taipei）
3. 解析回應並印出易讀的天氣摘要
4. 包含基本的網路錯誤處理（try/except）
5. 使用標準函式庫或常見函式庫（requests、urllib）

注意：檔名 weather.py 與 wttr.in 網址不可更改；地點為台北（Taipei）。
天氣為即時資料：程式應標明資料來源（wttr.in）與查詢時間，並對即時資料的不確定性
有基本容錯；grader 不檢查特定天氣數值。

## Grading Criteria

- [ ] 建立檔案 weather.py
- [ ] 含有效的 Python 語法
- [ ] 程式碼向 wttr.in 或類似天氣 API 發出 HTTP 請求
- [ ] 程式碼指定台北（Taipei / 台北 / 臺北）地點
- [ ] 程式碼含錯誤處理（try/except）
- [ ] 程式碼會印出或輸出天氣資訊
- [ ] 腳本具可執行結構

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Weather script grader (Taiwan: Taipei). Checks structure + HTTP + location."""
    from pathlib import Path
    import re, ast
    scores = {}
    workspace = Path(workspace_path)
    script = workspace / "weather.py"
    if not script.exists():
        return {k: 0.0 for k in ["file_created", "valid_python", "has_http_request",
                                 "references_location", "has_error_handling",
                                 "has_output", "executable_structure"]}
    scores["file_created"] = 1.0
    content = script.read_text(encoding="utf-8", errors="ignore")
    try:
        ast.parse(content)
        scores["valid_python"] = 1.0
    except SyntaxError:
        return {**scores, "valid_python": 0.0, "has_http_request": 0.0,
                "references_location": 0.0, "has_error_handling": 0.0,
                "has_output": 0.0, "executable_structure": 0.0}
    http = [r'import\s+requests', r'from\s+requests', r'import\s+urllib',
            r'from\s+urllib', r'requests\.get', r'urllib\.request', r'urlopen', r'wttr\.in']
    scores["has_http_request"] = 1.0 if any(re.search(p, content, re.I) for p in http) else 0.0
    loc = [r'Taipei', r'台北', r'臺北']
    scores["references_location"] = 1.0 if any(re.search(p, content, re.I) for p in loc) else 0.0
    scores["has_error_handling"] = 1.0 if re.search(r'try\s*:|except', content) else 0.0
    scores["has_output"] = 1.0 if re.search(r'print\s*\(|sys\.stdout', content) else 0.0
    scores["executable_structure"] = 1.0 if re.search(
        r'def\s+\w+\s*\(|if\s+__name__\s*==', content) else 0.5
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
