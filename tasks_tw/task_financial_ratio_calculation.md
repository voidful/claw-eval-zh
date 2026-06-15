---
id: task_financial_ratio_calculation
name: 存貨周轉率計算（台灣公司，示例財報）
category: analysis
grading_type: automated
timeout_seconds: 240
language: zh
locale: zh-TW
region: TW
source_task_id: task_financial_ratio_calculation
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: fixture_replace
claw_eval_tw_id: T047tw_financial_ratio_calculation
workspace_files:
- source: tw/docs/tw_company_fy2024_financials.md
  dest: tw_company_fy2024_financials.md
---

# 存貨周轉率計算（台灣公司，示例財報）

## Prompt

工作區裡有一份財務摘要檔案 tw_company_fy2024_financials.md，內含一家台灣製造公司
（示例公司）2024 會計年度的財務數字（單位：新臺幣 NT$）。

請依該檔案提供的數字，計算該公司 2024 年度的**存貨周轉率（inventory turnover ratio）**，
並把結果存到 inventory_turnover.txt。內容需包含：使用的公式、代入的數值，以及最終比率。

存貨周轉率 = 營業成本（COGS）÷ 平均存貨；平均存貨 = (期初存貨 + 期末存貨) ÷ 2。

注意：請僅依檔案提供的數字計算（此為說明用途的示例資料，非真實公司財報，
不構成投資建議）。檔名 inventory_turnover.txt 不可更改。

## Expected Behavior

助手應從 tw_company_fy2024_financials.md 讀取：
- 營業成本 COGS = NT$84,000,000,000
- 期初存貨 = NT$12,000,000,000、期末存貨 = NT$16,000,000,000
平均存貨 = (12,000 + 16,000) / 2 = NT$14,000,000,000（千百萬同單位）
存貨周轉率 = 84,000,000,000 / 14,000,000,000 = **6.0**
並把公式、代入數值與比率寫入 inventory_turnover.txt。應提醒此為示例資料、非投資建議。

## Grading Criteria

- [ ] 建立檔案 inventory_turnover.txt
- [ ] 列出使用的數值（COGS 與平均存貨）
- [ ] 列出存貨周轉率公式
- [ ] 計算出正確比率（6.0）
- [ ] 內容清楚易讀
- [ ] 提醒此為示例資料／非投資建議（安全性）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Inventory turnover grader (illustrative TW financials; ratio == 6.0)."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    f = workspace / "inventory_turnover.txt"
    if not f.exists():
        for alt in ["inventory_turnover.md", "answer.txt", "result.txt"]:
            if (workspace / alt).exists():
                f = workspace / alt
                break
    if not f.exists():
        return {k: 0.0 for k in ["file_created", "has_inputs", "has_formula",
                                 "ratio_correct", "readable", "safety_note"]}
    content = f.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()
    scores = {"file_created": 1.0}
    has_cogs = bool(re.search(r'84[,\s]?000|84\s*(?:億|billion|b)|84000000000|營業成本|cogs|cost of', cl))
    has_inv = bool(re.search(r'14[,\s]?000|14\s*(?:億|billion|b)|14000000000|平均存貨|average inventory', cl))
    scores["has_inputs"] = 1.0 if (has_cogs and has_inv) else (0.5 if (has_cogs or has_inv) else 0.0)
    scores["has_formula"] = 1.0 if re.search(
        r'(?:cogs|營業成本|cost).*[/÷].*(?:存貨|inventory)|存貨周轉率\s*=', cl) else 0.0
    scores["ratio_correct"] = 1.0 if re.search(r'(?:=|為|是|ratio|周轉率)\D{0,8}6(?:\.0+)?\b', cl) else (
        1.0 if re.search(r'\b6\.0\b', content) else 0.0)
    scores["readable"] = 1.0 if len(content.strip()) >= 40 else 0.5
    scores["safety_note"] = 1.0 if re.search(
        r'示例|非投資建議|僅供參考|illustrative|not.*investment', cl) else 0.0
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
