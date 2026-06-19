---
id: task_csv_pension_ranking
name: 台灣各縣市公教退休給付排名
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_pension_ranking
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T076tw_csv_pension_ranking
workspace_files:
- source: tw/csvs/tw_pension.csv
  dest: tw_pension.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台灣各縣市公教退休給付排名

## Prompt

我的工作區裡有一個 CSV 檔 `tw_pension.csv`，內含按**縣市**與**選區**細分的台灣
公教人員退休給付資料（資料為虛構，幣別為新臺幣 NT$，年度為 2024）。欄位如下：

- `STATE_ABBREV_NAME` — 縣市簡碼與名稱（縣市總計列以 " Total" 結尾，例如
  「TXG-臺中市 Total」；選區明細列則為「TXG-臺中市」）
- `DISTRICT` — 選區號碼、機關單位名稱，或年份（Grand Total 列填「2024」）
- `PAYEE_AMOUNT` — 發放給退休人員的給付總金額（以 $ 與逗號格式化，單位新臺幣 NT$）
- `PAYEE_COUNT` — 目前領取者人數（以逗號格式化）
- `DEFERRED_COUNT` — 遞延（未來）領取者人數（以逗號格式化）

以 " Total" 結尾的列為**縣市級彙總**。第一列資料是跨所有縣市的 Grand Total。

請分析這份資料，並把你的發現寫到 `pension_ranking_report.md`。報告請全程使用繁體中文，
金額一律以新臺幣（NT$）表示，並以 CSV 內實際數值為準，不要捏造未出現在檔案中的數字。
你的報告應包含：

- 依**給付總金額**由大到小排名的**前 10 大縣市**，附上金額與領取人數
- 依給付總金額排名的**後 5 名縣市／機關**（排除金額為 $0 的項目）
- 依**目前領取者人數**排名的**前 10 大縣市**
- 跨所有縣市的**總計（Grand Total）**：總金額、總領取人數、總遞延人數
- 一段簡短的**分析**：說明哪些縣市／區域在退休給付上占主導，以及可能的原因
  （例如人口規模、都會區公教人力集中、退休人口分布等）。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔，處理以美元符號格式化的金額（去除 `$` 與逗號）
2. 篩選縣市級 " Total" 列，取出金額、領取人數與遞延人數
3. 依給付總金額排序各縣市，產生前 10 名排名
4. 找出金額非零的後 5 名縣市／機關
5. 依領取人數排序，做出領取人數排名
6. 取出 Grand Total 列
7. 撰寫一份結構清晰、含分析的繁體中文 markdown 報告，金額以新臺幣（NT$）呈現

預期關鍵數值（以 `tw_pension.csv` 實際資料計，共 23 個縣市／機關級總計）：

- Grand Total：NT$3,522,337,308，跨 545,862 名領取者，遞延 332,084 人
- 金額前 5 名：臺中市（NT$561,035,674）、新北市（NT$439,602,278）、
  高雄市（NT$431,848,625）、臺北市（NT$401,246,363）、桃園市（NT$337,184,282）
- 金額第 6-10 名：臺南市（NT$295,926,927）、彰化縣（NT$205,084,463）、
  屏東縣（NT$116,683,567）、新竹縣（NT$97,840,516）、雲林縣（NT$92,316,812）
- 領取人數前 3 名：臺中市（80,552）、新北市（71,200）、高雄市（64,300）
- 領取人數第 9-10 名與金額排名互換：雲林縣（16,100）排第 9、新竹縣（14,800）排第 10
- 後 5 名（金額非零，由小到大）：連江縣（NT$2,943,163）、中央直轄機關（NT$3,426,734）、
  金門縣（NT$11,522,012）、澎湖縣（NT$17,091,271）、臺東縣（NT$30,119,630）

## Grading Criteria

- [ ] 已建立報告檔案 pension_ranking_report.md
- [ ] 正確列出依給付總金額排名的前 10 大縣市
- [ ] 已指出臺中市為金額第 1 名（NT$561,035,674）
- [ ] 已指出新北市為金額第 2 名（NT$439,602,278）
- [ ] 已指出高雄市為金額第 3 名（NT$431,848,625）
- [ ] 已指出後 5 名縣市／機關（連江縣、中央直轄機關、金門縣、澎湖縣、臺東縣）
- [ ] 已回報總計數字（NT$3,522,337,308、545,862 領取者、332,084 遞延）
- [ ] 已包含依領取人數排名的前段縣市（臺中市 80,552、新北市 71,200）
- [ ] 已提供地理／人口模式分析，金額以新臺幣（NT$）表示

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """台灣各縣市公教退休給付排名 grader。

    應有事實「從 tw_pension.csv（佈署的台灣 CSV）動態實算」——聚合縣市總計、
    依金額與人數排序、篩選後段，再比對 agent 產生的中文報告
    pension_ranking_report.md。僅用標準函式庫，不沿用任何美國數值。
    """
    from pathlib import Path
    import csv
    import re

    keys = [
        "report_created", "top_10_listed", "rank1_taichung",
        "rank2_newtaipei", "rank3_kaohsiung", "bottom_states",
        "grand_total", "payee_count_ranking", "geographic_analysis",
    ]
    workspace = Path(workspace_path)

    # --- 找報告檔 ---
    report_path = workspace / "pension_ranking_report.md"
    if not report_path.exists():
        for alt in ["ranking_report.md", "report.md", "pension_report.md",
                    "pension_ranking.md", "退休給付報告.md", "排名報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    # --- 從 CSV 動態實算正解 ---
    csv_path = workspace / "tw_pension.csv"

    def to_int(s):
        d = re.sub(r"[^\d]", "", s or "")
        return int(d) if d else 0

    grand = None
    totals = []  # [(縣市名, 金額, 領取人數, 遞延人數)]
    if csv_path.exists():
        with csv_path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                name = (row.get("STATE_ABBREV_NAME") or "").strip()
                amt = to_int(row.get("PAYEE_AMOUNT"))
                pc = to_int(row.get("PAYEE_COUNT"))
                dc = to_int(row.get("DEFERRED_COUNT"))
                if name == "Grand Total":
                    grand = (amt, pc, dc)
                elif name.endswith("Total"):
                    # 去掉「簡碼-縣市名」中的簡碼與末尾 Total，只留中文縣市/機關名
                    label = name[: -len("Total")].strip()
                    if "-" in label:
                        label = label.split("-", 1)[1].strip()
                    totals.append((label, amt, pc, dc))

    by_amt = sorted(totals, key=lambda t: t[1], reverse=True)
    by_amt_asc = sorted([t for t in totals if t[1] > 0], key=lambda t: t[1])
    by_pc = sorted(totals, key=lambda t: t[2], reverse=True)

    # --- 讀報告，準備數字比對（去千分位逗號與空白）---
    c = report_path.read_text(encoding="utf-8", errors="ignore")
    nospace = re.sub(r"[\s,]", "", c)

    def has_name(name):
        return bool(name) and name in c

    def has_amount(amt):
        # 接受 561,035,674 / 561035674 / 5.61 億 等寫法皆視為命中（以無逗號全額為準）
        return amt > 0 and str(amt) in nospace

    scores = {"report_created": 1.0}

    # 前 10 大（金額）：實算前 10 名縣市名至少出現 8 個
    top10_names = [t[0] for t in by_amt[:10]]
    mentioned = sum(1 for n in top10_names if has_name(n))
    scores["top_10_listed"] = (
        1.0 if mentioned >= 8 else (0.5 if mentioned >= 5 else 0.0)
    )

    # 第 1 名（金額）：名稱 + 金額皆需命中
    if by_amt:
        n1, a1 = by_amt[0][0], by_amt[0][1]
        scores["rank1_taichung"] = (
            1.0 if (has_name(n1) and has_amount(a1)) else 0.0
        )
    else:
        scores["rank1_taichung"] = 0.0

    # 第 2 名（金額）
    if len(by_amt) >= 2:
        n2, a2 = by_amt[1][0], by_amt[1][1]
        scores["rank2_newtaipei"] = (
            1.0 if (has_name(n2) and has_amount(a2)) else 0.0
        )
    else:
        scores["rank2_newtaipei"] = 0.0

    # 第 3 名（金額）
    if len(by_amt) >= 3:
        n3, a3 = by_amt[2][0], by_amt[2][1]
        scores["rank3_kaohsiung"] = (
            1.0 if (has_name(n3) and has_amount(a3)) else 0.0
        )
    else:
        scores["rank3_kaohsiung"] = 0.0

    # 後 5 名（金額非零，由小到大）：實算後 5 名至少提及 3 個
    bottom5 = [t[0] for t in by_amt_asc[:5]]
    bottom_hit = sum(1 for n in bottom5 if has_name(n))
    scores["bottom_states"] = (
        1.0 if bottom_hit >= 3 else (0.5 if bottom_hit >= 2 else 0.0)
    )

    # Grand Total：總金額／總領取人數／總遞延人數三項命中其二即滿分
    if grand:
        g_amt, g_pc, g_dc = grand
        g_hits = sum(
            1 for v in (g_amt, g_pc, g_dc) if v > 0 and str(v) in nospace
        )
        scores["grand_total"] = (
            1.0 if g_hits >= 2 else (0.5 if g_hits >= 1 else 0.0)
        )
    else:
        scores["grand_total"] = 0.0

    # 領取人數排名：前 2 名（依人數）之名稱 + 人數命中其一即可，另接受出現「領取人數」段落
    pc_hit = False
    for nm, _amt, pc, _dc in by_pc[:2]:
        if has_name(nm) and pc > 0 and str(pc) in nospace:
            pc_hit = True
            break
    if pc_hit:
        scores["payee_count_ranking"] = 1.0
    elif re.search(r"(領取(者)?人數|領取人口|現職領取)", c):
        scores["payee_count_ranking"] = 0.5
    else:
        scores["payee_count_ranking"] = 0.0

    # 地理／人口分析：命中關鍵分析詞彙的數量
    geo_patterns = [
        r"(六都|都會區|直轄市|人口規模|人口數)",
        r"(地理|區域|分布|集中|模式|趨勢)",
        r"(公教|退休人口|軍公教|公務人力)",
        r"(離島|偏鄉|北部|中部|南部|東部)",
    ]
    geo_count = sum(1 for p in geo_patterns if re.search(p, c))
    scores["geographic_analysis"] = (
        1.0 if geo_count >= 2 else (0.5 if geo_count >= 1 else 0.0)
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

### 評分項 1：資料解析與正確性（權重 35%）
- 1.0：所有金額、領取人數與排名皆正確解析並回報；縣市總計精確符合 CSV 實際值
  （臺中市約 5.61 億、新北市約 4.40 億、高雄市約 4.32 億；Grand Total 約 35.2 億／
  545,862 人／332,084 遞延）。金額以新臺幣（NT$）呈現。
- 0.75：多數數值正確，僅有小幅四捨五入差異，或排名中有一個縣市位置擺錯。
- 0.5：排名大致正確，但有多項數值解析錯誤，或將選區明細列與縣市總計混淆。
- 0.25：重大解析錯誤——金額錯誤、列類型混淆，或排名明顯不正確。
- 0.0：未能解析 CSV，或產出完全錯誤的結果。

### 評分項 2：排名完整性（權重 30%）
- 1.0：所有要求的排名皆具備——依金額的前 10、後 5、依領取人數的前 10、Grand Total，
  每項都有佐證數字。
- 0.75：多數排名具備，僅有小幅缺漏（例如缺一種排名類型或缺佐證數字）。
- 0.5：只提供依金額的前 10，其他排名缺漏或不完整。
- 0.25：只有部分排名且資料缺漏。
- 0.0：沒有提供排名。

### 評分項 3：分析品質（權重 20%）
- 1.0：分析有洞見，將退休給付集中連結到人口規模、六都／都會區公教人力集中、
  退休人口分布等因素，並指出有趣模式（如六都包辦前段、離島縣市墊底）。
- 0.75：分析合理，有一些地理／人口觀察。
- 0.5：表面觀察，缺乏更深入分析。
- 0.25：分析極少或模糊。
- 0.0：沒有提供分析。

### 評分項 4：報告結構（權重 15%）
- 1.0：markdown 組織良好，分區清楚，排名以表格或清單呈現，可讀性佳，金額皆以
  新臺幣（NT$）標示。
- 0.75：結構良好，僅有小幅排版問題。
- 0.5：有內容但組織不佳。
- 0.25：雜亂或不易閱讀。
- 0.0：沒有報告或空白檔案。
