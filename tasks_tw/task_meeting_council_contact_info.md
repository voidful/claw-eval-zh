---
id: task_meeting_council_contact_info
name: |
  市議會逐字稿 — 擷取聯絡資訊
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_contact_info
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T113tw_meeting_council_contact_info
workspace_files:
- source: meetings/2026-04-02-tampa-city-council-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 市議會逐字稿 — 擷取聯絡資訊


## Prompt

我手邊有一份 2026 年 4 月 2 日舉行的 Tampa City Council 會議逐字稿，存放在 `transcript.md`。請幫我產生 `contacts_report.md`，列出所有具名提及的人物，並附上職稱/角色、所屬組織與背景脈絡。整理時請分類為：**Council Members**、**City Staff**、**Presenters and Experts**、**Community Members / Public Speakers**、**Other People Mentioned**。

## Expected Behavior

60 位以上的具名人物，包含 7 位議會議員、市府職員（Shelby、Perry、Baird、Johns、Brody、DeManche、Kopesky）、簡報者（Hamilton/Raftelis、Guyette/Colliers、Chief Bercaw、晉升的 TPD 人員：DeFelice、Messmer、Purcell、McCormick）、16 位以上的公眾發言者，以及其他人（Officer McNeil、Milo/Related Urban、社區致贈禮物者）。

## Grading Criteria

- [ ] 已建立報告檔案 contacts_report.md
- [ ] 已列出全部 7 位議會議員
- [ ] Shelby 列為 Council Attorney
- [ ] Hamilton 列為 Raftelis 顧問
- [ ] Bercaw 列為 Police Chief
- [ ] McNeil 列為 Officer of the Month
- [ ] 已辨識 12 位以上公眾發言者
- [ ] TPD 晉升人員（DeFelice、Messmer、Purcell、McCormick）
- [ ] 已分類整理為各區段
- [ ] Milo 列為 Related Urban president

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    scores = {}
    workspace = Path(workspace_path)
    report_path = workspace / "contacts_report.md"
    if not report_path.exists():
        for alt in ["contacts.md", "people.md", "directory.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in ["report_created", "council_members", "shelby_attorney", "hamilton_raftelis", "bercaw_chief", "mcneil_officer", "public_speakers", "tpd_promotions", "organized_sections", "milo_related"]}
    scores["report_created"] = 1.0
    content = report_path.read_text()
    cl = content.lower()
    council = ['clendenin', 'miranda', 'maniscalco', 'hurtak', 'young', 'viera', 'carlson']
    scores["council_members"] = 1.0 if sum(1 for c in council if c in cl) == 7 else 0.5
    scores["shelby_attorney"] = 1.0 if (re.search(r'shelby', cl) and re.search(r'(?:attorney|legal|counsel)', cl)) else 0.0
    scores["hamilton_raftelis"] = 1.0 if (re.search(r'(?:murray|hamilton)', cl) and re.search(r'raftelis', cl)) else 0.0
    scores["bercaw_chief"] = 1.0 if (re.search(r'bercaw', cl) and re.search(r'(?:chief|police|tpd)', cl)) else 0.0
    scores["mcneil_officer"] = 1.0 if (re.search(r'mcneil', cl) and re.search(r'(?:officer.*month|award|honor)', cl)) else 0.0
    speakers = [r'jeraldine', r'iman', r'hych', r'cannella', r'cornell', r'citro', r'morrow', r'bennett', r'poole', r'michelini', r'adair', r'lockett', r'bullock', r'poynor', r'randolph', r'rodriguez']
    scores["public_speakers"] = 1.0 if sum(1 for s in speakers if re.search(s, cl)) >= 12 else 0.5
    promoted = ['defelice', 'messmer', 'purcell', 'mccormick']
    scores["tpd_promotions"] = 1.0 if sum(1 for p in promoted if p in cl) >= 3 else 0.5
    section_patterns = [r'council\s*member', r'(?:city\s*)?staff', r'(?:public|community|speaker)', r'(?:presenter|expert|consult)']
    scores["organized_sections"] = 1.0 if sum(1 for s in section_patterns if re.search(s, cl)) >= 3 else 0.5
    scores["milo_related"] = 1.0 if (re.search(r'milo', cl) and re.search(r'related\s*urban', cl)) else 0.0
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

### 評分項 1：人物辨識（權重 35%）
**1.0 分**：40 位以上人物。**0.75 分**：30-39 位。**0.5 分**：20-29 位。**0.0 分**：少於 10 位。

### 評分項 2：角色準確度（權重 30%）
**1.0 分**：職稱/隸屬正確。**0.5 分**：部分缺漏。**0.0 分**：錯誤。

### 評分項 3：分類（權重 20%）
**1.0 分**：區段清楚。**0.5 分**：部分。**0.0 分**：完全沒有。

### 評分項 4：背景脈絡（權重 15%）
**1.0 分**：每位人物皆有簡要背景脈絡。**0.5 分**：部分。**0.0 分**：完全沒有。
