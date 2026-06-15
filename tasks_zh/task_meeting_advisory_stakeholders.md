---
id: task_meeting_advisory_stakeholders
name: NTIA Advisory Board 利害關係人利益
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_advisory_stakeholders
source_benchmark: pinchbench
claw_eval_id: P121zh_meeting_advisory_stakeholders
workspace_files:
- source: meetings/2012-05-30-meeting-transcript-ntia-csmac.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# NTIA Advisory Board 利害關係人利益

## Prompt

我這裡有一份政府諮詢委員會會議的逐字稿，存放在 `meeting-transcript.md`。這是 Commerce Spectrum Management Advisory Committee（CSMAC）於 2012 年 5 月 30 日舉行的會議，聚焦於在政府與商用無線寬頻之間共享聯邦頻譜（1755-1850 MHz band）。

請分析這份逐字稿，並在一個名為 `stakeholder_analysis.md` 的檔案中建立一份利害關係人分析。針對每個利害關係人群體或個人，請辨識：

- **利害關係人名稱/群體**（例如「Department of Defense」、「Commercial Wireless Carriers」、「NTIA」、立場鮮明的個別委員會成員）
- **主要利益**（他們希望從此程序中得到什麼）
- **提出的關切**（所表達的具體擔憂或反對）
- **對共享（sharing）對比遷移（relocation）的立場**（他們在這個關鍵問題上的立場）
- **影響力等級**（依其角色與參與程度判定為 high/medium/low）

此外也請辨識：

- 利害關係人之間的**共識領域**
- 利害關係人群體之間的**關鍵張力或衝突**
- 會議期間提出的**未解決問題**

## Expected Behavior

助手應該：

1. 讀取並分析會議逐字稿
2. 辨識主要利害關係人群體及其立場
3. 將個別成員對應到他們所代表的利益
4. 掌握共享對比遷移的細緻立場

關鍵利害關係人群體及其利益：

- **NTIA/Karl Nebbia**：偏好共享勝過遷移，希望建立政府與業界合作的框架，關切 $18B 的遷移成本
- **White House/OSTP（Tom Power）**：支持 Obama 政府的 500 MHz 目標，強調共享為關鍵途徑
- **商用電信業者（AT&T/Carl Povelites、Verizon/Molly Feldman）**：希望取得 3 GHz 以下的頻譜，關注遷移時程與成本準確性
- **國防/軍方利益（Jennifer Warren/Lockheed Martin、Rick Reaser/Raytheon）**：需保護訓練、UAV 操作、衛星上行鏈路、電子戰能力
- **科技公司（Kevin Kahn/Intel）**：對標準收斂（LTE）務實，希望有實際可行的技術參數
- **學界/獨立顧問（Charles Rush、Dale Hatfield、Dave Borth）**：力主嚴謹的技術分析、各 working group 之間採用共同參數
- **公共利益（Michael Calabrese/New America Foundation）**：倡議 small cell/較低功率的途徑、有效率的頻譜使用
- **公眾參與者（Mr. Snider）**：關切公眾意見機會的萎縮

關鍵張力：
- 共享對比完全遷移
- 轉換成本（$18B 估計遭質疑）
- 各 working group 之間需要共同的商用部署參數
- 機密/敏感資訊的存取
- 程序中的公眾參與

## Grading Criteria

- [ ] 已建立檔案 stakeholder_analysis.md
- [ ] 已辨識政府利害關係人（NTIA、DoD、DHS/Justice、White House/OSTP）
- [ ] 已辨識商業界利害關係人（電信業者、設備製造商）
- [ ] 已記下 NTIA 偏好共享勝過純遷移
- [ ] 已提及 $18 billion 遷移成本為關鍵因素
- [ ] 已描述共享與遷移途徑之間的張力
- [ ] 已掌握共同技術參數的辯論（Rush/Warren/Kahn 的討論）
- [ ] 已辨識至少 3 個共識或衝突領域
- [ ] 個別成員立場連結到其組織利益

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the stakeholder analysis task.

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

    report_path = workspace / "stakeholder_analysis.md"
    if not report_path.exists():
        alternatives = ["stakeholders.md", "stakeholder_report.md", "analysis.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "gov_stakeholders": 0.0,
            "commercial_stakeholders": 0.0,
            "sharing_preference": 0.0,
            "relocation_cost": 0.0,
            "sharing_vs_relocation": 0.0,
            "common_parameters": 0.0,
            "conflicts_identified": 0.0,
            "member_positions": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Government stakeholders identified
    gov_entities = ["ntia", "dod", "department of defense", "defense",
                    "dhs", "homeland security", "justice",
                    "white house", "ostp", "science and technology policy"]
    gov_found = sum(1 for g in gov_entities if g in content_lower)
    scores["gov_stakeholders"] = 1.0 if gov_found >= 4 else (0.5 if gov_found >= 2 else 0.0)

    # Commercial stakeholders identified
    commercial = ["carrier", "wireless", "commercial", "industry",
                   "at&t", "att", "verizon", "intel", "t-mobile",
                   "equipment manufacturer", "service provider",
                   "ctia", "broadband"]
    comm_found = sum(1 for c in commercial if c in content_lower)
    scores["commercial_stakeholders"] = 1.0 if comm_found >= 4 else (0.5 if comm_found >= 2 else 0.0)

    # NTIA sharing preference noted
    sharing_patterns = [
        r'ntia.*(?:prefer|favor|advocate|support).*shar',
        r'shar.*(?:prefer|favor|better|alternative).*(?:relocat|vacat)',
        r'(?:better way|minimize.*movement|keep.*cost)',
        r'days of vacating.*coming to a close',
    ]
    scores["sharing_preference"] = 1.0 if any(re.search(p, content_lower) for p in sharing_patterns) else 0.0

    # $18 billion relocation cost mentioned
    cost_patterns = [r'\$?18\s*billion', r'18b', r'\$18b', r'18,000', r'eighteen billion']
    scores["relocation_cost"] = 1.0 if any(re.search(p, content_lower) for p in cost_patterns) else 0.0

    # Sharing vs relocation tension described
    tension_patterns = [
        r'shar.*(?:vs|versus|or|instead of|rather than).*relocat',
        r'relocat.*(?:vs|versus|or|instead of|rather than).*shar',
        r'(?:sharing|relocation).*(?:tension|debate|disagreement|question|trade-?off)',
        r'(?:why.*spend.*money.*move|if.*sharing.*works)',
    ]
    scores["sharing_vs_relocation"] = 1.0 if any(re.search(p, content_lower) for p in tension_patterns) else 0.0

    # Common parameters debate captured
    param_patterns = [
        r'(?:common|uniform|consistent).*(?:parameter|characteristic|assumption|input)',
        r'(?:parameter|characteristic|assumption).*(?:common|uniform|consistent|agree)',
        r'rush.*(?:parameter|standard|commercial)',
        r'warren.*(?:common|input|working group)',
        r'kahn.*(?:standard|lte)',
    ]
    scores["common_parameters"] = 1.0 if any(re.search(p, content_lower) for p in param_patterns) else 0.0

    # Conflicts/agreements identified (look for structural markers)
    conflict_indicators = 0
    conflict_terms = [
        r'(?:tension|conflict|disagree|debate|challenge|concern|oppose)',
        r'(?:agree|consensus|common ground|alignment|shared interest)',
        r'(?:unresolved|open question|outstanding|remain)',
    ]
    for ct in conflict_terms:
        if re.search(ct, content_lower):
            conflict_indicators += 1
    scores["conflicts_identified"] = 1.0 if conflict_indicators >= 2 else (0.5 if conflict_indicators >= 1 else 0.0)

    # Individual member positions linked to organizations
    member_org_pairs = [
        (r'rush', r'(?:consult|cmr|fcc|parameter)'),
        (r'warren', r'(?:lockheed|defense|military|engineer)'),
        (r'kahn', r'(?:intel|standard|lte)'),
        (r'calabrese', r'(?:new america|small cell|unlicensed|public interest)'),
        (r'povelites', r'(?:at.t|carrier|cost|relocation)'),
    ]
    pair_found = sum(1 for name, org in member_org_pairs
                     if re.search(name, content_lower) and re.search(org, content_lower))
    scores["member_positions"] = 1.0 if pair_found >= 3 else (0.5 if pair_found >= 2 else 0.0)

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

### 評分項 1：利害關係人辨識完整度（權重 30%）

**1.0 分**：辨識出所有主要利害關係人群體（政府機關、商用電信業者、設備製造商、國防承包商、學界、公共利益、公眾參與者），並在適用處附上具名代表。
**0.75 分**：辨識出多數利害關係人群體，僅有少許遺漏。
**0.5 分**：辨識出主要群體，但漏掉重要的次類別或代表。
**0.25 分**：僅辨識出最明顯的利害關係人（政府對比業界）。
**0.0 分**：利害關係人辨識不完整或不準確。

### 評分項 2：利益與立場分析（權重 30%）

**1.0 分**：每個利害關係人的利益、關切，以及對共享對比遷移的立場皆清楚闡述，並有逐字稿佐證。細緻立場皆有掌握（例如 NTIA 從遷移轉向偏好共享、業界對確定性的渴望）。
**0.75 分**：對多數利害關係人立場分析良好，僅有少許缺口。
**0.5 分**：記下基本立場，但缺乏細緻度或佐證。
**0.25 分**：對利害關係人立場處理流於表面。
**0.0 分**：立場錯誤或未分析。

### 評分項 3：衝突與共識對應（權重 25%）

**1.0 分**：清楚對應出關鍵張力（共享對比遷移、共同參數辯論、機密資訊存取、公眾參與、成本爭議）。共識領域亦有記下（需要合作、頻譜稀缺的現實）。
**0.75 分**：辨識出多數關鍵張力，僅有少許遺漏。
**0.5 分**：記下部分張力，但分析淺薄。
**0.25 分**：僅提及最明顯的衝突。
**0.0 分**：無衝突或共識分析。

### 評分項 4：證據導向分析（權重 15%）

**1.0 分**：論點皆有具體引文或對逐字稿對話的引用佐證。個別成員的發言皆正確歸屬。
**0.75 分**：多數論點皆有逐字稿證據佐證。
**0.5 分**：提供部分證據，但許多論點無佐證。
**0.25 分**：大致為斷言式而無逐字稿支撐。
**0.0 分**：未使用逐字稿證據。
