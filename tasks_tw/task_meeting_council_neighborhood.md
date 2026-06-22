---
id: task_meeting_council_neighborhood
name: 南港市議會逐字稿 — 辨識里別與選區提及
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_neighborhood
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T114tw_meeting_council_neighborhood
workspace_files:
- source: tw/meetings/tw_council_meeting.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 南港市議會逐字稿 — 辨識里別與選區提及

## Prompt

工作區裡有一份 2026 年 4 月 2 日召開的「南港市議會 第 12 屆第 3 次定期會」會議逐字稿
（虛構教學素材），存放在 transcript.md。請以台灣地方議會的語境閱讀整份逐字稿，產生一份
neighborhoods_report.md，辨識出稿中所有提及的**里別、選區（行政區）、地理區域與特定地點**
（含門牌地址、軍事用地、跨縣市比較對象等）。

每個地點請包含：
- 地點名稱（里別／選區／路段／門牌等）
- 背景脈絡（與哪個議案、陳情或議題相關）
- 相關發言者或議項（例如哪位議員、哪位市民、第幾案）
- 相關議題（治安、開發、街友安置、管線下水道、分區變更等）

整理時請納入：
- **以選區為基礎的概覽**（南港市議會共 5 個主要選區，逐字稿第七節有彙整）
- **出現次數統計**（提及頻次）
- **議題交叉對照**（cross-reference）

請以新臺幣（NT$）、台灣地名與 Asia/Taipei 時區的語境撰寫，數值請以 transcript.md
內的實際內容為準，不要捏造逐字稿中沒有的地點或數字。

## Expected Behavior

助手應讀取 transcript.md（虛構南港市議會逐字稿）並產出 neighborhoods_report.md，
準確辨識下列里別／選區／地點及其脈絡（皆為虛構）：

- 廟前里（第 6 選區）：治安改善，麥尼爾巡佐 獲本月模範員警，竊盜與街頭犯罪下降。
- 西港里（第 4 選區）：中崙倉庫園區 開發、未來職棒球場（樂天桃猿）選址、義塚公園 保存；
  為本日提及最頻繁地點（提及 6 次）。
- 南港大道沿線（第 2 選區）：封街施工、老舊管線與雨水下水道更新，商家 米其里尼 陳情。
- 東港里（第 5 選區）：東港路廊 建設、土地分區變更與環評補充。
- 高地里（第 5 選區）：街友（遊民）安置，中正路高架橋下，高德森 陳情。
- 社子里（第 2 選區）：雨水下水道與颱風（凱米颱風）防災積水。
- 古堡里 與 古堡灣：人行道（騎樓）退縮法規漏洞，班奈特 陳情。
- 市中心（南港大道商圈）：商業活動與交通。
- 河岸步道（基隆河 河岸步道）：與 中崙倉庫園區 開發及西側 串聯／延伸。
- 永豐里：社區權益。
- 重要門牌（分區變更基地）：公道五路 4102 號、市民大道二段 2707 號、南港大道 110 號。
- 南港空軍基地：周邊飛航噪音與用地協調。
- 跨縣市比較：參考 台中、嘉義、高雄 等地之容量費與都更經驗。

並以選區分組概覽、提及次數與議題交叉對照方式組織，辨識至少 15 個不同地點，
涵蓋從門牌地址到區域層級等多種尺度。

## Grading Criteria

- [ ] 已建立報告檔案 neighborhoods_report.md
- [ ] 廟前里 與 麥尼爾巡佐 / 治安犯罪
- [ ] 西港里 與 中崙倉庫園區 / 職棒球場（樂天桃猿）
- [ ] 南港大道 與 封街施工 / 老舊管線下水道
- [ ] 東港里 與 開發（東港路廊 / 分區變更 / 環評）
- [ ] 高地里 與 街友（遊民）安置
- [ ] 3 處以上分區變更門牌（公道五路 4102、市民大道二段 2707、南港大道 110）
- [ ] 提及 南港空軍基地
- [ ] 記下 河岸步道 與 中崙倉庫園區 / 串聯關係
- [ ] 出現次數統計或議題交叉對照
- [ ] 15 個以上不同地點

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """南港市議會（虛構）里別／選區辨識 grader。

    查核項依台灣逐字稿（dest=transcript.md）推導之事實比對，
    比對 agent 產出之中文報告 neighborhoods_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)
    report_path = workspace / "neighborhoods_report.md"
    if not report_path.exists():
        for alt in ["neighborhoods.md", "locations.md", "districts.md",
                    "areas.md", "里別報告.md", "社區報告.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = ["report_created", "temple_crest", "west_tampa", "south_howard",
            "east_tampa", "highland_pines", "rezoning_addresses", "macdill",
            "riverwalk", "frequency_or_crossref", "location_count"]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report_path.read_text(encoding="utf-8", errors="ignore")

    # 廟前里：治安改善 / 麥尼爾巡佐 / 犯罪下降
    scores["temple_crest"] = 1.0 if (
        re.search(r"廟前里|廟前", c)
        and re.search(r"麥尼爾|治安|犯罪|竊盜|模範員警", c)
    ) else 0.0

    # 西港里：中崙倉庫園區 / 職棒球場（樂天桃猿）/ 開發
    scores["west_tampa"] = 1.0 if (
        re.search(r"西港里|西港", c)
        and re.search(r"中崙倉庫園區|中崙倉庫|樂天桃猿|猿|職棒|球場|開發", c)
    ) else 0.0

    # 南港大道：封街施工 / 老舊管線 / 雨水下水道
    scores["south_howard"] = 1.0 if (
        re.search(r"南港大道", c)
        and re.search(r"封街|施工|管線|下水道|米其里尼", c)
    ) else 0.0

    # 東港里：東港路廊 / 開發 / 分區變更 / 環評
    scores["east_tampa"] = 1.0 if (
        re.search(r"東港里|東港", c)
        and re.search(r"開發|建設|東港路廊|路廊|分區|環評", c)
    ) else 0.0

    # 高地里：街友 / 遊民 / 安置 / 中正路 / 高德森
    scores["highland_pines"] = 1.0 if (
        re.search(r"高地里|高地", c)
        and re.search(r"街友|遊民|安置|中正路|高德森", c)
    ) else 0.0

    # 分區變更門牌：公道五路 4102 / 市民大道二段 2707 / 南港大道 110
    addresses = [
        r"公道五路\s*4102|4102\s*號",
        r"市民大道(?:二段)?\s*2707|2707\s*號",
        r"南港大道\s*110|110\s*號",
    ]
    addr_hits = sum(1 for a in addresses if re.search(a, c))
    scores["rezoning_addresses"] = (
        1.0 if addr_hits >= 3 else (0.5 if addr_hits >= 2 else 0.0)
    )

    # 南港空軍基地
    scores["macdill"] = 1.0 if re.search(r"南港空軍基地|空軍基地", c) else 0.0

    # 河岸步道：與 中崙倉庫園區 / 串聯 / 延伸 / 西側 / 開發
    scores["riverwalk"] = 1.0 if (
        re.search(r"河岸步道|基隆河", c)
        and re.search(r"中崙倉庫|串聯|延伸|西側|連通|連結|開發|基隆河", c)
    ) else 0.0

    # 出現次數統計 或 議題交叉對照
    scores["frequency_or_crossref"] = 1.0 if re.search(
        r"提及\s*\d+\s*次|提及次數|提及頻次|頻次|次數統計|交叉對照|"
        r"cross[\s-]*ref|最熱門|最頻繁|最常|frequen", c
    ) else 0.0

    # 不同地點數（自台灣逐字稿推導之候選清單）
    location_patterns = [
        r"廟前里|廟前",
        r"西港里|西港",
        r"南港大道",
        r"東港里|東港",
        r"高地里|高地",
        r"社子里|社子",
        r"古堡里|古堡灣|古堡",
        r"市中心|商圈",
        r"河岸步道|基隆河",
        r"永豐里|永豐",
        r"中崙倉庫園區|中崙倉庫",
        r"南港空軍基地|空軍基地",
        r"公道五路",
        r"市民大道",
        r"忠孝東路",
        r"中正路",
        r"中興路",
        r"福橡活動中心|福橡",
        r"義塚公園|義塚",
        r"台中|臺中|嘉義|高雄",
    ]
    found = sum(1 for p in location_patterns if re.search(p, c))
    scores["location_count"] = (
        1.0 if found >= 15 else (0.75 if found >= 10 else (0.5 if found >= 6 else 0.0))
    )

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

### 評分項 1：完整度（權重 35%）
**1.0 分**：辨識 20 個以上地點。**0.75 分**：15-19 個。**0.5 分**：10-14 個。
**0.0 分**：少於 5 個。

### 評分項 2：背景脈絡（權重 25%）
**1.0 分**：每一地點皆有準確的背景脈絡（相關議案／發言者／議題）。
**0.5 分**：部分含糊。**0.0 分**：完全沒有脈絡。

### 評分項 3：組織（權重 25%）
**1.0 分**：依選區分組、有提及次數、有議題交叉對照。**0.5 分**：僅部分具備。
**0.0 分**：完全沒有組織。

### 評分項 4：廣度（權重 15%）
**1.0 分**：涵蓋多種尺度（從門牌地址到區域、軍事用地、跨縣市比較）。
**0.5 分**：僅單一尺度。**0.0 分**：極少。
