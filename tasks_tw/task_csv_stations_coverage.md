---
id: task_csv_stations_coverage
name: 全臺氣象站涵蓋缺口分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_stations_coverage
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T067tw_csv_stations_coverage
workspace_files:
- source: tw/csvs/tw_weather_stations.csv
  dest: tw_weather_stations.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 全臺氣象站涵蓋缺口分析

## Prompt

我的工作區裡有一個 CSV 檔 `tw_weather_stations.csv`，內含全臺 190 個氣象站的
資料（虛構資料集，仿台灣公開氣象測站格式）。檔案欄位有：`OBJECTID`、
`Station Name`（測站名稱）、`Station Code`（測站編號）、`Managing Agency`
（管理機關）、`County`（縣市）、`Longitude`（經度）、`Latitude`（緯度）、
`Elevation (meters)`（海拔，單位為公尺）、`x`、`y`。

台灣共有 22 個直轄市／縣／市（六都：臺北市、新北市、桃園市、臺中市、臺南市、
高雄市；十三縣：宜蘭縣、新竹縣、苗栗縣、彰化縣、南投縣、雲林縣、嘉義縣、屏東縣、
臺東縣、花蓮縣、澎湖縣、金門縣、連江縣；三市：基隆市、新竹市、嘉義市）。

請分析這個氣象站網路的地理與海拔涵蓋情況，並把你的發現寫到 `coverage_report.md`。
你的報告應包含：

- **縣市涵蓋**：台灣的 22 個縣市中，有多少個縣市至少有一個氣象站？哪一個
  （或哪些）縣市完全沒有氣象站？
- **各縣市氣象站密度**：哪些縣市的氣象站最多、哪些（在有氣象站的縣市之中）最少？
- **海拔帶分布**：把氣象站依海拔分組（例如以 500 公尺或 1,000 公尺為一段），
  統計每個海拔帶各有多少個氣象站。指出哪些海拔帶涵蓋過多、哪些涵蓋不足。
- **機關涵蓋比較**：中央氣象署、林業署與水利署在氣象站布點上的地理／海拔差異
  為何？哪些縣市只由單一機關服務、哪些由多個機關共同服務？
- **資料品質問題**：找出任何縣市別資料缺漏或空白的氣象站。
- 一個**建議區段**：說明在哪些地方增設氣象站能改善涵蓋。

請以 CSV 內的實際數值為準，不要捏造未出現在檔案中的數字。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔（190 列）
2. 將氣象站的縣市別與台灣的 22 個直轄市／縣／市交叉比對
3. 發現 22 個縣市中有 21 個有氣象站；連江縣完全沒有氣象站
4. 注意到有 5 個氣象站的縣市別資料空白／缺漏
5. 找出氣象站最多的縣市：南投縣（17）、花蓮縣（14）、高雄市（14）、臺中市（13）、
   臺東縣（13）、宜蘭縣（13）
6. 找出只有單一氣象站的縣市：基隆市、新竹市、金門縣
7. 建立海拔帶分布，呈現氣象站集中在 1,000 公尺以下的低海拔區間
8. 比較中央氣象署（95 個站，海拔較低，平均約 432 公尺）、林業署（54 個站，海拔較高，
   平均約 1,890 公尺）與水利署（41 個站，中海拔，平均約 963 公尺）
9. 撰寫一份結構清晰、含建議的報告

關鍵預期數值（以 `tw_weather_stations.csv` 實際資料計）：

- 氣象站總數：190
- 有氣象站的縣市：22 個中有 21 個（以縣市別非空白者計則為 21 個）
- 缺漏的縣市：連江縣完全沒有氣象站
- 有 5 個氣象站的縣市別欄位空白（大霸尖山站、拉拉山野溪站、南湖大山林道站、
  玉山保線所站、關山山站）
- 氣象站最多：南投縣（17 個站）
- 只有單一氣象站的縣市：基隆市、新竹市、金門縣
- 機關分布：中央氣象署（95 個站）、林業署（54 個站）、水利署（41 個站）
- 海拔帶分布（500 公尺一段）：0-500 公尺（94 個站，最密集）、500-1,000 公尺
  （29 個站）、1,000-1,500 公尺（24 個站）、1,500-2,000 公尺（11 個站）、
  2,000-2,500 公尺（15 個站）、2,500-3,000 公尺（3 個站，最稀疏）、
  3,000-3,500 公尺（8 個站）、3,500-4,000 公尺（6 個站）
- 涵蓋過多的海拔帶：0-1,000 公尺（低海拔共 123 個站，約占 65%）
- 涵蓋稀疏的海拔帶：2,500-3,000 公尺（僅 3 個站）、3,500 公尺以上（僅 6 個站）
- 機關海拔差異：林業署多設於高山（平均約 1,890 公尺，海拔 2,000 公尺以上的站
  多由林業署管理），中央氣象署多設於平地與沿海（平均約 432 公尺，海拔 500 公尺
  以下的站約八成由中央氣象署管理），水利署居中（平均約 963 公尺）
- 只由中央氣象署服務的縣市：臺北市、基隆市、新竹市、嘉義市、澎湖縣、金門縣
  （多為都會區或離島）

## Grading Criteria

- [ ] 已建立報告檔 `coverage_report.md`
- [ ] 已指出連江縣沒有氣象站（22 個縣市中有 21 個有站）
- [ ] 已列出各縣市氣象站數，且氣象站最多的南投縣（17）正確
- [ ] 已包含海拔帶分布，並指出低海拔（1,000 公尺以下）涵蓋最密集
- [ ] 已包含中央氣象署、林業署、水利署的地理／海拔比較
- [ ] 已指出縣市別資料缺漏（5 個站空白）
- [ ] 有建議區段

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """全臺氣象站涵蓋缺口分析 grader（台灣 CSV）。

    以工作區內的台灣 CSV（dest=tw_weather_stations.csv）動態計算「應有的
    涵蓋／密度／海拔／機關」正解，再比對 agent 產出的中文報告 coverage_report.md。
    不沿用原始美國資料集數值。僅用標準函式庫。
    轉換器會在其後自動接上中→英正規化 wrapper，毋須自行處理。
    """
    from pathlib import Path
    import csv as _csv
    import re
    from collections import Counter

    workspace = Path(workspace_path)
    keys = [
        "report_created", "missing_county_identified", "county_counts",
        "elevation_bands", "agency_comparison", "missing_data", "recommendations",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report_path = workspace / "coverage_report.md"
    if not report_path.exists():
        for alt in ["coverage.md", "report.md", "gap_analysis.md", "analysis.md",
                    "coverage_analysis.md", "涵蓋分析.md", "涵蓋報告.md",
                    "氣象站涵蓋分析.md", "coverage_report.txt"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    content = report_path.read_text(encoding="utf-8", errors="ignore")
    content_lower = content.lower()
    scores = {"report_created": 1.0}

    # --- 從台灣 CSV 動態讀出正解（避免硬寫；以實際 fixture 為準） ---
    csv_path = workspace / "tw_weather_stations.csv"
    if not csv_path.exists():
        for alt in ["weather_stations.csv", "stations.csv"]:
            if (workspace / alt).exists():
                csv_path = workspace / alt
                break

    rows = []
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig", errors="ignore") as f:
            reader = _csv.DictReader(f)
            for r in reader:
                rows.append({(k or "").strip(): (v.strip() if v else "")
                             for k, v in r.items()})

    # 台灣 22 個直轄市／縣／市
    tw22 = [
        "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
        "宜蘭縣", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
        "屏東縣", "臺東縣", "花蓮縣", "澎湖縣", "金門縣", "連江縣",
        "基隆市", "新竹市", "嘉義市",
    ]

    counties = [r.get("County", "") for r in rows]
    nonblank = [c for c in counties if c]
    blank_rows = [r for r in rows if not r.get("County", "")]
    cc = Counter(nonblank)
    present = set(nonblank)
    missing_counties = [c for c in tw22 if c not in present]  # 應為 ['連江縣']
    top_counties = [c for c, _ in cc.most_common(6)]          # 南投縣居首
    single_counties = sorted([c for c, n in cc.items() if n == 1])
    n_blank = len(blank_rows)                                 # 應為 5
    blank_station_names = [r.get("Station Name", "") for r in blank_rows]

    # 若 CSV 缺失，退回硬編碼正解（以實際 fixture 計算所得）作為保底
    if not rows:
        missing_counties = ["連江縣"]
        top_counties = ["南投縣", "花蓮縣", "高雄市", "臺中市", "臺東縣", "宜蘭縣"]
        single_counties = ["基隆市", "新竹市", "金門縣"]
        cc = Counter({"南投縣": 17})
        n_blank = 5
        blank_station_names = ["大霸尖山站", "拉拉山野溪站", "南湖大山林道站",
                               "玉山保線所站", "關山山站"]

    # === 1. 缺漏縣市（連江縣）已被指認 ===
    miss_score = 0.0
    for mc in missing_counties:
        if mc and mc in content:
            # 報告中應指出此縣市「沒有／零」氣象站
            near = re.search(re.escape(mc) + r"[^。\n]{0,40}(?:沒有|零|0|缺|無|未設|不足)",
                             content)
            near2 = re.search(r"(?:沒有|零|缺|無|未設)[^。\n]{0,40}" + re.escape(mc),
                              content)
            miss_score = 1.0 if (near or near2) else 0.6
            break
    scores["missing_county_identified"] = miss_score

    # === 2. 各縣市氣象站數，且最多的縣市（南投縣 17）正確 ===
    # 取實際前五多縣市，檢查報告中縣市名旁是否出現對應正確計數。
    top5 = cc.most_common(5)
    hit = 0
    for cname, cnum in top5:
        # 縣市名出現，且其正確計數（cnum）也出現在縣市名附近（任一方向，60 字內）
        pat1 = re.escape(cname) + r"[^\n]{0,60}\b" + str(cnum) + r"\b"
        pat2 = r"\b" + str(cnum) + r"\b[^\n]{0,30}" + re.escape(cname)
        if re.search(pat1, content) or re.search(pat2, content):
            hit += 1
    if hit >= 3:
        scores["county_counts"] = 1.0
    elif hit >= 1:
        scores["county_counts"] = 0.5
    else:
        scores["county_counts"] = 0.0

    # === 3. 海拔帶分布 ===
    elev_indicators = 0
    # 「海拔」要與分組概念詞鄰近（同一段、30 字內），避免「氣象站分布在全臺」
    # 之類泛用「分布」誤觸。
    if re.search(r"海拔[^\n]{0,30}(?:帶|分組|區間|級距)"
                 r"|(?:海拔)?(?:帶|分組|區間|級距)[^\n]{0,12}海拔"
                 r"|海拔[^\n]{0,12}分布", content):
        elev_indicators += 1
    # 出現多個海拔分組數字（公尺刻度）
    if re.search(r"(?:500|1[,.]?000|1[,.]?500|2[,.]?000|3[,.]?000)\s*(?:公尺|m|公里)?",
                 content):
        elev_indicators += 1
    # 指出低海拔密集 / 高海拔稀疏（涵蓋過多／不足）
    if (re.search(r"(?:低海拔|1[,.]?000\s*公尺以下|0[\-－~～]500)", content)
            and re.search(r"(?:集中|密集|最多|過多|偏多)", content)) or \
       re.search(r"(?:稀疏|不足|偏少|稀少|涵蓋過少)", content):
        elev_indicators += 1
    if elev_indicators >= 2:
        scores["elevation_bands"] = 1.0
    elif elev_indicators >= 1:
        scores["elevation_bands"] = 0.5
    else:
        scores["elevation_bands"] = 0.0

    # === 4. 機關比較（中央氣象署 / 林業署 / 水利署） ===
    agencies = Counter(r.get("Managing Agency", "") for r in rows if r)
    # 實際三大機關名稱（取出現的機關）
    agency_names = [a for a, _ in agencies.most_common() if a] or \
        ["中央氣象署", "林業署", "水利署"]
    agency_hit = sum(1 for a in agency_names[:3] if a and a in content)
    # 機關計數是否出現（任一機關名旁有其正確站數）
    count_hit = False
    for a, n in agencies.most_common(3):
        if a and re.search(re.escape(a) + r"[^\n]{0,40}\b" + str(n) + r"\b", content):
            count_hit = True
            break
    # 海拔／地理差異敘述
    geo_hit = bool(re.search(r"(?:平地|沿海|低海拔|高山|山區|高海拔|流域|中海拔)",
                             content))
    if agency_hit >= 2 and (count_hit or geo_hit):
        scores["agency_comparison"] = 1.0
    elif agency_hit >= 2:
        scores["agency_comparison"] = 0.5
    else:
        scores["agency_comparison"] = 0.0

    # === 5. 資料品質：縣市別空白的氣象站已被指認 ===
    md_score = 0.0
    # 報告提到「空白／缺漏的縣市別」與站數，或直接點名空白站
    name_hits = sum(1 for nm in blank_station_names if nm and nm in content)
    mentions_blank = bool(re.search(r"(?:縣市|county)[^\n]{0,20}"
                                    r"(?:空白|缺漏|缺失|遺漏|未填|無資料|空缺)", content)
                          or re.search(r"(?:空白|缺漏|缺失|遺漏|未填|空缺)[^\n]{0,20}"
                                       r"(?:縣市|county)", content))
    mentions_count = bool(re.search(r"\b" + str(n_blank) + r"\b[^\n]{0,20}"
                                    r"(?:個|站|筆|個站)", content)
                          and mentions_blank)
    if name_hits >= 3 or mentions_count:
        md_score = 1.0
    elif mentions_blank or name_hits >= 1:
        md_score = 0.6
    scores["missing_data"] = md_score

    # === 6. 建議區段 ===
    rec_patterns = [
        r"建議", r"增設", r"增點", r"補強", r"改善[^\n]{0,10}涵蓋",
        r"新增[^\n]{0,10}(?:氣象站|測站|站)", r"加強",
    ]
    scores["recommendations"] = 1.0 if any(re.search(p, content)
                                           for p in rec_patterns) else 0.0

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

- 1.0：正確指出 22 個縣市中有 21 個有氣象站，點名連江縣為缺漏的縣市，提供各縣市
  正確的氣象站數（南投縣 17 最多），並正確找出 5 個縣市別缺漏的氣象站。
- 0.75：多數涵蓋事實正確，僅有一兩處小錯（例如某縣市計數略有偏差）。
- 0.5：找出部分缺口，但漏掉連江縣或有多處計數錯誤。
- 0.25：嘗試做涵蓋分析，但有重大事實錯誤。
- 0.0：沒有涵蓋分析，或完全錯誤。

### 評分項 2：海拔分布品質（權重 25%）

- 1.0：海拔帶劃分清楚且計數正確，指出 1,000 公尺以下低海拔的集中現象（約占
  三分之二），並注意到 2,500-3,000 公尺與 3,500 公尺以上涵蓋稀疏。
- 0.75：海拔帶劃分良好，僅有小幅計數錯誤。
- 0.5：有做海拔分組，但不完整或有錯誤。
- 0.25：海拔分析極少。
- 0.0：完全沒有海拔分布。

### 評分項 3：機關分析（權重 20%）

- 1.0：清楚說明中央氣象署、林業署與水利署在地理／海拔上的分布差異（中央氣象署
  設於平地與沿海、林業署設於高山以監測山區、水利署多在流域中海拔），指出只由
  單一機關服務的縣市（如臺北市、離島等只由中央氣象署服務），並提供差異成因的洞見。
- 0.75：機關比較良好，僅有小幅缺漏。
- 0.5：提到多個機關，但比較有限。
- 0.25：機關討論極少。
- 0.0：完全沒有機關分析。

### 評分項 4：建議品質（權重 20%）

- 1.0：提出具體、可執行且緊扣已發現缺口的建議（例如在連江縣增設氣象站、補強
  2,500-3,000 公尺中高海拔的稀疏涵蓋、為基隆市／新竹市／金門縣等單站縣市增點、
  補上 5 個空白的縣市別資料）。
- 0.75：建議良好，具一定具體性。
- 0.5：建議籠統，未緊扣具體發現。
- 0.25：建議模糊或無助益。
- 0.0：沒有建議區段。
