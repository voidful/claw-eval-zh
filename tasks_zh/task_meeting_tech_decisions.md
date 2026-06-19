---
id: task_meeting_tech_decisions
name: 會議決議擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_tech_decisions
source_benchmark: pinchbench
claw_eval_id: P116zh_meeting_tech_decisions
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 會議決議擷取

## Prompt

我有一個檔案 `meeting_transcript.md`，內含一場 2021 年 6 月 28 日的 GitLab Product Marketing 週會逐字稿。會議涵蓋企業活動贊助、GitLab Commit 的產品發布、競爭分析方法論、資訊圖設計回饋，以及一場訊息架構練習。

請辨識出會議期間所做成的所有決議（或達成的共識），並寫入一個名為 `decisions.md` 的檔案。針對每一項決議，請包含：

- **決議（Decision）**（決定了什麼）
- **背景脈絡（Context）**（為何討論此事的簡要背景）
- **參與者（Participants involved）**（誰表達了意見）
- **狀態（Status）**（final、tentative，或 needs follow-up）

並在最上方附上一段彙總，說明決議總數，以及其中哪些可能需要進一步確認。

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿
2. 區分決議（已達成的結論）與尚在進行的討論
3. 掌握每項決議背後的背景脈絡

應辨識出的關鍵決議：

1. **活動指派**：Platform team → AWS re:Invent、CI/CD → Google Next、GitOps → KubeCon
2. **產品發布方式**：將多個小型 MVC 整合為較大的主題（例如 vulnerability management），而非逐一條列個別功能；重用 GitLab 14.0 內容並加入新增項目
3. **Top 5 功能挑選**：團隊將從所有 stages 中挑出整體前 5 名功能用於 Commit keynote（而非每個 stage 取 3 個）
4. **競爭比較表方法論**：僅使用 tier one 競爭對手；僅納入與各特定 stage 相關的競爭對手（並非每個 stage 都放全部 5 個）；加入一個 GitLab 項目以供比較
5. **資訊圖配色**：維持只用綠色的配色方案（不用紅/黃），以保持比較（comparison）的調性而非競爭攻擊
6. **訊息標語挑選**：選定「More speed less risk」為最終標語（勝過「move fast with confidence」、「no trade-offs」等替代方案）
7. **Stage 命名**：承認如「configure」與「monitor」等 stage 名稱描述性不足，但目前先沿用；下一次迭代將加入可點選進入的細節頁面

## Grading Criteria

- [ ] 已建立檔案 decisions.md
- [ ] 至少辨識出 5 項不同的決議
- [ ] 已掌握活動指派的決議（re:Invent、Google Next、KubeCon）
- [ ] 已掌握產品發布的整合（bundling）方式
- [ ] 已掌握競爭方法論的決議（僅 tier one、相關 stages、GitLab 列）
- [ ] 已掌握訊息標語的決議（「more speed less risk」）
- [ ] 已掌握資訊圖配色的決議（只用綠色、不用紅色）
- [ ] 每項決議皆提供背景脈絡
- [ ] 已標示決議狀態（final 對比 needs follow-up）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting decisions extraction task.

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

    report_path = workspace / "decisions.md"
    if not report_path.exists():
        for alt in ["meeting_decisions.md", "decision_log.md", "decisions_summary.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "min_decisions": 0.0,
            "event_assignments": 0.0,
            "announcement_approach": 0.0,
            "competitive_methodology": 0.0,
            "messaging_tagline": 0.0,
            "infographic_colors": 0.0,
            "context_provided": 0.0,
            "status_indicated": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check minimum number of decisions
    decision_markers = re.findall(r'(?:^|\n)\s*(?:[-*•]|\d+[.)]) .{10,}', content)
    headers = re.findall(r'(?:^|\n)#+\s+.+', content)
    scores["min_decisions"] = 1.0 if len(decision_markers) >= 5 or len(headers) >= 5 else (0.5 if len(decision_markers) >= 3 or len(headers) >= 3 else 0.0)

    # Event assignments
    event_terms = ["reinvent", "re:invent", "google next", "kubecon"]
    event_hits = sum(1 for t in event_terms if t in content_lower)
    scores["event_assignments"] = 1.0 if event_hits >= 2 else (0.5 if event_hits >= 1 else 0.0)

    # Announcement approach (bundling/grouping MVCs)
    announce_patterns = [
        r'(?:bundle|group|bucket|aggregat)',
        r'(?:vulnerability\s*management|mvc|14\.0)',
    ]
    announce_hits = sum(1 for p in announce_patterns if re.search(p, content_lower))
    scores["announcement_approach"] = 1.0 if announce_hits >= 2 else (0.5 if announce_hits >= 1 else 0.0)

    # Competitive methodology
    comp_patterns = [
        r'(?:tier\s*(?:one|1))',
        r'(?:gitlab\s*(?:line|row|column)|add\s*gitlab|gitlab\s*comparison)',
        r'(?:relevant|applicable).*(?:stage|competitor)',
    ]
    comp_hits = sum(1 for p in comp_patterns if re.search(p, content_lower))
    scores["competitive_methodology"] = 1.0 if comp_hits >= 2 else (0.5 if comp_hits >= 1 else 0.0)

    # Messaging tagline
    tagline_patterns = [
        r'more\s*speed\s*less\s*risk',
    ]
    scores["messaging_tagline"] = 1.0 if any(re.search(p, content_lower) for p in tagline_patterns) else 0.0

    # Infographic colors
    color_patterns = [
        r'(?:green|color).*(?:no\s*red|without\s*red|comparison)',
        r'(?:no\s*red|avoid\s*red|stick\s*with\s*green)',
    ]
    scores["infographic_colors"] = 1.0 if any(re.search(p, content_lower) for p in color_patterns) else 0.0

    # Context provided (look for explanatory text around decisions)
    context_patterns = [r'(?:because|reason|background|context|rationale|why|since|given\s*that)', r'(?:discuss|debate|consider|weigh)']
    context_hits = sum(1 for p in context_patterns if re.search(p, content_lower))
    scores["context_provided"] = 1.0 if context_hits >= 2 else (0.5 if context_hits >= 1 else 0.0)

    # Status indicated
    status_patterns = [r'(?:final|tentative|follow.?up|confirmed|pending|needs?\s*(?:confirmation|follow))', r'(?:status|resolved|agreed|consensus)']
    status_hits = sum(1 for p in status_patterns if re.search(p, content_lower))
    scores["status_indicated"] = 1.0 if status_hits >= 2 else (0.5 if status_hits >= 1 else 0.0)

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

### 評分項 1：決議辨識準確度（權重 35%）

**1.0 分**：辨識出所有主要決議，包含活動指派、發布方式、競爭方法論、資訊圖配色與訊息標語。正確區分決議與進行中的討論。
**0.75 分**：掌握多數決議，但漏掉一項，或誤把曾討論但未決定的項目納入。
**0.5 分**：掌握部分決議，但漏掉數項，或把討論與決議混為一談。
**0.25 分**：僅辨識出一兩項顯而易見的決議。
**0.0 分**：未辨識出有意義的決議。

### 評分項 2：背景脈絡品質（權重 25%）

**1.0 分**：每項決議皆包含準確的背景脈絡，說明是什麼促成討論、考慮過哪些替代方案，以及為何選定該方案。
**0.75 分**：多數決議有良好背景脈絡，僅有少許缺口。
**0.5 分**：提供部分背景脈絡，但缺少關鍵推理或所考慮的替代方案。
**0.25 分**：背景脈絡極少，決議僅逐條列出而無說明。
**0.0 分**：未提供背景脈絡。

### 評分項 3：參與者歸屬（權重 20%）

**1.0 分**：正確指出誰倡議每一立場、誰參與了達成共識。姓名準確取自逐字稿。
**0.75 分**：多數參與者正確辨識，僅有少許錯誤。
**0.5 分**：辨識出部分參與者，但有數位缺漏或誤植。
**0.25 分**：參與者辨識極少。
**0.0 分**：未歸屬參與者。

### 評分項 4：結構與實用性（權重 20%）

**1.0 分**：決議格式清楚、結構一致，附上實用的彙總，並標示哪些決議為 final、哪些需 follow-up。可直接作為會議紀錄使用。
**0.75 分**：結構良好，僅有少許格式問題。
**0.5 分**：可讀，但結構不一致或缺少彙總。
**0.25 分**：組織不佳，難以作為參考。
**0.0 分**：無可用結構。
