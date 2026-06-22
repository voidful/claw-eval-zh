---
id: task_meeting_advisory_technical
name: 智慧城市暨資安顧問委員會：頻譜共用技術討論
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_advisory_technical
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T122tw_meeting_advisory_technical
workspace_files:
- source: tw/meetings/tw_advisory_meeting.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 智慧城市暨資安顧問委員會：頻譜共用技術討論

## Prompt

工作區裡有一份政府顧問委員會會議的逐字稿，存放在 `meeting-transcript.md`。
這是虛構的「數位治理委員會 智慧城市暨資安顧問委員會（DGC-SCAB）」第 14 次會議
（時間 2025 年 5 月 30 日，時區 Asia/Taipei，地點台北市南港），主軸是
1755-1850 MHz 這段聯邦級頻段，政府單位與商用行動寬頻要如何共用（spectrum
sharing）與遷移（relocation）。

請幫我分析這份逐字稿，並把所有技術討論擷取成一份名為 `technical_discussions.md`
的結構化中文報告。針對每個技術主題，請包含：

- **主題標題**（清楚、具描述性的名稱）
- **涉及的頻段**（討論到的具體 MHz 範圍）
- **受影響的政府系統／應用**（該頻段中有哪些政府用途）
- **所描述的技術挑戰**（具體的工程或干擾問題，特別注意干擾的方向）
- **提議的途徑或解決方案**（為解決此問題所建議的做法）
- **工作小組指派**（由所提議的 5 個工作小組（Working Group）中的哪一個處理）

此外也請提供：

- 對所提議的**五個工作小組（WG1～WG5）**的摘要，含其範圍與政府方共同主持人
  （co-chair）指派
- 關於商用佈建參數的**關鍵技術辯論**（需要哪些共同參數，以及為何這些參數對
  共用分析很重要）
- 提及的任何**具體技術量測或測試**（例如台灣大哥大／中華電信業者公會
  共同提出的 STA 特別臨時授權測量申請）

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿 meeting-transcript.md
2. 擷取所有討論到的技術主題
3. 將主題對應到五個提議的工作小組（WG1～WG5）
4. 掌握商用佈建參數的技術辯論

預期的關鍵技術主題（皆可由逐字稿推得）：

- **氣象衛星接收（1695-1710 MHz）**：接收站周圍劃有很大的排除區（exclusion
  area），有機會透過更精細的商用環境模型重新評估而縮小。由 WG1 處理（中央氣象
  單位的倪婉如共同主持，頻管署窗口杜俊賢），目標 2025 年 9 月完成，比其他小組早。
- **執法監察系統**：寬頻接收機、全國性授權，採三階段過渡計畫（三步驟）——先退出
  1755-1780 MHz，再把剩餘使用壓縮到更窄範圍，最後完全離開本頻段。由 WG2 處理
  （資安署與司法警政共同主持，頻管署窗口歐怡君、簡士豪）。
- **衛星控制上鏈（satellite control uplink）**：短期內無法遷移，且干擾方向是
  「干擾打進產業（interference into industry）」——是商用基地台會干擾脆弱的衛星
  測控接收，而非政府干擾別人，需要法規構造加以保護。由 WG3 處理。
- **電子戰訓練（electronic warfare training）**：敵方拿商用手機當引爆觸發器，
  部隊必須能對著商用技術做電子戰演訓，需要保證可用（guaranteed access）的頻譜。
  由 WG3 處理。
- **戰術無線中繼與固定式微波**：可借鏡 2014 年清整 1710-1755 MHz 的經驗，永久
  站址周圍的排除區可再縮小，由潘嘉瑞協調。由 WG4 處理。
- **空中作業（無人機 UAV、精準導引彈藥、空戰訓練、遙測 telemetry）**：**整個案子
  最大的挑戰**，高功率空中發射源對上地面接收機，幾何條件最糟；以台灣大哥大／
  中華電信業者公會的 STA 特別臨時授權測量申請取得實地量測值。由 WG5 處理
  （國防部的韓宗翰主導）。
- **商用佈建參數辯論**：周明德、鄭雅文、黃國昌、何信宏等委員討論需要一套共同的
  商用佈建參數（是否採 LTE 標準、大型基地台 macrocell 還是小型基地台 small cell、
  發射功率多少）作為對所有工作小組的共同輸入。

並把結果整理成清楚、依主題分段、含工作小組指派的 technical_discussions.md。

## Grading Criteria

- [ ] 已建立報告檔案 technical_discussions.md
- [ ] 已涵蓋氣象衛星排除區主題（1695-1710 MHz）
- [ ] 已描述執法監察轉換計畫（三階段／三步驟，先退出 1755-1780 MHz）
- [ ] 已辨識衛星上鏈保護問題，並記下干擾方向（干擾打進產業／into industry）
- [ ] 已提及電子戰訓練需求（對商用技術演訓、保證可用頻譜）
- [ ] 空中作業被辨識為最大的挑戰（無人機／精準導引彈藥／遙測）
- [ ] 已列出五個工作小組（WG1～WG5）及其範圍
- [ ] 已提及台灣大哥大／中華電信業者公會的 STA 特別臨時授權測量申請
- [ ] 已掌握商用佈建參數辯論（LTE、大型基地台 macrocell、小型基地台 small cell）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """智慧城市暨資安顧問委員會頻譜共用技術討論 grader。

    做法：先從台灣逐字稿 meeting-transcript.md「動態推導」出應有事實
    （各頻段、五個工作小組編號、干擾方向、STA 申請者等），再比對 agent
    產出的中文報告 technical_discussions.md。盡量不硬寫固定事實，
    提升可重現性。僅用標準函式庫。

    注意：轉換器會在本函式後自動接上中→英正規化 wrapper，會把中文報告
    原文「保留」並於檔尾附上英文關鍵字註解，故下列中文 pattern 仍可命中。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 找 agent 報告 ---
    report = workspace / "technical_discussions.md"
    if not report.exists():
        for alt in ["technical_report.md", "tech_discussions.md",
                    "technical.md", "technical-discussions.md",
                    "技術討論.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["report_created", "weather_satellite", "law_enforcement",
            "satellite_uplink", "electronic_warfare", "airborne_operations",
            "working_groups", "sta_measurement", "parameters_debate"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 讀逐字稿，動態推導「應有事實」---
    tpath = workspace / "meeting-transcript.md"
    tx = ""
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    def tx_has(*subs):
        """逐字稿是否包含某關鍵字（無逐字稿時視為 True，避免誤殺）。"""
        if not tx:
            return True
        return any(s in tx for s in subs)

    # (a) 動態抓出逐字稿中出現的頻段（MHz 區間），作為事實基準。
    bands = set(re.findall(r"(\d{4})\s*[-－~～至到]\s*(\d{4})\s*MHz", tx))
    band_pairs = {(a, b) for a, b in bands}

    def report_has_band(lo, hi):
        """報告是否提到某頻段（容許多種連接號與是否帶 MHz）。"""
        return bool(re.search(
            rf"{lo}\s*[-－~～至到]\s*{hi}", c))

    # 氣象衛星頻段：優先用逐字稿推得的 1695-1710，找不到才退回常數。
    weather_band = ("1695", "1710")
    for lo, hi in band_pairs:
        if lo == "1695":
            weather_band = (lo, hi)
            break
    # 執法監察第一步退出頻段：1755-1780。
    le_band = ("1755", "1780")
    for lo, hi in band_pairs:
        if lo == "1755" and hi == "1780":
            le_band = (lo, hi)
            break

    # --- 計分 ---

    # 1) 氣象衛星排除區（1695-1710）：須同時提到主題＋頻段（或排除區）。
    weather_topic = bool(re.search(r"氣象衛星|氣象.{0,4}接收|weather", c, re.I))
    weather_band_hit = report_has_band(*weather_band)
    weather_excl = bool(re.search(r"排除區|exclusion", c, re.I))
    if weather_topic and (weather_band_hit or weather_excl):
        scores["weather_satellite"] = 1.0
    elif weather_topic or weather_band_hit:
        scores["weather_satellite"] = 0.5
    else:
        scores["weather_satellite"] = 0.0

    # 2) 執法監察轉換計畫（三階段／三步驟、先退出 1755-1780）。
    le_topic = bool(re.search(r"執法監察|執法.{0,4}監|surveillance|law\s*enforcement",
                              c, re.I))
    le_steps = bool(re.search(r"三階段|三步驟|三步|three.?step|3.?step|分階段|逐步退出",
                              c, re.I))
    le_band_hit = report_has_band(*le_band)
    if le_topic and (le_steps or le_band_hit):
        scores["law_enforcement"] = 1.0
    elif le_topic or le_steps or le_band_hit:
        scores["law_enforcement"] = 0.5
    else:
        scores["law_enforcement"] = 0.0

    # 3) 衛星上鏈保護 + 干擾方向（干擾打進產業 / into industry）。
    sat_topic = bool(re.search(r"衛星.{0,4}上鏈|衛星.{0,4}上行|衛星控制|衛星測控|"
                               r"satellite.{0,6}uplink|control\s*uplink", c, re.I))
    # 干擾方向：報告須點出「干擾打進產業」這個反向關係。
    sat_dir = bool(re.search(
        r"打進產業|進入產業|干擾.{0,6}產業|產業.{0,6}(?:被|受).{0,4}干擾|"
        r"interference.{0,12}industry|into\s*industry", c, re.I))
    sat_cannot = bool(re.search(r"無法遷移|不能遷移|無法搬|不能搬|短期.{0,4}無法|"
                                r"cannot.{0,12}relocat|保護", c, re.I))
    if sat_topic and sat_dir:
        scores["satellite_uplink"] = 1.0
    elif sat_topic and sat_cannot:
        scores["satellite_uplink"] = 0.5
    elif sat_topic:
        scores["satellite_uplink"] = 0.25
    else:
        scores["satellite_uplink"] = 0.0

    # 4) 電子戰訓練需求。
    ew_topic = bool(re.search(r"電子戰|electronic\s*warfare|\bEW\b", c, re.I))
    ew_detail = bool(re.search(r"訓練|演訓|演練|手機.{0,6}觸發|觸發器|引爆|"
                               r"保證可用|guaranteed\s*access|train", c, re.I))
    if ew_topic and ew_detail:
        scores["electronic_warfare"] = 1.0
    elif ew_topic:
        scores["electronic_warfare"] = 0.5
    else:
        scores["electronic_warfare"] = 0.0

    # 5) 空中作業被點為最大挑戰。
    air_topic = bool(re.search(r"空中作業|空中.{0,4}操作|airborne|無人機|UAV|"
                               r"精準導引|精準.{0,2}彈|遙測|telemetry|空戰", c, re.I))
    air_biggest = bool(re.search(r"最大.{0,4}(?:挑戰|難題|困難)|最艱難|最困難|"
                                 r"最棘手|biggest|greatest|最難", c, re.I))
    if air_topic and air_biggest:
        scores["airborne_operations"] = 1.0
    elif air_topic:
        scores["airborne_operations"] = 0.5
    else:
        scores["airborne_operations"] = 0.0

    # 6) 五個工作小組（WG1～WG5）：計算報告中辨識到幾個小組編號。
    wg_indicators = 0
    for i in range(1, 6):
        if re.search(rf"(?:工作小組|WG|working\s*group|小組|group)\s*{i}",
                     c, re.I):
            wg_indicators += 1
    if re.search(r"五.{0,2}(?:個).{0,2}工作小組|五.{0,2}工作小組|"
                 r"5\s*(?:個)?\s*(?:工作小組|working\s*group)|"
                 r"(?:five|5)\s*working\s*group", c, re.I):
        wg_indicators += 2
    scores["working_groups"] = 1.0 if wg_indicators >= 3 else (
        0.5 if wg_indicators >= 1 else 0.0)

    # 7) STA 特別臨時授權測量申請（台灣大哥大／中華電信業者公會）。
    #    申請者名稱由逐字稿動態確認，避免硬寫。
    sta_kw = bool(re.search(r"STA|特別臨時授權|臨時授權|special\s*temporary",
                            c, re.I))
    applicant_terms = []
    for term in ["台灣大哥大", "中華電信業者公會", "電信業者公會", "電信公會",
                 "公會"]:
        if tx_has(term) and re.search(re.escape(term), c, re.I):
            applicant_terms.append(term)
    measure_kw = bool(re.search(r"量測|測量|實地量測|measurement|測試|test", c, re.I))
    if sta_kw and (applicant_terms or measure_kw):
        scores["sta_measurement"] = 1.0
    elif sta_kw or applicant_terms:
        scores["sta_measurement"] = 0.5
    else:
        scores["sta_measurement"] = 0.0

    # 8) 商用佈建參數辯論（LTE、大型基地台 macrocell、小型基地台 small cell）。
    param_common = bool(re.search(r"共同.{0,4}參數|統一.{0,4}參數|一致.{0,4}假設|"
                                  r"共同輸入|common\s*parameter|uniform\s*parameter",
                                  c, re.I))
    param_lte = bool(re.search(r"\bLTE\b|長期演進", c, re.I))
    param_cell = bool(re.search(r"大型基地台|小型基地台|微型基地台|小細胞|小基站|"
                                r"macro\s*cell|macrocell|small\s*cell|smallcell|"
                                r"基地台|發射功率|功率位準", c, re.I))
    hits = sum([param_common, param_lte, param_cell])
    scores["parameters_debate"] = 1.0 if hits >= 2 else (
        0.5 if hits >= 1 else 0.0)

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

### 評分項 1：技術準確度（權重 35%）
- 1.0：所有技術主題皆準確擷取，頻段（1695-1710、1755-1780、1755-1850）、系統描述
  與干擾動態皆正確。干擾方向正確記下——特別是衛星上鏈是「干擾打進產業」而非政府
  干擾別人。
- 0.75：多數技術細節正確，僅有少許不準確。
- 0.5：辨識出概略主題，但技術細節含糊或部分不正確。
- 0.25：有數處技術錯誤或誤述。
- 0.0：技術內容大致不正確。
### 評分項 2：技術主題完整度（權重 25%）
- 1.0：涵蓋所有主要技術主題：氣象衛星、執法監察、衛星上鏈、電子戰、戰術無線中繼、
  固定式微波、空中作業，以及商用佈建參數辯論。
- 0.75：涵蓋多數主題，僅有一兩處遺漏。
- 0.5：涵蓋主要主題，但漏掉數個次要主題。
- 0.25：僅擷取出兩三個主題。
- 0.0：擷取出的技術內容極少。
### 評分項 3：工作小組對應（權重 20%）
- 1.0：五個工作小組（WG1～WG5）皆清楚描述，含其範圍、所指派的技術主題、具名人員
  （共同主持人、頻管署窗口）與目標完成日期（WG1 為 2025 年 9 月，WG2～WG5 為
  2026 年 1 月）。
- 0.75：工作小組皆有描述且多數細節正確。
- 0.5：提及工作小組但細節不完整。
- 0.25：僅有部分工作小組資訊。
- 0.0：無工作小組資訊。
### 評分項 4：結構與實用性（權重 20%）
- 1.0：報告組織良好，每個主題清楚劃分，易於作為參考；技術挑戰與提議的解決方案
  清楚分開。
- 0.75：結構良好，僅有少許組織問題。
- 0.5：內容齊備但組織不佳。
- 0.25：雜亂無章，難以查找特定主題。
- 0.0：無有意義的結構。
