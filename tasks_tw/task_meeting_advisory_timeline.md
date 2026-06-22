---
id: task_meeting_advisory_timeline
name: 數位治理顧問委員會逐字稿 — 時間軸與期限整理
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_advisory_timeline
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T123tw_meeting_advisory_timeline
workspace_files:
- source: tw/meetings/tw_advisory_meeting.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 數位治理顧問委員會逐字稿 — 時間軸與期限整理

## Prompt

工作區裡有一份政府顧問委員會的會議逐字稿 meeting-transcript.md（虛構的台灣
「數位治理委員會 智慧城市暨資安顧問委員會（DGC-SCAB）」第 14 次會議，
2025 年 5 月 30 日於台北市南港召開，時區 Asia/Taipei）。會議核心議題是
1755-1850 MHz 這段聯邦級頻段要如何在政府單位與商用行動寬頻之間共用（spectrum
sharing）與遷移（relocation）。

請以台灣政府顧問委員會的語境閱讀逐字稿，把所有關於**時間軸、期限、時程與里程碑**
的內容，整理成一份結構化報告，存成 timeline.md。報告請涵蓋：

- **依時間先後排列的時間軸**：列出所有提及的日期、期限與里程碑（含過去與未來）
- **各工作小組（WG1~WG5）期限**：各工作小組預計何時交付成果
- **下次會議資訊**：日期、地點、形式
- **歷史背景參照**：提及的過往事件及其日期，用以提供脈絡
- **遷移／過渡時程**：政府機關表示完成遷出本頻段所需的時間長度

每一筆時間軸項目都請註明日期（或時間範圍）、所指事項、是誰提到的（發言人／單位），
以及任何附帶的條件或註記。

## Expected Behavior

助手應讀取 meeting-transcript.md，擷取所有時間相關的參照（明確日期、相對時間範圍、
持續期間），依時間先後組織，並區分過去事件、目前狀態與未來期限。

逐字稿可推導出的關鍵時間軸項目（皆為虛構）：

**歷史／過去：**
- 2023 年 6 月：行政院頒布「五百兆赫頻譜釋出總統府備忘錄」（簡稱「六月備忘錄」），
  設定十年內釋出 500 MHz 頻譜的目標（史國良政務次長提及）
- 會議前約兩年半（2022 年底至 2023 年初）：行政院政策評估得出 500 MHz 重整目標
- 六月備忘錄頒布後六個月內：本部與各機關盤點出 115 MHz 可釋出頻段
- 2024 年 10 月 1 日：惡名昭彰的「十月一日報告」法定期限（1755-1850 評估報告）
- 2014 年：清整 1710-1755 MHz，初估新臺幣 9 億元，實際耗時約 5 年（聶國維副署長提及）
- 過往：政府與產業在 5 GHz Wi-Fi 的合作先例（卜啟文委員提及）

**目前（截至 2025 年 5 月 30 日）：**
- 會議日期：2025 年 5 月 30 日
- 「500 MHz 小組委員會」與「共用小組委員會」暫時停止運作（stood down）
- 已送出台灣大哥大／中華電信業者公會的 STA 量測申請
- 工作小組邀請函將於本週內發出

**未來期限：**
- 約下週內：頻管署發出五個工作小組邀請函、敲定各小組共同主持人
- 約 10 天內：委員會兩位共同主持人回報整體收尾規劃（採納湯志賢委員提案）
- 2025 年 9 月：WG1（氣象衛星，1695-1710 MHz）目標完成（比其他小組早）
- 2025 年 7 月 24 日：下次委員會會議於台中（下午時段）
- 2025 年 7 月 25 至 26 日：ISART 研討會於電信技術研究所（ITS），主題頻譜共用，
  緊接在委員會會議之後
- 2026 年 1 月：WG2 至 WG5（1755-1850 頻段）目標完成（明年 1 月）
- 5 年：執法監察系統第一步退出 1755-1780 MHz（WG2 三階段過渡之第一階段）
- 10 年：各機關全面遷出本頻段（十年過渡期，現行規劃基準線）
- 10 年：500 MHz 整體重整目標（出自 2023 年六月備忘錄）

助手應產出清楚的 timeline.md，每筆含日期、事項、發言人與條件／註記，並依時間先後組織。

## Grading Criteria

- [ ] 建立報告檔案 timeline.md
- [ ] 提及 2023 年 6 月「六月備忘錄」（總統府備忘錄，500 MHz 十年目標）
- [ ] 提及 2024 年 10 月 1 日「十月一日報告」法定期限
- [ ] 記載下次委員會會議（2025 年 7 月 24 日，台中）
- [ ] 提及 WG1 氣象衛星工作小組 2025 年 9 月目標完成
- [ ] 提及 WG2~WG5 其餘工作小組 2026 年 1 月目標完成
- [ ] 提及十年過渡期（全面遷出本頻段）
- [ ] 記載緊接會議之後的 ISART 研討會（7 月 25-26 日，ITS）
- [ ] 時間軸依時間先後組織

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW (fictional) advisory-committee timeline grader.

    查核項（presidential_memo / october_report / next_meeting /
    september_target / january_target / ten_year_transition / isart_meeting /
    chronological_order），但事實改由台灣逐字稿（dest=meeting-transcript.md）動態
    推導，再比對 agent 產生的中文報告 timeline.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 找出 agent 報告檔（容許常見替代檔名）---
    report = workspace / "timeline.md"
    if not report.exists():
        for alt in ["timeline_report.md", "deadlines.md", "milestones.md",
                    "schedule.md", "時間軸.md", "時程.md", "期限.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["report_created", "presidential_memo", "october_report",
            "next_meeting", "september_target", "january_target",
            "ten_year_transition", "isart_meeting", "chronological_order"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態確認「應有事實」確實存在（避免硬寫；逐字稿缺失則不卡關）---
    tx = ""
    tpath = workspace / "meeting-transcript.md"
    if not tpath.exists():
        for alt in ["transcript.md", "meeting_transcript.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    def tx_has(*pats):
        # 逐字稿須含全部 pattern，才視為該事實可查核；無逐字稿時不阻擋
        return all(re.search(p, tx) for p in pats) if tx else True

    # 1) 六月備忘錄：2023 年 6 月，總統府／行政院備忘錄，500 MHz 十年目標
    fact = tx_has(r"2023\s*年\s*6\s*月", r"備忘錄", r"500\s*MHz")
    ok = bool(re.search(r"2023\s*年\s*6\s*月|2023[/\-]0?6|六月備忘錄", c)) and bool(
        re.search(r"備忘錄|總統府|行政院|memo|500\s*MHz|五百兆赫", c, re.IGNORECASE))
    scores["presidential_memo"] = 1.0 if (fact and ok) else 0.0

    # 2) 十月一日報告：2024 年 10 月 1 日法定期限（1755-1850 評估報告）
    fact = tx_has(r"2024\s*年\s*10\s*月\s*1\s*日")
    ok = bool(re.search(r"2024\s*年\s*10\s*月\s*1\s*日|2024[/\-]10[/\-]0?1|十月一日|10\s*月\s*1\s*日",
                        c)) and bool(
        re.search(r"報告|期限|deadline|惡名昭彰|十月一日|1755", c, re.IGNORECASE))
    scores["october_report"] = 1.0 if (fact and ok) else 0.0

    # 3) 下次會議：2025 年 7 月 24 日，台中
    fact = tx_has(r"7\s*月\s*24\s*日", r"台中")
    ok = bool(re.search(r"7\s*月\s*24\s*日|2025[/\-]0?7[/\-]24|July\s*24", c)) and bool(
        re.search(r"台中|下次會議|下次本委員會|next\s*meeting", c, re.IGNORECASE))
    scores["next_meeting"] = 1.0 if (fact and ok) else 0.0

    # 4) WG1 氣象衛星（1695-1710）目標 2025 年 9 月完成
    fact = tx_has(r"2025\s*年\s*9\s*月")
    ok = bool(re.search(r"2025\s*年\s*9\s*月|2025[/\-]0?9|9\s*月.*(?:完成|目標)|September",
                        c, re.IGNORECASE)) and bool(
        re.search(r"氣象衛星|氣象|1695|WG\s*1|WG1|第\s*1\s*工作小組|工作小組\s*1", c, re.IGNORECASE))
    scores["september_target"] = 1.0 if (fact and ok) else 0.0

    # 5) WG2~WG5（1755-1850）目標 2026 年 1 月完成
    fact = tx_has(r"2026\s*年\s*1\s*月")
    ok = bool(re.search(r"2026\s*年\s*1\s*月|2026[/\-]0?1|明年\s*1\s*月|January",
                        c, re.IGNORECASE)) and bool(
        re.search(r"WG\s*[2-5]|WG[2-5]|工作小組|1755|完成|target", c, re.IGNORECASE))
    scores["january_target"] = 1.0 if (fact and ok) else 0.0

    # 6) 十年過渡期：全面遷出本頻段
    fact = tx_has(r"十年", r"過渡")
    ok = bool(re.search(r"十年|10\s*年|10[\-\s]?year", c, re.IGNORECASE)) and bool(
        re.search(r"過渡|遷出|遷移|轉換|搬遷|relocat|transition", c, re.IGNORECASE))
    scores["ten_year_transition"] = 1.0 if (fact and ok) else 0.0

    # 7) ISART 研討會：7 月 25-26 日，於電信技術研究所（ITS）
    fact = tx_has(r"ISART")
    ok = bool(re.search(r"ISART", c, re.IGNORECASE)) and bool(
        re.search(r"7\s*月\s*25|25\s*(?:日|至|到|[\-~])\s*26|研討會|ITS|電信技術|頻譜共用|spectrum\s*sharing",
                  c, re.IGNORECASE))
    scores["isart_meeting"] = 1.0 if (fact and ok) else 0.0

    # 8) 依時間先後組織：年份大致遞增，或出現足夠多不同年份／日期錨點
    years = [int(m.group()) for m in re.finditer(r"20[12]\d", c)]
    if len(years) >= 3:
        ordered = sum(1 for i in range(len(years) - 1) if years[i] <= years[i + 1])
        ratio = ordered / (len(years) - 1)
        scores["chronological_order"] = 1.0 if ratio >= 0.6 else (0.5 if ratio >= 0.4 else 0.0)
    else:
        anchors = re.findall(
            r"(?:2023|2024|2025|2026|7\s*月\s*24|7\s*月\s*25|9\s*月|10\s*月\s*1|1\s*月|十年)", c)
        scores["chronological_order"] = (
            1.0 if len(set(anchors)) >= 4 else (0.5 if re.search(r"\d{4}", c) else 0.0))

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

### 評分項 1：時間軸項目完整度（權重 35%）
- 1.0：擷取所有主要時間軸項目——歷史參照（2023 六月備忘錄、2024 十月一日報告、
  2014 年 1710-1755 清整、5 GHz Wi-Fi 先例、180 億／9 億成本估算）、目前狀態項目，
  以及未來期限（2025 年 9 月、2026 年 1 月、下次會議、十年計畫）。至少 10 筆不同項目。
- 0.75：擷取多數項目，僅一兩項遺漏
- 0.5：記載主要期限，但缺少歷史脈絡或次要項目
- 0.25：僅擷取最明顯的期限
- 0.0：幾乎沒有或完全沒有時間軸項目
### 評分項 2：日期與時間範圍準確度（權重 25%）
- 1.0：所有日期、期間與相對時間範圍皆準確取自逐字稿，無捏造日期
  （2023/6、2024/10/1、2025/5/30、2025/7/24、2025/7/25-26、2025/9、2026/1、十年、5 年）
- 0.75：多數日期正確，僅一處小錯
- 0.5：部分日期正確，但有數處不準確
- 0.25：多處日期錯誤或捏造日期
- 0.0：日期大多不正確
### 評分項 3：脈絡與歸屬（權重 20%）
- 1.0：每筆項目都含是誰提到的（如史國良次長、聶國維副署長、林淑芬委員、沈柏睿委員）、
  所指事項，以及任何條件或相依關係，發言人歸屬正確
- 0.5：提供部分脈絡，但歸屬不一致
- 0.0：完全沒有提供脈絡
### 評分項 4：組織與可用性（權重 20%）
- 1.0：時間軸依時間先後（或依過去／現在／未來邏輯）清楚組織，易於瀏覽，
  格式清晰可區分日期與描述
- 0.5：有一些組織，但難以追隨時序
- 0.0：沒有有意義的組織
