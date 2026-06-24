---
id: task_cross_format_business_intelligence
name: 跨格式 BI：PPTX 策略 × TXT 供應鏈危機整合壓力測試
category: cross_format_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/pptx/ai_strategy_deck_2024.pptx
    dest: ai_strategy_deck_2024.pptx
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

同時讀取兩個資料來源：(1) `ai_strategy_deck_2024.pptx`（NovaTech 的 AI 策略簡報）和 (2) `supply_chain_incident_report.txt`（GlobalChip 供應鏈危機報告），進行整合分析，輸出 `integrated_risk_assessment.md`。

**重要背景**：NovaTech 在危機報告中被列為受影響公司之一（見 Section 2），其 Q3 2024 受到供應鏈衝擊。

1. **財務預測萃取**：從 PPTX 萃取 NovaTech FY2024～FY2027 的財務預測（Revenue、Net Income、Gross Margin）
2. **危機衝擊係數計算**：從 TXT 找出 NovaTech 的具體衝擊數字（Revenue Impact、Days Delayed）。計算「衝擊係數」= Revenue Impact / Q3 Projected Revenue
3. **壓力測試**：假設類似危機以 25% 的年度機率發生，對 NovaTech 的 FY2024～FY2027 財務預測進行調整：
   - 調整後收入 = 原始收入 × (1 - 0.25 × 衝擊係數)
   - 調整後 Net Income = 調整後收入 × Net Income Margin（保持 margin 不變）
4. **風險缺口分析**：對照 PPTX 的風險矩陣，NovaTech 的風險矩陣是否已涵蓋供應鏈風險？（Speaker Notes 有提示缺口）
5. **策略建議**：基於壓力測試結果和風險缺口，提出 3 條具體改善建議（引用兩份文件的具體數字）

### 輸出格式

輸出檔案：`integrated_risk_assessment.md`

結構如下：
```markdown
# NovaTech 整合風險評估報告：AI 策略 × 供應鏈危機壓力測試
### 一、財務預測萃取（來源：PPTX）
### 二、危機衝擊係數計算（來源：TXT）
### 三、壓力測試：調整後財務預測 FY2024～FY2027
### 四、風險缺口分析
### 五、策略建議
### 附錄：數據來源對照
```

報告撰寫要求：
- 「財務預測萃取」需以 Markdown 表格列出 FY2024～FY2027 的 Revenue（TWD／新台幣）、Net Income、Gross Margin
- 「危機衝擊係數計算」需引用 TXT 中的 USD 衝擊金額與延遲天數，並寫出衝擊係數的計算式與結果
- 「壓力測試」需以表格列出四年的調整後收入與調整後 Net Income，並標明所用公式
- 「風險缺口分析」需明確指出 PPTX 風險矩陣是否涵蓋供應鏈風險，並引用 Speaker Notes（投影片備忘錄）作為證據
- 「策略建議」需以編號列表給出 3 條建議，每條皆引用兩份文件的具體數字
- 全文至少包含 2 個 Markdown 表格，並在附錄標注每項數據的來源檔案

---

## Expected Behavior

代理人應執行以下步驟：

1. 解析 `ai_strategy_deck_2024.pptx`，萃取 NovaTech FY2024～FY2027 的 Revenue、Net Income、Gross Margin（以 TWD／新台幣計），並讀取投影片的 Speaker Notes（備忘錄）。
2. 解析 `supply_chain_incident_report.txt`，找出 NovaTech 的 Revenue Impact（USD）與 Days Delayed，以及 Q3 Projected Revenue。
3. 計算衝擊係數 = Revenue Impact / Q3 Projected Revenue（注意 TWD 與 USD 的單位對照與換算一致性）。
4. 以 25% 年度機率進行壓力測試：調整後收入 = 原始收入 × (1 - 0.25 × 衝擊係數)；調整後 Net Income = 調整後收入 × Net Income Margin（margin 維持不變），四年皆需計算。
5. 對照 PPTX 風險矩陣與 Speaker Notes，判斷供應鏈風險是否被涵蓋，識別風險缺口並引用備忘錄證據。
6. 綜合壓力測試與風險缺口，提出 3 條具體且可操作的策略建議，引用兩份文件數字。
7. 輸出結構完整、含至少 2 個 Markdown 表格的 `integrated_risk_assessment.md`，並在附錄標注數據來源。

---

## Grading Criteria

- [ ] 輸出檔案 `integrated_risk_assessment.md` 存在
- [ ] 引用 PPTX 的 NovaTech 財務數字（TWD／新台幣 + 營收／淨利／毛利）
- [ ] 引用 TXT 的 USD 衝擊金額（從危機報告擷取）
- [ ] 計算並呈現衝擊係數（係數或百分比結果）
- [ ] 報告中出現「壓力測試」分析
- [ ] 呈現調整後收入（調整後 / adjusted revenue）
- [ ] 識別供應鏈風險缺口
- [ ] 引用 Speaker Notes（投影片備忘錄）作為證據
- [ ] 提出 3 條具體策略建議（編號列表）
- [ ] 報告至少包含 2 個 Markdown 表格

---

## Automated Checks

```python
import re
from pathlib import Path

def grade(transcript: list, submission_dir: str) -> dict:
    report_path = Path(submission_dir) / "integrated_risk_assessment.md"
    if not report_path.exists():
        return {"score": 0, "max_score": 10, "details": "未找到 integrated_risk_assessment.md", "passed": False}

    text = report_path.read_text(encoding="utf-8")
    checks = {}

    # 1. report_created
    checks["report_created"] = True

    # 2. pptx_data_used: 有 NovaTech 財務數字（TWD 或新台幣數字）
    checks["pptx_data_used"] = bool(
        re.search(r"(TWD|NTD|NT\$|新台幣|億元)", text, re.IGNORECASE) and
        re.search(r"(Revenue|Net Income|Gross Margin|營收|淨利|毛利)", text, re.IGNORECASE)
    )

    # 3. txt_data_used: 有 USD 衝擊金額（從 TXT 擷取）
    checks["txt_data_used"] = bool(
        re.search(r"USD", text, re.IGNORECASE) and
        re.search(r"\$[\d,\.]+[MBmb]?|\d[\d,]{4,}", text)
    )

    # 4. impact_coefficient: 有衝擊係數或百分比計算結果
    checks["impact_coefficient"] = bool(
        re.search(r"(衝擊係數|impact.{0,20}coefficient|impact.{0,20}ratio)", text, re.IGNORECASE) or
        re.search(r"(係數|coefficient).{0,60}\d+\.?\d*\s*%?", text, re.IGNORECASE)
    )

    # 5. stress_test_present: 壓力測試詞出現
    checks["stress_test_present"] = bool(
        re.search(r"(壓力測試|stress.?test)", text, re.IGNORECASE)
    )

    # 6. adjusted_revenue: 有調整後數字（調整後收入或 adjusted revenue）
    checks["adjusted_revenue"] = bool(
        re.search(r"(調整後|adjusted).{0,30}(收入|revenue|营收)", text, re.IGNORECASE) or
        re.search(r"(收入|revenue).{0,30}(調整後|adjusted)", text, re.IGNORECASE)
    )

    # 7. risk_gap_identified: 供應鏈風險缺口被識別
    checks["risk_gap_identified"] = bool(
        re.search(r"(風險缺口|risk.{0,10}gap|供應鏈.{0,20}風險.{0,20}(未|缺|遺漏|missing))", text, re.IGNORECASE) or
        re.search(r"(supply.?chain.{0,20}risk.{0,20}(gap|missing|not.{0,10}covered))", text, re.IGNORECASE) or
        (re.search(r"(供應鏈|supply.?chain)", text, re.IGNORECASE) and
         re.search(r"(缺口|gap|遺漏|未涵蓋|not covered|missing)", text, re.IGNORECASE))
    )

    # 8. speaker_notes_evidence: 引用 speaker notes 的內容
    checks["speaker_notes_evidence"] = bool(
        re.search(r"(speaker.?notes?|備註|備注|演講者備忘|notes?.{0,10}(mention|indicate|state|say|show))",
                  text, re.IGNORECASE)
    )

    # 9. three_recommendations: 有 3 條建議（檢查數字列表 1. 2. 3. 或 一、二、三）
    numbered = re.findall(r"(^|\n)\s*[（(]?[1-3一二三][）)\.、]\s*.{10,}", text)
    checks["three_recommendations"] = len(numbered) >= 3 and bool(
        re.search(r"(建議|recommendation|suggest)", text, re.IGNORECASE)
    )

    # 10. has_tables: 表格 >= 2（markdown 表格分隔線）
    table_separators = re.findall(r"^\|[-| :]+\|", text, re.MULTILINE)
    checks["has_tables"] = len(table_separators) >= 2

    passed_count = sum(1 for v in checks.values() if v)
    score = passed_count

    details_lines = []
    for key, val in checks.items():
        icon = "✅" if val else "❌"
        details_lines.append(f"{icon} {key}")

    if checks["three_recommendations"]:
        details_lines.append(f"   → found {len(numbered)} numbered item(s) near recommendations")
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
| **Cross-File Integration** | 35% | 是否正確從兩個不同格式的文件提取並對照 NovaTech 的數據；PPTX 財務數字（TWD）與 TXT 衝擊數字（USD）是否均有引用且來源標注清楚 |
| **Stress Test Rigor** | 30% | 衝擊係數計算是否正確（= Revenue Impact / Q3 Projected Revenue）；調整後財務數字是否符合公式（原始收入 × (1 - 0.25 × 衝擊係數)）；FY2024～FY2027 四年均需計算 |
| **Risk Analysis** | 20% | 風險缺口識別是否基於文件證據（特別是 Speaker Notes 提到的供應鏈風險遺漏）；是否明確指出 PPTX 風險矩陣的不足之處 |
| **Strategic Recommendations** | 15% | 三條建議是否具體（有數字支撐）且引用了兩份文件的內容；建議是否有可操作性 |

> LLM Judge 總權重加總：35 + 30 + 20 + 15 = 100%

---

## Additional Notes

核心考驗：

- **跨格式資料讀取**：同時解析 PPTX（含 Speaker Notes）和純文字 TXT 兩種格式
- **跨文件數據對照**：NovaTech 在兩份文件中均有數據，需正確匹配並換算（TWD vs. USD）
- **多步驟財務計算**：衝擊係數 → 調整機率加權 → 四年財務預測調整，每步均需正確
- **Speaker Notes 解讀**：需主動讀取 PPTX 投影片備忘錄以識別風險缺口
- **整合敘事**：將兩份不同來源、不同語言的文件整合為一份有邏輯的風險評估報告
