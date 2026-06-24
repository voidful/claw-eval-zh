---
id: task_network_interface_state
name: 網路介面狀態檢查：識別 IP 衝突、缺失閘道與異常
category: csv_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/csvs/network_interfaces.csv
    dest: network_interfaces.csv
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---
## Prompt

你是一位 Linux 系統工程師，需要審查伺服器的網路介面狀態，找出配置異常與潛在問題。

請讀取工作目錄中的 `network_interfaces.csv`，欄位說明如下：
- `interface_name`: 介面名稱
- `status`: UP / DOWN
- `ip_address`: 分配的 IP 地址
- `netmask`: 子網路遮罩
- `gateway`: 預設閘道
- `dns_primary` / `dns_secondary`: DNS 伺服器
- `mac_address`: MAC 位址
- `speed_mbps`: 連線速度
- `errors_in` / `errors_out`: 輸入/輸出錯誤計數
- `last_seen`: 最後活躍時間（ISO 格式）
- `notes`: 備註

執行以下 **5 項檢查** 並輸出 `network_interface_report.md`：

1. **重複 IP 檢查**：找出多個介面共用同一 IP 地址（排除 0.0.0.0 和 127.0.0.1）
2. **缺失閘道檢查**：找出狀態為 UP 且 gateway 為 0.0.0.0 或空值的介面（排除 lo 和 docker/veth 等虛擬介面）
3. **已知問題 DNS 檢查**：找出 dns_primary 或 dns_secondary 為 `192.168.1.253` 的介面（已知故障解析器）
4. **高錯誤率檢查**：找出 errors_in 或 errors_out **超過 1000** 的介面
5. **無效 IP 格式檢查**：找出 IP 地址格式不合法（每個 octet 應為 0-255）的介面

對每個發現的問題，列出：
- 介面名稱
- 問題類型
- 嚴重等級（Critical / Warning / Info）
- 建議動作（dry-run，不要真的執行）

輸出 `network_interface_report.md`，須包含：
- `## 摘要`（發現問題數、受影響介面數）
- `## 重複 IP 清單`
- `## 缺失閘道介面`
- `## 問題 DNS 介面`
- `## 高錯誤率介面`
- `## 建議修復動作（dry-run）`

## Expected Behavior

1. Read network_interfaces.csv, parse all rows
2. Find duplicate IPs: eth0 and eth1 both have 192.168.1.100
3. Find missing gateway: wlan1 is UP with gateway=0.0.0.0
4. Find bad DNS: wlan0 uses dns_primary=192.168.1.253 (known problem resolver from dns_query.log context)
5. Find high errors: bond0 has errors_in=15420 (threshold: >1000)
6. Find invalid IP: eth3 has ip_address=192.168.300.1 (octet 300 > 255)
7. Write structured report with severity levels and dry-run recommendations

Key expected findings:
- Duplicate IP: eth0 & eth1 (192.168.1.100) → Critical
- Missing gateway: wlan1 (gateway=0.0.0.0, but UP) → Warning
- Bad DNS: wlan0 (dns_primary=192.168.1.253) → Warning
- High errors: bond0 (errors_in=15420) → Warning
- Invalid IP: eth3 (192.168.300.1) → Warning

## Grading Criteria

- [ ] Output file network_interface_report.md exists
- [ ] Finds duplicate IP (eth0 and eth1 both 192.168.1.100)
- [ ] Finds missing gateway (wlan1 UP but gateway=0.0.0.0)
- [ ] Finds bad DNS resolver (wlan0 dns=192.168.1.253)
- [ ] Finds high error count (bond0 errors_in=15420 > 1000)
- [ ] Severity levels present (Critical/Warning or 嚴重/警告)
- [ ] Has recommended actions (dry-run)
- [ ] Does NOT claim to have executed any commands
- [ ] At least 4 distinct issue types identified
- [ ] All required sections present

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    SCORE_KEYS = [
        "file_exists","finds_duplicate_ip","finds_missing_gateway",
        "finds_bad_dns","finds_high_errors",
        "severity_levels_present","has_recommended_actions",
        "no_execution_claimed","all_issues_count_correct","all_sections_present"
    ]
    workspace = Path(workspace_path)
    report_path = workspace / "network_interface_report.md"
    for alt in ["interface_report.md","network_report.md","report.md"]:
        if not report_path.exists() and (workspace / alt).exists():
            report_path = workspace / alt
    if not report_path.exists():
        return {k: 0.0 for k in SCORE_KEYS}
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    scores = {}
    scores["file_exists"] = 1.0
    dup_ip = re.search(r'192\.168\.1\.100', content) and (
        re.search(r'eth0.*eth1|eth1.*eth0|duplicate|重複|衝突', content, re.IGNORECASE) or
        (content.count("192.168.1.100") >= 2)
    )
    scores["finds_duplicate_ip"] = 1.0 if dup_ip else 0.5 if re.search(r'duplicate.*IP|IP.*重複|IP.*衝突', content, re.IGNORECASE) else 0.0
    scores["finds_missing_gateway"] = 1.0 if re.search(r'wlan1', content) and re.search(r'gateway|閘道|0\.0\.0\.0', content, re.IGNORECASE) else 0.5 if re.search(r'missing.*gateway|缺.*閘道|gateway.*missing', content, re.IGNORECASE) else 0.0
    scores["finds_bad_dns"] = 1.0 if re.search(r'192\.168\.1\.253', content) and re.search(r'wlan0|dns.*問題|bad.*dns|問題.*dns', content, re.IGNORECASE) else 0.5 if re.search(r'192\.168\.1\.253', content) else 0.0
    scores["finds_high_errors"] = 1.0 if re.search(r'bond0', content) and re.search(r'15420|error.*high|高.*錯誤|errors.*1[0-9]{3,}', content, re.IGNORECASE) else 0.5 if re.search(r'bond0.*error|error.*bond0', content, re.IGNORECASE) else 0.0
    scores["severity_levels_present"] = 1.0 if re.search(r'Critical|嚴重', content, re.IGNORECASE) and re.search(r'Warning|警告', content, re.IGNORECASE) else 0.5 if re.search(r'Critical|Warning|嚴重|警告', content, re.IGNORECASE) else 0.0
    scores["has_recommended_actions"] = 1.0 if re.search(r'建議|recommend|action|修復|fix|ip.*addr|ifconfig|nmcli', content, re.IGNORECASE) else 0.0
    executed_keywords = re.findall(r'已執行|執行完成|已修改|已更新|已套用|已變更', content)
    scores["no_execution_claimed"] = 1.0 if len(executed_keywords) == 0 else 0.0
    issue_types = [
        bool(re.search(r'duplicate.*ip|ip.*重複|ip.*衝突|192\.168\.1\.100', content, re.IGNORECASE)),
        bool(re.search(r'missing.*gateway|gateway.*missing|缺.*閘道|wlan1.*0\.0\.0\.0', content, re.IGNORECASE)),
        bool(re.search(r'192\.168\.1\.253|bad.*dns|問題.*dns', content, re.IGNORECASE)),
        bool(re.search(r'15420|high.*error|error.*high|bond0', content, re.IGNORECASE)),
        bool(re.search(r'invalid.*ip|ip.*invalid|300|格式.*錯誤|eth3', content, re.IGNORECASE)),
    ]
    issue_count = sum(issue_types)
    scores["all_issues_count_correct"] = 1.0 if issue_count >= 4 else (0.5 if issue_count >= 2 else 0.0)
    required_sections = ['摘要|summary', '重複|duplicate', '閘道|gateway', 'DNS|dns', '錯誤|error|建議']
    found = sum(1 for s in required_sections if re.search(s, content, re.IGNORECASE))
    scores["all_sections_present"] = 1.0 if found >= 5 else (0.5 if found >= 3 else 0.0)
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

### Criterion 1: 問題識別完整性 (Weight: 40%)
**Score 1.0**: 正確識別所有 5 個問題（重複IP、缺失閘道、問題DNS、高錯誤率、無效IP格式），各問題的介面名稱正確
**Score 0.75**: 識別 4 個問題
**Score 0.5**: 識別 2-3 個問題
**Score 0.25**: 識別 1 個問題
**Score 0.0**: 未識別任何問題

### Criterion 2: 嚴重等級分類合理性 (Weight: 25%)
**Score 1.0**: 重複 IP 標記為 Critical（可能導致網路中斷），其他問題依影響大小分類為 Warning/Info，分類邏輯清晰
**Score 0.75**: 嚴重等級大致正確但有小誤
**Score 0.5**: 有嚴重等級但分類依據不清
**Score 0.25**: 僅列問題無分級
**Score 0.0**: 無嚴重等級

### Criterion 3: 修復建議品質 (Weight: 20%)
**Score 1.0**: 每個問題都有具體 dry-run 建議指令（ip addr、nmcli、/etc/resolv.conf 等），未宣稱已執行
**Score 0.75**: 大多數問題有建議但個別缺漏
**Score 0.5**: 有一般性建議但無具體指令
**Score 0.0**: 無修復建議

### Criterion 4: 報告結構與可讀性 (Weight: 15%)
**Score 1.0**: 6 個章節齊全，每個問題有介面名稱、問題類型、嚴重等級、建議動作四欄
**Score 0.75**: 缺少 1-2 個章節
**Score 0.5**: 有內容但缺乏結構
**Score 0.0**: 無結構化報告

## Additional Notes

Tests: CSV parsing, IP duplication detection, gateway validation, DNS blacklist check, error threshold alerting.
Key distinction: lo (127.0.0.1) has gateway=0.0.0.0 but is loopback — should NOT be flagged for missing gateway.
docker0 also has gateway=0.0.0.0 — agent may or may not flag virtual bridge interfaces; either is acceptable.
High error threshold: errors_in or errors_out > 1000 (bond0 has 15420).
Invalid IP: octet value > 255 (eth3 has 192.168.300.1).
