---
id: task_meeting_blog_post
name: |
  會議轉部落格文章
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_blog_post
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T128tw_meeting_blog_post
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.4
  llm_judge: 0.6
---

# 會議轉部落格文章


## Prompt

我手上有一個檔案 `meeting_transcript.md`，內含 2021-06-28 舉行的 GitLab 產品行銷團隊會議逐字稿。團隊討論了他們如何處理產品公告、競品定位與訊息傳達。

請以這場會議作為素材，撰寫一篇部落格文章，談產品行銷團隊在公司採增量出貨（持續交付／開源模式）而非大爆炸式發布（big-bang releases）時，如何有效溝通產品上市。

請以英文撰寫這篇部落格文章，並寫入名為 `blog_post.md` 的檔案。要求：

- **標題（Title）**：取一個吸引人的標題
- **長度**：600-1000 字
- **讀者對象**：產品行銷專業人士與 DevOps 實務工作者
- **切入角度**：援引會議中關於「當路線圖公開、功能以 MVC／迭代方式出貨時，要如何做公告」這個挑戰的討論，提出洞見
- **必含**：至少 2-3 個其他團隊可套用的具體策略或經驗
- **語氣**：資訊性且務實，而非會議回顧

這篇請讀起來像一篇可獨立成篇的部落格文章，而非會議摘要。請把會議內容當作靈感與素材，但撰寫原創內容。

## Expected Behavior

助手應該：

1. 讀取會議逐字稿
2. 辨識關鍵洞見：GitLab 採持續出貨且路線圖公開，使得傳統的「上市」公告變得困難
3. 擷取討論到的策略：
   - 把小型 MVC 打包成較大的敘事主題（例如「vulnerability management」涵蓋許多小型發布）
   - 回顧過去一年，找出哪些功能現在已達「GA-ready」，即使個別零件較早就已出貨
   - 用興奮程度／堆疊排序（stack ranking）來決定優先突出哪些
   - 建立敘事桶（narrative buckets，如 UX 改善、GitOps 能力、安全），把多個功能打包在一起
   - 把公告時機安排在活動（Commit 大會）前後，以爭取媒體關注
   - 以正面框架陳述改善（用「新能力」而非「我們修好了壞掉的東西」）
4. 撰寫一篇將上述歸納為可執行建議的部落格文章（以英文撰寫）
5. 維持適合行銷／DevOps 讀者的專業、資訊性語氣

## Grading Criteria

- [ ] 已建立 `blog_post.md` 檔案
- [ ] 有吸引人的標題（非「Meeting Summary」之類）
- [ ] 切中持續交付模式下做公告的核心挑戰
- [ ] 包含至少 2 個具體策略或建議
- [ ] 讀起來像可獨立成篇的部落格文章（而非會議回顧）
- [ ] 長度適當（400-1200 字）
- [ ] 針對目標讀者撰寫（產品行銷／DevOps）
- [ ] 語氣專業且具資訊性

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting-to-blog-post task.

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

    # Check if file exists
    report_path = workspace / "blog_post.md"
    if not report_path.exists():
        alternatives = ["blog.md", "post.md", "article.md", "blogpost.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "file_created": 0.0,
            "has_title": 0.0,
            "core_challenge": 0.0,
            "strategies_present": 0.0,
            "standalone_post": 0.0,
            "appropriate_length": 0.0,
            "target_audience": 0.0,
            "professional_tone": 0.0,
        }

    scores["file_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()
    word_count = len(content.split())

    # Has a title (first heading)
    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).lower()
        # Title shouldn't be generic "meeting summary" type
        is_meeting_recap = bool(re.search(r'(?:meeting\s*(?:summary|recap|notes|minutes))', title))
        scores["has_title"] = 0.0 if is_meeting_recap else 1.0
    else:
        scores["has_title"] = 0.0

    # Core challenge addressed (continuous delivery + announcements)
    challenge_patterns = [
        r'(?:continuous|incremental|iterati).*(?:deliver|ship|release|deploy)',
        r'(?:ship|release|deploy).*(?:continuous|incremental|small|iterati)',
        r'(?:public\s*roadmap|open\s*source).*(?:announce|launch|market)',
        r'(?:mvc|minimum\s*viable)',
        r'(?:big[\s-]*bang|traditional).*(?:launch|release|announce)',
        r'(?:announce|launch|market).*(?:difficult|challenge|tough|hard).*(?:continuous|incremental|open)',
    ]
    scores["core_challenge"] = 1.0 if sum(1 for p in challenge_patterns if re.search(p, content_lower)) >= 2 else (
        0.5 if any(re.search(p, content_lower) for p in challenge_patterns) else 0.0)

    # Strategies present (at least 2 concrete recommendations)
    strategy_count = 0
    if re.search(r'(?:bundl|group|aggregat|roll[\s-]*up|bucket)', content_lower):
        strategy_count += 1
    if re.search(r'(?:look\s*back|retrospect|year\s*in\s*review|maturity|ga[\s-]*ready)', content_lower):
        strategy_count += 1
    if re.search(r'(?:prioriti|rank|stack[\s-]*rank|excitement|top\s*(?:5|five))', content_lower):
        strategy_count += 1
    if re.search(r'(?:narrative|theme|story|bucket|categor)', content_lower):
        strategy_count += 1
    if re.search(r'(?:event|conference|keynote|commit).*(?:timing|press|announce)', content_lower):
        strategy_count += 1
    if re.search(r'(?:frame|position|spin|messag).*(?:positive|improvement|capabilit)', content_lower):
        strategy_count += 1
    scores["strategies_present"] = 1.0 if strategy_count >= 3 else (0.5 if strategy_count >= 2 else 0.0)

    # Standalone post (should NOT read like a meeting recap)
    recap_signals = [
        r'in\s*the\s*meeting',
        r'(?:attendees|participants)\s*(?:discussed|talked)',
        r'the\s*team\s*(?:then|next)\s*(?:discussed|moved)',
        r'meeting\s*(?:minutes|notes|recap|summary)',
    ]
    recap_count = sum(1 for p in recap_signals if re.search(p, content_lower))
    scores["standalone_post"] = 1.0 if recap_count == 0 else (0.5 if recap_count <= 1 else 0.0)

    # Appropriate length (600-1000 target, 400-1200 acceptable)
    if 600 <= word_count <= 1000:
        scores["appropriate_length"] = 1.0
    elif 400 <= word_count <= 1200:
        scores["appropriate_length"] = 0.5
    else:
        scores["appropriate_length"] = 0.0

    # Target audience (product marketing / DevOps terms)
    audience_terms = [
        r'product\s*market', r'devops', r'(?:launch|release)\s*(?:strategy|plan)',
        r'go[\s-]*to[\s-]*market', r'press', r'pr\s*team',
        r'(?:ci|cd|ci/cd)', r'devsecops', r'(?:feature|product)\s*launch',
    ]
    audience_score = sum(1 for p in audience_terms if re.search(p, content_lower))
    scores["target_audience"] = 1.0 if audience_score >= 3 else (0.5 if audience_score >= 1 else 0.0)

    # Professional tone (no casual meeting language)
    casual_signals = [r'um\b', r'uh\b', r'like\s+you\s+know', r'et\s+cetera', r'yada']
    casual_count = sum(1 for p in casual_signals if re.search(p, content_lower))
    has_structure = len(re.findall(r'^#{1,3}\s+', content, re.MULTILINE)) >= 2
    scores["professional_tone"] = 1.0 if (casual_count == 0 and has_structure) else (
        0.5 if casual_count <= 1 else 0.0)

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

### 評分項 1：內容品質與洞見（權重 40%）

**1.0 分**：部落格文章從會議中萃取出真正有用的洞見，並以可執行建議的形式呈現。策略具體（把 MVC 打包成主題、運用成熟度里程碑、活動驅動的時機），並輔以推理。產品行銷專業人士會學到有用的東西。

**0.75 分**：洞見良好且建議扎實，僅在深度或具體性上有少許缺漏。

**0.5 分**：有一些有用內容，但大多停留在表層，或為未紮根於素材的通用行銷建議。

**0.25 分**：洞見薄弱，大多是空泛的老生常談。

**0.0 分**：沒有有意義的內容，或只是會議回顧。

### 評分項 2：寫作品質（權重 35%）

**1.0 分**：以英文撰寫，讀起來像出自行銷刊物的成熟部落格文章。有吸睛的開頭、合乎邏輯的脈絡、清楚的結構與有力的結論。運用具體例子但不淪為會議逐字稿。適合目標讀者且不堆砌術語。

**0.75 分**：寫得好，結構良好，僅有少許粗糙之處。

**0.5 分**：可讀但像草稿——結構或脈絡仍需打磨。

**0.25 分**：寫作不佳、難以追隨，語氣不恰當，或未以英文撰寫。

**0.0 分**：無法辨識為一篇部落格文章。

### 評分項 3：原創性與轉化（權重 25%）

**1.0 分**：成功把內部會議討論轉化為普遍適用的內容。會議是素材，而非主題。讀者不會知道這出自某次特定的會議逐字稿。加入了讓建議廣泛相關的脈絡與框架。

**0.75 分**：大致原創且歸納良好，偶有可再修飾的會議專屬指涉。

**0.5 分**：部分轉化，但仍略讀起來像會議回顧，或過於 GitLab 專屬。

**0.25 分**：幾乎未轉化——大多在描述會議中發生的事。

**0.0 分**：只是貼了「部落格文章」標籤的會議摘要。
