---
id: task_csv_stock_volatility
name: 台積電（2330）2024 波動率分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_stock_volatility
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: fixture_replace
claw_eval_tw_id: T054tw_csv_stock_volatility
workspace_files:
- source: tw/csvs/tw_stock_2330_2024.csv
  dest: tw_stock_2330_2024.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台積電（2330）2024 波動率分析

## Prompt

我的工作區裡有一個 CSV 檔案 tw_stock_2330_2024.csv，內含台積電（2330）2024 年的
每日收盤價（來源：TWSE 公開資料）。檔案有兩欄：date（日期）與 close（收盤價，NT$），
共 242 個交易日。

請分析台積電 2024 年的每日波動率（volatility），並把結果寫入 volatility_report.md。
報告需包含：

- **每日報酬率的標準差**（daily return standard deviation，以百分比表示）
- **年化波動率**（annualized volatility，標準差 × √252）
- **波動最劇烈的交易日**（單日漲跌幅最大者）與其日期、數值
- 一段對整體波動程度的**總結與解讀**

注意：CSV 檔名、欄名與報告檔名 volatility_report.md 不可更改。

## Expected Behavior

助手應計算（已由程式從 TWSE 真實資料驗算）：
- 每日報酬率標準差約 2.17%
- 年化波動率約 34.5%（2.17% × √252）
- 單日最大漲幅約 +7.98%（2024-08-06）、單日最大跌幅約 -9.75%（2024-08-05）
並輸出結構清晰的 markdown 報告與解讀。

## Grading Criteria

- [ ] 建立報告檔案 volatility_report.md
- [ ] 報告每日報酬率標準差（約 2.17%）
- [ ] 報告年化波動率（約 34.5%）
- [ ] 指出波動最劇烈的交易日（2024-08-05 與 2024-08-06）
- [ ] 報告該等交易日的漲跌幅數值（約 +7.98% / -9.75%）
- [ ] 含整體波動程度的解讀／總結

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """2330 volatility grader. Values recomputed from real TWSE fixture."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    report = workspace / "volatility_report.md"
    if not report.exists():
        for alt in ["volatility.md", "report.md", "stock_volatility_report.md", "analysis.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in ["report_created", "daily_std_dev", "annualized_volatility",
                                 "volatile_days_dates", "volatile_days_values",
                                 "summary_interpretation"]}
    scores = {"report_created": 1.0}
    content = report.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()
    scores["daily_std_dev"] = 1.0 if re.search(r'2\.1[5-9]|2\.17|2\.2\b', content) else 0.0
    scores["annualized_volatility"] = 1.0 if re.search(r'3[45]\.\d|34\.5|3[45]\s*%', content) else 0.0
    dates = ['2024-08-05', '2024-08-06']
    dfound = sum(1 for d in dates if d in content) + (
        1 if re.search(r'8月\s*[56]', content) else 0)
    scores["volatile_days_dates"] = 1.0 if dfound >= 2 else (0.5 if dfound == 1 else 0.0)
    vals = sum(1 for p in [r'7\.9[78]', r'9\.7[45]'] if re.search(p, content))
    scores["volatile_days_values"] = 1.0 if vals >= 2 else (0.5 if vals == 1 else 0.0)
    interp = [r'波動', r'volatil', r'風險', r'risk', r'劇烈', r'穩定', r'震盪']
    scores["summary_interpretation"] = 1.0 if any(re.search(p, cl) for p in interp) else 0.0
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

### 評分項 1：計算準確度（權重 50%）
- 1.0：標準差、年化波動率、極端日數值正確
- 0.5：部分正確
- 0.0：未正確計算
### 評分項 2：解讀品質（權重 30%）
- 1.0：對波動程度有合理且具體的解讀
- 0.5：解讀籠統
- 0.0：無解讀
### 評分項 3：報告結構（權重 20%）
- 1.0：markdown 清楚完整
- 0.5：組織不佳
- 0.0：缺失
