---
id: task_meeting_follow_up_email
name: |
  會議後續追蹤郵件
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_follow_up_email
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T127tw_meeting_follow_up_email
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 會議後續追蹤郵件


## Prompt

我手上有一個檔案 `meeting_transcript.md`，內含 2021-06-28 舉行的 GitLab 產品行銷團隊會議逐字稿。請幫我草擬一封專業的後續追蹤郵件，可在會後寄給團隊。

請以英文撰寫這封郵件，並寫入名為 `follow_up_email.md` 的檔案。郵件請包含：

- **主旨（Subject line）**
- **稱呼語**：向產品行銷團隊致意
- **簡短回顧**：摘述討論內容（最多 2-3 句）
- **做成的決議**：清楚的編號清單
- **行動項目**：可辨識時附上負責人與期限
- **待解項目（Open items）**：仍需解決的事項
- **結尾**：附上任何相關的下次會議資訊或期限

郵件請保持專業，同時貼合團隊合作的語氣，並力求精簡——讓繁忙的團隊成員能在一分鐘內掃完。

## Expected Behavior

助手應該：

1. 讀取會議逐字稿
2. 草擬一封郵件，掌握：
   - **決議：**
     - 活動分工：Platform→re:Invent、CI/CD→Google Next、GitOps→KubeCon
     - 訊息標語：選定「more speed, less risk」
     - 競品資訊圖：維持僅用綠色的配色方案
     - 最重要公告選擇：以 vulnerability management 作為安全領域的主打故事
     - 集會（assembly）標語：「single source of truth, countless possibilities」
   - **行動項目：**
     - 全體：向 campaign managers 確認活動承諾、在 issue 上留言
     - Cormac：補上 Plan stage 的前 5 大功能
     - 團隊：完成產品公告試算表的填寫（週二 Tuesday 截止）
     - Samia：調整競品表，使每個 stage 只採用相關的 tier 1 競爭對手
     - 在競品比較中把 GitLab 也列為一個項目
   - **待解項目：**
     - 跨所有 stage 的最終前 5 大產品公告
     - 是否將 UX 改善打包成一個突出類別
     - 究竟要納入哪些 VS Code 整合功能
3. 撰寫一封清楚、易於瀏覽的郵件（以英文撰寫）

## Grading Criteria

- [ ] 已建立 `follow_up_email.md` 檔案
- [ ] 有主旨行
- [ ] 包含決議或關鍵結論區段
- [ ] 列出至少 3 項具體決議
- [ ] 包含行動項目且至少有部分負責人姓名
- [ ] 列出至少 3 項行動項目
- [ ] 提及週二（Tuesday）的期限
- [ ] 語氣專業但平易近人
- [ ] 精簡（約 600 字以內）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting follow-up email task.

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
    report_path = workspace / "follow_up_email.md"
    if not report_path.exists():
        alternatives = ["followup_email.md", "follow_up.md", "email.md", "meeting_followup.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "file_created": 0.0,
            "has_subject": 0.0,
            "decisions_section": 0.0,
            "decisions_count": 0.0,
            "action_items_with_owners": 0.0,
            "action_items_count": 0.0,
            "deadline_mentioned": 0.0,
            "tone_appropriate": 0.0,
            "concise": 0.0,
        }

    scores["file_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Subject line
    subject_patterns = [r'subject\s*:', r're\s*:', r'^#\s*.*(?:follow|recap|summary)', r'\*\*subject\*\*']
    scores["has_subject"] = 1.0 if any(re.search(p, content_lower, re.MULTILINE) for p in subject_patterns) else 0.0

    # Decisions section
    decision_section_patterns = [r'decision', r'key\s*outcome', r'(?:what\s*we\s*)?(?:agreed|decided)', r'outcome', r'conclusion']
    scores["decisions_section"] = 1.0 if any(re.search(p, content_lower) for p in decision_section_patterns) else 0.0

    # Count specific decisions
    decision_count = 0
    if re.search(r'(?:platform|re:?\s*invent)', content_lower):
        decision_count += 1
    if re.search(r'(?:ci.*cd|google\s*next)', content_lower):
        decision_count += 1
    if re.search(r'(?:gitops|kubecon)', content_lower):
        decision_count += 1
    if re.search(r'more\s*speed.*less\s*risk', content_lower):
        decision_count += 1
    if re.search(r'(?:green|no\s*red|color\s*scheme)', content_lower):
        decision_count += 1
    if re.search(r'vulnerability\s*management', content_lower):
        decision_count += 1
    scores["decisions_count"] = 1.0 if decision_count >= 3 else (0.5 if decision_count >= 2 else 0.0)

    # Action items with owners (names from the meeting)
    names = ['cormac', 'cindy', 'brian', 'samia', 'william', 'tai']
    names_found = sum(1 for n in names if n in content_lower)
    action_patterns = [r'action\s*item', r'to[\s-]*do', r'(?:will|should|needs?\s*to|please)\s+\w+']
    has_actions = any(re.search(p, content_lower) for p in action_patterns)
    scores["action_items_with_owners"] = 1.0 if (names_found >= 2 and has_actions) else (0.5 if names_found >= 1 or has_actions else 0.0)

    # Count action items (look for list items in action section)
    action_list_items = re.findall(r'(?:^|\n)\s*[-*•\d]+[.)]\s*.{10,}', content)
    scores["action_items_count"] = 1.0 if len(action_list_items) >= 5 else (0.5 if len(action_list_items) >= 3 else 0.0)

    # Tuesday deadline mentioned
    deadline_patterns = [r'tuesday', r'due\s*(?:date|by|end\s*of)', r'deadline', r'end\s*of\s*(?:the\s*)?day']
    scores["deadline_mentioned"] = 1.0 if any(re.search(p, content_lower) for p in deadline_patterns) else 0.0

    # Tone (professional but approachable - look for greeting and closing)
    has_greeting = bool(re.search(r'(?:hi|hey|hello|dear|team|everyone|all)', content_lower[:200]))
    has_closing = bool(re.search(r'(?:thanks|thank\s*you|best|regards|cheers|talk\s*soon)', content_lower[-300:]))
    scores["tone_appropriate"] = 1.0 if (has_greeting and has_closing) else (0.5 if (has_greeting or has_closing) else 0.0)

    # Conciseness
    word_count = len(content.split())
    scores["concise"] = 1.0 if word_count <= 600 else (0.5 if word_count <= 900 else 0.0)

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

### 評分項 1：內容準確性（權重 35%）

**1.0 分**：郵件準確掌握會議中的決議、行動項目與待解問題。沒有捏造的承諾或錯誤歸屬。活動分工、標語選擇與競品做法都正確呈現。

**0.75 分**：多數內容準確，僅有一兩處小錯或遺漏。

**0.5 分**：核心決議俱在，但數項內容不準確，或缺少關鍵項目。

**0.25 分**：明顯的不準確或重大遺漏，損及實用性。

**0.0 分**：郵件缺失、空白或根本不準確。

### 評分項 2：郵件格式與專業度（權重 30%）

**1.0 分**：讀起來像 PMM 主管會發出的真正後續郵件。有適當主旨、稱呼語、結構化且易掃描的內文區段（決議、行動項目、待解項目）以及專業結尾。內容以英文撰寫，貼合團隊「合作但直接」的語氣。

**0.75 分**：郵件格式良好，僅有少許結構問題。

**0.5 分**：包含正確資訊，但讀起來不像自然的郵件。

**0.25 分**：格式不佳，語氣過於正式／過於隨意，或未以英文撰寫。

**0.0 分**：無法辨識為一封郵件。

### 評分項 3：可執行性與清晰度（權重 35%）

**1.0 分**：收到此郵件的團隊成員能確切知道做了哪些決定、自己個人該做什麼、何時到期。行動項目具體且有歸屬。後續步驟毫無歧義。

**0.75 分**：大致清楚且可執行，僅有少許歧義。

**0.5 分**：有一些行動項目，但缺乏具體性或明確歸屬。

**0.25 分**：對接下來該做什麼模糊或不清楚。

**0.0 分**：沒有可執行內容。
