---
id: task_10_multi_fault_triage
name: 多源故障分診與設備風險評分（CSV + JSON + LOG）
category: cross_format_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/csvs/fault_triage_incidents.csv
    dest: fault_triage_incidents.csv
  - source: tw/json/device_registry.json
    dest: device_registry.json
  - source: tw/logs/multi_service_failure.log
    dest: multi_service_failure.log
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---
## Prompt

你是一位網路維運工程師，需要對本週的網路故障工單進行多源分析，找出最需要優先處理的設備，並制定修復計劃。

你有三個檔案：
1. `fault_triage_incidents.csv` — 30 筆故障工單記錄
2. `device_registry.json` — 20 台設備的設備登錄冊
3. `multi_service_failure.log` — 2026-05-20 的系統事件日誌

### 任務要求

**Step 1: 讀取三個檔案**
- 讀取 CSV：ticket_id, reported_time, device_id, fault_type, severity, ip_address, affected_users, estimated_downtime_min, status, resolution_time_min, escalated, repeat_fault
- 讀取 JSON：從 devices 陣列中獲取每台設備的 device_id, hostname, criticality, known_issues, responsible_team
- 讀取 LOG：搜尋關鍵故障傳播事件

**Step 2: JOIN CSV 與 JSON**
將 CSV 中的 device_id 對應到 JSON 中的設備資訊：
- 每張工單加上 hostname（設備名稱）
- 每張工單加上 criticality（嚴重性評分 1-5）
- 每張工單加上 known_issues（已知問題列表）

**Step 3: 計算每台設備的統計指標**

對於每個 device_id，計算：
- `total_tickets`: 該設備的總工單數
- `avg_resolution_time_min`: 已解決工單的平均解決時間（NULL 值排除）
- `escalation_rate`: 工單中 escalated=true 的比例（0.0-1.0）
- `repeat_fault_rate`: 工單中 repeat_fault=true 的比例（0.0-1.0）

**Step 4: 計算複合風險評分**

使用以下公式計算每台設備的風險評分：

```
risk_score = criticality × escalation_rate × repeat_fault_rate
```

其中：
- criticality 來自 device_registry.json（1-5）
- escalation_rate = 已升級工單數 / 總工單數
- repeat_fault_rate = 重複故障工單數 / 總工單數

**Step 5: 識別故障傳播鏈**
從 `multi_service_failure.log` 中找出以下故障傳播事件：
- 10:30 附近：D-003（printer-1st-floor, IP: 192.168.10.150）的 IP 衝突如何導致 D-007（wlan-ap-lobby）的 DNS 失效
- 找到 LOG 中明確說明此傳播關係的條目（關鍵字：FAULT PROPAGATION DETECTED 或類似）

**Step 6: 計算回滾率**

```
rollback_rate = RESOLVED 且 escalated=true 的工單數 / 總 RESOLVED 工單數
```

（在本資料集中，若工單已解決但需要升級，視為需要人工深度介入的高複雜修復）

**Step 7: 輸出報告**

將結果輸出至 `fault_triage_report.md`，必須包含以下章節（按順序）：

```markdown
### 設備風險評分排名
（按 risk_score 降序排列，包含 device_id, hostname, criticality, total_tickets, escalation_rate, repeat_fault_rate, risk_score）

### 故障傳播鏈分析
（D-003 → D-007 的傳播路徑，引用 LOG 中的具體條目）

### 優先修復清單（Top 5 設備）
（風險最高的 5 台設備，含修復理由和建議動作）

### 回滾率與人工介入比例
（回滾率計算結果，分析高複雜度修復的比例）

### 修復指令白名單（dry-run）
（針對 Top 3 設備的具體修復指令，使用 --dry-run 或 echo 模式）
```

---

## Expected Behavior

1. 讀取並解析所有三個檔案
2. 執行 device_id JOIN：
   - D-003 → hostname: printer-1st-floor, criticality: 2
   - D-007 → hostname: wlan-ap-lobby, criticality: 3
   - D-012 → hostname: dev-workstation-5, criticality: 2
3. 計算每台設備指標：
   - D-003（8張工單）: escalation_rate=3/8=0.375, repeat_fault_rate=8/8=1.0
   - D-007（5張工單）: escalation_rate=2/5=0.4, repeat_fault_rate=5/5=1.0
   - D-012（3張工單）: escalation_rate=0/3=0.0, repeat_fault_rate=3/3=1.0
4. 計算 risk_score：
   - D-003: 2 × 0.375 × 1.0 = 0.750
   - D-007: 3 × 0.4 × 1.0 = 1.200（D-007 risk > D-003）
   - D-012: 2 × 0.0 × 1.0 = 0.000（escalation_rate=0，所以得分為0）
5. 從 LOG 找到故障傳播：`FAULT PROPAGATION DETECTED: D-003 IP conflict → ARP instability → Route disruption → D-007 DNS failure`
6. 計算 rollback_rate：
   - RESOLVED 且 escalated=true 的工單：TKT-2026-003, TKT-2026-004, TKT-2026-011, TKT-2026-014, TKT-2026-015, TKT-2026-016, TKT-2026-017 = 7 張（但需核對 status=RESOLVED 且 escalated=true）
   - 從 CSV：RESOLVED 工單共 23 張，其中 escalated=true 的有幾張需從 CSV 計算
7. 輸出完整 `fault_triage_report.md`

**關鍵數字（近似值）：**
- D-007 的 risk_score 最高：約 1.2（優先修復）
- D-003 的 risk_score 次高：約 0.75
- 故障傳播鏈：D-003（IP conflict 192.168.10.150）→ D-007（DNS failure）
- LOG 關鍵時間：10:30 FAULT PROPAGATION DETECTED

---

## Grading Criteria

- [ ] 輸出檔案 fault_triage_report.md 存在
- [ ] 正確 JOIN CSV 和 JSON（設備名稱出現在報告中）
- [ ] D-003 風險評分計算並排名高（大量工單設備）
- [ ] D-007 識別（wlan-ap-lobby, 壞 DNS 192.168.1.253）
- [ ] 故障傳播鏈：D-003 → D-007 關聯被找到
- [ ] 平均解決時間計算（avg_resolution_time_min）
- [ ] Escalation rate 計算
- [ ] Rollback rate 計算
- [ ] Top 5 優先修復清單存在
- [ ] 修復指令以 dry-run 模式列出
- [ ] LOG 中的事件被引用
- [ ] 全部 5 個章節存在

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    SCORE_KEYS = [
        "file_exists",
        "joins_csv_and_json",
        "device_d003_risk_score_high",
        "device_d007_identified",
        "fault_propagation_chain_found",
        "resolution_time_calculated",
        "escalation_rate_computed",
        "rollback_rate_computed",
        "top5_priority_list_present",
        "dryrun_commands_present",
        "log_evidence_cited",
        "all_sections_present",
    ]

    workspace = Path(workspace_path)
    report_path = workspace / "fault_triage_report.md"
    for alt in ["fault_triage_report.md", "triage_report.md", "fault_report.md", "network_report.md"]:
        if not report_path.exists() and (workspace / alt).exists():
            report_path = workspace / alt
    if not report_path.exists():
        return {k: 0.0 for k in SCORE_KEYS}

    content = report_path.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()

    scores = {}

    # 1. file_exists
    scores["file_exists"] = 1.0

    # 2. joins_csv_and_json — device names from registry appear in report
    has_printer = bool(re.search(r'printer.?1st.?floor|printer-1st|印表機|1st.*floor.*printer', cl))
    has_wlan = bool(re.search(r'wlan.?ap.?lobby|lobby.*ap|大廳.*ap', cl))
    has_dev_ws = bool(re.search(r'dev.?workstation.?5|dev-workstation|工作站.*5', cl))
    join_count = sum([has_printer, has_wlan, has_dev_ws])
    scores["joins_csv_and_json"] = 1.0 if join_count >= 3 else (0.5 if join_count >= 2 else 0.0)

    # 3. device_d003_risk_score_high — D-003 should rank among top devices
    has_d003 = bool(re.search(r'D-003|d-003', content))
    d003_prominent = bool(re.search(r'(?:D-003|printer.?1st).*(?:high|highest|top|優先|最高|風險|risk)|(?:most.?ticket|最多.*工單)', cl))
    scores["device_d003_risk_score_high"] = 1.0 if (has_d003 and d003_prominent) else (0.5 if has_d003 else 0.0)

    # 4. device_d007_identified — wlan-ap-lobby with bad DNS
    has_d007 = bool(re.search(r'D-007|wlan.?ap.?lobby', cl))
    has_bad_dns = bool(re.search(r'192\.168\.1\.253|bad.*dns|dns.*resolver.*wrong|錯誤.*dns|dns.*錯誤', cl))
    scores["device_d007_identified"] = 1.0 if (has_d007 and has_bad_dns) else (0.5 if has_d007 else 0.0)

    # 5. fault_propagation_chain_found — D-003 → D-007
    has_prop = bool(re.search(r'd-003.*d-007|d003.*d007|printer.*lobby|ip.?conflict.*dns|arp.*dns.*failure|傳播|propagat', cl))
    has_10_30 = bool(re.search(r'10:30', content))
    scores["fault_propagation_chain_found"] = 1.0 if has_prop else (0.5 if has_10_30 else 0.0)

    # 6. resolution_time_calculated — avg resolution time mentioned
    has_avg_res = bool(re.search(r'avg.*resolution|average.*resolution|平均.*解決|解決.*平均|avg_resolution|resolution.*avg', cl))
    has_res_number = bool(re.search(r'\d+\.?\d*\s*(?:min|分鐘|minutes?)', cl))
    scores["resolution_time_calculated"] = 1.0 if (has_avg_res and has_res_number) else (0.5 if has_res_number else 0.0)

    # 7. escalation_rate_computed
    has_esc_rate = bool(re.search(r'escalation.?rate|升級.*率|升級率|escalat.*%|esc.*rate', cl))
    has_esc_decimal = bool(re.search(r'0\.[0-9]{1,4}|[0-9]+%.*escal|escal.*[0-9]+%', cl))
    scores["escalation_rate_computed"] = 1.0 if (has_esc_rate and has_esc_decimal) else (0.5 if has_esc_rate else 0.0)

    # 8. rollback_rate_computed
    has_rollback = bool(re.search(r'rollback.?rate|回滾.*率|回滾率|rollback.*%|human.*intervention|人工介入', cl))
    has_rb_number = bool(re.search(r'rollback.*[0-9]|[0-9].*rollback|回滾.*[0-9]|[0-9].*回滾', cl))
    scores["rollback_rate_computed"] = 1.0 if (has_rollback and has_rb_number) else (0.5 if has_rollback else 0.0)

    # 9. top5_priority_list_present
    has_top5 = bool(re.search(r'top.?5|前5|優先.*5|top five|5.*設備|5 devices', cl))
    has_priority = bool(re.search(r'優先修復|priority.*fix|fix.*priority|修復.*清單', cl))
    scores["top5_priority_list_present"] = 1.0 if (has_top5 or has_priority) else 0.0

    # 10. dryrun_commands_present
    has_dryrun = bool(re.search(r'dry.?run|--dry-run|echo.*sudo|sudo.*echo|#.*dry|dry run', cl))
    has_cmds = bool(re.search(r'(?:sudo|ip |iptables|systemctl|dhcp|resolv).*(?:dry|echo|#\s*would)', cl))
    has_cmd_block = bool(re.search(r'bash|shell|sh\b', content))
    scores["dryrun_commands_present"] = 1.0 if (has_dryrun or has_cmds) else (0.5 if has_cmd_block else 0.0)

    # 11. log_evidence_cited — quotes from multi_service_failure.log
    has_log_ref = bool(re.search(r'multi_service_failure|fault_propagation|arp.?conflict.*192\.168|wlan-ap-lobby.*dns', cl))
    has_log_timestamp = bool(re.search(r'2026-05-20 \d{2}:\d{2}', content))
    scores["log_evidence_cited"] = 1.0 if (has_log_ref or has_log_timestamp) else 0.0

    # 12. all_sections_present — 5 required sections
    required_sections = [
        r'##.*設備風險評分|##.*risk.?score',
        r'##.*故障傳播鏈|##.*fault.?propagat',
        r'##.*優先修復|##.*top.?5|##.*priority',
        r'##.*回滾率|##.*rollback',
        r'##.*修復指令|##.*dry.?run|##.*command',
    ]
    section_count = sum(1 for p in required_sections if re.search(p, cl))
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

### Criterion 1: 跨格式資料整合品質 (Weight: 35%)
**Score 1.0**: 正確執行 CSV-JSON JOIN，每台設備的工單統計準確（D-003 有 8 張、D-007 有 5 張），risk_score 公式應用正確（D-007 風險最高，約 1.2）
**Score 0.75**: JOIN 正確，工單統計接近正確，risk_score 計算有小誤差
**Score 0.5**: 識別了主要設備，但統計數字有明顯誤差
**Score 0.25**: 讀取了多個文件但沒有正確 JOIN 或計算
**Score 0.0**: 只讀取了一個文件或輸出為空

### Criterion 2: 故障傳播鏈識別 (Weight: 30%)
**Score 1.0**: 從 LOG 正確識別 10:30 D-003 IP 衝突（192.168.10.150）觸發 D-007 DNS 失敗的傳播鏈，引用 LOG 中的「FAULT PROPAGATION DETECTED」條目
**Score 0.75**: 識別了 D-003 和 D-007 的關聯，但未引用 LOG 中的具體事件
**Score 0.5**: 從 CSV 的 known_issues 知道 D-003 有 IP conflict，D-007 有壞 DNS，但未用 LOG 驗證傳播
**Score 0.25**: 只提到設備各自的問題，沒有識別傳播關係
**Score 0.0**: 未識別任何故障傳播

### Criterion 3: 統計計算完整性 (Weight: 20%)
**Score 1.0**: 正確計算 avg_resolution_time（排除 NULL），escalation_rate，repeat_fault_rate 和 rollback_rate（RESOLVED 且 escalated=true 的比例）
**Score 0.75**: 計算了大部分指標，rollback_rate 有小誤差
**Score 0.5**: 計算了 2-3 個指標，有部分正確
**Score 0.25**: 只計算了 total_tickets，其他指標缺失
**Score 0.0**: 未計算任何統計指標

### Criterion 4: 修復指令與優先清單實用性 (Weight: 15%)
**Score 1.0**: Top 5 優先設備清單合理（含 D-007 和 D-003），dry-run 指令針對具體問題（D-003 修 DHCP 衝突、D-007 修 DNS resolver）
**Score 0.75**: 清單合理但 dry-run 指令較通用，不夠針對具體問題
**Score 0.5**: 有優先清單和指令，但沒有 dry-run 安全機制
**Score 0.25**: 有清單但沒有修復指令
**Score 0.0**: 沒有優先清單或修復指令

---

## Additional Notes

**測試重點：**
- 三格式資料整合：CSV + JSON + LOG
- 關聯查詢（類似 SQL JOIN）
- 複合公式計算（risk_score）
- 從非結構化 LOG 識別結構化事件

**關鍵計算細節：**
- D-003 escalation_rate = 3/8 = 0.375（TKT-003, TKT-004, TKT-006, TKT-007 中 escalated=true 的是 TKT-003, TKT-004, TKT-006, TKT-007 — 需從 CSV 精確計算）
- D-007 risk_score = 3 × 0.4 × 1.0 = 1.2（應高於 D-003 的 0.75）
- avg_resolution_time 必須排除 resolution_time_min 為空的工單（status=OPEN/IN_PROGRESS/ESCALATED）
- rollback_rate 定義：RESOLVED 且 escalated=true 的比例（而非所有 escalated=true）

**常見失敗模式：**
- 不做 JSON lookup，只用 CSV 計算
- 未從 LOG 找到傳播鏈（只用 CSV/JSON 的 known_issues 推斷）
- avg_resolution_time 計入了 NULL 值（應排除）
- rollback_rate 分母用錯（應為 RESOLVED 總數，不是所有工單）
- dry-run 指令不針對具體故障類型（DNS/DHCP）

**設備優先級的正確答案：**
根據 risk_score = criticality × escalation_rate × repeat_fault_rate：
- D-007 (wlan-ap-lobby): 3 × 0.4 × 1.0 ≈ 1.20 → 最高
- D-003 (printer-1st-floor): 2 × 0.375 × 1.0 ≈ 0.75 → 次高
- D-001/D-002 等設備若有工單且 criticality 高，可能排第3-5

此為 🔴 Hard 任務，需要三格式 JOIN 和複合指標計算，是本 benchmark batch 中最複雜的任務。
