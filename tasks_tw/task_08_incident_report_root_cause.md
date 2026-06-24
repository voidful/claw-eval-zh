---
id: task_08_incident_report_root_cause
name: 網路事故根本原因分析（DOCX + LOG 交叉驗證）
category: cross_format_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/docx/network_incident_report.docx
    dest: network_incident_report.docx
  - source: tw/logs/system_event.log
    dest: system_event.log
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---
## Prompt

你是一位資深 SRE（網站可靠性工程師），需要對 **2026-05-18** 的網路中斷事故進行根本原因分析。

你有兩個檔案：
1. `network_incident_report.docx` — 事故後驗（Post-Mortem）報告（Word 文件）
2. `system_event.log` — 系統事件日誌

**請完成以下分析任務：**

### 任務要求

**Step 1: 讀取兩個檔案**
- 使用 python-docx 讀取 DOCX 文件中的所有章節
- 逐行讀取 system_event.log

**Step 2: 交叉驗證時間軸**
從 DOCX 提取事故時間軸，並對照 LOG 中對應的事件。
需要找到以下關鍵時間點（LOG 中有對應記錄）：
- 09:15 — DNS 設定變更（CONFIG_CHANGE）
- 09:16 — 延遲告警（WARN）
- 09:17 — 第一個 ERROR 事件
- 09:20 — 斷路器觸發（Circuit Breaker OPEN）
- 14:30 — 監控告警（ALERT，failure_rate 超閾值）
- 17:30 — 回滾執行（CONFIG_CHANGE）

**Step 3: 識別根本原因鏈**
從 LOG 重建完整的根本原因鏈：
```
09:15 DNS 變更（192.168.1.253）
  → 09:16 延遲 4521ms（閾值 200ms）
  → 09:17 SERVFAIL（api-gateway 是第一個 ERROR 服務）
  → 09:20 Circuit Breaker OPEN（100% 失敗）
```

**Step 4: 驗證財務損失計算**
從 DOCX 讀取財務計算數字：
- 停機時間：確認是否為 8.25 小時（09:15 至 17:30）
- 每小時損失：NT$290,909
- 計算：8.25 × 290,909 = 2,399,999.25 ≈ NT$2,400,000
- 請驗證此計算並指出精確值與四捨五入後的差異

**Step 5: 識別首個 ERROR 事件**
在根本原因鏈中，找出第一個 ERROR 級別（非 CONFIG_CHANGE、非 WARN）的事件：
- 應為 09:17 [api-gateway] Failed to resolve api.github.com: SERVFAIL

**Step 6: 評估預防措施**
DOCX 中列出了 3 項預防措施，評估每一項的有效性及優先順序。

**輸出格式：**
請將分析結果輸出至 `root_cause_analysis.md`，必須包含以下章節（按順序）：

```markdown
### 事故時間軸（交叉驗證）
（LOG 與 DOCX 對照表格，至少包含6個關鍵時間點）

### 根本原因鏈（Root Cause Chain）
（從 LOG 重建的因果鏈，引用具體 LOG 條目）

### 財務損失驗證
（計算驗證，精確值 vs. 四捨五入值）

### 預防措施評估
（3 項措施各自評估）

### 改善建議
（至少 3 項具體建議）
```

**引用要求：**
- 兩個檔案都必須引用（直接引用文字片段）
- LOG 引用：包含完整時間戳記和級別
- DOCX 引用：包含章節名稱

---

## Expected Behavior

1. 使用 python-docx 解析 `network_incident_report.docx`，提取7個章節的內容
2. 讀取 `system_event.log`，搜尋關鍵時間點事件
3. 建立交叉驗證表格，列出 DOCX 時間軸 vs LOG 對應事件
4. 從 LOG 追蹤根本原因鏈：
   - `09:15:03 - CONFIG_CHANGE - [admin-alice] Modified /etc/resolv.conf`
   - `09:16:02 - WARN - [dns-monitor] DNS health check: 192.168.1.253 response latency=4521ms`
   - `09:17:01 - ERROR - [api-gateway] Failed to resolve api.github.com: SERVFAIL`（第一個 ERROR）
   - `09:20:00 - CRITICAL - [api-gateway] Circuit breaker OPEN: 100% requests failing`
5. 驗證財務計算：8.25 × 290,909 = 2,399,999.25（精確值），報告四捨五入為 2,400,000
6. 對 3 項預防措施進行質量評估
7. 輸出包含全部 5 個章節的 `root_cause_analysis.md`

**關鍵數字：**
- 精確財務損失：NT$2,399,999.25
- 四捨五入：NT$2,400,000
- 差異：NT$0.75
- 停機時長：8小時15分鐘 = 8.25小時
- 第一個 ERROR 服務：api-gateway（09:17:01）

---

## Grading Criteria

- [ ] 輸出檔案 root_cause_analysis.md 存在
- [ ] 時間軸交叉驗證（同時引用 LOG 和 DOCX）
- [ ] 根本原因識別：09:15 DNS CONFIG_CHANGE 事件被找到
- [ ] 第一個 ERROR 服務識別（api-gateway 在 09:17）
- [ ] Circuit Breaker 事件識別（09:20）
- [ ] 財務計算驗證（8.25h × 290909 ≈ 2400000）
- [ ] 回滾事件識別（17:30）
- [ ] 預防措施評估（至少提到 3 項）
- [ ] 跨格式引用（同時引用兩個檔案的具體文字）
- [ ] 全部 5 個章節存在

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    SCORE_KEYS = [
        "file_exists",
        "timeline_cross_referenced",
        "root_cause_dns_change_identified",
        "first_error_service_identified",
        "circuit_breaker_event_found",
        "financial_calc_verified",
        "rollback_event_identified",
        "prevention_measures_evaluated",
        "cross_format_evidence_cited",
        "all_sections_present",
    ]

    workspace = Path(workspace_path)
    report_path = workspace / "root_cause_analysis.md"
    for alt in ["root_cause_analysis.md", "root_cause.md", "analysis.md", "incident_analysis.md"]:
        if not report_path.exists() and (workspace / alt).exists():
            report_path = workspace / alt
    if not report_path.exists():
        return {k: 0.0 for k in SCORE_KEYS}

    content = report_path.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()

    scores = {}

    # 1. file_exists
    scores["file_exists"] = 1.0

    # 2. timeline_cross_referenced — mentions both LOG and DOCX
    has_log_ref = bool(re.search(r'system_event\.log|event\.log|日誌|log', cl))
    has_doc_ref = bool(re.search(r'network_incident|incident_report|docx|報告|post.?mortem', cl))
    scores["timeline_cross_referenced"] = 1.0 if (has_log_ref and has_doc_ref) else (0.5 if (has_log_ref or has_doc_ref) else 0.0)

    # 3. root_cause_dns_change_identified — 09:15 CONFIG_CHANGE
    has_0915 = bool(re.search(r'09:15', content))
    has_dns_change = bool(re.search(r'config.?change|dns.*(change|變更|modify|修改)|resolv\.conf.*chang|192\.168\.1\.253', cl))
    scores["root_cause_dns_change_identified"] = 1.0 if (has_0915 and has_dns_change) else (0.5 if has_dns_change else 0.0)

    # 4. first_error_service_identified — api-gateway at 09:17
    has_api_gw = bool(re.search(r'api.?gateway|api-gateway', cl))
    has_0917 = bool(re.search(r'09:17', content))
    has_servfail = bool(re.search(r'servfail|first.?error|第一.*error|第一.*錯誤', cl))
    scores["first_error_service_identified"] = 1.0 if (has_api_gw and (has_0917 or has_servfail)) else (0.5 if has_api_gw else 0.0)

    # 5. circuit_breaker_event_found — 09:20
    has_circuit = bool(re.search(r'circuit.?breaker|斷路器|09:20', cl))
    has_open = bool(re.search(r'open|100%.*fail|觸發|open', cl))
    scores["circuit_breaker_event_found"] = 1.0 if has_circuit else 0.0

    # 6. financial_calc_verified — 8.25h × 290909 ≈ 2400000
    has_8_25 = bool(re.search(r'8\.25|8 ?小時 ?15|8 hours 15', cl))
    has_290909 = bool(re.search(r'290.?909|290,909', content))
    has_2400000 = bool(re.search(r'2,400,000|2400000|2\.4 ?百萬|NT\$2,4', content))
    scores["financial_calc_verified"] = 1.0 if (has_8_25 and has_290909 and has_2400000) else (0.5 if (has_8_25 or has_2400000) else 0.0)

    # 7. rollback_event_identified — 17:30
    has_1730 = bool(re.search(r'17:30', content))
    has_rollback = bool(re.search(r'rollback|回滾|revert|restore|cp.*resolv|resolv.*bak', cl))
    scores["rollback_event_identified"] = 1.0 if (has_1730 and has_rollback) else (0.5 if has_rollback else 0.0)

    # 8. prevention_measures_evaluated — staging, monitoring, change approval
    has_staging = bool(re.search(r'staging|測試環境|test.*env', cl))
    has_monitoring = bool(re.search(r'monitor|閾值|threshold|5%|alert', cl))
    has_change_mgmt = bool(re.search(r'change.?approv|change.?management|變更審核|change.?control', cl))
    prevention_count = sum([has_staging, has_monitoring, has_change_mgmt])
    scores["prevention_measures_evaluated"] = 1.0 if prevention_count >= 3 else (0.5 if prevention_count >= 2 else 0.0)

    # 9. cross_format_evidence_cited — direct quotes from both files
    has_log_quote = bool(re.search(r'(config_change|alert|critical|warn|error).*\[.*\]|`.*log.*`|".*admin-alice|".*dns-monitor', cl))
    has_doc_quote = bool(re.search(r'nt\$|2,400,000|847|290,909|8\.25|staging.*dns|dns.*staging', cl))
    scores["cross_format_evidence_cited"] = 1.0 if (has_log_quote and has_doc_quote) else (0.5 if (has_log_quote or has_doc_quote) else 0.0)

    # 10. all_sections_present — 5 required sections
    required_sections = [
        r'##.*事故時間軸|##.*時間軸',
        r'##.*根本原因鏈|##.*root.?cause',
        r'##.*財務.*驗證|##.*財務損失',
        r'##.*預防措施',
        r'##.*改善建議|##.*建議',
    ]
    section_count = sum(1 for pat in required_sections if re.search(pat, cl))
    scores["all_sections_present"] = 1.0 if section_count >= 5 else (0.5 if section_count >= 3 else 0.0)

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

### Criterion 1: 根本原因鏈重建準確度 (Weight: 35%)
**Score 1.0**: 完整重建從 09:15 DNS 變更 → 09:16 延遲 → 09:17 第一個 ERROR（api-gateway SERVFAIL）→ 09:20 Circuit Breaker OPEN 的完整因果鏈，並引用具體 LOG 條目
**Score 0.75**: 識別了主要 DNS 變更事件和影響，但遺漏了 Circuit Breaker 或第一個 ERROR 服務的具體識別
**Score 0.5**: 識別了 DNS 變更是根本原因，但缺乏詳細的因果鏈或時間序列
**Score 0.25**: 只是泛泛提到 DNS 問題，沒有從 LOG 提取具體事件
**Score 0.0**: 未識別根本原因或完全錯誤

### Criterion 2: 跨格式交叉驗證品質 (Weight: 30%)
**Score 1.0**: 明確展示 DOCX 時間軸與 LOG 事件的對照，兩個文件都有直接引用，包含至少6個時間點
**Score 0.75**: 有交叉驗證但不完整，缺少部分時間點或只引用了一個文件
**Score 0.5**: 提到了兩個文件但沒有系統性的交叉對照
**Score 0.25**: 只讀了一個文件進行分析
**Score 0.0**: 沒有跨格式分析

### Criterion 3: 財務計算驗證 (Weight: 20%)
**Score 1.0**: 正確計算 8.25 × 290,909 = 2,399,999.25，說明精確值與四捨五入的差異（NT$0.75）
**Score 0.75**: 正確識別 8.25 小時和 290,909 的數字，計算結果接近正確
**Score 0.5**: 引用了 NT$2,400,000 但沒有進行實際計算驗證
**Score 0.25**: 提到財務損失但數字不正確
**Score 0.0**: 未進行財務計算驗證

### Criterion 4: 報告結構與改善建議品質 (Weight: 15%)
**Score 1.0**: 全部 5 個章節完整，改善建議具體可執行（包含工具、指令或流程說明）
**Score 0.75**: 4 個章節完整，改善建議有一定具體性
**Score 0.5**: 3 個章節存在，建議較為泛泛
**Score 0.25**: 章節不完整或格式混亂
**Score 0.0**: 輸出為空或格式完全不符

---

## Additional Notes

**測試重點：**
- 跨格式文件分析（DOCX 文字提取 + 結構化日誌解析）
- 從日誌重建時間序列事件鏈
- 數值計算驗證（不是整數的情況）
- 識別「第一個 ERROR」vs「設定變更」的區別

**常見失敗模式：**
- 將 09:15 CONFIG_CHANGE 誤認為是「第一個 ERROR」（應為 09:17 api-gateway ERROR）
- 忽略 DOCX 文件，只從 LOG 分析
- 財務計算停在 2,400,000 而不驗證精確值
- 遺漏 Circuit Breaker 事件（09:20）

**隱藏難點：**
- 根本原因鏈中有「備份在先（09:00），變更在後（09:15）」的正確順序需識別
- SERVFAIL 在多個服務（api-gateway, package-manager, auth-service）幾乎同時出現，第一個是 09:17:01 api-gateway
- 15:00 加入 1.1.1.1 未能完全解決問題，直到 17:30 完整回滾才恢復
