---
id: task_csv_stations_by_elevation
name: 台灣氣象站海拔排名
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
- source: tw/csvs/tw_weather_stations.csv
  dest: tw_weather_stations.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台灣氣象站海拔排名

## Prompt

我的工作區中有一個 CSV 檔 `tw_weather_stations.csv`，內含台灣各地 190 個（虛構的）
氣象與水文觀測站資料。該檔為 UTF-8（含 BOM）編碼，有下列欄位：`OBJECTID`、
`Station Name`（測站名稱）、`Station Code`（測站代碼）、`Managing Agency`
（管理機構）、`County`（所在縣市）、`Longitude`（經度）、`Latitude`（緯度）、
`Elevation (meters)`（海拔，單位為公尺）、`x`、`y`。

請依海拔（elevation）分析這些測站，並將你的發現寫入 `elevation_report.md`。報告
請以繁體中文（zh-TW）撰寫，並包含下列內容：

- **海拔最高的前 10 個測站**，由高至低排名，包含測站名稱、海拔（公尺）、所在縣市
  與管理機構
- **海拔最低的後 10 個測站**，由低至高排名，包含測站名稱、海拔（公尺）、所在縣市
  與管理機構
- **摘要統計**：所有測站的最小、最大、平均與中位數海拔（單位公尺）
- **依管理機構的海拔分布**：比較各管理機構（中央氣象署、林業署、水利署）的平均
  海拔，並解釋為何林業署測站普遍較高、中央氣象署測站普遍較低
- **平均海拔最高的縣市**（僅限有 3 個以上測站的縣市）與平均海拔最低的縣市
  （同樣僅限有 3 個以上測站的縣市）
- 一段簡短的**總結段落**，解讀海拔型態

備註：海拔一律以公尺（meters）為單位，並請以 CSV 內的實際數值為準，不要捏造未
出現在檔案中的數字。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔（190 列，UTF-8 含 BOM）
2. 依 `Elevation (meters)` 欄位排序測站
3. 找出最高測站：玉山主峰測站，3,952 公尺（南投縣，林業署）
4. 找出最低測站：安平海濱潮位站，2 公尺（臺南市，中央氣象署）
5. 計算摘要統計：最小 2、最大 3,952、平均約 961、中位數 575
6. 比較管理機構平均海拔，並解讀林業署（高山林班／野溪測站）普遍高於中央氣象署
   （多位於人口稠密之平原、市區與海濱）的型態
7. 找出縣市層級的海拔型態（以 3 站以上為篩選）
8. 撰寫一份結構良好的 markdown 報告

預期關鍵數值（以 `tw_weather_stations.csv` 實際資料計）：

- 測站總數：190 站（中央氣象署 95 站、林業署 54 站、水利署 41 站）
- 最高：玉山主峰測站，3,952 公尺（南投縣，林業署）
- 第 2~5 高：雪山圈谷站（3,886）、玉山北峰氣象站（3,845）、南湖大山山屋站（3,742）、
  奇萊北峰站（3,607）
- 最低：安平海濱潮位站，2 公尺（臺南市，中央氣象署）
- 海拔範圍：2 公尺 至 3,952 公尺
- 平均海拔：約 961 公尺
- 中位數海拔：575 公尺
- 林業署平均：約 1,890 公尺（54 站）
- 中央氣象署平均：約 432 公尺（95 站）
- 水利署平均：約 963 公尺（41 站）
- 平均海拔最高的縣市（3 站以上）：南投縣，約 1,971 公尺（17 站）
- 平均海拔最低的縣市（3 站以上）：澎湖縣，約 38 公尺（4 站）
- 有 5 列的縣市（County）欄位為空白

## Grading Criteria

- [ ] 已建立報告檔 `elevation_report.md`
- [ ] 列出海拔最高的前 10 站，第 1 正確（玉山主峰測站，3,952 公尺）
- [ ] 列出海拔最低的後 10 站，第 1 正確（安平海濱潮位站，2 公尺）
- [ ] 摘要統計包含最小、最大、平均與中位數（單位公尺）
- [ ] 包含各管理機構（林業署 對比 中央氣象署）海拔比較並附正確平均
- [ ] 含最高／最低平均海拔的縣市層級分析（南投縣最高、澎湖縣最低）
- [ ] 含解讀海拔型態的總結段落

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """台灣氣象站海拔排名 grader。

    所有「應有事實」皆由台灣 CSV tw_weather_stations.csv 動態計算後，再比對 agent
    產出的中文報告 elevation_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import csv
    import re

    workspace = Path(workspace_path)

    checks = ["report_created", "highest_station", "lowest_station",
              "summary_stats", "agency_comparison", "county_analysis",
              "summary_paragraph"]

    # --- 1. 從台灣 CSV 動態算出正解（避免硬寫） ---
    csv_path = workspace / "tw_weather_stations.csv"
    rows = []
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                try:
                    r["_elev"] = int(str(r.get("Elevation (meters)", "")).strip())
                except (ValueError, TypeError):
                    continue
                rows.append(r)

    def _median(vals):
        s = sorted(vals)
        n = len(s)
        if n == 0:
            return 0.0
        if n % 2:
            return float(s[n // 2])
        return (s[n // 2 - 1] + s[n // 2]) / 2.0

    def _mean(vals):
        return sum(vals) / len(vals) if vals else 0.0

    # 預設值（萬一 CSV 缺漏時的保底，數值來自此台灣 CSV）
    highest_name, highest_elev = "玉山主峰測站", 3952
    lowest_name, lowest_elev = "安平海濱潮位站", 2
    elev_min, elev_max = 2, 3952
    elev_mean, elev_median = 961.0, 575.0
    agency_means = {"林業署": 1889.65, "中央氣象署": 432.4, "水利署": 963.0}
    top_county, top_county_mean = "南投縣", 1970.76
    bot_county, bot_county_mean = "澎湖縣", 37.5

    if rows:
        elevs = [r["_elev"] for r in rows]
        shi = sorted(rows, key=lambda r: -r["_elev"])
        slo = sorted(rows, key=lambda r: r["_elev"])
        highest_name = shi[0]["Station Name"].strip()
        highest_elev = shi[0]["_elev"]
        lowest_name = slo[0]["Station Name"].strip()
        lowest_elev = slo[0]["_elev"]
        elev_min, elev_max = min(elevs), max(elevs)
        elev_mean, elev_median = _mean(elevs), _median(elevs)

        # 各管理機構平均
        ag = {}
        for r in rows:
            ag.setdefault(r["Managing Agency"].strip(), []).append(r["_elev"])
        agency_means = {k: _mean(v) for k, v in ag.items()}

        # 各縣市（County）平均，僅限 3 站以上且非空白
        cc = {}
        for r in rows:
            c = r["County"].strip()
            if c:
                cc.setdefault(c, []).append(r["_elev"])
        elig = {c: _mean(v) for c, v in cc.items() if len(v) >= 3}
        if elig:
            top_county = max(elig, key=elig.get)
            top_county_mean = elig[top_county]
            bot_county = min(elig, key=elig.get)
            bot_county_mean = elig[bot_county]

    # 找出機構平均的最高與最低者（用於彈性比對機構差異）
    if agency_means:
        hi_agency = max(agency_means, key=agency_means.get)
        lo_agency = min(agency_means, key=agency_means.get)
    else:
        hi_agency, lo_agency = "林業署", "中央氣象署"

    def _num_variants(value):
        """產生整數值的正則，容許千分位逗號（如 3952 / 3,952）。"""
        iv = int(round(value))
        s = str(iv)
        if len(s) > 3:
            comma = s[:-3] + "," + s[-3:]
            return r"(?:%s|%s)" % (re.escape(s), re.escape(comma))
        return re.escape(s)

    def _near_int(value, tol):
        """產生「value±tol 範圍內任一整數」的比對函式（容許千分位逗號）。"""
        iv = int(round(value))
        cands = list(range(iv - tol, iv + tol + 1))
        def _hit(text):
            for c in cands:
                if re.search(r"(?<!\d)" + _num_variants(c) + r"(?!\d)", text):
                    return True
            return False
        return _hit

    # --- 2. 找出 agent 的報告檔 ---
    report_path = workspace / "elevation_report.md"
    if not report_path.exists():
        for alt in ["elevation.md", "report.md", "stations_elevation.md",
                    "analysis.md", "海拔報告.md", "海拔分析.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in checks}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 3. 逐項比對中文關鍵字／數值 ---
    # 最高測站：名稱 + 海拔數值。
    has_hi_name = highest_name in content
    has_hi_val = bool(re.search(
        r"(?<!\d)" + _num_variants(highest_elev) + r"(?!\d)", content))
    scores["highest_station"] = (
        1.0 if (has_hi_name and has_hi_val)
        else (0.5 if (has_hi_name or has_hi_val) else 0.0))

    # 最低測站：名稱 + 海拔數值。
    has_lo_name = lowest_name in content
    has_lo_val = bool(re.search(
        r"(?<!\d)" + _num_variants(lowest_elev) + r"(?!\d)", content))
    scores["lowest_station"] = (
        1.0 if (has_lo_name and has_lo_val)
        else (0.5 if (has_lo_name or has_lo_val) else 0.0))

    # 摘要統計：最小、最大、平均、中位數，命中 3 項以上滿分。
    stats_found = 0
    if re.search(r"(?<!\d)" + _num_variants(elev_min) + r"(?!\d)", content):
        stats_found += 1
    if re.search(r"(?<!\d)" + _num_variants(elev_max) + r"(?!\d)", content):
        stats_found += 1
    if _near_int(elev_mean, 3)(content):   # 平均約 961
        stats_found += 1
    if _near_int(elev_median, 1)(content):  # 中位數 575
        stats_found += 1
    scores["summary_stats"] = min(1.0, stats_found / 3.0)

    # 機構比較：須出現平均最高與最低機構名稱，且各自平均數值接近正解。
    has_hi_agency_name = hi_agency in content
    has_lo_agency_name = lo_agency in content
    has_hi_agency_val = _near_int(agency_means[hi_agency], 5)(content)
    has_lo_agency_val = _near_int(agency_means[lo_agency], 5)(content)
    agency_names_ok = has_hi_agency_name and has_lo_agency_name
    agency_vals_ok = has_hi_agency_val and has_lo_agency_val
    scores["agency_comparison"] = (
        1.0 if (agency_names_ok and agency_vals_ok)
        else (0.5 if agency_names_ok else 0.0))

    # 縣市分析：須出現「縣／市」字樣與平均海拔最高／最低的縣市名。
    county_kw = bool(re.search(r"縣|市", content))
    has_top_county = top_county in content
    has_bot_county = bot_county in content
    county_found = (
        (1 if county_kw else 0)
        + (1 if has_top_county else 0)
        + (1 if has_bot_county else 0))
    scores["county_analysis"] = (
        1.0 if county_found >= 3
        else (0.5 if county_found >= 1 else 0.0))

    # 總結／解讀段落：須有總結字樣，並對高海拔（林業署／高山）與低海拔
    # （中央氣象署／平原海濱）型態作出解讀。
    summary_kw = bool(re.search(
        r"總結|結論|摘要|解讀|型態|分布|綜觀|整體", content))
    high_pattern = bool(re.search(
        r"(?:林業署|高山|山區|稜線|野溪|林班).{0,40}"
        r"(?:高|海拔較高|地勢高|偏高)", content)) or bool(re.search(
        r"(?:高|海拔較高|地勢高|偏高).{0,40}(?:林業署|高山|山區|稜線)",
        content))
    low_pattern = bool(re.search(
        r"(?:中央氣象署|平原|市區|海濱|沿海|低地).{0,40}"
        r"(?:低|海拔較低|地勢低|偏低)", content)) or bool(re.search(
        r"(?:低|海拔較低|地勢低|偏低).{0,40}"
        r"(?:中央氣象署|平原|市區|海濱|沿海)", content))
    summary_found = (
        (1 if summary_kw else 0)
        + (1 if high_pattern else 0)
        + (1 if low_pattern else 0))
    scores["summary_paragraph"] = (
        1.0 if summary_found >= 2
        else (0.5 if summary_found >= 1 else 0.0))

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

**1.0 分**：所有排名皆正確，統計準確（平均約 961、中位數 575、前／後 10 正確），
且各管理機構平均符合預期值（林業署約 1,890、中央氣象署約 432、水利署約 963）。
**0.75 分**：排名與統計大致正確，僅有小幅落差（例如平均差幾公尺）。
**0.5 分**：最高與最低測站正確，但中間排名或統計有錯誤。
**0.25 分**：排名或統計有數個重大錯誤。
**0.0 分**：未嘗試分析或根本性錯誤。

### 評分項 2：分析深度（權重 30%）

**1.0 分**：對各機構差異提供具意義的解讀（林業署測站多為高山林班、稜線、野溪等
高海拔監測點，中央氣象署測站多位於有人口的平原、市區與海濱）、縣市型態，以及
海拔分布洞見。
**0.75 分**：解讀良好，僅在說明機構差異上有小缺漏。
**0.5 分**：陳述事實，但解讀或洞見有限。
**0.25 分**：除列出數字外幾無分析。
**0.0 分**：未提供任何分析或解讀。

### 評分項 3：報告完整性（權重 20%）

**1.0 分**：所有要求章節皆齊備：前 10、後 10、摘要統計、機構比較、縣市分析、
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
