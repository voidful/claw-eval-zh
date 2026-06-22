---
id: task_meeting_council_public_comment
name: |
  市議會逐字稿 — 摘要公眾意見
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_public_comment
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T110tw_meeting_council_public_comment
workspace_files:
- source: tw/meetings/tw_council_meeting.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 市議會逐字稿 — 摘要公眾意見


## Prompt

我手邊有一份 2026 年 4 月 2 日（星期四，時區 Asia/Taipei）舉行的「南港市議會 第 12 屆第 3 次定期會」會議逐字稿，存放在 `transcript.md`。這是一份即時聽打的字幕稿（realtime captioning），並非正式逐字紀錄，內容以實際議事錄為準。逐字稿中的南港市、各里別、人名、機關、議案與金額皆為虛構教學素材。

請幫我分析其中「市民公眾意見發言（Public Comment）」的部分，並產生一個名為 `public_comments_report.md` 的檔案，摘要每一位上台（或線上視訊）發言市民的意見。針對每位發言者，請包含：

- **發言者姓名**（以逐字稿登載之姓名為準）
- **提及的主題或議程項目**（若適用，例如第幾案、里別）
- **提出的重點或關切事項**
- **對議會提出的任何具體請求或要求**（含金額、天數等具體數字）

最後也請附上一段**主題摘要（thematic summary）**，依主題領域（例如基礎建設、住宅、文史保存、警政、交通、環境防災等）將意見分組，並指出哪些主題引發最多市民關注。請以繁體中文（zh-TW）撰寫，金額沿用逐字稿之新臺幣（NT$）表示。

## Expected Behavior

助手應辨識出逐字稿「四、市民公眾意見發言（Public Comment）」這一段，並擷取每位發言者的發言。本日共 16 位市民登記發言（含 2 位線上視訊）。關鍵發言者與重點如下：

- **詹明慧**（西港里）— 第十六案「義塚公園／義塚紀念園區」，感謝議會通過保存無主墳塚遺址。
- **任薇**（西港里）— 義塚公園；代表西港里文史協會，請求市府編列 **新臺幣 8,000 萬元（NT$80,000,000）** 設置義塚紀念館暨族譜尋根中心。
- **海曉光**（退伍軍人代表）— 第二十二案退輔諮詢委員會；支持設置，但對委員多元組成（DEI／多元平等共融）條文有意見。
- **簡珮如**（社子里）— 雨水下水道與颱風（豪雨）防災；去年凱米颱風期間社子里嚴重積水，認為市府長期疏於排水維護。
- **高德森**（高地里）— 第 5 選區高地里遊民（街友）安置，中正路高架橋下街友聚集。
- **紀志中** — 交通議題，北北基跨域運輸（北北基大眾運輸協調會 跨縣市協調）、未來職棒球場（樂天桃猿主場）周邊交通衝擊。
- **莫雅淳**（在地文史工作者）— 南港在地黑歷史與族群史，請市府重視文史保存。
- **班奈特**（古堡里）— 人行道（騎樓）退縮法規漏洞，古堡灣一帶建商規避退縮人行道。
- **蒲怡婷**（家長代表）— 市警局（南港市警局）執法爭議，15 歲兒子與另一名少年遭 8 名員警包圍盤查，要求調閱密錄器。
- **米其里尼**（南港大道商家）— 南港大道封街施工影響生意，老舊管線與雨水下水道未更新。
- **賈明德** — 市府 2020 年購置的緊急發電機閒置未用，公帑浪費，請研考室清查列管。
- **駱明潔**（西港里）— 義塚公園後續維護，並關心永豐里社區權益。
- **卜雅玲**（社區居民）— 第十九至二十一案土地使用分區（zoning）變更，代表永泰物業管理公司住戶。
- **潘思妤**（中崙倉庫園區關注者）— 中崙倉庫園區從提案至今拖了 **1436 天**，請議會加速；退輔委員會也請盡速設置。
- **任明哲**（線上視訊）— 西港社區發展協會（西港 CDC）；針對中崙倉庫園區要求簽訂社區受益協議（CBA），保障在地就業與可負擔住宅。
- **羅志安**（線上視訊）— 第十六案義塚公園；依殯葬管理條例第 872 條規定，請市府妥善處理安溪舊塚遺骸。

助手應正確辨識義塚公園為多位發言者（詹明慧、任薇、駱明潔、羅志安）共同關注的熱門主題，並產出依主題分組的主題摘要。

## Grading Criteria

- [ ] 已建立報告檔案 public_comments_report.md
- [ ] 已辨識 詹明慧 與 義塚公園 的關聯
- [ ] 已辨識 任薇 與 8,000 萬元（NT$80,000,000）請求
- [ ] 已辨識 簡珮如 與 雨水下水道／颱風防災
- [ ] 已辨識 蒲怡婷 與 市警局執法爭議（15 歲兒子、8 名員警、密錄器）
- [ ] 已辨識 潘思妤 與 中崙倉庫園區（拖了 1436 天）
- [ ] 16 位發言者中至少辨識出 12 位
- [ ] 依主題分組的主題摘要（基礎建設、住宅、文史保存、警政、交通等）
- [ ] 義塚公園 被記為多位發言者共同提及的主題

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """對台灣化逐字稿（transcript.md）動態推導應有事實，比對 agent 的中文報告。

    只用標準函式庫。報告為中文 public_comments_report.md。
    """
    from pathlib import Path
    import re

    keys = [
        "report_created",
        "weilin_yizhong",
        "iman_8million",
        "cannella_stormwater",
        "pulin_police",
        "pan_zhonglunyard",
        "speaker_count",
        "thematic_summary",
        "yizhong_multiple",
    ]
    scores = {k: 0.0 for k in keys}
    workspace = Path(workspace_path)

    # 找出 agent 報告
    report_path = workspace / "public_comments_report.md"
    if not report_path.exists():
        for alt in [
            "public_comments_report.md",
            "public_comments.md",
            "comments_report.md",
            "comments.md",
            "公眾意見報告.md",
            "公眾意見.md",
        ]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return scores

    scores["report_created"] = 1.0
    try:
        content = report_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return scores

    # --- 從逐字稿動態推導「應有的 16 位公眾發言者姓名」 ---
    speaker_names = []
    try:
        tpath = workspace / "transcript.md"
        if tpath.exists():
            ttext = tpath.read_text(encoding="utf-8")
            in_pc = False
            for line in ttext.splitlines():
                # 進入「市民公眾意見發言」段落
                if re.search(r"市民公眾意見發言", line):
                    in_pc = True
                    continue
                # 離開該段落（進入「五、預算」等下一大段）
                if in_pc and re.match(r"^##\s*[五六七八]", line):
                    break
                if not in_pc:
                    continue
                # 形如：### 1. 詹明慧（西港里居民）
                m = re.match(r"^###\s*\d+\.\s*([^\s（(]+)", line.strip())
                if m:
                    nm = m.group(1).strip()
                    if nm and nm not in speaker_names:
                        speaker_names.append(nm)
    except (OSError, UnicodeDecodeError):
        speaker_names = []

    # 萬一逐字稿解析失敗，退回固定名單（與逐字稿一致）
    if len(speaker_names) < 16:
        speaker_names = [
            "詹明慧", "任薇", "海曉光", "簡珮如", "高德森", "紀志中",
            "莫雅淳", "班奈特", "蒲怡婷", "米其里尼", "賈明德", "駱明潔",
            "卜雅玲", "潘思妤", "任明哲", "羅志安",
        ]

    # --- 個別事實查核（中文關鍵字/數值）---
    yizhong = r"義塚"  # 義塚公園／義塚紀念園區／義塚紀念館
    scores["weilin_yizhong"] = (
        1.0 if ("詹明慧" in content and re.search(yizhong, content)) else 0.0
    )

    # 8,000 萬元 / NT$80,000,000 / 8000萬 等多種寫法
    eight_million = re.search(
        r"8[,，]?000\s*萬|8000\s*萬|八千萬|80[,，]?000[,，]?000",
        content,
    )
    scores["iman_8million"] = (
        1.0 if ("任薇" in content and eight_million) else 0.0
    )

    stormwater = re.search(r"雨水|颱風|豪雨|積水|淹水|防災|凱米", content)
    scores["cannella_stormwater"] = (
        1.0 if ("簡珮如" in content and stormwater) else 0.0
    )

    police = re.search(r"警|密錄器|員警|盤查|少年|兒子|未成年|執法", content)
    scores["pulin_police"] = (
        1.0 if ("蒲怡婷" in content and police) else 0.0
    )

    zhonglunyard = re.search(r"中崙倉庫|1436", content)
    scores["pan_zhonglunyard"] = (
        1.0 if ("潘思妤" in content and zhonglunyard) else 0.0
    )

    # --- 發言者辨識數量 ---
    found = sum(1 for nm in speaker_names if nm and nm in content)
    if found >= 14:
        scores["speaker_count"] = 1.0
    elif found >= 12:
        scores["speaker_count"] = 0.75
    elif found >= 8:
        scores["speaker_count"] = 0.5
    else:
        scores["speaker_count"] = 0.0

    # --- 主題摘要：須有「分組/主題」措辭 + 至少一個主題領域詞 ---
    has_grouping = re.search(r"主題|分類|分組|歸納|領域|彙整|歸類", content)
    has_topic = re.search(
        r"基礎建設|基礎設施|住宅|住房|文史|歷史|保存|警政|警察|治安|交通|"
        r"運輸|環境|防災|遊民|街友|分區|都市計畫|公共建設",
        content,
    )
    scores["thematic_summary"] = (
        1.0 if (has_grouping and has_topic) else 0.0
    )

    # --- 義塚 為多位發言者共同提及 ---
    # 動態：在逐字稿中找出提及「義塚」的公眾發言者，於報告中檢查其與「義塚」同段出現。
    yizhong_candidates = ["詹明慧", "任薇", "駱明潔", "羅志安"]
    # 以「段落」為單位（以兩個以上換行或 ### 標題切段較難，採行/區塊鄰近法）
    blocks = re.split(r"\n\s*\n|\n#{1,6}\s", content)
    yizhong_speakers = 0
    for nm in yizhong_candidates:
        for blk in blocks:
            if nm in blk and "義塚" in blk:
                yizhong_speakers += 1
                break
    if yizhong_speakers >= 2:
        scores["yizhong_multiple"] = 1.0
    elif yizhong_speakers >= 1:
        scores["yizhong_multiple"] = 0.5
    else:
        scores["yizhong_multiple"] = 0.0

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

### 評分項 1：發言者辨識（權重 35%）
**1.0 分**：辨識出全部 16 位發言者且主題正確。**0.75 分**：12-15 位。**0.5 分**：8-11 位。**0.0 分**：完全沒有。

### 評分項 2：摘要品質（權重 30%）
**1.0 分**：準確掌握每位發言者的重點與具體請求（含 8,000 萬元、1436 天、8 名員警等數值）。**0.5 分**：有附上但細節缺漏。**0.0 分**：完全沒有。

### 評分項 3：主題分組（權重 20%）
**1.0 分**：清楚依主題領域（基礎建設、住宅、文史保存、警政、交通、環境防災等）分組，並指出義塚公園等最受關注主題。**0.5 分**：有部分分組。**0.0 分**：完全沒有。

### 評分項 4：組織（權重 15%）
**1.0 分**：格式良好、條理清晰、依發言先後排列。**0.5 分**：組織不佳。**0.0 分**：難以閱讀。
