---
id: task_review_fake_detection
name: 電商評論刷評偵測分析
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

你是一位電商平台的資料分析師。請讀取 `product_reviews_2024.json`（1,200 筆商品評論），對評論資料進行「刷評（假評）偵測」分析，輸出 `fake_review_report.md`。

### 分析項目一：異常指標統計

計算以下三個異常信號：

1. **速度異常（Velocity）**：同一 `user_id` 在 7 天內對同一 `product_id` 評論超過 1 次的評論筆數（以評論為單位，而非 user 數）
2. **未驗證高分比例**：`verified_purchase = false` 且 `rating >= 4` 的評論，佔全部評論的比例（%）
3. **短評高分比例**：`review_body` 字數 < 20 個中文字（以 Python `len()` 計算）且 `rating >= 4` 的評論比例（%）

以表格列出三個指標的數值與說明。

### 分析項目二：商品「可信評分」計算

定義：移除「可疑評論」後的平均 rating。

可疑評論判定規則（符合其中任一即視為可疑）：
- `verified_purchase = false` 且 `rating >= 4`
- `len(review_body) < 20` 且 `rating >= 4`
- 同一 user 在 7 天內對同一商品評論超過 1 次（所有相關評論均標記可疑）

計算每個商品的：
- 原始平均 rating（含所有評論）
- 可疑評論數
- 移除可疑評論後的可信評分
- 評分差異（原始 - 可信）

以表格呈現全部 20 個商品的結果，按評分差異由高至低排序。

### 分析項目三：刷評風險分數計算

為每個商品建立 0~100 的「刷評風險分數」，加權計算公式：

```
risk_score = (
    unverified_high_rating_ratio * 30 +   # 未驗證高分比例，0~1 正規化
    short_review_ratio * 20 +              # 短評高分比例，0~1 正規化
    velocity_ratio * 30 +                  # 速度異常評論比例，0~1 正規化
    homogeneity_score * 20                 # 同質化分數（見說明）
) * 100
```

**同質化分數計算方式**：
- 取該商品所有 rating=5 評論的 `review_body`
- 計算標題重複率：`(重複 review_title 數 / 總 rating=5 評論數)`
- 此值即為 `homogeneity_score`（0~1）

所有比例請先在各商品內部計算（分子/該商品評論總數），再乘以對應權重。

以表格呈現 20 個商品的風險分數，由高至低排序。

### 分析項目四：Top 5 疑似刷評最嚴重商品

根據「刷評風險分數」取前 5 名，對每個商品：
1. 列出商品名稱、類別
2. 原始平均 rating vs 可信評分
3. 可疑評論數/總評論數
4. 主要異常信號說明（文字描述）
5. 建議平台採取的處置動作

### 分析項目五：平台比較分析

計算每個平台（shopee / momo / pchome）的：
1. 總評論數
2. 可疑評論數與比例（%）
3. 平均 rating（全體）
4. 平均 rating（移除可疑後）
5. 刷評率排名（1=最嚴重）

判斷哪個平台的刷評問題最嚴重，並給出數據支持的結論。

### 輸出格式

輸出檔案：`fake_review_report.md`

報告須依序包含以下六個章節（請於 `fake_review_report.md` 內以對應標題呈現）：

- 標題：`# 刷評偵測分析報告`
- 開頭標註：`**資料集**：product_reviews_2024.json（1,200 筆）` 與 `**分析日期**：YYYY-MM-DD`
- 章節一：一、異常指標統計
- 章節二：二、商品可信評分計算（全部 20 個商品表格）
- 章節三：三、刷評風險分數排行（全部 20 個商品表格）
- 章節四：四、Top 5 高風險商品深度分析
- 章節五：五、平台比較分析
- 章節六：六、總結與建議

---

## Expected Behavior

代理人應執行以下步驟：

1. 讀取並解析 `product_reviews_2024.json`，逐筆取得 `user_id`、`product_id`、`rating`、`verified_purchase`、`review_body`、`review_title`、`platform`、評論時間等欄位
2. **異常指標**：以日期計算找出 7 天內同一 user 對同一商品的重複評論（速度異常）；統計未驗證高分（`verified_purchase=false` 且 `rating>=4`）與短評高分（`len(review_body)<20` 且 `rating>=4`）比例
3. **可信評分**：依三條可疑規則標記每筆評論，對每個商品計算原始平均 rating、可疑評論數、移除可疑後的可信評分與評分差異，並按差異由高至低排序輸出 20 個商品
4. **風險分數**：在各商品內部計算未驗證高分比例、短評比例、速度異常比例與同質化分數（rating=5 評論的標題重複率），套用 30/20/30/20 加權公式得到 0~100 風險分數並排序
5. **Top 5**：取風險分數前 5 名商品，列出名稱/類別、評分比較、可疑佔比、異常信號說明與處置建議
6. **平台比較**：分別統計 shopee / momo / pchome 三平台的總評論數、可疑比例、平均與去可疑平均 rating、刷評率排名，並指出刷評最嚴重的平台
7. 以完整 Markdown 報告寫入 `fake_review_report.md`，包含六個章節與全部表格

預期參考值（近似）：
- 全部 1,200 筆評論、20 個商品、3 個平台
- 未驗證高分比例與短評高分比例為個位數至兩位數百分比
- 風險分數與評分差異應為合理量化數值

---

## Grading Criteria

- [ ] 輸出檔案 `fake_review_report.md` 存在
- [ ] 未驗證高分比例計算正確（容忍 ±3%）
- [ ] 短評高分比例計算正確（容忍 ±3%）
- [ ] 識別並說明速度異常（7 天內同一 user 對同一商品重複評論）指標
- [ ] 實作可疑評論移除邏輯並呈現可信評分
- [ ] 覆蓋 20 個商品（至少 15 個商品名稱出現）並呈現原始 vs 可信評分比較
- [ ] 建立刷評風險分數並實作多維度加權計算（含同質化分數）
- [ ] 識別 Top 5 高風險商品並提出平台處置建議
- [ ] 完成 shopee / momo / pchome 三平台比較並提出刷評率最嚴重結論

---

## Automated Checks

```python
import re, json
from pathlib import Path

def grade(transcript: list, submission_dir: str) -> dict:
    """
    評分標準（100分）：
    - 項目一異常指標數值正確（20分）
    - 項目二可信評分計算（25分）
    - 項目三風險分數計算（25分）
    - 項目四Top5分析（15分）
    - 項目五平台比較（15分）
    """
    report_path = Path(submission_dir) / "fake_review_report.md"
    if not report_path.exists():
        return {"score": 0, "max_score": 100, "details": "未找到 fake_review_report.md"}

    text = report_path.read_text(encoding="utf-8")
    score = 0
    details = []

    # ── 載入資料，計算參考答案 ────────────────────────────────────────────────
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

    # 參考：未驗證高分比例
    unverified_high = sum(1 for r in reviews if not r["verified_purchase"] and r["rating"] >= 4)
    unverified_high_pct = unverified_high / len(reviews) * 100

    # 參考：短評高分
    short_high = sum(1 for r in reviews if len(r["review_body"]) < 20 and r["rating"] >= 4)
    short_high_pct = short_high / len(reviews) * 100

    # ── 項目一：異常指標 (20分) ───────────────────────────────────────────────
    # 未驗證高分比例（容忍±3%）
    found_pcts = [float(x) for x in re.findall(r"(\d+\.?\d*)\s*%", text)]
    ref_uhp = round(unverified_high_pct, 1)
    close_to_uhp = any(abs(p - ref_uhp) <= 3.0 for p in found_pcts)
    if close_to_uhp:
        score += 8
        details.append(f"✅ [異常] 未驗證高分比例計算正確（參考值 ~{ref_uhp}%，+8）")
    else:
        details.append(f"❌ [異常] 未驗證高分比例偏差過大（參考值 ~{ref_uhp}%）")

    # 短評高分比例
    ref_shp = round(short_high_pct, 1)
    close_to_shp = any(abs(p - ref_shp) <= 3.0 for p in found_pcts)
    if close_to_shp:
        score += 6
        details.append(f"✅ [異常] 短評高分比例計算正確（參考值 ~{ref_shp}%，+6）")
    else:
        details.append(f"❌ [異常] 短評高分比例偏差（參考值 ~{ref_shp}%）")

    if re.search(r"(速度異常|velocity|7天|七天|同一.*評論.*[1-9]\s*次)", text, re.IGNORECASE):
        score += 6
        details.append("✅ [異常] 識別速度異常指標 (+6)")
    else:
        details.append("❌ [異常] 未識別速度異常指標")

    # ── 項目二：可信評分 (25分) ──────────────────────────────────────────────
    if re.search(r"(可信評分|可疑評論.*移除|移除.*可疑)", text):
        score += 8
        details.append("✅ [可信評分] 實作可疑評論移除邏輯 (+8)")
    else:
        details.append("❌ [可信評分] 未識別可疑評論移除邏輯")

    # 20 個商品均出現
    products = ["ELEC-001","ELEC-002","ELEC-003","ELEC-004",
                "HOME-001","HOME-002","HOME-003","HOME-004",
                "FASH-001","FASH-002","FASH-003","FASH-004",
                "BEAU-001","BEAU-002","BEAU-003","BEAU-004",
                "FOOD-001","FOOD-002","FOOD-003","FOOD-004"]
    prod_names = ["Samsung Galaxy", "MacBook Pro", "WH-1000XM5", "iPad",
                  "Dyson", "Panasonic", "大金", "Philips",
                  "UNIQLO", "Nike", "Levi", "ZARA",
                  "SK-II", "La Mer", "資生堂", "YSL",
                  "哈密瓜", "堅果", "辛拉麵", "伯朗"]
    found_products = sum(1 for name in prod_names if name in text)
    if found_products >= 15:
        score += 10
        details.append(f"✅ [可信評分] 覆蓋 {found_products}/20 個商品 (+10)")
    elif found_products >= 8:
        score += 5
        details.append(f"⚠️ [可信評分] 覆蓋 {found_products}/20 個商品（部分，+5）")
    else:
        details.append(f"❌ [可信評分] 僅覆蓋 {found_products}/20 個商品")

    if re.search(r"(評分差異|原始評分|可信評分|信任評分)", text):
        score += 7
        details.append("✅ [可信評分] 呈現原始vs可信評分比較 (+7)")
    else:
        details.append("❌ [可信評分] 未呈現評分比較")

    # ── 項目三：風險分數 (25分) ──────────────────────────────────────────────
    if re.search(r"(風險分數|risk.?score|刷評風險)", text, re.IGNORECASE):
        score += 10
        details.append("✅ [風險分數] 建立刷評風險分數指標 (+10)")
    else:
        details.append("❌ [風險分數] 未建立風險分數")

    if re.search(r"(加權|weight|權重.{0,20}(30|20)|homogeneity|同質化)", text, re.IGNORECASE):
        score += 8
        details.append("✅ [風險分數] 實作多維度加權計算 (+8)")
    else:
        details.append("❌ [風險分數] 未實作加權計算")

    # 是否有排序（數字由高到低）
    numbers_in_text = [float(x) for x in re.findall(r"\b(\d+\.?\d+)\b", text) if float(x) <= 100]
    if len(numbers_in_text) >= 10:
        score += 7
        details.append("✅ [風險分數] 呈現量化風險分數 (+7)")
    else:
        details.append("❌ [風險分數] 量化數值不足")

    # ── 項目四：Top 5 (15分) ─────────────────────────────────────────────────
    top5_mentions = len(re.findall(r"(Top\s*5|前五|第[一1]名|最高風險)", text))
    if top5_mentions >= 1:
        score += 8
        details.append("✅ [Top5] 識別高風險商品 (+8)")
    else:
        details.append("❌ [Top5] 未識別 Top5 高風險商品")

    if re.search(r"(建議|處置|下架|警告|標記|auditing)", text):
        score += 7
        details.append("✅ [Top5] 提出處置建議 (+7)")
    else:
        details.append("❌ [Top5] 未提出處置建議")

    # ── 項目五：平台比較 (15分) ──────────────────────────────────────────────
    platforms_mentioned = sum(1 for p in ["shopee", "momo", "pchome"] if p in text.lower())
    if platforms_mentioned == 3:
        score += 8
        details.append("✅ [平台] 三平台均分析 (+8)")
    else:
        details.append(f"❌ [平台] 僅分析 {platforms_mentioned} 個平台")

    if re.search(r"(最嚴重|刷評率.*高|比較.*平台|平台.*差異)", text):
        score += 7
        details.append("✅ [平台] 提出平台刷評率比較結論 (+7)")
    else:
        details.append("❌ [平台] 未提出平台比較結論")

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

### Criterion 1: 異常偵測正確性 (Weight: 30%)

**Score 1.0**：三種異常信號（速度異常、未驗證高分、短評高分）皆正確定義並計算；未驗證高分與短評高分比例與資料一致，速度異常採用正確的 7 天 / 同 user 同商品判定。
**Score 0.75**：三種信號皆涵蓋，但有一項數值或定義略有出入。
**Score 0.5**：僅正確處理 1~2 種信號，或比例明顯偏差。
**Score 0.25**：信號定義含糊或數值疑似憑空估算。
**Score 0.0**：未實際進行異常偵測。

### Criterion 2: 可信評分與風險分數計算 (Weight: 30%)

**Score 1.0**：依三條可疑規則正確標記評論，逐商品計算原始平均、可疑數、可信評分與評分差異；風險分數採用 30/20/30/20 加權公式並正確計算同質化分數，20 個商品皆有量化結果且正確排序。
**Score 0.75**：可信評分與風險分數大致正確，僅同質化分數或部分商品有小瑕疵。
**Score 0.5**：實作其一（可信評分或風險分數），另一項缺漏或加權不正確。
**Score 0.25**：僅有零星數值，缺乏可重現的計算邏輯。
**Score 0.0**：未實作可信評分與風險分數。

### Criterion 3: 洞察與處置建議品質 (Weight: 25%)

**Score 1.0**：Top 5 高風險商品分析具體，異常信號說明對應實際數據；平台比較正確指出刷評最嚴重平台並有數據支持；處置建議具可操作性。
**Score 0.75**：Top 5 與平台比較完整，但部分結論支持力較弱。
**Score 0.5**：有 Top 5 或平台比較其一，洞察偏淺。
**Score 0.25**：僅列數字而無解讀或建議。
**Score 0.0**：無洞察或建議。

### Criterion 4: 報告結構與清晰度 (Weight: 15%)

**Score 1.0**：報告章節完整（六大節），表格格式正確、易讀，數字內部一致（分項加總相符）。
**Score 0.75**：結構良好，僅有少數不一致。
**Score 0.5**：內容尚可但組織鬆散或表格不全。
**Score 0.25**：難以閱讀或缺少主要章節。
**Score 0.0**：無結構或內容空白。

---

## Additional Notes

本任務核心考驗：

- **多維度異常偵測**：速度異常、未驗證高分、短評高分三種信號的組合識別
- **加權評分設計**：四個信號不同權重的風險分數計算與正規化
- **比較分析**：原始評分 vs 可信評分的差異量化
- **JSON 資料處理**：大量評論的日期計算、字數統計、分組聚合
