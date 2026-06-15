---
id: task_market_research
name: 台灣產業市場研究
category: research
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
region: TW
source_task_id: task_market_research
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: manual_review_only
claw_eval_tw_id: T011tw_market_research
workspace_files: []
---

# 台灣產業市場研究

## Prompt

請針對**台灣電動車（EV）市場**這個產業區隔，撰寫一份市場研究與競爭態勢分析。
請找出台灣市場上的前 5 大業者（例如整車品牌、充電營運商或相關供應鏈業者）、
其關鍵差異化優勢、市場趨勢，以及常見的商業／定價模式。市場規模與金額請以
**新臺幣（NT$）**計。

**重要：你必須將報告儲存為一個檔名精確為 `market_research.md` 的檔案，且位於
目前的工作目錄中。** 不要只把報告輸出在你的回應裡——檔案必須實際寫入磁碟。
檔名必須精確一致（不可為 `market-research.md`，也不可放在子目錄中）。

請依各業者分段組織報告，並附上一份摘要比較表格。

請使用網路搜尋工具蒐集最新資訊。注意：這是即時資料，請對市場數據與業者資訊
**標示資料來源、標示查詢日期**，並在報告中說明**資料限制與不確定性**（例如
市場規模估算的來源差異、統計年度）。切勿捏造或寫死特定市佔率或金額。

## Expected Behavior

助手應該：

1. 找出台灣電動車市場的主要業者（整車品牌、充電營運商、相關供應鏈等）
2. 為每位業者記錄：
   - 公司概況與在台市場地位
   - 關鍵產品或服務差異化優勢
   - 常見的商業／定價模式（以新臺幣計）
   - 顯著的優勢與劣勢
3. 找出整體市場趨勢（政策補助、充電基礎建設、國產化、市場成長等）
4. 建立一份條理分明的 Markdown 報告，包含執行摘要、各業者側寫、比較表格與
   市場趨勢章節

這份報告應讀起來像商業分析師為策略會議所準備的內容。因為是即時資料，正確
行為是**標示資料來源、標示查詢日期，並說明資料限制與不確定性**（市場規模與
市佔率隨來源與年度而異），而非捏造或寫死特定數值。

## Grading Criteria

- [ ] 已建立檔案 market_research.md
- [ ] 報告至少找出 5 位台灣電動車市場相關業者
- [ ] 每位業者皆有具實質內容的側寫（不只是列出名稱）
- [ ] 報告包含一份比較表格或矩陣
- [ ] 報告涵蓋業者的商業／定價模式（以新臺幣計）
- [ ] 報告探討當前台灣市場趨勢
- [ ] 標示資料來源與查詢日期，並說明資料限制與不確定性
- [ ] 報告結構清楚，具有標題與章節
- [ ] 包含執行摘要或前言
- [ ] 寫作品質專業且具分析性

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the market research task based on file creation and structural content.

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

    report_file = workspace / "market_research.md"

    if not report_file.exists():
        return {
            "file_created": 0.0,
            "competitors_identified": 0.0,
            "has_comparison_table": 0.0,
            "has_pricing_info": 0.0,
            "has_trends_section": 0.0,
            "has_structure": 0.0,
            "has_executive_summary": 0.0,
            "used_web_search": 0.0,
        }

    scores["file_created"] = 1.0
    content = report_file.read_text()
    content_lower = content.lower()

    # Check for known APM/observability competitors
    known_competitors = [
        "datadog", "new relic", "dynatrace", "splunk", "grafana",
        "elastic", "appdynamics", "honeycomb", "lightstep", "sumo logic",
        "instana", "sentry", "chronosphere", "logz.io", "coralogix",
        "signoz", "observe inc", "mezmo",
    ]
    found_competitors = [c for c in known_competitors if c in content_lower]

    if len(found_competitors) >= 5:
        scores["competitors_identified"] = 1.0
    elif len(found_competitors) >= 3:
        scores["competitors_identified"] = 0.5
    elif len(found_competitors) >= 1:
        scores["competitors_identified"] = 0.25
    else:
        scores["competitors_identified"] = 0.0

    # Check for comparison table (markdown table syntax)
    table_patterns = [
        r'\|.*\|.*\|',  # Markdown table rows
        r'\|[\s-]+\|',  # Table separator row
    ]
    has_table = all(re.search(p, content) for p in table_patterns)
    scores["has_comparison_table"] = 1.0 if has_table else 0.0

    # Check for pricing information
    pricing_patterns = [
        r'pric(e|ing|ed)',
        r'per[\s-]?(host|gb|user|seat|node|core)',
        r'free\s+tier',
        r'subscription',
        r'\$\d+',
        r'cost',
    ]
    pricing_matches = sum(1 for p in pricing_patterns if re.search(p, content_lower))
    if pricing_matches >= 3:
        scores["has_pricing_info"] = 1.0
    elif pricing_matches >= 1:
        scores["has_pricing_info"] = 0.5
    else:
        scores["has_pricing_info"] = 0.0

    # Check for market trends section
    trends_patterns = [
        r'trend', r'market\s+(direction|shift|movement|growth)',
        r'opentelemetry', r'otel',
        r'ai[\s/]ml', r'artificial intelligence', r'machine learning',
        r'consolidat', r'cloud[\s-]native',
    ]
    trends_matches = sum(1 for p in trends_patterns if re.search(p, content_lower))
    if trends_matches >= 3:
        scores["has_trends_section"] = 1.0
    elif trends_matches >= 1:
        scores["has_trends_section"] = 0.5
    else:
        scores["has_trends_section"] = 0.0

    # Check for document structure (headings)
    headings = re.findall(r'^#{1,3}\s+.+', content, re.MULTILINE)
    if len(headings) >= 6:
        scores["has_structure"] = 1.0
    elif len(headings) >= 3:
        scores["has_structure"] = 0.5
    else:
        scores["has_structure"] = 0.0

    # Check for executive summary / introduction
    summary_patterns = [
        r'(executive\s+summary|overview|introduction)',
    ]
    if any(re.search(p, content_lower) for p in summary_patterns):
        scores["has_executive_summary"] = 1.0
    else:
        scores["has_executive_summary"] = 0.0

    # Check transcript for web search tool usage
    used_search = False
    for event in transcript:
        if event.get("type") != "message":
            continue
        msg = event.get("message", {})
        if msg.get("role") == "assistant":
            for item in msg.get("content", []):
                if item.get("type") == "toolCall":
                    tool_name = item.get("name", "").lower()
                    params = item.get("arguments", item.get("params", {}))
                    # Check for web search / fetch tools
                    if any(t in tool_name for t in [
                        "web_search", "websearch", "search",
                        "web_fetch", "webfetch", "fetch",
                        "browse", "http",
                    ]):
                        used_search = True
                    # Also check execute_command for curl/wget
                    if tool_name in ["execute_command", "executecommand"]:
                        cmd = params.get("command", "").lower()
                        if any(t in cmd for t in ["curl", "wget", "web"]):
                            used_search = True

    scores["used_web_search"] = 1.0 if used_search else 0.0

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

### 評分項 1：研究深度與正確性（權重 30%）

**1.0 分**：報告對每位業者皆有具體、正確的資訊。細節超越表面描述——包含具體
的產品／服務名稱、特定功能與在台市場定位。資訊明顯來自網路搜尋且為最新。

**0.75 分**：報告對多數業者皆有良好細節與具體資訊，但少數側寫顯得單薄或依賴
籠統描述。

**0.5 分**：報告以表面層次涵蓋各業者。資訊大致正確，但缺乏具體性或深度。

**0.25 分**：報告對業者的著墨極少。資訊顯得籠統或可能不準確。

**0.0 分**：缺少報告、無實質的市場分析，或含有明顯不正確的資訊。

### 評分項 2：分析品質（權重 20%）

**1.0 分**：報告讀起來像專業的市場分析。包含具意義的比較、指出策略定位差異，
並對台灣電動車競爭態勢提出具洞見的結論。執行摘要有效提煉出關鍵要點。

**0.75 分**：報告提供良好的分析，有合理的比較與部分策略洞見，但結論可加強。

**0.5 分**：報告呈現了資訊，但缺乏強有力的分析框架，較像事實清單。

**0.25 分**：報告多為原始資料堆砌，少有分析或綜整。

**0.0 分**：無任何分析內容。

### 評分項 3：來源、查詢日期與不確定性（權重 20%）

**1.0 分**：市場規模、市佔率與業者資訊皆標示可追溯的資料來源，明確標示查詢
日期，並說明資料限制與不確定性（例如不同來源的市場規模估算差異、統計年度、
新臺幣換算基礎）。明顯以引用來源取代捏造或寫死的數值。

**0.75 分**：多數關鍵數據有標示來源並標示查詢日期，對不確定性有提及但較簡略。

**0.5 分**：有標示部分來源或查詢日期，但不一致，或未說明資料限制。

**0.25 分**：僅零星提及來源或日期，未說明不確定性。

**0.0 分**：完全未標示來源或查詢日期，或出現捏造／寫死且未加註的市佔率或金額。

### 評分項 4：市場趨勢與脈絡（權重 15%）

**1.0 分**：報告找出並探討多項相關的台灣市場趨勢（例如政府補助政策、充電基礎
建設布建、國產化、市場成長率、消費者偏好轉變），並與競爭動態相互連結。

**0.75 分**：報告探討數項市場趨勢並有合理脈絡，但與競爭影響的連結較為有限。

**0.5 分**：報告提及趨勢，但僅止於表面，或遺漏了重要的當前趨勢。

**0.25 分**：趨勢著墨極少或流於籠統。

**0.0 分**：未探討任何市場趨勢。

### 評分項 5：結構、定價與呈現（權重 15%）

**1.0 分**：報告組織極佳，有實用的比較表格與專業的 Markdown 排版，並為各業者
提供以新臺幣計的具體商業／定價模式細節。易於瀏覽並擷取關鍵資訊。

**0.75 分**：報告組織良好、排版佳，涵蓋多數業者的定價模式並有合理具體性。

**0.5 分**：報告具備基本結構，但排版不一致，或定價／比較表格等關鍵元素缺漏。

**0.25 分**：報告組織不佳，定價幾乎未提及。

**0.0 分**：報告無可辨識的結構，且未包含任何定價資訊。
