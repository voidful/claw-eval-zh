---
id: task_csv_temp_trend
name: 全球氣溫趨勢分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_temp_trend
source_benchmark: pinchbench
claw_eval_id: P058zh_csv_temp_trend
workspace_files:
- source: csvs/global_temperature.csv
  dest: global_temperature.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 全球氣溫趨勢分析

## Prompt

我的工作區中有一個 CSV 檔 `global_temperature.csv`，內含全球氣溫距平資料。該檔
有三個欄位：`Source`（為 "GISTEMP" 或 "gcag"）、`Year`（格式為 YYYY-MM）與
`Mean`（相對於某基準期的氣溫距平，單位 °C）。

GISTEMP 資料涵蓋 1880–2023，gcag 資料涵蓋 1850–2024。

請使用 GISTEMP 資料分析長期氣溫趨勢，並將你的發現寫入名為 `trend_report.md`
的檔案。你的報告應包含：

- **整體趨勢**：計算年度平均距平，並對整段 1880–2023 期間擬合線性迴歸（linear
  regression），以求出每十年（per decade）的暖化速率（單位 °C）
- **加速分析**：將資料分為 1950 年前（1880–1949）與 1950 年後（1950–2023）兩個
  期間。分別計算各期的線性趨勢並比較暖化速率
- **最冷與最暖期間**：在紀錄中找出最冷的 10 年區段與最暖的 10 年區段
- **里程碑跨越**：找出年度平均距平首次超過 +0.5°C 的年份，以及首次超過 +1.0°C
  的年份
- **近期暖化脈絡**：最近的十年（2014–2023）與最早的十年（1880–1889）相比如何？
- 一段簡短的**總結**，說明整體暖化趨勢及其加速

## Expected Behavior

助手應該：

1. 讀取並解析 CSV，篩選出 GISTEMP
2. 從月度資料計算年度平均（僅使用 12 個月份齊全的年份）
3. 擬合線性迴歸以求出暖化速率
4. 比較 1950 年前與 1950 年後的趨勢以呈現加速
5. 找出最冷與最暖的 10 年區段
6. 找出里程碑年份
7. 撰寫一份結構化報告

預期關鍵數值：

- 全期線性趨勢：約 0.08°C/decade（斜率約 0.008°C/year）
- 1950 年前趨勢：約 0.04°C/decade
- 1950 年後趨勢：約 0.15°C/decade（約為 1950 年前的 4 倍）
- 最暖十年：2010 年代（約 0.80°C 平均）或部分的 2020 年代
- 最冷十年：1900 年代（約 -0.32°C）或 1910 年代（約 -0.33°C）
- 年度平均首次超過 +0.5°C 的年份：1998（約 0.61°C）
- 年度平均首次超過 +1.0°C 的年份：2016（約 1.01°C）
- 近期十年（2014–2023）與最早十年（1880–1889）相比：差距約 1.0°C

## Grading Criteria

- [ ] 已建立報告檔 `trend_report.md`
- [ ] 回報整體暖化速率約 0.07–0.09°C per decade
- [ ] 計算 1950 年前暖化速率（約 0.03–0.05°C/decade）
- [ ] 計算 1950 年後暖化速率（約 0.14–0.17°C/decade）
- [ ] 指出加速（1950 年後速率明顯快於 1950 年前）
- [ ] 找出首次超過 +0.5°C 的年份（1998 或相近）
- [ ] 找出首次超過 +1.0°C 的年份（2015 或 2016）
- [ ] 包含近期十年與最早十年的比較
- [ ] 提供總結或結論

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the temperature trend analysis task.

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
    report_path = workspace / "trend_report.md"
    if not report_path.exists():
        alternatives = ["trend_analysis.md", "report.md", "temperature_trend.md", "analysis.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "overall_rate": 0.0,
            "pre1950_rate": 0.0,
            "post1950_rate": 0.0,
            "acceleration": 0.0,
            "first_05": 0.0,
            "first_10": 0.0,
            "decade_comparison": 0.0,
            "summary": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Overall warming rate ~0.07-0.09°C per decade
    rate_patterns = [
        r'0\.0[78]\d*\s*°?C?\s*/?\s*(?:per\s*)?decade',
        r'0\.0[78]\d*\s*°?C?\s*(?:per|every)\s*(?:10|ten)\s*year',
        r'(?:per\s*decade|decade).*0\.0[78]',
        r'0\.00[78]\d*\s*°?C?\s*/?\s*(?:per\s*)?year',
    ]
    scores["overall_rate"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in rate_patterns) else 0.0

    # Pre-1950 rate ~0.03-0.05°C/decade
    pre1950_patterns = [
        r'(?:pre|before|prior)[\s\-]*1950.*0\.0[345]\d*',
        r'0\.0[345]\d*.*(?:pre|before|prior)[\s\-]*1950',
        r'1880.*1949.*0\.0[345]',
        r'0\.0[345].*1880.*194[09]',
    ]
    scores["pre1950_rate"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in pre1950_patterns) else 0.0

    # Post-1950 rate ~0.14-0.17°C/decade
    post1950_patterns = [
        r'(?:post|after|since)[\s\-]*1950.*0\.1[45678]\d*',
        r'0\.1[45678]\d*.*(?:post|after|since)[\s\-]*1950',
        r'1950.*2023.*0\.1[45678]',
        r'0\.1[45678].*1950.*202',
    ]
    scores["post1950_rate"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in post1950_patterns) else 0.0

    # Acceleration noted
    accel_patterns = [
        r'accelerat',
        r'(?:3|4|three|four)\s*(?:times|×|x)\s*(?:fast|great)',
        r'(?:fast|great).*(?:3|4|three|four)\s*(?:times|×|x)',
        r'(?:significant|notable|substantial).*(?:increas|fast)',
        r'(?:rapid|steep).*(?:recent|post|after|since)',
    ]
    scores["acceleration"] = 1.0 if any(re.search(p, content_lower) for p in accel_patterns) else 0.0

    # First year > +0.5°C (1998)
    first_05_patterns = [
        r'199[78].*(?:first|exceed|cross|breach|surpass).*0\.5',
        r'(?:first|exceed|cross|breach|surpass).*0\.5.*199[78]',
        r'0\.5\s*°?C.*(?:first|exceed|cross).*199[78]',
        r'199[78].*0\.[56]\d*.*(?:first|milestone)',
    ]
    scores["first_05"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in first_05_patterns) else 0.0

    # First year > +1.0°C (2015 or 2016)
    first_10_patterns = [
        r'201[56].*(?:first|exceed|cross|breach|surpass).*1\.0',
        r'(?:first|exceed|cross|breach|surpass).*1\.0.*201[56]',
        r'1\.0\s*°?C.*(?:first|exceed|cross).*201[56]',
        r'201[56].*1\.[01]\d*.*(?:first|milestone)',
    ]
    scores["first_10"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in first_10_patterns) else 0.0

    # Decade comparison (recent vs earliest)
    decade_patterns = [
        r'(?:2010|2014|2020|recent).*(?:1880|earliest|first)',
        r'(?:1880|earliest|first).*(?:2010|2014|2020|recent)',
        r'~?1\.0\d*\s*°?C.*(?:warmer|higher|difference|increase)',
        r'(?:warmer|higher|difference|increase).*~?1\.0\d*\s*°?C',
    ]
    scores["decade_comparison"] = 1.0 if any(re.search(p, content_lower) or re.search(p, content) for p in decade_patterns) else 0.0

    # Summary
    summary_patterns = [
        r'summar',
        r'conclusion',
        r'in\s+(?:summary|conclusion)',
        r'overall.*(?:trend|warming|temperature)',
        r'(?:clear|unmistakable|evident|undeniable).*(?:warm|trend)',
    ]
    scores["summary"] = 1.0 if any(re.search(p, content_lower) for p in summary_patterns) else 0.0

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

### 評分項 1：量化正確性（權重 35%）

**1.0 分**：線性迴歸斜率、各十年速率與里程碑年份在數值上皆正確，並清楚標示單位。
**0.75 分**：多數數值正確，僅在較不關鍵的數字上有一、兩處小錯誤。
**0.5 分**：部分數值正確，但關鍵數字（整體速率、里程碑年份）錯誤。
**0.25 分**：少數數值正確；有根本性計算錯誤。
**0.0 分**：無任何正確計算。

### 評分項 2：趨勢分析深度（權重 30%）

**1.0 分**：以 1950 年前後速率的量化比較清楚展現暖化加速。以正確年份找出里程碑
跨越。提供具意義的十年比較，呈現近期暖化的幅度。
**0.75 分**：加速分析良好，多數元件齊備且準確。
**0.5 分**：提及加速，但缺乏量化佐證或遺漏關鍵元件。
**0.25 分**：趨勢描述流於表面，缺乏量化分析。
**0.0 分**：無趨勢分析。

### 評分項 3：報告品質（權重 20%）

**1.0 分**：markdown 結構良好，分節清楚，適當運用表格或排版過的數字，並以連貫的
敘事串接各項分析。
**0.75 分**：結構良好，僅有小幅排版或組織問題。
**0.5 分**：含分析，但不易閱讀或排版不佳。
**0.25 分**：雜亂或缺少主要章節。
**0.0 分**：無報告或為空。

### 評分項 4：完整性（權重 15%）

**1.0 分**：所有要求元素皆齊備：整體趨勢、分期分析、最冷／最暖區段、里程碑跨越、
十年比較與總結。
**0.75 分**：多數元素齊備，僅有一處小缺漏。
**0.5 分**：缺少數個元素。
**0.25 分**：僅有少數元素。
**0.0 分**：報告缺漏或近乎空白。
