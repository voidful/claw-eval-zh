---
id: task_meeting_advisory_acronyms
name: 頻譜共用顧問委員會：縮寫詞彙表（虛構）
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_advisory_acronyms
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T124tw_meeting_advisory_acronyms
workspace_files:
- source: tw/meetings/tw_advisory_meeting.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 頻譜共用顧問委員會：縮寫詞彙表（虛構）

## Prompt

工作區裡有一份政府顧問委員會的會議逐字稿 meeting-transcript.md（虛構的台灣
「數位治理委員會 智慧城市暨資安顧問委員會（DGC-SCAB）」第 14 次會議）。會議於
2025 年 5 月 30 日在台北市南港數位治理大樓召開，主題是 1755-1850 MHz 聯邦級
頻段之政府與商用寬頻共用（spectrum sharing）與遷移（relocation）。逐字稿全文
為繁體中文，機關／單位多以中文全名與中文簡稱表示（如「頻管署」），技術與法規
名稱則夾雜英文縮寫（如 DGC、MHz、LTE、UAV、STA、ISART 等）。

請幫我分析這份逐字稿，在一個名為 `acronym_glossary.md` 的檔案中，建立一份完整的
縮寫詞彙表。對於每個找到的縮寫或簡稱，請列出：

- **縮寫**：逐字稿中使用的簡稱（如 DGC、MHz、STA）
- **全稱**：它所代表的完整名稱（中文全稱為主，可附英文對應）
- **脈絡**：簡述它在本次會議中的使用方式（1-2 句，須貼合本次頻譜共用會議）
- **類別**：政府機關、頻譜／技術、法規、業界、軍事或其他

請依英文字母順序（中文簡稱排在後面）排序，並在最後附上找到的縮寫與簡稱總數。

提醒：機關／單位類在逐字稿中以中文全名與中文簡稱表示（例如頻譜管理署簡稱
「頻管署」、行政院科技與政策辦公室簡稱「科政辦」）；國際標準、技術與法規等
通用術語則保留英文縮寫（如 MHz、LTE、STA）。請把所有出現的縮寫與簡稱都擷取
出來，包含各工作小組 WG1～WG5。

## Expected Behavior

助手應讀取 meeting-transcript.md，辨識所有縮寫與簡稱，判斷其中文全稱、貼合
會議的脈絡與類別，依字母順序整理後寫入 acronym_glossary.md，並在最後附上總數。

逐字稿中出現的關鍵縮寫與簡稱（最低集合，全稱以台灣語境為準）：

| 縮寫／簡稱 | 全稱（台灣語境） | 類別 |
|------|------------------|------|
| DGC | 數位治理委員會 | 政府機關 |
| SCAB | 智慧城市暨資安顧問委員會 | 政府機關 |
| 頻管署 | 頻譜管理署 | 政府機關 |
| 科政辦 | 行政院科技與政策辦公室 | 政府機關 |
| 主預辦 | 行政院主計與預算辦公室 | 政府機關 |
| 電信所 | 電信技術研究所 | 政府機關 |
| 資安署 | 數位發展部資通安全署 | 政府機關 |
| 鼎峰救難協會 | 鼎峰緊急救難服務協會 | 其他 |
| 公網會 | 台灣公共利益網路基金會 | 其他 |
| 電信公會 | 中華電信業者公會 | 產業 |
| ISART | 先進無線技術國際研討會 | 頻譜技術 |
| MHz | 百萬赫茲（Megahertz） | 頻譜技術 |
| GHz | 十億赫茲（Gigahertz） | 頻譜技術 |
| LTE | 長期演進技術（Long-Term Evolution） | 產業 |
| UAV | 無人機／無人飛行載具 | 軍事 |
| PCS | 個人通訊服務 | 頻譜技術 |
| AWS | 先進無線服務 | 頻譜技術 |
| CMRS | 商用行動無線服務 | 產業 |
| STA | 特別臨時授權（Special Temporary Authority） | 法規 |
| CSEA | 商用頻譜加值條例 | 法規 |
| TIA | 電信工業協會 | 產業 |
| TSB | 電信系統公報 | 頻譜技術 |
| ITU-R | 國際電信聯盟無線電通信部門 | 頻譜技術 |
| WRC | 世界無線電通信大會 | 頻譜技術 |
| EW | 電子戰（Electronic Warfare） | 軍事 |
| IP | 智慧財產權 | 其他 |
| WG1～WG5 | 第 1 至第 5 工作小組 | 其他 |

機關／單位類縮寫（頻管署、科政辦、主預辦、電信所、公網會、電信公會等）以
中文全名與中文簡稱表示，避免憑空套用英文縮寫。總計約 25～30 個縮寫與簡稱。

## Grading Criteria

- [ ] 建立縮寫詞彙表檔案 acronym_glossary.md
- [ ] DGC 正確展開為「數位治理委員會」
- [ ] 簡稱「頻管署」正確對應「頻譜管理署」
- [ ] 辨識出至少 15 個不重複的縮寫或簡稱
- [ ] 辨識出至少 20 個不重複的縮寫或簡稱（加分門檻）
- [ ] 包含技術類縮寫（MHz、GHz、LTE、UAV、STA）
- [ ] 包含機關／單位簡稱（頻管署、科政辦、主預辦、電信所）
- [ ] 對各項目套用類別或分組（政府機關／頻譜技術／法規／業界／軍事／其他）
- [ ] 採用英文字母順序排序，並附上縮寫總數

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """頻譜共用顧問委員會（虛構）縮寫與簡稱詞彙表 grader。

    以工作區內的台灣逐字稿（dest=meeting-transcript.md）動態推導「應有的縮寫／
    簡稱與中文全稱」，再比對 agent 產出的中文報告 acronym_glossary.md。
    機關／單位類以中文全名與中文簡稱（如「頻管署」）表示，技術／法規通用術語
    則為拉丁字母；逐字稿與報告皆原樣保留，故以「縮寫／簡稱 + 中文全稱關鍵詞」
    雙重比對。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "dgc_expanded", "osm_expanded",
        "min_15_acronyms", "min_20_acronyms", "technical_acronyms",
        "gov_agencies", "categories_applied", "alphabetical_sort",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "acronym_glossary.md"
    if not report.exists():
        for alt in ["glossary.md", "acronyms.md", "acronym_list.md",
                    "acronym_glossary.txt", "縮寫詞彙表.md", "詞彙表.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")
    c_lower = c.lower()

    # --- 從逐字稿動態讀出「應有的縮寫對照」（避免硬寫） ---
    tpath = workspace / "meeting-transcript.md"
    if not tpath.exists():
        for alt in ["meeting_transcript.md", "transcript.md",
                    "meeting-transcript.txt"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    # 逐字稿中所有「縮寫／簡稱 → 中文全稱」候選：
    #   對照表段落（| 縮寫／簡稱 | 全稱… |）抓出明確映射；第一欄可為拉丁縮寫
    #   （如 DGC、MHz）或中文簡稱（如 頻管署、科政辦）。
    tw_acr_full = {}    # 拉丁縮寫(大寫) -> 中文全稱字串
    tw_abbr_full = {}   # 中文簡稱 -> 中文全稱字串
    for line in t.split("\n"):
        m = re.match(r"\s*\|\s*([A-Za-z][A-Za-z0-9\-]{1,7})\s*\|\s*([^|]+)\|", line)
        if m:
            acr = m.group(1).upper()
            full = m.group(2).strip()
            if acr not in tw_acr_full:
                tw_acr_full[acr] = full
            continue
        m2 = re.match(r"\s*\|\s*([一-鿿]{2,6})\s*\|\s*([^|]+)\|", line)
        if m2:
            abbr = m2.group(1).strip()
            full = m2.group(2).strip()
            if abbr not in tw_abbr_full:
                tw_abbr_full[abbr] = full

    # 全文出現過的拉丁縮寫（2~6 字，含連字號如 ITU-R）。
    transcript_acrs = set()
    for mm in re.finditer(r"\b([A-Z]{2,6}(?:-[A-Z])?)\b", t):
        transcript_acrs.add(mm.group(1).upper())
    # WG1~WG5 之類帶數字者另計
    for mm in re.finditer(r"\bWG[1-9]\b", t):
        transcript_acrs.add(mm.group(0).upper())
    # 機關／單位中文簡稱（從對照表取得，另含常見口語簡稱）。
    transcript_abbrs = set(tw_abbr_full.keys())
    for ab in ["頻管署", "科政辦", "主預辦", "電信所", "資安署",
               "鼎峰救難協會", "公網會", "電信公會"]:
        if not t or ab in t:
            transcript_abbrs.add(ab)

    def acr_in_report(acr):
        # 縮寫在報告中出現（大小寫不敏感，作為獨立詞）
        return re.search(r"\b" + re.escape(acr) + r"\b", c, re.IGNORECASE) is not None

    def chinese_full_in_report(acr):
        """逐字稿對照表給出的中文全稱，其關鍵詞是否也出現在報告中。"""
        full = tw_acr_full.get(acr, "")
        # 取中文片段（連續 2 字以上的 CJK），任一片段命中即可
        frags = re.findall(r"[一-鿿]{2,}", full)
        for f in frags:
            if f and f in c:
                return True
        return False

    scores = {"report_created": 1.0}

    # --- DGC：須出現縮寫 DGC 且報告含「數位治理委員會」（從逐字稿動態取） ---
    dgc_full = tw_acr_full.get("DGC", "數位治理委員會")
    dgc_frag = (re.findall(r"[一-鿿]{4,}", dgc_full) or ["數位治理委員會"])[0]
    scores["dgc_expanded"] = 1.0 if (
        acr_in_report("DGC") and (dgc_frag in c or "數位治理委員會" in c)
    ) else 0.0

    # --- 頻管署：報告須含中文簡稱「頻管署」且對應「頻譜管理署」 ---
    # （機關英文縮寫已在地化為中文全名＋中文簡稱）
    scores["osm_expanded"] = 1.0 if (
        "頻管署" in c and "頻譜管理署" in c
    ) else 0.0

    # --- 不重複縮寫／簡稱計數：報告中出現、且確實是逐字稿中存在者 ---
    # 以逐字稿集合為基準，避免把報告裡隨意大寫詞（如英文段落）灌水。
    found_acrs = set()
    for acr in transcript_acrs:
        if acr_in_report(acr):
            found_acrs.add(acr)
    # 報告自身額外出現、且為已知頻譜縮寫者亦可計入（容錯）。
    # 機關／單位英文縮寫已在地化為中文，故 known 僅保留技術／法規通用術語
    # 與委員會代碼（DGC、SCAB）及工作小組編號。
    known = {"DGC", "SCAB", "ISART", "MHZ", "GHZ", "LTE", "UAV", "PCS",
             "AWS", "CMRS", "STA", "CSEA", "TIA", "TSB",
             "ITU", "ITU-R", "WRC", "EW", "IP",
             "WG1", "WG2", "WG3", "WG4", "WG5"}
    for acr in known:
        if acr_in_report(acr):
            found_acrs.add(acr)
    # 機關／單位中文簡稱亦計入不重複總數。
    for ab in transcript_abbrs:
        if ab in c:
            found_acrs.add(ab)
    count = len(found_acrs)
    scores["min_15_acronyms"] = 1.0 if count >= 15 else (0.5 if count >= 10 else 0.0)
    scores["min_20_acronyms"] = 1.0 if count >= 20 else (0.5 if count >= 15 else 0.0)

    # --- 技術類縮寫（MHz、GHz、LTE、UAV、STA、PCS） ---
    tech_acrs = ["MHZ", "GHZ", "LTE", "UAV", "STA", "PCS"]
    tech_found = sum(1 for a in tech_acrs if acr_in_report(a))
    scores["technical_acronyms"] = 1.0 if tech_found >= 4 else (0.5 if tech_found >= 2 else 0.0)

    # --- 政府機關縮寫／簡稱（頻管署、科政辦、主預辦、電信所＋委員會代碼 DGC/SCAB） ---
    gov_abbrs = ["頻管署", "科政辦", "主預辦", "電信所", "資安署"]
    gov_found = sum(1 for a in gov_abbrs if a in c)
    gov_found += sum(1 for a in ["DGC", "SCAB"] if acr_in_report(a))
    scores["gov_agencies"] = 1.0 if gov_found >= 4 else (0.5 if gov_found >= 2 else 0.0)

    # --- 類別／分組：報告須出現數種類別關鍵詞（中英皆可） ---
    category_patterns = [
        r"政府|機關|agency|agencies|government",
        r"頻譜|技術|technical|spectrum",
        r"法規|法令|regulator|regulation",
        r"業界|產業|industry|commercial",
        r"軍事|國防|military|defense",
        r"類別|分類|categor|group|分組",
    ]
    cat_found = sum(1 for p in category_patterns if re.search(p, c, re.IGNORECASE))
    scores["categories_applied"] = 1.0 if cat_found >= 3 else (0.5 if cat_found >= 2 else 0.0)

    # --- 字母排序：抽出各行開頭的縮寫，檢查是否大致依字母排序 ---
    acr_lines = []
    for line in c.split("\n"):
        s = line.strip()
        if not s:
            continue
        # 列表／表格／標題列開頭抓第一個拉丁縮寫
        m = re.match(r"[\*\-\|#>\s]*\**\s*([A-Z]{2,}(?:-[A-Z])?|WG[1-9])\b", s)
        if m:
            acr_lines.append(m.group(1).upper())

    if len(acr_lines) >= 5:
        sorted_lines = sorted(acr_lines)
        matches = sum(1 for a, b in zip(acr_lines, sorted_lines) if a == b)
        ratio = matches / len(acr_lines)
        scores["alphabetical_sort"] = 1.0 if ratio >= 0.7 else (0.5 if ratio >= 0.4 else 0.0)
    elif len(acr_lines) >= 2:
        scores["alphabetical_sort"] = 0.5
    else:
        scores["alphabetical_sort"] = 0.0

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

### 評分項 1：縮寫涵蓋度（權重 35%）
- 1.0：辨識出 25 個以上縮寫與簡稱，包含冷僻的如 CSEA、ISART、TSB、CMRS，機關
  簡稱如頻管署、科政辦、主預辦、電信所、公網會，以及 WG1～WG5 工作小組。
  既涵蓋機關／單位簡稱，也涵蓋技術性頻譜術語。
- 0.75：辨識出 20～24 個縮寫與簡稱，涵蓋多數主要類別。
- 0.5：辨識出 15～19 個縮寫與簡稱，涵蓋明顯項目但漏掉數個領域專有術語。
- 0.25：辨識出 10～14 個縮寫與簡稱，大多只是常見機關。
- 0.0：辨識出的縮寫與簡稱少於 10 個。
### 評分項 2：展開準確性（權重 30%）
- 1.0：所有縮寫與簡稱展開皆正確且貼合台灣語境（DGC＝數位治理委員會、頻管署＝
  頻譜管理署、STA＝特別臨時授權、ISART＝先進無線技術國際研討會、CMRS＝商用
  行動無線服務）。
- 0.75：多數展開正確，僅有一兩處小錯。
- 0.5：常見項目正確，但數個領域專有縮寫錯誤或缺少展開。
- 0.25：多處展開錯誤。
- 0.0：展開大多錯誤或捏造（如套用與本逐字稿不符之機關名稱）。
### 評分項 3：脈絡品質（權重 20%）
- 1.0：每筆項目都有貼合本次會議的脈絡描述，說明該縮寫與 1755-1850 MHz 頻譜共用
  討論的關聯（如 STA 是台灣大哥大會同電信公會提出的實地量測申請）。
- 0.75：多數項目有實用脈絡。
- 0.5：有脈絡但偏籠統（只重述全稱，而非會議脈絡）。
- 0.25：脈絡極少或為樣板文字。
- 0.0：完全沒有提供脈絡。
### 評分項 4：組織與分類（權重 15%）
- 1.0：依英文字母排序、分類清楚（政府機關、頻譜技術、法規、業界、軍事、其他）、
  全篇格式一致，並附縮寫總數。
- 0.75：組織良好，僅有少許格式不一致。
- 0.5：有一些組織，但分類或排序不完整。
- 0.25：組織不佳。
- 0.0：沒有組織。
