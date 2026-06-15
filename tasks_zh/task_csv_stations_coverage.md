---
id: task_csv_stations_coverage
name: 愛達荷州氣象站涵蓋缺口分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_stations_coverage
source_benchmark: pinchbench
claw_eval_id: P067zh_csv_stations_coverage
workspace_files:
- source: csvs/idaho_weather_stations.csv
  dest: idaho_weather_stations.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 愛達荷州氣象站涵蓋缺口分析

## Prompt

我的工作區裡有一個 CSV 檔案 `idaho_weather_stations.csv`，內含愛達荷州（Idaho）213 個氣象站的資料。檔案欄位有：`OBJECTID`、`Station Name`、`Station Code`、`Managing Agency`、`County`、`Longitude`、`Latitude`、`Elevation (feet)`、`x`、`y`。

愛達荷州共有 44 個郡（county）。請分析這個氣象站網路的地理與海拔涵蓋情況，並把你的發現寫到 `coverage_report.md`。你的報告應包含：

- **郡級涵蓋（county coverage）**：愛達荷州的 44 個郡中，有多少個郡至少有一個氣象站？哪一個（或哪些）郡完全沒有氣象站？
- **各郡氣象站密度（station density by county）**：哪些郡的氣象站最多、哪些（在有氣象站的郡之中）最少？
- **海拔帶分布（elevation band distribution）**：把氣象站依海拔分組（例如以 1,000 ft 為一段），統計每個海拔帶各有多少個氣象站。指出哪些海拔帶涵蓋過多、哪些涵蓋不足。
- **機構涵蓋比較（agency coverage comparison）**：NWS 與 NRCS 在氣象站布點上的地理差異為何？哪些郡只由 NWS 服務、哪些只由 NRCS 服務、哪些兩者都有？
- **資料品質問題（data quality issues）**：找出任何郡別資料缺漏或空白的氣象站。
- 一個**建議區段（recommendations）**：說明在哪些地方增設氣象站能改善涵蓋。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案（213 列）
2. 將氣象站的郡別與愛達荷州的 44 個郡交叉比對
3. 發現 44 個郡中有 43 個有氣象站；Payette County 完全沒有氣象站
4. 注意到有 5 個氣象站的郡別資料空白／缺漏
5. 找出氣象站最多的郡：Idaho（13）、Blaine（11）、Shoshone（10）、Custer（10）、Clearwater（10）
6. 找出只有單一氣象站的郡：Kootenai、Jefferson、Nez Perce、Madison、Lincoln
7. 建立海拔帶分布，呈現氣象站集中在 4,000-6,000 ft 區間
8. 比較 NWS（143 個站，海拔較低）與 NRCS（70 個站，海拔較高）
9. 撰寫一份結構清晰、含建議的報告

關鍵預期數值：

- 氣象站總數：213
- 有氣象站的郡：44 個中有 43 個（若僅計郡別非空白者則為 38-39 個）
- 缺漏的郡：Payette County 完全沒有氣象站
- 有 5 個氣象站的郡別欄位空白
- 氣象站最多：Idaho County（13）
- 機構：NWS（143）、NRCS（70）
- 最大的海拔帶：4,000-5,000 ft（37 個站）、5,000-6,000 ft（42 個站）
- 氣象站最少：低於 2,000 ft（10 個站）、高於 8,000 ft（7 個站）

## Grading Criteria

- [ ] 已建立報告檔案 `coverage_report.md`
- [ ] 已指出 Payette County 沒有氣象站
- [ ] 已列出各郡氣象站數，且氣象站最多的郡正確
- [ ] 已包含海拔帶分布
- [ ] 已包含 NWS 與 NRCS 的地理比較
- [ ] 已指出郡別資料缺漏（5 個站）
- [ ] 有建議區段

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the coverage gap analysis task.

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

    report_path = workspace / "coverage_report.md"
    if not report_path.exists():
        for alt in ["coverage.md", "report.md", "gap_analysis.md", "analysis.md", "coverage_analysis.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "payette_identified": 0.0,
            "county_counts": 0.0,
            "elevation_bands": 0.0,
            "agency_comparison": 0.0,
            "missing_data": 0.0,
            "recommendations": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check Payette County identified as missing
    has_payette = bool(re.search(r'payette', content_lower))
    has_zero_or_no = bool(re.search(r'payette.*(?:no |zero|0 |missing|without|lack)', content_lower) or
                         re.search(r'(?:no |zero|0 |missing|without|lack).*payette', content_lower))
    scores["payette_identified"] = 1.0 if has_payette else 0.0

    # Check county station counts
    top_counties = ['idaho', 'blaine', 'shoshone', 'custer', 'clearwater']
    county_mentions = sum(1 for c in top_counties if re.search(rf'\b{c}\b.*\b1[0-3]\b|\b1[0-3]\b.*\b{c}\b', content_lower))
    scores["county_counts"] = 1.0 if county_mentions >= 3 else (0.5 if county_mentions >= 1 else 0.0)

    # Check elevation band distribution
    elev_indicators = 0
    if re.search(r'elevation.*band|band.*elevation|elevation.*range|elevation.*distribution', content_lower):
        elev_indicators += 1
    if re.search(r'(?:4[,.]?000|5[,.]?000|6[,.]?000)', content):
        elev_indicators += 1
    if re.search(r'(?:37|42)\s*station', content_lower) or re.search(r'(?:over|under).*represent', content_lower):
        elev_indicators += 1
    scores["elevation_bands"] = 1.0 if elev_indicators >= 2 else (0.5 if elev_indicators >= 1 else 0.0)

    # Check NWS vs NRCS comparison
    has_nws = bool(re.search(r'\bnws\b', content_lower))
    has_nrcs = bool(re.search(r'\bnrcs\b', content_lower))
    has_143 = bool(re.search(r'\b143\b', content))
    has_70 = bool(re.search(r'\b70\b', content))
    scores["agency_comparison"] = 1.0 if (has_nws and has_nrcs and (has_143 or has_70)) else (0.5 if (has_nws and has_nrcs) else 0.0)

    # Check missing data identification
    missing_patterns = [
        r'(?:5|five)\s*station.*(?:missing|blank|empty)',
        r'(?:missing|blank|empty).*(?:5|five)\s*station',
        r'(?:missing|blank|empty).*county',
        r'county.*(?:missing|blank|empty)',
    ]
    scores["missing_data"] = 1.0 if any(re.search(p, content_lower) for p in missing_patterns) else 0.0

    # Check recommendations
    rec_patterns = [
        r'recommend',
        r'suggest',
        r'additional\s*station',
        r'improv.*coverage',
        r'gap.*(?:fill|address|close)',
    ]
    scores["recommendations"] = 1.0 if any(re.search(p, content_lower) for p in rec_patterns) else 0.0

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

### 評分項 1：涵蓋分析正確性（權重 35%）

- 1.0：正確指出 44 個郡中有 43 個有氣象站，點名 Payette 為缺漏的郡，提供各郡正確的氣象站數，並正確找出 5 個郡別缺漏的氣象站。
- 0.75：多數涵蓋事實正確，僅有一兩處小錯（例如某郡計數略有偏差）。
- 0.5：找出部分缺口，但漏掉 Payette 或有多處計數錯誤。
- 0.25：嘗試做涵蓋分析，但有重大事實錯誤。
- 0.0：沒有涵蓋分析，或完全錯誤。

### 評分項 2：海拔分布品質（權重 25%）

- 1.0：海拔帶劃分清楚且計數正確，指出 4,000-6,000 ft 的集中現象，並注意到低於 2,000 ft 與高於 8,000 ft 涵蓋稀疏。
- 0.75：海拔帶劃分良好，僅有小幅計數錯誤。
- 0.5：有做海拔分組，但不完整或有錯誤。
- 0.25：海拔分析極少。
- 0.0：完全沒有海拔分布。

### 評分項 3：機構分析（權重 20%）

- 1.0：清楚說明 NWS 與 NRCS 在地理／海拔上的分布差異，指出只由單一機構服務的郡，並提供差異成因的洞見（NWS 設於城鎮、NRCS 設於山區以監測積雪）。
- 0.75：機構比較良好，僅有小幅缺漏。
- 0.5：提到兩個機構，但比較有限。
- 0.25：機構討論極少。
- 0.0：完全沒有機構分析。

### 評分項 4：建議品質（權重 20%）

- 1.0：提出具體、可執行且緊扣已發現缺口的建議（例如在 Payette County 增設氣象站、改善北部郡的低海拔涵蓋、補上空白的郡別資料）。
- 0.75：建議良好，具一定具體性。
- 0.5：建議籠統，未緊扣具體發現。
- 0.25：建議模糊或無助益。
- 0.0：沒有建議區段。
