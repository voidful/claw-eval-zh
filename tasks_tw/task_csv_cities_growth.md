---
id: task_csv_cities_growth
name: 美國城市地理分布分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_cities_growth
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T075tw_csv_cities_growth
workspace_files:
- source: csvs/us_cities_top1000.csv
  dest: us_cities_top1000.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 美國城市地理分布分析

## Prompt

我的工作區裡有一個 CSV 檔案 `us_cities_top1000.csv`，內含美國人口最多的 1,000 個城市的資料。檔案欄位有：`City`、`State`、`Population`、`lat`、`lon`。

請分析這些城市的地理分布，並把你的發現寫到 `cities_geographic_report.md`。你的報告應包含：

1. **人口地理中心（geographic center of population）**：計算以人口為權重的重心（用人口當權重，對緯度與經度取加權平均）。將其與所有城市位置的簡單未加權重心比較。兩者的差異告訴我們什麼？

2. **地理極值（geographic extremes）**：找出最北、最南、最東、最西的城市。附上它們的座標與人口。

3. **緯度帶分析（latitude band analysis）**：將城市分成每 5° 的緯度帶（低於 30°N、30-35°N、35-40°N、40-45°N、高於 45°N）。對每個帶回報城市數、總人口與平均城市人口。哪個帶城市最多？哪個帶總人口最多？

4. **東西分割（east-west split）**：以經度 -95°W 為分界線，比較全國東半與西半的城市數、總人口與平均城市規模。

5. **各州地理跨幅（state geographic spread）**：對於有 10 個（含）以上城市的州，以最大與最小緯度、經度之間的簡單差距，計算該州任兩城市之間的最大距離（以度為單位）作為地理跨幅。哪些州地理上分布最廣？

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案
2. 計算加權與未加權的地理重心
3. 使用 lat/lon 欄位找出極值位置
4. 依緯度將城市分箱並計算各帶統計
5. 依經度分割並比較兩半
6. 計算各州的地理範圍

關鍵預期數值：

- 人口加權重心：約 (36.99°N, 96.51°W)
- 未加權重心：約 (37.34°N, 96.48°W)
- 最北：Anchorage, Alaska（61.22°N）
- 最南：Honolulu, Hawaii（21.31°N）
- 最東：Portland, Maine（70.26°W）
- 最西：Honolulu, Hawaii（157.86°W）
- 城市最多的緯度帶：40-45°N（316 個城市）
- 總人口最多的帶：30-35°N（38,580,127）
- 95°W 以東：546 個城市，人口 ~67,016,952
- 95°W 以西：454 個城市，人口 ~64,115,491

## Grading Criteria

- [ ] 已建立報告檔案 `cities_geographic_report.md`
- [ ] 已計算人口加權重心（約 37°N、96-97°W）
- [ ] 已計算未加權重心並與加權重心比較
- [ ] 已正確找出全部四個地理極值
- [ ] 緯度帶分析含城市數與人口
- [ ] 已包含東西分割比較
- [ ] 已為符合資格的州計算地理跨幅
- [ ] 已從地理模式中得出關鍵洞見
- [ ] 報告結構清晰、分區明確

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the US cities geographic distribution task.

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

    report_path = workspace / "cities_geographic_report.md"
    if not report_path.exists():
        for alt in ["geographic_report.md", "report.md", "geo_report.md", "cities_report.md",
                     "distribution_report.md", "cities_growth_report.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "weighted_centroid": 0.0,
            "geographic_extremes": 0.0,
            "latitude_bands": 0.0,
            "east_west_split": 0.0,
            "state_spread": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Weighted centroid (~37°N, ~96-97°W)
    centroid_patterns = [
        r'3[67]\.?\d*.*9[67]\.?\d*',
        r'centroid',
        r'weighted\s*(?:average|center|mean)',
        r'center\s*of\s*population',
    ]
    has_centroid_concept = any(re.search(p, content_lower) for p in centroid_patterns[1:])
    has_centroid_values = bool(re.search(r'3[67]\.\d', content))
    scores["weighted_centroid"] = 1.0 if (has_centroid_concept and has_centroid_values) else (0.5 if has_centroid_concept else 0.0)

    # Geographic extremes
    extremes = {
        "anchorage": "anchorage" in content_lower,
        "honolulu": "honolulu" in content_lower,
        "portland_me": bool(re.search(r'portland.*maine', content_lower)),
    }
    extreme_count = sum(extremes.values())
    scores["geographic_extremes"] = 1.0 if extreme_count >= 3 else (0.5 if extreme_count >= 2 else 0.0)

    # Latitude band analysis
    band_patterns = [r'30.*35', r'35.*40', r'40.*45', r'latitude.*band', r'latitude.*zone']
    band_indicators = sum(1 for p in band_patterns if re.search(p, content_lower))
    has_316 = "316" in content  # most cities in 40-45 band
    scores["latitude_bands"] = 1.0 if (band_indicators >= 2 and has_316) else (0.5 if band_indicators >= 2 else 0.0)

    # East-West split
    ew_patterns = [r'east.*west', r'95.*(?:°|degree|longitude)', r'(?:^|\D)546\s*(?:cit|\b)', r'(?:^|\D)454\s*(?:cit|\b)']
    ew_count = sum(1 for p in ew_patterns if re.search(p, content_lower))
    scores["east_west_split"] = 1.0 if ew_count >= 3 else (0.5 if ew_count >= 2 else 0.0)

    # State geographic spread
    spread_patterns = [r'spread', r'extent', r'geographic.*range', r'distance.*between',
                       r'max.*min.*lat', r'latitude.*range']
    scores["state_spread"] = 1.0 if any(re.search(p, content_lower) for p in spread_patterns) else 0.0

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

### 評分項 1：分析正確性（權重 35%）

- 1.0：重心計算正確，極值正確找出（包含 Honolulu 同時為最南與最西），緯度帶與預期計數相符，東西分割準確。
- 0.75：多數計算正確，僅有一兩處小錯。
- 0.5：部分正確，但有多項關鍵計算錯誤。
- 0.25：地理計算有重大錯誤。
- 0.0：沒有正確分析。

### 評分項 2：洞見品質（權重 30%）

- 1.0：從資料得出有意義的結論——例如人口集中於 30-45°N 走廊、人口加權重心相較未加權重心略向南偏移、東西人口大致平衡，以及 Hawaii/Alaska 如何使地理極值偏斜。
- 0.75：對多數區段有良好洞見。
- 0.5：有一些觀察，但漏掉主要模式。
- 0.25：大多是原始數字。
- 0.0：沒有詮釋。

### 評分項 3：完整性（權重 20%）

- 1.0：五個要求的分析皆具備，且處理充分。
- 0.75：所有區段具備，僅有小幅缺漏。
- 0.5：有區段缺漏。
- 0.25：多數區段缺漏。
- 0.0：報告缺漏或空白。

### 評分項 4：報告結構（權重 15%）

- 1.0：組織良好，分區清楚，緯度帶資料以表格呈現，流程合理。
- 0.75：組織良好，僅有小問題。
- 0.5：有分析但組織不佳。
- 0.25：不易閱讀。
- 0.0：沒有報告或無法使用。
