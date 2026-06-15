---
id: task_csv_stock_volatility
name: Apple 股票 2014 年波動率分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_stock_volatility
source_benchmark: pinchbench
claw_eval_id: P054zh_csv_stock_volatility
workspace_files:
- source: csvs/apple_stock_2014.csv
  dest: apple_stock_2014.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# Apple 股票 2014 年波動率分析

## Prompt

我的工作區（workspace）中有一個 CSV 檔 `apple_stock_2014.csv`，內含 Apple
(AAPL) 2014 年的調整後收盤價。該檔有兩個欄位：`AAPL_x`（日期，格式為
YYYY-MM-DD）與 `AAPL_y`（調整後收盤價）。共有 240 個交易日的資料。

請分析 Apple 股票 2014 年的每日波動率（daily volatility），並將你的發現寫入
名為 `volatility_report.md` 的檔案。你的報告應包含：

- **每日波動率指標**：計算每日百分比報酬（收盤對收盤，close-to-close），再
  計算這些每日報酬的標準差（standard deviation），作為波動率的衡量。
- **年化波動率**：將每日標準差乘以 252 的平方根（square root of 252），以進行
  年化（annualize）。
- **波動最大的前 5 個交易日**：依每日百分比變化的絕對值最大者排序，列出其日期
  與數值。
- 該年度的**每日絕對百分比變化平均值**。
- **各季波動率比較**：分別計算各季每日報酬的標準差（Q1：Jan-Mar、Q2：Apr-Jun、
  Q3：Jul-Sep、Q4：Oct-Dec），以呈現全年波動率的變化。
- 一段簡短的**總結**，解讀波動率的型態。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔
2. 以 `(price_today - price_yesterday) / price_yesterday * 100` 計算每日百分比報酬
3. 計算每日報酬的標準差（約 1.47%）
4. 將波動率年化（約 23.35%）
5. 依每日百分比變化的絕對值找出波動最大的前 5 個交易日
6. 計算各季標準差以比較全年波動率
7. 撰寫一份結構良好的 markdown 報告

預期關鍵數值：

- 每日報酬標準差：約 1.47%
- 年化波動率：約 23.35%
- 波動最大的前 5 日（依百分比變化絕對值）：
  1. 2014-01-28：-7.51%
  2. 2014-04-24：+7.40%
  3. 2014-10-21：+4.78%
  4. 2014-12-02：-4.47%
  5. 2014-09-04：-4.13%
- 各季標準差：Q1 約 1.58%、Q2 約 1.39%、Q3 約 1.30%、Q4 約 1.64%

## Grading Criteria

- [ ] 已建立報告檔 `volatility_report.md`
- [ ] 正確計算每日報酬標準差（約 1.47%）
- [ ] 正確計算年化波動率（約 23%）
- [ ] 找出波動最大的前 5 日並附正確日期
- [ ] 波動日附上每日百分比變化
- [ ] 包含各季波動率分解
- [ ] 包含每日報酬平均值或平均絕對變化
- [ ] 提供波動率型態的總結解讀

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the stock volatility analysis task.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check if report exists
    report_path = workspace / "volatility_report.md"
    if not report_path.exists():
        alternatives = ["volatility.md", "report.md", "stock_volatility.md", "analysis.md",
                        "stock_volatility_report.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "daily_std_dev": 0.0,
            "annualized_volatility": 0.0,
            "volatile_days_identified": 0.0,
            "volatile_days_values": 0.0,
            "quarterly_breakdown": 0.0,
            "average_metric": 0.0,
            "summary_interpretation": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check daily std dev (~1.47%)
    std_patterns = [
        r'1\.4[67]\d*%',
        r'1\.47',
        r'1\.48',
        r'0\.014[67]',
    ]
    scores["daily_std_dev"] = 1.0 if any(re.search(p, content) for p in std_patterns) else 0.0

    # Check annualized volatility (~23.35%)
    annual_patterns = [
        r'2[23]\.\d+%',
        r'23\.3',
        r'23\.4',
        r'23%',
        r'~23',
    ]
    # Must also be in context of annualized/annual
    has_annual_value = any(re.search(p, content) for p in annual_patterns)
    has_annual_context = bool(re.search(r'annual', content_lower))
    scores["annualized_volatility"] = 1.0 if (has_annual_value and has_annual_context) else (0.5 if has_annual_value else 0.0)

    # Check top volatile days identified (dates)
    volatile_dates = ['2014-01-28', '2014-04-24', '2014-10-21', '2014-12-02', '2014-09-04']
    dates_found = sum(1 for d in volatile_dates if d in content)
    # Also check informal date references
    informal_dates = [
        (r'jan(?:uary)?\s*28', '2014-01-28'),
        (r'apr(?:il)?\s*24', '2014-04-24'),
        (r'oct(?:ober)?\s*21', '2014-10-21'),
        (r'dec(?:ember)?\s*0?2\b', '2014-12-02'),
        (r'sep(?:tember)?\s*0?4\b', '2014-09-04'),
    ]
    for pattern, _ in informal_dates:
        if re.search(pattern, content_lower) and dates_found < 5:
            dates_found = min(dates_found + 1, 5)
    scores["volatile_days_identified"] = min(dates_found / 3.0, 1.0)

    # Check volatile day values
    volatile_values = [r'7\.5[01]', r'7\.40', r'4\.7[78]', r'4\.4[67]', r'4\.1[23]']
    values_found = sum(1 for p in volatile_values if re.search(p, content))
    scores["volatile_days_values"] = min(values_found / 3.0, 1.0)

    # Check quarterly breakdown
    quarter_patterns = [r'q1', r'q2', r'q3', r'q4']
    quarter_alt = [r'(?:first|1st)\s*quarter', r'(?:second|2nd)\s*quarter',
                   r'(?:third|3rd)\s*quarter', r'(?:fourth|4th)\s*quarter']
    quarters_found = sum(1 for p in quarter_patterns if re.search(p, content_lower))
    if quarters_found < 4:
        quarters_found += sum(1 for p in quarter_alt if re.search(p, content_lower))
    scores["quarterly_breakdown"] = 1.0 if quarters_found >= 4 else (0.5 if quarters_found >= 2 else 0.0)

    # Check for average metric (daily return or absolute change)
    avg_patterns = [
        r'average.*(?:daily|return|change)',
        r'(?:daily|return|change).*average',
        r'mean.*(?:daily|return|change)',
        r'(?:daily|return|change).*mean',
    ]
    scores["average_metric"] = 1.0 if any(re.search(p, content_lower) for p in avg_patterns) else 0.0

    # Check for summary/interpretation
    interpretation_patterns = [
        r'(?:summary|conclusion|interpretation|takeaway|insight)',
        r'(?:suggest|indicat|impl)',
        r'(?:correlat|driven\s*by|caused\s*by|due\s*to)',
        r'(?:earnings|product\s*launch|announcement|event)',
    ]
    interp_found = sum(1 for p in interpretation_patterns if re.search(p, content_lower))
    scores["summary_interpretation"] = 1.0 if interp_found >= 2 else (0.5 if interp_found >= 1 else 0.0)

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

### 評分項 1：分析正確性（權重 35%）

**1.0 分**：所有波動率指標皆正確計算：每日標準差（約 1.47%）、年化波動率
（約 23%）、波動最大的日期符合預期值，且各季分解皆正確。
**0.75 分**：多數指標正確，僅有一、兩處輕微的數值落差。
**0.5 分**：部分指標正確，但有數個關鍵數字錯誤，或方法論部分不正確。
**0.25 分**：僅少數指標正確；出現重大計算錯誤或方法論錯誤。
**0.0 分**：無任何正確計算，或未嘗試分析。

### 評分項 2：波動率解讀（權重 30%）

**1.0 分**：提供對波動率型態具意義的解讀，說明各季差異可能代表的意義，將高波動
日連結到可能的市場事件（財報、產品發表），並為年化波動率數字提供情境脈絡。
**0.75 分**：解讀良好，對型態與可能成因提供一些具意義的脈絡。
**0.5 分**：基本解讀，能指出型態，但對成因或意涵著墨有限。
**0.25 分**：解讀極少；大多只是呈現數字而缺乏脈絡。
**0.0 分**：未提供解讀，或分析完全錯誤。

### 評分項 3：報告結構與呈現（權重 20%）

**1.0 分**：報告組織良好，分節清楚，以表格呈現波動日與各季資料，排版適當，行文
流暢有邏輯。
**0.75 分**：報告有條理、可讀，僅有小幅排版問題。
**0.5 分**：報告包含分析，但組織不佳或不易閱讀。
**0.25 分**：報告雜亂或缺少主要章節。
**0.0 分**：未建立報告，或報告為空／無法使用。

### 評分項 4：完整性（權重 15%）

**1.0 分**：所有要求的元素皆齊備：每日標準差、年化波動率、波動最大的前 5 日、
平均指標、各季比較與總結。
**0.75 分**：多數要求元素齊備，僅有一、兩處小缺漏。
**0.5 分**：缺少數個要求元素。
**0.25 分**：僅有少數要求元素。
**0.0 分**：報告缺漏或近乎空白。
