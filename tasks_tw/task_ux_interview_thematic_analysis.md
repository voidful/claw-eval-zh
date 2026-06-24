---
id: task_ux_interview_thematic_analysis
name: "UX 訪談逐字稿主題分析"
category: txt_analysis
difficulty: medium
timeout_seconds: 300
workspace_files:
  - source: tw/txt/ux_interview_transcripts.txt
    dest: ux_interview_transcripts.txt
grading_weights:
  automated: 0.5
  llm_judge: 0.5
grading_type: hybrid
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v2
---
## Prompt

分析 `ux_interview_transcripts.txt`（10 位用戶對 PocketPay 行動支付 App 的訪談逐字稿），進行質性研究分析，輸出 `ux_research_report.md`：

1. **主題編碼**：從訪談中識別出 5~8 個主要主題（如「付款速度問題」「點數回饋價值」「安全感需求」等），標記每個主題在哪些受訪者（P01~P10）中出現
2. **情感分析**：對每位受訪者計算整體情感分數（-5 到 +5）；正面詞彙（方便/好用/推薦/喜歡/滿意/順暢 等）+1，負面詞彙（麻煩/難用/困惑/失望/複雜/卡住 等）-1
3. **功能優先級矩陣**：統計各功能被提及次數（快速付款/點數回饋/交易記錄/分期付款等），計算「優先級分數」= 提及次數 × 平均情感方向（提到某功能時是正面還是負面語境）
4. **用戶 Persona**：根據訪談歸納 3 個典型用戶角色（如「高頻輕鬆派」「謹慎安全派」「痛點敏感派」），每個 Persona 含代表性受訪者、主要需求、關鍵痛點
5. **NPS 分析**：從訪談中找出每位受訪者的 NPS 評分（0-10），計算整體 NPS = %推薦者(9-10) - %反對者(0-6)

## Expected Behavior

LLM 應完整閱讀 `ux_interview_transcripts.txt`，識別 10 位受訪者（P01~P10）的訪談段落，依序執行主題編碼、情感計算、功能統計、Persona 建構和 NPS 計算，最終輸出 `ux_research_report.md`，包含至少 2 個 Markdown 表格（主題×受訪者矩陣、功能優先級）以及每個 Persona 的結構化描述，所有量化結果須有訪談原文依據。

## Grading Criteria

10 個評分 key，每個 key 通過得 1 分，滿分 10 分（automated score = 通過數 / 10）。

| Key | 說明 |
|-----|------|
| `report_created` | `ux_research_report.md` 檔案存在 |
| `themes_identified` | 報告中有 5 個以上的主題名稱（有特定主題標籤，非泛稱）|
| `participants_mapped` | P01~P10 至少 8 個出現（代表受訪者對應已完成）|
| `sentiment_scores` | 報告中有 -5 到 +5 範圍的情感分數數字（含負數）|
| `feature_frequency` | 報告中有功能名稱搭配次數數字 |
| `priority_matrix` | 報告中出現「優先級」「優先順序」或「priority」相關概念 |
| `persona_count` | 報告中有 3 個 Persona（以 Persona 1/2/3 或具體命名出現）|
| `nps_calculated` | 報告中有 NPS 數值（可為正/負整數，如 NPS = 20 或 NPS: -10）|
| `qualitative_insight` | 報告中有超越計數的質性洞察段落（含引用原文或具體情境描述）|
| `has_tables` | Markdown 表格（`\|...\|` 格式）出現 >= 2 個 |


- [ ] ux_research_report.md 檔案存在
- [ ] 報告中有 5 個以上的主題名稱（有特定主題標籤，非泛稱）
- [ ] P01~P10 至少 8 個出現（代表受訪者對應已完成）
- [ ] 報告中有 -5 到 +5 範圍的情感分數數字（含負數）
- [ ] 報告中有功能名稱搭配次數數字
- [ ] 報告中出現「優先級」「優先順序」或「priority」相關概念
- [ ] 報告中有 3 個 Persona（以 Persona 1/2/3 或具體命名出現）
- [ ] 報告中有 NPS 數值（可為正/負整數，如 NPS = 20 或 NPS: -10）
- [ ] 報告中有超越計數的質性洞察段落（含引用原文或具體情境描述）
- [ ] 格式）出現 >= 2 個
## Automated Checks

```python
import re
from pathlib import Path


def grade(transcript: list, workspace_dir: str) -> dict[str, bool]:
    report_path = Path(workspace_dir) / "ux_research_report.md"

    results = {
        "report_created": False,
        "themes_identified": False,
        "participants_mapped": False,
        "sentiment_scores": False,
        "feature_frequency": False,
        "priority_matrix": False,
        "persona_count": False,
        "nps_calculated": False,
        "qualitative_insight": False,
        "has_tables": False,
    }

    if not report_path.exists():
        return results

    results["report_created"] = True
    text = report_path.read_text(encoding="utf-8", errors="ignore")

    # themes_identified: 主題標籤（特定名稱）出現 >= 5 個
    # 方法：找「主題」「Theme」後面跟的具體名稱，或標題行含「主題」
    theme_patterns = [
        r"(?:主題|Theme)\s*\d+\s*[：:]\s*\S+",
        r"#{1,4}\s*(?:主題|Theme)[^\n]+",
        r"\*\*(?:主題|Theme)[^\*]+\*\*",
    ]
    theme_count = 0
    for p in theme_patterns:
        theme_count += len(re.findall(p, text, re.IGNORECASE))
    # 常見主題關鍵詞計數（至少 5 個不同主題詞出現）
    theme_keywords = [
        "付款速度", "點數回饋", "安全感", "操作流程", "介面設計",
        "客服支援", "交易記錄", "分期付款", "通知設定", "隱私",
        "載入時間", "錯誤處理", "優惠活動", "跨平台", "綁定",
    ]
    keyword_hits = sum(1 for kw in theme_keywords if kw in text)
    results["themes_identified"] = theme_count >= 5 or keyword_hits >= 5

    # participants_mapped: P01~P10 至少 8 個出現
    participants_found = set(re.findall(r"P0?([1-9]|10)\b", text))
    results["participants_mapped"] = len(participants_found) >= 8

    # sentiment_scores: 含負數或正數情感分數
    sentiment_match = re.search(
        r"(?:情感分數|sentiment\s*score|情緒分數)[^\n]{0,60}[+-]?\d+(?:\.\d+)?",
        text,
        re.IGNORECASE,
    )
    if not sentiment_match:
        # 表格中的情感分數（-5~+5 範圍，含負號）
        sentiment_match = re.search(r"[+-][1-5](?:\.\d)?\b", text)
    if not sentiment_match:
        # 數字直接出現且範圍合理（-5 到 +5）
        neg_score = re.search(r"(?:^|\s)-[1-5](?:\.\d)?(?:\s|$)", text, re.MULTILINE)
        pos_score = re.search(r"(?:^|\s)\+?[1-5](?:\.\d)?(?:\s|$)", text, re.MULTILINE)
        sentiment_match = neg_score or pos_score
    results["sentiment_scores"] = sentiment_match is not None

    # feature_frequency: 功能名稱 + 次數數字
    feature_match = re.search(
        r"(?:快速付款|點數回饋|交易記錄|分期付款|快捷支付|掃碼|通知|客服)[^\n]{0,40}(?:\d+\s*次|次數[^\n]{0,10}\d+)",
        text,
    )
    if not feature_match:
        feature_match = re.search(
            r"(?:\d+\s*次)[^\n]{0,40}(?:快速付款|點數回饋|交易記錄|分期付款|掃碼|通知)",
            text,
        )
    if not feature_match:
        # 表格中功能 + 數字
        feature_match = re.search(
            r"^\s*\|[^\|]*(?:付款|回饋|記錄|分期|掃碼)[^\|]*\|[^\|]*\d+[^\|]*\|",
            text,
            re.MULTILINE,
        )
    results["feature_frequency"] = feature_match is not None

    # priority_matrix: 優先級概念
    priority_match = re.search(
        r"(?:優先級|優先順序|priority\s*(?:score|matrix|分數|矩陣))",
        text,
        re.IGNORECASE,
    )
    results["priority_matrix"] = priority_match is not None

    # persona_count: 3 個 Persona
    persona_patterns = [
        r"Persona\s*[123一二三]",
        r"(?:用戶角色|使用者角色)\s*[123一二三]",
        r"#{1,4}[^\n]*(?:Persona|角色|用戶類型)[^\n]*[123一二三派型]",
        r"\*\*[^\*]*(?:派|型|者|族)[^\*]*\*\*",
    ]
    persona_count = 0
    for p in persona_patterns:
        persona_count += len(re.findall(p, text, re.IGNORECASE))
    # 若用具體命名（如「高頻輕鬆派」）也算
    named_persona = re.findall(r"(?:高頻|謹慎|痛點|輕鬆|安全|敏感)[^\n]{0,10}(?:派|型|用戶|者)", text)
    results["persona_count"] = persona_count >= 3 or len(set(named_persona)) >= 3

    # nps_calculated: NPS 數值
    nps_match = re.search(
        r"NPS\s*[=:＝]\s*[+-]?\s*\d+",
        text,
        re.IGNORECASE,
    )
    if not nps_match:
        nps_match = re.search(r"(?:整體\s*)?NPS[^\n]{0,30}[+-]?\d+", text, re.IGNORECASE)
    results["nps_calculated"] = nps_match is not None

    # qualitative_insight: 質性洞察（引用原文或情境描述）
    insight_patterns = [
        r"「[^」]{10,}」",       # 引號引用（至少10字）
        r'[\u201c][^\u201d]{10,}[\u201d]',  # 英文引號（"..."）
        r"(?:受訪者|P0?\d+)\s*(?:提到|表示|指出|說)[^。\n]{10,}",
        r"(?:洞察|insight|發現|observation)[^：:\n]{0,10}[：:][^\n]{15,}",
    ]
    insight_count = sum(
        1 for p in insight_patterns if re.search(p, text, re.IGNORECASE)
    )
    results["qualitative_insight"] = insight_count >= 2

    # has_tables: 獨立表格數量 >= 2
    table_count = 0
    in_table = False
    for line in text.split("\n"):
        if re.match(r"\s*\|.+\|", line):
            if not in_table:
                table_count += 1
                in_table = True
        else:
            in_table = False
    results["has_tables"] = table_count >= 2

    return results


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

請依照以下四個維度對報告進行評分，各維度分數為 0~100，最終加權得分作為 LLM Judge 分數。

| 維度 | 權重 | 評分說明 |
|------|------|----------|
| **Thematic Coding Quality** | 35% | 識別的主題是否真實反映訪談內容（非隨意命名）；每個主題是否有訪談片段作為依據；主題間是否有足夠區分度（非過度重疊）；P01~P10 的主題對應是否有訪談原文支撐 |
| **Sentiment & Quantification** | 25% | 情感詞彙計算規則是否一致（正負詞彙定義明確）；功能提及次數統計是否合理；優先級分數計算是否有明確公式（次數 × 情感方向）；NPS 計算是否正確（推薦者% - 反對者%）|
| **Persona Design** | 25% | 3 個 Persona 是否有足夠差異性（非重複）；每個 Persona 是否有代表性受訪者、主要需求、關鍵痛點三要素；Persona 是否基於訪談資料（非泛型描述）；Persona 命名是否有記憶點 |
| **Report Usability** | 15% | 報告格式是否能直接用於產品決策會議；主題編碼矩陣是否清晰（受訪者 × 主題）；功能優先級建議是否具體（如「應優先改善 X 功能，因為 Y 個用戶有負面體驗」）；洞察是否超越數字層次 |

**評分指引**：
- 90~100：主題編碼有訪談原文依據，情感計算一致，3 Persona 有強差異性，NPS 正確，報告可立即用於產品規劃
- 70~89：主題基本準確，量化計算合理，Persona 有一定差異但部分描述偏泛型
- 50~69：主題識別過於粗略或與訪談脫節，或 Persona 設計缺乏訪談支持
- 30~49：多個核心分析缺失（如無功能統計、無 NPS、無情感分數）
- 0~29：報告嚴重不完整，基本未進行質性分析

## Additional Notes

- 情感分數範圍限定在 -5 到 +5（若詞彙計數超出，截斷到邊界值）。
- 若逐字稿中未明確詢問 NPS，應根據受訪者言語傾向推估（並標注為估計值）。
- 主題應命名為有意義的描述性短語（如「付款流程摩擦點」），避免純編號。
- 功能優先級矩陣的「情感方向」：正面語境計 +1，負面語境計 -1，中性計 0；取平均後乘以次數。
- Persona 至少包含：名稱（有記憶點的標籤）、代表受訪者（如 P03, P07）、核心需求（1~2 句）、關鍵痛點（1~2 句）、對 PocketPay 的整體態度。
