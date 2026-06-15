---
id: task_csv_temp_anomalies
name: 全球氣溫異常偵測
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_temp_anomalies
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T057tw_csv_temp_anomalies
workspace_files:
- source: csvs/global_temperature.csv
  dest: global_temperature.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 全球氣溫異常偵測

## Prompt

我的工作區中有一個 CSV 檔 `global_temperature.csv`，內含全球氣溫距平
（temperature anomaly）資料。該檔有三個欄位：`Source`（為 "GISTEMP" 或
"gcag"）、`Year`（格式為 YYYY-MM）與 `Mean`（相對於某基準期的氣溫距平，
單位 °C）。

GISTEMP 資料涵蓋 1880–2023，gcag 資料涵蓋 1850–2024。

請分析此資料集的氣溫異常，並將你的發現寫入名為 `anomaly_report.md` 的檔案。
請聚焦於 GISTEMP 來源資料。你的報告應包含：

- **極端月度距平**：在 GISTEMP 紀錄中找出最熱與最冷的單一月份及其數值
- **統計離群值（statistical outliers）**：計算每個曆月（例如所有的一月、所有的
  二月）跨各年的平均與標準差，找出距平超過其月平均 2 個標準差以上（z-score > 2）
  的月份。至少列出最極端的前 10 個離群值及其 z-score
- **最冷年份**：依年度平均距平找出最冷的 5 個年份
- **最暖年份**：依年度平均距平找出最暖的 5 個年份
- **最大的年對年變化**：找出年度平均距平中最大的 5 次年對年（year-over-year）
  擺動（正向或負向）
- 一段簡短的**總結**，解讀這些異常告訴我們什麼樣的氣溫型態

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔
2. 篩選出 GISTEMP 紀錄（1880–2023）
3. 找出最熱月份：2023 年 9 月，+1.48°C
4. 找出最冷月份：1893 年 1 月，-0.82°C
5. 計算各曆月統計並找出 z-score 離群值
6. 計算年度平均並為年份排名
7. 計算年度平均的年對年變化
8. 撰寫一份結構化的 markdown 報告

預期關鍵數值：

- 最熱月份（GISTEMP）：2023-09，+1.48°C
- 最冷月份（GISTEMP）：1893-01，-0.82°C
- 最暖的前 5 個年份：2023（約 1.17）、2016（約 1.01）、2020（約 1.01）、
  2019（約 0.98）、2017（約 0.92）
- 最冷的前 5 個年份：1909（約 -0.49）、1904（約 -0.48）、1917（約 -0.46）、
  1911（約 -0.45）、1910（約 -0.44）
- 最極端的統計離群值：2023-09，z-score 約 3.76
- 許多離群值集中在 2015–2023，反映暖化加速
- 最大的年對年躍升包括 1976→1977（+0.28）與 2022→2023（+0.28）

## Grading Criteria

- [ ] 已建立報告檔 `anomaly_report.md`
- [ ] 正確找出最熱月份為 2023-09，數值約 1.48°C
- [ ] 正確找出最冷月份為 1893-01，數值約 -0.82°C
- [ ] 最暖年份包含 2023、2016 與 2020
- [ ] 最冷年份包含 1909 與 1904
- [ ] 包含含 z-score 的統計離群值分析
- [ ] 找出 2023 年 9 月為最大離群值（z-score 約 3.7–3.8）
- [ ] 計算年對年變化並找出最大的擺動
- [ ] 提供總結或解讀

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the temperature anomaly detection task.

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
    report_path = workspace / "anomaly_report.md"
    if not report_path.exists():
        alternatives = ["anomalies.md", "report.md", "temperature_anomalies.md", "analysis.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "hottest_month": 0.0,
            "coldest_month": 0.0,
            "warmest_years": 0.0,
            "coldest_years": 0.0,
            "outlier_analysis": 0.0,
            "top_outlier_zscore": 0.0,
            "yoy_changes": 0.0,
            "summary": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Hottest month: 2023-09 at 1.48
    hottest_patterns = [
        r'2023[\-/]09.*1\.48',
        r'1\.48.*2023[\-/]09',
        r'september\s*2023.*1\.48',
        r'1\.48.*september\s*2023',
        r'sep(?:tember)?\s*2023.*1\.48',
    ]
    scores["hottest_month"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in hottest_patterns) else 0.0

    # Coldest month: 1893-01 at -0.82
    coldest_patterns = [
        r'1893[\-/]01.*-0\.82',
        r'-0\.82.*1893[\-/]01',
        r'january\s*1893.*-0\.82',
        r'-0\.82.*january\s*1893',
        r'jan(?:uary)?\s*1893.*-0\.82',
    ]
    scores["coldest_month"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in coldest_patterns) else 0.0

    # Warmest years include 2023, 2016, 2020
    warm_count = 0
    for year in ["2023", "2016", "2020"]:
        if re.search(rf'(?:warm|hot).*{year}|{year}.*(?:warm|hot)', content_lower) or \
           (year in content and re.search(r'warm|hot|highest', content_lower)):
            warm_count += 1
    # Also check if these years appear with high values
    for year in ["2023", "2016", "2020"]:
        if re.search(rf'{year}.*[01]\.\d{{2,4}}', content):
            warm_count += 1
    scores["warmest_years"] = 1.0 if warm_count >= 4 else (0.5 if warm_count >= 2 else 0.0)

    # Coldest years include 1909, 1904
    cold_count = 0
    for year in ["1909", "1904"]:
        if re.search(rf'(?:cold|cool).*{year}|{year}.*(?:cold|cool)', content_lower) or \
           (year in content and re.search(r'cold|cool|lowest', content_lower)):
            cold_count += 1
        if re.search(rf'{year}.*-0\.[34]\d', content):
            cold_count += 1
    scores["coldest_years"] = 1.0 if cold_count >= 3 else (0.5 if cold_count >= 1 else 0.0)

    # Outlier / z-score analysis
    outlier_patterns = [
        r'z[\-\s]?score',
        r'standard\s*deviation',
        r'outlier',
        r'sigma',
        r'statistical',
    ]
    outlier_count = sum(1 for p in outlier_patterns if re.search(p, content_lower))
    scores["outlier_analysis"] = 1.0 if outlier_count >= 2 else (0.5 if outlier_count >= 1 else 0.0)

    # Top outlier z-score ~3.7-3.8 for 2023-09
    zscore_patterns = [
        r'3\.7[0-9]',
        r'3\.8[0-9]',
        r'2023[\-/]09.*3\.[78]',
        r'september\s*2023.*3\.[78]',
    ]
    scores["top_outlier_zscore"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in zscore_patterns) else 0.0

    # Year-over-year changes
    yoy_patterns = [
        r'year[\-\s]?over[\-\s]?year',
        r'year[\-\s]?to[\-\s]?year',
        r'yoy',
        r'annual.*change',
        r'(?:1976|1977).*(?:1976|1977)',
        r'(?:2022|2023).*(?:swing|jump|change|increase)',
    ]
    yoy_count = sum(1 for p in yoy_patterns if re.search(p, content_lower))
    scores["yoy_changes"] = 1.0 if yoy_count >= 2 else (0.5 if yoy_count >= 1 else 0.0)

    # Summary / interpretation
    summary_patterns = [
        r'summar',
        r'interpret',
        r'conclusion',
        r'(?:accelerat|rapid).*warm',
        r'warm.*(?:accelerat|rapid)',
        r'climate',
        r'trend',
    ]
    summary_count = sum(1 for p in summary_patterns if re.search(p, content_lower))
    scores["summary"] = 1.0 if summary_count >= 2 else (0.5 if summary_count >= 1 else 0.0)

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

**1.0 分**：極端月份、最暖／最冷年份、z-score 與年對年變化在數值上皆正確，並以
具體數值清楚呈現。
**0.75 分**：多數數值正確，僅有一、兩處輕微落差。
**0.5 分**：部分數值正確，但有數個關鍵數字錯誤或缺漏。
**0.25 分**：少數數值正確；有重大計算錯誤。
**0.0 分**：無任何正確計算，或未嘗試分析。

### 評分項 2：統計嚴謹性（權重 30%）

**1.0 分**：正確計算各月統計與 z-score，以正確門檻找出離群值，並以適當脈絡呈現
結果（例如解釋 z-score > 2 的意義）。
**0.75 分**：z-score 分析已具備且大致正確，僅有小問題。
**0.5 分**：有一些統計分析，但缺少 z-score 或計算錯誤。
**0.25 分**：統計分析極少，多為質性觀察。
**0.0 分**：無統計分析。

### 評分項 3：報告結構與解讀（權重 20%）

**1.0 分**：markdown 組織良好，各分析元件分節清楚，並有一段周延的總結，將異常
連結到更廣的氣溫型態。
**0.75 分**：報告有條理，僅有小幅結構問題；有總結但較簡短。
**0.5 分**：含分析但組織不佳，或缺少總結。
**0.25 分**：雜亂或缺少主要章節。
**0.0 分**：無報告或為空。

### 評分項 4：完整性（權重 15%）

**1.0 分**：所有要求元素皆齊備：極端月份、含 z-score 的離群值分析、最暖／最冷
年份、年對年變化與總結。
**0.75 分**：多數元素齊備，僅有一處小缺漏。
**0.5 分**：缺少數個元素。
**0.25 分**：僅有少數元素。
**0.0 分**：報告缺漏或近乎空白。
