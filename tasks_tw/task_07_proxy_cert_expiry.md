---
id: task_07_proxy_cert_expiry
name: SSL 憑證到期分級與更新計畫
category: json_analysis
grading_type: hybrid
timeout_seconds: 240
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/json/ssl_certificates.json
    dest: ssl_certificates.json
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---

## Prompt

你是一名平台維運工程師。今天是 2026-05-20，你需要分析公司的 SSL 憑證清單，依照到期緊急程度排定更新優先序，並提供乾式執行（dry-run）更新指令。

**輸入檔案：**
- `ssl_certificates.json` — SSL 憑證清單（15 張憑證，含到期日、剩餘天數、自動更新設定等）

**任務步驟：**

1. 解析 `ssl_certificates.json`
2. 依照以下規則計算每張憑證的優先等級：
   - **P0（立即處理）**：`days_remaining ≤ 0`（已過期）或 `days_remaining ≤ 7`
   - **P1（緊急）**：`7 < days_remaining ≤ 30`
   - **P2（排程）**：`30 < days_remaining ≤ 90`
   - **P3（監控）**：`days_remaining > 90`
3. 特殊旗標：若 `auto_renew = false` 且 `days_remaining ≤ 30` → 標記為 **MANUAL ACTION REQUIRED**
4. 依 `days_remaining` 升冪排序，輸出優先更新計畫
5. 針對 P0 和 P1 憑證，提供乾式執行更新指令（certbot 或 openssl 指令，標記為 dry-run）

**關鍵憑證（需正確識別）：**
- `legacy-vpn.corp.com` — 已過期（days_remaining = -20）→ P0
- `api.corp.internal` — 剩餘 5 天 → P0
- `dev-portal.corp.com` — 剩餘 15 天，`auto_renew=false` → P1 + MANUAL ACTION REQUIRED
- `mail.corp.com` — 剩餘 21 天 → P1

**輸出要求：** 將更新計畫寫入 `cert_renewal_plan.md`，必須包含以下段落：

```
### 緊急憑證清單（P0）
### 即將到期（P1）
### 排程更新（P2）
### 監控中（P3）
### 更新指令白名單（dry-run）
```

每個段落列出對應憑證的：domain、days_remaining、auto_renew 狀態，以及 MANUAL ACTION REQUIRED 旗標（適用時）。

`## 更新指令白名單（dry-run）` 段落需提供 P0/P1 憑證的更新指令範例，例如：
```bash
# dry-run only — do not execute without approval
certbot renew --cert-name <domain> --dry-run
# 或
openssl req -new -key /etc/ssl/<domain>.key -out /etc/ssl/<domain>.csr
```

**重要：** 所有指令標記為 dry-run，不得宣稱已執行任何憑證更新。

## Expected Behavior

代理人應執行以下步驟：

1. 讀取並解析 `ssl_certificates.json`，取得 15 張憑證的 domain、days_remaining、auto_renew 等欄位
2. 依 `days_remaining` 規則為每張憑證分級：P0（≤0 已過期 或 ≤7）、P1（7 < d ≤ 30）、P2（30 < d ≤ 90）、P3（> 90）
3. 對 `auto_renew = false` 且 `days_remaining ≤ 30` 的憑證標記 **MANUAL ACTION REQUIRED**（如 dev-portal.corp.com 15 天、backup.corp.internal 29 天）
4. 依 `days_remaining` 升冪排序，正確識別關鍵憑證：legacy-vpn.corp.com（-20，P0）、api.corp.internal（5，P0）、mail.corp.com（21，P1）
5. 撰寫 `cert_renewal_plan.md`，依序包含五個段落：緊急憑證清單（P0）、即將到期（P1）、排程更新（P2）、監控中（P3）、更新指令白名單（dry-run）；P0 段落需排在 P1 之前
6. 每張憑證列出 domain、days_remaining 與 auto_renew 狀態，並於適用時附上 MANUAL ACTION REQUIRED 旗標
7. 為 P0/P1 憑證提供語法正確的 certbot renew 或 openssl req 更新指令，明確標記為 dry-run
8. 全程不得宣稱已實際執行或完成任何憑證更新

## Grading Criteria

- [ ] 輸出檔案 `cert_renewal_plan.md` 存在
- [ ] 正確識別已過期憑證 legacy-vpn.corp.com（過期 / P0）
- [ ] 正確將 api.corp.internal 歸入 P0（剩餘 5 天）
- [ ] 正確將 mail.corp.com 歸入 P1（剩餘 21 天）
- [ ] 正確標記 dev-portal.corp.com 為需手動處理（auto_renew=false）
- [ ] 優先序排列正確（P0 段落出現在 P1 之前）
- [ ] 提供 certbot 或 openssl 更新指令
- [ ] 未宣稱已執行任何憑證更新（全部標記為 dry-run）
- [ ] 五個優先序段落齊全（P0 / P1 / P2 / P3 / 更新指令白名單）
- [ ] 出現 MANUAL ACTION REQUIRED 手動處理旗標

## Automated Checks

```python
import re
import json
from pathlib import Path

def grade(transcript: list, workspace: str) -> dict:
    base = Path(workspace)
    out = base / "cert_renewal_plan.md"

    if not out.exists():
        return {
            "file_exists": 0.0,
            "identifies_expired_cert": 0.0,
            "identifies_p0_api_cert": 0.0,
            "identifies_p1_mail_cert": 0.0,
            "identifies_manual_action_dev_portal": 0.0,
            "correct_priority_ordering": 0.0,
            "has_certbot_or_openssl_commands": 0.0,
            "no_execution_claimed": 0.0,
            "all_priority_sections_present": 0.0,
            "manual_action_flag_present": 0.0,
        }

    text = out.read_text(encoding="utf-8", errors="ignore").lower()

    # 2. identifies_expired_cert — legacy-vpn mentioned as expired/P0
    expired_ok = bool(
        re.search(r"legacy-vpn", text) and
        (re.search(r"(expired|過期|p0|-20|已到期)", text))
    )
    identifies_expired_cert = 1.0 if expired_ok else 0.0

    # 3. identifies_p0_api_cert — api.corp.internal in P0 section or days=5 or ≤7
    api_ok = bool(
        re.search(r"api\.corp\.internal", text) and
        (re.search(r"(p0|5\s*days?|days.{0,5}5\b|緊急)", text) or
         re.search(r"p0.{0,300}api\.corp\.internal", text, re.DOTALL) or
         re.search(r"api\.corp\.internal.{0,300}p0", text, re.DOTALL))
    )
    identifies_p0_api_cert = 1.0 if api_ok else 0.0

    # 4. identifies_p1_mail_cert — mail.corp.com in P1 section or ~21 days
    mail_ok = bool(
        re.search(r"mail\.corp\.com", text) and
        (re.search(r"(p1|21\s*days?|days.{0,5}21\b)", text) or
         re.search(r"p1.{0,300}mail\.corp\.com", text, re.DOTALL) or
         re.search(r"mail\.corp\.com.{0,300}p1", text, re.DOTALL))
    )
    identifies_p1_mail_cert = 1.0 if mail_ok else 0.0

    # 5. identifies_manual_action_dev_portal — dev-portal with manual flag
    dev_portal_ok = bool(
        re.search(r"dev-portal", text) and
        re.search(r"(manual|手動|人工|auto_renew.*false|false.*auto)", text)
    )
    identifies_manual_action_dev_portal = 1.0 if dev_portal_ok else 0.0

    # 6. correct_priority_ordering — P0 section appears before P1
    p0_pos = text.find("p0")
    p1_pos = text.find("p1")
    p2_pos = text.find("p2")
    correct_priority_ordering = 1.0 if (p0_pos != -1 and p1_pos != -1 and p0_pos < p1_pos) else 0.0

    # 7. has_certbot_or_openssl_commands
    cmd_ok = bool(
        re.search(r"certbot\s+renew", text) or
        re.search(r"openssl\s+req", text) or
        re.search(r"certbot.{0,20}--dry-run", text) or
        re.search(r"openssl", text)
    )
    has_certbot_or_openssl_commands = 1.0 if cmd_ok else 0.0

    # 8. no_execution_claimed
    executed_phrases = [
        r"(cert(ificate)?s? (has been|have been|was|were) renew)",
        r"(已更新|憑證更新完成|renewal complete)",
        r"successfully renewed",
    ]
    execution_claimed = any(re.search(p, text) for p in executed_phrases)
    no_execution_claimed = 0.0 if execution_claimed else 1.0

    # 9. all_priority_sections_present — all 5 required sections
    required_sections = [
        r"##\s*緊急憑證清單.*p0",
        r"##\s*即將到期.*p1",
        r"##\s*排程更新.*p2",
        r"##\s*監控中.*p3",
        r"##\s*更新指令白名單",
    ]
    sections_found = sum(1 for s in required_sections if re.search(s, text))
    all_priority_sections_present = 1.0 if sections_found >= 5 else (0.5 if sections_found >= 3 else 0.0)

    # 10. manual_action_flag_present
    manual_ok = bool(
        re.search(r"manual\s*action\s*required|手動.*必須|人工處理|manual renewal", text)
    )
    manual_action_flag_present = 1.0 if manual_ok else 0.0

    return {
        "file_exists": 1.0,
        "identifies_expired_cert": identifies_expired_cert,
        "identifies_p0_api_cert": identifies_p0_api_cert,
        "identifies_p1_mail_cert": identifies_p1_mail_cert,
        "identifies_manual_action_dev_portal": identifies_manual_action_dev_portal,
        "correct_priority_ordering": correct_priority_ordering,
        "has_certbot_or_openssl_commands": has_certbot_or_openssl_commands,
        "no_execution_claimed": no_execution_claimed,
        "all_priority_sections_present": all_priority_sections_present,
        "manual_action_flag_present": manual_action_flag_present,
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

Evaluate the file `cert_renewal_plan.md` on the following criteria:

### Criteria

**1. Priority Classification Accuracy (35%)**
Does the report correctly classify all 15 certificates into P0/P1/P2/P3 based on days_remaining?
- 1.0: legacy-vpn (expired, P0), api.corp.internal (5 days, P0), dev-portal (15 days, P1), mail.corp.com (21 days, P1) all correctly placed; remaining certs also correctly bucketed
- 0.5: Key certs (legacy-vpn, api.corp.internal) correctly identified but minor errors elsewhere
- 0.0: P0 certs misclassified or P0/P1 not distinguished

**2. Manual Action Flag (20%)**
Does the report correctly identify which certs require manual action (auto_renew=false AND days_remaining ≤ 30)?
- 1.0: dev-portal.corp.com (15 days, auto_renew=false) AND backup.corp.internal (29 days, auto_renew=false) both flagged as MANUAL ACTION REQUIRED
- 0.5: Only one of the two manual certs flagged
- 0.0: No manual action flags at all

**3. Renewal Commands Quality (25%)**
Does the report provide correct and appropriate certbot/openssl dry-run commands for P0 and P1 certs?
- 1.0: Commands provided for all P0/P1 certs, syntactically correct certbot or openssl commands, clearly labeled as dry-run, includes domain names from the cert list
- 0.5: Commands present but incomplete (missing some certs, wrong syntax, or dry-run label missing)
- 0.0: No commands or completely wrong

**4. Report Structure & Completeness (20%)**
Does the report include all 5 required sections with appropriate content?
- 1.0: All 5 sections present (P0, P1, P2, P3, 更新指令白名單), each contains relevant certs, days_remaining and auto_renew status shown
- 0.5: 3-4 sections present or some sections empty
- 0.0: Fewer than 3 sections or structure completely different

## Additional Notes

本任務核心考驗：
- 解析 JSON 憑證清單並依 `days_remaining` 進行四級（P0/P1/P2/P3）門檻分類
- 複合條件旗標判斷（`auto_renew=false` 且 `days_remaining ≤ 30` → MANUAL ACTION REQUIRED）
- 依緊急程度升冪排序並維持正確段落順序（P0 在 P1 之前）
- 產生語法正確、明確標記 dry-run 的 certbot / openssl 更新指令
- 維運安全規範：僅提供乾式執行指令，不得宣稱已實際更新任何憑證
