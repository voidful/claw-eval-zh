---
id: task_csv_pension_liability
name: 縣市退休金負債分析（虛構彙整資料）
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_pension_liability
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T077tw_csv_pension_liability
workspace_files:
- source: tw/csvs/tw_pension.csv
  dest: tw_pension.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 縣市退休金負債分析（虛構彙整資料）

## Prompt

我的工作區裡有一個 CSV 檔 `tw_pension.csv`，內含一份依縣市與選區細分的退休金
年度給付彙整資料（虛構之公務退撫給付示意資料，金額單位為新臺幣 NT$）。欄位如下：

- `STATE_ABBREV_NAME` — 縣市代碼與名稱（縣市彙總列以 " Total" 結尾，
  例如 "TPE-臺北市 Total"）
- `DISTRICT` — 選區號碼、"At Large"、空白或年份
- `PAYEE_AMOUNT` — 給付給目前退休領取者的年度總金額（以 $ 與千分位逗號格式化）
- `PAYEE_COUNT` — 目前領取者人數
- `DEFERRED_COUNT` — 遞延（尚未開始請領）的未來領取者人數

以 " Total" 結尾的列為縣市級彙總。第一列是 Grand Total（全國總計）。

請分析退休金負債曝險（liability exposure），並把你的發現寫到
`pension_liability_report.md`。報告請以繁體中文撰寫，金額一律以新臺幣（NT$）表示，
並以 CSV 內的實際數值為準，不要捏造未出現在檔案中的數字。報告應包含：

- 每個縣市的**每位領取者平均給付**（PAYEE_AMOUNT ÷ PAYEE_COUNT）——依此指標將
  前 10 大縣市排名。
- 各縣市的**遞延總人數**——將遞延（未來）領取者最多的前 10 大縣市排名。
- **預估未來負債**：對每個縣市，以該縣市的每位領取者平均給付乘以其遞延人數，
  估算未來年度負債。依此預估負債將前 10 大縣市排名。
- **全國摘要**：目前年度給付總額、目前領取者總數、遞延領取者總數、整體每位
  領取者平均給付，以及若所有遞延領取者皆以目前平均水準請領時的總預估未來負債。
- 一段簡短的**分析**：說明哪些縣市代表最大的未來財務曝險，以及原因。

請注意：預估未來負債是一個估計值，它假設遞延領取者未來將以與目前領取者相同的
平均水準請領。好的回應應指出此假設及其限制。

## Expected Behavior

助手應該：

1. 解析 CSV，去除金額的 $ 格式與千分位逗號
2. 計算每個縣市的每位領取者平均給付（PAYEE_AMOUNT ÷ PAYEE_COUNT）
3. 依平均給付排名各縣市——金門縣（約 NT$7,946）、澎湖縣（約 NT$7,431）、
   連江縣（約 NT$7,008）居前
4. 依遞延人數排名各縣市——臺北市（53,519）、臺中市（44,440）、新北市（37,416）居前
5. 計算每個縣市的預估未來負債（平均給付 × 遞延人數）
6. 回報全國總計：給付總額約 NT$3.52 billion（$3,522,337,308）、545,862 名領取者、
   332,084 名遞延、整體平均約 NT$6,453
7. 計算總預估未來負債：約 NT$6,453 × 332,084 ≈ NT$2.14 billion（約 21.4 億）

以 tw_pension.csv 實際資料計，關鍵預期數值如下（金額單位新臺幣 NT$）：

- 整體平均給付：每位領取者約 NT$6,453
- 平均給付前段：金門縣（約 7,946）、澎湖縣（約 7,431）、連江縣（約 7,008）、
  臺中市（約 6,965）、新竹市（約 6,925）
- 遞延人數最多：臺北市（53,519）、臺中市（44,440）、新北市（37,416）、
  高雄市（35,951）、桃園市（34,733）
- 預估未來負債前段：臺北市（約 3.53 億）、臺中市（約 3.10 億）、高雄市（約 2.41 億）、
  新北市（約 2.31 億）、桃園市（約 2.29 億）
- 全國總預估未來負債：約 NT$2,142,871,023（約 NT$2.14 billion）

重點觀察：平均給付前段多為離島／偏鄉小縣（金門、澎湖、連江），但因領取與遞延
人數小，對總負債影響有限；真正的未來財務曝險集中在六都（臺北、臺中、高雄、新北、
桃園），因其遞延人數龐大且平均給付中等偏上，兩者相乘才推升預估未來負債。
好的報告會點出「平均給付排名前段的縣市」與「預估負債排名前段的縣市」並不相同。

## Grading Criteria

- [ ] 已建立報告檔案 `pension_liability_report.md`
- [ ] 已計算每位領取者平均給付並列出前段縣市
- [ ] 已指出平均給付最高為金門縣（約 NT$7,946）
- [ ] 已列出依遞延人數排名的前段縣市
- [ ] 已指出遞延人數最多為臺北市（53,519）
- [ ] 已逐縣市計算預估未來負債（平均給付 × 遞延人數）
- [ ] 全國摘要含給付總額、領取者總數、遞延總數與整體平均
- [ ] 已估算總預估未來負債（約 NT$2.14 billion）
- [ ] 已提供財務曝險分析，並區分平均給付前段與負債前段縣市之差異

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """縣市退休金負債分析 grader（台灣 CSV 版）。

    以工作區內的台灣 CSV（dest=tw_pension.csv）動態實算正解，再比對 agent
    產生的中文報告 pension_liability_report.md。僅用標準函式庫。
    報告為繁體中文，故比對中文縣市名與數值關鍵字。
    """
    from pathlib import Path
    import csv
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "avg_payout_ranking", "top_avg_county",
        "deferred_ranking", "top_deferred_county", "projected_liability",
        "national_summary", "total_projected", "exposure_analysis",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "pension_liability_report.md"
    if not report.exists():
        for alt in [
            "liability_report.md", "report.md", "pension_report.md",
            "pension_liability.md", "pension_liability_report.txt",
        ]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從台灣 CSV 動態實算正解（避免硬寫美國數值） ---
    def num(s):
        s = (s or "").strip().strip('"').replace("$", "").replace(",", "").strip()
        try:
            return float(s)
        except ValueError:
            return 0.0

    csv_path = workspace / "tw_pension.csv"
    if not csv_path.exists():
        for alt in ["pension.csv", "tw_pension_by_county.csv"]:
            if (workspace / alt).exists():
                csv_path = workspace / alt
                break

    counties = []
    grand = None
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = (row.get("STATE_ABBREV_NAME") or "").strip()
                amount = num(row.get("PAYEE_AMOUNT"))
                count = num(row.get("PAYEE_COUNT"))
                deferred = num(row.get("DEFERRED_COUNT"))
                if name == "Grand Total":
                    grand = {"amount": amount, "count": count, "deferred": deferred}
                    continue
                if name.endswith("Total"):
                    label = name[: -len("Total")].strip()
                    # 取中文縣市名（去掉 "TPE-" 之類前綴）
                    zh = label.split("-")[-1].strip() if "-" in label else label
                    avg = amount / count if count else 0.0
                    counties.append({
                        "label": label, "zh": zh, "amount": amount,
                        "count": count, "deferred": deferred,
                        "avg": avg, "projected": avg * deferred,
                    })

    def topn(key, n=10):
        return sorted(counties, key=lambda x: -x[key])[:n]

    top_avg = topn("avg")
    top_def = topn("deferred")
    top_proj = topn("projected")

    # 全國摘要（以縣市彙總列加總；若有 Grand Total 列則優先採用）
    tot_amount = sum(x["amount"] for x in counties)
    tot_count = sum(x["count"] for x in counties)
    tot_deferred = sum(x["deferred"] for x in counties)
    if grand:
        tot_amount = grand["amount"] or tot_amount
        tot_count = grand["count"] or tot_count
        tot_deferred = grand["deferred"] or tot_deferred
    overall_avg = tot_amount / tot_count if tot_count else 0.0
    total_projected = overall_avg * tot_deferred

    def zh_present(name):
        # 報告可能寫 "臺北市" 或 "台北市"；做臺/台等值處理
        variants = {name, name.replace("臺", "台"), name.replace("台", "臺")}
        return any(v and v in c for v in variants)

    scores = {"report_created": 1.0}

    # 平均給付排名：前 5 大平均給付縣市中至少命中 3 個，且有「平均」語境
    has_avg_ctx = bool(re.search(r"平均給付|每位領取者|平均.{0,4}給付|average|avg", c, re.I))
    avg_hits = sum(1 for x in top_avg[:5] if zh_present(x["zh"]))
    scores["avg_payout_ranking"] = (
        1.0 if (avg_hits >= 3 and has_avg_ctx)
        else (0.5 if avg_hits >= 2 else 0.0)
    )

    # 最高平均給付縣市（動態：實算 top1）須出現，且鄰近有「最高／第一／平均」語境或其數值
    if top_avg:
        t = top_avg[0]
        tname_variants = [t["zh"], t["zh"].replace("臺", "台"), t["zh"].replace("台", "臺")]
        tname_re = "(?:%s)" % "|".join(re.escape(v) for v in set(tname_variants) if v)
        avg_int = int(round(t["avg"]))
        # 數值容忍：四捨五入到整數附近（容許千分位逗號）
        avg_num_re = r"%s[,]?%s" % (str(avg_int // 1000), "%03d" % (avg_int % 1000))
        top_avg_ok = bool(
            re.search(tname_re + r".{0,40}(?:最高|第一|第 1|#1|top|平均給付|" + avg_num_re + r")",
                      c, re.I)
            or re.search(r"(?:最高|第一|#1|top).{0,40}(?:平均|給付).{0,20}" + tname_re, c, re.I)
            or re.search(tname_re + r".{0,40}" + avg_num_re, c)
        )
    else:
        top_avg_ok = False
    scores["top_avg_county"] = 1.0 if top_avg_ok else 0.0

    # 遞延人數排名：前 5 大遞延縣市中至少命中 3 個，且有「遞延」語境
    has_def_ctx = bool(re.search(r"遞延|deferred", c, re.I))
    def_hits = sum(1 for x in top_def[:5] if zh_present(x["zh"]))
    scores["deferred_ranking"] = (
        1.0 if (def_hits >= 3 and has_def_ctx)
        else (0.5 if def_hits >= 2 else 0.0)
    )

    # 遞延最多縣市（動態 top1）須出現，且鄰近有「最多／第一／遞延」語境或其數值
    if top_def:
        t = top_def[0]
        tname_variants = [t["zh"], t["zh"].replace("臺", "台"), t["zh"].replace("台", "臺")]
        tname_re = "(?:%s)" % "|".join(re.escape(v) for v in set(tname_variants) if v)
        dval = int(round(t["deferred"]))
        dnum_re = r"%s[,]?%s" % (str(dval // 1000), "%03d" % (dval % 1000))
        top_def_ok = bool(
            re.search(tname_re + r".{0,40}(?:最多|最高|第一|#1|top|" + dnum_re + r")",
                      c, re.I)
            or re.search(r"(?:最多|最高|第一|#1|top).{0,40}遞延.{0,20}" + tname_re, c, re.I)
            or re.search(tname_re + r".{0,40}" + dnum_re, c)
        )
    else:
        top_def_ok = False
    scores["top_deferred_county"] = 1.0 if top_def_ok else 0.0

    # 預估未來負債：須出現「預估／預測／未來」+「負債／曝險」語境，或乘法說明
    proj_ok = bool(
        re.search(r"(?:預估|預測|未來|推估).{0,12}(?:負債|曝險|成本|給付)", c)
        or re.search(r"(?:平均給付|平均).{0,12}(?:乘以|×|x|\*).{0,12}遞延", c, re.I)
        or re.search(r"遞延.{0,12}(?:乘以|×|x|\*).{0,12}(?:平均給付|平均)", c, re.I)
    )
    scores["projected_liability"] = 1.0 if proj_ok else 0.0

    # 全國摘要：在領取者總數、遞延總數、整體平均、給付總額中至少命中 3 項數值
    def has_int(value, slack_digits=True):
        v = int(round(value))
        hi = str(v // 1000)
        lo = "%03d" % (v % 1000)
        return bool(re.search(r"%s[,]?%s" % (hi, lo), c))

    nat_count = 0
    if has_int(tot_count):
        nat_count += 1
    if has_int(tot_deferred):
        nat_count += 1
    if has_int(overall_avg):
        nat_count += 1
    # 給付總額：以 billion 或前幾位數字命中
    amt_billions = tot_amount / 1e9
    if (re.search(r"3[.,]5\d*\s*billion", c, re.I)
            or re.search(r"35[\d,.]{0,3}\s*億", c)
            or has_int(tot_amount)):
        nat_count += 1
    scores["national_summary"] = (
        1.0 if nat_count >= 3 else (0.5 if nat_count >= 2 else 0.0)
    )

    # 總預估未來負債（動態，約 NT$2.14B）：命中 billion 表述、約 21.4 億、或整數金額
    tp_billions = total_projected / 1e9
    tp_int = int(round(total_projected))
    tp_ok = bool(
        re.search(r"2[.,]1\d*\s*billion", c, re.I)
        or re.search(r"21[.,]?\d?\s*億", c)
        or re.search(r"2[,]?1\d\d[,]?\d{3}[,]?\d{3}", c)
        or re.search(r"%s[,]?%s" % (str(tp_int // 1000000), "%06d" % (tp_int % 1000000)), c)
    )
    # 也接受報告寫整體平均(約6,453)乘遞延(332,084)約2.14B的口語近似
    if not tp_ok and re.search(r"(?:總|全國).{0,10}(?:預估|未來).{0,10}負債", c):
        if re.search(r"2[.,]1", c) or re.search(r"21[.,]?\d?\s*億", c):
            tp_ok = True
    scores["total_projected"] = 1.0 if tp_ok else 0.0

    # 財務曝險分析：須有「曝險／風險／負債／財務」其一，且有實質分析語境
    ana = 0
    if re.search(r"曝險|風險|負債|財務|obligation|exposure|risk", c, re.I):
        ana += 1
    if re.search(r"(?:龐大|顯著|可觀|集中|最大).{0,12}(?:遞延|未來|負債|曝險)", c):
        ana += 1
    if re.search(r"六都|人口|公務|人力|離島|平均給付.{0,20}(?:不同|差異|並不相同)", c):
        ana += 1
    scores["exposure_analysis"] = (
        1.0 if ana >= 2 else (0.5 if ana >= 1 else 0.0)
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

### 評分項 1：計算正確性（權重 35%）

- 1.0：所有計算正確——每位領取者平均給付、遞延人數、預估未來負債與全國總計皆符合
  以 tw_pension.csv 實算之預期值（整體平均約 NT$6,453、總給付約 NT$3.52B、
  領取者 545,862、遞延 332,084、總預估負債約 NT$2.14B）。正確去除 $ 與逗號格式。
- 0.75：多數計算正確，僅有小幅四捨五入或一處計算錯誤。
- 0.5：核心方法正確，但有多項數值錯誤，或預估負債方法有瑕疵。
- 0.25：重大計算錯誤或對資料理解有誤（如誤用 Grand Total 列重複計入）。
- 0.0：未能完成計算，或結果完全錯誤（如沿用美國原版數值）。

### 評分項 2：多維度分析（權重 30%）

- 1.0：三種排名維度皆具備（每位領取者平均給付、遞延人數、預估未來負債），且彼此
  區分清楚。展現出「高負債來自高平均給付『且』高遞延人數的組合」之理解。
- 0.75：三種維度皆具備，但其中一項不完整，或未探討維度之間的交互作用。
- 0.5：只分析三者中的兩種，或有排名但無說明。
- 0.25：只分析一種維度。
- 0.0：沒有多維度分析。

### 評分項 3：財務洞見（權重 20%）

- 1.0：對退休金負債集中的成因提供有意義的洞見——人口與公務人力規模、六都集中、
  離島小縣平均給付雖高但總量小。明確指出「依平均給付排名前段的縣市（離島小縣）」
  與「依預估負債排名前段的縣市（六都）」並不相同。
- 0.75：對模式有良好觀察，並有一些脈絡推理。
- 0.5：基本觀察，缺乏更深入的財務推理。
- 0.25：除列數字外洞見極少。
- 0.0：沒有分析或洞見。

### 評分項 4：報告品質（權重 15%）

- 1.0：報告結構良好，每項排名各有清楚分區，使用表格或清單，全國摘要顯著呈現，
  流程合理，繁體中文通順，金額以新臺幣（NT$）標示。
- 0.75：結構良好，僅有小問題。
- 0.5：有內容但組織不佳。
- 0.25：雜亂或區段不完整。
- 0.0：沒有報告或空白檔案。
