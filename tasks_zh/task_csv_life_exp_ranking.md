---
id: task_csv_life_exp_ranking
name: 各國平均壽命排名
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_life_exp_ranking
source_benchmark: pinchbench
claw_eval_id: P060zh_csv_life_exp_ranking
workspace_files:
- source: csvs/gapminder_life_expectancy.csv
  dest: gapminder_life_expectancy.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 各國平均壽命排名

## Prompt

我的工作區中有一個 CSV 檔 `gapminder_life_expectancy.csv`，內含取自 Gapminder
資料集的平均壽命（life expectancy）資料。該檔有下列欄位：`country`、`year`、
`pop`、`continent`、`lifeExp` 與 `gdpPercap`。資料涵蓋 5 大洲（Africa、
Americas、Asia、Europe、Oceania）的 142 個國家，自 1952 至 2007 每 5 年一筆。

請分析各國依平均壽命的排名，並將你的發現寫入名為 `life_exp_ranking.md` 的檔案。
你的報告應包含：

- **平均壽命最高的前 10 國**（2007 年），附上其所屬大洲與確切的平均壽命數值
- **平均壽命最低的後 10 國**（2007 年），附上其所屬大洲與確切的平均壽命數值
- **各大洲平均壽命平均值**（2007 年）
- **排名隨時間的變化**：比較 1952 與 2007 的前 5 國與後 5 國
- 一段簡短的**總結**，說明排名中的關鍵型態（例如哪些大洲主導頂端／底端、有無
  任何意外之處）

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔（1704 列、142 個國家、12 個時間點）
2. 篩選出 2007 年資料並依平均壽命排序
3. 找出前 10 名：Japan (82.603)、Hong Kong China (82.208)、Iceland (81.757)、
   Switzerland (81.701)、Australia (81.235)、Spain (80.941)、Sweden (80.884)、
   Israel (80.745)、France (80.657)、Canada (80.653)
4. 找出後 10 名：Swaziland (39.613)、Mozambique (42.082)、Zambia (42.384)、
   Sierra Leone (42.568)、Lesotho (42.592)、Angola (42.731)、Zimbabwe (43.487)、
   Afghanistan (43.828)、Central African Republic (44.741)、Liberia (45.678)
5. 計算各大洲平均：Africa（約 54.806）、Americas（約 73.608）、Asia（約 70.728）、
   Europe（約 77.649）、Oceania（約 80.719）
6. 比較 1952 與 2007 的排名，呈現其變化
7. 指出 2007 年後 10 國除 Afghanistan 外皆為非洲國家

預期關鍵數值：

- 2007 年第 1 名：Japan (82.603)
- 2007 年第 142 名（最後）：Swaziland (39.613)
- 最高大洲平均：Oceania（約 80.72）
- 最低大洲平均：Africa（約 54.81）
- 2007 年範圍：82.603 - 39.613 = 42.99 年

## Grading Criteria

- [ ] 已建立報告檔 `life_exp_ranking.md`
- [ ] 正確列出 2007 年前 10 國並附平均壽命數值
- [ ] 正確找出 Japan 為第 1 名（82.603）
- [ ] 正確列出 2007 年後 10 國
- [ ] 正確找出 Swaziland 為最低（39.613）
- [ ] 計算並回報各大洲平均
- [ ] 指出 Africa 的大洲平均最低
- [ ] 包含歷史比較（1952 vs 2007）
- [ ] 提供型態總結

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the life expectancy ranking task.

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
    report_path = workspace / "life_exp_ranking.md"
    if not report_path.exists():
        alternatives = ["ranking.md", "report.md", "life_expectancy_ranking.md",
                        "rankings.md", "life_exp_report.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "top_countries": 0.0,
            "japan_first": 0.0,
            "bottom_countries": 0.0,
            "swaziland_last": 0.0,
            "continent_averages": 0.0,
            "africa_lowest": 0.0,
            "historical_comparison": 0.0,
            "pattern_summary": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check top countries (at least 5 of top 10 mentioned)
    top_countries = ["japan", "hong kong", "iceland", "switzerland", "australia",
                     "spain", "sweden", "israel", "france", "canada"]
    top_found = sum(1 for c in top_countries if c in content_lower)
    scores["top_countries"] = 1.0 if top_found >= 7 else (0.5 if top_found >= 4 else 0.0)

    # Japan as #1
    japan_patterns = [
        r'japan.*82\.6',
        r'1\.\s*japan',
        r'japan.*(?:highest|first|top|#1|number one|rank.*1)',
        r'(?:highest|first|top|#1).*japan',
    ]
    scores["japan_first"] = 1.0 if any(re.search(p, content_lower) for p in japan_patterns) else 0.0

    # Bottom countries (at least 5 of bottom 10)
    bottom_countries = ["swaziland", "mozambique", "zambia", "sierra leone", "lesotho",
                        "angola", "zimbabwe", "afghanistan", "central african republic", "liberia"]
    bottom_found = sum(1 for c in bottom_countries if c in content_lower)
    scores["bottom_countries"] = 1.0 if bottom_found >= 7 else (0.5 if bottom_found >= 4 else 0.0)

    # Swaziland as lowest
    swaziland_patterns = [
        r'swaziland.*39\.6',
        r'swaziland.*(?:lowest|last|bottom|worst)',
        r'(?:lowest|last|bottom).*swaziland',
    ]
    scores["swaziland_last"] = 1.0 if any(re.search(p, content_lower) for p in swaziland_patterns) else 0.0

    # Continent averages
    continents_mentioned = 0
    for cont in ["africa", "americas", "asia", "europe", "oceania"]:
        if cont in content_lower:
            continents_mentioned += 1
    has_averages = bool(re.search(r'(?:average|mean|avg).*(?:continent|region)', content_lower) or
                        re.search(r'(?:continent|region).*(?:average|mean|avg)', content_lower) or
                        (continents_mentioned >= 4 and re.search(r'\d{2}\.\d', content)))
    scores["continent_averages"] = 1.0 if (has_averages and continents_mentioned >= 4) else (
        0.5 if continents_mentioned >= 3 else 0.0)

    # Africa as lowest continent
    africa_low_patterns = [
        r'africa.*(?:lowest|worst|behind|last|lag|trail)',
        r'(?:lowest|worst|last).*(?:continent|region).*africa',
        r'africa.*54\.\d',
        r'africa.*55\.\d',
    ]
    scores["africa_lowest"] = 1.0 if any(re.search(p, content_lower) for p in africa_low_patterns) else 0.0

    # Historical comparison (1952 mentioned with ranking context)
    historical_patterns = [
        r'1952.*(?:rank|top|bottom|highest|lowest)',
        r'(?:rank|top|bottom|highest|lowest).*1952',
        r'(?:changed|shifted|evolved|compared).*(?:1952|over time|historically)',
        r'1952.*2007',
    ]
    scores["historical_comparison"] = 1.0 if any(re.search(p, content_lower) for p in historical_patterns) else 0.0

    # Pattern summary
    pattern_indicators = 0
    if re.search(r'africa.*(?:dominat|most|all|majority).*bottom', content_lower):
        pattern_indicators += 1
    if re.search(r'(?:europe|oceania).*(?:dominat|most|top)', content_lower):
        pattern_indicators += 1
    if re.search(r'(?:gap|disparity|inequality|range|difference)', content_lower):
        pattern_indicators += 1
    if re.search(r'(?:pattern|trend|observation|notable|key\s*finding)', content_lower):
        pattern_indicators += 1
    scores["pattern_summary"] = 1.0 if pattern_indicators >= 2 else (0.5 if pattern_indicators >= 1 else 0.0)

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

### 評分項 1：排名正確性（權重 35%）

**1.0 分**：前 10 國與後 10 國皆正確找出，平均壽命數值準確。所有數值皆符合
資料集。
**0.75 分**：多數排名正確，僅有一、兩國位置不對或數值小錯。
**0.5 分**：大方向正確（頂端／底端國家正確），但數個具體名次或數值錯誤。
**0.25 分**：找出一些正確國家，但排名多半錯誤或不完整。
**0.0 分**：未嘗試排名或完全錯誤。

### 評分項 2：分析深度（權重 30%）

**1.0 分**：包含各大洲平均、歷史比較與具洞察力的型態分析。指出關鍵觀察，例如
Africa 主導底端排名、最高與最低之間 43 年的差距，以及排名自 1952 至 2007 的
變化。
**0.75 分**：包含多數分析元素並有良好觀察，但缺少一個元件。
**0.5 分**：有基本分析，但缺乏深度——缺少各大洲平均、歷史比較或型態分析其中之一。
**0.25 分**：除列出國家外幾無分析。
**0.0 分**：除原始數字外毫無分析。

### 評分項 3：報告結構與呈現（權重 20%）

**1.0 分**：markdown 組織良好，分節清楚，以排版過的表格或清單呈現排名，由概覽到
細節的脈絡流暢。
**0.75 分**：組織良好，僅有小幅排版問題。
**0.5 分**：內容齊備，但組織不佳。
**0.25 分**：雜亂或不易閱讀。
**0.0 分**：無報告或輸出無法使用。

### 評分項 4：完整性（權重 15%）

**1.0 分**：所有要求元素皆齊備：前 10、後 10、各大洲平均、歷史比較與總結。
**0.75 分**：多數元素齊備，僅有一處小缺漏。
**0.5 分**：缺少數個要求元素。
**0.25 分**：僅部分完成。
**0.0 分**：報告缺漏或近乎空白。
