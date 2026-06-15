---
id: task_meeting_advisory_technical
name: NTIA Advisory Board 技術討論
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_advisory_technical
source_benchmark: pinchbench
claw_eval_id: P122zh_meeting_advisory_technical
workspace_files:
- source: meetings/2012-05-30-meeting-transcript-ntia-csmac.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# NTIA Advisory Board 技術討論

## Prompt

我這裡有一份政府諮詢委員會會議的逐字稿，存放在 `meeting-transcript.md`。這是 Commerce Spectrum Management Advisory Committee（CSMAC）於 2012 年 5 月 30 日舉行的會議，聚焦於 1755-1850 MHz band 的聯邦頻譜管理。

請分析這份逐字稿，並將所有技術討論擷取成一份名為 `technical_discussions.md` 的結構化報告。針對每個技術主題，請包含：

- **主題標題**（清楚、具描述性的名稱）
- **涉及的頻段**（討論到的具體 MHz 範圍）
- **受影響的聯邦系統/應用**（該頻段中有哪些政府用途）
- **所描述的技術挑戰**（具體的工程或干擾問題）
- **提議的途徑或解決方案**（為解決此問題所建議的做法）
- **Working group 指派**（由所提議的 5 個 working groups 中的哪一個處理）

此外也請提供：

- 對所提議的**五個 working groups** 的摘要，含其範圍與政府方共同主席（co-chair）指派
- 關於商用部署參數的**關鍵技術辯論**（需要哪些參數，以及為何這些參數對共享分析很重要）
- 提及的任何**具體技術量測或測試**（例如 T-Mobile/CTIA STA）

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿
2. 擷取所有討論到的技術主題
3. 將主題對應到五個提議的 working groups
4. 掌握技術參數辯論

預期的關鍵技術主題：

- **氣象衛星接收器（1695-1710 MHz）**：接收器周邊的排除區（exclusion areas），有可能透過更佳的商用環境建模加以縮小（Working Group 1，co-chair：Yvonne Navarro/NOAA，NTIA 代表：Ed Drocella）
- **執法監視（Law enforcement surveillance）**：寬頻接收器、全國性授權、三步驟轉換計畫（先退出 1755-1780，再壓縮，最後離開該頻段）（Working Group 2，co-chair 來自 DHS/Justice，NTIA 代表：Rich Orsulak、Scott Jackson）
- **衛星控制上行鏈路（Satellite control uplinks）**：短期內無法遷移，干擾問題是「干擾進入業界」（而非來自業界），需要保護用的法規架構（Working Group 3）
- **電子戰訓練（Electronic warfare training）**：軍方需針對商用技術進行訓練（敵方以手機作為觸發器），需要有保障的存取（Working Group 3）
- **戰術無線電中繼與固定微波（Tactical Radio Relay and Fixed Microwave）**：來自 1710-1755 遷移的既有經驗，永久站址周邊的排除區可加以縮小，Gary Patrick 參與其中（Working Group 4）
- **空中操作（UAVs、precision-guided munitions、空戰訓練、telemetry）**：最大的挑戰，高功率空中發射源對比地面接收器，以 T-Mobile/CTIA STA 進行量測（Working Group 5，DoD 的 John Hunter）
- **商用部署參數辯論**：Rush/Warren/Kahn/Calabrese 討論需要統一參數（LTE 標準、macrocells 對比 small cells、功率位準）作為對所有 working groups 的共同輸入

## Grading Criteria

- [ ] 已建立檔案 technical_discussions.md
- [ ] 已涵蓋氣象衛星排除區主題（1695-1710 MHz）
- [ ] 已描述執法監視轉換計畫（三步驟流程）
- [ ] 已辨識衛星上行鏈路保護問題（並記下干擾方向）
- [ ] 已提及電子戰訓練需求
- [ ] 空中操作被辨識為最大的挑戰
- [ ] 已列出五個 working groups 及其範圍
- [ ] 已提及 T-Mobile/CTIA STA 量測請求
- [ ] 已掌握商用參數辯論（LTE、small cells、macrocells）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the technical discussions extraction task.

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

    report_path = workspace / "technical_discussions.md"
    if not report_path.exists():
        alternatives = ["technical_report.md", "tech_discussions.md", "technical.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "weather_satellite": 0.0,
            "law_enforcement": 0.0,
            "satellite_uplink": 0.0,
            "electronic_warfare": 0.0,
            "airborne_operations": 0.0,
            "working_groups": 0.0,
            "sta_measurement": 0.0,
            "parameters_debate": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Weather satellite (1695-1710)
    weather_patterns = [
        r'(?:weather|satellite).*(?:1695|1710)',
        r'1695.*1710.*(?:weather|satellite|exclusion)',
        r'exclusion.*(?:area|zone).*(?:weather|satellite|receiver)',
    ]
    scores["weather_satellite"] = 1.0 if any(re.search(p, content_lower) for p in weather_patterns) else 0.0

    # Law enforcement surveillance transition
    le_patterns = [
        r'law enforcement.*(?:surveillance|transition|three.?step|wideband)',
        r'surveillance.*(?:transition|three.?step|1755.*1780|digital)',
        r'(?:three.?step|3.?step).*(?:process|plan|transition)',
        r'1755.*1780.*(?:first|initial|phase)',
    ]
    scores["law_enforcement"] = 1.0 if any(re.search(p, content_lower) for p in le_patterns) else 0.0

    # Satellite uplink protection
    sat_patterns = [
        r'satellite.*(?:uplink|control).*(?:protect|interference|relocat)',
        r'(?:uplink|satellite control).*(?:cannot|not.*moving|remain)',
        r'interference.*(?:into|toward|against).*industry',
    ]
    scores["satellite_uplink"] = 1.0 if any(re.search(p, content_lower) for p in sat_patterns) else 0.0

    # Electronic warfare
    ew_patterns = [
        r'electronic warfare.*(?:training|test|train)',
        r'(?:ew|electronic warfare).*(?:commercial technology|cell phone|trigger)',
        r'(?:train|training).*(?:electronic warfare|ew)',
    ]
    scores["electronic_warfare"] = 1.0 if any(re.search(p, content_lower) for p in ew_patterns) else 0.0

    # Airborne operations as biggest challenge
    air_patterns = [
        r'airborne.*(?:challenge|difficult|biggest|greatest|complex)',
        r'(?:biggest|greatest).*challenge.*airborne',
        r'(?:uav|unmanned|precision.guided|telemetry|air combat).*(?:challenge|airborne)',
    ]
    scores["airborne_operations"] = 1.0 if any(re.search(p, content_lower) for p in air_patterns) else 0.0

    # Five working groups listed
    wg_patterns = [
        r'working group.*[1-5]',
        r'(?:five|5).*working group',
        r'group 1.*group 2',
    ]
    wg_indicators = 0
    for i in range(1, 6):
        if re.search(rf'(?:working group|group|wg)\s*{i}', content_lower):
            wg_indicators += 1
    if re.search(r'(?:five|5)\s*working\s*group', content_lower):
        wg_indicators += 2
    scores["working_groups"] = 1.0 if wg_indicators >= 3 else (0.5 if wg_indicators >= 1 else 0.0)

    # T-Mobile/CTIA STA measurement
    sta_patterns = [
        r't-?mobile.*(?:sta|measurement|test)',
        r'ctia.*(?:sta|measurement|test)',
        r'sta.*(?:request|measurement|test).*(?:t-?mobile|ctia)',
        r'special temporary auth',
    ]
    scores["sta_measurement"] = 1.0 if any(re.search(p, content_lower) for p in sta_patterns) else 0.0

    # Commercial parameters debate
    param_patterns = [
        r'(?:lte|long term evolution).*(?:standard|parameter|deployment)',
        r'(?:small cell|microcell|macrocell|femtocell).*(?:deploy|parameter|power)',
        r'(?:commercial|industry).*(?:parameter|characteristic|deployment).*(?:common|uniform|consistent)',
        r'(?:common|uniform).*(?:parameter|characteristic)',
    ]
    scores["parameters_debate"] = 1.0 if any(re.search(p, content_lower) for p in param_patterns) else 0.0

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

**1.0 分**：所有技術主題皆準確擷取，頻段、系統描述與干擾動態皆正確。干擾的方向（例如衛星上行鏈路——干擾是進入業界，而非來自業界）正確記下。
**0.75 分**：多數技術細節正確，僅有少許不準確。
**0.5 分**：辨識出概略主題，但技術細節含糊或部分不正確。
**0.25 分**：有數處技術錯誤或誤述。
**0.0 分**：技術內容大致不正確。

### 評分項 2：技術主題完整度（權重 25%）

**1.0 分**：涵蓋所有主要技術主題：氣象衛星、執法監視、衛星上行鏈路、電子戰、戰術無線電中繼、固定微波、空中操作，以及商用參數辯論。
**0.75 分**：涵蓋多數主題，僅有一兩處遺漏。
**0.5 分**：涵蓋主要主題，但漏掉數個次要主題。
**0.25 分**：僅擷取出兩三個主題。
**0.0 分**：擷取出的技術內容極少。

### 評分項 3：Working Group 對應（權重 20%）

**1.0 分**：五個 working groups 皆清楚描述，含其範圍、所指派的技術主題、具名人員（co-chairs、NTIA 代表）與目標完成日期（WG1 為 September，其餘為 January）。
**0.75 分**：working groups 皆有描述且多數細節正確。
**0.5 分**：提及 working groups 但細節不完整。
**0.25 分**：僅有部分 working group 資訊。
**0.0 分**：無 working group 資訊。

### 評分項 4：結構與實用性（權重 20%）

**1.0 分**：報告組織良好，每個主題清楚劃分，易於作為參考。技術挑戰與提議的解決方案清楚分開。
**0.75 分**：結構良好，僅有少許組織問題。
**0.5 分**：內容齊備但組織不佳。
**0.25 分**：雜亂無章，難以查找特定主題。
**0.0 分**：無有意義的結構。
