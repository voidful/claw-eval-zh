---
id: task_meeting_gov_data_sources
name: 數位治理委員會（虛構）：生成式 AI 治理公聽會 資料來源與監測系統擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_gov_data_sources
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T134tw_meeting_gov_data_sources
workspace_files:
- source: tw/meetings/tw_gov_hearing.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 數位治理委員會（虛構）：生成式 AI 治理公聽會 資料來源與監測系統擷取

## Prompt

工作區裡有一份逐字稿檔案 transcript.md，是虛構的「數位治理委員會」就「生成式 AI
治理」召開的第一場對外公開公聽會（依《行政程序法》公聽會相關程序公開舉行）之全程
逐字稿。會議過程中，各發言者提到了與 AI 風險研究相關的各種「資料來源、監測系統、
感測機制、資料庫與量測系統」（例如案例庫、終端側／骨幹側監測、自願標示機制、開放
資料入口、群眾外包平台等）。

請讀完逐字稿，把所有提及的「資料來源與監測／量測系統」擷取到一個名為
data_sources.md 的繁體中文檔案。對於每一個來源，請列出：

- **名稱／類型（Name/Type）**：資料來源、監測系統或感測機制
- **擁有者／營運者（Owner/Operator）**：機關或組織（如委員會、AIRC、NCRA、業者、民眾）
- **描述（Description）**：它量測或提供什麼
- **與 AI 風險的關聯（Relevance）**：它在這場公聽會的 AI 風險治理脈絡中如何被討論
- **侷限（Limitations）**：任何被提到的侷限或附註（如非為科學設計、會濾掉小訊號、
  只對配合者有效、保存期限等）
- **是誰提到的（Who referenced it）**：發言者姓名

請把來源分成以下幾類：政府／公部門監測系統、業者端／網路通訊系統、跨機構／科學運算
資源、公民科學／公眾資料，以及資料庫／封存。在報告最上方附一張摘要表，列出所有來源
及其類別與擁有者。報告請以繁體中文撰寫，輸出檔名為 data_sources.md。

## Expected Behavior

助手應讀取並解析 transcript.md，全面辨識逐字稿中提及的資料來源與監測／量測系統，
同時掌握各來源的能力與侷限，最後以結構良好的繁體中文 markdown 檔 data_sources.md
呈現，並在最上方附摘要表。逐字稿中（皆為虛構）的關鍵資料來源如下：

政府／公部門監測系統：
- AIRC 案例庫（累積「超過 800 件」生成式 AI 事故與疑似事故通報；經完整分析後真正
  難以解釋的僅約 2%–5%；張庭瑋）。
- 資安監測與情資系統（本來就不是為「科學分析」設計，目的是辨識並阻斷／反制已知威脅，
  拿來做科學推論要很小心；張庭瑋）。
- 情報級監測系統（少數很接近科學感測器：經過校準、精度高，但卡在機敏分級；張庭瑋）。
- AIRC 將在風險熱點領域「部署專門打造的偵測探針」（張庭瑋）。

業者端／網路通訊系統（NCRA，黃建宏）：
- 終端側監測：部署在業者端的稽核探針，涵蓋範圍小、解析度高，看不到跨平台全貌。
- 骨幹側監測：在網路骨幹與大型節點佈建，涵蓋範圍大、解析度粗，看不清單一互動內容。
- 合作式自願標示機制（業者主動標註 AI 生成內容的標籤系統，類似航空的 ADS-B；只對
  願意配合標示的業者有效，對刻意隱匿者沒輒）。
- 過濾規則會把很多「看起來像雜訊」的小型零星訊號濾掉（罕見異常可能在進分析前就被濾掉）。
- 全國 AI 事件通報網（National AI Incident Network；第一線人員平均每月只回報 3 到 5 件；
  單日約 4,500 萬次可記錄互動事件、約 14,000 名第一線人員）。

跨機構／科學運算資源：
- 既有大型科學運算與監測基礎設施（評估能否用於風險偵測；很多本為「時域異常偵測」設計；
  張庭瑋、郭佳穎）。
- 「五方資料圈」（台日韓新澳）跨國資料共享聯盟（張庭瑋）。
- 監督式與非監督式機器學習用於既有案例的異常偵測（張庭瑋、郭佳穎、白雅雯）。

公民科學／公眾資料：
- 民眾自行截圖的爆料（除非高解析、帶完整中繼資料，否則通常幫助有限；黃建宏）。
- 公民科學群眾外包平台／App（讓民眾上傳 AI 異常案例，一併蒐集時間戳、定位、版本資訊、
  互動序列等；郭佳穎、陳冠宇）。

資料庫／封存：
- 開放資料入口 data.gov.tw（逐步釋出去識別化、標準化的非機敏資料；林淑芬）。
- NCRA 處理過的雷達式流量原始紀錄（保存數個月後即輪替刪除；黃建宏）。
- AIRC 案例庫（逐案歸檔，涵蓋近三年；張庭瑋、黃建宏）。

報告須為每個來源同時記錄能力與侷限，並附摘要表與清楚分類。

## Grading Criteria

- [ ] 建立輸出檔案 data_sources.md
- [ ] 提及 AIRC 案例庫並附案例數量細節（超過 800 件，且帶 2%–5% 真正異常比例）
- [ ] 描述 NCRA 監測系統並區分終端側（範圍小、解析度高）與骨幹側（範圍大、解析度粗）
- [ ] 提及合作式自願標示機制（業者標註 AI 內容，類似 ADS-B）
- [ ] 提及跨機構／科學運算基礎設施或情報級／科學監測資源（含五方資料圈、機器學習等）
- [ ] 包含公民科學／公眾資料來源（民眾截圖爆料、群眾外包平台、時間戳／定位等）
- [ ] 提及開放資料入口 data.gov.tw
- [ ] 至少為 3 個資料來源註記侷限（如非為科學設計、會濾掉小訊號、只對配合者有效、保存期限）
- [ ] 來源分成各類別（政府監測、業者／網路、科學運算、公民科學、資料庫封存等）
- [ ] 報告最上方包含摘要表或概覽

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會（虛構）公聽會 資料來源／監測系統擷取 grader。

    對應原版 grader 的查核項，但改查台灣逐字稿（dest=transcript.md）
    推導之事實 + agent 的中文報告 data_sources.md。僅用標準函式庫。
    報告為繁體中文，故以中文關鍵字／數值比對；可查核的數值（超過 800 件、
    2-5% 異常、每月 3-5 件、約 14,000 人、單日約 4,500 萬次、保存數個月）
    優先從逐字稿動態讀出再比對，避免硬寫英文原版事實。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "airc_database", "ncra_monitoring", "voluntary_labeling",
        "scientific_infra", "citizen_data", "open_data_portal",
        "limitations", "categorization", "summary_table",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "data_sources.md"
    if not report.exists():
        for alt in ["sources.md", "data.md", "sensors.md",
                    "data_sources_report.md", "資料來源.md",
                    "監測系統.md", "data_sources.txt"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出可查核的數值（避免硬寫；逐字稿缺漏時退回其載明之事實） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "tw_gov_hearing.md", "meeting_transcript.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def first(pattern, text, default=None, group=1):
        m = re.search(pattern, text)
        return m.group(group) if m else default

    # AIRC 案例件數（逐字稿：「超過 800 件」）
    case_count = first(r'超過\s*(\d{3,})\s*件', t) or first(r'(\d{3,})\s*多?\s*件', t) or "800"
    # 真正異常比例（逐字稿：「2% 到 5%」「約 2%–5%」）
    anom_lo = first(r'(\d+)\s*%\s*(?:到|–|-|~|～|至)\s*\d+\s*%', t) or "2"
    anom_hi = first(r'\d+\s*%\s*(?:到|–|-|~|～|至)\s*(\d+)\s*%', t) or "5"
    # NCRA 每月通報件數（逐字稿：「每月只回報 3 到 5 件」「每月只有 3–5 件」）
    rep_lo = first(r'每月[^。]{0,12}?(\d+)\s*(?:到|–|-|~|～|至)\s*\d+\s*件', t) or "3"
    rep_hi = first(r'每月[^。]{0,12}?\d+\s*(?:到|–|-|~|～|至)\s*(\d+)\s*件', t) or "5"

    def has(*pats):
        return any(re.search(p, c, re.IGNORECASE) for p in pats)

    scores = {"report_created": 1.0}

    # --- AIRC 案例庫（對應原 aaro_database）：須有案例庫 + 數量細節 ---
    cc = re.escape(case_count)
    lo = re.escape(anom_lo)
    hi = re.escape(anom_hi)
    has_db = has(r'AIRC', r'案例庫', r'風險研析中心', r'案例.{0,4}資料庫')
    # 數量細節：超過/逾 800 件，或單獨出現該數字，或 2-5% 異常比例
    has_count = bool(
        re.search(r'(?:超過|逾)\s*%s\s*多?\s*件' % cc, c)
        or re.search(r'\b%s\b' % cc, c)
        or re.search(r'%s\s*%%?\s*(?:到|–|-|~|～|至)\s*%s\s*%%' % (lo, hi), c)
        or re.search(r'%s\s*(?:到|–|-|~|～|至)\s*%s\s*%%' % (lo, hi), c)
        or has(r'案例', r'通報', r'歸檔')
    )
    scores["airc_database"] = 1.0 if (has_db and has_count) else (0.5 if has_db else 0.0)

    # --- NCRA 監測（對應原 faa_radar 短程／長程）：終端側 vs 骨幹側 ---
    has_terminal = has(r'終端側', r'業者端.{0,6}探針', r'稽核探針',
                        r'範圍小.{0,8}解析度高', r'解析度高')
    has_backbone = has(r'骨幹側', r'網路骨幹', r'大型節點',
                       r'範圍大.{0,8}解析度', r'解析度粗', r'跨平台.{0,6}流量輪廓')
    scores["ncra_monitoring"] = 1.0 if (has_terminal and has_backbone) else (0.5 if (has_terminal or has_backbone) else 0.0)

    # --- 合作式自願標示機制（對應原 ADS-B） ---
    scores["voluntary_labeling"] = 1.0 if has(
        r'自願標示', r'合作式.{0,6}標示', r'標籤系統', r'標註\s*AI',
        r'ADS-?B', r'業者.{0,6}標註',
    ) else 0.0

    # --- 跨機構／科學運算基礎設施（對應原 nasa_satellites 太空／科學資產） ---
    sci_pats = [
        r'科學運算.{0,4}基礎設施', r'監測基礎設施', r'時域異常',
        r'情報級.{0,6}監測', r'科學感測器', r'五方資料圈',
        r'監督式', r'非監督式', r'機器學習', r'科學觀測',
    ]
    sci_n = sum(1 for p in sci_pats if re.search(p, c, re.IGNORECASE))
    scores["scientific_infra"] = 1.0 if sci_n >= 2 else (0.5 if sci_n >= 1 else 0.0)

    # --- 公民科學／公眾資料（對應原 citizen_data 智慧型手機／群眾） ---
    citizen_pats = [
        r'群眾外包', r'公民科學', r'民眾.{0,4}截圖', r'民眾.{0,4}爆料',
        r'智慧型手機', r'時間戳', r'定位', r'中繼資料', r'上傳.{0,6}異常',
    ]
    citizen_n = sum(1 for p in citizen_pats if re.search(p, c, re.IGNORECASE))
    scores["citizen_data"] = 1.0 if citizen_n >= 2 else (0.5 if citizen_n >= 1 else 0.0)

    # --- 開放資料入口（對應原 data.nasa.gov / data.gov） ---
    scores["open_data_portal"] = 1.0 if has(
        r'data\.gov\.tw', r'開放資料.{0,4}入口', r'開放資料平台', r'去識別化.{0,6}資料',
    ) else 0.0

    # --- 侷限（對應原 limitations）：須涵蓋至少 3 類侷限說明 ---
    limitation_pats = [
        r'不是.{0,6}科學.{0,4}(?:分析|設計)', r'並非.{0,6}科學', r'本來就不是',
        r'濾掉', r'過濾.{0,6}(?:規則|掉)', r'濾掉.{0,6}異常',
        r'只對.{0,8}有效', r'沒輒', r'看不到.{0,6}全貌', r'看不清',
        r'幫助有限', r'通常.{0,4}幫助有限',
        r'輪替刪除', r'保存.{0,4}數個月', r'保存期限',
        r'機敏', r'卡.{0,4}機敏', r'視線.{0,6}限制', r'授權範圍',
        r'通報偏差', r'低度通報', r'解析度粗',
    ]
    lim_n = sum(1 for p in limitation_pats if re.search(p, c, re.IGNORECASE))
    scores["limitations"] = 1.0 if lim_n >= 3 else (0.5 if lim_n >= 1 else 0.0)

    # --- 分類（對應原 categorization）：至少 4 類 ---
    category_pats = [
        r'政府|公部門|委員會|AIRC|情資',
        r'業者|網路|通訊|NCRA|骨幹|終端',
        r'科學運算|科學.{0,4}基礎設施|科學觀測|機器學習|五方',
        r'公民科學|群眾|公眾|民眾',
        r'資料庫|封存|歸檔|開放資料|入口',
    ]
    cat_n = sum(1 for p in category_pats if re.search(p, c, re.IGNORECASE))
    scores["categorization"] = 1.0 if cat_n >= 4 else (0.5 if cat_n >= 2 else 0.0)

    # --- 摘要表（對應原 summary_table）：markdown 表格或摘要概覽 ---
    has_table = bool(re.search(r'\|.*\|.*\|', c))
    has_overview = bool(re.search(r'摘要表|概覽|總覽|一覽|摘要', c))
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
- 1.0：辨識出至少 12 個不同的資料來源／監測系統，橫跨所有類別（政府監測、業者／網路、
  科學運算、公民科學、資料庫封存），涵蓋 AIRC 案例庫、資安監測與情資系統、情報級監測
  系統、NCRA 終端側／骨幹側監測、自願標示機制、群眾外包平台、data.gov.tw、雷達式原始
  紀錄等，沒有遺漏主要來源。
- 0.75：8-11 個來源，涵蓋多數類別。
- 0.5：5-7 個來源，部分類別著墨不足。
- 0.25：少於 5 個來源。
- 0.0：未辨識任何來源。
### 評分項 2：技術準確性（權重 25%）
- 1.0：描述在技術上準確，含具體細節（如 AIRC 超過 800 件、真正異常約 2%–5%、NCRA 終端側
  範圍小解析度高 vs 骨幹側範圍大解析度粗、單日約 4,500 萬次互動、約 14,000 名人員、
  每月回報 3-5 件、自願標示機制類似 ADS-B、原始紀錄保存數個月即輪替刪除），侷限描述正確。
- 0.75：大致準確，僅有少許技術錯誤或數字偏差。
- 0.5：有一定準確性，但缺少重要技術細節。
- 0.25：描述模糊或不準確。
- 0.0：沒有技術細節。
### 評分項 3：侷限分析（權重 25%）
- 1.0：清楚註記關鍵系統的侷限，包含：資安監測與情資系統並非為科學分析設計、NCRA 過濾
  規則會濾掉罕見小訊號、終端側／骨幹側各有涵蓋與解析度的取捨、自願標示只對配合者有效、
  民眾截圖通常幫助有限、雷達式原始紀錄保存數月即刪除、情報級系統卡機敏分級。
- 0.75：多數系統都註記了侷限。
- 0.5：註記了一些侷限但不完整。
- 0.25：提及的侷限很少。
- 0.0：未討論任何侷限。
### 評分項 4：組織與呈現（權重 20%）
- 1.0：分類清楚、最上方有摘要表、每筆項目格式一致（名稱／擁有者／描述／關聯／侷限／
  提到者），繁體中文通順，便於查閱與比較各來源。
- 0.75：組織良好，僅有少許問題。
- 0.5：有組織但格式不一致。
- 0.25：組織不佳。
- 0.0：沒有組織或非繁體中文。
