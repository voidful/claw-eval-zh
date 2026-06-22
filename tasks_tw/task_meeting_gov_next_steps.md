---
id: task_meeting_gov_next_steps
name: 數位治理委員會（虛構）：生成式 AI 治理公聽會後續步驟擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_gov_next_steps
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: new_tw_variant
claw_eval_tw_id: T136tw_meeting_gov_next_steps
workspace_files:
- source: tw/meetings/tw_gov_hearing.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 數位治理委員會（虛構）：生成式 AI 治理公聽會後續步驟擷取

## Prompt

工作區裡有一份公聽會逐字稿 transcript.md，來自台灣虛構的「數位治理委員會」
首場「生成式 AI 治理」公開公聽會。這是一場審議性質的公聽會，在研析小組提出
最終報告前，還有數個月的工作要做。

請讀過 transcript.md，把所有提及的後續步驟、後續行動、時程與交付項目，擷取到
一個名為 next_steps.md 的檔案。對於每一項，請列出：

- **行動項目**：需要發生的事
- **負責方**：預期由誰負責——數位治理委員會、風析中心、研析小組、通監中心 等
- **時程**：預期何時（若逐字稿有提及）
- **狀態**：被提及為計畫中、進行中或已完成
- **來源**：誰在會議中提到的（沿用逐字稿中的中文姓名，如張庭瑋、王志明、陳冠宇等）

請組織成以下區段：即將進行（數週內）、近期（數月內）、長期（持續／數年），
以及待解問題（已被提出、但尚無明確後續指派的項目）。最後附上一段關鍵里程碑的
時間軸視覺化（可用表格或條列），呈現重要時間點。

請忠實依逐字稿原文擷取，姓名、機關、日期等事實一律沿用逐字稿原樣。報告請以
繁體中文（zh-TW）撰寫。

## Expected Behavior

助手應讀取並解析完整的 transcript.md，辨識所有關於行動、交付項目與時程的
前瞻性陳述，區分「已承諾的行動」與「抱負性的目標」，並註記哪些項目有具體時程、
哪些時機模糊。關鍵後續步驟（皆出自虛構逐字稿）包括：

**即將進行（數週內）：**
- 研析小組在公聽會後將持續審議「數個月」，再提出最終報告（王志明）
- 風析中心年度風險報告須於 8 月 1 日前提交本委員會，並附更新後的案例
  數字（張庭瑋）
- 風析中心在首次協作論壇後，正建立「五方資料圈」（台日韓新澳）的跨國資料共享協議
  （張庭瑋）

**近期（數月內）：**
- 小組最終報告預計於「今年夏天」、最遲 7 月底前對外發布
  （王志明、陳冠宇）
- 報告將發布於本委員會官方網站（王志明）
- 報告依程序先送「數位治理諮詢委員會」審議，再正式轉交相關部會（王志明）
- 風析中心將公布「對話紀錄遭刪除」案例的調查結果（確認為記錄系統假影）（張庭瑋）
- 風析中心將在風險熱點領域部署專門打造的偵測探針進行監測（張庭瑋）
- 本委員會將接受風析中心派駐一名連絡人（窗口：鄭立群），協助制定科學化偵測計畫
  （張庭瑋）
- 額外的問答補充說明，將發布於本委員會知識網站 science.gov.tw（陳冠宇）

**長期（持續／數年）：**
- 風析中心將在風險熱點領域進行每次為期 3 個月的 24/7 連續監測，以建立常態行為基線
  （張庭瑋）
- 風析中心將以已知案例校準各監測系統（用受控測試流量比對偵測反應）（張庭瑋）
- 風析中心將為案例庫開發 AI/ML 分析能力（張庭瑋）
- 建立「五方資料圈」以外的更廣國際科學夥伴關係（張庭瑋、李宗翰）
- 開發公民科學群眾外包平台（郭佳穎、陳冠宇）
- 本委員會在收到小組建議後，再決定預算分配（王志明）

**待解問題（已提出但尚無明確後續指派）：**
- 小組範圍應只聚焦「生成式內容」，還是擴及代理式 AI 與跨系統行為——小組仍在辯論
- 如何為治理目的精確定義「異常」——周怡安與張庭瑋的討論
- 如何取得通監中心的原始（未過濾）監測資料而非僅處理過的資料——鄭立群建議；
  黃建宏指出「技術上可行，但並非毫無挑戰」
- 如何把群眾外包平台串接到即時的後續查證觀測——郭佳穎的討論
- 本委員會是否會設立具專屬經費的正式 AI 治理計畫——王志明：「現在說還太早」

## Grading Criteria

- [ ] 已建立輸出檔案 next_steps.md
- [ ] 提及小組最終報告的時程（今年夏天／7 月底前）並發布於官方網站
- [ ] 提及風析中心年度報告須於 8 月 1 日前提交委員會
- [ ] 提及風析中心在風險熱點部署專門打造的偵測探針
- [ ] 提及「五方資料圈」（台日韓新澳）跨國資料共享
- [ ] 註記預算／計畫狀態（目前未設立常設計畫、無專屬經費；現在說還太早）
- [ ] 至少辨識出一項待解問題（如異常定義、範圍辯論、原始監測資料）
- [ ] 項目依時間範圍組織（即將進行／近期／長期）
- [ ] 至少為 5 項辨識出負責方（機關或發言者）
- [ ] 包含關鍵里程碑的時間軸視覺化或里程碑摘要

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會（虛構）公聽會後續步驟擷取 grader。

    查核項皆改查工作區內的台灣逐字稿
    （dest=transcript.md）動態推導之事實，再與 agent 產生的中文報告
    next_steps.md 比對。報告為中文（轉換器會在其後接上中→英正規化 wrapper，
    但中文原文會被保留），故以中文關鍵字為主、英文為輔。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "final_report_timeline", "annual_report",
        "sensor_deployment", "data_sharing_circle", "budget_status",
        "open_questions", "timeframe_org", "responsible_parties",
        "timeline_viz",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "next_steps.md"
    if not report.exists():
        for alt in ["next_steps.txt", "後續步驟.md", "後續行動.md",
                    "follow_up.md", "followup.md", "action_items.md",
                    "actions.md", "後續步驟與行動.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出可查核事實（避免硬寫） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "meeting_transcript.md", "hearing.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    # 逐字稿以「**姓名（角色）：**」或「姓名（…）問／答／向…建議」標示發言者。
    speaker_candidates = set()
    for m in re.finditer(r'\*\*([一-鿿]{2,4})（', t):
        speaker_candidates.add(m.group(1))
    fallback_speakers = {
        "王志明", "陳冠宇", "林淑芬", "張庭瑋", "黃建宏", "周怡安",
        "蔡明翰", "郭佳穎", "高志遠", "李宗翰", "鄭立群", "白雅雯",
        "蕭文哲", "吳孟蓉",
    }
    speakers = {s for s in speaker_candidates
                if re.search(re.escape(s) + r'\s*[（(]', t)}
    if len(speakers) < 5:
        speakers = {s for s in fallback_speakers if s in t}
    if not speakers:
        speakers = fallback_speakers

    # 從逐字稿動態取出年度報告的提交日期（如「8 月 1 日」）。
    annual_date_re = (
        r'(\d{1,2})\s*月\s*(\d{1,2})\s*日|august\s*1|august\s*first|8\s*/\s*1')
    annual_date_in_t = bool(re.search(annual_date_re, t, re.IGNORECASE))

    # 從逐字稿動態取出資料共享聯盟的名稱（如「五方資料圈」）。
    circle_name = None
    mcir = re.search(r'(五方資料圈|[一-鿿]{1,4}資料圈)', t)
    if mcir:
        circle_name = mcir.group(1)

    scores = {"report_created": 1.0}

    # --- 1) 最終報告時程：今年夏天／7 月底前／發布於官方網站 ---
    report_patterns = [
        r'最終報告|final\s*report',
        r'今年夏天|這個?夏天|夏季|summer',
        r'7\s*月底|七月底|月底前|end\s*of\s*july|july',
        r'(?:發布|公布|刊登|上傳).{0,8}(?:官方)?網站|publish.*website|官方網站',
    ]
    rhits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in report_patterns)
    scores["final_report_timeline"] = (
        1.0 if rhits >= 2 else (0.5 if rhits >= 1 else 0.0))

    # --- 2) 年度報告須於提交日期（逐字稿之 8 月 1 日）前提交 ---
    annual_patterns = [
        r'年度(?:風險)?報告|annual\s*report',
        r'8\s*月\s*1\s*日|八月一日|八月\s*1\s*日|august\s*1|august\s*first|8\s*/\s*1',
        r'提交.{0,6}委員會|送交?.{0,6}委員會|呈報.{0,6}委員會|submit.*committee',
    ]
    ahits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in annual_patterns)
    # 至少要點到「年度報告」並帶到日期或提交對象；逐字稿確有 8 月 1 日才給滿分門檻。
    has_date_match = bool(
        re.search(r'8\s*月\s*1\s*日|八月一日|八月\s*1\s*日|august\s*1|august\s*first',
                  c, re.IGNORECASE))
    if re.search(r'年度(?:風險)?報告|annual\s*report', c, re.IGNORECASE):
        if annual_date_in_t and has_date_match:
            scores["annual_report"] = 1.0
        elif ahits >= 2:
            scores["annual_report"] = 1.0
        else:
            scores["annual_report"] = 0.5
    else:
        scores["annual_report"] = 0.0

    # --- 3) 偵測探針部署：專門打造的偵測探針／風險熱點／部署 ---
    sensor_patterns = [
        r'偵測探針|專門打造.{0,6}探針|專屬.{0,4}探針|purpose.?built|dedicated\s*sensor',
        r'部署.{0,6}(?:探針|感測|偵測)|deploy.*(?:sensor|probe)',
        r'風險熱點|熱點(?:領域|地區)|hotspot|surveillance',
        r'探針|感測器|sensor|probe',
    ]
    shits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in sensor_patterns)
    scores["sensor_deployment"] = (
        1.0 if shits >= 1 else 0.0)

    # --- 4) 跨國資料共享聯盟（逐字稿之「五方資料圈」／台日韓新澳） ---
    circle_patterns = [
        r'五方資料圈|[一-鿿]{1,4}資料圈',
        r'台日韓新澳|台、日、韓、新、澳|台.{0,2}日.{0,2}韓.{0,2}新.{0,2}澳',
        r'跨國.{0,4}資料共享|資料共享.{0,2}(?:聯盟|協議|協定)|data.?sharing',
    ]
    # 若能從逐字稿取出聯盟名稱，優先比對該名稱是否出現在報告。
    chits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in circle_patterns)
    if circle_name and circle_name in c:
        scores["data_sharing_circle"] = 1.0
    else:
        scores["data_sharing_circle"] = 1.0 if chits >= 1 else 0.0

    # --- 5) 預算／計畫狀態（未設常設計畫、無專屬經費、現在說還太早） ---
    budget_patterns = [
        r'未設立.{0,6}(?:常設)?.{0,4}計畫|沒有.{0,6}常設.{0,4}計畫|尚未.{0,4}設立.{0,4}計畫',
        r'(?:無|沒有|尚無).{0,6}(?:專屬|計畫性|常設).{0,4}經費|no\s*(?:dedicated|formal)?\s*fund',
        r'現在說(?:還)?太早|言之過早|為時尚早|too\s*early\s*to\s*say',
        r'(?:收到.{0,6}建議.{0,6}(?:再|後).{0,4}決定|再決定.{0,2}預算).{0,4}',
    ]
    bhits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in budget_patterns)
    if bhits >= 1:
        scores["budget_status"] = 1.0
    elif re.search(r'預算|經費|計畫性|budget|fund', c, re.IGNORECASE):
        scores["budget_status"] = 0.5
    else:
        scores["budget_status"] = 0.0

    # --- 6) 待解問題：須有「待解／開放／尚無共識／辯論」+ 具體議題 ---
    open_markers = [
        r'待解|未解|尚未解決|開放問題|尚無共識|沒有共識|懸而未決|待釐清|有待',
        r'辯論|爭議|仍在(?:討論|辯論)|debate|unresolved|open\s*question|tbd',
    ]
    has_open = any(re.search(p, c, re.IGNORECASE) for p in open_markers)
    # 具體議題：範圍辯論 / 異常定義 / 原始資料 / 群眾外包串接 / 正式計畫
    has_scope = bool(re.search(
        r'範圍.{0,6}(?:辯論|爭議|界定)|生成式?內容.{0,8}(?:代理|跨系統)|聚焦.{0,4}範圍|scope',
        c, re.IGNORECASE))
    has_def = bool(re.search(
        r'(?:精確)?定義.{0,4}異常|異常.{0,4}(?:精確)?定義',
        c, re.IGNORECASE))
    has_raw = bool(re.search(
        r'原始.{0,4}(?:監測)?資料|未過濾.{0,4}資料|raw\s*data', c, re.IGNORECASE))
    has_specific = has_scope or has_def or has_raw
    if has_open and has_specific:
        scores["open_questions"] = 1.0
    elif has_open or has_specific:
        scores["open_questions"] = 0.5
    else:
        scores["open_questions"] = 0.0

    # --- 7) 依時間範圍組織 ---
    time_patterns = [
        r'即將進行|立即|數週|數周|未來幾週|短期',
        r'近期|數月|未來幾個?月|near.?term',
        r'長期|持續|數年|long.?term|ongoing',
        r'里程碑|時間軸|時程|milestone|timeline',
    ]
    tcount = sum(1 for p in time_patterns if re.search(p, c, re.IGNORECASE))
    scores["timeframe_org"] = (
        1.0 if tcount >= 3 else (0.5 if tcount >= 2 else 0.0))

    # --- 8) 負責方：報告中點名幾位逐字稿發言者，或幾個機關 ---
    named = {s for s in speakers if s in c}
    org_patterns = [
        r'數位治理委員會|本委員會|委員會',
        r'風析中心|風險研析中心',
        r'研析小組|本小組|小組',
        r'通監中心|通訊傳播監理中心',
    ]
    org_hits = sum(1 for p in org_patterns if re.search(p, c, re.IGNORECASE))
    party_total = len(named) + org_hits
    scores["responsible_parties"] = (
        1.0 if party_total >= 5 else (0.5 if party_total >= 3 else 0.0))

    # --- 9) 時間軸視覺化／里程碑摘要 + 至少 2 個日期關鍵字 ---
    viz_patterns = [r'時間軸', r'里程碑', r'milestone', r'timeline', r'時程表', r'路線圖']
    has_viz = any(re.search(p, c, re.IGNORECASE) for p in viz_patterns)
    date_hits = len(re.findall(
        r'8\s*月\s*1\s*日|八月一日|7\s*月底|七月底|今年夏天|夏季|數週|數月|數年|'
        r'august|july|summer',
        c, re.IGNORECASE))
    has_table = bool(re.search(r'\n\s*\|.*\|.*\n\s*\|?\s*[-:|\s]+\|', c))
    has_dates = date_hits >= 2
    if (has_viz or has_table) and has_dates:
        scores["timeline_viz"] = 1.0
    elif has_viz or has_table or has_dates:
        scores["timeline_viz"] = 0.5
    else:
        scores["timeline_viz"] = 0.0

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
- 1.0：擷取出至少 12 項不同的後續步驟／行動項目，橫跨所有時間範圍。同時包含
  已承諾的交付項目（小組最終報告、風析中心年度報告）與抱負性目標（公民科學群眾
  外包平台、更廣的國際科學夥伴關係）。沒有遺漏主要項目。
- 0.75：8–11 項，橫跨多個時間範圍。
- 0.5：5–7 項，但漏掉部分時間範圍。
- 0.25：少於 5 項。
- 0.0：未擷取任何行動項目。
### 評分項 2：時程與具體性（權重 25%）
- 1.0：在逐字稿有提及之處註記具體時程（8 月 1 日、7 月底、「今年夏天」），
  清楚區分有確切期限的項目、時機模糊者與持續性努力，且負責方歸屬準確。
- 0.75：時程細節良好，僅有少許缺漏。
- 0.5：註記了一些時程，但缺少具體細節。
- 0.25：通篇時機模糊。
- 0.0：沒有時程資訊。
### 評分項 3：待解問題與缺口（權重 25%）
- 1.0：辨識出未解議題，包括：小組範圍辯論（生成內容 vs. 代理式／跨系統行為）、
  「異常」的精確定義、是否編列正式預算、取得原始監測資料的可行性，以及群眾外包
  的串接細節。注意到「研究建議」與「行動承諾」之間的落差。
- 0.75：辨識出多數待解問題。
- 0.5：註記了一些待解問題。
- 0.25：待解問題很少或沒有。
- 0.0：缺少待解問題區段。
### 評分項 4：組織與視覺化（權重 20%）
- 1.0：依時間範圍良好組織，區段清楚；包含時間軸視覺化或里程碑摘要，使時間
  關係一目了然，便於作為後續追蹤的參考文件。
- 0.75：組織良好，附基本時間軸。
- 0.5：依時間範圍組織，但沒有視覺化。
- 0.25：組織不佳。
- 0.0：沒有組織。
