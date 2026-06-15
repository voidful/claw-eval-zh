---
id: task_meeting_tech_competitors
name: 會議競爭對手分析擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_tech_competitors
source_benchmark: pinchbench
claw_eval_id: P117zh_meeting_tech_competitors
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 會議競爭對手分析擷取

## Prompt

我有一個檔案 `meeting_transcript.md`，內含一場 2021 年 6 月 28 日的 GitLab Product Marketing 週會逐字稿。會議的一部分涉及競爭定位（competitive positioning）、一份比較試算表，以及如何呈現 GitLab 對比競爭對手的詳細討論。

請分析這份逐字稿，並建立一個名為 `competitor_analysis.md` 的檔案，內容涵蓋：

1. **提及的競爭對手**：列出所有提及的競爭對手或競品，並附上有討論到的層級分類（tier classification）
2. **競爭定位方式**：團隊計畫如何將 GitLab 定位於這些競爭對手之上？
3. **各 stage 對應的競爭對手對照**：哪些競爭對手對應到哪些產品 stages（如討論所述）？
4. **方法論決議**：對於如何進行競爭分析做了哪些決定（例如聚焦哪些 tiers、如何處理競爭對手不適用的 stage）？
5. **關鍵競爭洞察**：討論中提到關於特定競爭對手的任何策略性洞察

## Expected Behavior

助手應該：

1. 仔細閱讀會議逐字稿
2. 擷取所有競爭對手名稱並予以分類

關鍵競爭對手與細節：

- **Tier 1 競爭對手**（目前分析的重點）：Azure DevOps（ADO）、Atlassian、GitHub、Jenkins、JFrog、CloudBees
- **層級分類**：團隊先前已將競爭對手分為 tier 1、2、3；目前僅聚焦於 tier 1
- **Stage 相關性**：並非所有 tier 1 競爭對手都適用於所有 stages（例如 CloudBees 可能與 Monitor 無關；GitHub 可能與 Monitor 無關）
- **Platform 定位**：部分競爭對手（Azure DevOps、GitHub、Atlassian、JFrog）將自己定位為 platform；Jenkins/CloudBees 則否
- **方法論**：競爭試算表是被複製貼上、每個 stage 分頁都放同樣的 6 個競爭對手，這被指出是錯的——每個 stage 應只出現相關的競爭對手
- **GitLab 項目**：團隊決定在比較表加入一個 GitLab 列，使該表不會只呈現 GitLab 較強之處
- **功能挑選視角**：功能應從市場視角（market lens，即買家會比較選購什麼）挑選，而非僅從 GitLab 視角；為求誠實，也應納入一些僅競爭對手才有的功能
- **資訊圖方式**：新設計只用綠色（不用紅色），呈現為有幫助的產業比較，而非競爭攻擊式素材

## Grading Criteria

- [ ] 已建立檔案 competitor_analysis.md
- [ ] 已列出所有 tier 1 競爭對手（ADO/Azure DevOps、Atlassian、GitHub、Jenkins、JFrog、CloudBees）
- [ ] 已提及層級分類系統（tier 1、2、3）
- [ ] 已討論各 stage 的相關性（並非所有競爭對手都適用於所有 stages）
- [ ] 已掌握 platform 與非 platform 的區分（GitHub、ADO、Atlassian、JFrog 為 platform；Jenkins/CloudBees 則否）
- [ ] 已掌握加入 GitLab 項目的決議
- [ ] 已記下功能挑選的市場視角（market lens）方式
- [ ] 已掌握資訊圖設計理念（只用綠色、比較而非攻擊）
- [ ] 已掌握先聚焦 tier 1 的方法論決議

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting competitor analysis extraction task.

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

    report_path = workspace / "competitor_analysis.md"
    if not report_path.exists():
        for alt in ["competitors.md", "competitive_analysis.md", "competitor_report.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "tier1_competitors": 0.0,
            "tier_system": 0.0,
            "stage_relevance": 0.0,
            "platform_distinction": 0.0,
            "gitlab_line_item": 0.0,
            "market_lens": 0.0,
            "infographic_philosophy": 0.0,
            "tier1_focus": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Tier 1 competitors listed
    competitors = {
        "ado": [r'(?:azure\s*devops|ado)'],
        "atlassian": [r'atlassian'],
        "github": [r'github'],
        "jenkins": [r'jenkins'],
        "jfrog": [r'jfrog|j\s*frog'],
        "cloudbees": [r'cloudbees|cloud\s*bees'],
    }
    comp_count = 0
    for name, patterns in competitors.items():
        if any(re.search(p, content_lower) for p in patterns):
            comp_count += 1
    scores["tier1_competitors"] = 1.0 if comp_count >= 5 else (0.75 if comp_count >= 4 else (0.5 if comp_count >= 3 else 0.0))

    # Tier classification system
    tier_patterns = [r'tier\s*(?:one|1|two|2|three|3)', r'tier[- ]?\d']
    scores["tier_system"] = 1.0 if any(re.search(p, content_lower) for p in tier_patterns) else 0.0

    # Stage-specific relevance
    stage_patterns = [
        r'(?:not\s*(?:all|every)|relevant|applicable|apply).*(?:stage|monitor|configure)',
        r'(?:stage|monitor|configure).*(?:not\s*(?:all|every)|relevant|applicable)',
    ]
    scores["stage_relevance"] = 1.0 if any(re.search(p, content_lower) for p in stage_patterns) else 0.0

    # Platform distinction
    platform_patterns = [
        r'platform',
    ]
    non_platform_patterns = [
        r'(?:jenkins|cloudbees).*(?:not|don.t|doesn.t).*platform',
        r'(?:not|don.t|doesn.t).*platform.*(?:jenkins|cloudbees)',
    ]
    has_platform = any(re.search(p, content_lower) for p in platform_patterns)
    has_non_platform = any(re.search(p, content_lower) for p in non_platform_patterns)
    scores["platform_distinction"] = 1.0 if has_platform and has_non_platform else (0.5 if has_platform else 0.0)

    # GitLab line item decision
    gitlab_patterns = [
        r'(?:add|include).*gitlab.*(?:line|row|column|entry)',
        r'gitlab.*(?:line|row|column|entry).*(?:add|include)',
        r'(?:add|include).*(?:line|row|column|entry).*gitlab',
    ]
    scores["gitlab_line_item"] = 1.0 if any(re.search(p, content_lower) for p in gitlab_patterns) else 0.0

    # Market lens approach
    market_patterns = [
        r'market\s*lens',
        r'(?:buyer|customer|shopp)',
        r'(?:honest|trustworthy|accurate\s*assessment)',
    ]
    market_hits = sum(1 for p in market_patterns if re.search(p, content_lower))
    scores["market_lens"] = 1.0 if market_hits >= 2 else (0.5 if market_hits >= 1 else 0.0)

    # Infographic philosophy
    infographic_patterns = [
        r'(?:green|color).*(?:comparison|helpful|industry)',
        r'(?:no\s*red|without\s*red|avoid\s*red)',
        r'(?:comparison|helpful).*(?:not\s*(?:competitive|attack))',
    ]
    infographic_hits = sum(1 for p in infographic_patterns if re.search(p, content_lower))
    scores["infographic_philosophy"] = 1.0 if infographic_hits >= 2 else (0.5 if infographic_hits >= 1 else 0.0)

    # Tier 1 focus decision
    focus_patterns = [
        r'(?:focus|only|just).*tier\s*(?:one|1)',
        r'tier\s*(?:one|1).*(?:focus|first|now|current)',
    ]
    scores["tier1_focus"] = 1.0 if any(re.search(p, content_lower) for p in focus_patterns) else 0.0

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

### 評分項 1：競爭對手辨識完整度（權重 30%）

**1.0 分**：辨識出全部六個 tier 1 競爭對手（Azure DevOps、Atlassian、GitHub、Jenkins、JFrog、CloudBees），並有準確的層級分類與對 tier 系統的討論。
**0.75 分**：辨識出多數競爭對手並附 tier 資訊，漏掉一兩個。
**0.5 分**：辨識出數個競爭對手，但 tier 系統說明不佳。
**0.25 分**：僅提及少數競爭對手且無分類。
**0.0 分**：未辨識出競爭對手。

### 評分項 2：策略定位分析（權重 30%）

**1.0 分**：完整掌握 GitLab 定位方式的所有細微之處：功能採市場視角、platform 對比非 platform 的區分、只用綠色的資訊圖以呈現比較（而非攻擊）、加入 GitLab 列以誠實比較，以及打造有幫助的產業資源此一目標。
**0.75 分**：掌握多數定位要素，僅有少許缺口。
**0.5 分**：有部分定位洞察，但漏掉關鍵策略決議。
**0.25 分**：對競爭定位僅有表面提及。
**0.0 分**：無定位分析。

### 評分項 3：各 stage 對照（權重 20%）

**1.0 分**：清楚說明並非所有競爭對手都適用於所有 stages，給出具體例子（例如 CloudBees/GitHub 與 Monitor 無關），並記下被指出的試算表複製貼上問題。
**0.75 分**：對 stage 相關性有良好理解，僅有少許缺口。
**0.5 分**：提及 stage 相關性但缺乏具體細節。
**0.25 分**：對 stages 僅含糊提及。
**0.0 分**：無各 stage 分析。

### 評分項 4：方法論清晰度（權重 20%）

**1.0 分**：清楚記載議定的方法論：先聚焦 tier 1，再擴展；每個 stage 只放相關競爭對手；功能採市場視角；加入 GitLab 以供比較。並以可行動的指引方式呈現。
**0.75 分**：掌握多數方法論決議。
**0.5 分**：提及部分方法論但不完整。
**0.25 分**：方法論描述含糊。
**0.0 分**：未記載方法論。
