---
id: task_meeting_gov_qa_extract
name: 數位治理委員會公聽會（虛構）：問答交流擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_gov_qa_extract
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T132tw_meeting_gov_qa_extract
workspace_files:
- source: tw/meetings/tw_gov_hearing.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 數位治理委員會公聽會（虛構）：問答交流擷取

## Prompt

工作區裡有一份逐字稿檔案 transcript.md，是一場虛構的台灣公聽會：數位治理委員會
「生成式 AI 治理獨立研析小組」第一場對外公開的公聽會（依《行政程序法》公聽會程序
公開舉行，時區 Asia/Taipei）。會議包含多場單位報告，每場報告後有「小組問答」
（召集人與委員、學者、產業代表彼此提問），最後另有一段事先徵集、經會務組彙整的
「公眾問答（public Q&A）」。

請閱讀 transcript.md，把所有問答交流擷取到名為 qa_exchanges.md 的檔案。
每一筆交流請列出：

- **提問者**：姓名與身分／角色（若逐字稿有載明，例如「召集人陳冠宇」「資安專家蕭文哲」）
- **回答者**：姓名與身分／角色
- **主題**：簡短標籤（例如「資料校準流程」「案例庫具體數字」「感測器假影」）
- **問題**：摘述或引用
- **回答**：摘述重點（保留關鍵數字與結論）

請依時間順序組織各筆交流，把「小組問答」與後面的「公眾問答」清楚區隔開來，
並把每筆交流依序編號。

## Expected Behavior

助手應讀取 transcript.md，辨識出有別於事先準備好的報告的問答交流，擷取「小組問答」
與「公眾問答」兩部分，準確把問題與回答歸於正確的具名發言者，精簡摘述問題與回答，
並寫入 qa_exchanges.md。

逐字稿中的關鍵問答交流（皆為虛構）包括：

小組問答（第一場 資料品質）
- 召集人陳冠宇 問 林淑芬（副主任委員）關於對外釋出資料的「校準與品質控管標準作業」，
  林淑芬答：目前各部會各做各的，應建立統一後設資料與校準規範。
- 蔡明翰（資訊社會學者）問 陳冠宇 關於跨領域的資料品質門檻差異，陳冠宇答：差很多，
  不追求單一萬用指標，各領域先各自訂高品質資料標準。
- 李宗翰（鼎峰科技 法遵長）問 陳冠宇 是否會錯過「高風險、高報酬」的治理創新，
  陳冠宇答：應保留一部分高風險高報酬的探索空間。

小組問答（第二場 風析中心案例庫）
- 周怡安（科技記者）問 張庭瑋（風析中心主任）案例庫「到底有多大、涵蓋幾年、真正異常多少」，
  張庭瑋答：超過 800 件、涵蓋近三年，真正異常約 2%–5%（約數十件），但不代表「沒事」。
- 林淑芬 問 張庭瑋 那段解密影像（自動化測試流量被誤判）如何確認不是攻擊，
  張庭瑋答：比對排程紀錄、來源網段與時間戳三者吻合，判定為誤判。
- 蕭文哲（資安專家）問 張庭瑋 如何把「感測器假影」與「真異常」分開、前處理流程，
  張庭瑋答：先建立各監測系統的假影特徵庫濾掉已知誤差再標記。
- 白雅雯（機器學習研究員）問 張庭瑋 打算用什麼 AI/ML 方法，張庭瑋答：監督式用在已知
  類型、非監督式找新模式，兩者並用。
- 李宗翰 問 張庭瑋 如何定義「異常」、以及污名是否壓低通報，張庭瑋答：異常精確定義
  尚無共識；污名確實會壓低通報意願，委員會應帶頭去污名化。

小組問答（第三場 通監中心監測能力與限制）
- 蕭文哲 問 黃建宏（通監中心監理組）原始監測資料保存多久、分析用原始或處理過的資料，
  黃建宏答：原始流量紀錄約保存數個月即輪替刪除，平常多用處理過、過濾過的資料。
- 郭佳穎（資料科學家）問 黃建宏 每月只有 3–5 件是否為通報偏差、探針部署地點如何決定，
  黃建宏答：探針偏向大型業者與高流量節點，確實可能漏掉長尾小型服務，通報偏差存在。
- 吳孟蓉（網路工程學者）問 黃建宏 對不配合自願標示的服務能否偵測異常，黃建宏答：很有限，
  只能靠骨幹側粗粒度流量輪廓推估。
- 李宗翰 問 黃建宏 第一線人員的通報流程與是否完整歸檔，黃建宏答：透過全國 AI 事件
  通報網填報、逐案歸檔，但各業者詳實程度不一。
- 鄭立群（小組顧問）向 黃建宏 建議讓研究端拿到「未過濾的原始監測資料」，黃建宏回應：
  技術上可行但並非毫無挑戰（量太大、涉及個資去識別化）。

公眾問答（public Q&A，由林淑芬主持）
- 公眾提問 1（非人類智慧／自主意圖的證據）：周怡安代表回應「目前沒有決定性證據」，
  強調「非凡的主張需要非凡的證據」。
- 公眾提問 2（委員會的 AI 治理預算）：王志明（執行秘書）代表回應「目前並未設立常設
  計畫、也沒有專屬計畫性經費，現在說還太早」。
- 公眾提問 3（若真發現重大難解風險的處置與揭露協定）：陳冠宇代表回應「原則是透明、
  可重現、跨部會協作」，先由風析中心完成技術重現與同儕檢視再分級揭露。

## Grading Criteria

- [ ] 建立輸出檔案 qa_exchanges.md
- [ ] 辨識出至少 10 筆不同的問答交流
- [ ] 小組問答與公眾問答兩個區段清楚分開
- [ ] 包含周怡安向張庭瑋（風析中心主任）提問案例庫具體數字（規模／年數／真正異常多少）的交流
- [ ] 包含張庭瑋關於案例庫超過 800 件、真正異常約 2%–5% 的回應
- [ ] 包含至少一筆與通監中心（黃建宏）相關的問答（如原始資料保存、探針部署、通報偏差）
- [ ] 包含公眾問答中關於非人類智慧／自主意圖（非凡的主張需要非凡的證據）的提問與回應
- [ ] 問題與回答正確歸於逐字稿中的具名發言者
- [ ] 各筆交流有編號或清楚分隔

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會公聽會（虛構）問答擷取 grader。

    以工作區內的台灣逐字稿（dest=transcript.md）動態推導「應有事實」
    （案例數、異常比例、發言者名單、通監中心監測等），再比對 agent 產生的
    中文報告 qa_exchanges.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "qa_exchanges.md"
    if not report.exists():
        for alt in ["qa.md", "questions_answers.md", "q_and_a.md",
                    "qa_extract.md", "qa_exchanges.txt", "問答交流.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = [
        "report_created", "exchange_count", "section_separation",
        "case_numbers_qa", "case_stats", "ncra_qa", "nhi_question",
        "attribution", "numbering",
    ]
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")
    c_low = c.lower()

    # --- 從逐字稿動態讀出可查核事實（避免硬寫英文原版） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "meeting_transcript.md", "逐字稿.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def first(pattern, text, default=None, group=1):
        m = re.search(pattern, text)
        return m.group(group) if m else default

    # 案例庫規模：逐字稿「超過 800 件」/「800 多件」
    case_total = first(r'(?:超過|逾)?\s*(\d{3,})\s*多?\s*件', t) or "800"
    # 真正異常比例：逐字稿「2% 到 5%」/「2%–5%」/「2%-5%」
    pct_lo = first(r'(\d+)\s*%\s*(?:到|–|-|~|至)\s*\d+\s*%', t) or "2"
    pct_hi = first(r'\d+\s*%\s*(?:到|–|-|~|至)\s*(\d+)\s*%', t) or "5"
    # 通監中心第一線每月通報件數：逐字稿「每月只回報 3 到 5 件」
    rep_lo = first(r'每月只?\s*回?報\s*(\d+)\s*(?:到|–|-|~|至)\s*\d+\s*件', t) or "3"
    rep_hi = first(r'每月只?\s*回?報\s*\d+\s*(?:到|–|-|~|至)\s*(\d+)\s*件', t) or "5"

    scores = {"report_created": 1.0}

    # --- 交流筆數：報告中編號項或問答區塊／提問者標記 ≥ 10 ---
    numbered = re.findall(r'(?:^|\n)\s*(?:\d+\s*[.\):、]|第\s*\d+\s*(?:筆|題|案|則))', c)
    headed = re.findall(
        r'(?:^|\n)#{2,4}\s*.*?(?:交流|問答|q\s*&?\s*a|提問|exchange)', c_low)
    qmark = re.findall(r'提問者|回答者|提問|問\s*[:：]|q\s*[:：]', c_low)
    n_units = max(len(numbered), len(headed))
    scores["exchange_count"] = (
        1.0 if (n_units >= 10 or len(qmark) >= 10)
        else 0.5 if (n_units >= 5 or len(qmark) >= 5)
        else 0.0)

    # --- 區段分隔：須同時出現「小組問答」與「公眾問答」兩類標記 ---
    has_panel = bool(re.search(r'小組問答|小組\s*提問|報告者|小組成員', c))
    has_public = bool(re.search(r'公眾問答|公眾\s*提問|public\s*q', c_low)
                      or re.search(r'公眾問答|公眾\s*提問', c))
    scores["section_separation"] = (
        1.0 if (has_panel and has_public)
        else 0.5 if (has_panel or has_public)
        else 0.0)

    # --- 周怡安 ↔ 張庭瑋 案例庫數字問答：須點名雙方且問及規模／年數／數量 ---
    has_zhou = bool(re.search(r'周怡安', c))
    has_zhang = bool(re.search(r'張庭瑋', c))
    ask_size = bool(re.search(r'多大|多少|規模|案例庫|資料庫|幾年|涵蓋', c))
    scores["case_numbers_qa"] = (
        1.0 if (has_zhou and has_zhang and ask_size)
        else 0.5 if (has_zhou and has_zhang)
        else 0.0)

    # --- 案例庫統計事實：報告須含逐字稿推導之 800 件 與 2%–5% 異常比例 ---
    # 800（容許「超過 800」「800 多」「800 件」等）
    has_total = bool(re.search(r'%s' % re.escape(case_total), c))
    # 2%–5%（容許 2%~5%、2-5%、2% 到 5%、2％至5％ 等寫法）
    pct_pat = r'%s\s*[%%％]?\s*(?:到|–|-|~|至|—)\s*%s\s*[%%％]' % (
        re.escape(pct_lo), re.escape(pct_hi))
    has_pct = bool(re.search(pct_pat, c)) or (
        bool(re.search(r'%s\s*[%%％]' % re.escape(pct_lo), c))
        and bool(re.search(r'%s\s*[%%％]' % re.escape(pct_hi), c)))
    scores["case_stats"] = (
        1.0 if (has_total and has_pct)
        else 0.5 if (has_total or has_pct)
        else 0.0)

    # --- 通監中心／黃建宏 相關問答：須點名黃建宏或通監中心，且至少觸及兩個監測主題 ---
    has_ncra = bool(re.search(r'黃建宏|通監中心|通訊傳播監理中心', c, re.IGNORECASE))
    ncra_topics = sum([
        # 原始資料保存／輪替刪除
        bool(re.search(r'保存|輪替|刪除|數個月|原始(?:流量|資料|紀錄)', c)),
        # 探針部署／涵蓋／長尾
        bool(re.search(r'探針|部署|涵蓋|長尾|高流量節點', c)),
        # 通報偏差
        bool(re.search(r'通報偏差|偏差', c)),
        # 每月 3–5 件 通報量
        bool(re.search(
            r'%s\s*(?:到|–|-|~|至)\s*%s\s*件' % (
                re.escape(rep_lo), re.escape(rep_hi)), c)
            or re.search(r'每月.{0,6}件', c)),
    ])
    scores["ncra_qa"] = (
        1.0 if (has_ncra and ncra_topics >= 2)
        else 0.5 if has_ncra
        else 0.0)

    # --- 非人類智慧／自主意圖 公眾提問：至少命中兩個關鍵概念 ---
    nhi_hits = sum([
        bool(re.search(r'非人類(?:的)?(?:智慧|智能)', c)),
        bool(re.search(r'自主(?:意圖|意識|智慧)', c)),
        bool(re.search(r'非凡的?(?:主張|證據)', c)),
        bool(re.search(r'(?:沒有|無)決定性(?:的)?證據', c)),
    ])
    scores["nhi_question"] = (
        1.0 if nhi_hits >= 2
        else 0.5 if nhi_hits >= 1
        else 0.0)

    # --- 歸屬：逐字稿中的具名發言者，報告須命中 ≥ 6 位 ---
    # 動態從逐字稿擷取「**姓名（…）：**」或「姓名 問／答」的中文人名作參考，
    # 並輔以一份逐字稿確有的具名發言者清單交集，避免空集合。
    roster = set(re.findall(r'([一-鿿]{2,3})（[^）]*?(?:委員|主任|秘書|'
                            r'學者|記者|專家|研究員|長|顧問|召集人|科學家|'
                            r'監理|代表)', t))
    known = ["陳冠宇", "林淑芬", "蔡明翰", "李宗翰", "張庭瑋", "周怡安",
             "蕭文哲", "白雅雯", "黃建宏", "郭佳穎", "吳孟蓉", "鄭立群",
             "高志遠", "王志明"]
    roster |= {k for k in known if k in t}
    named = {nm for nm in roster if nm in c}
    scores["attribution"] = (
        1.0 if len(named) >= 6
        else 0.5 if len(named) >= 3
        else 0.0)

    # --- 編號／分隔：報告須有清楚的編號、標題或分隔線 ---
    n_numbered = len(re.findall(
        r'(?:^|\n)\s*(?:\d+\s*[.\):、]|第\s*\d+\s*(?:筆|題|案|則))', c))
    n_headed = len(re.findall(r'(?:^|\n)#{2,4}\s', c))
    n_sep = len(re.findall(r'(?:^|\n)---', c))
    scores["numbering"] = (
        1.0 if (n_numbered >= 5 or n_headed >= 5)
        else 0.5 if n_sep >= 3
        else 0.0)

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

### 評分項 1：交流完整性（權重 30%）
- **1.0**：擷取至少 12 筆不同問答交流，涵蓋三場小組問答與公眾問答，沒有遺漏重要交流。
- **0.75**：擷取 8–11 筆，涵蓋多數場次。
- **0.5**：擷取 5–7 筆，但漏掉一些關鍵的。
- **0.25**：少於 5 筆，或有重大缺口。
- **0.0**：未擷取任何交流。

### 評分項 2：歸屬準確性（權重 25%）
- **1.0**：所有問答都正確歸於對的發言者（如周怡安問張庭瑋、蕭文哲問黃建宏、
  鄭立群向黃建宏建議），姓名與身分準確。
- **0.5**：數處歸屬錯誤或缺少姓名／身分。
- **0.0**：沒有歸屬或全然錯誤（例如把問答張冠李戴，或出現逐字稿裡根本沒有的人名）。

### 評分項 3：摘要品質（權重 25%）
- **1.0**：問題與回答皆精簡準確，保留關鍵數字與結論（800 件、2%–5%、每月 3–5 件、
  保存數個月即刪除、非凡證據等）。
- **0.5**：有摘要但漏掉關鍵細節或過於模糊。
- **0.0**：沒有摘要，或只是無脈絡的原始引言。

### 評分項 4：組織（權重 20%）
- **1.0**：依時間順序清楚組織，小組問答與公眾問答分開，每筆交流有編號並附主題標籤。
- **0.5**：有一些組織，但區段混雜或難以瀏覽。
- **0.0**：沒有可辨識的組織，或非繁體中文。
