---
id: task_meeting_council_upcoming
name: 南港市議會逐字稿 — 擷取後續事件與截止期限
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_upcoming
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T112tw_meeting_council_upcoming
workspace_files:
- source: tw/meetings/tw_council_meeting.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 南港市議會逐字稿 — 擷取後續事件與截止期限

## Prompt

工作區裡有一份議會逐字稿 transcript.md（虛構的台灣地方議會「南港市議會」第 12 屆
第 3 次定期會，2026 年 4 月 2 日召開，時區 Asia/Taipei）。請以台灣地方議會的語境
閱讀逐字稿，產生 upcoming_events.md，依**時間先後**列出所有後續事件、截止期限與
未來日期。

每一筆請包含：日期、事件內容、負責方（承辦單位／議員／委員會），以及狀態
（已確認 confirmed／已排定／預定 tentative／依條例）。最後請以一個
**「值得關注（What to watch）」**重點區段作結。

## Expected Behavior

助手應讀取 transcript.md（特別是第六節「後續議程與重要日期」），擷取下列後續事件
並依時間先後整理到 upcoming_events.md：
- 4 月 16 日（次會）：退輔諮詢委員會設置條例續審；第二十六至二十八案二讀／續審；
  天然氣和解金 NT$65 萬元 經費重新分配案。
- 4 月 20 日：東港里里民座談會（Town Hall），地點 福橡活動中心。
- 5 月 7 日：議員利益衝突暨倫理自律報告提報；土地使用管理自治條例（土管自治條例）
  修正進度報告。
- 5 月 15 日：第 24 號消防分隊 GMP（工程上限價）核定。
- 8 月 3 日、8 月 10 日、8 月 17 日：民國 116 年度（2027 年度）總預算編列工作坊三場。
- 2027 年 3 月 1 日：自來水及污水容量費新費率開始實施。
- 2027 年 9 月：第 24 號消防分隊完工。
- 2028 年 9 月：羅馬倉庫園區第四期（Phase 4）完工。
- 2030 年 3 月：容量費三階段調整全面到位。
- 下週：大眾捷運董事會（南港捷運董事會）開會。
- 約 60 天內：羅馬倉庫園區土地交割（closing）完成。
並以「值得關注」重點區段標出最關鍵的幾項（如 4 月 16 日次會、5 月 15 日消防分隊
GMP、8 月三場預算工作坊、2027 年 3 月容量費上路）。

## Grading Criteria

- [ ] 建立報告檔案 upcoming_events.md
- [ ] 辨識 4 月 16 日次會各項目（退輔委員會、第 26-28 案、NT$65 萬和解金）
- [ ] 辨識 4 月 20 日 東港里里民座談會（福橡活動中心）
- [ ] 辨識 5 月 7 日 倫理自律報告與土管自治條例
- [ ] 辨識 5 月 15 日 第 24 號消防分隊 GMP
- [ ] 辨識 8 月三場預算編列工作坊
- [ ] 辨識 2027 年 3 月 容量費新費率上路
- [ ] 辨識 2028 年 9 月 羅馬倉庫園區第四期完工
- [ ] 依時間先後組織
- [ ] 包含『值得關注／重點』區段

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW (fictional) council upcoming-events grader.

    查核項對應原 grader，但事實改由台灣逐字稿（dest=transcript.md）推導，
    再比對 agent 產生的中文報告 upcoming_events.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 找出 agent 報告檔 ---
    report = workspace / "upcoming_events.md"
    if not report.exists():
        for alt in ["events.md", "deadlines.md", "upcoming.md", "timeline.md",
                    "後續事件.md", "後續議程.md", "重要日期.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["report_created", "april_16_items", "april_20_townhall",
            "may_7_ethics", "fire_station_gmp", "budget_workshops",
            "march_2027_fees", "rome_yard_sept2028", "chronological",
            "highlights_section"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態確認「應有事實」確實存在於 transcript（避免硬寫）---
    tx = ""
    tpath = workspace / "transcript.md"
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    def tx_has(*pats):
        # 逐字稿須含全部 pattern，才視為該事實可查核
        return all(re.search(p, tx) for p in pats) if tx else True

    # 1) 4 月 16 日次會：退輔委員會／第 26-28 案／NT$65 萬和解金
    fact = tx_has(r"4\s*月\s*16\s*日")
    ok = bool(re.search(r"4\s*月\s*16\s*日|0?4[/-]16|April\s*16", c)) and bool(
        re.search(r"退輔|退伍軍人|二十[六七八]|26|27|28|65\s*萬|和解金|重新分配", c))
    scores["april_16_items"] = 1.0 if (fact and ok) else 0.0

    # 2) 4 月 20 日：東港里里民座談會／福橡活動中心
    fact = tx_has(r"4\s*月\s*20\s*日", r"東港里", r"福橡")
    ok = bool(re.search(r"4\s*月\s*20\s*日|0?4[/-]20|April\s*20", c)) and bool(
        re.search(r"東港里|里民座談|座談會|Town\s*Hall|福橡", c))
    scores["april_20_townhall"] = 1.0 if (fact and ok) else 0.0

    # 3) 5 月 7 日：倫理自律報告／土管自治條例
    fact = tx_has(r"5\s*月\s*7\s*日", r"倫理")
    ok = bool(re.search(r"5\s*月\s*7\s*日|0?5[/-]7|May\s*7", c)) and bool(
        re.search(r"倫理|利益衝突|自律報告|土管|土地使用管理|LDC", c))
    scores["may_7_ethics"] = 1.0 if (fact and ok) else 0.0

    # 4) 5 月 15 日：第 24 號消防分隊 GMP
    fact = tx_has(r"5\s*月\s*15\s*日", r"24\s*號\s*消防")
    ok = bool(re.search(r"5\s*月\s*15\s*日|0?5[/-]15|May\s*15|GMP|工程上限價", c)) and bool(
        re.search(r"消防分隊|24\s*號消防|第\s*24\s*號|Fire\s*Station|Station\s*24", c))
    scores["fire_station_gmp"] = 1.0 if (fact and ok) else 0.0

    # 5) 8 月三場預算編列工作坊
    fact = tx_has(r"8\s*月\s*3\s*日")
    ok = bool(re.search(r"8\s*月\s*(?:3|10|17)\s*日|0?8[/-](?:3|10|17)|August\s*(?:3|10|17)", c)) and bool(
        re.search(r"預算|工作坊|workshop", c, re.IGNORECASE))
    scores["budget_workshops"] = 1.0 if (fact and ok) else 0.0

    # 6) 2027 年 3 月 1 日：容量費新費率上路
    fact = tx_has(r"2027\s*年\s*3\s*月")
    ok = bool(re.search(r"2027\s*年\s*3\s*月|2027[/-]0?3|March.*2027", c)) and bool(
        re.search(r"容量費|容量接管費|費率|自來水|污水|capacity|fee", c, re.IGNORECASE))
    scores["march_2027_fees"] = 1.0 if (fact and ok) else 0.0

    # 7) 2028 年 9 月：羅馬倉庫園區第四期完工
    fact = tx_has(r"2028\s*年\s*9\s*月", r"羅馬倉庫")
    ok = bool(re.search(r"2028\s*年\s*9\s*月|2028[/-]0?9|(?:September|Sept).*28", c)) and bool(
        re.search(r"羅馬倉庫|園區|第四期|Phase\s*4|完工|completion", c, re.IGNORECASE))
    scores["rome_yard_sept2028"] = 1.0 if (fact and ok) else 0.0

    # 8) 依時間先後（至少出現 4 個不同月份／日期錨點）
    anchors = re.findall(
        r"(?:4\s*月\s*16|4\s*月\s*20|5\s*月\s*7|5\s*月\s*15|8\s*月\s*3|8\s*月\s*10|8\s*月\s*17|2027|2028|2030)",
        c)
    scores["chronological"] = 1.0 if len(set(anchors)) >= 4 else 0.0

    # 9) 重點／值得關注區段
    scores["highlights_section"] = 1.0 if re.search(
        r"值得關注|重點|關注重點|What\s*to\s*watch|提醒|留意|focus|watch|highlight",
        c, re.IGNORECASE) else 0.0

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

### 評分項 1：完整度（權重 35%）
- 1.0：列出 10 項以上後續事件
- 0.75：列出 7-9 項
- 0.5：列出 4-6 項
- 0.0：完全沒有
### 評分項 2：日期準確度（權重 25%）
- 1.0：所有日期皆與逐字稿一致（4/16、4/20、5/7、5/15、8/3、8/10、8/17、
  2027/3/1、2027/9、2028/9、2030/3）
- 0.5：有若干日期錯誤
- 0.0：日期大多錯誤
### 評分項 3：背景脈絡（權重 25%）
- 1.0：每一事件皆附清楚背景（負責方、狀態、相關議案）
- 0.5：背景脈絡基本
- 0.0：僅列日期、無脈絡
### 評分項 4：優先排序（權重 15%）
- 1.0：「值得關注」重點整理有效，凸顯關鍵事件
- 0.5：重點薄弱
- 0.0：完全沒有重點區段
