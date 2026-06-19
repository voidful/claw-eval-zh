---
id: task_spreadsheet_summary
name: |
  CSV 與 Excel 資料摘要
category: analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_spreadsheet_summary
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T042tw_spreadsheet_summary
workspace_files:
- source: quarterly_sales.csv
  dest: quarterly_sales.csv
- source: company_expenses.xlsx
  dest: company_expenses.xlsx
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# CSV 與 Excel 資料摘要


## Prompt

工作區裡有兩個資料檔，提供給你分析：

1. `quarterly_sales.csv` —— 一個包含銷售交易的 CSV 檔，欄位有：Date、Region、Product、Units_Sold、Unit_Price、Revenue、Cost（共 24 列資料）
2. `company_expenses.xlsx` —— 一個 Excel 活頁簿，含兩個工作表：「Q1_Expenses」（員工費用報告，12 筆紀錄）與「Budgets」（各部門預算分配）

請讀取並分析這兩個檔案，然後把一份摘要報告寫入 `data_summary.md`，內容包含：

- **CSV 分析**：總營收、總利潤（營收減成本）、總銷售數量、依營收計算表現最佳的地區，以及依營收計算最暢銷的產品。
- **Excel 分析**：Q1 總費用、費用最高的部門、總費用最高的員工，以及各部門 Q1 實際費用與 Q1 預算的比較。
- 一段結合兩個檔案發現的整體洞察（insights）區段。

請只根據檔案中實際存在的資料作答，不要臆測或填補缺漏的數字。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔（標準 CSV 格式，容易解析）
2. 讀取並解析 Excel 檔（需處理含多個工作表的 `.xlsx` 格式）
3. 從兩個檔案計算出正確的彙總統計
4. 把一份結構良好的 markdown 摘要報告寫入 `data_summary.md`

CSV 含 24 列銷售資料，橫跨 4 個地區（North、South、East、West）與 3 項產品（Widget A、B、C）。Excel 檔有 12 筆費用紀錄、橫跨 4 個部門，並有一個獨立的預算工作表列出各部門的季度分配。

預期關鍵數值：

- CSV 總營收：$119,900
- CSV 總利潤：$47,960
- CSV 總數量：3,775
- CSV 最佳地區：East（$33,075）
- CSV 最佳產品：Widget B（$47,400）
- Excel Q1 總費用：$15,430
- Excel 費用最高部門：Engineering（$7,680）
- Excel 費用最高員工：Alice Chen（$5,400）

## Grading Criteria

- [ ] 助手成功讀取 CSV 檔
- [ ] 助手成功讀取 Excel 檔（含多個工作表）
- [ ] 已建立摘要報告檔 data_summary.md
- [ ] 正確回報總營收（約 $119,900）
- [ ] 正確計算總利潤（約 $47,960）
- [ ] 辨識出依營收計算的最佳地區（East）
- [ ] 辨識出依營收計算的最佳產品（Widget B）
- [ ] 正確回報 Q1 總費用（約 $15,430）
- [ ] 辨識出費用最高的部門（Engineering）
- [ ] 辨識出費用最高的員工（Alice Chen）
- [ ] 包含預算與實際費用的比較
- [ ] 報告結構良好、易讀

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the spreadsheet summary task by checking the output report
    for correct numerical values and key findings.

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

    # Check if summary report exists
    report_path = workspace / "data_summary.md"
    if not report_path.exists():
        # Try common alternative names
        alternatives = ["summary.md", "report.md", "data_report.md", "analysis.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        scores["report_created"] = 0.0
        scores["total_revenue"] = 0.0
        scores["total_profit"] = 0.0
        scores["top_region"] = 0.0
        scores["top_product"] = 0.0
        scores["total_expenses"] = 0.0
        scores["top_department"] = 0.0
        scores["top_employee"] = 0.0
        scores["budget_comparison"] = 0.0
        return scores

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check total revenue (~119,900)
    # Look for the number in various formats: 119900, 119,900, 119900.00, etc.
    revenue_patterns = [
        r'119[,.]?900',
        r'119[,.]?900\.00',
    ]
    has_revenue = any(re.search(p, content.replace(' ', '')) for p in revenue_patterns)
    scores["total_revenue"] = 1.0 if has_revenue else 0.0

    # Check total profit (~47,960)
    profit_patterns = [
        r'47[,.]?960',
    ]
    has_profit = any(re.search(p, content.replace(' ', '')) for p in profit_patterns)
    scores["total_profit"] = 1.0 if has_profit else 0.0

    # Check top region (East)
    # Look for East being called out as top/highest/best/leading region
    east_patterns = [
        r'east.*(?:top|highest|most|best|leading|largest)',
        r'(?:top|highest|most|best|leading|largest).*east',
        r'east.*\$?33[,.]?075',
        r'33[,.]?075.*east',
    ]
    has_top_region = any(re.search(p, content_lower) for p in east_patterns)
    scores["top_region"] = 1.0 if has_top_region else 0.0

    # Check top product (Widget B)
    product_patterns = [
        r'widget\s*b.*(?:top|highest|most|best|leading|largest)',
        r'(?:top|highest|most|best|leading|largest).*widget\s*b',
        r'widget\s*b.*\$?47[,.]?400',
        r'47[,.]?400.*widget\s*b',
    ]
    has_top_product = any(re.search(p, content_lower) for p in product_patterns)
    scores["top_product"] = 1.0 if has_top_product else 0.0

    # Check total Q1 expenses (~15,430)
    expense_patterns = [
        r'15[,.]?430',
    ]
    has_expenses = any(re.search(p, content.replace(' ', '')) for p in expense_patterns)
    scores["total_expenses"] = 1.0 if has_expenses else 0.0

    # Check top department (Engineering)
    dept_patterns = [
        r'engineering.*(?:top|highest|most|largest|leading)',
        r'(?:top|highest|most|largest|leading).*engineering',
        r'engineering.*\$?7[,.]?680',
        r'7[,.]?680.*engineering',
    ]
    has_top_dept = any(re.search(p, content_lower) for p in dept_patterns)
    scores["top_department"] = 1.0 if has_top_dept else 0.0

    # Check top employee (Alice Chen)
    employee_patterns = [
        r'alice\s*chen.*(?:top|highest|most|largest|leading)',
        r'(?:top|highest|most|largest|leading).*alice\s*chen',
        r'alice\s*chen.*\$?5[,.]?400',
        r'5[,.]?400.*alice\s*chen',
    ]
    has_top_employee = any(re.search(p, content_lower) for p in employee_patterns)
    scores["top_employee"] = 1.0 if has_top_employee else 0.0

    # Check for budget vs actual comparison
    budget_indicators = [
        r'budget.*actual',
        r'actual.*budget',
        r'budget.*expense',
        r'under\s*budget',
        r'over\s*budget',
        r'variance',
        r'25[,.]?000',  # Engineering Q1 budget
    ]
    has_budget = any(re.search(p, content_lower) for p in budget_indicators)
    scores["budget_comparison"] = 1.0 if has_budget else 0.0

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

### 評分項 1：資料讀取與解析（權重 25%）

**1.0 分**：助手正確讀取了 CSV 檔與含多個工作表的 Excel 檔，無誤地擷取所有相關資料。
**0.75 分**：助手讀取了兩個檔案，但對其中一種格式略有問題（例如只讀了一個 Excel 工作表）。
**0.5 分**：助手正確讀取了其中一個檔案，但對另一種格式有困難。
**0.25 分**：助手嘗試讀取檔案，但遇到顯著的解析錯誤。
**0.0 分**：助手未能讀取任一檔案，或未嘗試擷取資料。

### 評分項 2：分析準確性（權重 35%）

**1.0 分**：所有計算出的統計（總計、最佳表現者、比較）在數值上皆正確且清楚呈現，且皆有檔案資料支持。
**0.75 分**：多數統計正確，僅有一兩個小數值錯誤。
**0.5 分**：部分統計正確，但數個關鍵數字錯誤或缺漏。
**0.25 分**：少數統計正確；存在重大計算錯誤，或出現檔案中沒有依據的捏造數字。
**0.0 分**：沒有任何正確統計，或未嘗試分析。

### 評分項 3：報告品質與結構（權重 25%）

**1.0 分**：報告組織良好、區段清楚、markdown 格式得當，發現呈現一目了然。含標題，並以表格或格式化清單呈現資料。
**0.75 分**：報告有條理且易讀，僅有少許格式問題。
**0.5 分**：報告含有資訊，但組織不佳或難以閱讀。
**0.25 分**：報告雜亂無章或缺少主要區段。
**0.0 分**：未建立報告，或報告為空／無法使用。

### 評分項 4：洞察與綜整（權重 15%）

**1.0 分**：報告含有縝密的跨檔案洞察、對趨勢的有意義觀察，以及結合兩個資料來源的可行建議；洞察以資料為依據，未過度推論。
**0.75 分**：報告含有一些跨檔案觀察，但可以更具洞見。
**0.5 分**：報告呈現了兩個檔案的資料，但缺乏有意義的綜整。
**0.25 分**：報告幾乎沒有把兩個資料來源的發現連結起來。
**0.0 分**：未提供任何綜整或洞察。
