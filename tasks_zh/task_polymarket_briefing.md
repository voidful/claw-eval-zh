---
id: task_polymarket_briefing
name: Polymarket + 新聞簡報
category: research
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_polymarket_briefing
source_benchmark: pinchbench
claw_eval_id: P012zh_polymarket_briefing
workspace_files: []
---

# Polymarket + 新聞簡報

## Prompt

請抓取 Polymarket（polymarket.com）目前最熱門的 3 個預測市場（prediction
markets）。針對每個市場，找出一則近期相關的新聞報導（過去 48 小時內），用來
說明人們為何在此下注。

請將結果儲存為 `polymarket_briefing.md`，格式如下：

```
# Polymarket Briefing — {today's date}

## 1. {Market Question}
**Current odds:** Yes {X}% / No {Y}%
**Related news:** {1-2 sentence summary of a real news story that contextualizes this market}

## 2. {Market Question}
**Current odds:** Yes {X}% / No {Y}%
**Related news:** {1-2 sentence summary}

## 3. {Market Question}
**Current odds:** Yes {X}% / No {Y}%
**Related news:** {1-2 sentence summary}
```

只能使用真實、目前有效運作的市場。不可捏造市場或賠率。

## Expected Behavior

助手應該：
1. 使用 Polymarket API（`https://gamma-api.polymarket.com/markets?active=true&order=volumeNum&ascending=false&limit=10`）
   或瀏覽 polymarket.com，抓取熱門／有效運作的市場
2. 依交易量選出 3 個最活躍／最熱門的市場
3. 針對每個市場，搜尋一則過去 48 小時內發布的相關新聞報導
4. 將輸出排版並儲存至 `polymarket_briefing.md`

助手不可虛構（hallucinate）市場資料。若 API 無法使用，應註明此情況並嘗試替代
做法（例如以網路搜尋「polymarket trending markets today」）。

## Grading Criteria

- [ ] 已在工作區建立 polymarket_briefing.md
- [ ] 檔案標頭包含今天的日期
- [ ] 恰好有 3 個市場區段（若市場無法取得，可較少並加註說明）
- [ ] 每個市場皆有問題、賠率（Yes/No 百分比）與相關新聞
- [ ] 賠率以百分比格式呈現，且加總約為 100%
- [ ] 相關新聞摘要為 1～3 句，且看起來符合事實
- [ ] 市場問題看起來是真實的預測市場題目
- [ ] 格式符合所要求的 markdown 結構

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    from datetime import date

    scores = {}
    workspace = Path(workspace_path)
    briefing_file = workspace / "polymarket_briefing.md"

    if not briefing_file.exists():
        return {
            "file_created": 0.0,
            "has_date_header": 0.0,
            "has_three_markets": 0.0,
            "has_odds": 0.0,
            "has_news_summaries": 0.0,
            "correct_format": 0.0,
        }

    scores["file_created"] = 1.0
    content = briefing_file.read_text()

    # Check date header
    year = date.today().strftime("%Y")
    has_date = year in content and "# Polymarket Briefing" in content
    scores["has_date_header"] = 1.0 if has_date else 0.0

    # Check for 3 market sections (## 1., ## 2., ## 3.)
    market_headers = re.findall(r'^## \d+\.', content, re.MULTILINE)
    count = len(market_headers)
    scores["has_three_markets"] = 1.0 if count >= 3 else (0.5 if count >= 2 else 0.0)

    # Check for odds pattern (XX% format)
    odds_matches = re.findall(r'\d{1,3}%', content)
    scores["has_odds"] = 1.0 if len(odds_matches) >= 6 else (0.5 if len(odds_matches) >= 3 else 0.0)

    # Check for related news sections with content
    news_sections = re.findall(r'\*\*Related news:\*\*\s*(.+)', content)
    valid_news = [n for n in news_sections if len(n.split()) >= 5]
    scores["has_news_summaries"] = 1.0 if len(valid_news) >= 3 else (0.5 if len(valid_news) >= 2 else 0.0)

    # Check overall format
    has_header = content.strip().startswith("# Polymarket Briefing")
    has_current_odds = "Current odds:" in content
    scores["correct_format"] = 1.0 if has_header and has_current_odds else 0.5

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

### 評分項 1：資料真實性（權重 45%）

**1.0 分**：3 個市場皆為真實、目前有效運作的 Polymarket 預測市場。賠率合理
（加總接近 100%，無在缺乏脈絡下出現的極端值）。無捏造的市場或賠率。
**0.75 分**：市場看似真實，但賠率可能略為過時，或有一個市場無法查證。
**0.5 分**：部分市場看似合理，但有一個看似虛構，或賠率不合理（例如不論題目為何
皆為 50/50）。
**0.25 分**：多個市場看似捏造，或賠率呈現明顯的虛構模式（全為剛好 50%、出現不可能
的數值）。
**0.0 分**：所有市場明顯為虛構，或助手拒絕產出內容。

### 評分項 2：新聞相關性（權重 35%）

**1.0 分**：每則相關新聞都直接說明該市場為何活躍。新聞合理且近期。新聞事件與預測
市場問題之間連結清楚。
**0.75 分**：新聞大致相關，僅有小幅不符，或新聞稍嫌過時。
**0.5 分**：新聞與市場主題有些相關，但未清楚說明當前賠率或活躍程度。
**0.25 分**：新聞籠統，或與特定市場問題僅有鬆散連結。
**0.0 分**：無新聞、新聞完全不相關，或明顯為捏造的事件。

### 評分項 3：格式符合度（權重 20%）

**1.0 分**：檔案完全符合要求格式：日期標頭、3 個編號區段、欄位標籤以粗體呈現、
百分比賠率、新聞摘要。
**0.75 分**：有小幅偏差（例如百分比格式略有不同、多餘空白）。
**0.5 分**：結構可辨識，但有明顯偏差（例如缺少賠率、區段合併）。
**0.25 分**：有內容，但多半未排版。
**0.0 分**：檔案為空，或無任何預測市場內容。
