---
id: task_review_sentiment_product_insights
name: 商品評論情感分析與商品洞察報告
category: json_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/json/product_reviews_2024.json
    dest: product_reviews_2024.json
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v2
---
## Prompt

你是一位電商商品洞察分析師。請讀取 `product_reviews_2024.json`（1,200 筆商品評論），對評論進行情感分析與商品洞察，輸出 `sentiment_product_report.md`。

### 分析項目一：評論情感分類

對每條評論進行簡易情感分類（**正面 / 負面 / 中性**），判定規則如下：

**正面關鍵詞**（出現任一即為正面）：
`好用`、`推薦`、`滿意`、`優秀`、`喜歡`、`超讚`、`值得`、`棒`、`完美`、`超棒`、`物超所值`、`高品質`、`回購`

**負面關鍵詞**（出現任一即為負面）：
`失望`、`退貨`、`差`、`不推薦`、`後悔`、`浪費`、`損壞`、`問題`、`不符`、`粗糙`、`故障`、`踩雷`、`假貨`

**優先規則**：若同時出現正面和負面關鍵詞，以負面為優先；若都沒有，歸為中性。

統計全體 1,200 筆評論的情感分布（正面/負面/中性數量與比例）。

### 分析項目二：商品情感淨值（NPS）計算

對每個商品計算：

```
NPS = (正面評論數 / 該商品總評論數 × 100) - (負面評論數 / 該商品總評論數 × 100)
```

以表格呈現所有 20 個商品的 NPS 值，從高到低排序。
識別：NPS 最高的商品（最佳口碑）和 NPS 最低的商品（最差口碑）。

### 分析項目三：各商品主要抱怨關鍵詞

從每個商品的**負面評論**（情感分類為負面的）中：
1. 統計所有負面關鍵詞的出現頻率
2. 列出每個商品被抱怨最多的前 3 個問題關鍵詞（以頻率排序）
3. 若某商品沒有負面評論，標記「暫無負面評論」

以表格或列表呈現結果（每個商品一行，列出前3個抱怨詞）。

### 分析項目四：「有用評論」情感傾向分析

分析 `helpful_votes` 高的評論是否傾向負面：

1. 將評論依 `helpful_votes` 由高到低排序，取前 20%（約 240 筆）為「高用處評論組」
2. 計算高用處組的情感分布（正面/負面/中性比例）
3. 與全體比較，分析差異（例：高用處評論中負面比例是否高於平均）
4. 計算「負面偏向指數」= 高用處組負面比例 / 全體負面比例（> 1 表示有負面偏向）
5. 給出結論：有用評論是否具有明顯的負面偏向？

### 分析項目五：跨平台評分差異分析

對每個有足夠評論數的商品（在多個平台各有至少 2 筆評論），計算：

1. 各平台的平均評分
2. 同一商品在不同平台間的評分差異（最大值 - 最小值）
3. 找出跨平台評分差異最大的前 5 個商品
4. 判斷哪個平台的整體平均評分最高（可能是刷評較多或消費者行為差異）

以表格呈現商品 × 平台的評分矩陣（部分為 N/A 可接受）。

### 輸出格式

輸出檔案：`sentiment_product_report.md`

```markdown
# 情感分析與商品洞察報告
**資料集**：product_reviews_2024.json（1,200 筆）
**分析日期**：YYYY-MM-DD

### 一、情感分類統計（全體）
### 二、商品情感淨值（NPS）排行
### 三、各商品主要抱怨關鍵詞
### 四、有用評論情感傾向分析
### 五、跨平台評分差異分析
### 六、洞察摘要與商品優化建議
```

---

## Expected Behavior

代理人應執行以下步驟：

1. 讀取並解析 `product_reviews_2024.json`，取得 1,200 筆評論的 `review_body`、商品名稱、`helpful_votes`、平台與評分等欄位
2. 依詞典規則（負面優先）對每筆評論做情感分類，統計全體正面/負面/中性的數量與比例
3. 依商品分組計算 NPS（正面比例 − 負面比例），對 20 個商品由高到低排序，並標出最高/最低口碑商品
4. 從各商品的負面評論中統計負面關鍵詞頻率，列出每個商品前 3 名抱怨詞（無負面評論者標記「暫無負面評論」）
5. 依 `helpful_votes` 取前 20%（約 240 筆）為高用處組，計算其情感分布並與全體比較，求出負面偏向指數並下結論
6. 建立商品 × 平台評分矩陣，計算各商品跨平台評分差異，找出差異最大的前 5 個商品並判斷平均評分最高的平台
7. 輸出格式完整、章節齊全的 `sentiment_product_report.md`，並附上洞察摘要與商品優化建議

關鍵參考值（近似）：
- 全體評論 1,200 筆，商品 20 個，平台為 shopee / momo / pchome
- 高用處組約 240 筆（前 20%）
- 負面偏向指數 > 1 通常表示有用評論偏向負面

---

## Grading Criteria

- [ ] 輸出檔案 `sentiment_product_report.md` 存在
- [ ] 正面與負面情感比例接近參考值，且三類情感（正面/負面/中性）均呈現
- [ ] 計算 NPS（情感淨值）指標並覆蓋 20 個商品中的大多數
- [ ] 識別 NPS 最高（最佳口碑）與最低（最差口碑）的商品
- [ ] 識別多個負面關鍵詞並列出各商品前 3 名抱怨詞
- [ ] 分析 `helpful_votes` 高用處評論組，定義前 20% 並討論負面偏向現象
- [ ] 跨平台分析涵蓋 shopee / momo / pchome 三個平台並呈現評分差異結論
- [ ] 報告章節齊全，含洞察摘要與商品優化建議

---

## Automated Checks

```python
import re, json
from pathlib import Path

def grade(transcript: list, submission_dir: str) -> dict:
    """
    評分標準（100分）：
    - 項目一情感分類統計（20分）
    - 項目二NPS計算（25分）
    - 項目三抱怨關鍵詞（20分）
    - 項目四有用評論分析（20分）
    - 項目五跨平台分析（15分）
    """
    report_path = Path(submission_dir) / "sentiment_product_report.md"
    if not report_path.exists():
        return {"score": 0, "max_score": 100, "details": "未找到 sentiment_product_report.md"}

    text = report_path.read_text(encoding="utf-8")
    score = 0
    details = []

    # ── 載入資料計算參考答案 ──────────────────────────────────────────────────
    data_candidates = [
        Path(submission_dir) / "product_reviews_2024.json",
        Path(submission_dir).parent / "assets" / "json" / "product_reviews_2024.json",
    ]
    reviews = None
    for p in data_candidates:
        if p.exists():
            with open(p, encoding="utf-8") as f:
                reviews = json.load(f)
            break

    if reviews is None:
        return {"score": 0, "max_score": 100, "details": "無法載入評論資料集進行驗算"}

    POSITIVE_KW = ["好用","推薦","滿意","優秀","喜歡","超讚","值得","棒","完美","超棒","物超所值","高品質","回購"]
    NEGATIVE_KW = ["失望","退貨","差","不推薦","後悔","浪費","損壞","問題","不符","粗糙","故障","踩雷","假貨"]

    def classify(body):
        has_neg = any(k in body for k in NEGATIVE_KW)
        has_pos = any(k in body for k in POSITIVE_KW)
        if has_neg: return "負面"
        if has_pos: return "正面"
        return "中性"

    sentiments = [classify(r["review_body"]) for r in reviews]
    pos_count = sentiments.count("正面")
    neg_count = sentiments.count("負面")
    neu_count = sentiments.count("中性")
    pos_pct = pos_count / len(reviews) * 100
    neg_pct = neg_count / len(reviews) * 100

    # ── 項目一：情感分類統計 (20分) ──────────────────────────────────────────
    found_numbers = [float(x) for x in re.findall(r"(\d+\.?\d*)\s*%", text)]
    ref_pos = round(pos_pct, 1)
    ref_neg = round(neg_pct, 1)

    close_pos = any(abs(n - ref_pos) <= 5 for n in found_numbers)
    close_neg = any(abs(n - ref_neg) <= 5 for n in found_numbers)

    if close_pos:
        score += 8
        details.append(f"✅ [情感] 正面比例接近參考值 ~{ref_pos}% (+8)")
    else:
        details.append(f"❌ [情感] 正面比例偏差（參考值 ~{ref_pos}%）")

    if close_neg:
        score += 7
        details.append(f"✅ [情感] 負面比例接近參考值 ~{ref_neg}% (+7)")
    else:
        details.append(f"❌ [情感] 負面比例偏差（參考值 ~{ref_neg}%）")

    if re.search(r"(正面|負面|中性).{0,30}(正面|負面|中性)", text):
        score += 5
        details.append("✅ [情感] 三類情感均呈現 (+5)")
    else:
        details.append("❌ [情感] 未同時呈現三類情感")

    # ── 項目二：NPS計算 (25分) ────────────────────────────────────────────────
    if re.search(r"NPS|情感淨值|淨推薦", text):
        score += 10
        details.append("✅ [NPS] 識別並計算 NPS 指標 (+10)")
    else:
        details.append("❌ [NPS] 未計算 NPS 指標")

    # 20 個商品均出現
    prod_names_check = ["Samsung", "MacBook", "Sony", "iPad",
                        "Dyson", "Panasonic", "大金", "Philips",
                        "UNIQLO", "Nike", "Levi", "ZARA",
                        "SK-II", "La Mer", "資生堂", "YSL",
                        "哈密瓜", "堅果", "辛拉麵", "伯朗"]
    prod_coverage = sum(1 for n in prod_names_check if n in text)
    if prod_coverage >= 15:
        score += 10
        details.append(f"✅ [NPS] 覆蓋 {prod_coverage}/20 個商品 (+10)")
    elif prod_coverage >= 8:
        score += 5
        details.append(f"⚠️ [NPS] 覆蓋 {prod_coverage}/20 個商品（部分，+5）")
    else:
        details.append(f"❌ [NPS] 覆蓋 {prod_coverage}/20 個商品")

    if re.search(r"(最高|最佳口碑|NPS.*最高|最低|最差口碑|NPS.*最低)", text):
        score += 5
        details.append("✅ [NPS] 識別最高/最低 NPS 商品 (+5)")
    else:
        details.append("❌ [NPS] 未識別極端 NPS 商品")

    # ── 項目三：抱怨關鍵詞 (20分) ────────────────────────────────────────────
    neg_kw_found = sum(1 for kw in NEGATIVE_KW if kw in text)
    if neg_kw_found >= 5:
        score += 12
        details.append(f"✅ [抱怨] 識別 {neg_kw_found} 個負面關鍵詞 (+12)")
    elif neg_kw_found >= 3:
        score += 6
        details.append(f"⚠️ [抱怨] 識別 {neg_kw_found} 個負面關鍵詞（+6）")
    else:
        details.append(f"❌ [抱怨] 僅識別 {neg_kw_found} 個負面關鍵詞")

    if re.search(r"(前3|前三|Top\s*3|最多.*抱怨|抱怨.*最多)", text):
        score += 8
        details.append("✅ [抱怨] 列出前3抱怨關鍵詞 (+8)")
    else:
        details.append("❌ [抱怨] 未列出前3抱怨關鍵詞")

    # ── 項目四：有用評論分析 (20分) ──────────────────────────────────────────
    if re.search(r"(helpful_votes|有用評論|高用處|helpful)", text, re.IGNORECASE):
        score += 8
        details.append("✅ [有用] 分析 helpful_votes 高評論組 (+8)")
    else:
        details.append("❌ [有用] 未分析 helpful_votes")

    # 負面偏向指數（> 1 通常為真）或結論討論
    if re.search(r"(負面偏向|偏向負面|偏負面|負面.*高.*平均|高.*負面.*均)", text):
        score += 7
        details.append("✅ [有用] 分析負面偏向現象 (+7)")
    else:
        details.append("❌ [有用] 未分析負面偏向現象")

    if re.search(r"(前20%|前\s*240|top\s*20|排名前)", text, re.IGNORECASE):
        score += 5
        details.append("✅ [有用] 正確定義高用處組（前20%）(+5)")
    else:
        details.append("❌ [有用] 未明確定義高用處組")

    # ── 項目五：跨平台分析 (15分) ────────────────────────────────────────────
    plat_cov = sum(1 for p in ["shopee", "momo", "pchome"] if p in text.lower())
    if plat_cov == 3:
        score += 8
        details.append("✅ [平台] 三平台均分析 (+8)")
    else:
        details.append(f"❌ [平台] 僅分析 {plat_cov} 個平台")

    if re.search(r"(差異最大|評分最高.*平台|平台.*評分|評分.*平台)", text):
        score += 7
        details.append("✅ [平台] 呈現平台評分差異結論 (+7)")
    else:
        details.append("❌ [平台] 未呈現平台評分差異結論")

    return {
        "score": score,
        "max_score": 100,
        "passed": score >= 60,
        "details": "\n".join(details),
    }


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

---

## LLM Judge Rubric

### Criterion 1: 情感分類與 NPS 計算正確性 (Weight: 35%)

**Score 1.0**: 依詞典規則（負面優先）正確分類，全體正面/負面/中性比例與資料一致；20 個商品的 NPS 由實際資料正確計算並排序，最高/最低口碑商品判斷正確。
**Score 0.75**: 分類大致正確、NPS 覆蓋多數商品，僅少量數字偏差。
**Score 0.5**: 分類或 NPS 其一明顯有誤，或數值疑似估計而非實算。
**Score 0.25**: 僅有零星分類或 NPS，缺乏系統性計算。
**Score 0.0**: 未實際進行情感分類或 NPS 計算。

### Criterion 2: 抱怨關鍵詞與有用評論偏向分析 (Weight: 30%)

**Score 1.0**: 從各商品負面評論正確統計負面關鍵詞並列出前 3 名抱怨詞；正確定義高用處組（前 20%），計算負面偏向指數並給出合理結論。
**Score 0.75**: 兩項分析其一完整、另一項僅有小瑕疵。
**Score 0.5**: 抱怨詞或負面偏向有提及但數值疑似估計或定義不清。
**Score 0.25**: 僅有片段結果，缺少前 3 名或偏向指數。
**Score 0.0**: 兩項分析皆未進行。

### Criterion 3: 跨平台分析與洞察品質 (Weight: 20%)

**Score 1.0**: 涵蓋 shopee/momo/pchome 三平台，建立商品 × 平台評分矩陣，找出差異最大前 5 商品並判斷最高平均評分平台；洞察摘要與優化建議具體可行。
**Score 0.75**: 平台分析完整但洞察略嫌一般，或漏一個結論。
**Score 0.5**: 平台分析不完整或洞察流於空泛。
**Score 0.25**: 僅提及部分平台，缺乏結論。
**Score 0.0**: 未進行跨平台分析。

### Criterion 4: 報告結構與清晰度 (Weight: 15%)

**Score 1.0**: 章節齊全（六大段落），使用適當 Markdown 標題與表格，數字內部一致，含洞察摘要與商品優化建議。
**Score 0.75**: 結構良好，僅有少量不一致。
**Score 0.5**: 內容尚可但組織鬆散或缺少部分章節。
**Score 0.25**: 難以閱讀或結構殘缺。
**Score 0.0**: 無結構或內容空白。

---

## Additional Notes

本任務考驗以下能力（核心考驗）：

- **關鍵詞情感分類**：基於詞典的規則式情感判斷、優先順序邏輯
- **NPS 計算**：分組聚合、百分比計算、排序
- **文本特徵頻率統計**：從負面評論中提取高頻詞彙
- **分組比較**：高用處組 vs 全體的統計比較
- **多維交叉分析**：商品 × 平台的評分矩陣
