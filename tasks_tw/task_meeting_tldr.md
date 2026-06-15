---
id: task_meeting_tldr
name: |
  會議 TL;DR 速覽
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_tldr
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T129tw_meeting_tldr
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 會議 TL;DR 速覽


## Prompt

我手上有一個檔案 `meeting_transcript.md`，內含 GitLab 產品行銷團隊會議的逐字稿。我錯過了這場會議，需要快速跟上進度。

請幫我把一份 TL;DR 寫入名為 `meeting_tldr.md` 的檔案。它應該**極度精簡**——就像你會貼在 Slack 上給沒參加通話的同事看的那種摘要。要求：

- **最多 150 字**（硬性上限）
- 最上方有一句**一行總結**（用一句話說明這場會議在談什麼）
- **3-5 個重點**，涵蓋最重要的結論
- 提及任何**期限**

不要廢話、不要前言、不要「In this meeting, the team discussed...」之類——只要必要的事實。

## Expected Behavior

助手應該：

1. 讀取逐字稿
2. 把整場會議濃縮到約 150 字以內
3. 產出類似這樣的內容：

   **每週 PMM sync——活動分工、Commit 公告、訊息傳達。**

   - 活動歸屬確定：Platform→re:Invent、CI/CD→Google Next、GitOps→KubeCon。請向你的 campaign managers 確認並在 issue 上留言。
   - Commit 需要前 5 大產品公告。Vulnerability management 是安全領域的首選。團隊正在票選最終名單。
   - 訊息標語定案：「more speed, less risk」。公司層級：「single source of truth, countless possibilities」。
   - 競品資訊圖改為僅用綠色（不用紅色）——design 團隊的建議。
   - 競品表：只採用與你 stage 相關的 tier 1 競爭對手。把 GitLab 也列為一個項目。

   **⏰ 產品公告試算表週二（Tuesday）截止。**

## Grading Criteria

- [ ] 已建立 `meeting_tldr.md` 檔案
- [ ] 最上方有一句一行總結
- [ ] 包含 3-5 個重點
- [ ] 提及活動分工（re:Invent、Google Next 或 KubeCon）
- [ ] 提及訊息決議（「more speed, less risk」）
- [ ] 提及期限（週二 Tuesday）
- [ ] 總字數在 200 字以內
- [ ] 沒有不必要的填充或前言

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting TL;DR task.

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
    report_path = workspace / "meeting_tldr.md"
    if not report_path.exists():
        alternatives = ["tldr.md", "tl_dr.md", "meeting_tl_dr.md", "summary.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "file_created": 0.0,
            "one_line_summary": 0.0,
            "bullet_points": 0.0,
            "events_mentioned": 0.0,
            "messaging_decision": 0.0,
            "deadline_mentioned": 0.0,
            "word_count_ok": 0.0,
            "no_filler": 0.0,
        }

    scores["file_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()
    word_count = len(content.split())

    # One-line summary at top (first non-empty, non-heading line or first heading)
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    if lines:
        first_content = lines[0] if not lines[0].startswith('#') else (lines[1] if len(lines) > 1 else lines[0])
        # Should be a short summary line (under 30 words)
        first_words = len(first_content.split())
        scores["one_line_summary"] = 1.0 if first_words <= 30 else 0.5
    else:
        scores["one_line_summary"] = 0.0

    # Bullet points (3-5)
    bullets = re.findall(r'(?:^|\n)\s*[-*•]\s+.+', content)
    if 3 <= len(bullets) <= 7:
        scores["bullet_points"] = 1.0
    elif 2 <= len(bullets) <= 9:
        scores["bullet_points"] = 0.5
    else:
        scores["bullet_points"] = 0.0

    # Event assignments mentioned
    event_patterns = [r're:?\s*invent', r'google\s*next', r'kubecon']
    events_found = sum(1 for p in event_patterns if re.search(p, content_lower))
    scores["events_mentioned"] = 1.0 if events_found >= 2 else (0.5 if events_found >= 1 else 0.0)

    # Messaging decision
    scores["messaging_decision"] = 1.0 if re.search(r'more\s*speed.*less\s*risk', content_lower) else 0.0

    # Deadline mentioned
    scores["deadline_mentioned"] = 1.0 if re.search(r'tuesday|deadline|due', content_lower) else 0.0

    # Word count (target: ≤150, acceptable: ≤200)
    if word_count <= 150:
        scores["word_count_ok"] = 1.0
    elif word_count <= 200:
        scores["word_count_ok"] = 0.5
    else:
        scores["word_count_ok"] = 0.0

    # No filler/preamble
    filler_patterns = [
        r'in\s*this\s*meeting',
        r'the\s*team\s*(?:discussed|met|gathered)',
        r'this\s*(?:document|summary)\s*(?:provides|contains|covers)',
        r'here\s*(?:is|are)\s*(?:the|a)\s*(?:summary|overview)',
        r'below\s*(?:is|are)',
    ]
    filler_count = sum(1 for p in filler_patterns if re.search(p, content_lower))
    scores["no_filler"] = 1.0 if filler_count == 0 else (0.5 if filler_count == 1 else 0.0)

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

### 評分項 1：資訊密度（權重 40%）

**1.0 分**：每一句都承載必要資訊。掌握了會議最重要的 5 項結論。沒有贅字。同事讀完即能掌握所有需要知道的事。

**0.75 分**：掌握多數重要結論，僅有少許遺漏或略嫌冗長。

**0.5 分**：關鍵結論俱在，但漏掉部分重要項目，或塞入不必要的脈絡。

**0.25 分**：漏掉主要結論，或對 TL;DR 而言過於囉嗦。

**0.0 分**：作為快速摘要沒有用處。

### 評分項 2：精簡度（權重 35%）

**1.0 分**：150 字以內。讀起來像一則 Slack 訊息——有力、直接、不拖泥帶水。適當使用簡寫（用 → 表示分工、對熟知術語用縮寫）。

**0.75 分**：200 字以內，大致精簡，仍有可刪減之處。

**0.5 分**：200-300 字，內容合理，但稱不上真正的 TL;DR。

**0.25 分**：超過 300 字——這是摘要，不是 TL;DR。

**0.0 分**：超過 500 字，或完全未達精簡要求。

### 評分項 3：可掃描性（權重 25%）

**1.0 分**：能在 30 秒內完全吸收。視覺結構清楚（重點符號、用粗體強調、期限被標示出來）。最上方的一行總結立即讓讀者定位。

**0.75 分**：結構良好，大致可掃描，仍有少許可改進。

**0.5 分**：包含資訊，但需要仔細閱讀才能擷取重點。

**0.25 分**：一大片文字或結構不佳。

**0.0 分**：沒有結構或內容缺失。
