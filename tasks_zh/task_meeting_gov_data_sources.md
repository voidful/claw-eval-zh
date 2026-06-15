---
id: task_meeting_gov_data_sources
name: NASA UAP 聽證會資料來源擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_gov_data_sources
source_benchmark: pinchbench
claw_eval_id: P134zh_meeting_gov_data_sources
workspace_files:
- source: meetings/2025-07-30-nasa-holds-first-public-meeting-on-ufos-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# NASA UAP 聽證會資料來源擷取

## Prompt

我有一份逐字稿檔案 `transcript.md`，來自 NASA 首場關於不明異常現象（UAPs/UFOs）的公開會議。會議過程中，發言者提到了與 UAP 研究相關的各種資料來源、感測器、資料庫與量測系統。

請閱讀逐字稿，並把所有提及的資料來源與量測系統擷取到名為 `data_sources.md` 的檔案。對於每個來源，請列出：

- **名稱／類型（Name/Type）**：資料來源或感測器系統
- **擁有者／營運者（Owner/Operator）**：機關或組織
- **描述（Description）**：它量測或提供什麼
- **與 UAP 的關聯（Relevance to UAP）**：它在 UAP 研究脈絡中如何被討論
- **侷限（Limitations）**：任何提到的侷限或附註
- **是誰提到的（Who referenced it）**：發言者姓名

請把來源分成以下類別：Government/Military Sensors、Civilian Aviation Systems、Space-Based Assets、Ground-Based Scientific Instruments、Crowdsource/Public Data 與 Databases/Archives。在最上方附一張摘要表，列出所有來源及其類別與擁有者。

## Expected Behavior

助手應該：

1. 讀取並解析完整逐字稿
2. 辨識所有提及的資料來源、感測器、資料庫與量測系統
3. 同時掌握所討論的能力與侷限
4. 全面性地組織

關鍵資料來源：

**Government/Military：**
- AARO 資料庫（800+ 案例、DOD/IC 機密持有）
- DOD 感測器（F-35 攝影機、MQ-9 EO 感測器——「並非科學感測器」）
- 情報界感測器（「非常接近科學感測器、經校準、高精度」）
- AARO 為 UAP 偵測專門打造的感測器

**Civilian Aviation：**
- FAA 短程雷達（40-60 英里範圍，最高 24,000 英尺）
- FAA 長程雷達／ARSR-4 與 CRSR 系統（200-250 海里範圍，最高 100,000 英尺）
- ADS-B（Automatic Dependent Surveillance-Broadcast）協作系統
- FAA TRACON 終端系統
- ERAM（En Route Automation Modernization）／STARS 系統
- FAA Domestic Events Network（通報系統）

**Space-Based：**
- NASA 地球科學／遙測衛星
- NOAA 衛星
- James Webb Space Telescope（作為校準範例提及）
- Hubble Space Telescope（作為校準範例提及）
- International Space Station 影像（精靈閃電 sprites 觀測範例）

**Ground-Based Scientific：**
- 大型電波望遠鏡（FRB 偵測類比）
- 天文觀測站（時域巡天望遠鏡）
- NOAA 地面感測器
- National Weather Service 氣球追蹤系統

**Crowdsource/Public：**
- 智慧型手機感測器資料（GPS、位置、速度、加速度計）
- 目擊者通報（指出單靠它並不足夠）
- iPhone 影像（指出除非近距離，否則「通常沒有幫助」）
- 提議中的 NASA 群眾外包平台

**Databases/Archives：**
- NASA 開放資料入口（data.nasa.gov）
- Data.gov 開放資料資源
- FAA 處理過的雷達資料封存（保存數個月）
- National Weather Service 氣球施放紀錄（92 個站點，每日兩次）

## Grading Criteria

- [ ] 已建立輸出檔案 `data_sources.md`
- [ ] 提及 AARO 資料庫並附案例數量細節
- [ ] 描述 FAA 雷達系統（區分短程與長程）
- [ ] 提及 ADS-B 系統
- [ ] 提及 NASA 衛星／地球遙測資產
- [ ] 包含智慧型手機／公民科學資料來源
- [ ] 提及 NASA 開放資料入口（data.nasa.gov）
- [ ] 至少為 3 個資料來源註記侷限
- [ ] 來源分成各類別
- [ ] 包含摘要表或概覽

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the data sources extraction task.

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

    report_path = workspace / "data_sources.md"
    if not report_path.exists():
        alternatives = ["sources.md", "data.md", "sensors.md", "data_sources_report.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "aaro_database": 0.0,
            "faa_radar": 0.0,
            "adsb": 0.0,
            "nasa_satellites": 0.0,
            "citizen_data": 0.0,
            "nasa_portal": 0.0,
            "limitations": 0.0,
            "categorization": 0.0,
            "summary_table": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # AARO database
    has_aaro = bool(re.search(r'aaro', content_lower))
    has_cases = bool(re.search(r'800|case|holding', content_lower))
    scores["aaro_database"] = 1.0 if has_aaro and has_cases else (0.5 if has_aaro else 0.0)

    # FAA radar systems
    has_short = bool(re.search(r'short.range\s+radar|asr|terminal\s+radar', content_lower))
    has_long = bool(re.search(r'long.range\s+radar|arsr|crsr|en.?route', content_lower))
    scores["faa_radar"] = 1.0 if has_short and has_long else (0.5 if has_short or has_long else 0.0)

    # ADS-B
    scores["adsb"] = 1.0 if re.search(r'ads.?b|automatic\s+dependent\s+surveillance', content_lower) else 0.0

    # NASA satellites
    nasa_sat_patterns = [r'earth\s+(?:science|sensing)\s+satellite', r'nasa\s+satellite', r'space.based', r'james\s+webb|jwst', r'hubble']
    scores["nasa_satellites"] = 1.0 if sum(bool(re.search(p, content_lower)) for p in nasa_sat_patterns) >= 2 else (0.5 if any(re.search(p, content_lower) for p in nasa_sat_patterns) else 0.0)

    # Citizen / smartphone data
    citizen_patterns = [r'smartphone|cell\s*phone|iphone|mobile\s+(?:phone|device)', r'crowdsourc', r'citizen\s+science', r'eyewitness']
    scores["citizen_data"] = 1.0 if sum(bool(re.search(p, content_lower)) for p in citizen_patterns) >= 2 else (0.5 if any(re.search(p, content_lower) for p in citizen_patterns) else 0.0)

    # NASA data portal
    scores["nasa_portal"] = 1.0 if re.search(r'data\.nasa\.gov|nasa.*open\s+data\s+portal|data\.gov', content_lower) else 0.0

    # Limitations noted
    limitation_patterns = [
        r'not\s+(?:calibrated|scientific|optimized)',
        r'uncalibrated',
        r'limit(?:ation|ed)',
        r'cannot\s+(?:detect|see|measure)',
        r'insufficient|inadequate',
        r'filter(?:ing|ed)\s+out',
        r'not\s+helpful',
        r'clutter',
        r'not\s+designed\s+for',
    ]
    lim_count = sum(1 for p in limitation_patterns if re.search(p, content_lower))
    scores["limitations"] = 1.0 if lim_count >= 3 else (0.5 if lim_count >= 1 else 0.0)

    # Categorization
    category_patterns = [
        r'government|military|dod|defense',
        r'civilian|aviation|faa',
        r'space.based|satellite|orbital',
        r'ground.based|terrestrial|observatory',
        r'crowdsourc|public|citizen',
        r'database|archive|repository',
    ]
    cat_count = sum(1 for p in category_patterns if re.search(p, content_lower))
    scores["categorization"] = 1.0 if cat_count >= 4 else (0.5 if cat_count >= 2 else 0.0)

    # Summary table
    has_table = bool(re.search(r'\|.*\|.*\|', content))
    has_overview = bool(re.search(r'summary|overview|at.a.glance', content_lower))
    scores["summary_table"] = 1.0 if has_table else (0.5 if has_overview else 0.0)

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

### 評分項 1：來源辨識完整性（權重 30%）

**1.0 分**：辨識出至少 15 個不同的資料來源／系統，橫跨所有類別。涵蓋軍事感測器、FAA 系統、太空資產、科學儀器與公眾／公民資料。沒有遺漏主要來源。

**0.75 分**：10-14 個來源，涵蓋多數類別。

**0.5 分**：6-9 個來源，部分類別著墨不足。

**0.25 分**：少於 6 個來源。

**0.0 分**：未辨識任何來源。

### 評分項 2：技術準確性（權重 25%）

**1.0 分**：描述在技術上準確，包含具體細節（例如 FAA 短程雷達 40-60 英里範圍、ADS-B 涵蓋至 1,500 英尺 AGL、MQ-9 EO 感測器）。侷限描述正確。

**0.75 分**：大致準確，僅有少許技術錯誤。

**0.5 分**：有一定準確性，但缺少重要技術細節。

**0.25 分**：描述模糊或不準確。

**0.0 分**：沒有技術細節。

### 評分項 3：侷限分析（權重 25%）

**1.0 分**：清楚註記關鍵系統的侷限。包含：DOD 感測器並非為科學設計、FAA 過濾會移除小型目標、雷達視線限制、iPhone 照片通常沒幫助、目擊者通報單獨並不足夠。

**0.75 分**：多數系統都註記了侷限。

**0.5 分**：註記了一些侷限但不完整。

**0.25 分**：提及的侷限很少。

**0.0 分**：未討論任何侷限。

### 評分項 4：組織與呈現（權重 20%）

**1.0 分**：分類清楚、最上方有摘要表、每筆項目格式一致，便於查閱與比較各來源。

**0.75 分**：組織良好，僅有少許問題。

**0.5 分**：有組織但格式不一致。

**0.25 分**：組織不佳。

**0.0 分**：沒有組織。
