---
id: task_csv_stations_by_elevation
name: Idaho 氣象站海拔排名
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_stations_by_elevation
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T066tw_csv_stations_by_elevation
workspace_files:
- source: csvs/idaho_weather_stations.csv
  dest: idaho_weather_stations.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# Idaho 氣象站海拔排名

## Prompt

我的工作區中有一個 CSV 檔 `idaho_weather_stations.csv`，內含 Idaho 各地 213 個
氣象站的資料。該檔有下列欄位：`OBJECTID`、`Station Name`、`Station Code`、
`Managing Agency`、`County`、`Longitude`、`Latitude`、`Elevation (feet)`、
`x`、`y`。

請依海拔（elevation）分析這些測站，並將你的發現寫入 `elevation_report.md`。你的
報告應包含：

- **海拔最高的前 10 個測站**，由高至低排名，包含測站名稱、海拔、所在郡（county）
  與管理機構（managing agency）
- **海拔最低的後 10 個測站**，由低至高排名，包含測站名稱、海拔、所在郡與管理機構
- **摘要統計**：所有測站的最小、最大、平均與中位數海拔
- **依管理機構的海拔分布**：比較 NWS 測站與 NRCS 測站的平均海拔，並解釋其差異
- **平均海拔最高的郡**（僅限有 3 個以上測站的郡）與平均海拔最低的郡（同樣僅限
  有 3 個以上測站的郡）
- 一段簡短的**總結段落**，解讀海拔型態

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔（213 列，UTF-8 含 BOM）
2. 依 `Elevation (feet)` 欄位排序測站
3. 找出最高測站：MEADOW LAKE SNOTEL，9,150 ft（LEMHI 郡，NRCS）
4. 找出最低測站：DWORSHAK FISH HATCHERY，995 ft（CLEARWATER 郡，NWS）
5. 計算摘要統計：最小 995、最大 9150、平均約 4859、中位數約 4920
6. 比較機構：NWS 平均約 3,993 ft（143 站）vs NRCS 平均約 6,628 ft（70 站）
7. 找出郡層級的海拔型態（以 3 站以上為篩選）
8. 撰寫一份結構良好的 markdown 報告

預期關鍵數值：

- 最高：MEADOW LAKE SNOTEL，9,150 ft
- 最低：DWORSHAK FISH HATCHERY，995 ft
- 平均海拔：約 4,859 ft
- 中位數海拔：約 4,920 ft
- NWS 平均：約 3,993 ft（143 站）
- NRCS 平均：約 6,628 ft（70 站）
- 前 10 包含：MEADOW LAKE SNOTEL (9150)、VIENNA MINE PILLOW (8960)、
  MILL CREEK SUMMIT SNOTEL (8800)、GALENA SUMMIT SNOTEL (8780)、
  DOLLARHIDE SUMMIT SNOTEL (8420)

## Grading Criteria

- [ ] 已建立報告檔 `elevation_report.md`
- [ ] 列出海拔最高的前 10 站，第 1 正確（MEADOW LAKE SNOTEL，9150 ft）
- [ ] 列出海拔最低的後 10 站，第 1 正確（DWORSHAK FISH HATCHERY，995 ft）
- [ ] 摘要統計包含最小、最大、平均與中位數
- [ ] 包含 NWS 與 NRCS 海拔比較並附正確平均
- [ ] 含最高／最低平均海拔的郡層級分析
- [ ] 含解讀型態的總結段落

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the elevation ranking task.

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

    report_path = workspace / "elevation_report.md"
    if not report_path.exists():
        for alt in ["elevation.md", "report.md", "stations_elevation.md", "analysis.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "highest_station": 0.0,
            "lowest_station": 0.0,
            "summary_stats": 0.0,
            "agency_comparison": 0.0,
            "county_analysis": 0.0,
            "summary_paragraph": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check highest station (MEADOW LAKE SNOTEL, 9150)
    has_meadow = bool(re.search(r'meadow\s*lake', content_lower))
    has_9150 = bool(re.search(r'9[,.]?150', content))
    scores["highest_station"] = 1.0 if (has_meadow and has_9150) else (0.5 if has_meadow or has_9150 else 0.0)

    # Check lowest station (DWORSHAK FISH HATCHERY, 995)
    has_dworshak = bool(re.search(r'dworshak', content_lower))
    has_995 = bool(re.search(r'\b995\b', content))
    scores["lowest_station"] = 1.0 if (has_dworshak and has_995) else (0.5 if has_dworshak or has_995 else 0.0)

    # Check summary statistics
    stats_found = 0
    if re.search(r'\b995\b', content):
        stats_found += 1
    if re.search(r'9[,.]?150', content):
        stats_found += 1
    if re.search(r'4[,.]?8[56]\d', content):
        stats_found += 1
    if re.search(r'4[,.]?9[12]\d', content):
        stats_found += 1
    scores["summary_stats"] = min(1.0, stats_found / 3)

    # Check agency comparison
    has_nws_avg = bool(re.search(r'(?:3[,.]?99\d|3[,.]?98\d|4[,.]?0[01]\d)', content))
    has_nrcs_avg = bool(re.search(r'(?:6[,.]?6[23]\d|6[,.]?64\d)', content))
    has_agency_text = bool(re.search(r'nws.*nrcs|nrcs.*nws', content_lower))
    scores["agency_comparison"] = 1.0 if (has_nws_avg and has_nrcs_avg) else (0.5 if has_agency_text else 0.0)

    # Check county analysis
    county_patterns = [r'county', r'counties', r'highest.*average.*elevation', r'lowest.*average.*elevation']
    county_found = sum(1 for p in county_patterns if re.search(p, content_lower))
    scores["county_analysis"] = 1.0 if county_found >= 2 else (0.5 if county_found >= 1 else 0.0)

    # Check for summary/interpretation paragraph
    summary_patterns = [
        r'(?:summary|interpretation|overview|conclusion|pattern)',
        r'(?:nrcs|snotel).*(?:higher|mountain|alpine|backcountry)',
        r'(?:nws).*(?:lower|valley|town|populated|urban)',
    ]
    summary_found = sum(1 for p in summary_patterns if re.search(p, content_lower))
    scores["summary_paragraph"] = 1.0 if summary_found >= 2 else (0.5 if summary_found >= 1 else 0.0)

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

### 評分項 1：資料正確性（權重 35%）

**1.0 分**：所有排名皆正確，統計準確（平均約 4859、中位數約 4920、前／後 10 正確），
且各機構平均符合預期值。
**0.75 分**：排名與統計大致正確，僅有小幅落差（例如平均差幾英尺）。
**0.5 分**：最高與最低測站正確，但中間排名或統計有錯誤。
**0.25 分**：排名或統計有數個重大錯誤。
**0.0 分**：未嘗試分析或根本性錯誤。

### 評分項 2：分析深度（權重 30%）

**1.0 分**：對 NWS 與 NRCS 差異提供具意義的解讀（NRCS/SNOTEL 測站為高海拔積雪
監測站，NWS 測站位於有人口的河谷）、郡型態，以及海拔分布洞見。
**0.75 分**：解讀良好，僅在說明機構差異上有小缺漏。
**0.5 分**：陳述事實，但解讀或洞見有限。
**0.25 分**：除列出數字外幾無分析。
**0.0 分**：未提供任何分析或解讀。

### 評分項 3：報告完整性（權重 20%）

**1.0 分**：所有要求章節皆齊備：前 10、後 10、摘要統計、機構比較、郡分析、
總結段落。
**0.75 分**：多數章節齊備，僅有一處小缺漏。
**0.5 分**：缺少數個章節。
**0.25 分**：僅有一、兩個章節。
**0.0 分**：報告缺漏或為空。

### 評分項 4：呈現品質（權重 15%）

**1.0 分**：markdown 排版良好，含表格、標題清楚、版面有條理。
**0.75 分**：排版良好，僅有小問題。
**0.5 分**：可讀但組織不佳。
**0.25 分**：不易閱讀。
**0.0 分**：無報告或無法閱讀。
