---
id: task_meeting_executive_summary
name: |
  會議高階主管摘要
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_executive_summary
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T125tw_meeting_executive_summary
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 會議高階主管摘要


## Prompt

我手上有一個檔案 `meeting_transcript.md`，內含 2021-06-28 舉行的 GitLab 產品行銷團隊會議逐字稿。請幫我讀過逐字稿，產出一份精簡的高階主管摘要（executive summary）。

請把摘要寫入名為 `executive_summary.md` 的檔案，內容涵蓋：

- **會議標題與日期**
- **與會者**（逐字稿中提到的姓名）
- **討論的關鍵主題**（3-5 個重點，摘述主要討論面向）
- **做成的決議**（團隊達成的具體決定或結論）
- **行動項目（action items）**（指派給特定人員的任務，可辨識時附上負責人）
- **後續步驟**（下次會議前需要完成的事項）

摘要長度請控制在約 500 字以內，並以一位未出席會議的繁忙高階主管為對象來撰寫。

## Expected Behavior

助手應該：

1. 讀取會議逐字稿
2. 辨識主要討論主題：
   - 企業活動贊助分工（platform 對應 re:Invent、CI/CD 對應 Google Next、GitOps 對應 KubeCon）
   - Commit 大會的產品公告（橫跨各 stage 的前 5 大功能）
   - 競品比較資訊圖（design 團隊的新設計、配色決定）
   - 訊息框架（如「more speed, less risk」與「single source of truth, countless possibilities」等標語）
   - 競品試算表方法論（tier 1 競爭對手、按 stage 對應的比較）
3. 辨識關鍵決議：
   - 活動分工：Platform→re:Invent、CI/CD→Google Next、GitOps→KubeCon
   - 訊息：選定「more speed, less risk」為最終標語
   - 競品資訊圖：維持僅用綠色配色（不用紅色）
   - 以 vulnerability management 作為最重要的安全公告
4. 擷取行動項目（Cormac 負責補上 Plan stage 的前 5 大功能、團隊向 campaign managers 確認等）
5. 撰寫一份結構良好的高階主管摘要

## Grading Criteria

- [ ] 已建立 `executive_summary.md` 檔案
- [ ] 提及會議日期（2021-06-28 或 June 28, 2021）
- [ ] 辨識出至少 3 個關鍵主題
- [ ] 涵蓋企業活動／活動贊助主題
- [ ] 涵蓋產品公告／Commit 大會主題
- [ ] 記載至少 2 項具體決議
- [ ] 包含行動項目或後續步驟區段
- [ ] 摘要精簡（約 800 字以內）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting executive summary task.

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
    report_path = workspace / "executive_summary.md"
    if not report_path.exists():
        alternatives = ["exec_summary.md", "summary.md", "meeting_summary.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "file_created": 0.0,
            "meeting_date": 0.0,
            "topics_identified": 0.0,
            "events_covered": 0.0,
            "announcements_covered": 0.0,
            "decisions_documented": 0.0,
            "action_items_present": 0.0,
            "concise": 0.0,
        }

    scores["file_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check meeting date
    date_patterns = [r'2021-06-28', r'june\s*28', r'6/28/2021', r'28\s*june\s*2021']
    scores["meeting_date"] = 1.0 if any(re.search(p, content_lower) for p in date_patterns) else 0.0

    # Count key topics identified
    topic_count = 0
    if re.search(r'(?:corporate\s*event|event\s*sponsor|re:?\s*invent|kubecon|google\s*next)', content_lower):
        topic_count += 1
    if re.search(r'(?:product\s*announce|commit\s*(?:conference|event)|top\s*(?:5|five)\s*feature)', content_lower):
        topic_count += 1
    if re.search(r'(?:competitive|infographic|comparison)', content_lower):
        topic_count += 1
    if re.search(r'(?:messaging\s*framework|tagline|more\s*speed|single\s*source\s*of\s*truth)', content_lower):
        topic_count += 1
    if re.search(r'(?:vulnerability\s*management|security\s*announce)', content_lower):
        topic_count += 1
    scores["topics_identified"] = 1.0 if topic_count >= 3 else (0.5 if topic_count >= 2 else 0.0)

    # Events coverage
    events_patterns = [
        r're:?\s*invent',
        r'google\s*next',
        r'kubecon',
        r'event\s*(?:sponsor|support|assign)',
    ]
    scores["events_covered"] = 1.0 if sum(1 for p in events_patterns if re.search(p, content_lower)) >= 2 else 0.0

    # Product announcements coverage
    announce_patterns = [
        r'commit',
        r'product\s*announce',
        r'top\s*(?:5|five)',
        r'vulnerability\s*management',
        r'kubernetes\s*agent',
    ]
    scores["announcements_covered"] = 1.0 if sum(1 for p in announce_patterns if re.search(p, content_lower)) >= 2 else 0.0

    # Decisions documented
    decision_count = 0
    if re.search(r'more\s*speed.*less\s*risk', content_lower):
        decision_count += 1
    if re.search(r'(?:green|no\s*red|color)', content_lower):
        decision_count += 1
    if re.search(r'vulnerability\s*management', content_lower):
        decision_count += 1
    if re.search(r'(?:platform.*re:?\s*invent|ci.*cd.*google|gitops.*kubecon)', content_lower):
        decision_count += 1
    scores["decisions_documented"] = 1.0 if decision_count >= 2 else (0.5 if decision_count >= 1 else 0.0)

    # Action items present
    action_patterns = [
        r'action\s*item',
        r'next\s*step',
        r'follow[\s-]*up',
        r'(?:need|should|will|to)\s*(?:do|complete|confirm|add|update|review)',
        r'assign(?:ed|ment)',
        r'(?:cormac|cindy|brian|samia|william).*(?:will|to|should)',
    ]
    scores["action_items_present"] = 1.0 if sum(1 for p in action_patterns if re.search(p, content_lower)) >= 2 else 0.0

    # Conciseness check (under ~800 words)
    word_count = len(content.split())
    scores["concise"] = 1.0 if word_count <= 800 else (0.5 if word_count <= 1200 else 0.0)

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

### 評分項 1：準確性與完整性（權重 40%）

**1.0 分**：摘要準確掌握所有主要討論主題（企業活動、產品公告、競品資訊圖、訊息框架）、關鍵決議與行動項目，且未引入錯誤資訊。

**0.75 分**：多數主題與決議準確掌握，僅有一兩處小遺漏。

**0.5 分**：核心主題俱在，但缺少或誤記了數項重要細節。

**0.25 分**：僅涵蓋少數主題，或存在重大不準確。

**0.0 分**：摘要缺失、空白或根本不準確。

### 評分項 2：高階主管可讀性（權重 30%）

**1.0 分**：摘要精簡，結構良好且分區清楚，用語專業，繁忙的高階主管能在 2 分鐘內掌握重點。沒有從閒聊語氣中混入不必要的細節。

**0.75 分**：摘要可讀且組織良好，僅略嫌冗長。

**0.5 分**：有摘要，但過於瑣碎、組織不佳，或難以快速瀏覽。

**0.25 分**：摘要雜亂，或讀起來更像原始筆記而非主管簡報。

**0.0 分**：沒有摘要，或格式完全無法使用。

### 評分項 3：可執行性（權重 30%）

**1.0 分**：決議陳述清楚，行動項目在可辨識時附有負責人，後續步驟具體到足以執行。讀者能確切知道做了哪些決定、接下來會發生什麼。

**0.75 分**：多數決議與行動項目清楚，僅在負責人或具體性上有少許缺漏。

**0.5 分**：有一些決議或行動項目，但模糊或缺乏脈絡。

**0.25 分**：行動項目大多缺失或過於模糊而無用。

**0.0 分**：未從會議擷取任何可執行內容。
