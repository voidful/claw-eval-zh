---
id: task_xlsx_hr_analytics
name: "XLSX 人力資源深度分析"
category: xlsx_analysis
difficulty: medium
timeout_seconds: 300
workspace_files:
  - source: tw/xlsx/hr_employee_data_2024.xlsx
    dest: hr_employee_data_2024.xlsx
grading_weights:
  automated: 0.5
  llm_judge: 0.5
grading_type: hybrid
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v2
---
## Prompt

讀取 `hr_employee_data_2024.xlsx`，分析 200 名員工的人力資源數據，輸出 `hr_analytics_report.md`：

1. **部門人力結構**：各部門人數、平均年資（以天/月計算，以今天為基準日）、職級分布（L1~L6 各多少人）
2. **薪資公平性分析**：
   - 各職級的平均薪資（跨所有部門）
   - 同職級不同部門的薪資標準差（是否存在明顯差異？）
   - 計算薪資的 Gini 係數（衡量薪資不平等程度）：Gini = Σ|xi-xj| / (2n²μ)
3. **績效-薪資相關性**：各績效等級（A/B/C/D）的平均薪資；計算 Pearson 相關係數（績效→數值轉換：A=4, B=3, C=2, D=1）
4. **離職率分析**：有離職日期的員工佔比；按部門和職級分析誰最常離職
5. **高飛風險人員識別**：年資 > 3 年且薪資低於同職級平均 10% 以上 → 標記為高風險，列出人數與代表性案例

## Expected Behavior

LLM 應使用 xlsx 解析工具讀取 `hr_employee_data_2024.xlsx`（可能含多個 sheet），正確辨識欄位（員工編號、部門、職級、入職日期、離職日期、薪資、績效等），並以今日日期計算年資。最終輸出 `hr_analytics_report.md`，包含至少 3 個 Markdown 表格（部門結構、薪資分析、高飛風險）以及洞察段落。

## Grading Criteria

10 個評分 key，每個 key 通過得 1 分，滿分 10 分（automated score = 通過數 / 10）。

| Key | 說明 |
|-----|------|
| `report_created` | `hr_analytics_report.md` 檔案存在 |
| `dept_headcount` | 報告中有部門名稱搭配人數數字 |
| `tenure_calculated` | 報告中有月份或年資相關數字（如「X 個月」「X 年」）|
| `level_distribution` | L1~L6 至少出現 4 個（代表職級分布已呈現）|
| `salary_by_level` | 報告中有職級（L1~L6）搭配薪資數字 |
| `gini_calculated` | 報告中有 Gini 係數（0 到 1 之間的小數，如 0.xx）|
| `performance_salary` | 績效等級（A/B/C/D）與薪資數字同時出現 |
| `attrition_rate` | 報告中有離職率（含 % 符號）|
| `flight_risk_count` | 報告中有高飛風險人數的具體數字 |
| `has_tables` | Markdown 表格（`\|...\|` 格式）出現 >= 3 個 |


- [ ] hr_analytics_report.md 檔案存在
- [ ] 報告中有部門名稱搭配人數數字
- [ ] 報告中有月份或年資相關數字（如「X 個月」「X 年」）
- [ ] L1~L6 至少出現 4 個（代表職級分布已呈現）
- [ ] 報告中有職級（L1~L6）搭配薪資數字
- [ ] 報告中有 Gini 係數（0 到 1 之間的小數，如 0.xx）
- [ ] 績效等級（A/B/C/D）與薪資數字同時出現
- [ ] 報告中有離職率（含 % 符號）
- [ ] 報告中有高飛風險人數的具體數字
- [ ] 格式）出現 >= 3 個
## Automated Checks

```python
import re
from pathlib import Path


def grade(transcript: list, workspace_dir: str) -> dict[str, bool]:
    report_path = Path(workspace_dir) / "hr_analytics_report.md"

    results = {
        "report_created": False,
        "dept_headcount": False,
        "tenure_calculated": False,
        "level_distribution": False,
        "salary_by_level": False,
        "gini_calculated": False,
        "performance_salary": False,
        "attrition_rate": False,
        "flight_risk_count": False,
        "has_tables": False,
    }

    if not report_path.exists():
        return results

    results["report_created"] = True
    text = report_path.read_text(encoding="utf-8", errors="ignore")

    # dept_headcount: 部門名稱後面或附近有人數數字
    dept_patterns = [
        r"(?:工程|業務|行銷|人資|財務|產品|研發|客服|營運|法務|IT|Engineering|Sales|Marketing|HR|Finance)\D{0,20}\d+\s*(?:人|名|位)?",
        r"\d+\s*(?:人|名|位)[^\n]{0,30}(?:部|組|team)",
    ]
    results["dept_headcount"] = any(re.search(p, text) for p in dept_patterns)

    # tenure_calculated: 出現月份或年資數字
    tenure_match = re.search(
        r"(?:平均年資|年資|任職)[^\n]{0,60}(\d+\.?\d*)\s*(?:個月|月|年|天|days|months|years)",
        text,
    )
    if not tenure_match:
        tenure_match = re.search(r"(\d+\.?\d*)\s*(?:個月|月份|年)[^\n]{0,40}(?:年資|平均|tenure)", text)
    results["tenure_calculated"] = tenure_match is not None

    # level_distribution: L1~L6 至少 4 個出現
    levels_found = set(re.findall(r"L[1-6]", text))
    results["level_distribution"] = len(levels_found) >= 4

    # salary_by_level: L1~L6 + 數字（薪資）同時出現
    salary_level_match = re.search(
        r"L[1-6][^\n]{0,60}\d[\d,]+",
        text,
    )
    if not salary_level_match:
        salary_level_match = re.search(r"\d[\d,]+[^\n]{0,40}L[1-6]", text)
    results["salary_by_level"] = salary_level_match is not None

    # gini_calculated: Gini 係數（0~1 小數）
    gini_match = re.search(
        r"(?:Gini|基尼)[^\n]{0,60}0\.\d{2,4}",
        text,
        re.IGNORECASE,
    )
    if not gini_match:
        gini_match = re.search(r"0\.\d{2,4}[^\n]{0,40}(?:Gini|基尼)", text, re.IGNORECASE)
    results["gini_calculated"] = gini_match is not None

    # performance_salary: A/B/C/D 等級 + 薪資數字
    perf_match = re.search(
        r"(?:績效|等級|Performance)[^\n]{0,20}[ABCD][^\n]{0,60}\d[\d,]+",
        text,
    )
    if not perf_match:
        perf_match = re.search(r"[ABCD]\s*(?:等級|級|績效)[^\n]{0,40}\d[\d,]+", text)
    if not perf_match:
        # 表格中 A/B/C/D 行含數字
        perf_match = re.search(r"^\s*\|\s*[ABCD]\s*\|[^\n]+\d[\d,]+", text, re.MULTILINE)
    results["performance_salary"] = perf_match is not None

    # attrition_rate: 離職率百分比
    attrition_match = re.search(
        r"(?:離職率|attrition)[^\n]{0,60}(\d+\.?\d*)\s*%",
        text,
        re.IGNORECASE,
    )
    if not attrition_match:
        attrition_match = re.search(r"(\d+\.?\d*)\s*%[^\n]{0,40}(?:離職|attrition)", text, re.IGNORECASE)
    results["attrition_rate"] = attrition_match is not None

    # flight_risk_count: 高飛風險人數具體數字
    risk_match = re.search(
        r"(?:高飛風險|高風險|flight.?risk)[^\n]{0,60}(\d+)\s*(?:人|名|位|employees)?",
        text,
        re.IGNORECASE,
    )
    if not risk_match:
        risk_match = re.search(r"(\d+)\s*(?:人|名|位)[^\n]{0,40}(?:高飛風險|高風險|flight.?risk)", text, re.IGNORECASE)
    results["flight_risk_count"] = risk_match is not None

    # has_tables: 計算獨立表格數量 >= 3
    table_count = 0
    in_table = False
    for line in text.split("\n"):
        if re.match(r"\s*\|.+\|", line):
            if not in_table:
                table_count += 1
                in_table = True
        else:
            in_table = False
    results["has_tables"] = table_count >= 3

    return results


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

請依照以下四個維度對報告進行評分，各維度分數為 0~100，最終加權得分作為 LLM Judge 分數。

| 維度 | 權重 | 評分說明 |
|------|------|----------|
| **Data Extraction** | 25% | xlsx 多 sheet 是否正確讀取；欄位識別是否準確（入職日、離職日、薪資、職級、績效等）；200 筆資料是否完整處理，無遺漏 |
| **Statistical Analysis** | 35% | Gini 係數公式 `Σ\|xi-xj\| / (2n²μ)` 使用正確；Pearson 相關係數計算有效；年資以基準日正確計算（非硬編碼）；標準差分析有依據；高飛風險篩選條件（年資>3年且薪資<同職級平均×90%）準確 |
| **Insight Quality** | 25% | 報告是否超越數字，提供可行洞察（例如：「業務部L3薪資比工程部L3低42%，是潛在流失風險」）；離職分析是否指出高風險部門/職級；薪資公平性是否給出政策建議 |
| **Report Completeness** | 15% | 5 個分析項目（部門結構/薪資公平性/績效相關性/離職率/高飛風險）是否都有完整呈現；報告結構清晰，可直接用於 HR 會議 |

**評分指引**：
- 90~100：所有統計計算正確，洞察深刻具體，報告結構完整可立即使用
- 70~89：大部分計算正確，洞察基本到位，個別項目略嫌單薄
- 50~69：計算有誤差或缺少 1~2 個分析項目，洞察停留在數字描述
- 30~49：多個統計計算錯誤，或缺少 Gini/相關係數等核心指標
- 0~29：報告嚴重不完整，缺少核心分析

## Additional Notes

- 年資計算應以腳本執行當日為基準日，不可硬編碼日期。
- Gini 係數計算時應只包含在職員工（無離職日期）的薪資。
- Pearson 相關係數計算前須先將績效等級轉為數值（A=4, B=3, C=2, D=1）。
- 高飛風險定義：在職狀態（無離職日期）+ 年資 > 3 年 + 薪資 < 同職級平均薪資 × 90%。
- 若 xlsx 含多個 sheet，應逐一掃描並在報告中說明各 sheet 的用途。
