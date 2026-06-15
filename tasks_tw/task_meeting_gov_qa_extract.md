---
id: task_meeting_gov_qa_extract
name: |
  NASA UAP 聽證會問答擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_gov_qa_extract
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T132tw_meeting_gov_qa_extract
workspace_files:
- source: meetings/2025-07-30-nasa-holds-first-public-meeting-on-ufos-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# NASA UAP 聽證會問答擷取


## Prompt

我手上有一份逐字稿檔案 `transcript.md`，來自 NASA 首場關於不明異常現象（UAPs/UFOs）的公開會議。這場會議包含多場報告，報告後有小組成員與報告者之間的問答交流，以及後來一場經篩選的公眾問答（public Q&A）。

請幫我讀過逐字稿，把所有問答交流擷取到名為 `qa_exchanges.md` 的檔案。對於每一筆交流，請列出：

- **提問者（Questioner）**：姓名與角色（若知道）
- **回答者（Respondent）**：姓名與角色（若知道）
- **主題（Topic）**：簡短標籤，例如「Data calibration」「Sensor limitations」
- **問題（Question）**：摘述或引用
- **回答（Answer）**：摘述重點

請依時間順序組織各筆交流，把小組對報告者的問答與後來的公眾問答區隔開來，並把每筆交流依序編號。

## Expected Behavior

助手應該：

1. 讀取並解析完整逐字稿
2. 辨識出有別於事先準備好的報告的問答交流
3. 擷取小組內部提問與公眾問答兩部分
4. 準確把問題與回答歸於正確的發言者
5. 精簡摘述問題與回答

關鍵問答交流包括：

- Spergel 問 Fox 關於 NASA 的資料校準流程
- Bontempi 問 Spergel 關於不同科學挑戰中的資料品質
- Gold 問 Spergel 關於宇宙學中的高風險／高報酬研究
- Drake 問 Kirkpatrick 關於具體數字（資料庫規模、年數、「few」的定義）
- Fox 問 Kirkpatrick 關於解密 P-3 影像的細節
- Walter 問 Kirkpatrick 關於感測器假影與資料處理
- Berea 問 Kirkpatrick 關於 AI/ML 技術
- Gold 問 Kirkpatrick 何謂異常＋污名化的影響
- Walter 問 Freie 關於雷達資料保存與運作模式
- Bianco 問 Freie 關於通報偏差與感測器部署決策
- Wright 問 Freie 關於非合作式監視的異常
- Gold 問 Freie 關於飛行員通報流程與歸檔
- 公眾問答：非人類智慧的證據、NASA 的 UAP 預算、發現外星生命的協定

## Grading Criteria

- [ ] 已建立輸出檔案 `qa_exchanges.md`
- [ ] 辨識出至少 10 筆不同的問答交流
- [ ] 小組對報告者的問答與公眾問答區段分開
- [ ] 包含 Drake 向 Kirkpatrick 提問資料庫數字的交流
- [ ] 包含 Kirkpatrick 關於 800+ 案例與 2-5% 異常的回應
- [ ] 包含至少一筆與 FAA 相關的問答交流
- [ ] 包含公眾問答中關於非人類智慧／外星起源的問題
- [ ] 問題與回答正確歸於具名發言者
- [ ] 各筆交流有編號或清楚分隔

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the Q&A extraction task.

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

    report_path = workspace / "qa_exchanges.md"
    if not report_path.exists():
        alternatives = ["qa.md", "questions_answers.md", "q_and_a.md", "qa_extract.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "exchange_count": 0.0,
            "section_separation": 0.0,
            "drake_kirkpatrick": 0.0,
            "case_numbers": 0.0,
            "faa_qa": 0.0,
            "nhi_question": 0.0,
            "attribution": 0.0,
            "numbering": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Count exchanges (look for numbered items or Q/A patterns)
    exchange_patterns = re.findall(r'(?:^|\n)\s*(?:\d+[\.\):]|#{2,3}\s*(?:exchange|q&?a|question))', content_lower)
    questioner_patterns = re.findall(r'question(?:er)?|asked|q:', content_lower)
    scores["exchange_count"] = 1.0 if len(exchange_patterns) >= 10 or len(questioner_patterns) >= 10 else (0.5 if len(exchange_patterns) >= 5 or len(questioner_patterns) >= 5 else 0.0)

    # Check section separation (panel Q&A vs public Q&A)
    has_sections = bool(re.search(r'public\s+q\s*&?\s*a|curated|audience|submitted', content_lower))
    has_panel = bool(re.search(r'panel|presenter|presentation', content_lower))
    scores["section_separation"] = 1.0 if has_sections and has_panel else (0.5 if has_sections or has_panel else 0.0)

    # Check Drake-Kirkpatrick exchange
    has_drake = bool(re.search(r'drake', content_lower))
    has_kirk = bool(re.search(r'kirkpatrick', content_lower))
    has_numbers_q = bool(re.search(r'how\s+(?:big|many|large)|database|number', content_lower))
    scores["drake_kirkpatrick"] = 1.0 if has_drake and has_kirk and has_numbers_q else (0.5 if has_drake and has_kirk else 0.0)

    # Check case numbers in response
    has_800 = bool(re.search(r'800|eight\s+hundred', content_lower))
    has_pct = bool(re.search(r'2.{0,5}5\s*%|single.digit|percent', content_lower))
    scores["case_numbers"] = 1.0 if has_800 and has_pct else (0.5 if has_800 or has_pct else 0.0)

    # Check FAA Q&A
    has_faa_qa = bool(re.search(r'faa|freie', content_lower))
    faa_topics = sum([
        bool(re.search(r'radar\s+data|retain|retention', content_lower)),
        bool(re.search(r'filter', content_lower)),
        bool(re.search(r'report.*process|pilot.*report', content_lower)),
        bool(re.search(r'deploy|coverage|site', content_lower)),
    ])
    scores["faa_qa"] = 1.0 if has_faa_qa and faa_topics >= 2 else (0.5 if has_faa_qa else 0.0)

    # Check non-human intelligence question
    nhi_patterns = [
        r'non.?human\s+intelligence',
        r'extraterrestrial\s+(?:origin|life|intelligence)',
        r'alien',
        r'extraordinary\s+claims.*extraordinary\s+evidence',
    ]
    scores["nhi_question"] = 1.0 if sum(bool(re.search(p, content_lower)) for p in nhi_patterns) >= 2 else (0.5 if any(re.search(p, content_lower) for p in nhi_patterns) else 0.0)

    # Check attribution (multiple named speakers in Q&A context)
    named_speakers = set()
    for name in ['drake', 'kirkpatrick', 'spergel', 'fox', 'freie', 'gold', 'walter', 'bianco', 'bontempi', 'wright', 'grinspoon', 'berea']:
        if name in content_lower:
            named_speakers.add(name)
    scores["attribution"] = 1.0 if len(named_speakers) >= 6 else (0.5 if len(named_speakers) >= 3 else 0.0)

    # Check numbering/delineation
    numbered = len(re.findall(r'(?:^|\n)\s*\d+[\.\):]', content)) >= 5
    headed = len(re.findall(r'(?:^|\n)#{2,4}\s', content)) >= 5
    separated = len(re.findall(r'(?:^|\n)---', content)) >= 3
    scores["numbering"] = 1.0 if numbered or headed else (0.5 if separated else 0.0)

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

### 評分項 1：交流完整性（權重 30%）

**1.0 分**：擷取出至少 12 筆不同的問答交流，涵蓋所有主要報告問答場次與公眾問答。沒有遺漏重要交流。

**0.75 分**：擷取 8-11 筆交流，涵蓋多數場次。

**0.5 分**：擷取 5-7 筆交流，但漏掉一些關鍵的。

**0.25 分**：少於 5 筆交流，或有重大缺口。

**0.0 分**：未擷取任何交流。

### 評分項 2：歸屬準確性（權重 25%）

**1.0 分**：所有問題與回答都正確歸於對的發言者，姓名與角色準確。

**0.75 分**：多數歸屬正確，僅有一兩處錯誤。

**0.5 分**：數處歸屬錯誤或缺少姓名。

**0.25 分**：頻繁誤歸。

**0.0 分**：沒有歸屬或全然錯誤。

### 評分項 3：摘要品質（權重 25%）

**1.0 分**：問題與回答皆精簡且準確地摘述，掌握必要資訊而不冗長。關鍵細節如具體數字、例子與結論皆保留。

**0.75 分**：摘要良好，僅有少許遺漏。

**0.5 分**：有摘要，但漏掉關鍵細節或過於模糊。

**0.25 分**：摘要品質差。

**0.0 分**：沒有摘要，或只是無脈絡的原始引言。

### 評分項 4：組織（權重 20%）

**1.0 分**：依時間順序清楚組織，小組問答與公眾問答分開。每筆交流有編號並附主題標籤。便於查閱。

**0.75 分**：組織良好，僅有少許問題。

**0.5 分**：有一些組織，但區段混雜或難以瀏覽。

**0.25 分**：組織不佳。

**0.0 分**：沒有可辨識的組織。
