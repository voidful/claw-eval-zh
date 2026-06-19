---
id: task_meeting_tldr
name: 會議 TL;DR 速覽（鼎峰科技產品行銷週會）
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_tldr
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T129tw_meeting_tldr
workspace_files:
- source: tw/meetings/tw_tech_product_meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 會議 TL;DR 速覽（鼎峰科技產品行銷週會）

## Prompt

工作區裡有一個檔案 meeting_transcript.md，內含虛構台灣軟體公司「鼎峰科技」一場
產品暨行銷週會的逐字稿。我錯過了這場會議，需要快速跟上進度。

請幫我把一份 TL;DR 寫入名為 meeting_tldr.md 的檔案。它應該**極度精簡**——就像你
會貼在公司 Slack 上、給沒參加的同事看的那種速覽。要求：

- **最多 150 字**（硬性上限，以中文字數計）
- 最上方有一句**一行總結**（用一句話說明這場會議在談什麼）
- **3-5 個重點**，涵蓋最重要的結論
- 提及任何**期限**

不要廢話、不要前言、不要「在這場會議中，團隊討論了……」之類的開場白——只要必要
的事實。請以繁體中文撰寫。

## Expected Behavior

助手應讀取 meeting_transcript.md，把整場會議濃縮到約 150 字以內，產出一份像貼在
Slack 上的速覽，內容類似：

  **鼎峰產品行銷週會——活動分工、匯流大會發布題材、競品與訊息定案。**

  - 活動主線確定：平台→開源人年會 COSCUP、CI/CD→DevOpsDays Taipei、
    GitOps→Kubernetes Day Taiwan。各自跟活動行銷經理確認並在 issue 留言。
  - 鼎峰匯流大會發布：把過去一年的小型 MVC 整合成主題，漏洞管理當資安主打；
    改挑「整體前 5 名」功能。
  - 競品資訊圖維持只用綠色（不放紅色），保持產業比較而非攻擊調性。
  - 競品表只比 tier 1、每個 stage 只放相關對手，並加上「鼎峰」自己一列。
  - 訊息主標語定案：「更快交付，更低風險」。

  ⏰ 產品發布試算表星期二截止。

重點是極度壓縮（逐字稿很長）、優先保留最重要的結論與期限，並避免冗長前言。

## Grading Criteria

- [ ] 已建立 meeting_tldr.md 檔案
- [ ] 最上方有一句一行總結
- [ ] 包含 3-5 個重點
- [ ] 提及活動分工（COSCUP、DevOpsDays Taipei 或 Kubernetes Day Taiwan）
- [ ] 提及訊息決議（「更快交付，更低風險」）
- [ ] 提及期限（星期二／週二截止）
- [ ] 總字數精簡（約 150 字以內，至多不超過 200 字）
- [ ] 沒有不必要的填充或前言

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW 鼎峰科技 會議 TL;DR grader（依台灣逐字稿動態推導應有事實）。

    對齊原 task_meeting_tldr 的查核項，但改查台灣逐字稿（meeting_transcript.md）
    推導之事實 + agent 的中文 TL;DR 報告 meeting_tldr.md。僅用標準函式庫。
    字數查核改用 CJK 字元數（中文無空白可切）。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "file_created", "one_line_summary", "bullet_points",
        "events_mentioned", "messaging_decision", "deadline_mentioned",
        "word_count_ok", "no_filler",
    ]

    # --- 1) 定位 agent 報告（含常見替代檔名）---
    report_path = workspace / "meeting_tldr.md"
    if not report_path.exists():
        for alt in ["tldr.md", "tl_dr.md", "meeting_tl_dr.md", "summary.md",
                    "會議速覽.md", "速覽.md", "會議摘要.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores = {"file_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    content_lower = content.lower()

    # --- helper：CJK 字元數（中文以字計，不靠空白切詞）---
    def cjk_len(s):
        # 計入中日韓統一表意文字；其餘非空白可見字元也粗略計入，
        # 但全形標點不計（避免懲罰正常標點）。
        cjk = len(re.findall(r"[一-鿿]", s))
        # 半形英數連續詞（如 COSCUP、tier 1、CI/CD）各算一個詞
        latin_tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9/_:.\-]*", s)
        return cjk + len(latin_tokens)

    word_count = cjk_len(content)

    # --- helper：寬鬆比對（去全形標點與空白）---
    def norm(s):
        for ch in "，、。「」（）(),：:；; ":
            s = s.replace(ch, "")
        return re.sub(r"\s+", "", s)

    # --- 2) 從逐字稿動態讀出「應有事實」（避免硬寫英文原版）---
    tpath = workspace / "meeting_transcript.md"
    if not tpath.exists():
        for alt in ["transcript.md", "meeting.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    tx = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""
    tx_norm = norm(tx)

    def in_tx(*phrases):
        return any(norm(p) in tx_norm for p in phrases)

    # 三場活動主線（逐字稿原文，皆為虛構台灣研討會）
    event_candidates = [
        ("COSCUP", r"coscup|開源人年會"),
        ("DevOpsDays Taipei", r"devopsdays"),
        ("Kubernetes Day Taiwan", r"kubernetes\s*day|k8s\s*day"),
    ]
    present_events = [(name, pat) for (name, pat) in event_candidates
                      if in_tx(name) or re.search(pat, tx, re.IGNORECASE)]

    # 訊息主標語（逐字稿宣布的最終定案）
    messaging_final = "更快交付，更低風險"
    messaging_in_tx = in_tx(messaging_final, "更快交付更低風險")

    # 期限（逐字稿明示產品發布試算表的截止）
    deadline_in_tx = bool(re.search(r"星期二|週二|tuesday", tx, re.IGNORECASE))

    # --- 3) 一行總結（最上方第一個非空、非純標題行，長度合理）---
    lines = [ln.strip() for ln in content.split("\n") if ln.strip()]
    if lines:
        first = lines[0]
        if first.startswith("#") and len(lines) > 1:
            first = lines[1]
        # 去掉粗體標記再量長度
        first_clean = first.replace("**", "").replace("*", "").lstrip("#").strip()
        first_len = cjk_len(first_clean)
        # 一句總結應簡短（約 50 字以內為佳）
        scores["one_line_summary"] = 1.0 if first_len <= 50 else 0.5
    else:
        scores["one_line_summary"] = 0.0

    # --- 4) 重點符號（3-5，寬鬆容許 3-7）---
    bullets = re.findall(r"(?:^|\n)\s*(?:[-*•]|\d+[.)、])\s+\S", content)
    n = len(bullets)
    if 3 <= n <= 7:
        scores["bullet_points"] = 1.0
    elif 2 <= n <= 9:
        scores["bullet_points"] = 0.5
    else:
        scores["bullet_points"] = 0.0

    # --- 5) 活動分工：依逐字稿實際出現的活動，數報告命中幾個 ---
    events_found = 0
    for (name, pat) in present_events:
        if norm(name) in norm(content) or re.search(pat, content, re.IGNORECASE):
            events_found += 1
    scores["events_mentioned"] = (
        1.0 if events_found >= 2 else (0.5 if events_found >= 1 else 0.0)
    )

    # --- 6) 訊息決議：「更快交付，更低風險」（僅在逐字稿確有此定案時查核）---
    if messaging_in_tx:
        hit = (norm(messaging_final) in norm(content)) or bool(
            re.search(r"更快交付[，,]?\s*更低風險", content)
        )
        scores["messaging_decision"] = 1.0 if hit else 0.0
    else:
        # 逐字稿若無此事實則不懲罰（理論上不會發生）
        scores["messaging_decision"] = 1.0

    # --- 7) 期限：星期二／週二／截止／期限 ---
    if deadline_in_tx:
        scores["deadline_mentioned"] = 1.0 if re.search(
            r"星期二|週二|tuesday|截止|期限|deadline|due", content, re.IGNORECASE
        ) else 0.0
    else:
        scores["deadline_mentioned"] = 1.0

    # --- 8) 字數（目標 ≤150 漢字）---
    # 註：cjk_len 會把每個半形英數詞（COSCUP、DevOpsDays、tier 1…）各算一個，
    # 而這類雙語技術 TL;DR 必然帶不少英文活動／產品名，純漢字本來就逼近上限。
    # 為避免「完整覆蓋所有決議的正確答案」反被字數懲罰（本題作者範例答案即達
    # 約 183），門檻放寬到 ≤200 給滿分、≤300 給半分，超過 300 才視為「這是
    # 摘要不是 TL;DR」給 0；如此仍能與冗長前言版本拉開差距。
    if word_count <= 200:
        scores["word_count_ok"] = 1.0
    elif word_count <= 300:
        scores["word_count_ok"] = 0.5
    else:
        scores["word_count_ok"] = 0.0

    # --- 9) 無填充／前言（中英文常見開場白）---
    filler_patterns = [
        r"在(這|本)?(場|次)?(會議|會中)",
        r"團隊(討論|開會|聚集|進行了)",
        r"(本|這)(份)?(文件|摘要|報告)(提供|包含|涵蓋)",
        r"(以下|底下)(是|為)",
        r"in\s*this\s*meeting",
        r"the\s*team\s*(?:discussed|met|gathered)",
    ]
    filler_count = sum(
        1 for p in filler_patterns
        if re.search(p, content, re.IGNORECASE)
    )
    scores["no_filler"] = (
        1.0 if filler_count == 0 else (0.5 if filler_count == 1 else 0.0)
    )

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

### 評分項 1：資訊密度（權重 40%）
- 1.0：每一句都承載必要資訊，掌握會議最重要的 5 項結論（活動分工、發布題材／
  漏洞管理、競品資訊圖只用綠色、競品表只比 tier 1 並加鼎峰一列、訊息主標語），
  沒有贅字；同事讀完即能掌握所有需要知道的事。
- 0.75：掌握多數重要結論，僅少許遺漏或略嫌冗長。
- 0.5：關鍵結論俱在，但漏掉部分重要項目，或塞入不必要的脈絡。
- 0.25：漏掉主要結論，或對 TL;DR 而言過於囉嗦。
- 0.0：作為快速摘要沒有用處。

### 評分項 2：精簡度（權重 35%）
- 1.0：150 字以內，讀起來像一則 Slack 訊息——有力、直接、不拖泥帶水，適當使用
  簡寫（用 → 表示分工等）。
- 0.75：200 字以內，大致精簡，仍有可刪減之處。
- 0.5：200-300 字，內容合理，但稱不上真正的 TL;DR。
- 0.25：超過 300 字——這是摘要，不是 TL;DR。
- 0.0：超過 500 字，或完全未達精簡要求。

### 評分項 3：可掃描性（權重 25%）
- 1.0：能在 30 秒內完全吸收，視覺結構清楚（重點符號、用粗體強調、期限被標示
  出來），最上方的一行總結立即讓讀者定位。
- 0.75：結構良好，大致可掃描，仍有少許可改進。
- 0.5：包含資訊，但需要仔細閱讀才能擷取重點。
- 0.25：一大片文字或結構不佳。
- 0.0：沒有結構或內容缺失。
