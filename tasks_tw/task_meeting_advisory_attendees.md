---
id: task_meeting_advisory_attendees
name: 數位治理顧問委員會逐字稿 — 整理結構化與會者名單
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_advisory_attendees
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T120tw_meeting_advisory_attendees
workspace_files:
- source: tw/meetings/tw_advisory_meeting.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 數位治理顧問委員會逐字稿 — 整理結構化與會者名單

## Prompt

工作區裡有一份政府諮詢委員會會議的逐字稿，存放在 `meeting-transcript.md`。這是
虛構的「數位治理委員會 智慧城市暨資安顧問委員會（DGC-SCAB）」第 14 次會議，
日期 2025 年 5 月 30 日，時區 Asia/Taipei，地點在台北市南港數位治理大樓，部分委員
以視訊連線出席。會議主題是 1755-1850 MHz 聯邦級頻段的政府與商用寬頻共用與遷移。

請幫我分析這份逐字稿，並在一個名為 `attendees.md` 的檔案中建立一份結構化的與會者
名單。針對每位與會者，請包含：

- **全名**（含頭銜或職務，例如「主席」「委員」「政務次長」「副署長」「先生」）
- **會議中的角色**（主席、委員、列席官員、公眾參與者）
- **所屬機關或公司與職稱**（依逐字稿所述）
- **與會方式**（親自到場 in-person 或 視訊連線 remote/phone）
- **發言角色**（是否做了實質發言、提問，或僅在點名時報出自己的身分）

請將名單整理為以下區段：委員會主席（Committee Leadership）、委員（親自到場）、
委員（視訊連線）、列席官員（非委員）、公眾參與者。最後附上與會者總數的彙總計數。

報告請以繁體中文（zh-TW）撰寫，分區段條列清楚，方便後續查找與點名核對。

## Expected Behavior

助手應讀取 meeting-transcript.md，從「一、出席名單」區塊（含親自到場、視訊連線、
列席官員、公眾參與者四類）與「二、會議逐字內容」的點名與對話交叉比對，整理出所有
具名人物（皆為虛構），並正確歸類與會方式與發言角色：

- 委員會主席（親自到場）：王志明 主席，鼎峰緊急救難服務協會（鼎峰救難協會）理事長。
- 委員（親自到場，6 位）：林淑芬（DGC 頻率管理處 處長）、陳建宏（中華電信寬頻技術
  研究所 所長）、周明德（南港大學電機工程學系 教授）、鄭雅文（鼎峰科技 標準與法規部
  協理）、黃國昌（台灣公共利益網路基金會〔公網會〕執行長）、吳孟儒（玉山防務系統
  首席工程師）。
- 委員（視訊連線，9 位，姓名後標星號*）：何信宏（南港大學頻譜政策研究中心 主任）、
  馮淑惠（遠傳行動通訊 政策研究部 副總）、麥國輝（台電綜合研究所 通訊組 組長）、
  沈柏睿（中央科技大學無線通訊實驗室 教授）、雷宗翰（雷神防務台灣分公司 經理）、
  湯志賢（台灣有線電視業者協會 技術顧問）、鮑昌霖（工研院 通訊技術組 資深研究員）、
  賴明達（南港市政府 智慧城市辦公室 主任）、柯怡君（資安署 風險評估科 科長）。
- 列席官員（非委員，親自到場，4 位）：史國良（經濟與數位發展部 政務次長）、
  聶國維（頻譜管理署〔頻管署〕副署長）、鮑彥廷（指定政府聯絡官）、卜啟文（行政院
  科技與政策辦公室〔科政辦〕諮詢委員）。
- 公眾參與者：施敬堯 先生（一般民眾，於公眾意見時段發言）。

與會方式判定：星號（*）與點名回應為「在線上／連線」者屬視訊連線；其餘為親自到場。
發言角色：主席、史國良、聶國維、卜啟文等有實質致詞或政策發言；多數委員在技術討論
與工作小組分工時有發言；少數委員僅在點名時報出身分。委員具名人數共 16 位（含主席），
連同 4 位列席官員與 1 位公眾參與者，與會者總數約 21 位。

## Grading Criteria

- [ ] 已建立報告檔案 attendees.md
- [ ] 王志明 正確辨識為主席（Chair），並標出鼎峰救難協會（鼎峰緊急救難服務協會）隸屬
- [ ] 至少具名辨識出 15 位委員會成員（含主席）
- [ ] 正確辨識視訊連線（remote/phone）委員（何信宏、馮淑惠、麥國輝、沈柏睿、雷宗翰、湯志賢 等）
- [ ] 已列出列席的非委員官員（史國良、聶國維、鮑彥廷、卜啟文）
- [ ] 多數與會者皆附所屬機關／公司隸屬
- [ ] 正確記下與會方式（親自到場 對比 視訊連線／電話）
- [ ] 施敬堯 先生 辨識為公眾參與者
- [ ] 已包含與會者總數的彙總計數

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理顧問委員會（虛構）與會者名單 grader。

    事實全部由台灣逐字稿 meeting-transcript.md 動態推導後，再比對 agent 產出的
    中文報告 attendees.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 1. 從台灣逐字稿動態讀出「應有事實」（避免硬寫） ---
    transcript_path = workspace / "meeting-transcript.md"
    tcontent = ""
    if transcript_path.exists():
        tcontent = transcript_path.read_text(encoding="utf-8", errors="ignore")

    def _names(header_regex):
        """擷取某出席名單小節下，條列項中的『某某 委員/主席/…』中文姓名。"""
        m = re.search(header_regex + r"\*\*\n(.*?)\n\n", tcontent, re.DOTALL)
        if not m:
            return []
        out = []
        for line in m.group(1).splitlines():
            nm = re.match(
                r"-\s*([一-鿿]{2,4})\s*(?:委員|主席|政務次長|副署長|"
                r"指定聯絡官|先生|女士)", line)
            if nm:
                out.append(nm.group(1))
        return out

    # 主席
    chair_list = _names(r"委員會主席（Chair）") or ["王志明"]
    chair = chair_list[0] if chair_list else "王志明"

    # 親自到場委員（6 位）
    inperson = _names(r"委員（親自到場 in-person）")
    if len(inperson) < 5:
        inperson = ["林淑芬", "陳建宏", "周明德", "鄭雅文", "黃國昌", "吳孟儒"]

    # 視訊連線委員（9 位）
    remote = _names(r"委員（視訊連線 remote / phone）")
    if len(remote) < 6:
        remote = ["何信宏", "馮淑惠", "麥國輝", "沈柏睿", "雷宗翰",
                  "湯志賢", "鮑昌霖", "賴明達", "柯怡君"]

    # 列席官員（4 位，非委員）
    officials = _names(r"列席官員（Also Present，非委員）")
    if len(officials) < 3:
        officials = ["史國良", "聶國維", "鮑彥廷", "卜啟文"]

    # 取前 6 位視訊連線委員作為核心查核名單。
    remote_core = remote[:6] if len(remote) >= 6 else [
        "何信宏", "馮淑惠", "麥國輝", "沈柏睿", "雷宗翰", "湯志賢"]

    # 全體委員（含主席）名單，用於 member_count。
    all_members = [chair] + inperson + remote

    checks = ["report_created", "chair_identified", "member_count",
              "remote_attendees", "officials_listed", "organizations_included",
              "attendance_mode", "public_participant", "summary_count"]

    # --- 2. 找出 agent 的報告檔 ---
    report_path = workspace / "attendees.md"
    if not report_path.exists():
        for alt in ["attendee_list.md", "attendees_list.md",
                    "meeting_attendees.md", "與會者名單.md", "出席名單.md",
                    "與會者.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in checks}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 3. 逐項比對中文關鍵字／人物 ---
    # 主席：王志明 + 「主席」+ 鼎峰救難協會／鼎峰緊急救難。
    chair_ok = (
        chair in content
        and re.search(r"主席|Chair", content)
        and re.search(r"鼎峰救難|鼎峰緊急救難", content)
    )
    scores["chair_identified"] = 1.0 if chair_ok else 0.0

    # 委員具名人數（含主席，共 16 位）：命中 15 位以上滿分。
    found = sum(1 for m in all_members if m and m in content)
    scores["member_count"] = (
        1.0 if found >= 15 else (0.5 if found >= 10 else 0.0))

    # 視訊連線委員：須出現姓名且其附近有「視訊／連線／遠端／電話／線上／*」等標記。
    remote_kw = r"視訊|連線|遠端|遠距|電話|線上|remote|phone|virtual|dial|\*"
    remote_found = 0
    for rm in remote_core:
        if rm and rm in content:
            near = (
                re.search(rm + r".{0,30}(?:" + remote_kw + r")", content)
                or re.search(r"(?:" + remote_kw + r").{0,30}" + rm, content)
            )
            if near:
                remote_found += 1
            elif re.search(r"\*", content):
                remote_found += 0.5
    scores["remote_attendees"] = (
        1.0 if remote_found >= 4 else (0.5 if remote_found >= 2 else 0.0))

    # 列席非委員官員：命中 3 位以上滿分。
    officials_found = sum(1 for o in officials if o and o in content)
    scores["officials_listed"] = (
        1.0 if officials_found >= 3 else (0.5 if officials_found >= 2 else 0.0))

    # 所屬機關／公司：從逐字稿出現的關鍵組織名取交集後再比對報告。
    org_candidates = [
        "鼎峰救難協會", "鼎峰緊急救難", "鼎峰科技", "中華電信", "遠傳", "台電",
        "工研院", "雷神", "玉山防務", "南港大學", "中央科技大學",
        "資安署", "頻譜管理署", "經濟與數位發展部", "數位治理委員會",
        "公共利益網路基金會", "公網會", "有線電視業者協會", "南港市政府",
        "頻譜政策研究中心", "智慧城市辦公室",
    ]
    orgs = [o for o in org_candidates if o in tcontent] or org_candidates
    org_found = sum(1 for o in orgs if o in content)
    scores["organizations_included"] = (
        1.0 if org_found >= 8 else (0.5 if org_found >= 4 else 0.0))

    # 與會方式標記：須同時出現「親自到場」類與「視訊／連線／電話」類用語。
    inperson_kw = re.search(r"親自到場|現場|到場|實體|in[- ]?person", content)
    remote_mode = re.search(
        r"視訊|連線|遠端|遠距|電話|線上|remote|phone|virtual|dial", content)
    mode_found = (1 if inperson_kw else 0) + (1 if remote_mode else 0)
    scores["attendance_mode"] = (
        1.0 if mode_found >= 2 else (0.5 if mode_found >= 1 else 0.0))

    # 公眾參與者 施敬堯。
    scores["public_participant"] = 1.0 if "施敬堯" in content else 0.0

    # 彙總計數：報告中須出現「總數／合計／共 N 位」等含數字的彙總敘述。
    count_patterns = [
        r"總(?:數|計|人數).{0,12}\d+",
        r"\d+.{0,12}總(?:數|計|人數)",
        r"(?:合計|共|總共).{0,8}\d+\s*(?:位|人|名)",
        r"\d+\s*(?:位|人|名).{0,8}與會",
        r"與會(?:者|人數).{0,12}\d+",
    ]
    scores["summary_count"] = (
        1.0 if any(re.search(p, content) for p in count_patterns) else 0.0)

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

### 評分項 1：與會者辨識完整度（權重 35%）
- 1.0：所有委員、列席官員與公眾參與者皆以正確姓名與角色辨識，無一遺漏（21 位）。
- 0.75：辨識出多數與會者（18 位以上），僅少許遺漏。
- 0.5：辨識出多數，但有數位缺漏（14-17 位）。
- 0.25：僅辨識出最突出的發言者。
- 0.0：辨識出的與會者不到一半。
### 評分項 2：細節準確度（權重 30%）
- 1.0：所有機關、職稱與與會方式皆正確；視訊連線 對比 親自到場 與逐字稿的星號標記
  及點名相符（如何信宏、馮淑惠等 9 位為視訊連線；6 位委員與主席為親自到場）。
- 0.75：多數細節正確，僅一兩處小誤。
- 0.5：機關或與會方式有數處錯誤。
- 0.25：隸屬或角色有許多不準確之處。
- 0.0：細節大致錯誤或為杜撰。
### 評分項 3：組織與結構（權重 20%）
- 1.0：清楚分區——主席、親自到場委員、視訊連線委員、列席官員、公眾參與者，易於瀏覽。
- 0.75：組織良好，僅少許結構問題。
- 0.5：有部分組織，但區段不清楚或不一致。
- 0.25：組織不佳，難以查找。
- 0.0：無有意義的結構。
### 評分項 4：發言角色評估（權重 15%）
- 1.0：準確區分積極參與者（致詞、提問、技術發言）與僅在點名時報出身分者。
- 0.75：多數發言角色正確記下。
- 0.5：嘗試記下參與程度但不完整。
- 0.25：區分參與程度的努力極少。
- 0.0：未評估發言角色。
