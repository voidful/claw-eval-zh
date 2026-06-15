---
id: task_meeting_tech_action_items
name: 會議行動項目擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_tech_action_items
source_benchmark: pinchbench
claw_eval_id: P115zh_meeting_tech_action_items
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 會議行動項目擷取

## Prompt

我有一個檔案 `meeting_transcript.md`，內含一場 2021 年 6 月 28 日的 GitLab Product Marketing 週會逐字稿。會議涵蓋多個主題，包括企業活動、GitLab Commit 的產品發布、競爭分析、一份新的資訊圖（infographic）設計，以及一套訊息架構（messaging framework）。

請從這場會議中擷取所有行動項目（action items），並寫入一個名為 `action_items.md` 的檔案。針對每一個行動項目，請包含：

- **負責人（Owner）**（負責的人，具名）
- **行動（Action）**（他們需要做什麼）
- **截止期限（Deadline）**（若有提及）
- **背景脈絡（Context）**（與哪一個討論主題相關）

請依主題領域將行動項目分組。並在最上方附上行動項目總數的彙總計數。

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿
2. 從討論中辨識出所有明確與隱含的行動項目
3. 將每個行動項目與正確的人/負責人關聯
4. 依主題分組

應擷取的關鍵行動項目：

- **企業活動（Corporate Events）**：各 PMM 需向其活動經理（campaign manager）取得對特定活動的承諾（platform→re:Invent、CI/CD→Google Next、GitOps→KubeCon），並在 issue 上留言
- **產品發布（Product Announcements）**：Cormac 需為 Plan stage 補上一份 top five；團隊成員需檢視並挑出整體前 5 名功能；此項截止為 Tuesday
- **競爭分析（Competitive Analysis）**：Samia 需僅就與她負責 stages 相關的 tier one 競爭對手進行比較；團隊需在競爭比較表（competitive sheet）加上一個 GitLab 的項目（line item）
- **訊息架構（Messaging Framework）**：William 需以「more speed less risk」作為選定標語（tagline）來定稿訊息；截止為 end of day
- **一般事項（General）**：團隊應觀看 Talladega Nights（一項詼諧的回家作業）

## Grading Criteria

- [ ] 已建立檔案 action_items.md
- [ ] 至少辨識出 5 個不同的行動項目
- [ ] 行動項目與特定負責人關聯（例如 Cormac、Samia、William、Cindy）
- [ ] 已掌握企業活動的行動項目（取得活動經理的承諾）
- [ ] 已掌握產品發布的行動項目（top 5 功能，截止 Tuesday）
- [ ] 已掌握競爭分析的行動項目（tier one 競爭對手，加上 GitLab 列）
- [ ] 已掌握訊息架構的行動項目（標語定稿，截止 end of day）
- [ ] 行動項目依主題或類別分組
- [ ] 在有提及處記下截止期限（產品發布為 Tuesday，訊息架構為 end of day）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting action items extraction task.

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

    report_path = workspace / "action_items.md"
    if not report_path.exists():
        for alt in ["actions.md", "action-items.md", "meeting_actions.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "min_action_items": 0.0,
            "owners_identified": 0.0,
            "events_actions": 0.0,
            "announcements_actions": 0.0,
            "competitive_actions": 0.0,
            "messaging_actions": 0.0,
            "grouped_by_topic": 0.0,
            "deadlines_noted": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check minimum number of action items (look for bullet points or numbered items)
    action_markers = re.findall(r'(?:^|\n)\s*(?:[-*•]|\d+[.)]) .+', content)
    scores["min_action_items"] = 1.0 if len(action_markers) >= 5 else (0.5 if len(action_markers) >= 3 else 0.0)

    # Check that owners are identified
    owners = ["cormac", "samia", "william", "cindy", "brian", "tai"]
    owner_count = sum(1 for o in owners if o in content_lower)
    scores["owners_identified"] = 1.0 if owner_count >= 3 else (0.5 if owner_count >= 2 else 0.0)

    # Corporate events actions
    events_patterns = [
        r'(?:campaign\s*manager|event|reinvent|google\s*next|kubecon)',
        r'(?:commit|sign\s*up|sponsor)',
    ]
    events_hits = sum(1 for p in events_patterns if re.search(p, content_lower))
    scores["events_actions"] = 1.0 if events_hits >= 2 else (0.5 if events_hits >= 1 else 0.0)

    # Product announcements actions
    announce_patterns = [
        r'(?:top\s*(?:five|5)|product\s*announce|feature)',
        r'(?:plan|cormac)',
    ]
    announce_hits = sum(1 for p in announce_patterns if re.search(p, content_lower))
    scores["announcements_actions"] = 1.0 if announce_hits >= 2 else (0.5 if announce_hits >= 1 else 0.0)

    # Competitive analysis actions
    competitive_patterns = [
        r'(?:tier\s*(?:one|1)|competitor)',
        r'(?:gitlab\s*(?:line|row|column)|add\s*gitlab)',
    ]
    competitive_hits = sum(1 for p in competitive_patterns if re.search(p, content_lower))
    scores["competitive_actions"] = 1.0 if competitive_hits >= 2 else (0.5 if competitive_hits >= 1 else 0.0)

    # Messaging framework actions
    messaging_patterns = [
        r'(?:messag|tagline|framework)',
        r'(?:more\s*speed\s*less\s*risk|finalize)',
    ]
    messaging_hits = sum(1 for p in messaging_patterns if re.search(p, content_lower))
    scores["messaging_actions"] = 1.0 if messaging_hits >= 2 else (0.5 if messaging_hits >= 1 else 0.0)

    # Check grouping by topic (look for headers or clear sections)
    headers = re.findall(r'(?:^|\n)#+\s+.+|(?:^|\n)\*\*.+\*\*', content)
    scores["grouped_by_topic"] = 1.0 if len(headers) >= 3 else (0.5 if len(headers) >= 2 else 0.0)

    # Check deadlines
    deadline_patterns = [r'tuesday', r'end\s*of\s*(?:the\s*)?day', r'due', r'deadline']
    deadline_hits = sum(1 for p in deadline_patterns if re.search(p, content_lower))
    scores["deadlines_noted"] = 1.0 if deadline_hits >= 2 else (0.5 if deadline_hits >= 1 else 0.0)

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

### 評分項 1：行動項目擷取的完整度（權重 35%）

**1.0 分**：辨識出橫跨所有討論主題（活動、發布、競爭、訊息）的所有主要行動項目。明確指派與隱含承諾皆有掌握。
**0.75 分**：掌握多數行動項目，但漏掉一兩個次要的。
**0.5 分**：掌握部分主題的行動項目，但漏掉整個主題領域。
**0.25 分**：僅掌握少數顯而易見的行動項目。
**0.0 分**：未擷取出有意義的行動項目。

### 評分項 2：負責人歸屬準確度（權重 30%）

**1.0 分**：每個行動項目皆正確指出負責人。姓名依對話脈絡準確歸屬。
**0.75 分**：多數負責人正確辨識，僅一兩處小誤植。
**0.5 分**：辨識出部分負責人，但有數處錯誤或缺漏。
**0.25 分**：負責人多半缺漏或歸屬錯誤。
**0.0 分**：完全未嘗試歸屬負責人。

### 評分項 3：組織與結構（權重 20%）

**1.0 分**：行動項目依主題清楚分組、格式一致，並附上彙總計數。易於瀏覽，可直接作為後續追蹤清單。
**0.75 分**：組織良好，僅有少許格式不一致。
**0.5 分**：有部分組織，但項目跨主題混雜或難以追蹤。
**0.25 分**：組織極少，項目未分組逐條列出。
**0.0 分**：毫無結構或組織。

### 評分項 4：背景脈絡與截止期限準確度（權重 15%）

**1.0 分**：在有提及處記下截止期限（發布為 Tuesday，訊息為 end of day）。每個行動項目的背景脈絡準確且有幫助。
**0.75 分**：多數截止期限與背景脈絡有掌握，僅少數遺漏。
**0.5 分**：提供部分背景脈絡，但截止期限缺漏或不準確。
**0.25 分**：背景脈絡極少，無截止期限。
**0.0 分**：無背景脈絡或截止期限資訊。
