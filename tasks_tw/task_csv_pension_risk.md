---
id: task_csv_pension_risk
name: 美國退休金風險評估
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_pension_risk
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T078tw_csv_pension_risk
workspace_files:
- source: csvs/us_pension_by_state.csv
  dest: us_pension_by_state.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 美國退休金風險評估

## Prompt

我的工作區裡有一個 CSV 檔案 `us_pension_by_state.csv`，內含按州與國會選區細分的美國聯邦退休金給付資料。欄位如下：

- `STATE_ABBREV_NAME` — 州縮寫與名稱（例如州總計列為 "OH-OHIO Total"）
- `DISTRICT` — 國會選區號碼、"At Large" 或年份
- `PAYEE_AMOUNT` — 給付給目前退休人員的總金額（以 $ 與逗號格式化）
- `PAYEE_COUNT` — 目前領取給付者人數
- `DEFERRED_COUNT` — 遞延領取者人數（已具請領資格但尚未開始請領的員工）

以 "Total" 結尾的列為州級彙總。第一列是 Grand Total。

請對退休金的給付義務進行風險評估，並把你的發現寫到 `pension_risk_report.md`。你的分析應包含：

- 每個州的**遞延對領取者比值（deferred-to-payee ratio）**：計算 DEFERRED_COUNT / PAYEE_COUNT。此比值代表每一位目前領取者背後有多少未來領取者在等待——比值愈高，代表相對於目前的未來義務愈多。依此比值將前 10 大州排名（排除領取者少於 100 人的項目）。
- **集中度風險（concentration risk）**：前 5 大州占總給付金額的百分比為何？前 10 大州呢？
- **選區級熱點（district-level hotspots）**：找出給付金額最高的 5 個個別國會選區（非州總計）。這些代表退休金義務的地理集中。
- **風險等級分類（risk tier classification）**：依遞延對領取者比值將所有州分成三個等級：
  - **高風險（high risk）**（比值 > 0.75）：相對於目前領取者有顯著的未來義務
  - **中風險（medium risk）**（比值 0.50–0.75）：中等的未來義務
  - **低風險（low risk）**（比值 < 0.50）：可控的未來義務

  列出各等級的州數，並點名高風險等級中的各州。
- 一段整體風險樣貌的**摘要（summary）**與建議

## Expected Behavior

助手應該：

1. 解析 CSV、清理格式，並計算每州的遞延對領取者比值
2. 依比值排名：DC（~5.69）、NJ（~1.07）、AK（~0.99）、ND（~0.99）、UT（~0.88）居前
3. 計算集中度：前 5 大州（OH、PA、FL、MI、CA）占總額 ~38%；前 10 大州 ~55%
4. 找出選區熱點：IN-1（$99.2M）、MI-5（$97.8M）、OH-13（$111.2M）、PA-7（$72.0M）、WV-1（$67.4M）
5. 依比值門檻將各州分入風險等級
6. DC 是重大離群值，比值 ~5.69（544 名領取者、3,093 遞延）
7. 高風險等級包含：DC、NJ、AK、ND、UT、CA、NY、CO、CT、HI（比值 > 0.75）

關鍵預期數值：

- DC 遞延對領取者比值：~5.69（遠高於其他）
- NJ 比值：~1.07（除 DC 外唯一 > 1.0 的州）
- 金額最高的選區：OH-13（~$111.2M）
- 前 5 大集中度：占總額 $5.71B 的 ~38%
- 全國平均比值：~0.55
- 高風險州（比值 > 0.75）：約 10 個州

## Grading Criteria

- [ ] 已建立報告檔案 `pension_risk_report.md`
- [ ] 已計算遞延對領取者比值並將前 10 大州排名
- [ ] 已指出 DC 為比值最高（~5.69）
- [ ] 已指出 NJ 為比值第二高（~1.07）
- [ ] 已計算集中度風險（前 5 與前 10 的百分比）
- [ ] 已找出選區級熱點
- [ ] 已指出 OH-13 為金額最高的選區之一（~$111M）
- [ ] 風險等級分類含各等級州數
- [ ] 已列出高風險等級的各州
- [ ] 有摘要，含風險評估與建議

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the pension risk assessment task.

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
    report_path = workspace / "pension_risk_report.md"
    if not report_path.exists():
        alternatives = ["risk_report.md", "report.md", "pension_report.md", "pension_risk.md", "risk_assessment.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "ratio_ranking": 0.0,
            "dc_highest_ratio": 0.0,
            "nj_second_ratio": 0.0,
            "concentration_risk": 0.0,
            "district_hotspots": 0.0,
            "oh13_top_district": 0.0,
            "risk_tiers": 0.0,
            "high_risk_states": 0.0,
            "summary_recommendations": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Deferred-to-payee ratio ranking
    ratio_context = bool(re.search(r'(?:deferred|ratio|defer.*payee)', content_lower))
    ratio_states = ["washington dc", "dc", "new jersey", "alaska", "north dakota", "utah"]
    ratio_mentioned = sum(1 for s in ratio_states if s in content_lower)
    scores["ratio_ranking"] = 1.0 if ratio_mentioned >= 4 and ratio_context else (0.5 if ratio_mentioned >= 2 else 0.0)

    # DC highest ratio
    dc_patterns = [
        r'(?:dc|washington\s*dc|district\s*of\s*columbia).*(?:5\.69|5\.7|highest|outlier|extreme)',
        r'(?:highest|outlier|extreme).*(?:ratio).*(?:dc|washington\s*dc)',
        r'(?:dc|washington\s*dc).*ratio.*(?:5\.[67])',
    ]
    scores["dc_highest_ratio"] = 1.0 if any(re.search(p, content_lower) for p in dc_patterns) else 0.0

    # NJ second ratio
    nj_patterns = [
        r'new\s*jersey.*(?:1\.0[67]|second|#2|only.*(?:above|over|exceed).*1)',
        r'(?:second|#2).*(?:ratio).*new\s*jersey',
        r'new\s*jersey.*1\.0\d',
    ]
    scores["nj_second_ratio"] = 1.0 if any(re.search(p, content_lower) for p in nj_patterns) else 0.0

    # Concentration risk
    conc_patterns = [
        r'(?:3[5-9]|4[0-2])\s*%.*(?:top\s*5|five)',
        r'(?:top\s*5|five).*(?:3[5-9]|4[0-2])\s*%',
        r'(?:5[2-8]|concentration).*(?:top\s*10|ten)',
        r'(?:top\s*10|ten).*(?:5[2-8])\s*%',
        r'concentration.*risk',
    ]
    scores["concentration_risk"] = 1.0 if any(re.search(p, content_lower) for p in conc_patterns) else 0.0

    # District hotspots
    district_terms = ["district", "congressional", "hotspot"]
    has_district_context = any(t in content_lower for t in district_terms)
    hotspot_patterns = [r'in-?1', r'mi-?5', r'oh-?13', r'pa-?7', r'wv-?1', r'oh-?6']
    hotspot_count = sum(1 for p in hotspot_patterns if re.search(p, content_lower))
    scores["district_hotspots"] = 1.0 if hotspot_count >= 3 and has_district_context else (0.5 if hotspot_count >= 2 else 0.0)

    # OH-13 as top district
    oh13_patterns = [
        r'oh(?:io)?[- ]?13.*(?:111|highest|top|largest|first)',
        r'(?:highest|top|largest|first).*(?:district).*oh(?:io)?[- ]?13',
        r'oh(?:io)?[- ]?13.*\$?111',
    ]
    scores["oh13_top_district"] = 1.0 if any(re.search(p, content_lower) for p in oh13_patterns) else 0.0

    # Risk tiers
    tier_patterns = [
        r'(?:high|medium|low)\s*risk',
        r'(?:tier|category|classification)',
        r'(?:0\.75|0\.50|0\.5)',
    ]
    tier_count = sum(1 for p in tier_patterns if re.search(p, content_lower))
    scores["risk_tiers"] = 1.0 if tier_count >= 2 else (0.5 if tier_count >= 1 else 0.0)

    # High-risk states listed
    high_risk_names = ["dc", "washington dc", "new jersey", "alaska", "north dakota",
                       "utah", "california", "new york", "colorado", "connecticut", "hawaii"]
    hr_mentioned = sum(1 for s in high_risk_names if s in content_lower)
    has_high_risk_context = bool(re.search(r'high.*risk', content_lower))
    scores["high_risk_states"] = 1.0 if hr_mentioned >= 6 and has_high_risk_context else (0.5 if hr_mentioned >= 3 else 0.0)

    # Summary and recommendations
    rec_patterns = [
        r'recommend',
        r'(?:monitor|watch|attention|concern)',
        r'(?:mitigat|manag|address|plan)',
        r'(?:risk|exposure).*(?:profile|assessment|overall)',
    ]
    rec_count = sum(1 for p in rec_patterns if re.search(p, content_lower))
    scores["summary_recommendations"] = 1.0 if rec_count >= 2 else (0.5 if rec_count >= 1 else 0.0)

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

### 評分項 1：風險指標正確性（權重 30%）

- 1.0：遞延對領取者比值正確計算，指出 DC 為極端離群值（~5.69）、NJ 第二（~1.07），並指出全國平均（~0.55）。集中度百分比準確。
- 0.75：多數比值正確，僅有小錯；關鍵離群值有指出。
- 0.5：理解比值概念，但有多項數值錯誤或漏掉關鍵離群值。
- 0.25：重大計算錯誤或對比值概念理解有誤。
- 0.0：未計算比值，或完全錯誤。

### 評分項 2：多層次分析（權重 25%）

- 1.0：分析在三個層次運作——州級比值、整體組合的集中度風險，以及選區級的細緻度。每個層次都提供不同洞見。選區熱點正確找出。
- 0.75：三個層次皆具備，但其中一項淺薄或不完整。
- 0.5：只有三個分析層次中的兩個。
- 0.25：只有一個分析層次。
- 0.0：沒有結構化分析。

### 評分項 3：風險框架品質（權重 25%）

- 1.0：等級分類清楚，門檻定義明確，各州正確歸類，且框架產出可執行的分組。指出 DC 為特殊個案。承認單以比值作為風險指標的限制。
- 0.75：等級系統良好，多數州正確歸類。
- 0.5：有等級概念，但門檻不清或歸類有誤。
- 0.25：風險分類模糊，缺乏明確準則。
- 0.0：未嘗試風險分類。

### 評分項 4：建議與洞見（權重 20%）

- 1.0：提出緊扣具體發現的可執行建議。指出單憑高比值並不代表高金額風險（ND 比值高但金額極小）。區分比值風險與絕對金額風險。提及監測策略。
- 0.75：建議良好，具一定細膩度。
- 0.5：建議籠統，未緊扣具體資料發現。
- 0.25：建議極少或流於表面。
- 0.0：沒有建議。
