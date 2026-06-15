---
id: task_meeting_advisory_attendees
name: |
  NTIA Advisory Board 與會者名單
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_advisory_attendees
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T120tw_meeting_advisory_attendees
workspace_files:
- source: meetings/2012-05-30-meeting-transcript-ntia-csmac.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# NTIA Advisory Board 與會者名單


## Prompt

我手邊有一份政府諮詢委員會會議的逐字稿，存放在 `meeting-transcript.md`。這是 Commerce Spectrum Management Advisory Committee（CSMAC）於 2012 年 5 月 30 日舉行的會議。

請幫我分析這份逐字稿，並在一個名為 `attendees.md` 的檔案中建立一份結構化的與會者名單。針對每位與會者，請包含：

- **全名**（若有提及頭銜，如 Dr.、Esq.，請一併附上）
- **會議中的角色**（Chair、Member、Also Present、Public Participant）
- **所屬組織與職稱**（依逐字稿所述）
- **與會方式**（In-person 或 Phone/Remote）
- **發言角色**（是否做了實質發言、提問，或僅報出自己的身分）

請將名單整理為以下區段：Committee Leadership、Committee Members (In-Person)、Committee Members (Remote)、Non-Member Officials、Public Participants。最後附上與會者總數的彙總計數。

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿
2. 從「Members Present」名單、「Also Present」區段與對話中辨識出所有具名人物
3. 從星號標記（電話）與點名（roll call）判定與會方式
4. 將每位人物的角色與參與程度分類
5. 產出一份結構良好的 markdown 文件

預期的關鍵與會者：

- Dr. Brian Fontes（Chair，NENA）— In-person
- Larry Strickling（Asst. Secretary of Commerce）— In-person，Also Present
- Karl Nebbia（Associate Administrator，Office of Spectrum Management）— In-person，Also Present
- Tom Power（White House OSTP）— In-person，Also Present
- Bruce M. Washington（Designated Federal Officer）— In-person，Also Present
- Dale Hatfield（University of Colorado）— Remote（phone）
- Molly Feldman（Verizon Wireless）— Remote（phone）
- Doug McGinnis（Exelon）— Remote（phone）
- Dan Stancil（NC State）— Remote（phone）
- Rick Reaser（Raytheon）— Remote（phone）
- David Donovan — Remote（phone）
- Mr. Snider — Public participant（於公眾意見時段發言）
- 委員會成員總數：約 19-20 人
- 含官員與公眾的與會者總數：約 23-24 人

## Grading Criteria

- [ ] 已建立檔案 attendees.md
- [ ] Brian Fontes 正確辨識為 Chair 並具 NENA 隸屬
- [ ] 至少具名辨識出 15 位委員會成員
- [ ] 正確辨識遠端/電話與會者（Hatfield、Feldman、McGinnis、Stancil、Reaser、Donovan）
- [ ] 已列出非成員官員（Strickling、Nebbia、Power、Washington）
- [ ] 多數與會者皆含所屬組織/隸屬
- [ ] 正確記下與會方式（in-person 對比 phone）
- [ ] Mr. Snider 辨識為公眾參與者
- [ ] 已包含與會者彙總計數

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting attendee list task.

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

    report_path = workspace / "attendees.md"
    if not report_path.exists():
        alternatives = ["attendee_list.md", "attendees_list.md", "meeting_attendees.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "chair_identified": 0.0,
            "member_count": 0.0,
            "remote_attendees": 0.0,
            "officials_listed": 0.0,
            "organizations_included": 0.0,
            "attendance_mode": 0.0,
            "public_participant": 0.0,
            "summary_count": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check Chair identification
    chair_ok = (
        "fontes" in content_lower
        and ("chair" in content_lower)
        and re.search(r'nena|national emergency number', content_lower) is not None
    )
    scores["chair_identified"] = 1.0 if chair_ok else 0.0

    # Check member count (at least 15 of ~19 committee members named)
    members = [
        "fontes", "borth", "calabrese", "dombrowsky", "donovan",
        "feldman", "furchtgott", "gibson", "hatfield", "kahn",
        "mcginnis", "mchenry", "obuchowski", "povelites", "reaser",
        "rush", "stancil", "tramont", "warren"
    ]
    found = sum(1 for m in members if m in content_lower)
    scores["member_count"] = 1.0 if found >= 15 else (0.5 if found >= 10 else 0.0)

    # Check remote/phone attendees identified
    remote_members = ["hatfield", "feldman", "mcginnis", "stancil", "reaser", "donovan"]
    remote_found = 0
    for rm in remote_members:
        # Check if the member is mentioned near phone/remote/telephone keywords
        if rm in content_lower:
            # Look for phone/remote indicators near the name
            patterns = [
                rf'{rm}.*(?:phone|remote|virtual|telephone|dial)',
                rf'(?:phone|remote|virtual|telephone|dial).*{rm}',
            ]
            if any(re.search(p, content_lower) for p in patterns):
                remote_found += 1
            elif re.search(r'\*', content):
                # Asterisk convention mentioned
                remote_found += 0.5
    scores["remote_attendees"] = 1.0 if remote_found >= 4 else (0.5 if remote_found >= 2 else 0.0)

    # Check non-member officials
    officials = ["strickling", "nebbia", "power", "washington"]
    officials_found = sum(1 for o in officials if o in content_lower)
    scores["officials_listed"] = 1.0 if officials_found >= 3 else (0.5 if officials_found >= 2 else 0.0)

    # Check organizations included
    orgs = [
        "nena", "national emergency number",
        "verizon", "at&t", "att", "intel",
        "lockheed", "raytheon", "comsearch",
        "new america", "wiley rein", "wilkinson barker",
        "shared spectrum", "exelon", "ntia",
        "furchtgott-roth", "nc state", "north carolina",
        "colorado", "freedom technologies"
    ]
    org_found = sum(1 for o in orgs if o in content_lower)
    scores["organizations_included"] = 1.0 if org_found >= 10 else (0.5 if org_found >= 5 else 0.0)

    # Check attendance mode notation
    mode_patterns = [
        r'in[- ]person', r'on[- ]?site', r'physical',
        r'phone', r'remote', r'virtual', r'telephone', r'dial'
    ]
    mode_found = sum(1 for p in mode_patterns if re.search(p, content_lower))
    scores["attendance_mode"] = 1.0 if mode_found >= 2 else (0.5 if mode_found >= 1 else 0.0)

    # Check public participant (Snider)
    scores["public_participant"] = 1.0 if "snider" in content_lower else 0.0

    # Check summary count
    count_patterns = [
        r'total.*\d+', r'\d+.*total',
        r'(?:attendee|participant|member)s?.*\d+',
        r'\d+.*(?:attendee|participant|member)',
        r'count.*\d+', r'summary.*\d+'
    ]
    scores["summary_count"] = 1.0 if any(re.search(p, content_lower) for p in count_patterns) else 0.0

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

### 評分項 1：與會者辨識完整度（權重 35%）

**1.0 分**：所有委員會成員、官員與公眾參與者皆以正確姓名與角色辨識。無一遺漏。
**0.75 分**：辨識出多數與會者（18 位以上），僅有少許遺漏。
**0.5 分**：辨識出多數，但有數位與會者缺漏。
**0.25 分**：僅辨識出最突出的發言者。
**0.0 分**：辨識出的與會者不到一半。

### 評分項 2：細節準確度（權重 30%）

**1.0 分**：所有組織、職稱與與會方式皆正確。Remote 對比 in-person 的狀態與逐字稿的星號標記及點名相符。
**0.75 分**：多數細節正確，僅一兩處小誤。
**0.5 分**：組織或與會方式有數處錯誤。
**0.25 分**：隸屬或角色有許多不準確之處。
**0.0 分**：細節大致錯誤或為杜撰。

### 評分項 3：組織與結構（權重 20%）

**1.0 分**：清楚分區，分開 leadership、in-person 成員、remote 成員、官員與公眾。易於瀏覽與查閱。
**0.75 分**：組織良好，僅有少許結構問題。
**0.5 分**：有部分組織，但區段不清楚或不一致。
**0.25 分**：組織不佳，難以查找。
**0.0 分**：無有意義的結構。

### 評分項 4：發言角色評估（權重 15%）

**1.0 分**：準確區分積極參與者（提問、做出發言）與僅在點名時報出身分者。
**0.75 分**：多數發言角色正確記下。
**0.5 分**：嘗試記下參與程度但不完整。
**0.25 分**：區分參與程度的努力極少。
**0.0 分**：未評估發言角色。
