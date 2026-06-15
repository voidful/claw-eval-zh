---
id: task_csv_stations_filter
name: 愛達荷州氣象站多條件篩選
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_stations_filter
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T068tw_csv_stations_filter
workspace_files:
- source: csvs/idaho_weather_stations.csv
  dest: idaho_weather_stations.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 愛達荷州氣象站多條件篩選

## Prompt

我的工作區裡有一個 CSV 檔案 `idaho_weather_stations.csv`，內含愛達荷州（Idaho）213 個氣象站的資料。檔案欄位有：`OBJECTID`、`Station Name`、`Station Code`、`Managing Agency`、`County`、`Longitude`、`Latitude`、`Elevation (feet)`、`x`、`y`。

請執行下列篩選與分析任務，並把結果寫到 `filter_report.md`：

1. **高海拔 NWS 氣象站**：找出所有由 NWS 管理、海拔在 5,000 ft 以上（含）的氣象站。依海拔由高到低排序，列出站名、海拔與郡別。共有幾個？

2. **Custer County 的 NRCS 氣象站**：找出所有位於 Custer County、由 NRCS 管理的氣象站。依海拔由高到低排序，列出站名與海拔。

3. **南部低海拔氣象站**：找出所有海拔介於 3,000 到 4,000 ft（含）之間、且位於北緯 43°N 以南的氣象站。緯度欄位為 DMS 格式（例如 "42 57 00"）。列出站名、郡別、海拔與緯度。

4. **彙總表**：建立一個交叉統計表（cross-tabulation），呈現各管理機構（NWS、NRCS）與各海拔類別（Below 3000、3000-4999、5000-6999、7000+）的氣象站數。

每一項篩選都請註明符合條件的氣象站總數。

## Expected Behavior

助手應該：

1. 解析 CSV 檔案，處理 BOM 與 DMS 格式座標
2. 篩選海拔 >= 5,000 ft 的 NWS 站：恰好 39 個站，最高為 GALENA（7,300 ft）
3. 篩選 Custer County 的 NRCS 站：4 個站（DOLLARHIDE SUMMIT SNOTEL 8420、HILTS CREEK SNOTEL 8000、BEAR CANYON SNOTEL 7900、STICKNEY MILL SNOTEL 7430）
4. 解析 DMS 緯度，篩選海拔 3000-4000 ft 且位於 43°N 以南者：8 個站，包含 BLISS 4 NW、BUHL 2、CASTLEFORD 2 N、GOODING 2S、JEROME、SHOSHONE 1 WNW、TWIN FALLS KVMT、TWIN FALLS WSO
5. 建立機構 × 海拔類別的交叉統計表
6. 把整理後的結果寫到報告檔

關鍵預期數值：

- NWS >= 5000 ft：39 個站；最高為 GALENA（7,300 ft）
- Custer 的 NRCS：4 個站；DOLLARHIDE SUMMIT SNOTEL（8,420 ft）最高
- 3000-4000 ft 且位於 43°N 以南：8 個站
- 交叉統計表總計：NWS 143、NRCS 70

## Grading Criteria

- [ ] 已建立報告檔案 `filter_report.md`
- [ ] NWS >= 5000 ft 的數量為 39
- [ ] 已指出 GALENA 為最高的 NWS 站（7,300 ft）
- [ ] Custer County 的 NRCS 數量為 4
- [ ] 已指出 DOLLARHIDE SUMMIT SNOTEL（8,420 ft）
- [ ] 南部篩選有正確解析 DMS 緯度
- [ ] 已找出 8 個南部低海拔氣象站
- [ ] 有依機構與海拔類別建立的交叉統計表

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the multi-criteria filtering task.

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

    report_path = workspace / "filter_report.md"
    if not report_path.exists():
        for alt in ["report.md", "filter_results.md", "filtering_report.md", "analysis.md", "stations_filter.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "nws_high_count": 0.0,
            "nws_highest": 0.0,
            "nrcs_custer_count": 0.0,
            "nrcs_custer_top": 0.0,
            "southern_filter": 0.0,
            "cross_tabulation": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check NWS >= 5000 ft count (39)
    nws_count_patterns = [r'\b39\b.*(?:station|nws)', r'(?:station|nws).*\b39\b', r'\b39\b']
    scores["nws_high_count"] = 1.0 if any(re.search(p, content_lower) for p in nws_count_patterns) else 0.0

    # Check GALENA as highest NWS station at 7300
    has_galena = bool(re.search(r'galena', content_lower))
    has_7300 = bool(re.search(r'7[,.]?300', content))
    scores["nws_highest"] = 1.0 if (has_galena and has_7300) else (0.5 if has_galena else 0.0)

    # Check NRCS Custer count (4)
    custer_section = re.search(r'custer.*?(?=\n#|\Z)', content_lower, re.DOTALL)
    custer_text = custer_section.group() if custer_section else content_lower
    has_4_custer = bool(re.search(r'\b4\b.*(?:station|nrcs|custer)', custer_text) or
                       re.search(r'(?:station|nrcs|custer).*\b4\b', custer_text))
    scores["nrcs_custer_count"] = 1.0 if has_4_custer else 0.0

    # Check DOLLARHIDE as top NRCS/Custer station
    has_dollarhide = bool(re.search(r'dollarhide', content_lower))
    has_8420 = bool(re.search(r'8[,.]?420', content))
    scores["nrcs_custer_top"] = 1.0 if (has_dollarhide and has_8420) else (0.5 if has_dollarhide else 0.0)

    # Check southern filter (8 stations, latitude parsing)
    southern_stations = ['bliss', 'buhl', 'castleford', 'gooding', 'jerome', 'shoshone', 'twin falls']
    found_southern = sum(1 for s in southern_stations if s in content_lower)
    has_8_count = bool(re.search(r'\b8\b.*(?:station|south|low)', content_lower) or
                      re.search(r'(?:station|south|low).*\b8\b', content_lower))
    scores["southern_filter"] = 1.0 if found_southern >= 5 else (0.5 if found_southern >= 3 else 0.0)

    # Check cross-tabulation
    cross_tab_indicators = 0
    if re.search(r'cross.*tab|tabul|matrix|breakdown.*agency.*elev|agency.*elevation', content_lower):
        cross_tab_indicators += 1
    if re.search(r'\b143\b', content) and re.search(r'\b70\b', content):
        cross_tab_indicators += 1
    if re.search(r'(?:below|under|<)\s*3[,.]?000', content_lower) or re.search(r'7[,.]?000\s*\+|above\s*7', content_lower):
        cross_tab_indicators += 1
    scores["cross_tabulation"] = 1.0 if cross_tab_indicators >= 2 else (0.5 if cross_tab_indicators >= 1 else 0.0)

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

### 評分項 1：篩選正確性（權重 40%）

- 1.0：四項篩選結果全部正確，數量精確（39、4、8）且站名清單正確；DMS 緯度解析正確處理。
- 0.75：四項中有三項正確，一項有小錯。
- 0.5：兩項正確，其餘有明顯錯誤。
- 0.25：僅一項正確，其餘有重大錯誤。
- 0.0：沒有任何篩選結果正確。

### 評分項 2：DMS 座標處理（權重 20%）

- 1.0：正確解析 DMS 格式緯度（例如 "42 57 00" → 42.95°），準確套用 43°N 門檻，並列出全部 8 個符合的氣象站。
- 0.75：DMS 解析正確，但漏掉一個站或有輕微邊界誤差。
- 0.5：嘗試解析 DMS，但錯誤影響到結果。
- 0.25：把 DMS 當成十進位度，或只取度的部分。
- 0.0：沒有嘗試緯度篩選，或完全錯誤。

### 評分項 3：交叉統計表品質（權重 20%）

- 1.0：表格／矩陣清楚，以機構為列、海拔帶為欄，計數正確，且列／欄總計加總為 213。
- 0.75：表格良好，僅有小幅計數錯誤。
- 0.5：嘗試做交叉統計，但格式不佳或計數有誤。
- 0.25：交叉統計做得極少。
- 0.0：完全沒有交叉統計。

### 評分項 4：報告組織（權重 20%）

- 1.0：每一項篩選結果各自分區，數量顯著標示，站名清單排版良好（表格或排序清單），報告流暢有條理。
- 0.75：組織良好，僅有小幅排版問題。
- 0.5：有結果但組織不佳、不易閱讀。
- 0.25：雜亂或缺漏區段。
- 0.0：沒有報告或無法使用。
