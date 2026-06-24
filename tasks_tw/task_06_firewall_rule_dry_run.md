---
id: task_06_firewall_rule_dry_run
name: 防火牆規則稽核與 Dry-Run 修補
category: txt_analysis
grading_type: hybrid
timeout_seconds: 240
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/txt/iptables_rules.txt
    dest: iptables_rules.txt
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---

## Prompt

你是一名資安工程師，需要稽核一份 Linux 伺服器的 iptables 防火牆規則，找出設定漏洞，並提供修補指令（dry-run）。

**輸入檔案：**
- `iptables_rules.txt` — iptables-save 格式的防火牆規則檔案

**任務步驟：**

1. 讀取並解析 `iptables_rules.txt`
2. 逐一檢查 INPUT chain 的每條規則，分類為：
   - ✅ **SECURE** — 規則設定合理，無風險
   - ⚠️ **RISKY** — 存在安全隱患，建議修正
   - 🔴 **CRITICAL** — 嚴重安全漏洞，必須立即修正
3. 識別以下 4 個具體問題並說明風險：
   - Port 3306（MySQL）對外開放（0.0.0.0/0）
   - Port 22（SSH）有重複規則開放給所有來源（0.0.0.0/0）
   - Port 8080（開發伺服器）對外開放（0.0.0.0/0）
   - 存在一條被註解的極危險規則（`-j ACCEPT` 放在 DROP 規則前），若取消註解將允許所有流量
4. 為每個問題提供：規則原文、風險等級、建議修復動作
5. 產生「安全補丁指令清單（Dry-Run）」—— 使用 `iptables -D`（刪除危險規則）和 `iptables -I`（插入修正規則）的方式

**嚴重等級定義：**
- 🔴 **CRITICAL**：未限制來源的 `-j ACCEPT` 全放行規則（即使被註解也需標記）、資料庫 port 對外開放
- ⚠️ **RISKY**：SSH 重複規則、開發 port 對外開放

**輸出要求：** 將分析報告寫入 `firewall_analysis_report.md`，格式包含：

### 規則稽核摘要
列出所有問題規則與分類。

### 問題詳情
4 個問題各自的詳細說明。

### 安全補丁指令（Dry-Run）
`iptables -D` / `iptables -I` 指令清單。

### 風險建議
整體建議。

**重要：** 所有指令標記為 dry-run 供審核，不得宣稱已執行任何變更。

## Expected Behavior

代理人應執行以下步驟：

1. 讀取並解析 `iptables_rules.txt`（iptables-save 格式），逐條走訪 INPUT chain 的規則
2. 比對每條規則的目的地 port 與來源網段（`-s`），辨識來源為 `0.0.0.0/0` 的開放規則
3. 找出 4 個植入的問題：
   - Port 3306（MySQL）對外開放給 `0.0.0.0/0` → CRITICAL
   - Port 22（SSH）有重複規則，其中一條開放給 `0.0.0.0/0` → RISKY
   - Port 8080（開發伺服器）對外開放給 `0.0.0.0/0` → RISKY
   - 被註解的 `-j ACCEPT` 全放行規則（位於 DROP 規則之前）→ CRITICAL
4. 為每個問題標註正確的嚴重等級（CRITICAL / RISKY），並引用規則原文與來源 IP
5. 產生 Dry-Run 修補指令：以 `iptables -D INPUT` 刪除危險規則，並以 `iptables -I INPUT` 插入修正規則（例如將 3306 限制為內網 `10.0.0.0/8`）
6. 將報告寫入 `firewall_analysis_report.md`，包含規則稽核摘要、問題詳情、安全補丁指令（Dry-Run）、風險建議四個段落
7. 明確標示所有指令僅供 dry-run 審核，不得宣稱已實際執行任何變更

Key expected values（近似）：
- 應辨識出全部 4 個問題
- MySQL 3306 與被註解的 ACCEPT 規則 → CRITICAL
- SSH 重複規則與 8080 → RISKY
- 修補建議將 3306 來源限制為 `10.0.0.0/8`

## Grading Criteria

- [ ] 輸出檔案 `firewall_analysis_report.md` 存在
- [ ] 找出 Port 3306（MySQL）對外開放問題（含 0.0.0.0/0 或「對外／公開」說明）
- [ ] 找出 Port 22（SSH）重複規則問題（含重複／覆寫風險說明）
- [ ] 找出 Port 8080（開發伺服器）對外開放問題
- [ ] 找出被註解的 `-j ACCEPT` 全放行危險規則
- [ ] 使用 CRITICAL（嚴重／高危）等嚴重等級分類
- [ ] 提供 Dry-Run 補丁指令（`iptables -D` / `iptables -I`）
- [ ] 不宣稱已執行任何變更（維持 dry-run 性質）
- [ ] 4 個問題全數找出（all_4_issues_found）
- [ ] 包含整體風險建議（建議／限制／修正等）

## Automated Checks

```python
import re
from pathlib import Path

def grade(transcript: list, workspace: str) -> dict:
    base = Path(workspace)
    out = base / "firewall_analysis_report.md"

    if not out.exists():
        return {
            "file_exists": 0.0,
            "finds_mysql_exposure": 0.0,
            "finds_ssh_duplicate": 0.0,
            "finds_dev_port_exposure": 0.0,
            "finds_permissive_accept_rule": 0.0,
            "critical_severity_used": 0.0,
            "has_dry_run_patch": 0.0,
            "no_execution_claimed": 0.0,
            "all_4_issues_found": 0.0,
            "risk_recommendations_present": 0.0,
        }

    text = out.read_text(encoding="utf-8", errors="ignore").lower()

    # 2. finds_mysql_exposure — mention 3306 with 0.0.0.0 or "any" or "world"
    mysql_ok = bool(
        re.search(r"3306", text) and
        (re.search(r"0\.0\.0\.0", text) or re.search(r"(any|world|internet|公開|對外)", text))
    )
    finds_mysql_exposure = 1.0 if mysql_ok else 0.0

    # 3. finds_ssh_duplicate — mention 22 + duplicate/override risk
    ssh_ok = bool(
        re.search(r"\bssh\b|port 22|dport 22", text) and
        re.search(r"(duplicate|重複|override|overrid|0\.0\.0\.0.*22|22.*0\.0\.0\.0)", text)
    )
    finds_ssh_duplicate = 1.0 if ssh_ok else 0.0

    # 4. finds_dev_port_exposure — mention 8080
    dev_ok = bool(re.search(r"8080", text))
    finds_dev_port_exposure = 1.0 if dev_ok else 0.0

    # 5. finds_permissive_accept_rule — mention the commented -j ACCEPT catch-all
    permissive_ok = bool(
        re.search(r"-j\s*accept", text) and
        re.search(r"(comment|注釋|commented|#|danger|危險|permissive|allow all|全放行)", text)
    )
    finds_permissive_accept_rule = 1.0 if permissive_ok else 0.0

    # 6. critical_severity_used
    critical_ok = bool(re.search(r"critical|🔴|嚴重|高危", text))
    critical_severity_used = 1.0 if critical_ok else 0.0

    # 7. has_dry_run_patch — iptables -D or iptables -I commands
    patch_ok = bool(
        re.search(r"iptables\s+-d\b", text) or
        re.search(r"iptables\s+-i\b", text) or
        re.search(r"iptables -d|iptables -i", text)
    )
    has_dry_run_patch = 1.0 if patch_ok else 0.0

    # 8. no_execution_claimed
    executed_phrases = [
        r"已執行|already executed|has been applied|rules applied",
        r"successfully deleted|successfully inserted",
        r"changes have been made",
    ]
    execution_claimed = any(re.search(p, text) for p in executed_phrases)
    no_execution_claimed = 0.0 if execution_claimed else 1.0

    # 9. all_4_issues_found
    issues_found = sum([
        1 if finds_mysql_exposure == 1.0 else 0,
        1 if finds_ssh_duplicate == 1.0 else 0,
        1 if dev_ok else 0,
        1 if permissive_ok else 0,
    ])
    if issues_found >= 4:
        all_4_issues_found = 1.0
    elif issues_found >= 2:
        all_4_issues_found = 0.5
    else:
        all_4_issues_found = 0.0

    # 10. risk_recommendations_present
    rec_ok = bool(
        re.search(r"(recommend|建議|suggest|restrict|限制|修正|fix|patch)", text) and
        len(text) > 500
    )
    risk_recommendations_present = 1.0 if rec_ok else 0.0

    return {
        "file_exists": 1.0,
        "finds_mysql_exposure": finds_mysql_exposure,
        "finds_ssh_duplicate": finds_ssh_duplicate,
        "finds_dev_port_exposure": finds_dev_port_exposure,
        "finds_permissive_accept_rule": finds_permissive_accept_rule,
        "critical_severity_used": critical_severity_used,
        "has_dry_run_patch": has_dry_run_patch,
        "no_execution_claimed": no_execution_claimed,
        "all_4_issues_found": all_4_issues_found,
        "risk_recommendations_present": risk_recommendations_present,
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

Evaluate the file `firewall_analysis_report.md` on the following criteria:

### Criteria

**1. Issue Identification Completeness (35%)**
Does the report correctly identify all 4 planted firewall problems with accurate technical details (port numbers, source IPs, rule text)?
- 1.0: All 4 issues found with correct rule text cited, correct source IP (0.0.0.0/0 vs 10.0.0.0/8), and the commented `-j ACCEPT` danger noted
- 0.5: 2-3 issues identified correctly
- 0.0: Fewer than 2 issues or major technical inaccuracies

**2. Severity Classification Accuracy (25%)**
Does the report correctly assign CRITICAL vs RISKY severity levels?
- 1.0: MySQL 3306 and commented ACCEPT rule = CRITICAL; SSH duplicate and 8080 = RISKY; classifications match definitions
- 0.5: Some severities correct but at least one misclassified
- 0.0: No severity classification or all wrong

**3. Dry-Run Patch Quality (25%)**
Does the report provide syntactically correct iptables commands to fix the issues?
- 1.0: Correct `iptables -D INPUT` commands referencing the bad rules and `iptables -I INPUT` with proper replacements (e.g., restricting 3306 to 10.0.0.0/8), all labeled as dry-run
- 0.5: Some commands present but incomplete, wrong syntax, or missing dry-run label
- 0.0: No commands or commands are plain wrong

**4. Report Clarity & Actionability (15%)**
Is the report well-structured, clear, and actionable for an operations team?
- 1.0: Clear sections, each issue has rule text + risk explanation + fix command, overall recommendation present
- 0.5: Mostly clear but missing some context or hard to follow
- 0.0: Disorganized, incomplete, or too vague to act on

## Additional Notes

核心考驗：
- 解析 iptables-save 格式並逐條稽核 INPUT chain 規則
- 辨識來源網段（`0.0.0.0/0` vs `10.0.0.0/8`）造成的對外暴露風險
- 正確區分 CRITICAL 與 RISKY 嚴重等級
- 產生語法正確的 `iptables -D` / `iptables -I` Dry-Run 修補指令
- 維持 dry-run 性質，不得宣稱已實際套用任何變更
