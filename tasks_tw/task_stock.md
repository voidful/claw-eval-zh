---
id: task_stock
name: 查詢台積電（2330）目前股價
category: research
grading_type: automated
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_stock
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: manual_review_only
claw_eval_tw_id: T009tw_stock
workspace_files: []
---

# 查詢台積電（2330）目前股價

## Prompt

請查詢台積電（2330，TSMC）目前的股價，並存到 stock_report.txt，內容包含：股價、
查詢日期，以及一段簡短的市場摘要。

注意：這是即時資料，請務必標明**查詢日期與資料來源**；若無法取得即時報價，請說明
資料限制與不確定性，不要捏造數字。股票代號 2330、檔名 stock_report.txt 不可更改。

## Expected Behavior

助手應透過網路查詢台積電（2330）目前股價，並將股價、查詢日期、資料來源與一段市場摘要
寫入 stock_report.txt。因為是即時資料，正確行為是**標明查詢日期與來源、說明不確定性**，
而非給出某個寫死的價格。評分不檢查特定價格數值。

## Grading Criteria

- [ ] 建立檔案 stock_report.txt
- [ ] 提及台積電 / 2330 / TSMC
- [ ] 包含股價數值（NT$ 或數字）
- [ ] 標明查詢日期
- [ ] 包含市場摘要
- [ ] 格式清楚（價格、日期、摘要分明）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW stock lookup (台積電 2330). Live data: checks ticker/date/summary
    presence, NOT a hard-coded price (reproducibility)."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    f = workspace / "stock_report.txt"
    if not f.exists():
        return {k: 0.0 for k in ["file_created", "ticker_present", "price_present",
                                 "date_present", "summary_present", "well_formatted"]}
    content = f.read_text(encoding="utf-8", errors="ignore")
    scores = {"file_created": 1.0}
    scores["ticker_present"] = 1.0 if re.search(r'\b2330\b|台積電|臺積電|TSMC', content, re.I) else 0.0
    price_patterns = [r'NT\$?\s*\d', r'\d{3,4}(?:\.\d+)?\s*元', r'\b\d{3,4}(?:\.\d+)?\b', r'\$\s*\d']
    scores["price_present"] = 1.0 if any(re.search(p, content, re.I) for p in price_patterns) else 0.0
    date_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{4}\s*年\s*\d{1,2}\s*月', r'查詢日期', r'\d{1,2}/\d{1,2}']
    scores["date_present"] = 1.0 if any(re.search(p, content, re.I) for p in date_patterns) else 0.0
    scores["summary_present"] = 1.0 if (re.search(r'摘要|總結|市場|走勢|分析|summary', content, re.I)
                                        and len(content.strip()) >= 40) else 0.0
    scores["well_formatted"] = 1.0 if len(content.strip()) >= 60 else 0.5
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
