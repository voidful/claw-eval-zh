---
id: task_meeting_gov_recommendations
name: 數位治理委員會（虛構）：生成式 AI 治理公聽會建議擷取
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_gov_recommendations
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T133tw_meeting_gov_recommendations
workspace_files:
- source: tw/meetings/tw_gov_hearing.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 數位治理委員會（虛構）：生成式 AI 治理公聽會建議擷取

## Prompt

工作區裡有一份公聽會逐字稿 transcript.md，來自虛構的「數位治理委員會」
首場「生成式 AI 治理」公開公聽會。會議過程中，研析小組成員與各單位報告者，
針對委員會在生成式 AI 風險治理上「應採取的作為」提出了許多建議（有些是明說的，
有些則藏在討論裡，需要從脈絡判讀）。

請讀過 transcript.md，把所有建議擷取到一個名為 recommendations.md 的檔案。
每一項建議請列出：

- **建議**：清楚、可執行的陳述
- **提出者**：發言者姓名（如：張庭瑋、郭佳穎、林淑芬等）
- **脈絡**：簡述為何提出此建議
- **類別**：分類為下列其一——資料收集、資料標準、感測技術、夥伴關係、
  公眾參與、科學方法、其他

請依「類別」將建議分組；在每個類別內，依其在逐字稿中的出場順序排列。
最後，附上一段簡短的**摘要**，點出最被強調、或被多位發言者重複呼應的建議主題。

報告請以繁體中文（zh-TW）撰寫，發言者姓名請沿用逐字稿中的中文姓名。

## Expected Behavior

助手應讀取 transcript.md，辨識明示與隱含的建議，分類、歸屬到正確的發言者，
並寫入 recommendations.md。關鍵建議（皆出自虛構逐字稿）包括：

**資料收集：**
- 向公眾群眾外包非機敏的開源資料（張庭瑋）
- 開發公民科學群眾外包平台／App，讓民眾上傳遇到的 AI 異常案例（郭佳穎、陳冠宇）
- 同時收集多來源、多平台、多地點的資料（含時間戳、定位、版本資訊、互動序列）（郭佳穎）
- 在風險熱點領域進行每次為期 3 個月的 24/7 連續監測，以建立常態行為基線（張庭瑋）

**資料標準：**
- 所有 AI 風險資料應符合 FAIR 原則——可尋、可取、可互通、可重用（郭佳穎）
- 建立有組織的資料儲存庫以便系統化檢索（郭佳穎）
- 在每筆觀測旁收集完整的後設資料（metadata）（郭佳穎）
- 委員會應提供高資料品質的標準；先有高品質標準、再談發現（陳冠宇、林淑芬）

**感測技術：**
- 評估既有的大型科學運算與監測基礎設施能否用於風險偵測（張庭瑋）
- 在風險熱點領域部署專門打造的偵測探針（張庭瑋）
- 善用既有的科學觀測與運算基礎設施（很多本為時域異常偵測而設計）（郭佳穎）
- 以已知案例校準各監測系統（用受控測試流量比對偵測反應）（張庭瑋）
- 讓研究端取得未經過濾的原始監測資料，而非僅處理過的資料（鄭立群建議；黃建宏）

**夥伴關係：**
- 建立跨國資料共享聯盟「五方資料圈」（台、日、韓、新、澳）（張庭瑋）
- 跨部會合作——與 NCRA、勞動、著作權、能源主管機關打通資料（張庭瑋）
- 建立「五方資料圈」以外的更廣國際科學夥伴關係（張庭瑋、李宗翰）

**公眾參與：**
- 委員會應帶頭把 AI 通報「去污名化」，讓業者願意誠實揭露（張庭瑋、蔡明翰）
- 運用公眾對委員會的長期信任，去除 AI 通報的污名（蔡明翰）
- 把此議題當作向公眾說明「科學方法」的好機會（郭佳穎）

**科學方法：**
- 在辨識異常前，先徹底刻畫「正常」的背景行為（陳冠宇）
- 把先進偵測能力拿去同儕審查、發表在學術期刊（張庭瑋）
- 監督式與非監督式機器學習並用，做案例異常偵測（張庭瑋、郭佳穎、白雅雯）
- 為案例庫開發 AI/ML 分析能力（張庭瑋）
- 一定要組跨領域研究團隊（蔡明翰）
- 把搜尋範圍擴大到生態系的「行為特徵」、跨系統行為，超出單一服務邊界（高志遠）

## Grading Criteria

- [ ] 已建立輸出檔案 recommendations.md
- [ ] 擷取出至少 12 項不同的建議
- [ ] 建議分類成有意義的群組（資料收集、資料標準、感測技術、夥伴關係、公眾參與、科學方法等）
- [ ] 包含群眾外包／公民科學平台的建議
- [ ] 包含資料標準（FAIR 或後設資料／高資料品質）的建議
- [ ] 包含感測器／偵測探針評估的建議
- [ ] 包含國際／跨國夥伴關係（五方資料圈）的建議
- [ ] 包含去污名化（讓業者願意誠實通報）的建議
- [ ] 建議歸於逐字稿中的特定發言者（中文姓名）
- [ ] 附上對最被強調主題的摘要

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會（虛構）公聽會建議擷取 grader。

    以工作區內的台灣逐字稿（dest=transcript.md）動態推導「應有的發言者名單」，
    再比對 agent 產生的中文報告 recommendations.md；其餘查核項比對逐字稿確實
    出現之中文關鍵字。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "recommendation_count", "categorization",
        "crowdsourcing", "data_standards", "sensor_eval", "international",
        "stigma", "attribution", "summary",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "recommendations.md"
    if not report.exists():
        for alt in ["recs.md", "recommendation.md", "建議.md",
                    "建議清單.md", "ai_recommendations.md", "recommendations.txt"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出「應有的發言者名單」（避免硬寫） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "meeting_transcript.md", "hearing.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    # 逐字稿以「**姓名（角色）：**」或「姓名（…）問／答／向…建議」標示發言者。
    # 抓出三個中文字的姓名（台灣常見姓名長度），收斂成候選清單。
    speaker_candidates = set()
    for m in re.finditer(r'\*\*([一-鿿]{2,4})（', t):
        speaker_candidates.add(m.group(1))
    for m in re.finditer(r'(?:^|\n)\s*\*\*([一-鿿]{2,4})\s*[（(]', t):
        speaker_candidates.add(m.group(1))
    # 後援：逐字稿存在但解析失敗時，退回逐字稿載明之發言者名單。
    fallback_speakers = {
        "王志明", "陳冠宇", "林淑芬", "張庭瑋", "黃建宏", "周怡安",
        "蔡明翰", "郭佳穎", "高志遠", "李宗翰", "鄭立群", "白雅雯",
        "蕭文哲", "吳孟蓉",
    }
    # 動態候選中夾雜「公民科學」「待解問題」等非姓名片段（它們也以
    # **粗體（** 形式出現），故與已知姓名集合取交集以濾除雜訊；交集即為
    # 「在逐字稿中、以發言者身分出現、且確為人名」者。逐字稿解析失敗時退回後援。
    parsed = {s for s in speaker_candidates
              if re.search(re.escape(s) + r'\s*[（(]', t)}
    speakers = parsed & fallback_speakers
    if len(speakers) < 5:
        speakers = {s for s in fallback_speakers if s in t}
    if not speakers:
        speakers = fallback_speakers

    scores = {"report_created": 1.0}

    # --- 建議數量：條列項（- / *）或編號項，取較大者，需 >= 12 ---
    bullet_items = len(re.findall(r'(?:^|\n)\s*[-*]\s+\S', c))
    numbered_items = len(re.findall(r'(?:^|\n)\s*\d+[\.\)、]\s*\S', c))
    rec_count = max(bullet_items, numbered_items)
    scores["recommendation_count"] = (
        1.0 if rec_count >= 12 else (0.5 if rec_count >= 6 else 0.0))

    # --- 分類：報告中出現幾個有意義的類別關鍵字 ---
    category_patterns = [
        r'資料收集|資料蒐集|收集資料|data\s*collect',
        r'資料標準|資料品質|data\s*standard',
        r'感測|偵測探針|sensor|探針|儀器',
        r'夥伴|合作|聯盟|partner',
        r'公眾參與|去?污名|public\s*engage|outreach',
        r'科學方法|方法論|機器學習|同儕審查|scientific\s*method|methodolog',
    ]
    cat_count = sum(
        1 for p in category_patterns if re.search(p, c, re.IGNORECASE))
    scores["categorization"] = (
        1.0 if cat_count >= 4 else (0.5 if cat_count >= 2 else 0.0))

    # --- 群眾外包／公民科學（逐字稿確有：群眾外包、公民科學、平台／App） ---
    crowd_patterns = [
        r'群眾外包|眾包|crowdsourc',
        r'公民科學|citizen\s*science',
        r'平台|平臺|app|應用程式',
        r'民眾.{0,6}上傳|公眾.{0,6}通報|開源資料',
    ]
    crowd_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                     for p in crowd_patterns)
    scores["crowdsourcing"] = (
        1.0 if crowd_hits >= 2 else (0.5 if crowd_hits >= 1 else 0.0))

    # --- 資料標準（FAIR／可尋可取可互通可重用／後設資料／高資料品質） ---
    fair_patterns = [
        r'fair\b',
        r'可尋|可取|可互通|可重用|findab|accessib|interoper|reusab',
        r'後設資料|中繼資料|metadata',
        r'資料標準|資料品質|高品質.{0,4}資料|資料儲存庫|data\s*standard|data\s*quality',
    ]
    fair_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                    for p in fair_patterns)
    scores["data_standards"] = (
        1.0 if fair_hits >= 2 else (0.5 if fair_hits >= 1 else 0.0))

    # --- 感測器／偵測探針評估（逐字稿：偵測探針、監測基礎設施、校準、儀器） ---
    sensor_patterns = [
        r'偵測探針|專門打造.{0,6}探針|部署.{0,6}探針|purpose.?built|dedicated\s*sensor',
        r'監測基礎設施|運算.{0,4}基礎設施|科學.{0,4}觀測|觀測站|telescope|observator',
        r'評估.{0,8}(?:儀器|設施|衛星|感測)|校準.{0,6}監測|大型科學',
        r'感測器|感測|儀器|sensor',
    ]
    sensor_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                      for p in sensor_patterns)
    scores["sensor_eval"] = (
        1.0 if sensor_hits >= 2 else (0.5 if sensor_hits >= 1 else 0.0))

    # --- 國際／跨國夥伴（逐字稿：五方資料圈、跨國、跨部會、國際科學夥伴） ---
    intl_patterns = [
        r'五方資料圈|台日韓新澳|台、日、韓、新、澳',
        r'跨國|國際.{0,4}(?:夥伴|合作|聯盟|科學)|international',
        r'跨部會|跨機關|跨領域.{0,2}機關',
        r'資料共享.{0,2}(?:聯盟|協議|協定)|global\s*(?:partner|cooperat|collaborat)',
    ]
    intl_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                    for p in intl_patterns)
    scores["international"] = (
        1.0 if intl_hits >= 2 else (0.5 if intl_hits >= 1 else 0.0))

    # --- 去污名化（逐字稿：去污名、污名、不敢通報、誠實揭露） ---
    stigma_patterns = [
        r'去?污名|汙名|destigma|stigma',
        r'不敢通報|低度通報|壓低通報|reluctan',
        r'誠實.{0,4}(?:通報|揭露|上報)|願意.{0,4}(?:通報|揭露)',
        r'騷擾|恐嚇|威脅|harass',
    ]
    stigma_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                      for p in stigma_patterns)
    scores["stigma"] = (
        1.0 if stigma_hits >= 2 else (0.5 if stigma_hits >= 1 else 0.0))

    # --- 歸屬：報告中點名幾位逐字稿裡的發言者（中文姓名） ---
    named = {s for s in speakers if s in c}
    scores["attribution"] = (
        1.0 if len(named) >= 5 else (0.5 if len(named) >= 3 else 0.0))

    # --- 摘要：須有摘要／結論／最被強調／重點等字樣 ---
    summary_patterns = [
        r'摘要|結論|總結|重點|最被?強調|最常.{0,4}(?:重複|提及|呼應)|'
        r'整體.{0,2}觀察|主要主題|關鍵主題|takeaway|summary|conclusion',
    ]
    scores["summary"] = (
        1.0 if any(re.search(p, c, re.IGNORECASE)
                   for p in summary_patterns) else 0.0)

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

### 評分項 1：建議擷取完整性（權重 30%）
- 1.0：擷取出至少 15 項不同、可執行的建議，涵蓋資料收集、資料標準、感測技術、
  夥伴關係、公眾參與、科學方法。沒有遺漏主要建議。
- 0.75：10–14 項建議，涵蓋多數類別。
- 0.5：6–9 項建議，部分類別著墨不足。
- 0.25：少於 6 項，或有重大缺口。
- 0.0：未擷取任何建議。
### 評分項 2：分類品質（權重 20%）
- 1.0：建議清楚分類成有意義、不重疊的群組，類別直觀且標示得當。
- 0.5：有類別，但模糊或有明顯重疊。
- 0.0：沒有分類。
### 評分項 3：準確性與歸屬（權重 30%）
- 1.0：建議準確反映逐字稿所述，正確歸於對的中文姓名發言者（如張庭瑋、郭佳穎、
  蔡明翰、鄭立群、高志遠），並附適當脈絡。
- 0.5：有一些不準確或缺少歸屬。
- 0.0：建議為捏造或全然誤歸。
### 評分項 4：綜整與摘要（權重 20%）
- 1.0：結語摘要點出最被強調的 2–3 個主題（例如高品質可重現資料、公民科學群眾外包、
  去污名化），並指出哪些建議被多位發言者呼應。
- 0.5：有摘要但流於表面。
- 0.0：沒有摘要。
