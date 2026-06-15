---
id: task_meeting_tech_product_features
name: |
  會議產品功能優先排序
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_tech_product_features
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T119tw_meeting_tech_product_features
workspace_files:
- source: meetings/2021-06-28-gitlab-product-marketing-meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 會議產品功能優先排序


## Prompt

我手上有一個檔案 `meeting_transcript.md`，內含一場 2021 年 6 月 28 日的 GitLab Product Marketing 週會逐字稿。會議有相當篇幅在討論要在即將到來的 GitLab Commit 大會上重點呈現哪些產品功能與改進。

請幫我分析這份逐字稿，並建立一個名為 `feature_priorities.md` 的檔案，內含一份依優先順序排列的功能清單。針對每個功能，請包含：

1. **功能名稱**
2. **Stage/領域**（例如 Create、Secure、Monitor、Plan、CI/CD、GitOps 等）
3. **興奮度（Excitement level）**（依會議討論為 1-3，3 為最令人興奮）
4. **描述**（該功能的作用或重要性）
5. **備註**（任何討論要點，例如是否為社群貢獻、是否已有媒體報導等）

此外也請包含：
- 團隊對 Commit keynote 的**整體 top 5 名選**
- 他們議定用來評估功能的**方法論**（整合 MVCs、興奮度等級、stack ranking）
- 任何被**明確降低優先序（deprioritized）**的功能及其原因

## Expected Behavior

助手應該：

1. 解析會議逐字稿以找出所有功能討論
2. 擷取並整理功能及其後設資料

討論到的關鍵功能：

**Top 5 / 高優先序：**
1. **UX improvements**（跨 stage）— 興奮度：3。Brian 指出這不僅限於 Create stage。依業界慣例屬常見的「big launch」類別。
2. **Vulnerability management**（Secure）— 興奮度：高。Cindy 提議把一整年的多個小型 MVC 整合為單一敘事。已是 14.0 發布的一部分。
3. **GitOps capabilities**（Configure/GitOps）— Kubernetes agent + HashiCorp/Terraform 整合，包裹在一起。
4. **Pipeline editor**（CI/CD）— 被提及為 CI/CD stage 的明確選項。
5. **Something from Plan** — 指派給 Cormac 補上；提到 epic boards（長期被要求的功能）、milestone burnup charts。

**其他值得注意的功能：**
- **Fuzzing acquisitions**（Secure）— 被降低優先序，因為已有兩次媒體報導（收購公告 + 整合後續），已「worn out」
- **Semgrep scanner replacement**（Secure）— 取代了既有掃描器；可作為一個項目
- **DAST Browser scanner**（Secure）— 用於單頁應用的專有 DAST，beta 階段；代號「Berserker」
- **VS Code integrations**（Create）— 兩個源自社群貢獻的整合；非官方的擴充功能轉為官方
- **Terraform module**（Configure）— 社群模組現已獲官方支援
- **Value Stream Analytics**（Plan）— 可能的題材，但可自訂版本來自 12.9（太舊）
- **Incident management**（Monitor）— 一批改進的整合，但核心來自更早之前

**方法論：**
- 將多個小型 MVC 整合為較大的主題，而非逐一列出個別功能
- 以興奮度 1-3 作為 stack rank（各取一個，而非原始分數）
- 回顧過去一年，找出當初為 beta、現已 GA-ready 的功能
- 重用 GitLab 14.0 發布內容並加入新增項目
- 目標：整體 top 5 供 PR 團隊作為 keynote 素材

## Grading Criteria

- [ ] 已建立檔案 feature_priorities.md
- [ ] 至少列出 8 個不同的功能或功能組合
- [ ] UX improvements 被辨識為 top pick
- [ ] Vulnerability management 被辨識為 top pick
- [ ] GitOps/Kubernetes agent 被辨識為 top pick
- [ ] 提及 CI/CD 的 Pipeline editor
- [ ] Fuzzing 因先前媒體報導而被降低優先序
- [ ] 已記下社群貢獻（VS Code、Terraform module）
- [ ] 已掌握整合（bundling）方法論（把 MVCs 整合為主題）
- [ ] 已包含整體 top 5 名選區段

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the meeting product feature prioritization task.

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

    report_path = workspace / "feature_priorities.md"
    if not report_path.exists():
        for alt in ["features.md", "product_features.md", "feature_list.md", "priorities.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "min_features": 0.0,
            "ux_top_pick": 0.0,
            "vuln_mgmt_top_pick": 0.0,
            "gitops_top_pick": 0.0,
            "pipeline_editor": 0.0,
            "fuzzing_deprioritized": 0.0,
            "community_contributions": 0.0,
            "bundling_methodology": 0.0,
            "top_five_section": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Minimum features listed
    feature_markers = re.findall(r'(?:^|\n)\s*(?:[-*•]|\d+[.)]) .{10,}', content)
    headers = re.findall(r'(?:^|\n)#+\s+.+', content)
    total_items = len(feature_markers) + len(headers)
    scores["min_features"] = 1.0 if total_items >= 8 else (0.5 if total_items >= 5 else 0.0)

    # UX as top pick
    ux_patterns = [
        r'(?:ux|user\s*experience).*(?:top|high|exciting|priorit|important)',
        r'(?:top|high|exciting|priorit|important).*(?:ux|user\s*experience)',
    ]
    scores["ux_top_pick"] = 1.0 if any(re.search(p, content_lower) for p in ux_patterns) else (0.5 if re.search(r'(?:ux|user\s*experience)', content_lower) else 0.0)

    # Vulnerability management as top pick
    vuln_patterns = [
        r'vulnerability\s*management',
    ]
    scores["vuln_mgmt_top_pick"] = 1.0 if any(re.search(p, content_lower) for p in vuln_patterns) else 0.0

    # GitOps/K8s agent as top pick
    gitops_patterns = [
        r'(?:kubernetes|k8s)\s*agent',
        r'gitops',
        r'(?:hashicorp|terraform)\s*integrat',
    ]
    gitops_hits = sum(1 for p in gitops_patterns if re.search(p, content_lower))
    scores["gitops_top_pick"] = 1.0 if gitops_hits >= 2 else (0.5 if gitops_hits >= 1 else 0.0)

    # Pipeline editor
    scores["pipeline_editor"] = 1.0 if re.search(r'pipeline\s*editor', content_lower) else 0.0

    # Fuzzing deprioritized
    fuzzing_patterns = [
        r'fuzz.*(?:already|prior|previous|worn|press|cover|depriorit)',
        r'(?:already|prior|previous|worn|press|cover|depriorit).*fuzz',
    ]
    scores["fuzzing_deprioritized"] = 1.0 if any(re.search(p, content_lower) for p in fuzzing_patterns) else (0.5 if re.search(r'fuzz', content_lower) else 0.0)

    # Community contributions
    community_patterns = [
        r'communit.*contribut',
        r'(?:vs\s*code|vscode).*communit',
        r'communit.*(?:vs\s*code|vscode|terraform)',
    ]
    community_hits = sum(1 for p in community_patterns if re.search(p, content_lower))
    scores["community_contributions"] = 1.0 if community_hits >= 1 else 0.0

    # Bundling methodology
    bundle_patterns = [
        r'(?:bundle|group|bucket|aggregat|roll\s*up)',
        r'(?:mvc|small\s*feature|iteration)',
        r'(?:theme|narrative|story)',
    ]
    bundle_hits = sum(1 for p in bundle_patterns if re.search(p, content_lower))
    scores["bundling_methodology"] = 1.0 if bundle_hits >= 2 else (0.5 if bundle_hits >= 1 else 0.0)

    # Top 5 section
    top5_patterns = [
        r'top\s*(?:five|5)',
    ]
    scores["top_five_section"] = 1.0 if any(re.search(p, content_lower) for p in top5_patterns) else 0.0

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

### 評分項 1：功能擷取完整度（權重 30%）

**1.0 分**：列出所有討論到的功能，包含 UX improvements、vulnerability management、GitOps/K8s agent、pipeline editor、fuzzing、Semgrep、DAST Browser（Berserker）、VS Code integrations、Terraform module、value stream analytics、incident management 與 epic boards。每項皆有準確的 stage 歸屬。
**0.75 分**：掌握多數功能並有正確 stage 歸屬，漏掉一兩個。
**0.5 分**：掌握主要功能，但漏掉數個次要的。
**0.25 分**：僅掌握最顯而易見的功能。
**0.0 分**：未擷取出有意義的功能。

### 評分項 2：優先排序準確度（權重 30%）

**1.0 分**：正確指出浮現的 top 5（UX、vulnerability management、GitOps bundle、CI/CD、Plan 待定）。準確反映興奮度等級與團隊的排序理由。記下哪些功能被降低優先序（fuzzing 因先前媒體報導）以及哪些需 follow-up。
**0.75 分**：top picks 大致正確，僅有少許排序問題。
**0.5 分**：有部分優先排序，但漏掉關鍵排名或理由。
**0.25 分**：功能逐條列出但無有意義的優先排序。
**0.0 分**：未嘗試優先排序。

### 評分項 3：方法論記載（權重 20%）

**1.0 分**：清楚說明議定的方法論：把 MVCs 整合為主題、以 1-3 興奮度作為 stack rank、回顧過去一年找出 beta→GA 功能、重用 14.0 內容、目標整體 top 5 供 PR 使用。並記下從「每個 stage 取 3 個」改為「整體 top 5」的轉變。
**0.75 分**：掌握多數方法論要素。
**0.5 分**：提及部分方法論但不完整。
**0.25 分**：方法論提及含糊。
**0.0 分**：未記載方法論。

### 評分項 4：背景脈絡與細節品質（權重 20%）

**1.0 分**：每個功能皆含相關背景脈絡：社群貢獻狀態、先前媒體報導、成熟度、客戶需求訊號（upvotes、MAU 討論）。並記下與 GitLab Commit keynote 的關聯。
**0.75 分**：背景脈絡良好，僅有少許缺口。
**0.5 分**：有部分背景脈絡，但許多功能缺乏細節。
**0.25 分**：提供的背景脈絡極少。
**0.0 分**：無背景脈絡或細節。
