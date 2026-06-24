---
id: task_09_network_recovery_checklist
name: 網路故障排除 SOP 快速參考卡製作
category: markdown_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/markdown/network_recovery_sop.md
    dest: network_recovery_sop.md
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---
## Prompt

你是一位 IT 支援工程師，公司給了你一份完整的網路故障排除標準作業程序（SOP）文件 `network_recovery_sop.md`。

你的任務是閱讀此文件，並製作一份供現場工程師使用的**快速參考資料**。

### 任務要求

**Step 1: 讀取 SOP 文件**
讀取 `network_recovery_sop.md` 全文。

**Step 2: 提取各階段步驟**
SOP 分為 5 個階段，提取每個階段的所有步驟：
- 第一階段：初始診斷（Steps 1-4）
- 第二階段：故障隔離（Steps 5-8）
- 第三階段：修復執行（Steps 9-12）
- 第四階段：驗證（Steps 13-15）
- 第五階段：文件記錄（Steps 16-18）

**Step 3: 列出高風險操作**
從「高風險操作清單」章節，列出所有需要二次確認的操作及其風險說明。
應找到至少 3 項（SOP 中有 4 項）。

**Step 4: 製作 L1 事故快速參考卡**
L1 等級（嚴重：全公司斷網，15分鐘內回應）的完整處理流程：
- 列出 L1 事故的定義和回應時間
- 列出 L1 觸發時必須完成的步驟
- 包含 NOC 緊急聯絡方式（從 SOP 中找到電話/Email）

**Step 5: 統計授權要求**
計算各類步驟數量：
- 總步驟數（Step 1 到 Step 18 = 18 步）
- 需要授權的步驟：找到標記 `[需授權]` 的步驟（Step 9, 10, 11 = 3 步）
- 需要二次確認的步驟：找到標記 `[需二次確認]` 的步驟（Step 12 = 1 步）

**輸出格式：**
將結果輸出至 `sop_quick_reference.md`，包含以下內容（格式自由，但需清晰）：

1. 標題：SOP 快速參考卡
2. 五個階段的步驟摘要（每步驟一行，含步驟號）
3. 高風險操作清單（含風險說明）
4. L1 事故快速處理指南（含 NOC 聯絡方式）
5. 統計摘要（總步驟數、需授權數、需二次確認數）

---

## Expected Behavior

1. 讀取 `network_recovery_sop.md` 的全文
2. 識別並解析5個標題以「## 第X階段」開頭的章節
3. 從每個章節提取以「### Step N:」格式標記的步驟
4. 搜尋「高風險操作清單」章節，找到標記的4項操作
5. 識別步驟標記：
   - `[需授權]`: Step 9, Step 10, Step 11（共3步）
   - `[需二次確認]`: Step 12（共1步）
6. 從文件中找到 NOC 聯絡方式：
   - Email: noc@corp.com
   - 電話: ext.9911
7. 統計 Step 1 到 Step 18 = 18 個總步驟
8. 輸出結構清晰的 `sop_quick_reference.md`

**關鍵數字：**
- 總步驟數：18
- 需授權步驟：3（Step 9, 10, 11）
- 需二次確認步驟：1（Step 12）
- 高風險操作：4項（iptables -F, ip link set down, route del default, systemctl restart networking）
- NOC Email: noc@corp.com
- NOC 電話: ext.9911

---

## Grading Criteria

- [ ] 輸出檔案 sop_quick_reference.md 存在
- [ ] 全部 5 個階段都有出現
- [ ] 高風險操作列出至少 3 項（含風險說明）
- [ ] L1 事故處理步驟有提取
- [ ] 授權步驟計數（3步）
- [ ] 二次確認步驟計數（至少1步）
- [ ] NOC 聯絡方式有提及
- [ ] 報告結構清晰完整

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    SCORE_KEYS = [
        "file_exists",
        "all_5_phases_present",
        "high_risk_operations_listed",
        "l1_incident_steps_extracted",
        "authorization_steps_counted",
        "double_confirm_steps_counted",
        "noc_contact_mentioned",
        "report_well_structured",
    ]

    workspace = Path(workspace_path)
    report_path = workspace / "sop_quick_reference.md"
    for alt in ["sop_quick_reference.md", "quick_reference.md", "sop_reference.md", "sop.md"]:
        if not report_path.exists() and (workspace / alt).exists():
            report_path = workspace / alt
    if not report_path.exists():
        return {k: 0.0 for k in SCORE_KEYS}

    content = report_path.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()

    scores = {}

    # 1. file_exists
    scores["file_exists"] = 1.0

    # 2. all_5_phases_present
    phase_patterns = [
        r'第一階段|phase.?1|初始診斷|step.?[1-4]',
        r'第二階段|phase.?2|故障隔離|step.?[5-8]',
        r'第三階段|phase.?3|修復執行|step.?(?:9|1[0-2])',
        r'第四階段|phase.?4|驗證|step.?1[3-5]',
        r'第五階段|phase.?5|文件記錄|step.?1[6-8]',
    ]
    phase_count = sum(1 for p in phase_patterns if re.search(p, cl))
    scores["all_5_phases_present"] = 1.0 if phase_count >= 5 else (0.5 if phase_count >= 3 else 0.0)

    # 3. high_risk_operations_listed (at least 3 of 4)
    high_risk_patterns = [
        r'iptables.*-f|iptables.*flush|清空.*規則',
        r'ip link set.*down|interface.*down|介面.*down',
        r'route del default|ip route del default|預設路由.*刪除',
        r'systemctl restart networking|networking.*restart',
    ]
    risk_count = sum(1 for p in high_risk_patterns if re.search(p, cl))
    scores["high_risk_operations_listed"] = 1.0 if risk_count >= 3 else (0.5 if risk_count >= 2 else 0.0)

    # 4. l1_incident_steps_extracted
    has_l1 = bool(re.search(r'\bL1\b|l1 事故|等級.*L1|嚴重.*全公司|全公司.*斷網', content))
    has_15min = bool(re.search(r'15.?分鐘|15 min', cl))
    scores["l1_incident_steps_extracted"] = 1.0 if (has_l1 and has_15min) else (0.5 if has_l1 else 0.0)

    # 5. authorization_steps_counted (steps 9, 10, 11 = 3)
    has_auth_mention = bool(re.search(r'需授權|authorization|need.*auth|authorized|授權.*步驟|step.?9|step.?10|step.?11', cl))
    has_count_3 = bool(re.search(r'3\s*步|3\s*個.*授權|授權.*3|three.*auth|auth.*3', cl))
    scores["authorization_steps_counted"] = 1.0 if (has_auth_mention and has_count_3) else (0.5 if has_auth_mention else 0.0)

    # 6. double_confirm_steps_counted (step 12 = 1)
    has_double = bool(re.search(r'二次確認|double.?confirm|double.?check|step.?12|iptables|需二次', cl))
    scores["double_confirm_steps_counted"] = 1.0 if has_double else 0.0

    # 7. noc_contact_mentioned
    has_noc_email = bool(re.search(r'noc@corp\.com', cl))
    has_noc_phone = bool(re.search(r'ext\.?9911|9911|noc.*phone|noc.*電話', cl))
    scores["noc_contact_mentioned"] = 1.0 if (has_noc_email or has_noc_phone) else 0.0

    # 8. report_well_structured — has headings, tables or lists
    has_headings = len(re.findall(r'^##\s+', content, re.MULTILINE)) >= 3
    has_lists = len(re.findall(r'^[-*]\s+', content, re.MULTILINE)) >= 5
    has_steps = bool(re.search(r'step \d+|步驟 \d+|Step\s+\d+', content))
    structure_count = sum([has_headings, has_lists, has_steps])
    scores["report_well_structured"] = 1.0 if structure_count >= 3 else (0.5 if structure_count >= 2 else 0.0)

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

---

## LLM Judge Rubric

### Criterion 1: 內容提取準確度 (Weight: 35%)
**Score 1.0**: 正確提取全部18個步驟並分配到5個階段，授權/二次確認計數正確（授權3步，二次確認1步），高風險操作全部4項列出
**Score 0.75**: 提取了大部分步驟，授權計數正確，但遺漏1-2個高風險操作
**Score 0.5**: 識別了大部分階段但步驟有遺漏，計數不完整
**Score 0.25**: 只讀取了部分章節，大量遺漏
**Score 0.0**: 未成功讀取文件或輸出為空

### Criterion 2: L1 事故快速參考實用性 (Weight: 30%)
**Score 1.0**: L1 快速參考包含：定義（全公司斷網）、回應時間（15分鐘）、完整步驟流程、NOC 聯絡方式（email + 電話）
**Score 0.75**: 包含 L1 定義和大部分內容，但缺少聯絡方式或回應時間
**Score 0.5**: 有 L1 相關內容但不完整
**Score 0.25**: 提到 L1 但沒有具體參考資訊
**Score 0.0**: 沒有 L1 特定內容

### Criterion 3: 高風險操作清單完整性 (Weight: 20%)
**Score 1.0**: 列出全部4項高風險操作，每項都附上風險說明和回滾方式
**Score 0.75**: 列出3-4項，但回滾方式不完整
**Score 0.5**: 列出2-3項
**Score 0.25**: 只提到高風險操作概念，沒有具體列出
**Score 0.0**: 未列出高風險操作

### Criterion 4: 報告可讀性與格式 (Weight: 15%)
**Score 1.0**: 格式清晰（使用表格或分類清單），易於現場工程師快速查閱，有明確的章節標題
**Score 0.75**: 格式基本清晰，但部分章節排版不佳
**Score 0.5**: 內容正確但格式凌亂，難以快速查閱
**Score 0.25**: 以純文字呈現，沒有結構化格式
**Score 0.0**: 格式不可讀

---

## Additional Notes

**測試重點：**
- Markdown 文件解析：識別標題層級、表格、程式碼區塊
- 結構化資訊提取（分階段步驟）
- 計數任務（授權步驟數量）
- 資訊篩選（L1 事故特定資訊）

**常見失敗模式：**
- 未找到 Step 12 的 `[需二次確認]` 標籤（容易與 `[需授權]` 混淆）
- 遺漏「高風險操作清單」章節（在文件後半段）
- NOC 聯絡方式分散在兩個地方（Step 6 和附錄 B），需要全部找到
- 步驟計數到18但忘記確認附錄中沒有額外步驟

**設計說明：**
此為 🟢 Easy 任務，主要測試 Markdown 文件的基本解析能力和結構化資訊提取，不需要複雜的計算或跨文件比對。
