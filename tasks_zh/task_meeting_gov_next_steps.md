---
id: task_meeting_gov_next_steps
name: NASA UAP 聽證會後續步驟擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_gov_next_steps
source_benchmark: pinchbench
claw_eval_id: P136zh_meeting_gov_next_steps
workspace_files:
- source: meetings/2025-07-30-nasa-holds-first-public-meeting-on-ufos-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# NASA UAP 聽證會後續步驟擷取

## Prompt

我有一份逐字稿檔案 `transcript.md`，來自 NASA 首場關於不明異常現象（UAPs/UFOs）的公開會議。這是一場審議會議，在小組提出最終報告前還有數個月的工作要做。

請閱讀逐字稿，並把所有提及的後續步驟、後續行動、時程與交付項目擷取到名為 `next_steps.md` 的檔案。對於每一項，請列出：

- **行動項目（Action item）**：需要發生的事
- **負責方（Responsible party）**：預期由誰負責——NASA、AARO、小組、FAA 等
- **時程（Timeline）**：預期何時（若有提及）
- **狀態（Status）**：被提及為計畫中、進行中或已完成
- **來源（Source）**：誰在會議中提到的

請組織成以下區段：Immediate Next Steps（數週）、Near-Term Actions（數月）、Longer-Term Goals（持續／數年）與 Open Questions（被提出但尚無明確後續指派的項目）。最後附上一份時間軸視覺化，呈現關鍵里程碑。

## Expected Behavior

助手應該：

1. 讀取並解析完整逐字稿
2. 辨識所有關於行動、交付項目與時程的前瞻性陳述
3. 區分已承諾的行動與抱負性的目標
4. 注意哪些項目有具體時程、哪些時機模糊

關鍵後續步驟與後續行動：

**Immediate（數週）：**
- 小組在本次會議後將持續審議「數個月」（Evans）
- AARO 年度報告須於 August 1 前提交國會，並附更新的案例數字（Kirkpatrick）
- AARO 在首次論壇後正建立 Five Eyes 資料共享協議（Kirkpatrick）

**Near-Term（數月）：**
- 小組最終報告將於「this summer」／「by end of July」前發布（Evans、Spergel）
- 報告發布於 NASA 網站（Evans）
- 報告先送 Earth Science Advisory Committee，再正式轉交政府（Evans）
- AARO 將發表關於「沉入水中」感測器假影案例的調查結果（Kirkpatrick）
- AARO 將在特定區域部署專門打造的感測器進行監視（Kirkpatrick）
- NASA 歡迎 AARO 派駐人員（Pritar）協助科學計畫（Kirkpatrick）
- 額外的問答回覆將發布於 science.nasa.gov（Spergel）

**Longer-Term（持續）：**
- AARO 將在熱點地區進行每次 3 個月的 24/7 收集監測行動（Kirkpatrick）
- AARO 將以已知物體校準 DOD 感測器（在各種條件下飛 F-35 對照氣象氣球）（Kirkpatrick）
- AARO 將為案例持有開發 AI/ML 分析（Kirkpatrick）
- 建立 Five Eyes 以外的國際科學夥伴關係（Kirkpatrick、Gold）
- 開發公民科學群眾外包平台（Bianco、Spergel）
- NASA 在收到小組建議後決定預算分配（Evans）

**Open Questions（被提出但未解決）：**
- 小組範圍是否納入水下／太空領域，或維持聚焦於空中（小組辯論）
- 如何為科學目的精確定義「anomalous」（Drake、Kirkpatrick 的討論）
- 如何收集 FAA 原始雷達資料而非僅處理／過濾過的資料（Reggie 建議；Freie 指出「可行但並非毫無技術挑戰」）
- 如何把群眾外包平台連結到即時的後續觀測（Bianco 討論）
- NASA 是否會設立具專屬經費的正式 UAP 計畫（Evans：「現在說還太早」）

## Grading Criteria

- [ ] 已建立輸出檔案 `next_steps.md`
- [ ] 提及小組最終報告的時程（夏季／7 月底）
- [ ] 提及 AARO 年度報告須於 August 1 前提交
- [ ] 提及 AARO 感測器部署計畫
- [ ] 提及 Five Eyes 資料共享
- [ ] 註記預算／計畫狀態（尚未設立正式計畫）
- [ ] 至少辨識出一項 open question
- [ ] 項目依時間範圍組織
- [ ] 至少為 5 項辨識出負責方
- [ ] 包含時間軸視覺化或里程碑摘要

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the next steps extraction task.

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

    report_path = workspace / "next_steps.md"
    if not report_path.exists():
        alternatives = ["action_items.md", "follow_up.md", "followup.md", "actions.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "final_report_timeline": 0.0,
            "aaro_annual_report": 0.0,
            "sensor_deployment": 0.0,
            "five_eyes": 0.0,
            "budget_status": 0.0,
            "open_questions": 0.0,
            "timeframe_org": 0.0,
            "responsible_parties": 0.0,
            "timeline_viz": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Final report timeline
    report_patterns = [r'final\s+report', r'report.*summer|summer.*report', r'end\s+of\s+july|july', r'publish.*website']
    scores["final_report_timeline"] = 1.0 if sum(bool(re.search(p, content_lower)) for p in report_patterns) >= 2 else (0.5 if any(re.search(p, content_lower) for p in report_patterns) else 0.0)

    # AARO annual report
    aaro_report_patterns = [r'aaro.*annual\s+report|annual\s+report.*aaro', r'august\s+1|august\s+first', r'report.*congress|congress.*report']
    scores["aaro_annual_report"] = 1.0 if sum(bool(re.search(p, content_lower)) for p in aaro_report_patterns) >= 1 else 0.0

    # Sensor deployment
    sensor_patterns = [r'purpose.built\s+sensor', r'dedicated\s+sensor', r'deploy.*sensor|sensor.*deploy', r'surveillance.*area|hotspot']
    scores["sensor_deployment"] = 1.0 if sum(bool(re.search(p, content_lower)) for p in sensor_patterns) >= 1 else 0.0

    # Five Eyes
    five_patterns = [r'five\s+eyes', r'uk.*canada.*australia', r'intelligence.*partner|partner.*intelligence']
    scores["five_eyes"] = 1.0 if any(re.search(p, content_lower) for p in five_patterns) else 0.0

    # Budget status
    budget_patterns = [r'no\s+(?:associated\s+)?(?:programmatic\s+)?fund', r'not\s+established\s+a\s+program', r'no\s+formal\s+(?:program|budget)', r'too\s+early\s+to\s+say', r'budget.*complex|complex.*budget']
    scores["budget_status"] = 1.0 if sum(bool(re.search(p, content_lower)) for p in budget_patterns) >= 1 else (0.5 if re.search(r'budget|fund', content_lower) else 0.0)

    # Open questions
    open_patterns = [r'open\s+question', r'unresolved', r'unclear|undefined', r'debate|debated', r'tbd|to\s+be\s+determined']
    has_open = any(re.search(p, content_lower) for p in open_patterns)
    # Also check for content about scope debate or definition of anomalous
    has_scope = bool(re.search(r'scope.*aerial.*anomalous|aerial.*anomalous.*scope|domain.*debate', content_lower))
    has_definition = bool(re.search(r'defin.*anomalous|anomalous.*defin', content_lower))
    scores["open_questions"] = 1.0 if has_open and (has_scope or has_definition) else (0.5 if has_open else 0.0)

    # Timeframe organization
    time_patterns = [r'immediate', r'short.term', r'near.term', r'long.term', r'ongoing', r'weeks', r'months', r'years']
    time_count = sum(1 for p in time_patterns if re.search(p, content_lower))
    scores["timeframe_org"] = 1.0 if time_count >= 3 else (0.5 if time_count >= 2 else 0.0)

    # Responsible parties
    parties = set()
    for party in ['nasa', 'aaro', 'panel', 'faa', 'congress', 'kirkpatrick', 'spergel', 'evans', 'department']:
        if party in content_lower:
            parties.add(party)
    scores["responsible_parties"] = 1.0 if len(parties) >= 5 else (0.5 if len(parties) >= 3 else 0.0)

    # Timeline visualization
    viz_patterns = [r'timeline', r'milestone', r'gantt', r'roadmap', r'schedule']
    has_viz = any(re.search(p, content_lower) for p in viz_patterns)
    has_dates = len(re.findall(r'(?:july|august|summer|2023|q[1-4])', content_lower)) >= 2
    scores["timeline_viz"] = 1.0 if has_viz and has_dates else (0.5 if has_viz or has_dates else 0.0)

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

### 評分項 1：行動項目完整性（權重 30%）

**1.0 分**：擷取出至少 12 項不同的後續步驟／行動項目，橫跨所有時間範圍。同時包含已承諾的交付項目（小組報告、AARO 年度報告）與抱負性目標（群眾外包平台、國際夥伴關係）。沒有遺漏主要項目。

**0.75 分**：8-11 項，橫跨多個時間範圍。

**0.5 分**：5-7 項，但漏掉部分時間範圍。

**0.25 分**：少於 5 項。

**0.0 分**：未擷取任何行動項目。

### 評分項 2：時程與具體性（權重 25%）

**1.0 分**：在有提及之處註記具體時程（August 1、end of July、「this summer」）。清楚區分有確切期限的項目、時機模糊者與持續性努力。負責方歸屬準確。

**0.75 分**：時程細節良好，僅有少許缺漏。

**0.5 分**：註記了一些時程，但缺少具體細節。

**0.25 分**：通篇時機模糊。

**0.0 分**：沒有時程資訊。

### 評分項 3：未解問題與缺口（權重 25%）

**1.0 分**：辨識出未解議題，包括：範圍界定（空中 vs. 異常）、「anomalous」的定義、預算承諾、原始資料收集可行性，以及群眾外包的實作細節。注意到研究建議與行動承諾之間的落差。

**0.75 分**：辨識出多數未解問題。

**0.5 分**：註記了一些未解問題。

**0.25 分**：未解問題很少或沒有。

**0.0 分**：缺少未解問題區段。

### 評分項 4：組織與視覺化（權重 20%）

**1.0 分**：依時間範圍良好組織，區段清楚。包含時間軸視覺化或里程碑摘要，使時間關係一目了然。便於作為參考文件追蹤。

**0.75 分**：組織良好，附基本時間軸。

**0.5 分**：依時間範圍組織，但沒有視覺化。

**0.25 分**：組織不佳。

**0.0 分**：沒有組織。
