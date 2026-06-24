---
id: task_pptx_strategy_evaluation
name: "PPTX 策略簡報評估與一致性驗證"
category: pptx_analysis
difficulty: medium
timeout_seconds: 600
workspace_files:
  - source: tw/pptx/ai_strategy_deck_2024.pptx
    dest: ai_strategy_deck_2024.pptx
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

使用 PPTX 解析工具讀取 `ai_strategy_deck_2024.pptx`（NovaTech 的 AI 策略簡報），進行策略評估，輸出 `strategy_evaluation_report.md`：

1. **財務數字萃取與一致性驗證**：
   - 從投影片提取所有財務數字（FY2024~FY2027 營收、EBITDA margin、Net Income、投資金額）
   - 驗算：投資細項加總是否等於總投資 TWD 3.6B？
   - 驗算：FY2024E Net Income = 4.20B × 18% × (1 - 有效稅率) 是否與 0.63B 自洽？
   - 驗算：FY2024→FY2027 CAGR 是否等於簡報宣稱的 35%（或計算真實 CAGR）
2. **競爭對手威脅指數**：從 Competitive Landscape 投影片萃取 5 家對手的優劣勢，計算：威脅指數 = 優勢數量 / (優勢 + 劣勢) × 市占率%
3. **風險矩陣完整性**：統計高/中/低風險各幾項，識別「供應鏈風險」是否被涵蓋（Speaker Notes 有提示）
4. **Speaker Notes 關鍵假設萃取**：從所有投影片的 Speaker Notes 提取關鍵假設和行動項目
5. **技術路線圖里程碑密度**：每季有幾個里程碑？識別關鍵路徑

## Expected Behavior

LLM 應使用 PPTX 解析工具逐頁讀取投影片正文及 Speaker Notes，正確識別各投影片的主題（財務、競爭分析、風險、路線圖），執行數字驗算並明確指出一致或矛盾之處，最終輸出結構化的 `strategy_evaluation_report.md`，包含至少 2 個 Markdown 表格，並對每項驗算給出明確結論（✓ 自洽 / ✗ 矛盾）。

## Grading Criteria

10 個評分 key，每個 key 通過得 1 分，滿分 10 分（automated score = 通過數 / 10）。

| Key | 說明 |
|-----|------|
| `report_created` | `strategy_evaluation_report.md` 檔案存在 |
| `financial_numbers_extracted` | 報告中有 TWD 數字（含 B/億/百萬等單位）|
| `investment_verified` | 報告提及 3.6B 總投資或各分類投資項目 |
| `cagr_calculated` | 報告中有 CAGR 百分比數值 |
| `competitor_analysis` | 報告中提及至少 5 家競爭對手（可為公司名、代號、或 Competitor A~E）|
| `threat_index` | 報告中有威脅指數相關數字（小數或百分比）|
| `risk_matrix_counted` | 高/中/低風險各有數量統計 |
| `supply_chain_risk_noted` | 提及供應鏈風險缺失或供應鏈相關風險 |
| `speaker_notes_used` | 報告中明確引用或提及 Speaker Notes 的內容 |
| `has_tables` | Markdown 表格（`\|...\|` 格式）出現 >= 2 個 |


- [ ] strategy_evaluation_report.md 檔案存在
- [ ] 報告中有 TWD 數字（含 B/億/百萬等單位）
- [ ] 報告提及 3.6B 總投資或各分類投資項目
- [ ] 報告中有 CAGR 百分比數值
- [ ] 報告中提及至少 5 家競爭對手（可為公司名、代號、或 Competitor A~E）
- [ ] 報告中有威脅指數相關數字（小數或百分比）
- [ ] 高/中/低風險各有數量統計
- [ ] 提及供應鏈風險缺失或供應鏈相關風險
- [ ] 報告中明確引用或提及 Speaker Notes 的內容
- [ ] 格式）出現 >= 2 個
## Automated Checks

```python
import re
from pathlib import Path


def grade(transcript: list, workspace_dir: str) -> dict[str, bool]:
    report_path = Path(workspace_dir) / "strategy_evaluation_report.md"

    results = {
        "report_created": False,
        "financial_numbers_extracted": False,
        "investment_verified": False,
        "cagr_calculated": False,
        "competitor_analysis": False,
        "threat_index": False,
        "risk_matrix_counted": False,
        "supply_chain_risk_noted": False,
        "speaker_notes_used": False,
        "has_tables": False,
    }

    if not report_path.exists():
        return results

    results["report_created"] = True
    text = report_path.read_text(encoding="utf-8", errors="ignore")

    # financial_numbers_extracted: TWD 數字（含單位）
    fin_match = re.search(
        r"(?:TWD|NTD|NT\$|\$|億|百萬|十億)[^\n]{0,20}\d[\d,.]+|"
        r"\d[\d,.]+\s*(?:TWD|NTD|B|M|億|百萬|十億)",
        text,
        re.IGNORECASE,
    )
    results["financial_numbers_extracted"] = fin_match is not None

    # investment_verified: 提及 3.6B 或分類投資
    invest_match = re.search(r"3\.6\s*(?:B|億|billion|十億)", text, re.IGNORECASE)
    if not invest_match:
        invest_match = re.search(r"(?:總投資|投資總額|total\s*invest)[^\n]{0,60}\d[\d,.]+", text, re.IGNORECASE)
    results["investment_verified"] = invest_match is not None

    # cagr_calculated: CAGR + 百分比
    cagr_match = re.search(r"CAGR[^\n]{0,60}(\d+\.?\d*)\s*%", text, re.IGNORECASE)
    if not cagr_match:
        cagr_match = re.search(r"(\d+\.?\d*)\s*%[^\n]{0,40}CAGR", text, re.IGNORECASE)
    results["cagr_calculated"] = cagr_match is not None

    # competitor_analysis: 5 家以上競爭對手（公司名或 Competitor A~E / 代號）
    competitor_patterns = [
        r"Competitor\s*[A-E]",
        r"競爭者[A-E甲乙丙丁戊]",
        r"(?:Google|Microsoft|Amazon|Apple|Meta|Alibaba|Baidu|Tencent|OpenAI|AWS)",
    ]
    competitor_count = 0
    for p in competitor_patterns:
        found = set(re.findall(p, text, re.IGNORECASE))
        competitor_count += len(found)
    # 若有「5家」「五家」等描述也算
    if competitor_count < 5:
        if re.search(r"(?:5|五)\s*(?:家|個|competitors)", text, re.IGNORECASE):
            competitor_count = 5
    results["competitor_analysis"] = competitor_count >= 5

    # threat_index: 威脅指數數字（小數或百分比）
    threat_match = re.search(
        r"(?:威脅指數|threat\s*index)[^\n]{0,80}(?:0\.\d+|\d+\.?\d*\s*%)",
        text,
        re.IGNORECASE,
    )
    if not threat_match:
        threat_match = re.search(
            r"(?:0\.\d+|\d+\.?\d*\s*%)[^\n]{0,40}(?:威脅指數|threat\s*index)",
            text,
            re.IGNORECASE,
        )
    results["threat_index"] = threat_match is not None

    # risk_matrix_counted: 高/中/低風險 + 數量
    risk_high = re.search(r"高(?:風險|risk)[^\n]{0,40}\d+|(?:\d+)[^\n]{0,40}高(?:風險|risk)", text, re.IGNORECASE)
    risk_mid = re.search(r"中(?:風險|risk)[^\n]{0,40}\d+|(?:\d+)[^\n]{0,40}中(?:風險|risk)", text, re.IGNORECASE)
    risk_low = re.search(r"低(?:風險|risk)[^\n]{0,40}\d+|(?:\d+)[^\n]{0,40}低(?:風險|risk)", text, re.IGNORECASE)
    results["risk_matrix_counted"] = all([risk_high, risk_mid, risk_low])

    # supply_chain_risk_noted: 供應鏈風險相關
    supply_chain_match = re.search(
        r"供應鏈[^\n]{0,40}(?:風險|缺失|missing|未涵蓋|not\s*covered|遺漏)|"
        r"(?:supply\s*chain)[^\n]{0,40}(?:risk|missing|缺失)",
        text,
        re.IGNORECASE,
    )
    results["supply_chain_risk_noted"] = supply_chain_match is not None

    # speaker_notes_used: 提及 speaker notes 內容
    notes_match = re.search(
        r"(?:speaker\s*notes?|備忘錄|演講者備註|講者備註|notes?\s*中)[^\n]{0,80}\S",
        text,
        re.IGNORECASE,
    )
    results["speaker_notes_used"] = notes_match is not None

    # has_tables: 獨立表格數量 >= 2
    table_count = 0
    in_table = False
    for line in text.split("\n"):
        if re.match(r"\s*\|.+\|", line):
            if not in_table:
                table_count += 1
                in_table = True
        else:
            in_table = False
    results["has_tables"] = table_count >= 2

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
| **Data Extraction from PPTX** | 30% | 是否正確讀取多頁投影片正文；Speaker Notes 是否被讀取並引用；圖表中的數字是否被萃取（如圖表標籤、bar chart 數值）；投影片頁碼/標題是否有對應 |
| **Financial Verification** | 35% | 投資細項加總驗算是否執行（是否明確計算並比對 3.6B）；Net Income 反推有效稅率是否合理；FY2024→FY2027 CAGR 是否正確計算（公式使用正確）；對矛盾之處是否明確指出 ✗，對自洽之處是否確認 ✓ |
| **Strategic Analysis** | 20% | 5 家競爭對手的威脅指數是否有邏輯依據；風險矩陣分析是否識別缺口（如供應鏈風險遺漏）；技術路線圖里程碑分析是否識別關鍵路徑瓶頸 |
| **Report Quality** | 15% | Markdown 格式規整；數字驗算有清楚的計算過程展示；結論明確可操作；競爭分析表格清晰 |

**評分指引**：
- 90~100：所有驗算正確且明確標示一致性結論，競爭分析有量化威脅指數，風險缺口識別準確
- 70~89：主要驗算完成，個別計算有小誤，競爭分析基本完整
- 50~69：財務驗算有缺漏（如未計算 CAGR），或競爭分析停留在文字描述
- 30~49：多個核心驗算缺失，或嚴重依賴推測而非 PPTX 原文
- 0~29：報告嚴重不完整，基本未執行驗算任務

## Additional Notes

- CAGR 計算：FY2024→FY2027 共 3 個期間，CAGR = (FY2027/FY2024)^(1/3) - 1。
- Net Income 驗算：若有效稅率未明確標示，應從 Net Income / EBIT 反推，並在報告中說明假設。
- 投資細項加總驗算：應列出各細項金額及加總值，明確指出是否等於 3.6B。
- 供應鏈風險：即使簡報未提及，也應標注此風險缺口（Speaker Notes 中有提示）。
- 威脅指數公式：若對手無市占率數據，可設為 1（等權重），並說明此假設。
