---
id: task_dhcp_config_audit
name: DHCP 設定稽核：識別 IP 衝突與設定矛盾
category: txt_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/txt/dhcp_server_config.txt
    dest: dhcp_server_config.txt
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---
## Prompt

你是一位網路管理員，需要稽核 DHCP 伺服器設定檔，找出潛在問題。

請讀取工作目錄中的 `dhcp_server_config.txt`（ISC DHCP 格式設定檔），執行以下分析並輸出 `dhcp_audit_report.md`：

1. **列出所有子網路（subnet）的 Pool 範圍**（起始 IP ～ 結束 IP）
2. **檢查每個靜態保留（host reservation）的 IP 是否落在 Pool 範圍內**
   - 判斷公式：若 `reserved_ip >= pool_start AND reserved_ip <= pool_end` → 衝突
3. **識別 lease-time 矛盾**：若 `default-lease-time > max-lease-time` → 標記為設定錯誤
4. **列出所有問題的嚴重等級**：
   - 🔴 嚴重（Critical）：IP 衝突可能導致設備無法連線
   - 🟡 警告（Warning）：設定矛盾但不立即斷線
5. **提供修復建議**（dry-run，列出應修改的設定行）

輸出報告 `dhcp_audit_report.md`，須包含：
- `## 子網路 Pool 清單`
- `## 靜態保留衝突清單`（表格：主機名、保留IP、衝突Pool範圍、嚴重等級）
- `## Lease-Time 矛盾`
- `## 修復建議（dry-run）`
- `## 風險摘要`

## Expected Behavior

1. Read dhcp_server_config.txt
2. Parse subnet declarations and pool ranges
3. Parse host reservation IP addresses
4. Check each host IP against pool ranges
5. Identify: printer-1st-floor (192.168.10.150) conflicts with 192.168.10.100-200
6. Identify: server-backup (192.168.20.100) conflicts with 192.168.20.50-150
7. Identify: default-lease-time 86400 > max-lease-time 3600 = inconsistency
8. Write structured report

Key expected findings:
- 2 IP conflicts (Critical)
- 1 lease-time inconsistency (Warning)
- office-gateway 192.168.10.1 should NOT be flagged as conflict

## Grading Criteria

- [ ] Output dhcp_audit_report.md exists
- [ ] Identifies printer-1st-floor as IP conflict
- [ ] Identifies server-backup as IP conflict
- [ ] Does NOT flag office-gateway as conflict
- [ ] Identifies lease-time inconsistency (86400 > 3600)
- [ ] Conflict severity marked as Critical/嚴重
- [ ] Lease inconsistency severity marked as Warning/警告
- [ ] Dry-run fix suggestions present
- [ ] All 5 required sections present
- [ ] Pool ranges correctly listed for both subnets

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    SCORE_KEYS = [
        "file_exists","identifies_printer_conflict","identifies_server_conflict",
        "no_false_gateway_conflict","identifies_lease_inconsistency",
        "critical_severity_used","warning_severity_used",
        "has_dryrun_fixes","all_sections_present","pool_ranges_listed"
    ]
    workspace = Path(workspace_path)
    report_path = workspace / "dhcp_audit_report.md"
    for alt in ["dhcp_report.md","audit_report.md","report.md"]:
        if not report_path.exists() and (workspace / alt).exists():
            report_path = workspace / alt
    if not report_path.exists():
        return {k: 0.0 for k in SCORE_KEYS}
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    scores = {}
    scores["file_exists"] = 1.0
    scores["identifies_printer_conflict"] = 1.0 if re.search(r'printer.1st.floor|printer.*floor|192\.168\.10\.150', content, re.IGNORECASE) and re.search(r'衝突|conflict|問題|conflict', content, re.IGNORECASE) else 0.0
    scores["identifies_server_conflict"] = 1.0 if re.search(r'server.backup|192\.168\.20\.100', content, re.IGNORECASE) and re.search(r'衝突|conflict', content, re.IGNORECASE) else 0.0
    gateway_conflict = re.search(r'office.gateway.*衝突|office.gateway.*conflict|192\.168\.10\.1[^0-9].*衝突', content, re.IGNORECASE)
    scores["no_false_gateway_conflict"] = 0.0 if gateway_conflict else 1.0
    scores["identifies_lease_inconsistency"] = 1.0 if re.search(r'86400.*3600|lease.*time.*矛盾|lease.*inconsisten|default.*max.*lease', content, re.IGNORECASE) else 0.5 if re.search(r'lease.time|租約時間', content, re.IGNORECASE) else 0.0
    scores["critical_severity_used"] = 1.0 if re.search(r'Critical|嚴重|🔴', content) else 0.0
    scores["warning_severity_used"] = 1.0 if re.search(r'Warning|警告|🟡', content) else 0.0
    scores["has_dryrun_fixes"] = 1.0 if re.search(r'dry.?run|修復建議|建議.*修改|fixed.*config', content, re.IGNORECASE) else 0.0
    required_sections = ['子網路|subnet|Pool', '靜態保留|衝突|conflict', 'lease|租約', '修復|fix|建議', '風險|risk|摘要']
    found = sum(1 for s in required_sections if re.search(s, content, re.IGNORECASE))
    scores["all_sections_present"] = 1.0 if found >= 5 else (0.5 if found >= 3 else 0.0)
    pool_ranges = bool(re.search(r'192\.168\.10\.100.*192\.168\.10\.200', content)) and bool(re.search(r'192\.168\.20\.50.*192\.168\.20\.150', content))
    scores["pool_ranges_listed"] = 1.0 if pool_ranges else 0.5 if re.search(r'192\.168\.10\.\d+|192\.168\.20\.\d+', content) else 0.0
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

### Criterion 1: 衝突識別準確性 (Weight: 40%)
**Score 1.0**: 正確找出所有 2 個 IP 衝突（printer-1st-floor + server-backup），未誤報 office-gateway，衝突範圍計算正確
**Score 0.75**: 找出 1 個衝突，或有輕微誤報
**Score 0.5**: 提到 IP 衝突問題但未識別具體主機
**Score 0.25**: 僅提到 DHCP 設定有問題
**Score 0.0**: 未發現任何衝突

### Criterion 2: 設定矛盾識別 (Weight: 25%)
**Score 1.0**: 正確識別 default-lease-time 86400 > max-lease-time 3600 的矛盾，說明影響（DHCP 伺服器可能拒絕請求或行為異常）
**Score 0.75**: 識別矛盾但說明不完整
**Score 0.5**: 提到 lease-time 但未指出矛盾關係
**Score 0.0**: 未識別 lease-time 問題

### Criterion 3: 修復建議品質 (Weight: 20%)
**Score 1.0**: 提供具體修復行（如將 host 的 fixed-address 改到 pool 外、調整 max-lease-time），有 dry-run 標記
**Score 0.75**: 修復方向正確但缺少具體設定行
**Score 0.5**: 建議模糊
**Score 0.0**: 無修復建議

### Criterion 4: 報告完整性與格式 (Weight: 15%)
**Score 1.0**: 5 個章節齊全，有嚴重等級分類，表格格式清晰
**Score 0.75**: 缺少 1 個章節
**Score 0.5**: 缺少 2 個章節或格式混亂
**Score 0.0**: 無結構化報告

## Additional Notes

Tests: DHCP config parsing, IP range comparison, lease-time logic validation.
Key trap: office-gateway at 192.168.10.1 is outside pool range 100-200, should NOT be flagged.
Common failure: confusing /24 subnet with pool range; treating all static hosts as conflicts.
