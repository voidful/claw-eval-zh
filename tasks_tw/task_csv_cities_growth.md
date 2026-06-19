---
id: task_csv_cities_growth
name: 台灣鄉鎮市區地理分布分析
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
- source: tw/csvs/tw_townships.csv
  dest: tw_townships.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台灣鄉鎮市區地理分布分析

## Prompt

我的工作區裡有一個 CSV 檔案 `tw_townships.csv`，內含台灣 204 個鄉鎮市區的資料。
檔案欄位有：`Township`（鄉鎮市區名）、`County`（所屬縣市）、`Population`（人口）、
`lat`（緯度，單位為度）、`lon`（經度，單位為度）。

請分析這些鄉鎮市區的地理分布，並把你的發現寫到 `townships_geographic_report.md`。
你的報告應包含下列五個部分：

1. **人口地理中心（人口加權重心）**：以人口為權重，對緯度與經度取加權平均，計算
   人口加權重心。再計算所有鄉鎮市區位置的簡單未加權重心（不以人口加權），並與
   加權重心比較。兩者的差異告訴我們什麼？

2. **地理極值**：找出最北、最南、最東、最西的鄉鎮市區。請附上它們所屬的縣市、
   座標與人口。

3. **緯度帶分析**：將鄉鎮市區依緯度切成每 1° 的緯度帶（低於 23°N、23-24°N、
   24-25°N、25-26°N、26°N 以上）。對每一帶回報鄉鎮市區數、總人口與平均人口。
   哪一帶的鄉鎮市區最多？哪一帶的總人口最多？

4. **東西分割**：以經度 121°E 為分界線，比較全臺東半部（≥121°E）與西半部
   （<121°E）的鄉鎮市區數、總人口與平均規模。

5. **各縣市地理跨幅**：對於擁有 10 個（含）以上鄉鎮市區的縣市，以該縣市內所有
   鄉鎮市區的最大緯度與最小緯度之差（Δlat）、最大經度與最小經度之差（Δlon），
   計算對角跨幅 `sqrt(Δlat² + Δlon²)`（單位為度）作為地理跨幅。哪些縣市地理上
   分布最廣？哪個最集中？

注意：CSV 檔名、欄名與報告檔名 `townships_geographic_report.md` 請勿更改；數值
一律以 CSV 內實際資料計算，不要捏造未出現在檔案中的數字。

## Expected Behavior

助手應讀取並解析 `tw_townships.csv`（204 個鄉鎮市區、22 縣市、總人口 19,275,800），
計算加權與未加權重心、找出極值、依緯度分箱、依經度分割並計算各縣市跨幅，最後寫出
結構清晰的中文報告。

關鍵預期數值（已由程式從 fixture 實算，可重現）：

- 人口加權重心：約 (24.29°N, 120.98°E)；未加權重心：約 (24.08°N, 120.82°E)。
  加權重心相較未加權重心往北、往東偏移（Δlat 約 +0.21°、Δlon 約 +0.16°），反映
  人口較集中於中北部與西部走廊（如雙北、桃園、臺中、高雄等都會區）。
- 最北：連江縣 東引鄉（約 26.37°N）。
- 最南：屏東縣 恆春鎮（約 22.00°N）。
- 最東：新北市 貢寮區（約 121.91°E）。
- 最西：金門縣 烈嶼鄉（約 118.24°E）。
- 緯度帶分析：鄉鎮市區最多的帶與總人口最多的帶都是 24-25°N（76 個 / 7,887,200 人）。
  其餘各帶：低於 23°N 為 35 個 / 3,090,500 人；23-24°N 為 55 個 / 2,732,100 人；
  25-26°N 為 35 個 / 5,553,600 人；26°N 以上為 3 個 / 12,400 人。
- 東西分割（121°E）：東半部（≥121°E）84 個、總人口約 10,162,500；西半部（<121°E）
  120 個、總人口約 9,113,300。西半部鄉鎮數較多，但東半部因含雙北、宜蘭、花東等
  較大都會區，總人口反而略高。
- 各縣市地理跨幅（共 7 個縣市達 ≥10 個鄉鎮市區：新北、臺中、高雄、臺北、桃園、臺南、
  彰化）：跨幅最大為高雄市（約 0.78°），其次為新北市（約 0.63°）、臺中市（約 0.50°）、
  臺南市（約 0.48°）；跨幅最小（最集中）為臺北市（約 0.18°）。高雄市因含旗津到那瑪夏
  的山海跨距而分布最廣。

## Grading Criteria

- [ ] 已建立報告檔案 `townships_geographic_report.md`
- [ ] 已計算人口加權重心（約 24.29°N、120.98°E）
- [ ] 已計算未加權重心並與加權重心比較（加權偏北偏東）
- [ ] 已正確找出四個地理極值（最北連江、最南屏東、最東新北、最西金門）
- [ ] 緯度帶分析含各帶鄉鎮數與人口，並指出 24-25°N 同時是鄉鎮最多與總人口最多的帶
- [ ] 已包含以 121°E 為界的東西分割比較（西半部鄉鎮較多、東半部總人口略高）
- [ ] 已為符合資格（≥10 鄉鎮）的縣市計算地理跨幅，並指出高雄市最廣、臺北市最集中
- [ ] 已從地理模式中得出關鍵洞見
- [ ] 報告結構清晰、分區明確

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """台灣鄉鎮市區地理分布 grader。

    正解一律從工作區內的 tw_townships.csv 動態計算（不沿用任何原版英文數值），
    再比對 agent 產生的中文報告 townships_geographic_report.md。報告為中文，
    故以中文關鍵字／數值比對。轉換器會在其後接上中→英正規化 wrapper。
    """
    from pathlib import Path
    import csv as _csv
    import re
    import math

    workspace = Path(workspace_path)

    report_path = workspace / "townships_geographic_report.md"
    if not report_path.exists():
        for alt in ["geographic_report.md", "townships_report.md", "report.md",
                    "geo_report.md", "cities_geographic_report.md",
                    "townships_geographic.md", "distribution_report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = ["report_created", "weighted_centroid", "geographic_extremes",
            "latitude_bands", "east_west_split", "county_spread"]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    content = report_path.read_text(encoding="utf-8", errors="ignore")
    low = content.lower()

    # --- 從 CSV 動態計算正解 ---
    csv_path = workspace / "tw_townships.csv"
    rows = []
    if csv_path.exists():
        with csv_path.open(encoding="utf-8", errors="ignore") as f:
            for r in _csv.DictReader(f):
                try:
                    rows.append({
                        "name": r["Township"], "county": r["County"],
                        "pop": int(r["Population"]),
                        "lat": float(r["lat"]), "lon": float(r["lon"]),
                    })
                except (KeyError, ValueError):
                    pass

    # 預設（萬一 CSV 缺失，仍給可運作的回退值，對應目前 fixture 實算結果）
    most_band_count = 76
    ew_east_count, ew_west_count = 84, 120
    north_county = south_county = east_county = west_county = ""
    widest_county = "高雄"
    narrow_county = "臺北"
    w_lat = w_lon = u_lat = u_lon = None
    if rows:
        n = len(rows)
        totpop = sum(r["pop"] for r in rows)
        w_lat = sum(r["lat"] * r["pop"] for r in rows) / totpop
        w_lon = sum(r["lon"] * r["pop"] for r in rows) / totpop
        u_lat = sum(r["lat"] for r in rows) / n
        u_lon = sum(r["lon"] for r in rows) / n

        north_county = max(rows, key=lambda r: r["lat"])["county"]
        south_county = min(rows, key=lambda r: r["lat"])["county"]
        east_county = max(rows, key=lambda r: r["lon"])["county"]
        west_county = min(rows, key=lambda r: r["lon"])["county"]

        def band(lat):
            if lat < 23:
                return 0
            if lat < 24:
                return 1
            if lat < 25:
                return 2
            if lat < 26:
                return 3
            return 4
        bcount = [0, 0, 0, 0, 0]
        bpop = [0, 0, 0, 0, 0]
        for r in rows:
            b = band(r["lat"])
            bcount[b] += 1
            bpop[b] += r["pop"]
        most_band_idx = max(range(5), key=lambda i: bcount[i])
        most_band_count = bcount[most_band_idx]

        DIV = 121.0
        ew_east_count = sum(1 for r in rows if r["lon"] >= DIV)
        ew_west_count = sum(1 for r in rows if r["lon"] < DIV)

        groups = {}
        for r in rows:
            groups.setdefault(r["county"], []).append(r)
        spreads = []
        for cty, rs in groups.items():
            if len(rs) < 10:
                continue
            lats = [r["lat"] for r in rs]
            lons = [r["lon"] for r in rs]
            sp = math.hypot(max(lats) - min(lats), max(lons) - min(lons))
            spreads.append((cty, sp))
        if spreads:
            spreads.sort(key=lambda x: -x[1])
            widest_county = spreads[0][0]
            narrow_county = spreads[-1][0]

    def has_any(*subs):
        return any(s and s in content for s in subs)

    def in_report(county):
        # 去掉「縣／市」字尾後也接受，報告可能只寫「花蓮」
        if not county:
            return False
        return county in content or county.rstrip("縣市") in content

    scores = {"report_created": 1.0}

    # 1) 加權重心：概念 + 數值（接近實算的加權緯度／經度）+ 與未加權比較。
    # 數值門檻一律以 CSV 實算的加權重心為準（±0.3° 容差），不寫死任何座標。
    centroid_concept = bool(re.search(r"加權|重心|人口.*中心|中心.*人口", content))
    nums = [float(x) for x in re.findall(r"\d{1,3}\.\d+", content)]
    if w_lat is not None:
        lat_val = any(abs(v - w_lat) <= 0.3 for v in nums)
        lon_val = any(abs(v - w_lon) <= 0.3 for v in nums)
    else:
        # 回退：CSV 缺失時退回對目前 fixture 的寬鬆範圍比對
        lat_val = bool(re.search(r"24\.[0-5]\d*", content))
        lon_val = bool(re.search(r"120\.[8-9]\d*|121\.0", content))
    unweighted = bool(re.search(r"未加權|簡單.*重心|不加權|未以.*加權", content))
    if centroid_concept and lat_val and lon_val and unweighted:
        scores["weighted_centroid"] = 1.0
    elif centroid_concept and (lat_val or lon_val):
        scores["weighted_centroid"] = 0.5
    else:
        scores["weighted_centroid"] = 0.0

    # 2) 地理極值：四個方向所屬縣市，皆由 CSV 動態判定（目前為最北連江、
    #    最南屏東、最東新北、最西金門），報告須同時寫出方向詞與正確縣市。
    ext = 0
    ext += 1 if (re.search(r"最北", content) and in_report(north_county)) else 0
    ext += 1 if (re.search(r"最南", content) and in_report(south_county)) else 0
    ext += 1 if (re.search(r"最東", content) and in_report(east_county)) else 0
    ext += 1 if (re.search(r"最西", content) and in_report(west_county)) else 0
    scores["geographic_extremes"] = 1.0 if ext >= 4 else (0.5 if ext >= 2 else 0.0)

    # 3) 緯度帶：帶標籤 ≥2 + 最多帶數值
    band_hits = sum(1 for p in [r"23.{0,3}24", r"24.{0,3}25", r"25.{0,3}26",
                                r"緯度帶", r"緯度.*分"] if re.search(p, content))
    has_most = str(most_band_count) in content
    if band_hits >= 2 and has_most:
        scores["latitude_bands"] = 1.0
    elif band_hits >= 2:
        scores["latitude_bands"] = 0.5
    else:
        scores["latitude_bands"] = 0.0

    # 4) 東西分割：東/西概念 + 121 分界 + 兩半計數
    ew = 0
    ew += 1 if re.search(r"東半|西半|東西|東.*西.*分|分.*東.*西", content) else 0
    ew += 1 if re.search(r"121", content) else 0
    ew += 1 if str(ew_east_count) in content else 0
    ew += 1 if str(ew_west_count) in content else 0
    scores["east_west_split"] = 1.0 if ew >= 3 else (0.5 if ew >= 2 else 0.0)

    # 5) 縣市跨幅：跨幅概念 + 最廣縣市（由 CSV 動態判定，目前為高雄）
    #    + 最集中縣市（目前為臺北），兩者皆從 fixture 實算後比對報告。
    #    為避免「把答案對調」也拿滿分，這裡要求方向詞與縣市名在鄰近範圍內
    #    出現（任一語序皆可），亦即最廣縣市須緊鄰「最廣／分布最廣」等敘述、
    #    最集中縣市須緊鄰「最集中／最密／分布最窄」等敘述。
    spread_concept = bool(re.search(r"跨幅|分布.*廣|地理.*範圍|範圍|對角|最廣|分散", content))

    def _county_forms(county):
        # 同時接受「高雄市」與「高雄」兩種寫法。
        if not county:
            return None
        short = county.rstrip("縣市")
        forms = {county, short}
        return "(?:" + "|".join(re.escape(f) for f in forms if f) + ")"

    def attributed(county, desc_pat, window=12):
        # 縣市名與方向敘述須在 window 字元內共現（任一語序），避免對調作答得分。
        # gap 內不得跨越標點（，。、；！？換行或表格分隔），以免兩個對調子句
        # 互相沾染（例如「跨幅最廣的是臺北市，最集中的是高雄市」不應讓高雄被判為最廣）。
        cf = _county_forms(county)
        if not cf:
            return False
        gap = r"[^，。、；！？\n\r|]{0,%d}" % window
        return bool(
            re.search(cf + gap + desc_pat, content)
            or re.search(desc_pat + gap + cf, content)
        )

    # 最廣縣市須與「最廣／分布最廣／跨幅最大／範圍最大」等敘述鄰近共現。
    widest_desc = r"(?:最廣|分布最廣|跨幅最大|範圍最大|跨距最大|分布範圍最大)"
    # 最集中縣市須與「最集中／最密／分布最窄／跨幅最小」等敘述鄰近共現。
    narrow_desc = r"(?:最集中|最密集|最密|分布最窄|範圍最小|跨幅最小|跨距最小|最緊密)"
    widest_ok = attributed(widest_county, widest_desc)
    narrow_ok = attributed(narrow_county, narrow_desc)
    if spread_concept and widest_ok and narrow_ok:
        scores["county_spread"] = 1.0
    elif spread_concept and (widest_ok or narrow_ok):
        scores["county_spread"] = 0.5
    else:
        scores["county_spread"] = 0.0

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

- 1.0：重心計算正確（加權約 24.29°N/120.98°E、未加權約 24.08°N/120.82°E），四個
  極值正確找出（最北連江縣東引鄉、最南屏東縣恆春鎮、最東新北市貢寮區、最西金門縣
  烈嶼鄉），緯度帶計數與預期相符（24-25°N 共 76 個，同時為鄉鎮最多與總人口最多的
  帶），東西分割準確（西半 120 個、東半 84 個，東半部總人口略高）。
- 0.75：多數計算正確，僅有一兩處小錯。
- 0.5：部分正確，但有多項關鍵計算錯誤。
- 0.25：地理計算有重大錯誤。
- 0.0：沒有正確分析。

### 評分項 2：洞見品質（權重 30%）

- 1.0：從資料得出有意義的結論——例如人口集中於 24-25°N 的中北部走廊、加權重心相較
  未加權重心往北往東偏移代表人口重心偏向雙北桃竹與中部都會區、東西分割顯示西半部
  鄉鎮較多但東半部因含雙北與宜花東較大行政區而總人口反略高，以及離島（連江、金門）
  與恆春半島如何拉開地理極值。
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
