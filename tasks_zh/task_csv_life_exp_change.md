---
id: task_csv_life_exp_change
name: 平均壽命隨時間的變化
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_life_exp_change
source_benchmark: pinchbench
claw_eval_id: P062zh_csv_life_exp_change
workspace_files:
- source: csvs/gapminder_life_expectancy.csv
  dest: gapminder_life_expectancy.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 平均壽命隨時間的變化

## Prompt

我的工作區中有一個 CSV 檔 `gapminder_life_expectancy.csv`，內含取自 Gapminder
資料集的平均壽命資料。該檔有下列欄位：`country`、`year`、`pop`、`continent`、
`lifeExp` 與 `gdpPercap`。資料涵蓋 5 大洲的 142 個國家，自 1952 至 2007 每 5 年
一筆。

請分析平均壽命隨時間的變化，並將你的發現寫入名為 `life_exp_change.md` 的檔案。
你的報告應包含：

- **全球趨勢**：計算每一年（1952 至 2007）的全球平均壽命，並描述整體走勢
- **大洲層級趨勢**：計算每一年各大洲的平均壽命，並比較不同大洲的進展
- **進步最多者**：找出自 1952 至 2007 平均壽命絕對增幅最大的 10 個國家，附上
  起始值、結束值與總變化
- **進步最慢者／衰退者**：找出自 1952 至 2007 平均壽命改善最小（或衰退）的
  10 個國家
- **收斂或發散**：分析最高與最低大洲平均之間的差距隨時間是縮小還是擴大
- 一段簡短的**總結**，說明關鍵重點

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔
2. 計算各年全球平均：1952 (49.058)、1957 (51.507)、1962 (53.609)、1967 (55.678)、
   1972 (57.647)、1977 (59.570)、1982 (61.533)、1987 (63.213)、1992 (64.160)、
   1997 (65.015)、2002 (65.695)、2007 (67.007)
3. 計算各大洲平均，呈現 Europe／Oceania 居頂、Africa 居底，而 Asia 增幅最大
4. 找出前 10 名進步者：Oman (+38.062)、Vietnam (+33.837)、Indonesia (+33.182)、
   Saudi Arabia (+32.902)、Libya (+31.229)、Korea Rep. (+31.170)、
   Nicaragua (+30.585)、West Bank and Gaza (+30.262)、Yemen Rep. (+30.150)、
   Gambia (+29.448)
5. 找出後 10 名：Norway (+7.526)、Congo Dem. Rep. (+7.319)、Liberia (+7.198)、
   Rwanda (+6.242)、South Africa (+4.330)、Botswana (+3.106)、Lesotho (+0.454)、
   Zambia (+0.346)、Swaziland (-1.794)、Zimbabwe (-4.964)
6. 分析收斂／發散：指出最高（Oceania/Europe）與最低（Africa）大洲平均之間的差距
   持續存在，且可能因 HIV/AIDS 而在 1990–2000 年代略為擴大

預期關鍵數值：

- 全球平均 1952：約 49.06，2007：約 67.01
- 整體全球增幅：約 17.95 年
- 進步最多者：Oman（+38.062，自 37.578 至 75.640）
- 衰退最多者：Zimbabwe（-4.964，自 48.451 至 43.487）
- 1952-2007 間僅有 2 國淨變化為負：Swaziland (-1.794)、Zimbabwe (-4.964)

## Grading Criteria

- [ ] 已建立報告檔 `life_exp_change.md`
- [ ] 計算各年（或多數年份）的全球平均壽命
- [ ] 正確描述全球上升趨勢（55 年間自約 49 升至約 67）
- [ ] 計算並比較大洲層級趨勢
- [ ] 找出進步最多者，以 Oman 為第 1（+38 年）
- [ ] 找出進步最慢者／衰退者
- [ ] 找出 Zimbabwe 與 Swaziland 為唯二淨衰退的國家
- [ ] 包含收斂／發散分析
- [ ] 提供含關鍵重點的總結

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the life expectancy change over time task.

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
    report_path = workspace / "life_exp_change.md"
    if not report_path.exists():
        alternatives = ["change.md", "report.md", "life_expectancy_change.md",
                        "life_exp_trends.md", "trends.md", "life_exp_over_time.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "global_averages": 0.0,
            "global_trend": 0.0,
            "continent_trends": 0.0,
            "top_improvers": 0.0,
            "oman_first": 0.0,
            "decliners": 0.0,
            "convergence_analysis": 0.0,
            "summary": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Global averages computed (check for year-average pairs)
    year_avg_patterns = [
        r'1952.*49\.\d',
        r'1977.*59\.\d',
        r'2007.*67\.\d',
    ]
    avg_found = sum(1 for p in year_avg_patterns if re.search(p, content))
    scores["global_averages"] = 1.0 if avg_found >= 2 else (0.5 if avg_found >= 1 else 0.0)

    # Global upward trend described
    trend_patterns = [
        r'(?:increas|ris|improv|grew|gain).*(?:49|50).*(?:67|68)',
        r'(?:49|50).*(?:to|→|->).*(?:67|68)',
        r'(?:upward|positive|steady|consistent).*(?:trend|trajectory|increase)',
        r'(?:17|18).*year.*(?:gain|increase|improv)',
    ]
    scores["global_trend"] = 1.0 if any(re.search(p, content_lower) for p in trend_patterns) else 0.0

    # Continent-level trends
    continents_with_data = 0
    for cont in ["africa", "americas", "asia", "europe", "oceania"]:
        if cont in content_lower:
            continents_with_data += 1
    has_temporal = bool(re.search(r'(?:1952|1977|1982).*(?:africa|europe|asia)', content_lower) or
                        re.search(r'(?:africa|europe|asia).*(?:1952|1977|1982)', content_lower))
    scores["continent_trends"] = 1.0 if (continents_with_data >= 4 and has_temporal) else (
        0.5 if continents_with_data >= 3 else 0.0)

    # Top improvers (at least 5 of top 10)
    top_improvers = ["oman", "vietnam", "indonesia", "saudi arabia", "libya",
                     "korea", "nicaragua", "west bank", "yemen", "gambia"]
    improver_found = sum(1 for c in top_improvers if c in content_lower)
    scores["top_improvers"] = 1.0 if improver_found >= 6 else (0.5 if improver_found >= 3 else 0.0)

    # Oman as biggest improver
    oman_patterns = [
        r'oman.*(?:38|37\.\d|largest|biggest|most|#1|first|top)',
        r'(?:largest|biggest|most|#1|first|top).*oman',
        r'oman.*37\.578.*75\.640',
        r'oman.*\+?38',
    ]
    scores["oman_first"] = 1.0 if any(re.search(p, content_lower) for p in oman_patterns) else 0.0

    # Decliners identified
    decliner_patterns = [
        r'zimbabwe.*(?:declin|decreas|negative|drop|fell|lost|\-)',
        r'swaziland.*(?:declin|decreas|negative|drop|fell|lost|\-)',
        r'(?:only|two|2).*(?:countr|nation).*(?:declin|decreas|negative)',
    ]
    decliner_found = sum(1 for p in decliner_patterns if re.search(p, content_lower))
    scores["decliners"] = 1.0 if decliner_found >= 2 else (0.5 if decliner_found >= 1 else 0.0)

    # Convergence/divergence analysis
    convergence_patterns = [
        r'(?:converg|diverg)',
        r'(?:gap|dispar|inequal).*(?:narrow|widen|persist|grew|shrank)',
        r'(?:narrow|widen).*(?:gap|dispar|inequal)',
        r'africa.*(?:lag|behind|gap|slow)',
        r'(?:hiv|aids).*(?:widen|revers|set\s*back)',
    ]
    scores["convergence_analysis"] = 1.0 if any(re.search(p, content_lower) for p in convergence_patterns) else 0.0

    # Summary / takeaways
    summary_patterns = [
        r'(?:summary|conclusion|takeaway|key\s*finding|in\s*summary)',
        r'(?:overall|in\s*conclusion|to\s*summarize)',
    ]
    has_summary = any(re.search(p, content_lower) for p in summary_patterns)
    has_insight = bool(re.search(r'(?:despite|although|however|notably|remarkably)', content_lower))
    scores["summary"] = 1.0 if (has_summary and has_insight) else (0.5 if has_summary or has_insight else 0.0)

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

### 評分項 1：資料分析正確性（權重 35%）

**1.0 分**：所有計算數值皆正確——全球平均符合資料，前／後進步者皆正確找出且
幅度準確，大洲趨勢準確。
**0.75 分**：多數數值正確，僅有一、兩處輕微數值錯誤。
**0.5 分**：整體趨勢正確，但數個具體數值錯誤或缺漏。
**0.25 分**：有重大計算錯誤，或多數數值不正確。
**0.0 分**：無任何正確計算。

### 評分項 2：趨勢分析深度（權重 30%）

**1.0 分**：在全球、大洲與國家層級皆有完整分析。指出 1990 年後全球增幅趨緩、
Africa 因 HIV/AIDS 而進展停滯、Asia 戲劇性追趕，以及少數倒退的國家。討論各大洲
間的收斂／發散。
**0.75 分**：多層級分析良好，但缺少一個維度或對成因著墨不足。
**0.5 分**：在一、兩個層級有基本趨勢描述，但缺乏深度。
**0.25 分**：分析流於表面，洞見甚少。
**0.0 分**：無趨勢分析。

### 評分項 3：比較洞見（權重 20%）

**1.0 分**：有效對比進步最多者與衰退者，說明中東／亞洲國家何以進步最多（起點低、
快速發展），而南部非洲國家何以衰退（HIV/AIDS）。指出 Norway 增幅小（+7.5）是因
其起點本就很高（1952 年 72.7）。
**0.75 分**：比較良好，但缺少一些細緻之處。
**0.5 分**：嘗試一些比較，但缺乏深度。
**0.25 分**：比較分析極少。
**0.0 分**：未在各群組間作比較。

### 評分項 4：完整性與呈現（權重 15%）

**1.0 分**：所有要求元素皆齊備（全球趨勢、大洲趨勢、進步最多者、衰退者、收斂
分析、總結），組織良好並含表格或排版過的資料。
**0.75 分**：多數元素齊備且組織良好。
**0.5 分**：缺少數個元素或組織不佳。
**0.25 分**：不完整或雜亂。
**0.0 分**：報告缺漏或無法使用。
