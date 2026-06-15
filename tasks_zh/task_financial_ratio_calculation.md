---
id: task_financial_ratio_calculation
name: 財務比率計算
category: analysis
grading_type: automated
timeout_seconds: 240
language: zh
locale: zh-TW
source_task_id: task_financial_ratio_calculation
source_benchmark: pinchbench
claw_eval_id: P047zh_financial_ratio_calculation
workspace_files: []
---

# 財務比率計算

## Prompt

請計算 U.S. Steel 在 2024 會計年度（fiscal year 2024）的存貨週轉率（inventory turnover ratio）。

請查找所需的財務數字、執行計算，並把結果存到 `us_steel_inventory_turnover.txt`。請附上公式、你使用的數值，以及最終的比率。

（提醒：本任務僅供資訊與分析參考，不構成投資或財務建議，亦不取代專業財務意見。）

## Expected Behavior

助手應該：

1. 找到計算存貨週轉率所需的 U.S. Steel FY2024 相關數字。
2. 使用標準的存貨週轉率公式，例如銷貨成本（cost of sales）除以平均存貨（average inventory）。
3. 列出計算中使用的數值。
4. 建立 `us_steel_inventory_turnover.txt` 並附上最終答案。

就 FY2024 而言，以年度銷貨成本與依期初、期末餘額計算的平均存貨來算，正確答案應落在約 6.5x 左右。

## Grading Criteria

- [ ] 已建立 us_steel_inventory_turnover.txt 檔案
- [ ] 檔案含有銷貨成本（cost of sales）與存貨（inventory）輸入值
- [ ] 檔案展示了公式或計算方法
- [ ] 最終比率約為 6.55x
- [ ] 答案易讀且在財務上合理

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    workspace = Path(workspace_path)
    answer_file = workspace / "us_steel_inventory_turnover.txt"

    if not answer_file.exists():
        return {
            "file_created": 0.0,
            "has_inputs": 0.0,
            "has_formula": 0.0,
            "ratio_correct": 0.0,
            "readable": 0.0,
        }

    content = answer_file.read_text(encoding="utf-8", errors="ignore")
    lowered = content.lower()
    scores = {"file_created": 1.0}

    has_cost = bool(re.search(r"14[, ]?060|cost of sales", lowered))
    has_inventory = bool(re.search(r"2[, ]?128|2[, ]?168|2[, ]?148|average inventory|inventory", lowered))
    scores["has_inputs"] = 1.0 if has_cost and has_inventory else (0.5 if has_cost or has_inventory else 0.0)

    scores["has_formula"] = 1.0 if re.search(r"turnover|cost of sales\s*/\s*average inventory|cost of sales divided by average inventory", lowered) else 0.0

    ratio_matches = re.findall(r"\b(\d+\.\d+|\d+)\s*(?:x|times)?\b", lowered)
    ratio_score = 0.0
    for match in ratio_matches:
        try:
            value = float(match)
        except ValueError:
            continue
        if 6.45 <= value <= 6.65:
            ratio_score = 1.0
            break
        if 6.3 <= value <= 6.8:
            ratio_score = max(ratio_score, 0.5)
    scores["ratio_correct"] = ratio_score

    scores["readable"] = 1.0 if len(content.strip()) >= 40 and ("u.s. steel" in lowered or "us steel" in lowered) else 0.5
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
