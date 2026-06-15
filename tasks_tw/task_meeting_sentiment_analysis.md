---
id: task_meeting_sentiment_analysis
name: |
  會議情緒分析
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_sentiment_analysis
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T126tw_meeting_sentiment_analysis
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 會議情緒分析


## Prompt

我手上有一個檔案 `meeting_transcript.md`，內含 GitLab 產品行銷團隊會議的逐字稿。請幫我分析這場會議整體的情緒與情感動態。

請把分析寫入名為 `sentiment_analysis.md` 的檔案，內容涵蓋：

- **整體會議情緒**（正面、負面或混合），並附簡短理由
- **逐主題情緒拆解**：針對每個主要討論主題，評定其情緒（正面／中性／負面）並說明原因
- **團隊動態觀察**：記錄出現認同、分歧、熱絡或不滿的時刻
- **值得注意的引言（notable quotes）**：摘出 3-5 句最能呈現會議情感基調的直接引言
- **投入程度（engagement level）**：評估參與者的投入程度（積極討論 vs. 被動聆聽）
- **潛在疑慮**：找出參與者表達遲疑、不確定或反對意見的主題

## Expected Behavior

助手應該：

1. 讀取會議逐字稿
2. 辨識整體偏正面／合作的情緒——團隊大致同調且具生產力
3. 逐主題分析情緒：
   - 企業活動：中性／略帶不確定（仍在等待各 GTM 團隊的回饋）
   - 產品公告：正面／熱絡（團隊對彙整成果感到興奮）
   - 競品資訊圖：正面，伴隨輕度爭辯（配色選擇、stage 名稱的描述性）
   - 訊息框架：高度投入、帶玩鬧氣氛（Talladega Nights 梗、對標語的熱烈討論）
4. 記錄具體動態：
   - 對「more speed, less risk」標語的熱情
   - 玩鬧式打趣（Ricky Bobby／NASCAR 梗、學校集會）
   - William 直白的「我不是愛就是恨」風格
   - 對公司不夠慶祝成果的輕微不滿
   - Samia 對競品試算表方法論的建設性反對意見
5. 摘出能呈現基調的相關引言
6. 評估整體偏高的投入程度

## Grading Criteria

- [ ] 已建立 `sentiment_analysis.md` 檔案
- [ ] 整體情緒正確辨識為正面／合作
- [ ] 至少分析 3 個主題並各自評定情緒
- [ ] 包含團隊動態或人際互動觀察
- [ ] 包含至少 2 句來自逐字稿的直接引言
- [ ] 評估了投入程度
- [ ] 至少辨識出一項疑慮或不確定之處
- [ ] 分析能區分不同主題間的不同情感基調

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting sentiment analysis task.

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

    # Check if report exists
    report_path = workspace / "sentiment_analysis.md"
    if not report_path.exists():
        alternatives = ["sentiment_report.md", "sentiment.md", "meeting_sentiment.md", "analysis.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "file_created": 0.0,
            "overall_sentiment": 0.0,
            "topic_breakdown": 0.0,
            "team_dynamics": 0.0,
            "quotes_included": 0.0,
            "engagement_assessed": 0.0,
            "concerns_identified": 0.0,
            "tonal_distinction": 0.0,
        }

    scores["file_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Overall sentiment (should be positive/collaborative)
    positive_patterns = [r'(?:overall|general).*(?:positive|collaborative|constructive|productive|upbeat|energetic)',
                         r'(?:positive|collaborative|constructive|productive).*(?:overall|tone|sentiment|atmosphere)']
    scores["overall_sentiment"] = 1.0 if any(re.search(p, content_lower) for p in positive_patterns) else 0.0

    # Topic-by-topic breakdown (at least 3 topics analyzed)
    topic_count = 0
    if re.search(r'(?:event|sponsor|re:?\s*invent|kubecon).*(?:sentiment|tone|feeling|positive|neutral|negative|uncertain)', content_lower):
        topic_count += 1
    if re.search(r'(?:product\s*announce|commit|feature|top\s*(?:5|five)).*(?:sentiment|tone|feeling|positive|neutral|negative|enthus)', content_lower):
        topic_count += 1
    if re.search(r'(?:infographic|competitive|comparison|design).*(?:sentiment|tone|feeling|positive|neutral|negative|debate)', content_lower):
        topic_count += 1
    if re.search(r'(?:messag|tagline|speed.*risk|source.*truth).*(?:sentiment|tone|feeling|positive|neutral|negative|engag|excit)', content_lower):
        topic_count += 1
    # Also accept if they just have 3+ subsections with sentiment words nearby
    if topic_count < 3:
        sections = re.findall(r'#{2,3}\s+[^\n]+', content)
        sentiment_words = len(re.findall(r'(?:positive|negative|neutral|mixed|enthusias|frustrat|uncertain|collaborat|engag)', content_lower))
        if len(sections) >= 4 and sentiment_words >= 5:
            topic_count = max(topic_count, 3)
    scores["topic_breakdown"] = 1.0 if topic_count >= 3 else (0.5 if topic_count >= 2 else 0.0)

    # Team dynamics observations
    dynamics_patterns = [
        r'(?:agreement|consensus|align)',
        r'(?:disagree|pushback|debate|tension)',
        r'(?:enthusiasm|excited|energy|passion)',
        r'(?:humor|joke|laugh|playful|banter)',
        r'(?:collaborat|team\s*work|support)',
    ]
    dynamics_count = sum(1 for p in dynamics_patterns if re.search(p, content_lower))
    scores["team_dynamics"] = 1.0 if dynamics_count >= 3 else (0.5 if dynamics_count >= 2 else 0.0)

    # Quotes included (look for quotation marks or attributed speech)
    quote_patterns = [
        r'[""\u201c].{10,}[""\u201d]',  # Quoted text
        r'(?:said|stated|mentioned|noted|commented)\s*[,:]?\s*[""\u201c]',
        r'>\s*.{10,}',  # Blockquotes
    ]
    quote_matches = sum(len(re.findall(p, content)) for p in quote_patterns)
    scores["quotes_included"] = 1.0 if quote_matches >= 2 else (0.5 if quote_matches >= 1 else 0.0)

    # Engagement level assessed
    engagement_patterns = [
        r'engag(?:ed|ement|ing)',
        r'(?:active|lively)\s*(?:discussion|participat|debate)',
        r'(?:high|strong|good)\s*(?:engagement|participation|energy)',
        r'(?:participat\w+|contribut\w+).*(?:most|all|several|multiple)',
    ]
    scores["engagement_assessed"] = 1.0 if sum(1 for p in engagement_patterns if re.search(p, content_lower)) >= 2 else (
        0.5 if any(re.search(p, content_lower) for p in engagement_patterns) else 0.0)

    # Concerns identified
    concern_patterns = [
        r'(?:concern|hesitat|uncertain|frustrat|challenge|struggle)',
        r'(?:difficult|tough|hard)\s*(?:to|for)',
        r'(?:pushback|resist|reluctan)',
        r'(?:not\s*(?:sure|certain)|unclear)',
        r'(?:worry|worries|worried|anxious)',
    ]
    scores["concerns_identified"] = 1.0 if sum(1 for p in concern_patterns if re.search(p, content_lower)) >= 2 else (
        0.5 if any(re.search(p, content_lower) for p in concern_patterns) else 0.0)

    # Tonal distinction (different tones identified for different parts)
    tone_words = re.findall(r'(?:positive|negative|neutral|mixed|enthusias\w+|frustrat\w+|uncertain\w*|playful|serious|collaborative|tense|relaxed|energetic|subdued)', content_lower)
    unique_tones = set(tone_words)
    scores["tonal_distinction"] = 1.0 if len(unique_tones) >= 4 else (0.5 if len(unique_tones) >= 2 else 0.0)

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

### 評分項 1：分析深度（權重 35%）

**1.0 分**：分析超越表層的情緒標籤。辨識出會議過程中細膩的情緒轉折，解釋為何某些主題更具熱度，並掌握「非正式卻有生產力」的動態。記錄如 Talladega Nights 離題等具體時刻，作為團隊默契的佐證。

**0.75 分**：分析良好，逐主題拆解清楚並具一定細膩度。

**0.5 分**：指派了基本情緒標籤，但說明或洞見有限。

**0.25 分**：分析淺薄，大多只是重述明顯的觀察。

**0.0 分**：未做出有意義的分析。

### 評分項 2：以證據為本的觀察（權重 30%）

**1.0 分**：論點有逐字稿中的具體引言或時刻佐證。在適當之處將情緒歸於特定人物（例如 William 對標語的強烈意見、Samia 對競品的條理化提問）。引言選得好且具說明力。

**0.75 分**：多數論點有證據支持，引言選擇良好。

**0.5 分**：提供部分證據，但許多論點是無佐證的斷言。

**0.25 分**：引言極少或全無，多為臆測。

**0.0 分**：未使用逐字稿中的任何證據。

### 評分項 3：實用價值（權重 35%）

**1.0 分**：分析提供團隊主管可用的可執行洞見——辨識潛在摩擦點、團隊同調之處、誰可能需要更多支援，以及哪些主題能激發團隊。「疑慮」區段點出真正值得處理的問題。

**0.75 分**：大致可執行，能良好辨識動態與疑慮。

**0.5 分**：有一些有用觀察，但多為描述性而非可執行。

**0.25 分**：實用價值有限；讀起來更像讀書報告而非有用的分析。

**0.0 分**：沒有可執行的洞見。
