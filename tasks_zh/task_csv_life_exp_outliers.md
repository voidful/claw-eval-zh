---
id: task_csv_life_exp_outliers
name: 平均壽命離群值偵測
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_life_exp_outliers
source_benchmark: pinchbench
claw_eval_id: P061zh_csv_life_exp_outliers
workspace_files:
- source: csvs/gapminder_life_expectancy.csv
  dest: gapminder_life_expectancy.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 平均壽命離群值偵測

## Prompt

我的工作區中有一個 CSV 檔 `gapminder_life_expectancy.csv`，內含取自 Gapminder
資料集的平均壽命資料。該檔有下列欄位：`country`、`year`、`pop`、`continent`、
`lifeExp` 與 `gdpPercap`。資料涵蓋 5 大洲的 142 個國家，自 1952 至 2007 每 5 年
一筆。

請找出平均壽命資料中的離群值（outliers）與異常（anomalies），並將你的發現寫入
名為 `life_exp_outliers.md` 的檔案。你的報告應包含：

- **2007 年的統計離群值偵測**：使用 z-score 或 IQR 法找出平均壽命異常高或異常低
  的國家。回報所用方法、門檻，以及哪些國家屬於離群值。
- **大洲內離群值**：找出 2007 年明顯偏離其所屬大洲平均的國家（例如某非洲國家的
  平均壽命遠高於非洲平均）。
- **時序異常**：找出平均壽命在相鄰時間點（5 年區間）之間**下降**的國家。由於
  平均壽命通常隨時間上升，這類情形相當令人意外。列出國家、時間區間與下降幅度。
- **最劇烈的單期下降**：找出所有國家中相鄰時間點之間最大的 5 次平均壽命下降。
- 一段簡短的**分析**，說明可能驅動這些離群值與異常的因素（例如 HIV/AIDS 疫情、
  戰爭、種族滅絕）。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔
2. 對 2007 年資料套用統計方法（z-score 或 IQR）。以 z-score（離平均 >2 個標準差）
   找出 6 個低離群值：Swaziland (z=-2.27)、Mozambique (z=-2.06)、Zambia (z=-2.04)、
   Sierra Leone (z=-2.02)、Lesotho (z=-2.02)、Angola (z=-2.01)。無高離群值。
   以 IQR（1.5×IQR）則因分布甚廣（IQR=19.556）而找不到離群值。
3. 找出 2007 年大洲內離群值——偏離其大洲平均 >1.5 個標準差的國家：
   - Africa：Reunion (76.442, z=2.25)、Libya (73.952)、Tunisia (73.923)、
     Algeria (72.301)、Mauritius (72.801)、Morocco (71.164)、Egypt (71.338) 偏高；
     Swaziland (39.613, z=-1.58) 偏低
   - Americas：Haiti (60.916, z=-2.86) 明顯偏低；Canada (80.653) 與
     Bolivia (65.554) 為離群值
   - Asia：Afghanistan (43.828, z=-3.38) 為極端離群值
   - Europe：Turkey (71.777)、Romania (72.476)、Bulgaria (73.005) 為低離群值
4. 找出時序下降——平均壽命在相鄰 5 年區間之間下滑的國家
5. 標示最劇烈的下降：Rwanda 1987-1992 (-20.421)、Zimbabwe 1992-1997 (-13.568)、
   Lesotho 1997-2002 (-10.965)、Swaziland 1997-2002 (-10.420)、
   Botswana 1992-1997 (-10.189)
6. 將離群值連結到真實世界事件（南部非洲的 HIV/AIDS、盧安達種族滅絕、柬埔寨種族
   滅絕、戰爭）

預期關鍵數值：

- 2007 年 z-score 離群值（z < -2）：Swaziland、Mozambique、Zambia、Sierra Leone、
  Lesotho、Angola
- 最嚴重的大洲內離群值：Asia 的 Afghanistan（z=-3.38）
- 最大的單期下降：Rwanda 1987-1992（-20.421 年，自 44.02 降至 23.599）
- 第二大：Zimbabwe 1992-1997（-13.568）

## Grading Criteria

- [ ] 已建立報告檔 `life_exp_outliers.md`
- [ ] 描述統計離群值方法（z-score、IQR 或類似方法）
- [ ] 找出 2007 年低端離群值（Swaziland、Mozambique 等）
- [ ] 分析大洲內離群值
- [ ] 找出 Afghanistan 為 Asia 內的離群值
- [ ] 找出平均壽命的時序下降
- [ ] 找出 Rwanda 1987-1992 的下降為極端（約 20 年降幅）
- [ ] 列出最劇烈的下降並附幅度
- [ ] 提供真實世界的解釋（HIV/AIDS、衝突等）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the life expectancy outlier detection task.

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
    report_path = workspace / "life_exp_outliers.md"
    if not report_path.exists():
        alternatives = ["outliers.md", "report.md", "life_expectancy_outliers.md",
                        "outlier_report.md", "anomalies.md", "life_exp_anomalies.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "statistical_method": 0.0,
            "low_outliers_2007": 0.0,
            "continent_outliers": 0.0,
            "afghanistan_outlier": 0.0,
            "temporal_decreases": 0.0,
            "rwanda_drop": 0.0,
            "dramatic_drops": 0.0,
            "explanations": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Statistical method described
    method_patterns = [
        r'z[- ]?score',
        r'iqr',
        r'interquartile',
        r'standard\s*deviation',
        r'(?:1\.5|2).*(?:std|sigma|sd)',
    ]
    scores["statistical_method"] = 1.0 if any(re.search(p, content_lower) for p in method_patterns) else 0.0

    # Low-end outliers in 2007
    low_outlier_countries = ["swaziland", "mozambique", "zambia", "sierra leone", "lesotho", "angola"]
    found = sum(1 for c in low_outlier_countries if c in content_lower)
    scores["low_outliers_2007"] = 1.0 if found >= 4 else (0.5 if found >= 2 else 0.0)

    # Within-continent outliers discussed
    continent_outlier_patterns = [
        r'(?:within|continent).*outlier',
        r'outlier.*(?:within|continent)',
        r'deviat.*(?:continent|region)',
        r'(?:continent|region).*(?:average|mean).*(?:far|deviat|outlier|anomal)',
    ]
    continent_examples = ["haiti", "afghanistan", "reunion", "turkey", "romania"]
    example_found = sum(1 for c in continent_examples if c in content_lower)
    scores["continent_outliers"] = 1.0 if (
        any(re.search(p, content_lower) for p in continent_outlier_patterns) or example_found >= 3
    ) else (0.5 if example_found >= 2 else 0.0)

    # Afghanistan as outlier within Asia
    afghan_patterns = [
        r'afghanistan.*(?:outlier|anomal|lowest|extreme)',
        r'afghanistan.*asia.*(?:below|low|deviat)',
        r'asia.*afghanistan.*(?:outlier|anomal|lowest)',
        r'afghanistan.*43\.\d',
    ]
    scores["afghanistan_outlier"] = 1.0 if any(re.search(p, content_lower) for p in afghan_patterns) else 0.0

    # Temporal decreases identified
    decrease_countries = ["botswana", "cambodia", "rwanda", "zimbabwe", "swaziland",
                          "lesotho", "south africa", "zambia", "iraq"]
    decrease_found = sum(1 for c in decrease_countries if c in content_lower)
    has_decrease_concept = bool(re.search(r'(?:decreas|declin|drop|fell|reduc).*life\s*exp', content_lower) or
                                re.search(r'life\s*exp.*(?:decreas|declin|drop|fell|reduc)', content_lower))
    scores["temporal_decreases"] = 1.0 if (decrease_found >= 4 and has_decrease_concept) else (
        0.5 if decrease_found >= 2 else 0.0)

    # Rwanda drop specifically
    rwanda_patterns = [
        r'rwanda.*(?:1987|1992).*(?:drop|declin|decreas|fell)',
        r'rwanda.*(?:20|23\.5|44\.0|genoci)',
        r'rwanda.*(?:-20|-?20\.\d)',
        r'genoci.*rwanda',
        r'rwanda.*genoci',
    ]
    scores["rwanda_drop"] = 1.0 if any(re.search(p, content_lower) for p in rwanda_patterns) else 0.0

    # Top dramatic drops listed
    dramatic_countries = ["rwanda", "zimbabwe", "lesotho", "swaziland", "botswana", "cambodia"]
    dramatic_found = sum(1 for c in dramatic_countries if c in content_lower)
    has_magnitude = bool(re.search(r'-?\d{1,2}\.\d+\s*year', content_lower) or
                         re.search(r'(?:drop|declin|fell|decreas).*\d{1,2}\.\d', content_lower))
    scores["dramatic_drops"] = 1.0 if (dramatic_found >= 4 and has_magnitude) else (
        0.5 if dramatic_found >= 2 else 0.0)

    # Real-world explanations
    explanation_patterns = [
        r'hiv|aids',
        r'genoci',
        r'(?:civil\s*)?war',
        r'(?:khmer|rouge|pol\s*pot)',
        r'conflict',
        r'epidemic|pandemic',
        r'famine',
    ]
    explanations_found = sum(1 for p in explanation_patterns if re.search(p, content_lower))
    scores["explanations"] = 1.0 if explanations_found >= 3 else (0.5 if explanations_found >= 1 else 0.0)

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

### 評分項 1：統計嚴謹性（權重 30%）

**1.0 分**：清楚描述所用統計方法，回報門檻與具體數值（z-score 或 IQR 界限），
正確找出離群值及其統計量，並指出其侷限（例如分布甚廣時 IQR 可能標不出離群值）。
**0.75 分**：使用有效的統計方法並正確找出多數離群值，但在門檻或方法論細節上有
缺漏。
**0.5 分**：找出離群值，但統計佐證薄弱或不清楚。
**0.25 分**：提及離群值但缺乏適當的統計分析。
**0.0 分**：未嘗試統計離群值偵測。

### 評分項 2：異常偵測廣度（權重 30%）

**1.0 分**：涵蓋三類異常：全域統計離群值、大洲內離群值與時序下降。對每一類皆
提供具體國家、時間區間與幅度。
**0.75 分**：涵蓋至少兩類異常並具良好細節。
**0.5 分**：將一類處理得當，或多類但流於表面。
**0.25 分**：僅有基本的離群值辨識而無深度。
**0.0 分**：無具意義的異常偵測。

### 評分項 3：脈絡分析（權重 25%）

**1.0 分**：將離群值連結到真實世界事件（南部非洲的 HIV/AIDS 疫情、盧安達種族
滅絕、柬埔寨赤柬、伊拉克／索馬利亞的戰爭），並有具體引述。
**0.75 分**：對多數離群值提供合理解釋，但缺少一些關鍵連結。
**0.5 分**：提供一些解釋，但缺乏具體性或遺漏主要成因。
**0.25 分**：解釋含糊或籠統。
**0.0 分**：未嘗試任何解釋。

### 評分項 4：報告品質（權重 15%）

**1.0 分**：報告結構良好，分節清楚，以表格或排版過的清單呈現資料，由方法論到
發現再到分析的脈絡合乎邏輯。
**0.75 分**：結構良好，僅有小問題。
**0.5 分**：內容齊備，但組織不佳。
**0.25 分**：不易閱讀或缺少章節。
**0.0 分**：無報告或輸出無法使用。
