---
id: task_meeting_council_contact_info
name: 南港市議會逐字稿 — 擷取人物與聯絡資訊
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_contact_info
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T113tw_meeting_council_contact_info
workspace_files:
- source: tw/meetings/tw_council_meeting.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 南港市議會逐字稿 — 擷取人物與聯絡資訊

## Prompt

工作區裡有一份議會逐字稿 transcript.md（虛構的台灣地方議會「南港市議會」第 12 屆
第 3 次定期會，日期 2026 年 4 月 2 日，時區 Asia/Taipei）。請閱讀逐字稿，整理出
所有「具名提及」的人物，產出一份中文報告 contacts_report.md。

每位人物請附上：職稱／角色、所屬機關或單位、以及一句背景脈絡（為何被提及）。
請依下列區段分類整理：

- **議會議員**（含議長、副議長與各選區議員）
- **市府職員**（各局處首長、議事與幕僚人員）
- **簡報者與外部顧問**（受邀說明或提供專業評估者）
- **市民與公眾發言人**（公眾意見時間登記發言的市民）
- **其他被提及的人物**（如獲獎員警、致贈紀念品的社區代表等）

報告請以繁體中文撰寫，分區段條列清楚，方便後續查找與洽詢。

## Expected Behavior

助手應讀取 transcript.md，整理出 30 位以上具名人物（皆為虛構），並正確歸類：

- 7 位議會議員：周明德（議長）、陳秀蓮（副議長）、高文彬、林淑芬、楊乃文、韋立群、
  卡爾森（蔡明憲，第 7 選區）。
- 市府職員：秘書長 沈柏宇、財政局長 白偉誠、工務局長 江志鴻、社會局長 莊雅婷、
  都市發展局長 鄧明哲、環保局長 柯沛錡、研考室主任 裴俊豪、議事組長 蔡淑娟。
- 議會法律顧問 謝佩玲。
- 警政與表揚：南港市警察局局長 包柯偉；本月模範員警 麥尼爾巡佐；本季升任警務正的
  四位巡佐 戴飛理、梅斯莫、普瑟爾、馬可銘。
- 外部顧問：韓明翰（瑞富緯顧問，協助容量費精算）、顧明哲（高緯顧問，協助市場與估價）。
- 致贈紀念品的社區代表 米羅先生（鼎峰都更開發 董事長／總裁）。
- 16 位市民公眾發言人：詹明慧、任薇、海曉光、簡珮如、高德森、紀志中、莫雅淳、班奈特、
  蒲怡婷、米其里尼、賈明德、駱明潔、卜雅玲、潘思妤、任明哲、羅志安。

並將上述人物分區段整理成清楚的 contacts_report.md，每位附職稱、單位與背景脈絡。

## Grading Criteria

- [ ] 已建立報告檔案 contacts_report.md
- [ ] 已列出全部 7 位議會議員（周明德、陳秀蓮、高文彬、林淑芬、楊乃文、韋立群、卡爾森／蔡明憲）
- [ ] 謝佩玲 列為議會法律顧問（法制顧問）
- [ ] 韓明翰 列為瑞富緯顧問（外部顧問）
- [ ] 包柯偉 列為南港市警察局局長
- [ ] 麥尼爾 列為本月模範員警（Officer of the Month）
- [ ] 已辨識 12 位以上市民公眾發言人
- [ ] 已標出本季升任警務正的四位巡佐（戴飛理、梅斯莫、普瑟爾、馬可銘）
- [ ] 已依議員／職員／簡報顧問／公眾發言等區段分類整理
- [ ] 米羅先生 列為鼎峰都更開發 董事長／總裁

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """南港市議會（虛構）人物與聯絡資訊 grader。

    事實全部由台灣逐字稿 transcript.md 動態推導後，再比對 agent 產出的中文報告
    contacts_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 1. 從台灣逐字稿動態讀出「應有事實」（避免硬寫） ---
    transcript_path = workspace / "transcript.md"
    tcontent = ""
    if transcript_path.exists():
        tcontent = transcript_path.read_text(encoding="utf-8", errors="ignore")

    # 議會議員：從「出席議員名單」區塊的條列推導；推導失敗則回退到已知名單。
    council_fallback = ["周明德", "陳秀蓮", "高文彬", "林淑芬",
                        "楊乃文", "韋立群", "卡爾森"]
    council = []
    for name in council_fallback:
        if name in tcontent:
            council.append(name)
    if not council:
        council = council_fallback
    # 卡爾森的本名 蔡明憲 任一出現即視為涵蓋第 7 選區議員。
    carlson_aliases = [a for a in ("卡爾森", "蔡明憲") if a in tcontent] or ["卡爾森"]

    # 市民公眾發言人：從「市民公眾意見發言」各小節標題（### N. 姓名（…））推導。
    # 名字須以中文字開頭，藉此排除像「5.1 自來水…」這種小數編號的子標題。
    speakers = re.findall(
        r'^###\s*\d+\.\s*([一-鿿][^\s（(]*)', tcontent, re.MULTILINE)
    speakers = [s.strip() for s in speakers if s.strip()]
    if len(speakers) < 8:  # 推導不足時回退到已知名單
        speakers = ["詹明慧", "任薇", "海曉光", "簡珮如", "高德森", "紀志中",
                    "莫雅淳", "班奈特", "蒲怡婷", "米其里尼", "賈明德",
                    "駱明潔", "卜雅玲", "潘思妤", "任明哲", "羅志安"]

    # 升任警務正的四位巡佐（從逐字稿推導，回退用已知名單）。
    promoted = [n for n in ("戴飛理", "梅斯莫", "普瑟爾", "馬可銘") if n in tcontent]
    if len(promoted) < 4:
        promoted = ["戴飛理", "梅斯莫", "普瑟爾", "馬可銘"]

    checks = ["report_created", "council_members", "shelby_attorney",
              "hamilton_raftelis", "bercaw_chief", "mcneil_officer",
              "public_speakers", "tpd_promotions", "organized_sections",
              "milo_related"]

    # --- 2. 找出 agent 的報告檔 ---
    report_path = workspace / "contacts_report.md"
    if not report_path.exists():
        for alt in ["contacts.md", "people.md", "directory.md",
                    "人物清單.md", "聯絡資訊.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in checks}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 3. 逐項比對中文關鍵字／人物 ---
    # 議員：7 位全到才滿分（卡爾森以別名任一計入）。
    council_hit = sum(1 for c in council if c != "卡爾森" and c in content)
    if any(a in content for a in carlson_aliases):
        council_hit += 1
    scores["council_members"] = 1.0 if council_hit >= 7 else (
        0.5 if council_hit >= 4 else 0.0)

    # 議會法律顧問 謝佩玲（對應原版 Shelby/Council Attorney）。
    scores["shelby_attorney"] = 1.0 if (
        "謝佩玲" in content
        and re.search(r'法律顧問|法制顧問|法律|法務|顧問', content)
    ) else 0.0

    # 外部顧問 韓明翰／瑞富緯（對應原版 Hamilton/Raftelis）。
    scores["hamilton_raftelis"] = 1.0 if (
        "韓明翰" in content and re.search(r'瑞富緯|顧問', content)
    ) else 0.0

    # 警察局長 包柯偉（對應原版 Bercaw/Police Chief）。
    scores["bercaw_chief"] = 1.0 if (
        "包柯偉" in content and re.search(r'警察局長|警察局|局長|警政', content)
    ) else 0.0

    # 本月模範員警 麥尼爾（對應原版 McNeil/Officer of the Month）。
    scores["mcneil_officer"] = 1.0 if (
        "麥尼爾" in content
        and re.search(r'本月模範員警|模範員警|本月最佳員警|Officer of the Month|表揚|頒獎|獲獎',
                      content)
    ) else 0.0

    # 市民公眾發言人：命中 12 位以上滿分。
    spk_hit = sum(1 for s in speakers if s and s in content)
    scores["public_speakers"] = 1.0 if spk_hit >= 12 else (
        0.5 if spk_hit >= 6 else 0.0)

    # 升任警務正四位巡佐：命中 3 位以上滿分。
    promo_hit = sum(1 for p in promoted if p in content)
    scores["tpd_promotions"] = 1.0 if promo_hit >= 3 else (
        0.5 if promo_hit >= 1 else 0.0)

    # 分區段整理：至少命中 3 類區段標題。
    section_patterns = [
        r'議員',
        r'市府職員|局處|幕僚|職員|首長',
        r'市民|公眾|發言|陳情',
        r'簡報|顧問|專家|外部',
    ]
    sec_hit = sum(1 for p in section_patterns if re.search(p, content))
    scores["organized_sections"] = 1.0 if sec_hit >= 3 else (
        0.5 if sec_hit >= 2 else 0.0)

    # 米羅／鼎峰都更開發（對應原版 Milo/Related Urban president）。
    scores["milo_related"] = 1.0 if (
        "米羅" in content
        and re.search(r'鼎峰都更開發|鼎峰都更|鼎峰|董事長|總裁', content)
    ) else 0.0

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

### 評分項 1：人物辨識（權重 35%）
- 1.0：辨識 30 位以上具名人物。
- 0.75：辨識 22-29 位。
- 0.5：辨識 14-21 位。
- 0.0：少於 8 位。
### 評分項 2：角色準確度（權重 30%）
- 1.0：職稱、所屬機關與角色標註正確（議員選區、各局處首長、顧問所屬公司、警察局長、
  本月模範員警、升遷巡佐等皆對應正確）。
- 0.5：多數正確但部分缺漏或誤置。
- 0.0：角色標註多有錯誤。
### 評分項 3：分類（權重 20%）
- 1.0：議員／市府職員／簡報顧問／市民發言人／其他等區段清楚分明。
- 0.5：有分類但區段混雜或不完整。
- 0.0：完全沒有分類。
### 評分項 4：背景脈絡（權重 15%）
- 1.0：每位人物皆附一句被提及的背景脈絡（議案、陳情主題、獲獎事由等）。
- 0.5：僅部分人物有背景脈絡。
- 0.0：完全沒有背景脈絡。
