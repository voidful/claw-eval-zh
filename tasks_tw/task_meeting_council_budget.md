---
id: task_meeting_council_budget
name: 南港市議會逐字稿 — 擷取預算討論
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_budget
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T111tw_meeting_council_budget
workspace_files:
- source: tw/meetings/tw_council_meeting.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 南港市議會逐字稿 — 擷取預算討論

## Prompt

工作區裡有一份 2026 年 4 月 2 日舉行的「南港市議會 第 12 屆第 3 次定期會」會議逐字稿，
存放在 transcript.md（虛構的台灣地方議會，人名、機關、金額皆為杜撰）。

請以台灣地方議會與財政的語境閱讀逐字稿，產生一份 budget_report.md，擷取所有與**預算、
經費、費率**相關的討論。每一項請包含：

- 項目名稱（例如：自來水及污水容量費、中崙倉庫園區、南港大道行政園區增建等）
- 相關**金額**（一律以新臺幣 NT$ 計，逐字稿怎麼寫就照實引用，例如 NT$1,020、
  9,400 萬元、30 億元）
- 背景脈絡（為什麼要花這筆錢、要做什麼）
- 議會行動（例如：完成一讀、納入追加預算、尚未編列、待研議等）
- 關切或爭議事項（若逐字稿有提到）

最後請附上一個**財務彙總（財務摘要）**段落，把本日重大財務案的金額整理在一起。

請全程使用繁體中文，金額沿用逐字稿中的新臺幣數字，不要自行換算成美元或其他幣別。

## Expected Behavior

助手應讀取 transcript.md，並產生 budget_report.md，至少涵蓋以下（皆為虛構）重大財務項目：

- **自來水及污水容量費（容量接管費）**：未來 20 年總計需投入約新臺幣 30 億元
  （NT$3,000,000,000）資本改善，其中已爭取中央補助約 1 億 7,000 萬元（NT$170,000,000）。
  目前每戶自來水 NT$1,020、污水 NT$1,237；提案調整為自來水 NT$1,530、污水 NT$1,847。
  調整後預估每年可增加約 NT$1,500 萬至 2,000 萬元之額外收入。第二十三案已完成一讀。
- **中崙倉庫園區 第四期**：總開發經費約新臺幣 9,400 萬元（NT$94,000,000），
  其中民間開發商（鼎峰都更開發）投入約 NT$300 萬元先期建設，預計 2028 年 9 月完工。
- **南港大道行政園區增建**：總經費新臺幣 3,420 萬元（NT$34,200,000）；第一期已支用約
  NT$700 萬元（NT$7,000,000，已支出），第二期尚需 NT$2,720 萬元（NT$27,200,000）。
- **第 24 號消防分隊**：保證最高價（GMP）將於 5 月 15 日提報核定，預計 2027 年 9 月完工。
- **天然氣管線損鄰和解金**：新臺幣 65 萬元（NT$650,000），已納入追加預算。
- **義塚紀念館（市民請求）**：市民任薇等人請求編列 NT$8,000 萬元（NT$80,000,000）設置義塚
  紀念館暨族譜中心，本案尚未編列，將提交研議。
- **老舊管線汰換方案**：擬採每戶每月加收 NT$8 元自來水管線費加 NT$8 元污水管線費
  （合計每月 NT$16 元）方式分攤。

並在最後附上清楚的財務彙總（財務摘要），整理上述金額。

## Grading Criteria

- [ ] 已建立報告檔案 budget_report.md
- [ ] 已辨識容量費目前與提議金額（NT$1,020／NT$1,237 與 NT$1,530／NT$1,847）
- [ ] 已提及 30 億元（NT$3,000,000,000）資本投資
- [ ] 已記下每年增加約 NT$1,500 萬至 2,000 萬元收入
- [ ] 已辨識中崙倉庫園區 9,400 萬元（NT$94,000,000）
- [ ] 已辨識南港大道行政園區增建 3,420 萬元（NT$34,200,000）
- [ ] 已記下第一期已支出 NT$700 萬元（NT$7,000,000）
- [ ] 已提及天然氣和解金 NT$65 萬元（NT$650,000）
- [ ] 已掌握義塚紀念館請求 NT$8,000 萬元（NT$80,000,000）
- [ ] 已包含財務彙總（財務摘要）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """南港市議會預算報告 grader。

    應有事實「從 transcript.md（佈署的台灣逐字稿）動態推導」，再比對 agent 產生
    的中文報告 budget_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    keys = [
        "report_created", "capacity_fee_amounts", "three_billion",
        "annual_revenue_increase", "zhonglun_yard_94m", "annex_34m",
        "phase1_7m", "gas_settlement_650k", "yizhong_8m", "financial_summary",
    ]
    workspace = Path(workspace_path)

    # --- 找報告檔 ---
    report_path = workspace / "budget_report.md"
    if not report_path.exists():
        for alt in ["budget.md", "financial_report.md", "finances.md",
                    "預算報告.md", "財務報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    # --- 讀逐字稿，動態推導應有金額 ---
    tpath = workspace / "transcript.md"
    tx = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def digits(s):
        """只保留數字，方便比對 1,020 / 1020 / NT$1,020 等寫法。"""
        return re.sub(r"\D", "", s)

    # 從逐字稿抓出關鍵金額（抓不到時退回已知預設值，避免逐字稿格式變動就壞掉）
    def find_amount(pattern, default):
        m = re.search(pattern, tx)
        return digits(m.group(1)) if m else default

    water_now = find_amount(r"自來水\s*\*{0,2}NT\$?([\d,]+)", "1020")    # 1020
    sewer_now = find_amount(r"污水\s*\*{0,2}NT\$?([\d,]+)", "1237")      # 1237
    water_new = find_amount(r"調整為\s*自來水\s*\*{0,2}NT\$?([\d,]+)", "1530")  # 1530
    sewer_new = "1847"  # 提議之污水費率（逐字稿第二筆污水數字）
    three_b = find_amount(r"NT\$?([\d,]+)，3 billion", "3000000000")    # 30 億
    zhonglun = find_amount(r"中崙倉庫園區.{0,40}?NT\$?([\d,]+)，94 million", "94000000")
    annex = find_amount(r"行政園區增建案.{0,20}?NT\$?([\d,]+)，34", "34200000")
    phase1 = find_amount(r"第一期已支用約\s*\*{0,2}NT\$?([\d,]+)", "7000000")
    gas = find_amount(r"和解金\s*新臺幣[^（]*（NT\$?([\d,]+)", "650000")  # 650000
    yizhong = find_amount(r"請求編列\s*\*{0,2}NT\$?([\d,]+)\s*萬", "8000")   # 8000(萬)

    # --- 讀報告並去除空白，便於數字比對 ---
    raw = report_path.read_text(encoding="utf-8", errors="ignore")
    c = raw  # 原文（保留漢字）
    nospace = re.sub(r"[\s,]", "", raw)  # 去空白與千分位逗號

    def has_num(*nums):
        return all(n and n in nospace for n in nums)

    scores = {"report_created": 1.0}

    # 容量費：現行(自來水/污水) 與 提議(自來水/污水) 至少各出現一組
    now_ok = has_num(water_now) and has_num(sewer_now)
    new_ok = has_num(water_new) and has_num(sewer_new)
    scores["capacity_fee_amounts"] = 1.0 if (now_ok and new_ok) else 0.0

    # 30 億資本投資：接受「30億」「3,000,000,000」「3 billion」等寫法
    scores["three_billion"] = 1.0 if (
        re.search(r"30\s*億", c) or has_num(three_b) or re.search(r"3\s*billion", c.lower())
    ) else 0.0

    # 每年增加約 1,500 萬至 2,000 萬元收入
    rev_amt = (re.search(r"1[,，]?500\s*萬", c) or re.search(r"1500萬", nospace)
               or "15000000" in nospace)
    rev_ctx = re.search(r"(收入|增加|每年|額外|挹注)", c)
    scores["annual_revenue_increase"] = 1.0 if (rev_amt and rev_ctx) else 0.0

    # 中崙倉庫園區 9,400 萬元（NT$94,000,000）
    zhonglun_amt = (re.search(r"9[,，]?400\s*萬", c) or has_num(zhonglun)
                or re.search(r"94\s*million", c.lower()))
    zhonglun_ctx = re.search(r"中崙倉庫", c)
    scores["zhonglun_yard_94m"] = 1.0 if (zhonglun_amt and zhonglun_ctx) else 0.0

    # 行政園區增建 3,420 萬元（NT$34,200,000）
    annex_amt = (re.search(r"3[,，]?420\s*萬", c) or has_num(annex)
                 or re.search(r"34\.?2?\s*million", c.lower()))
    annex_ctx = re.search(r"(行政園區增建|南港大道.{0,6}增建)", c)
    scores["annex_34m"] = 1.0 if (annex_amt and annex_ctx) else 0.0

    # 第一期已支出 NT$700 萬元（NT$7,000,000）
    phase_amt = (re.search(r"700\s*萬", c) or has_num(phase1)
                 or re.search(r"7\s*million", c.lower()))
    phase_ctx = re.search(r"(第一期|已支用|已支出|Phase\s*1)", c)
    scores["phase1_7m"] = 1.0 if (phase_amt and phase_ctx) else 0.0

    # 天然氣和解金 NT$65 萬元（NT$650,000）
    gas_amt = (re.search(r"65\s*萬", c) or has_num(gas)
               or re.search(r"650[,.]?000", c))
    gas_ctx = re.search(r"(和解金|天然氣|管線損鄰)", c)
    scores["gas_settlement_650k"] = 1.0 if (gas_amt and gas_ctx) else 0.0

    # 義塚紀念館請求 NT$8,000 萬元（NT$80,000,000）；yizhong 為逐字稿推導之「萬元」數字
    # （例 "8000"）；接受 8,000 萬 / 80,000,000 / 8 million 等寫法
    yizhong_amount = ((yizhong + "萬") in nospace or (yizhong + "0000") in nospace
                   or "80000000" in nospace or re.search(r"8\s*million", c.lower()))
    yizhong_ctx = re.search(r"(義塚|紀念館)", c)
    scores["yizhong_8m"] = 1.0 if (yizhong_amount and yizhong_ctx) else 0.0

    # 財務彙總（財務摘要）
    scores["financial_summary"] = 1.0 if re.search(
        r"(財務|預算)\s*(彙總|摘要|概要|總覽|總結)|財務概要", c
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

### 評分項 1：財務資料擷取（權重 40%）
- 1.0：所有主要新臺幣金額皆正確擷取（容量費現/提議費率、30 億資本支出、每年增收、
  中崙倉庫 9,400 萬、行政園區增建 3,420 萬與分期、和解金 65 萬、義塚紀念館 8,000 萬等）。
- 0.5：擷取多數但有部分缺漏或金額錯置。
- 0.0：金額大量缺漏或錯誤。
### 評分項 2：背景脈絡（權重 25%）
- 1.0：每一項目皆有清楚的背景脈絡與議會行動（一讀／追加預算／尚未編列等）。
- 0.5：部分項目有脈絡。
- 0.0：僅列金額，幾乎沒有脈絡。
### 評分項 3：周延度（權重 20%）
- 1.0：涵蓋逐字稿第五節所有財務段落（容量費、中崙倉庫、行政園區增建、消防分隊、
  和解金、義塚紀念館、管線月費）。
- 0.5：僅涵蓋主要幾項。
- 0.0：明顯不完整。
### 評分項 4：財務彙總（權重 15%）
- 1.0：結尾有清楚的財務彙總（財務摘要），整理本日重大金額。
- 0.5：有彙總但不完整。
- 0.0：沒有彙總。
