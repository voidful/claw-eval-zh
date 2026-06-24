---
id: task_wifi_password_reset_plan
name: Wi-Fi 密碼安全稽核：識別違規 SSID 並產生重設計畫
category: json_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/json/wifi_config.json
    dest: wifi_config.json
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---
## Prompt

你是一位企業網路安全工程師，需要稽核公司 Wi-Fi 設定的安全性。

請讀取工作目錄中的 `wifi_config.json`，執行以下分析並輸出 `wifi_security_report.md`：

1. **讀取密碼原則（password_policy）**：
   - `min_length`: 密碼最短長度
   - `require_special`: 必須包含特殊字元（非英數字）
   - `no_ssid_fragment`: 密碼不可包含 SSID 名稱的任何片段（大小寫不敏感）
   - `max_age_days`: 密碼最大有效天數

2. **針對每個 SSID 檢查下列項目**：
   - 加密方式是否安全（WEP → 🔴 Critical；WPA2 → 可接受；WPA3 → 最佳）
   - 密碼長度是否符合 `min_length`
   - 密碼是否包含特殊字元（若 `require_special=true`）
   - 密碼是否包含 SSID 名稱片段（若 `no_ssid_fragment=true`）
   - 密碼最後更改時間 vs 今日（2026-05-20），若超過 `max_age_days` 天 → 需輪換

3. **產生優先重設清單**（依風險高低排序）：
   - 🔴 Critical：WEP 加密
   - 🔴 High：密碼含 SSID 片段
   - 🟡 Medium：缺少特殊字元或長度不足
   - 🟢 Low：密碼過期但符合其他規則

4. **產生 dry-run 修改指令**（使用 `wpa_cli` 或 `nmcli` 語法，不要真的執行）

輸出報告 `wifi_security_report.md`，須包含：
- `## 摘要`（發現問題數量、整體風險等級）
- `## SSID 安全狀態表`（每個 SSID 的各項檢查結果）
- `## 違規問題清單`（含問題描述、風險等級）
- `## 優先重設順序`（依風險排序，說明理由）
- `## 修改指令白名單（dry-run）`（wpa_cli 或 nmcli 指令）

## Expected Behavior

1. Parse wifi_config.json, read password_policy and ssids array
2. Check Corp-Legacy: WEP encryption → Critical risk
3. Check Corp-Main: password "Corp123!" contains "Corp" (SSID fragment) → High risk; also length=8 < min_length=12
4. Check Corp-Guest: password "Guest2024" has no special character → Medium risk; length=9 < min_length=12
5. Check password ages relative to 2026-05-20 and max_age_days=180 (cutoff: 2025-11-21)
6. Corp-IoT and Corp-Executive should pass all checks
7. Priority order: Corp-Legacy (WEP) > Corp-Main (SSID fragment) > Corp-Guest (no special char)
8. Provide nmcli or wpa_cli dry-run commands for flagged SSIDs

Key expected findings:
- Corp-Legacy: Critical (WEP)
- Corp-Main: High (SSID fragment "Corp" in password "Corp123!", length violation)
- Corp-Guest: Medium (no special char, length violation)
- Corp-IoT: password age check (last_changed 2026-03-10, ~71 days, OK)
- Corp-Executive: Compliant

## Grading Criteria

- [ ] Output file wifi_security_report.md exists
- [ ] Identifies Corp-Legacy WEP as Critical risk
- [ ] Identifies Corp-Guest as having weak password (no special char)
- [ ] Identifies Corp-Main password contains SSID fragment
- [ ] Correct priority order (WEP > SSID fragment > no-special)
- [ ] Dry-run commands present (wpa_cli or nmcli mentioned)
- [ ] Does NOT claim to have executed any commands
- [ ] Password policy referenced in report
- [ ] Risk levels present (Critical/High/Medium or 嚴重/高/中)
- [ ] All 5 required sections present

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    SCORE_KEYS = [
        "file_exists","identifies_corp_legacy_wep","identifies_corp_guest_weak",
        "identifies_corp_main_ssid_fragment","correct_priority_order",
        "has_dryrun_commands","no_execution_claimed",
        "password_policy_referenced","risk_levels_present","all_sections_present"
    ]
    workspace = Path(workspace_path)
    report_path = workspace / "wifi_security_report.md"
    for alt in ["wifi_report.md","security_report.md","report.md"]:
        if not report_path.exists() and (workspace / alt).exists():
            report_path = workspace / alt
    if not report_path.exists():
        return {k: 0.0 for k in SCORE_KEYS}
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    scores = {}
    scores["file_exists"] = 1.0
    scores["identifies_corp_legacy_wep"] = 1.0 if re.search(r'Corp.Legacy', content, re.IGNORECASE) and re.search(r'WEP', content) and re.search(r'Critical|嚴重|🔴', content) else 0.5 if re.search(r'WEP', content) and re.search(r'Critical|嚴重', content, re.IGNORECASE) else 0.0
    scores["identifies_corp_guest_weak"] = 1.0 if re.search(r'Corp.Guest', content, re.IGNORECASE) and re.search(r'special|特殊|weak|弱|長度|length', content, re.IGNORECASE) else 0.5 if re.search(r'Guest2024', content) else 0.0
    scores["identifies_corp_main_ssid_fragment"] = 1.0 if re.search(r'Corp.Main', content, re.IGNORECASE) and re.search(r'SSID.*fragment|ssid.*片段|包含.*SSID|Corp123', content, re.IGNORECASE) else 0.5 if re.search(r'Corp123', content) and re.search(r'問題|violation|違規', content, re.IGNORECASE) else 0.0
    legacy_pos = content.find("Corp-Legacy") if "Corp-Legacy" in content else content.lower().find("wep")
    main_pos = content.find("Corp-Main") if "Corp-Main" in content else -1
    guest_pos = content.find("Corp-Guest") if "Corp-Guest" in content else -1
    if legacy_pos != -1 and main_pos != -1 and guest_pos != -1:
        priority_section = re.search(r'優先|priority|順序|order', content, re.IGNORECASE)
        scores["correct_priority_order"] = 1.0 if priority_section and legacy_pos < main_pos else 0.5
    else:
        scores["correct_priority_order"] = 0.0
    scores["has_dryrun_commands"] = 1.0 if re.search(r'nmcli|wpa_cli|wpa_passphrase', content) else 0.5 if re.search(r'dry.?run|指令白名單|command.*whitelist', content, re.IGNORECASE) else 0.0
    executed_keywords = re.findall(r'已執行|執行完成|已修改|已更新|已套用|已變更', content)
    scores["no_execution_claimed"] = 1.0 if len(executed_keywords) == 0 else 0.0
    scores["password_policy_referenced"] = 1.0 if re.search(r'password.policy|密碼原則|min.length|require.special|no.ssid', content, re.IGNORECASE) else 0.5 if re.search(r'原則|policy|12.*char|特殊字元', content, re.IGNORECASE) else 0.0
    scores["risk_levels_present"] = 1.0 if re.search(r'Critical|嚴重', content, re.IGNORECASE) and re.search(r'Medium|中|Warning|警告|High|高', content, re.IGNORECASE) else 0.5 if re.search(r'Critical|嚴重|🔴', content) else 0.0
    required_sections = ['摘要|summary', 'SSID.*狀態|SSID.*table|SSID.*安全', '違規|問題清單|issue', '優先|priority|順序', '指令|command|dry.?run']
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

### Criterion 1: 安全問題識別準確性 (Weight: 35%)
**Score 1.0**: 正確識別所有 3 個問題 SSID（Corp-Legacy WEP、Corp-Main SSID 片段、Corp-Guest 無特殊字元），未誤報 Corp-IoT 或 Corp-Executive 為問題
**Score 0.75**: 識別 2 個問題，或有輕微誤報
**Score 0.5**: 識別 1 個問題（WEP）但遺漏其他
**Score 0.25**: 僅提到安全問題但未識別具體 SSID
**Score 0.0**: 未發現任何安全問題

### Criterion 2: 優先順序與風險分級 (Weight: 30%)
**Score 1.0**: 優先順序正確（WEP Critical > SSID 片段 High > 無特殊字元 Medium），各風險等級說明清楚，引用密碼原則條文
**Score 0.75**: 優先順序大致正確但風險等級有小誤
**Score 0.5**: 有優先順序但依據不清楚
**Score 0.25**: 僅列出問題清單，無優先順序
**Score 0.0**: 無風險分級

### Criterion 3: 修改指令品質 (Weight: 20%)
**Score 1.0**: 提供 nmcli 或 wpa_cli 語法的具體 dry-run 指令，對應各問題 SSID，有 dry-run 標記
**Score 0.75**: 指令格式基本正確但不完整
**Score 0.5**: 有提及指令但語法不正確
**Score 0.25**: 只說明需要修改，無具體指令
**Score 0.0**: 無指令

### Criterion 4: 報告完整性 (Weight: 15%)
**Score 1.0**: 5 個章節齊全，SSID 狀態表清晰，密碼原則有引用
**Score 0.75**: 缺少 1 個章節
**Score 0.5**: 缺少 2 個章節
**Score 0.0**: 無結構化報告

## Additional Notes

Tests: JSON parsing, password policy enforcement, multi-criteria security evaluation, priority ranking.
Key trap: Corp-IoT and Corp-Executive are compliant — do not flag them.
Age calculation: last_audit is 2026-01-15, but check vs 2026-05-20 with max_age_days=180 (cutoff 2025-11-21).
Corp-Legacy last_changed 2023-06-01 → also extremely overdue for rotation.
