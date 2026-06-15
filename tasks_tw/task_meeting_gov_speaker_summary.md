---
id: task_meeting_gov_speaker_summary
name: |
  NASA UAP 聽證會發言者摘要
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_gov_speaker_summary
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T131tw_meeting_gov_speaker_summary
workspace_files:
- source: meetings/2025-07-30-nasa-holds-first-public-meeting-on-ufos-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# NASA UAP 聽證會發言者摘要


## Prompt

我手上有一份逐字稿檔案 `transcript.md`，來自 NASA 首場關於不明異常現象（Unidentified Anomalous Phenomena, UAPs/UFOs）的公開會議。這是 NASA 的 UAP 獨立研究小組依《聯邦諮詢委員會法》（Federal Advisory Committee Act, FACA）召開的審議會議。

請幫我讀過逐字稿，產出一個名為 `speaker_summary.md` 的檔案，摘述每位發言者的重點。對於每位做了實質報告或發言的發言者，請列出：

- **發言者姓名與角色／所屬單位**（若有提及）
- **重點（Key points）**：條列式
- **值得注意的引言（Notable quotes）**：1-2 句能呈現其核心訊息的直接引言

請依發言者出場順序排列。把次要的插話或簡短的程序性發言歸入「Panel Q&A Contributions」區段，而非各給一個完整條目。聚焦於做了報告或實質發言的發言者。

## Expected Behavior

助手應該：

1. 讀取並解析完整逐字稿
2. 辨識主要發言者：Dan Evans（NASA，指定聯邦官員）、Nicola Fox（NASA Associate Administrator）、David Spergel（小組主席，宇宙學家）、Sean Kirkpatrick（AARO 主任）、Mike Freie（FAA）、Nadia Drake（科學記者）、Paula Bontempi（地球科學家）、Federica Bianco（天體物理學家／資料科學家）、David Grinspoon（行星科學家／天體生物學家）等
3. 準確摘述每位發言者的重點
4. 包含值得注意的直接引言
5. 撰寫一份結構良好的 markdown 檔案

關鍵發言者及其要點：

- **Dan Evans**：開場、處理對小組成員的騷擾、說明 FACA 合規、描述 UAP 研究目的
- **Nicola Fox**：強調資料品質的侷限、解釋機密與非機密資料的區別（戰機／自由女神像的比喻）、推廣開放資料
- **David Spergel**：需要高品質的校準資料、快速電波爆發（fast radio bursts）的類比、異常作為發現的引擎、公民科學的機會
- **Sean Kirkpatrick**：AARO 的 800+ 案例、僅 2-5% 真正異常、展示解密影像、描述感測器校準需求、建議群眾外包與地基儀器
- **Mike Freie**：FAA 的監視能力與侷限、雷達涵蓋範圍圖、管制員每月 3-5 件 UAP 通報、過濾技術
- **Nadia Drake**：界定 UAP 問題、「大乾草堆裡的細針」、沒有外星起源的決定性證據
- **Paula Bontempi**：NASA 的獨特角色——60 年經驗、開放資料、公眾信任、跨領域團隊
- **Federica Bianco**：資料標準（FAIR）、異常偵測方法、群眾外包平台建議、機器學習的就緒程度
- **David Grinspoon**：技術特徵（technosignatures）、天體生物學連結、與 UAP 相關的地球以外觀測

## Grading Criteria

- [ ] 已建立輸出檔案 `speaker_summary.md`
- [ ] 辨識 Dan Evans 並摘述其重點（開場、騷擾疑慮、FACA 合規）
- [ ] 辨識 Nicola Fox 並摘述其重點（資料品質、機密與非機密之別）
- [ ] 辨識 David Spergel 並摘述其重點（需要校準資料、小組主席角色）
- [ ] 辨識 Sean Kirkpatrick 並摘述其重點（AARO 資料、800+ 案例、2-5% 異常）
- [ ] 辨識 Mike Freie／FAA 並摘述其重點（監視能力、雷達涵蓋）
- [ ] 至少摘述另外 3 位小組成員（Drake、Bontempi、Bianco、Grinspoon 等）
- [ ] 至少 3 位發言者附有直接引言
- [ ] 發言者大致依出場順序排列

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the speaker summary task.

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

    report_path = workspace / "speaker_summary.md"
    if not report_path.exists():
        alternatives = ["speakers.md", "summary.md", "speaker_summaries.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "dan_evans": 0.0,
            "nicola_fox": 0.0,
            "david_spergel": 0.0,
            "sean_kirkpatrick": 0.0,
            "faa_speaker": 0.0,
            "additional_panelists": 0.0,
            "quotes_included": 0.0,
            "speaker_order": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check Dan Evans
    dan_patterns = [r'dan\s+evans', r'designated\s+federal\s+official']
    has_dan = any(re.search(p, content_lower) for p in dan_patterns)
    dan_points = sum([
        bool(re.search(r'harass', content_lower)),
        bool(re.search(r'faca|federal\s+advisory', content_lower)),
        bool(re.search(r'stigma', content_lower)),
    ])
    scores["dan_evans"] = 1.0 if has_dan and dan_points >= 2 else (0.5 if has_dan else 0.0)

    # Check Nicola Fox
    fox_patterns = [r'nicola?\s+fox', r'nicky?\s+fox', r'dr\.?\s+fox']
    has_fox = any(re.search(p, content_lower) for p in fox_patterns)
    fox_points = sum([
        bool(re.search(r'classif', content_lower)),
        bool(re.search(r'calibrat', content_lower)),
        bool(re.search(r'open\s+data|data\.nasa', content_lower)),
    ])
    scores["nicola_fox"] = 1.0 if has_fox and fox_points >= 2 else (0.5 if has_fox else 0.0)

    # Check David Spergel
    spergel_patterns = [r'sperg[eo]l', r'panel\s+chair']
    has_spergel = any(re.search(p, content_lower) for p in spergel_patterns)
    spergel_points = sum([
        bool(re.search(r'fast\s+radio\s+burst|frb', content_lower)),
        bool(re.search(r'calibrat', content_lower)),
        bool(re.search(r'high.quality\s+data', content_lower)),
        bool(re.search(r'citizen\s+science', content_lower)),
    ])
    scores["david_spergel"] = 1.0 if has_spergel and spergel_points >= 2 else (0.5 if has_spergel else 0.0)

    # Check Sean Kirkpatrick
    kirk_patterns = [r'kirkpatrick', r'aaro']
    has_kirk = any(re.search(p, content_lower) for p in kirk_patterns)
    kirk_points = sum([
        bool(re.search(r'800', content_lower)),
        bool(re.search(r'2.{0,5}5\s*%|single.digit\s*percent', content_lower)),
        bool(re.search(r'declassif|footage|video', content_lower)),
        bool(re.search(r'five\s+eyes', content_lower)),
    ])
    scores["sean_kirkpatrick"] = 1.0 if has_kirk and kirk_points >= 2 else (0.5 if has_kirk else 0.0)

    # Check FAA speaker
    faa_patterns = [r'freie|faa']
    has_faa = any(re.search(p, content_lower) for p in faa_patterns)
    faa_points = sum([
        bool(re.search(r'radar', content_lower)),
        bool(re.search(r'14.?000\s*controller|controller', content_lower)),
        bool(re.search(r'3.{0,5}5\s*report|per\s+month', content_lower)),
        bool(re.search(r'surveillance', content_lower)),
    ])
    scores["faa_speaker"] = 1.0 if has_faa and faa_points >= 2 else (0.5 if has_faa else 0.0)

    # Check additional panelists (need at least 3 of: Drake, Bontempi, Bianco, Grinspoon, Gold, Wright, Kelly)
    additional = 0
    if re.search(r'drake', content_lower): additional += 1
    if re.search(r'bontempi', content_lower): additional += 1
    if re.search(r'bianco|federica', content_lower): additional += 1
    if re.search(r'grinspoon', content_lower): additional += 1
    if re.search(r'mike\s+gold|gold', content_lower): additional += 1
    if re.search(r'shelley\s+wright|wright', content_lower): additional += 1
    scores["additional_panelists"] = 1.0 if additional >= 4 else (0.5 if additional >= 2 else 0.0)

    # Check for quotes (look for quotation marks with substantial text)
    quote_patterns = re.findall(r'["\u201c].{20,}?["\u201d]', content)
    scores["quotes_included"] = 1.0 if len(quote_patterns) >= 3 else (0.5 if len(quote_patterns) >= 1 else 0.0)

    # Check speaker order (Evans/Fox before Kirkpatrick before FAA)
    evans_pos = content_lower.find('evans')
    kirk_pos = content_lower.find('kirkpatrick')
    faa_pos = content_lower.find('freie') if 'freie' in content_lower else content_lower.find('faa')
    if evans_pos >= 0 and kirk_pos >= 0 and faa_pos >= 0:
        scores["speaker_order"] = 1.0 if evans_pos < kirk_pos < faa_pos else 0.5
    elif evans_pos >= 0 and kirk_pos >= 0:
        scores["speaker_order"] = 1.0 if evans_pos < kirk_pos else 0.5
    else:
        scores["speaker_order"] = 0.0

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

### 評分項 1：發言者辨識完整性（權重 30%）

**1.0 分**：所有主要發言者皆被辨識，姓名、角色與所屬單位正確。至少涵蓋 8 位發言者。

**0.75 分**：多數主要發言者辨識正確。涵蓋 6-7 位。

**0.5 分**：核心發言者已辨識，但有些遺漏或角色有誤。涵蓋 4-5 位。

**0.25 分**：僅辨識少數發言者，許多遺漏。

**0.0 分**：未辨識發言者或完全錯誤。

### 評分項 2：重點準確性（權重 35%）

**1.0 分**：每位發言者的重點準確、具體，掌握其主要論點。包含具體細節，如統計數字（800+ 案例、2-5% 異常、每日 45,000 架次飛行）。

**0.75 分**：多數重點準確，僅有少許遺漏或籠統概括。

**0.5 分**：重點部分準確，但漏掉重要細節或含不準確之處。

**0.25 分**：重點模糊或明顯不準確。

**0.0 分**：未擷取有意義的重點。

### 評分項 3：引言品質（權重 15%）

**1.0 分**：包含相關、具啟發性的引言，能呈現每位發言者的觀點。引言準確或為貼近的轉述。

**0.75 分**：多數發言者附有良好引言。

**0.5 分**：包含一些引言，但可能籠統或選得不佳。

**0.25 分**：引言少或品質差。

**0.0 分**：未包含引言。

### 評分項 4：組織與可讀性（權重 20%）

**1.0 分**：依發言者出場順序良好組織，格式清楚，易於瀏覽與查閱。

**0.75 分**：組織良好，僅有少許問題。

**0.5 分**：可讀但組織不佳。

**0.25 分**：雜亂且難以追隨。

**0.0 分**：沒有可用的結構。
