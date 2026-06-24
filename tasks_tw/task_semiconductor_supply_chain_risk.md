---
id: task_semiconductor_supply_chain_risk
name: 半導體供應鏈風險評估
category: markdown_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/markdown/tw_semiconductor_analysis_2024.md
    dest: tw_semiconductor_analysis_2024.md
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v1
---
## Prompt

我有一份台灣半導體產業鏈深度分析報告 `tw_semiconductor_analysis_2024.md`（44KB），包含 30 家公司的財務指標、技術指標、風險指標、季度數據等多個表格。

請根據報告數據進行供應鏈風險評估，並將結果輸出至 `supply_chain_risk_report.md`。

### 第一步：建立產業鏈位置圖

從報告中識別每家公司在半導體供應鏈的層級，分類為：
- **IC設計（Fabless）**：聯發科、聯詠、瑞昱、世芯-KY 等
- **晶圓代工（Foundry）**：台積電、聯電等
- **封裝測試（OSAT）**：日月光控股、京元電等
- **PCB / 基板**：臻鼎、台光電等
- **設備 / 材料**：漢微科、環球晶等
- **系統代工（EMS/ODM）**：廣達、鴻海等

輸出各層級的公司清單。

### 第二步：台積電樞紐的上下游傳導矩陣

- 識別報告中台積電的主要上下游客戶與供應商關係
- 建立簡化矩陣：台積電 → 下游公司（封測廠）、上游公司（設備材料廠）的業務依存度估計值
- 若報告未明確揭露數字，使用合理的業界估計並標記「(估計值)」

### 第三步：情境壓力測試

**假設情境**：台積電毛利率下降 5 個百分點（模擬客戶砍單、稼動率下滑）

套用以下公式估算衝擊：

1. **封測廠（OSAT）衝擊**：
   ```
   封測廠營收衝擊% = 台積電業務依存度% × 0.70
   ```
2. **設備材料廠衝擊**：
   ```
   設備材料廠營收衝擊% = 台積電CapEx佔比% × 削減率15%
   ```

對至少 3 家相關公司計算衝擊百分比，明確說明假設值。

### 第四步：供應鏈集中度風險評分

- 從報告中提取（或估算）每家公司的「前三大客戶集中度%」和「Beta 值」
- 若 Beta 未揭露，使用行業默認值：IC設計=1.2，晶圓代工=1.0，封測=0.9，設備材料=1.1
- 計算風險分數：`供應鏈集中度風險分數 = 客戶集中度(%) × Beta`
- 分級：高風險（> 80）/ 中風險（40~80）/ 低風險（< 40）
- 對至少 10 家公司計算並排名

### 輸出報告 `supply_chain_risk_report.md` 需包含：

1. 產業鏈位置分類表（各層級公司清單）
2. 台積電上下游傳導矩陣
3. 情境壓力測試結果（至少 3 家公司的衝擊數字）
4. 供應鏈集中度風險評分排行榜（≥ 10 家）
5. 風險緩解建議（至少 3 條具體建議）

---

## Expected Behavior

代理人應執行以下步驟：

1. 解析 44KB Markdown 文件，提取多個表格的財務數據
2. 依產業鏈位置分類 30 家公司
3. 從報告的客戶/供應商相關段落推斷依存度
4. 套用情境壓力公式計算衝擊百分比（需明確說明假設值）
5. 提取或估算客戶集中度 × Beta，計算風險評分
6. 對 ≥ 10 家公司排名，三級分類

Key expected outputs：
- 應覆蓋至少 4 個產業層級
- 台積電封測依存度通常 30~60%
- 情境衝擊數字應有正負符號及百分比
- 高風險（> 80）通常是單一大客戶集中度高的公司

---

## Grading Criteria

- [ ] 輸出檔案 `supply_chain_risk_report.md` 存在
- [ ] 報告涵蓋至少 3 個產業層級的公司分類
- [ ] 報告識別至少 8 家台灣半導體相關公司
- [ ] 台積電的上下游關係有描述或矩陣
- [ ] 情境壓力測試有數字結果（至少 2 家公司的衝擊%）
- [ ] 衝擊估算有百分比數值（非零）
- [ ] 供應鏈集中度風險評分對 ≥ 5 家公司有數值
- [ ] 風險分數計算使用客戶集中度 × Beta 的概念
- [ ] 至少 3 條風險緩解建議
- [ ] 報告含 Markdown 表格（至少兩個）

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "supply_chain_risk_report.md"
    if not report_path.exists():
        for alt in ["risk_report.md", "supply_chain_report.md", "report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "supply_chain_layers": 0.0,
            "company_coverage": 0.0,
            "tsmc_relations": 0.0,
            "stress_test_present": 0.0,
            "impact_percentages": 0.0,
            "risk_scores": 0.0,
            "beta_used": 0.0,
            "risk_mitigation": 0.0,
            "has_tables": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Supply chain layers
    layer_kws = ["ic設計", "晶圓代工", "封測", "封裝", "pcb", "基板", "設備", "材料", "ems", "odm", "fabless", "foundry", "osat"]
    found_layers = sum(1 for kw in layer_kws if kw in content_lower)
    scores["supply_chain_layers"] = 1.0 if found_layers >= 5 else (0.5 if found_layers >= 3 else 0.0)

    # Company coverage
    companies = ["台積電", "tsmc", "聯發科", "日月光", "聯電", "環球晶", "漢微科",
                 "廣達", "鴻海", "京元電", "臻鼎", "瑞昱", "聯詠", "世芯"]
    found_co = sum(1 for c in companies if c.lower() in content_lower)
    scores["company_coverage"] = 1.0 if found_co >= 7 else (0.5 if found_co >= 4 else 0.0)

    # TSMC relations
    has_tsmc_context = bool(
        re.search(r'台積電|tsmc', content, re.IGNORECASE) and
        re.search(r'上游|下游|客戶|供應|upstream|downstream|customer|supplier', content_lower)
    )
    scores["tsmc_relations"] = 1.0 if has_tsmc_context else 0.0

    # Stress test present
    has_stress = bool(re.search(r'情境|scenario|壓力|stress|毛利率.*下降|毛利.*-5', content_lower))
    scores["stress_test_present"] = 1.0 if has_stress else 0.0

    # Impact percentages
    impact_pcts = re.findall(r'-?\d+\.?\d*\s*%', content)
    scores["impact_percentages"] = 1.0 if len(impact_pcts) >= 5 else (0.5 if len(impact_pcts) >= 2 else 0.0)

    # Risk scores (numbers between 10 and 200)
    risk_nums = re.findall(r'\b([1-9]\d{1,2}\.?\d*)\b', content)
    valid_risk_nums = [float(n) for n in risk_nums if 10 <= float(n) <= 200]
    scores["risk_scores"] = 1.0 if len(valid_risk_nums) >= 5 else (0.5 if len(valid_risk_nums) >= 2 else 0.0)

    # Beta used
    has_beta = bool(re.search(r'beta|貝塔|β', content, re.IGNORECASE))
    scores["beta_used"] = 1.0 if has_beta else 0.0

    # Risk mitigation (at least 3 suggestions)
    mitigation_kws = ["緩解", "建議", "分散", "多元", "避險", "降低", "mitigation", "recommend", "diversif", "reduce risk"]
    found_mit = sum(1 for kw in mitigation_kws if kw.lower() in content_lower)
    bullet_items = len(re.findall(r'^\s*[-*\d]', content, re.MULTILINE))
    scores["risk_mitigation"] = 1.0 if (found_mit >= 2 and bullet_items >= 3) else (0.5 if found_mit >= 1 else 0.0)

    # Tables
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
    scores["has_tables"] = 1.0 if len(table_rows) >= 8 else (0.5 if len(table_rows) >= 3 else 0.0)

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

---

## LLM Judge Rubric

### Criterion 1: Data Extraction from Markdown (Weight: 30%)

**Score 1.0**: Correctly reads and interprets the 44KB Markdown file. Extracts financial data from multiple tables. Company classifications align with actual industry positions. Cross-table references handled correctly.
**Score 0.75**: Most data extracted correctly; 1-2 company misclassifications.
**Score 0.5**: Partial extraction; significant portions missed or misread.
**Score 0.25**: Only reads summary text; doesn't extract tabular data.
**Score 0.0**: Does not read the file or uses fabricated data.

### Criterion 2: Stress Test Calculation (Weight: 35%)

**Score 1.0**: Applies formulas correctly to OSAT and equipment/materials companies. All assumptions are clearly stated and labeled as estimates. Impact percentages are numerically plausible (OSAT impact typically 15-40%). At least 3 companies computed.
**Score 0.75**: Formulas applied correctly for 2 company types; one type missing or calculation slightly off.
**Score 0.5**: Stress test present but formula not followed (e.g., uses ad-hoc numbers without formula).
**Score 0.25**: Only qualitative description of impact; no quantitative calculation.
**Score 0.0**: No stress test performed.

### Criterion 3: Risk Scoring System (Weight: 20%)

**Score 1.0**: Customer concentration × Beta computed for ≥ 10 companies. Industry default Betas used correctly when not disclosed. Three-tier classification (high/mid/low) applied correctly.
**Score 0.75**: 6-9 companies scored; classification thresholds correctly applied.
**Score 0.5**: 3-5 companies scored; one dimension (concentration or Beta) missing.
**Score 0.25**: Only qualitative risk description; no quantitative scoring.
**Score 0.0**: No risk scoring.

### Criterion 4: Mitigation Quality (Weight: 15%)

**Score 1.0**: At least 3 specific, actionable recommendations tied to identified risks (e.g., "高集中度公司應將最大客戶佔比控制在 40% 以下"). Recommendations differentiate between company types.
**Score 0.75**: 3 recommendations present but somewhat generic.
**Score 0.5**: 1-2 specific recommendations or 3 very generic ones.
**Score 0.25**: Only mentions risk without suggesting mitigation.
**Score 0.0**: No mitigation recommendations.

---

## Additional Notes

This task tests:
- Complex Markdown parsing with multiple table formats
- Supply chain domain knowledge (semiconductor industry structure)
- Scenario-based financial modeling with explicit assumptions
- Risk quantification combining two variables
- Reading 44KB document without truncation

Key challenges:
- The source document has many tables with different column structures — must handle each correctly
- Customer concentration data may be scattered across different sections
- Beta values may not be explicitly listed — must use industry defaults from the prompt
- Stress test requires clear documentation of ALL assumptions used
- Stronger models will correctly distinguish OSAT impact formula from equipment/materials formula
