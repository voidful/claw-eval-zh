---
id: task_docx_contract_audit
name: 供應商服務合約法務合規審計
category: docx_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/docx/vendor_contract_2024.docx
    dest: vendor_contract_2024.docx
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v2
---
## Prompt

你是一位法務合規顧問。請讀取 `vendor_contract_2024.docx`，對此份虛構供應商服務合約進行全面的法律合規審計，並輸出 `contract_audit_report.md`。

報告必須包含以下五個審計項目：

### 項目一：金額數字驗算

1. 從合約中提取所有金額數字（包含服務項目明細、里程碑付款表）
2. 計算服務項目各小計之加總（SVC-001 到 SVC-010）
3. 驗算：分期付款（第1期～第8期）之加總是否等於合約總金額 30,000,000 元
4. 找出文中提及的「稅前合計」「含稅總金額」與最終議定金額之間的差異說明
5. 以表格呈現所有數字來源、數值與驗算結果（通過/異常）

### 項目二：SLA 指標分析

1. 從 SLA 指標表（附件二）提取所有服務水準指標
2. 計算懲罰觸發條件：
   - 若系統可用性為 99.7%，應扣款多少金額？（計算過程要詳細）
   - 若可用性連續 2 個月低於 95%，依哪個條款可啟動終止合約？
3. 計算每月允許最長停機時間（99.9% uptime，以分鐘表示）
4. P1 事故若回應超過 1 小時，應扣款多少？

### 項目三：交叉引用條款驗證

1. 掃描合約全文，找出所有「依第X條」「依本條」「依附件X」格式的引用
2. 逐一驗證引用的條款/附件是否存在於合約中
3. 標記「引用正確」或「引用不存在（潛在錯誤）」
4. 統計交叉引用總數、正確數、疑似錯誤數

### 項目四：付款里程碑時間計算

1. 從里程碑付款表提取所有付款日期
2. 計算相鄰里程碑之間的間隔天數
3. 識別間隔最長和最短的相鄰里程碑
4. 計算合約總期間（2024-04-07 至 2027-03-01）共幾天
5. 以表格呈現各期次、日期、距上期天數

### 項目五：模糊措辭識別

1. 全文搜尋下列關鍵詞：「合理」「適當」「視情況」「同等級」「相應」「充分」「適時」
2. 列出每個關鍵詞出現的條款位置、原文摘錄
3. 評估該措辭對甲方（委託方）是否有利或不利
4. 提出建議措辭（更明確的替代寫法）

### 輸出格式

輸出檔案：`contract_audit_report.md`

報告須以一級標題（`#`）「合約法務審計報告」開頭，並包含下列六個二級章節（`##`）：

- 一、金額驗算
- 二、SLA 指標分析
- 三、交叉引用驗證
- 四、里程碑時間計算
- 五、模糊措辭識別
- 六、審計總結與風險等級評估

## Expected Behavior

代理人應執行以下步驟：

1. 使用 DOCX 解析工具（如 python-docx）讀取 `vendor_contract_2024.docx`，同時擷取段落文字與所有表格內容
2. 從服務項目明細與里程碑付款表中提取所有金額，進行加總與驗算（各期加總應等於 30,000,000 元），並比對稅前合計、含稅總金額與最終議定金額之差異
3. 從 SLA 指標表計算停機時間與扣款：99.9% uptime 對應每月約 43.2 分鐘允許停機；99.7% 可用性對應 2% 扣款；並識別 P1 事故逾時的懲罰與終止條款
4. 掃描全文找出「依第X條」「依附件X」等交叉引用，逐一驗證引用目標是否存在，統計總數、正確數與疑似錯誤數
5. 從里程碑付款表提取日期，計算相鄰里程碑間隔天數與合約總期間（2024-04-07 至 2027-03-01 約 1059 天），識別最長與最短間隔
6. 全文搜尋模糊措辭關鍵詞，標註出現位置與原文，評估對甲方利弊並提出更明確的替代寫法
7. 以完整的 Markdown 報告輸出 `contract_audit_report.md`，涵蓋六大章節

關鍵預期數值（近似）：
- 合約總金額 30,000,000 元；8 期里程碑加總應等於此數
- 99.9% uptime → 每月允許停機約 43.2 分鐘
- 99.7% 可用性 → 2% 扣款（約 3,000 元）
- 合約總期間 2024-04-07 至 2027-03-01 約 1059 天

## Grading Criteria

- [ ] 輸出檔案 `contract_audit_report.md` 存在
- [ ] 識別合約總金額 30,000,000 元
- [ ] 提及至少 6 個里程碑期次（第1期～第8期）
- [ ] 分析稅費調整差異（稅前/含稅金額）
- [ ] 正確計算每月允許停機 43.2 分鐘（99.9% uptime）
- [ ] 正確計算 99.7% 可用性扣款（2% = 3,000 元）
- [ ] 識別 P1 逾時懲罰或終止條款
- [ ] 識別並驗證合約內部交叉引用（條款/附件）
- [ ] 計算里程碑間隔天數並識別最長/最短間隔
- [ ] 識別模糊措辭並提出改善建議

## Automated Checks

```python
import re, json
from pathlib import Path

def grade(transcript: list, submission_dir: str) -> dict:
    """
    評分標準（100分）：
    - 項目一金額驗算正確（30分）
    - 項目二SLA計算正確（25分）
    - 項目三交叉引用識別（20分）
    - 項目四里程碑時間計算（15分）
    - 項目五模糊措辭識別（10分）
    """
    report_path = Path(submission_dir) / "contract_audit_report.md"
    if not report_path.exists():
        return {"score": 0, "max_score": 100, "details": "未找到 contract_audit_report.md"}

    text = report_path.read_text(encoding="utf-8")
    score = 0
    details = []

    # ── 項目一：金額驗算 (30分) ──────────────────────────────────────────────
    # 分期加總 = 30,000,000
    if re.search(r"30[,，]?000[,，]?000", text):
        score += 10
        details.append("✅ [金額] 識別合約總金額 30,000,000 (+10)")
    else:
        details.append("❌ [金額] 未識別合約總金額")

    # 各期加總驗算通過（報告中需提及 8 期加總等於3000萬）
    periods_mentioned = len(re.findall(r"第[1-8一二三四五六七八]期", text))
    if periods_mentioned >= 6:
        score += 10
        details.append(f"✅ [金額] 提及 {periods_mentioned} 個里程碑期次 (+10)")
    else:
        details.append(f"❌ [金額] 僅提及 {periods_mentioned} 個期次（需≥6）")

    # 發現稅額或稅前合計說明
    if re.search(r"(稅前|含稅|1[,，]?400[,，]?000|29[,，]?400[,，]?000)", text):
        score += 10
        details.append("✅ [金額] 分析稅費調整差異 (+10)")
    else:
        details.append("❌ [金額] 未分析稅費差異")

    # ── 項目二：SLA 計算 (25分) ──────────────────────────────────────────────
    # 99.9% uptime → 43.2 分鐘允許停機（30天/月×24小時×60分鐘×0.1%）
    if re.search(r"43\.?[12]\s*分鐘", text):
        score += 8
        details.append("✅ [SLA] 正確計算每月允許停機 43.2 分鐘 (+8)")
    else:
        details.append("❌ [SLA] 未正確計算允許停機時間（期望 43.2 分鐘）")

    # 99.7% → 扣款 2% 或 3,000 元
    if re.search(r"(扣款.{0,10}2%|3[,，]?000\s*元|147[,，]?000)", text):
        score += 10
        details.append("✅ [SLA] 正確計算 99.7% 可用性扣款 (+10)")
    else:
        details.append("❌ [SLA] 未正確計算 99.7% 可用性扣款（期望 2% = 3,000 元）")

    # P1 逾時引用條款
    if re.search(r"(P1|第十二條|第12條).{0,100}(5[,，]?000|超時|逾時|終止)", text):
        score += 7
        details.append("✅ [SLA] 識別 P1 逾時懲罰或終止條款 (+7)")
    else:
        details.append("❌ [SLA] 未識別 P1 逾時相關懲罰")

    # ── 項目三：交叉引用 (20分) ──────────────────────────────────────────────
    cross_refs = len(re.findall(r"(第[一二三四五六七八九十百\d]+條|附件[一二三四\d])", text))
    if cross_refs >= 8:
        score += 12
        details.append(f"✅ [交叉引用] 識別 {cross_refs} 個引用 (+12)")
    elif cross_refs >= 4:
        score += 6
        details.append(f"⚠️ [交叉引用] 識別 {cross_refs} 個引用（不足，+6）")
    else:
        details.append(f"❌ [交叉引用] 僅識別 {cross_refs} 個引用")

    if re.search(r"(引用正確|引用存在|驗證|核對)", text):
        score += 8
        details.append("✅ [交叉引用] 進行引用有效性驗證 (+8)")
    else:
        details.append("❌ [交叉引用] 未進行引用有效性驗證")

    # ── 項目四：里程碑時間 (15分) ────────────────────────────────────────────
    # 計算天數（例如合約期間約1059天，或任意相鄰里程碑天數）
    if re.search(r"\d{3,4}\s*天", text):
        score += 8
        details.append("✅ [時間] 計算里程碑間隔天數 (+8)")
    else:
        details.append("❌ [時間] 未計算間隔天數")

    # 識別最長間隔里程碑
    if re.search(r"(最長|最短|間隔最大|間隔最小)", text):
        score += 7
        details.append("✅ [時間] 識別最長/最短間隔里程碑 (+7)")
    else:
        details.append("❌ [時間] 未識別最長/最短間隔")

    # ── 項目五：模糊措辭 (10分) ──────────────────────────────────────────────
    vague_found = sum(1 for kw in ["合理", "適當", "同等級", "相應", "充分"] if kw in text)
    if vague_found >= 3:
        score += 6
        details.append(f"✅ [措辭] 識別 {vague_found} 類模糊措辭 (+6)")
    else:
        details.append(f"❌ [措辭] 僅識別 {vague_found} 類模糊措辭（需≥3）")

    if re.search(r"(建議|替代|改寫|修改措辭|具體化)", text):
        score += 4
        details.append("✅ [措辭] 提出改善建議 (+4)")
    else:
        details.append("❌ [措辭] 未提出改善建議")

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

## LLM Judge Rubric

### Criterion 1: 金額驗算與稅費分析正確性 (Weight: 30%)

**Score 1.0**：正確提取所有金額，8 期里程碑加總驗算等於 30,000,000 元，並清楚說明稅前合計、含稅總金額與最終議定金額之間的差異，以表格呈現數字來源與驗算結果。
**Score 0.75**：金額提取大致正確，加總驗算正確，但稅費差異說明不完整。
**Score 0.5**：識別總金額但缺少加總驗算或稅費分析。
**Score 0.25**：僅零星提及金額，無驗算邏輯。
**Score 0.0**：未進行金額分析或數字明顯捏造。

### Criterion 2: SLA 計算與條款引用正確性 (Weight: 30%)

**Score 1.0**：正確計算 99.9% uptime 每月允許停機 43.2 分鐘、99.7% 可用性 2% 扣款，並識別 P1 逾時懲罰與終止條款，計算過程詳細；交叉引用驗證完整，統計總數/正確數/疑似錯誤數。
**Score 0.75**：SLA 計算大致正確，交叉引用驗證有少量遺漏。
**Score 0.5**：部分 SLA 計算或交叉引用驗證正確，但有明顯缺漏。
**Score 0.25**：僅提及指標而無實際計算或驗證。
**Score 0.0**：未進行 SLA 計算與引用驗證。

### Criterion 3: 時間計算與模糊措辭識別 (Weight: 25%)

**Score 1.0**：正確計算相鄰里程碑間隔天數與合約總期間（約 1059 天），識別最長/最短間隔；全面識別模糊措辭並標註位置、評估利弊、提出具體替代寫法。
**Score 0.75**：時間計算正確，模糊措辭識別大致完整但建議略弱。
**Score 0.5**：時間計算或模糊措辭其一完整，另一不足。
**Score 0.25**：僅部分完成。
**Score 0.0**：兩項皆未完成。

### Criterion 4: 報告結構與專業度 (Weight: 15%)

**Score 1.0**：報告分為六大章節，結構清晰，使用適當 Markdown 標題與表格，含風險等級評估，數字內部一致，呈現法務顧問的專業判斷。
**Score 0.75**：結構良好但有少量不一致或缺漏。
**Score 0.5**：內容尚可但組織鬆散。
**Score 0.25**：難以閱讀或缺少多數章節。
**Score 0.0**：無結構或空白。

## Additional Notes

本任務核心考驗：

- **DOCX 跨段落數字萃取**：需解析表格與段落文字中的金額
- **邏輯驗算**：加總比對、稅費計算
- **時間計算**：日期差、間隔天數
- **條款引用圖譜**：識別並驗證合約內部交叉引用
- **文本特徵識別**：模糊措辭偵測與法律風險評估
