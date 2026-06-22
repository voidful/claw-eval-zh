---
id: task_meeting_tech_decisions
name: 台灣公司產品會議：擷取會議決議
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_tech_decisions
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T116tw_meeting_tech_decisions
workspace_files:
- source: tw/meetings/tw_tech_product_meeting.md
  dest: meeting_transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台灣公司產品會議：擷取會議決議

## Prompt

我手上有一個檔案 meeting_transcript.md，內含一場虛構台灣軟體公司「鼎峰科技」的
產品暨行銷週會逐字稿（時間為 2025-03-18，Asia/Taipei）。會議涵蓋研討會贊助分工、
「鼎峰匯流大會」(DingFeng Connect) 的產品發布題材、競品比較資訊圖（infographic）
設計回饋、競品分析方法論與比較試算表，以及一場訊息架構（messaging）練習。

請幫我辨識出會議期間所做成的所有決議（或達成的共識），並寫入一個名為 decisions.md
的檔案。針對每一項決議，請包含：

- 決議（Decision）：決定了什麼
- 背景脈絡（Context）：為何討論此事的簡要背景
- 參與者（Participants）：誰表達了意見（請使用逐字稿中的姓名）
- 狀態（Status）：final（定案）、tentative（暫定），或 needs follow-up（待後續確認）

並在最上方附上一段彙總，說明決議總數，以及其中哪些可能需要進一步確認。請務必區分
「已達成的決議」與「只是討論、尚未拍板」的事項，不要把後者誤當決議。

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿 meeting_transcript.md
2. 區分決議（已達成的結論／共識）與尚在進行的討論
3. 掌握每項決議背後的背景脈絡與相關參與者

應辨識出的關鍵決議（皆取自逐字稿、皆為虛構素材）：

1. 活動贊助分工：平台（Platform）→ 開源人年會 COSCUP；CI/CD → DevOpsDays Taipei；
   GitOps → Kubernetes Day Taiwan。三場各對一條產品主線。（注意：各條線預算仍待
   各自的活動行銷經理確認，王志明先列為暫定／待確認，故狀態為 needs follow-up。）
2. 產品發布方式：把過去一年的多個小型 MVC 整合（bundle）成一個大主題敘事（例如
   「漏洞管理 vulnerability management」），而非逐條列功能；重用 5.0 版的發布內容
   再加上之後的新增項目。
3. Top 5 功能挑選：改掉「每個 stage 各挑 3 個」的做法，改成從所有 stage 裡挑出
   整體前 5 名（top 5 overall），交給公關（PR）團隊當 keynote 素材。
4. 競品比較方法論：只聚焦 tier 1 對手；每個 stage 只放與該 stage 相關的 tier 1 對手
   （不是每頁都塞滿六家）；並在比較表新增「鼎峰」自己一列，以誠實呈現對手較強之處。
5. 資訊圖配色：維持只用綠色的配色（不放紅色或黃色），以保持「比較」的調性，而非
   競爭攻擊式（attack piece）。
6. 訊息主標語：在多個候選中選定「更快交付，更低風險」為最終主標語（勝過「自信地
   快速前進」「零取捨」等替代方案）。
7. stage 命名：承認如「設定（Configure）」「監控（Monitor）」等名稱描述性不足，
   但這次先沿用（needs follow-up），下一版迭代再加上可點選進入的細節頁。

## Grading Criteria

- [ ] 已建立檔案 decisions.md
- [ ] 至少辨識出 5 項不同的決議
- [ ] 已掌握活動贊助分工的決議（COSCUP、DevOpsDays Taipei、Kubernetes Day Taiwan）
- [ ] 已掌握產品發布的整合（bundle）方式（多個 MVC 包成主題，如漏洞管理）
- [ ] 已掌握競品方法論的決議（只用 tier 1、每個 stage 只放相關對手、新增鼎峰一列）
- [ ] 已掌握訊息主標語的決議（「更快交付，更低風險」）
- [ ] 已掌握資訊圖配色的決議（只用綠色、不放紅色）
- [ ] 每項決議皆提供背景脈絡
- [ ] 已標示決議狀態（final 對比 needs follow-up）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """台灣鼎峰科技產品會議「決議擷取」grader（固定虛構逐字稿）。

    本任務的九個查核項，改查台灣逐字稿
    (dest=meeting_transcript.md) 推導之事實 + agent 的中文報告 decisions.md。
    僅用標準函式庫。報告為繁體中文，故以中文關鍵字／數值比對；轉換器會在其後自動
    接上中→英正規化 wrapper（附加英文關鍵字、保留原中文），不影響中文比對。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "decisions.md"
    if not report_path.exists():
        for alt in ["meeting_decisions.md", "decision_log.md",
                    "decisions_summary.md", "decisions_report.md",
                    "會議決議.md", "決議.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "min_decisions": 0.0,
            "event_assignments": 0.0,
            "announcement_approach": 0.0,
            "competitive_methodology": 0.0,
            "messaging_tagline": 0.0,
            "infographic_colors": 0.0,
            "context_provided": 0.0,
            "status_indicated": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    low = content.lower()

    # --- 從逐字稿動態讀出「應有事實」以供比對（避免硬寫）---
    tpath = workspace / "meeting_transcript.md"
    tx = ""
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")
    tx_low = tx.lower()

    # 1) 最少決議數量：中文標題/條列/含「決議|決定」的行
    decision_markers = re.findall(
        r'(?:^|\n)\s*(?:[-*•]|\d+[.)、]|決議|決定) .{4,}', content)
    headers = re.findall(r'(?:^|\n)#+\s+.+', content)
    decision_word_lines = re.findall(r'(?:^|\n)[^\n]*(?:決議|決定)[^\n]{2,}', content)
    n_dec = max(len(decision_markers), len(decision_word_lines))
    if n_dec >= 5 or len(headers) >= 5:
        scores["min_decisions"] = 1.0
    elif n_dec >= 3 or len(headers) >= 3:
        scores["min_decisions"] = 0.5
    else:
        scores["min_decisions"] = 0.0

    # 2) 活動贊助分工：三場台灣研討會（COSCUP / DevOpsDays Taipei / Kubernetes Day）
    #    從逐字稿動態抓出實際出現的活動名，再看報告命中幾個。
    event_terms = []
    for pat in [r'coscup', r'devopsdays', r'kubernetes day']:
        if re.search(pat, tx_low):
            event_terms.append(pat)
    if not event_terms:  # 逐字稿缺失時的保險預設
        event_terms = [r'coscup', r'devopsdays', r'kubernetes day']
    # 中文別名也接受（開源人年會 ~ COSCUP）
    event_hits = 0
    if re.search(r'coscup|開源人年會', low):
        event_hits += 1
    if re.search(r'devopsdays', low):
        event_hits += 1
    if re.search(r'kubernetes day|k8s day', low):
        event_hits += 1
    scores["event_assignments"] = (
        1.0 if event_hits >= 2 else (0.5 if event_hits >= 1 else 0.0))

    # 3) 產品發布整合方式：把多個 MVC 包成主題（如漏洞管理），重用 5.0 版內容
    announce_a = bool(re.search(r'整合|包成|彙整|歸納|bundle|綁成一(?:包|個)|打包|主題敘事', content, re.IGNORECASE))
    announce_b = bool(re.search(r'漏洞管理|vulnerability\s*management|mvc|5\.0', content, re.IGNORECASE))
    announce_hits = int(announce_a) + int(announce_b)
    scores["announcement_approach"] = (
        1.0 if announce_hits >= 2 else (0.5 if announce_hits >= 1 else 0.0))

    # 4) 競品方法論：只用 tier 1、每個 stage 只放相關對手、新增鼎峰一列
    comp_a = bool(re.search(r'tier\s*(?:1|one|一)|第一層|一級', content, re.IGNORECASE))
    comp_b = bool(re.search(r'鼎峰.{0,8}(?:一列|一行|加[一上]|列|row|line)|新增.{0,6}鼎峰|加上.{0,6}鼎峰|gitlab', content, re.IGNORECASE))
    comp_c = bool(re.search(r'(?:相關|適用|對應)[^\n]{0,12}(?:stage|對手|競爭|競品)|每個\s*stage|各\s*stage', content, re.IGNORECASE))
    comp_hits = int(comp_a) + int(comp_b) + int(comp_c)
    scores["competitive_methodology"] = (
        1.0 if comp_hits >= 2 else (0.5 if comp_hits >= 1 else 0.0))

    # 5) 訊息主標語：選定「更快交付，更低風險」
    tagline = bool(re.search(r'更快交付[，,、\s]*更低風險|more\s*speed\s*less\s*risk', content, re.IGNORECASE))
    scores["messaging_tagline"] = 1.0 if tagline else 0.0

    # 6) 資訊圖配色：只用綠色、不放紅色（保持比較調性）
    color = bool(re.search(
        r'(?:只用|維持|保留|沿用).{0,6}綠|綠色.{0,10}(?:不[用放]|沒有|避免).{0,4}紅|不[用放].{0,4}紅|避免.{0,4}紅|綠色.{0,6}比較|green.*(?:no\s*red|without\s*red)',
        content, re.IGNORECASE))
    scores["infographic_colors"] = 1.0 if color else 0.0

    # 7) 背景脈絡：報告中有解釋性敘述
    ctx_a = bool(re.search(r'因為|原因|背景|脈絡|理由|為了|由於|考量|緣由|since|because|rationale|context', content, re.IGNORECASE))
    ctx_b = bool(re.search(r'討論|考慮|權衡|評估|爭論|斟酌|替代方案|候選|discuss|debate|consider', content, re.IGNORECASE))
    ctx_hits = int(ctx_a) + int(ctx_b)
    scores["context_provided"] = (
        1.0 if ctx_hits >= 2 else (0.5 if ctx_hits >= 1 else 0.0))

    # 8) 決議狀態：final / tentative / needs follow-up（暫定、待確認、定案…）
    st_a = bool(re.search(r'final|定案|確定|拍板|tentative|暫定|待確認|待後續|follow.?up|needs?\s*follow|待跟進|待確定|未定案', content, re.IGNORECASE))
    st_b = bool(re.search(r'狀態|status|共識|consensus|已通過|議定|達成|agreed', content, re.IGNORECASE))
    st_hits = int(st_a) + int(st_b)
    scores["status_indicated"] = (
        1.0 if st_hits >= 2 else (0.5 if st_hits >= 1 else 0.0))

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

### 評分項 1：決議辨識準確度（權重 35%）

**1.0 分**：辨識出所有主要決議，包含活動贊助分工、產品發布整合方式、競品方法論、
資訊圖配色與訊息主標語。正確區分決議與進行中的討論（例如把「活動預算仍待活動行銷
經理確認」標為待後續，而非已定案）。
**0.75 分**：掌握多數決議，但漏掉一項，或誤把曾討論但未拍板的項目納入。
**0.5 分**：掌握部分決議，但漏掉數項，或把討論與決議混為一談。
**0.25 分**：僅辨識出一兩項顯而易見的決議。
**0.0 分**：未辨識出有意義的決議。

### 評分項 2：背景脈絡品質（權重 25%）

**1.0 分**：每項決議皆附上準確的背景脈絡，說明是什麼促成討論、考慮過哪些替代方案，
以及為何選定該方案（例如資訊圖不用紅色是為了避免變成攻擊式素材、保持比較調性）。
**0.75 分**：多數決議有良好背景脈絡，僅有少許缺口。
**0.5 分**：提供部分背景脈絡，但缺少關鍵推理或所考慮的替代方案。
**0.25 分**：背景脈絡極少，決議僅逐條列出而無說明。
**0.0 分**：未提供背景脈絡。

### 評分項 3：參與者歸屬（權重 20%）

**1.0 分**：正確指出誰倡議每一立場、誰參與了達成共識，姓名準確取自逐字稿
（王志明、林淑芬、高敏哲、陳柏宇、蔡思敏、戴立安）。
**0.75 分**：多數參與者正確辨識，僅有少許錯誤。
**0.5 分**：辨識出部分參與者，但有數位缺漏或誤植。
**0.25 分**：參與者辨識極少。
**0.0 分**：未歸屬參與者。

### 評分項 4：結構與實用性（權重 20%）

**1.0 分**：決議格式清楚、結構一致，附上實用的彙總，並標示哪些決議為 final、哪些
需 follow-up。可直接作為會議紀錄使用。
**0.75 分**：結構良好，僅有少許格式問題。
**0.5 分**：可讀，但結構不一致或缺少彙總。
**0.25 分**：組織不佳，難以作為參考。
**0.0 分**：無可用結構。
