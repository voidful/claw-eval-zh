---
id: task_meeting_tech_messaging
name: 會議訊息架構擷取（鼎峰科技標語與支柱）
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_tech_messaging
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T118tw_meeting_tech_messaging
workspace_files:
- source: tw/meetings/tw_tech_product_meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 會議訊息架構擷取（鼎峰科技標語與支柱）

## Prompt

工作區裡有一份會議逐字稿 meeting_transcript.md（虛構台灣軟體公司「鼎峰科技」的
產品暨行銷週會）。會議接近尾聲時（逐字稿「五、訊息架構練習：標語與支柱」一節），
團隊做了一場協作式的訊息（messaging）練習，為旗下「鼎峰雲平台」發展標語（tagline）
與三個訊息支柱（pillar）。

請閱讀逐字稿，擷取並整理會議中討論到的所有訊息架構選項，寫入一個名為
messaging_framework.md 的檔案。你的輸出應包含：

1. **所有候選標語／語句**：所有被提出的標語／語句，依其所對應的訊息支柱分組
2. **評估準則（evaluation criteria）**：團隊所使用的準則（例如調性的對等性、是否
   朗朗上口、名詞片語對比動詞片語、技術準確性、能否套進平行句構）
3. **每個選項所討論的優缺點**
4. **最終選定（final selections）**：團隊決定採用的標語
5. **被否決的替代方案（rejected alternatives）**及其被否決的原因

請以繁體中文撰寫，並清楚區分「最終選定」與「被否決／其他候選」。

## Expected Behavior

助手應解析 meeting_transcript.md 第五段「訊息架構練習」，辨識出三個訊息支柱與
所有候選語句，並產出 messaging_framework.md。

關鍵訊息內容（皆為逐字稿原文，主持人為王志明，靈感參考 Ash Withers 架構）：

支柱一 — 透明／單一平台（Transparency / Single Platform）：
- 「從路線圖到公司願景，我們都透明」（原始版）
- 「單一真相來源，無限可能」（提議版，王志明很喜歡、大家評價也很好）
- 「人人都能用的一體式平台」（提議版，王志明喜歡但承認不是每個人都會買單）

支柱二 — 端到端掌控（End-to-end control）：
- 「幾乎什麼都能自動化，凡事都能協作」（原始版）
- 「端到端掌控你的軟體工廠」（提議版，較不朗朗上口但很有描述性）

支柱三 — 速度／資安（Speed / Security）：
- 「規模拉大、速度拉快、測試拉滿」（原始版——王志明超討厭，尤其「測試拉滿」聽起來超蠢）
- 「自信地快速前進」（提議版——意涵喜歡，但是動詞片語，與其他名詞片語的調性對不齊、缺乏對等性）
- 「更快交付，更低風險」（提議版——團隊共識最愛）
- 「加速並維持在軌道上」（提議版——大家不愛）
- 「帶著自信的速度」（當作一個概念提及）
- 「零取捨（no trade-offs）」（短暫考慮後被否決——工程師心態認為永遠都有取捨，講絕對話不準確）
- 「更快交付、更低風險，帶著自信」（提議的組合版）

評估準則（王志明列出四項）：
1. 調性的對等性（parity）——名詞片語要配名詞片語
2. 是否朗朗上口、精煉有力（catchy／pithy）
3. 技術準確性——不做絕對化主張（如「零取捨」或「100% 安全」）
4. 能否套進平行句構——例如「使用鼎峰，你就能得到 X」

最終選定（final）：
- 透明支柱：「單一真相來源，無限可能」
- 端到端支柱：「端到端掌控你的軟體工廠」
- 速度／資安支柱：「更快交付，更低風險」（主標語）

資安子標語：
- 「守護工廠與每一次交付」（出自林淑芬的部落格文章）

助手應清楚區分最終選定與被否決的替代方案，並盡可能標出貢獻者（王志明、林淑芬、
以及 Ash Withers 的啟發）。

## Grading Criteria

- [ ] 建立報告檔案 messaging_framework.md
- [ ] 辨識出全部三個訊息支柱（透明／單一平台、端到端掌控、速度／資安）
- [ ] 每個支柱列出多個候選語句
- [ ] 「更快交付，更低風險」被辨識為速度／資安支柱的選定標語
- [ ] 「單一真相來源，無限可能」被辨識為透明支柱的選定標語
- [ ] 「端到端掌控你的軟體工廠」被辨識為端到端支柱的選定標語
- [ ] 列出被否決的替代方案及原因（如「測試拉滿」超蠢被否決、「零取捨」因永遠有取捨被否決）
- [ ] 掌握評估準則（對等性／調性、朗朗上口、技術準確性、平行句構）
- [ ] 掌握「守護工廠與每一次交付」作為資安子標語
- [ ] 最終選定與替代方案清楚區分

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW 鼎峰科技 訊息架構擷取 grader（依台灣逐字稿動態推導應有事實）。

    讀 meeting_transcript.md 推導「應有的標語／支柱／最終選定」，再比對 agent 的
    中文報告 messaging_framework.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 1) 定位 agent 報告 ---
    report = workspace / "messaging_framework.md"
    if not report.exists():
        for alt in ["messaging.md", "framework.md", "taglines.md",
                    "messaging_options.md", "訊息架構.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = [
        "report_created", "three_pillars", "multiple_candidates",
        "chosen_speed_tagline", "chosen_transparency_tagline",
        "chosen_e2e_tagline", "rejected_alternatives",
        "evaluation_criteria", "security_subtagline", "finals_distinguished",
    ]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    content = report.read_text(encoding="utf-8", errors="ignore")

    # --- helper：把全形標點、空白統一掉，方便寬鬆比對 ---
    def norm(s):
        s = s.replace("，", "").replace("、", "").replace("。", "")
        s = s.replace("「", "").replace("」", "").replace("（", "").replace("）", "")
        s = s.replace("(", "").replace(")", "").replace(",", "")
        s = re.sub(r"\s+", "", s)
        return s

    c_norm = norm(content)

    def has(*phrases):
        return any(norm(p) in c_norm for p in phrases)

    # --- 2) 從逐字稿動態讀出「應有事實」（避免硬寫英文原版）---
    tpath = workspace / "meeting_transcript.md"
    tx = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""
    tx_norm = norm(tx)

    def in_tx(*phrases):
        return any(norm(p) in tx_norm for p in phrases)

    # 三大支柱的代表語句（逐字稿原文）
    pillar_transparency = ["單一真相來源，無限可能", "人人都能用的一體式平台",
                           "從路線圖到公司願景，我們都透明"]
    pillar_e2e = ["端到端掌控你的軟體工廠", "幾乎什麼都能自動化，凡事都能協作"]
    pillar_speed = ["更快交付，更低風險", "自信地快速前進", "規模拉大、速度拉快、測試拉滿",
                    "加速並維持在軌道上", "帶著自信的速度", "零取捨"]

    # 最終選定（逐字稿宣布）
    final_transparency = "單一真相來源，無限可能"
    final_e2e = "端到端掌控你的軟體工廠"
    final_speed = "更快交付，更低風險"
    security_sub = "守護工廠與每一次交付"

    # 只保留「確實出現在台灣逐字稿裡」的事實當查核基準（動態推導，不硬寫）
    present_transparency = [p for p in pillar_transparency if in_tx(p)]
    present_e2e = [p for p in pillar_e2e if in_tx(p)]
    present_speed = [p for p in pillar_speed if in_tx(p)]

    # --- 3) 三個支柱是否都被辨識（用各支柱任一代表語句 / 支柱名稱判定）---
    pillar_hits = 0
    if has(*present_transparency) or re.search(r"透明|單一平台|單一真相|一體式", content):
        pillar_hits += 1
    if has(*present_e2e) or re.search(r"端到端|掌控|自動化", content):
        pillar_hits += 1
    if has(*present_speed) or re.search(r"速度|資安|風險|安全|取捨", content):
        pillar_hits += 1
    scores["three_pillars"] = 1.0 if pillar_hits >= 3 else (0.5 if pillar_hits >= 2 else 0.0)

    # --- 4) 多個候選語句（從逐字稿出現的所有候選裡，數報告命中幾個）---
    all_candidates = present_transparency + present_e2e + present_speed + ["更快交付、更低風險，帶著自信"]
    # 去重
    seen = set()
    uniq_candidates = []
    for p in all_candidates:
        k = norm(p)
        if k and k not in seen:
            seen.add(k)
            uniq_candidates.append(p)
    phrase_count = sum(1 for p in uniq_candidates if has(p))
    scores["multiple_candidates"] = (
        1.0 if phrase_count >= 6 else
        0.75 if phrase_count >= 4 else
        0.5 if phrase_count >= 3 else 0.0
    )

    # --- 5) 速度／資安最終選定：「更快交付，更低風險」並標為選定／最愛 ---
    speed_chosen_marker = re.search(
        r"(更快交付[，,]?\s*更低風險)[^\n]{0,40}?(最終|選定|採用|主標語|共識|最愛|決定|定案|首選)|"
        r"(最終|選定|採用|主標語|共識|最愛|決定|定案|首選)[^\n]{0,40}?(更快交付[，,]?\s*更低風險)",
        content,
    )
    if has(final_speed) and speed_chosen_marker:
        scores["chosen_speed_tagline"] = 1.0
    elif has(final_speed):
        scores["chosen_speed_tagline"] = 0.5
    else:
        scores["chosen_speed_tagline"] = 0.0

    # --- 6) 透明支柱最終選定：「單一真相來源，無限可能」 ---
    scores["chosen_transparency_tagline"] = 1.0 if has(final_transparency) else 0.0

    # --- 7) 端到端支柱最終選定：「端到端掌控你的軟體工廠」 ---
    scores["chosen_e2e_tagline"] = 1.0 if has(final_e2e) else 0.0

    # --- 8) 被否決的替代方案及原因 ---
    rejected_hits = 0
    # 「測試拉滿 / 規模拉大…」被否決（蠢／討厭）
    if re.search(r"(測試拉滿|規模拉大[^\n]{0,20}測試拉滿)", content) and \
       re.search(r"(超蠢|蠢|討厭|不喜歡|否決|不愛|goofy)", content):
        rejected_hits += 1
    # 「零取捨」被否決（永遠有取捨／工程師心態／不準確）
    if re.search(r"零取捨|no\s*trade", content, re.IGNORECASE) and \
       re.search(r"(否決|永遠都有取捨|永遠有取捨|工程師|不準確|絕對)", content):
        rejected_hits += 1
    # 「自信地快速前進」因對等性／動詞片語被排除
    if re.search(r"自信地快速前進", content) and \
       re.search(r"(對等性|對不齊|動詞片語|parity|名詞片語)", content):
        rejected_hits += 1
    scores["rejected_alternatives"] = (
        1.0 if rejected_hits >= 2 else (0.5 if rejected_hits >= 1 else 0.0)
    )

    # --- 9) 評估準則 ---
    criteria_hits = 0
    if re.search(r"對等性|對不齊|調性|平行句構|parity|parallel", content):
        criteria_hits += 1
    if re.search(r"朗朗上口|精煉|有力|catch|pith", content, re.IGNORECASE):
        criteria_hits += 1
    if re.search(r"名詞片語|動詞片語|技術準確|準確性|絕對化|絕對話|100\s*%\s*安全", content):
        criteria_hits += 1
    scores["evaluation_criteria"] = (
        1.0 if criteria_hits >= 2 else (0.5 if criteria_hits >= 1 else 0.0)
    )

    # --- 10) 資安子標語 ---
    scores["security_subtagline"] = 1.0 if has(security_sub) else 0.0

    # --- 11) 最終 vs 否決是否清楚區分 ---
    final_word = bool(re.search(r"最終|選定|採用|決定|定案|主標語|final", content, re.IGNORECASE))
    reject_word = bool(re.search(r"否決|被否決|不採用|替代方案|淘汰|捨棄|排除|reject", content, re.IGNORECASE))
    fin = (1 if final_word else 0) + (1 if reject_word else 0)
    scores["finals_distinguished"] = 1.0 if fin >= 2 else (0.5 if fin >= 1 else 0.0)

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

### 評分項 1：選項掌握的完整度（權重 30%）
- 1.0：列出橫跨三個支柱的所有提議標語／語句，含原始版與替代版；至少掌握 8–10 個
  不同語句並正確歸入支柱。
- 0.75：掌握多數語句並正確分組，僅漏一兩個。
- 0.5：掌握數個語句，但漏掉整批替代方案或某一支柱。
- 0.25：僅掌握最終選定而無替代方案。
- 0.0：未掌握有意義的選項。

### 評分項 2：評估準則與推理（權重 25%）
- 1.0：準確掌握評估架構（調性對等性、朗朗上口、技術準確性、平行句構），並含否決的
  具體理由（如「測試拉滿」聽起來蠢、「零取捨」違背工程師心態、「自信地快速前進」是
  動詞片語缺乏名詞片語對等性）。
- 0.75：掌握多數準則並有良好推理。
- 0.5：提及部分準則但推理不完整。
- 0.25：推理極少。
- 0.0：無評估準則或推理。

### 評分項 3：最終與否決的區分（權重 25%）
- 1.0：清楚區分最終選定與被否決的替代方案，容易辨識何者被選用、何者被捨棄。
- 0.75：區分良好，僅有少許模糊。
- 0.5：有部分區分，但讀者需自行推斷何者為最終。
- 0.25：所有選項混在一起且無明確結果。
- 0.0：未做區分。

### 評分項 4：細微之處與歸屬（權重 20%）
- 1.0：掌握誰提出了什麼，含「守護工廠與每一次交付」出自林淑芬部落格文章的歸功、
  記下 Ash Withers 的啟發，並反映此練習的協作動態。
- 0.75：歸屬良好，僅有少許缺口。
- 0.5：有部分歸屬，但漏掉關鍵貢獻。
- 0.25：未將想法歸屬到個人。
- 0.0：無細微之處或歸屬。
