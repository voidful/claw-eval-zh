---
id: task_supply_chain_timeline_analysis
name: 供應鏈危機事件時序重建與財務量化
category: txt_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/txt/supply_chain_incident_report.txt
    dest: supply_chain_incident_report.txt
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v2
---
## Prompt

請分析 `supply_chain_incident_report.txt`（GlobalChip Crisis Q3 2024 供應鏈危機報告），並產出 `supply_chain_analysis_report.md`，內容需包含以下五項分析：

1. **事件時序重建（Event Timeline Reconstruction）**：擷取報告中所有帶日期的事件，計算連續事件之間相隔的天數，並找出「危機升溫點（crisis escalation points）」（任何 7 天視窗內出現 3 件以上事件者）。
2. **財務衝擊量化（Financial Impact Quantification）**：擷取報告中所有美元金額（USD），分類為：(a) 各公司的直接營收衝擊、(b) 保險理賠、(c) 市場/股價影響。加總出總額，並計算每家公司的平均衝擊。
3. **公司曝險評分（Company Exposure Scoring）**：對 20 家具名公司逐一計算「曝險分數」＝ (revenue_impact_USD_M / Q3_projected_revenue_USD_M) × 100 + (days_delayed × 0.5)，並依曝險分數排名。
4. **恢復速度分析（Recovery Speed Analysis）**：對有明確恢復日期的公司，計算自觸發事件（7 月 12 日）起算的恢復天數，找出恢復最快與最慢的公司。
5. **ASCII 時間軸視覺化（ASCII Timeline Visualization）**：以純文字字元繪製一條水平時間軸，呈現 20 個關鍵事件，並以 `[!!!]` 標記危機升溫點。

### 輸出格式

輸出檔案：`supply_chain_analysis_report.md`

報告結構如下（請使用對應的 Markdown 標題，並在各節填入分析結果）：

```markdown
# GlobalChip Crisis Q3 2024 — Supply Chain Analysis Report
### 1. Event Timeline Reconstruction
### 2. Financial Impact Quantification
### 3. Company Exposure Scoring
### 4. Recovery Speed Analysis
### 5. ASCII Timeline Visualization
### 6. Key Findings & Lessons Learned
```

要求說明：

- 日期請使用 `2024-MM-DD` 格式，至少呈現 10 個以上的日期。
- 天數請以「N days」或「N 天」形式標示。
- 財務數字請保留原文中的 USD 金額（如 `$XXM`），並標明加總總額。
- 至少要在報告中呈現 10 家以上具名公司。
- 曝險分數與恢復天數需附上實際計算的數值，並指出恢復最快的公司。
- 至少使用 2 個 Markdown 表格來整理時序、財務或曝險資料。
- 所有數字必須來自報告原文，不得自行編造。

---

## Expected Behavior

代理人應執行以下步驟：

1. 逐段讀取 `supply_chain_incident_report.txt`，解析出所有帶日期的事件與其敘述。
2. 計算連續事件之間的天數差，並以 7 天滑動視窗偵測 3 件以上事件聚集的危機升溫點。
3. 以 regex 擷取所有 USD 金額，依直接營收衝擊、保險理賠、市場/股價影響分類並加總，計算每家公司平均衝擊。
4. 對 20 家具名公司套用曝險分數公式 (revenue_impact / Q3_projected × 100 + days_delayed × 0.5)，並排名。
5. 找出有明確恢復日期的公司，計算自 7 月 12 日觸發事件起算的恢復天數，比較最快與最慢者。
6. 以純文字字元繪製水平 ASCII 時間軸，並用 `[!!!]` 標記危機升溫點。
7. 輸出結構完整、含至少 2 個 Markdown 表格的報告 `supply_chain_analysis_report.md`。

Key expected values（近似）：

- 帶日期事件至少 10 個以上（`2024-XX-XX` 格式）。
- 具名公司至少 10 家以上（總共 20 家）。
- 財務加總應為百萬美元級別（USD millions）。
- 恢復天數與曝險分數應與報告原文一致，不出現自相矛盾的數字。

---

## Grading Criteria

- [ ] 輸出檔案 `supply_chain_analysis_report.md` 存在
- [ ] 時序中擷取出至少 10 個 `2024-XX-XX` 格式日期
- [ ] 報告含有事件間隔天數（如 `47 days` 或 `47 天`）
- [ ] 財務加總含 USD 與百萬級大數字
- [ ] 報告中出現至少 10 家具名公司
- [ ] 呈現曝險分數（exposure / score 加數值）
- [ ] 含有恢復相關天數（recovery days）
- [ ] 指出恢復最快的公司名稱（fastest / quickest / 最快）
- [ ] 含 ASCII 時間軸視覺化（連續字元或 `[!!!]` 標記）
- [ ] 報告至少包含 2 個 Markdown 表格

---

## Automated Checks

```python
import re
from pathlib import Path

def grade(transcript: list, submission_dir: str) -> dict:
    report_path = Path(submission_dir) / "supply_chain_analysis_report.md"
    if not report_path.exists():
        return {"score": 0, "max_score": 10, "details": "未找到 supply_chain_analysis_report.md", "passed": False}

    text = report_path.read_text(encoding="utf-8")
    checks = {}

    # 1. report_created
    checks["report_created"] = True

    # 2. timeline_extracted: 有 2024-0x-xx 格式日期 >= 10 個
    dates = re.findall(r"2024-\d{2}-\d{2}", text)
    checks["timeline_extracted"] = len(dates) >= 10

    # 3. days_computed: 有天數數字，例如 "47 days" 或 "47 天"
    checks["days_computed"] = bool(re.search(r"\d+\s*(days|天)", text, re.IGNORECASE))

    # 4. financial_totals: 有 USD 加上大數字（百萬以上）
    checks["financial_totals"] = bool(
        re.search(r"USD", text, re.IGNORECASE) and
        re.search(r"\$[\d,]+[MBmb]|\d[\d,]{5,}", text)
    )

    # 5. company_count: 有 >= 10 家公司名稱（大寫開頭連續詞或常見公司詞）
    company_candidates = re.findall(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}\b", text)
    unique_companies = set(company_candidates)
    # 過濾常見非公司單詞
    stopwords = {"The", "This", "That", "These", "Those", "For", "With", "From", "And", "But",
                 "USD", "July", "August", "September", "October", "November", "December",
                 "January", "February", "March", "April", "May", "June", "Key", "Total",
                 "Section", "Table", "Figure", "Crisis", "Supply", "Chain", "Recovery",
                 "Analysis", "Report", "Timeline", "Financial", "Impact", "Company",
                 "ASCII", "Event", "Days", "Score", "Revenue", "Exposure", "Fastest", "Slowest"}
    filtered = [c for c in unique_companies if c not in stopwords and len(c) > 3]
    checks["company_count"] = len(filtered) >= 10

    # 6. exposure_score_present: 有 "exposure" 或 "score" 加數字
    checks["exposure_score_present"] = bool(
        re.search(r"(exposure|score)\D{0,20}\d+\.?\d*", text, re.IGNORECASE)
    )

    # 7. recovery_days: 有 recovery 相關天數
    checks["recovery_days"] = bool(
        re.search(r"recover\w*\D{0,30}\d+\s*(days|天)", text, re.IGNORECASE) or
        re.search(r"\d+\s*(days|天)\D{0,30}recover", text, re.IGNORECASE)
    )

    # 8. fastest_recovery: 有最快恢復的公司名稱（fastest 或 quickest 附近有大寫詞）
    checks["fastest_recovery"] = bool(
        re.search(r"(fastest|quickest|最快)\D{0,60}[A-Z][A-Za-z]+", text, re.IGNORECASE) or
        re.search(r"[A-Z][A-Za-z]+\D{0,60}(fastest|quickest|最快)", text, re.IGNORECASE)
    )

    # 9. ascii_timeline: 有 ASCII 字符如 = 或 | 組成的視覺化（連續 >= 5 個）
    checks["ascii_timeline"] = bool(
        re.search(r"[=|]{5,}", text) or
        re.search(r"[-]{10,}", text) or
        re.search(r"\[!!!\]", text)
    )

    # 10. has_tables: 表格 >= 2（以 markdown 表格分隔線計算）
    table_separators = re.findall(r"^\|[-| :]+\|", text, re.MULTILINE)
    checks["has_tables"] = len(table_separators) >= 2

    passed_count = sum(1 for v in checks.values() if v)
    score = passed_count

    details_lines = []
    for key, val in checks.items():
        icon = "✅" if val else "❌"
        details_lines.append(f"{icon} {key}")

    if checks["timeline_extracted"]:
        details_lines.append(f"   → found {len(dates)} dates with format 2024-XX-XX")
    if checks["company_count"]:
        details_lines.append(f"   → found {len(filtered)} candidate company tokens")
    if checks["has_tables"]:
        details_lines.append(f"   → found {len(table_separators)} markdown table(s)")

    return {
        "score": score,
        "max_score": 10,
        "passed": passed_count >= 7,
        "checks": checks,
        "details": "\n".join(details_lines),
    }


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

---

## LLM Judge Rubric

| 維度 | 權重 | 評分說明 |
|------|------|----------|
| **Data Extraction Accuracy** | 35% | 數字是否從報告中正確提取（不能編造）；USD 金額、日期、公司名稱必須與原文一致 |
| **Quantitative Analysis** | 30% | 曝險分數公式是否正確應用（revenue_impact / Q3_projected × 100 + days_delayed × 0.5）；加總是否一致且無矛盾 |
| **Timeline Reconstruction** | 20% | 時序是否完整有序；ASCII 視覺化是否清晰並標記 [!!!] 危機升溫點 |
| **Insight Quality** | 15% | 是否識別出危機模式（如多事件聚集視窗）和關鍵教訓，並提供可操作建議 |

> LLM Judge 總權重加總：35 + 30 + 20 + 15 = 100%

---

## Additional Notes

本任務的核心考驗：

- **大型 TXT 跨段落數字萃取**：需從長篇報告中精確抓取所有 USD 金額與日期。
- **時序重建與視窗偵測**：計算連續事件日期差，識別 7 天內 3+ 事件的危機升溫期。
- **多公式量化計算**：曝險分數涉及兩個數值來源的比值計算。
- **ASCII 視覺化**：需用純文字字元呈現時間軸，標記關鍵節點。
- **恢復速度對比**：需從報告中找出明確恢復日期並計算距觸發事件的天數。
