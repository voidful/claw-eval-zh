---
id: task_csv_pension_liability
name: 美國退休金負債分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_pension_liability
source_benchmark: pinchbench
claw_eval_id: P077zh_csv_pension_liability
workspace_files:
- source: csvs/us_pension_by_state.csv
  dest: us_pension_by_state.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 美國退休金負債分析

## Prompt

我的工作區裡有一個 CSV 檔案 `us_pension_by_state.csv`，內含按州與國會選區細分的美國聯邦退休金給付資料。欄位如下：

- `STATE_ABBREV_NAME` — 州縮寫與名稱（例如州總計列為 "OH-OHIO Total"）
- `DISTRICT` — 國會選區號碼、"At Large" 或年份
- `PAYEE_AMOUNT` — 給付給目前退休人員的總金額（以 $ 與逗號格式化）
- `PAYEE_COUNT` — 目前領取者人數
- `DEFERRED_COUNT` — 遞延（未來）領取者人數，尚未開始請領給付

以 "Total" 結尾的列為州級彙總。第一列是 Grand Total。

請分析退休金負債曝險（liability exposure），並把你的發現寫到 `pension_liability_report.md`。你的報告應包含：

- 每個州的**每位領取者平均給付（average payout per payee）**——依此指標將前 10 大州排名
- 各州的**遞延總人數（total deferred count by state）**——將遞延（未來）領取者最多的前 10 大州排名
- **預估未來負債（projected future liability）**：對每個州，以該州的每位領取者平均給付乘以其遞延人數，估算未來年度負債。依此預估負債將前 10 大州排名。
- **全國摘要（national summary）**：目前年度給付總額、目前領取者總數、遞延領取者總數、整體每位領取者平均給付，以及若所有遞延領取者皆以目前平均水準請領時的預估未來負債總額
- 一段簡短的**分析**：說明哪些州代表最大的未來財務曝險，以及原因

請注意：預估未來負債是一個估計值，它假設遞延領取者未來將以與目前領取者相同的平均水準請領。強的回應應指出此假設及其限制。

## Expected Behavior

助手應該：

1. 解析 CSV，去除美元格式與逗號
2. 計算每個州的每位領取者平均給付（PAYEE_AMOUNT / PAYEE_COUNT）
3. 依平均給付排名各州——Colorado（~$9,711）、Hawaii（~$9,643）、Washington（~$9,224）居前
4. 依遞延人數排名各州——New York（40,592）、California（35,564）、Pennsylvania（34,285）居前
5. 計算每個州的預估負債（平均給付 × 遞延人數）
6. 回報全國總計：~$5.71B 目前、877,305 名領取者、483,720 遞延、~$6,510 平均
7. 計算預估未來負債總額：~$6,510 × 483,720 = ~$3.15B

關鍵預期數值：

- 整體平均給付：每位領取者 ~$6,510
- 平均給付最高：Colorado（~$9,711/領取者）、Hawaii（~$9,643/領取者）、Washington（~$9,224/領取者）
- 遞延最多：New York（40,592）、California（35,564）、Pennsylvania（34,285）
- 預估負債前段：New York、California、Ohio、Pennsylvania（高遞延人數 × 中至高平均給付）
- 全國預估未來負債：~$3.15B

## Grading Criteria

- [ ] 已建立報告檔案 `pension_liability_report.md`
- [ ] 已計算每位領取者平均給付並列出前 10 大州
- [ ] 已指出 Colorado 為平均給付最高（~$9,711）
- [ ] 已列出依遞延人數排名的前 10 大州
- [ ] 已指出 New York 為遞延人數最多（40,592）
- [ ] 已逐州計算預估未來負債
- [ ] 全國摘要含總金額、領取者、遞延與整體平均
- [ ] 已估算預估未來負債總額（~$3.15B）
- [ ] 已提供財務曝險分析

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the pension liability analysis task.

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
    report_path = workspace / "pension_liability_report.md"
    if not report_path.exists():
        alternatives = ["liability_report.md", "report.md", "pension_report.md", "pension_liability.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "avg_payout_ranking": 0.0,
            "colorado_highest_avg": 0.0,
            "deferred_ranking": 0.0,
            "ny_highest_deferred": 0.0,
            "projected_liability": 0.0,
            "national_summary": 0.0,
            "total_projected": 0.0,
            "exposure_analysis": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Average payout ranking — check if top states mentioned with avg context
    avg_states = ["colorado", "hawaii", "washington", "nevada", "wyoming", "montana"]
    avg_mentioned = sum(1 for s in avg_states if s in content_lower)
    has_avg_context = bool(re.search(r'(?:average|avg|per\s*payee|per\s*recipient)', content_lower))
    scores["avg_payout_ranking"] = 1.0 if avg_mentioned >= 4 and has_avg_context else (0.5 if avg_mentioned >= 2 else 0.0)

    # Colorado as highest avg payout
    co_patterns = [
        r'colorado.*(?:9[,.]?711|highest|first|#1|top|rank.*1)',
        r'(?:highest|first|#1|top).*(?:average|avg|per\s*payee).*colorado',
        r'colorado.*\$?9[,.]?7\d\d',
    ]
    scores["colorado_highest_avg"] = 1.0 if any(re.search(p, content_lower) for p in co_patterns) else 0.0

    # Deferred count ranking
    deferred_states = ["new york", "california", "pennsylvania", "ohio", "illinois", "michigan", "new jersey"]
    def_mentioned = sum(1 for s in deferred_states if s in content_lower)
    has_deferred_context = bool(re.search(r'deferred', content_lower))
    scores["deferred_ranking"] = 1.0 if def_mentioned >= 5 and has_deferred_context else (0.5 if def_mentioned >= 3 else 0.0)

    # NY highest deferred
    ny_patterns = [
        r'new\s*york.*(?:40[,.]?592|highest|most|first|#1|top|largest).*deferred',
        r'(?:highest|most|first|#1|top|largest).*deferred.*new\s*york',
        r'new\s*york.*40[,.]?592',
    ]
    scores["ny_highest_deferred"] = 1.0 if any(re.search(p, content_lower) for p in ny_patterns) else 0.0

    # Projected liability calculated
    proj_patterns = [
        r'(?:projected|estimated|future).*(?:liability|cost|exposure|payout)',
        r'(?:avg|average).*(?:multiply|times|x|\*).*deferred',
        r'deferred.*(?:multiply|times|x|\*).*(?:avg|average)',
    ]
    scores["projected_liability"] = 1.0 if any(re.search(p, content_lower) for p in proj_patterns) else 0.0

    # National summary
    national_patterns = [
        r'5[,.]7\d*\s*billion',
        r'877[,.]?\d*',
        r'483[,.]?\d*',
        r'6[,.]?510',
    ]
    nat_count = sum(1 for p in national_patterns if re.search(p, content_lower))
    scores["national_summary"] = 1.0 if nat_count >= 3 else (0.5 if nat_count >= 2 else 0.0)

    # Total projected future liability (~$3.15B)
    total_proj_patterns = [
        r'3[,.]1\d*\s*billion',
        r'\$?3[,.]?1[45]\d',
        r'(?:projected|future).*(?:total|national).*(?:3[,.]1|billion)',
        r'(?:3[,.]1|billion).*(?:projected|future)',
    ]
    scores["total_projected"] = 1.0 if any(re.search(p, content_lower) for p in total_proj_patterns) else 0.0

    # Exposure analysis
    analysis_patterns = [
        r'(?:exposure|risk|liability|burden)',
        r'(?:large|significant|substantial).*(?:deferred|future|obligation)',
        r'(?:federal|government).*(?:employ|workforce)',
    ]
    analysis_count = sum(1 for p in analysis_patterns if re.search(p, content_lower))
    scores["exposure_analysis"] = 1.0 if analysis_count >= 2 else (0.5 if analysis_count >= 1 else 0.0)

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

### 評分項 1：計算正確性（權重 35%）

- 1.0：所有計算正確——平均給付、遞延人數、預估負債與全國總計皆符合預期值。正確處理貨幣格式。
- 0.75：多數計算正確，僅有小幅四捨五入或一處計算錯誤。
- 0.5：核心方法正確，但有多項數值錯誤，或預估負債方法有瑕疵。
- 0.25：重大計算錯誤或對資料理解有誤。
- 0.0：未能完成計算，或結果完全錯誤。

### 評分項 2：多維度分析（權重 30%）

- 1.0：三種排名維度皆具備（平均給付、遞延人數、預估負債），且彼此區分清楚。展現出對「高負債來自高平均給付『且』高遞延人數的組合」之理解。
- 0.75：三種維度皆具備，但其中一項不完整，或未探討維度之間的交互作用。
- 0.5：只分析三者中的兩種，或有排名但無說明。
- 0.25：只分析一種維度。
- 0.0：沒有多維度分析。

### 評分項 3：財務洞見（權重 20%）

- 1.0：對退休金負債集中的成因提供有意義的洞見——聯邦就業模式、生活成本差異、軍事／政府存在。指出依金額排名前段的州與依平均給付排名前段的州有所不同。
- 0.75：對模式有良好觀察，並有一些脈絡推理。
- 0.5：基本觀察，缺乏更深入的財務推理。
- 0.25：除列數字外洞見極少。
- 0.0：沒有分析或洞見。

### 評分項 4：報告品質（權重 15%）

- 1.0：報告結構良好，每項排名各有清楚分區，使用表格或清單，全國摘要顯著呈現，流程合理。
- 0.75：結構良好，僅有小問題。
- 0.5：有內容但組織不佳。
- 0.25：雜亂或區段不完整。
- 0.0：沒有報告或空白檔案。
