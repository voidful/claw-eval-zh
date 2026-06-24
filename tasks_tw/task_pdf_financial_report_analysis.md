---
id: task_pdf_financial_report_analysis
name: "PDF 財報深度分析 — ACME Corp 2024"
category: pdf_analysis
difficulty: medium
timeout_seconds: 600
workspace_files:
  - source: tw/pdfs/acme_annual_report_2024.pdf
    dest: acme_annual_report_2024.pdf
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

使用 PDF 解析工具讀取 `acme_annual_report_2024.pdf`，萃取財務報表數據並進行以下計算，輸出 `financial_analysis_report.md`：

1. **5年營收 CAGR**：從損益表提取 2020~2024 營收，計算 CAGR = (End/Start)^(1/(n-1)) - 1
2. **DuPont 分解（2024）**：ROE = 淨利率 × 資產週轉率 × 權益乘數
   - 淨利率 = 稅後淨利/營收；資產週轉率 = 營收/平均總資產；權益乘數 = 總資產/股東權益
3. **FCF 計算**：FCF = 營業活動現金流 - 資本支出（資本支出從投資活動現金流萃取）；FCF Margin = FCF / 營收
4. **Altman Z-Score**（簡化版）：Z = 1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5
   - X1 = 營運資金/總資產
   - X2 = 保留盈餘/總資產
   - X3 = EBIT/總資產
   - X4 = 市值/總負債（若無市值，用股東權益代替）
   - X5 = 營收/總資產
   - Z > 2.99：安全；1.81~2.99：灰色區間；Z < 1.81：危險
5. 提供摘要表格和管理建議

## Expected Behavior

LLM 應使用 PDF 解析工具開啟 `acme_annual_report_2024.pdf`，從損益表、資產負債表、現金流量表萃取對應數字，並依照公式逐步計算，最終輸出結構化的 `financial_analysis_report.md`，包含至少 3 個 Markdown 表格（5年營收、DuPont 分解、Altman Z-Score 各項）以及管理建議段落。

## Grading Criteria

10 個評分 key，每個 key 通過得 1 分，滿分 10 分（automated score = 通過數 / 10）。

| Key | 說明 |
|-----|------|
| `report_created` | `financial_analysis_report.md` 檔案存在 |
| `revenue_table` | 報告中有 5 年以上的營收數字（TWD 或數值格式）|
| `cagr_calculated` | 報告中有 CAGR 百分比數值（含 % 符號）|
| `dupont_present` | ROE、淨利率、資產週轉率、權益乘數均出現 |
| `dupont_multiplication` | 提及三者相乘（乘號、×、* 或文字說明相乘）|
| `fcf_calculated` | 報告中有 FCF 數值 |
| `fcf_margin` | 報告中有 FCF Margin 百分比 |
| `altman_zscore` | 報告中有 Z-Score 數值 |
| `altman_interpretation` | 有安全/灰色/危險的 Z-Score 分類說明 |
| `has_tables` | Markdown 表格（`\|...\|` 格式）出現 >= 3 個 |


- [ ] financial_analysis_report.md 檔案存在
- [ ] 報告中有 5 年以上的營收數字（TWD 或數值格式）
- [ ] 報告中有 CAGR 百分比數值（含 % 符號）
- [ ] ROE、淨利率、資產週轉率、權益乘數均出現
- [ ] 提及三者相乘（乘號、×、* 或文字說明相乘）
- [ ] 報告中有 FCF 數值
- [ ] 報告中有 FCF Margin 百分比
- [ ] 報告中有 Z-Score 數值
- [ ] 有安全/灰色/危險的 Z-Score 分類說明
- [ ] 格式）出現 >= 3 個
## Automated Checks

```python
import re
from pathlib import Path


def grade(transcript: list, workspace_dir: str) -> dict[str, bool]:
    report_path = Path(workspace_dir) / "financial_analysis_report.md"

    results = {
        "report_created": False,
        "revenue_table": False,
        "cagr_calculated": False,
        "dupont_present": False,
        "dupont_multiplication": False,
        "fcf_calculated": False,
        "fcf_margin": False,
        "altman_zscore": False,
        "altman_interpretation": False,
        "has_tables": False,
    }

    if not report_path.exists():
        return results

    results["report_created"] = True
    text = report_path.read_text(encoding="utf-8", errors="ignore")

    # revenue_table: 至少 5 個數字出現，且包含 2020~2024 任意年份
    year_mentions = len(re.findall(r"202[0-4]", text))
    number_mentions = len(re.findall(r"\d[\d,]+(?:\.\d+)?(?:\s*(?:億|百萬|千萬|TWD|NTD|B|M))?", text))
    results["revenue_table"] = year_mentions >= 4 and number_mentions >= 10

    # cagr_calculated: 含 CAGR 字樣且附近有百分比
    cagr_match = re.search(r"CAGR[^\n]{0,60}(\d+\.?\d*)\s*%", text, re.IGNORECASE)
    if not cagr_match:
        cagr_match = re.search(r"(\d+\.?\d*)\s*%[^\n]{0,40}CAGR", text, re.IGNORECASE)
    results["cagr_calculated"] = cagr_match is not None

    # dupont_present: 四個關鍵詞都出現
    dupont_keywords = ["ROE", "淨利率", "資產週轉率", "權益乘數"]
    results["dupont_present"] = all(kw in text for kw in dupont_keywords)

    # dupont_multiplication: 含乘號或相乘說明
    mult_patterns = [r"×", r"淨利率\s*[×*×]\s*資產週轉率", r"相乘", r"三者之積", r"ROE\s*=.*×.*×"]
    results["dupont_multiplication"] = any(re.search(p, text) for p in mult_patterns)

    # fcf_calculated: FCF 後面跟數字
    fcf_match = re.search(r"FCF[^\n]{0,80}\d[\d,]+", text, re.IGNORECASE)
    if not fcf_match:
        fcf_match = re.search(r"自由現金流[^\n]{0,80}\d[\d,]+", text)
    results["fcf_calculated"] = fcf_match is not None

    # fcf_margin: FCF Margin 後面跟百分比
    fcf_margin_match = re.search(r"FCF\s*Margin[^\n]{0,60}(\d+\.?\d*)\s*%", text, re.IGNORECASE)
    if not fcf_margin_match:
        fcf_margin_match = re.search(r"(\d+\.?\d*)\s*%[^\n]{0,40}FCF\s*Margin", text, re.IGNORECASE)
    results["fcf_margin"] = fcf_margin_match is not None

    # altman_zscore: Z-Score 後面跟數字
    zscore_match = re.search(
        r"(?:Z[-\s]?Score|Z\s*=|Altman)[^\n]{0,80}(\d+\.?\d+)",
        text,
        re.IGNORECASE,
    )
    results["altman_zscore"] = zscore_match is not None

    # altman_interpretation: 安全/灰色/危險 分類
    interp_keywords = ["安全", "灰色", "危險"]
    results["altman_interpretation"] = all(kw in text for kw in interp_keywords)

    # has_tables: Markdown 表格行（含 | 分隔）出現 >= 3 個獨立表格
    table_rows = re.findall(r"^\s*\|.+\|.*$", text, re.MULTILINE)
    # 以連續行為一個表格，計算表格數量
    table_count = 0
    in_table = False
    for row in text.split("\n"):
        if re.match(r"\s*\|.+\|", row):
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
| **Data Extraction Accuracy** | 35% | PDF 表格萃取是否完整；損益表、資產負債表、現金流量表的數字是否與 PDF 來源一致；是否有明顯的數字誤讀或遺漏 |
| **Formula Application** | 30% | CAGR 公式 `(End/Start)^(1/(n-1)) - 1` 使用正確；DuPont 三因子公式正確且展示完整計算過程；FCF = 營業現金流 - 資本支出定義正確；Z-Score 五個係數(1.2/1.4/3.3/0.6/1.0)正確使用 |
| **Financial Interpretation** | 20% | CAGR 結果的成長意義是否正確詮釋；DuPont 分解揭示哪個因子是 ROE 驅動力；FCF Margin 對應行業基準的評價；Z-Score 分類是否給出管理意涵 |
| **Report Quality** | 15% | Markdown 格式規整；表格對齊清晰；段落邏輯連貫；管理建議具體可行（非泛泛而談） |

**評分指引**：
- 90~100：所有計算正確，數字有來源佐證，洞察深刻，格式無誤
- 70~89：大部分計算正確，個別數字有小誤差（< 5%），洞察基本合理
- 50~69：公式架構正確但數字錯誤較多，或缺少 1~2 個分析項目
- 30~49：多個公式應用錯誤，或大量數字無法對應 PDF 來源
- 0~29：報告嚴重不完整，核心分析缺失

## Additional Notes

- 若 PDF 中無市值數據，Z-Score X4 應使用股東權益替代，並在報告中說明此替代假設。
- 「平均總資產」應使用期初期末平均值：(2023 總資產 + 2024 總資產) / 2。
- CAGR 計算的 n = 5（年份 2020~2024），期數 n-1 = 4。
- FCF Margin 分母為當年（2024）營收。
- Altman Z-Score 臨界值適用於製造業上市公司，服務業建議註記適用性差異。
