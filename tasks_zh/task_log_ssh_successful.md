---
id: task_log_ssh_successful
name: SSH 認證日誌 — 成功認證摘要
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_ssh_successful
source_benchmark: pinchbench
claw_eval_id: P092zh_log_ssh_successful
workspace_files:
- dest: auth.log
  source: logs/openssh_auth.log
---

# SSH 認證日誌 — 成功認證摘要

## Prompt

請分析位於 `auth.log` 的 OpenSSH 認證日誌，並產生一份聚焦於成功認證的報告。請在眾多失敗嘗試的雜訊中，找出所有合法存取。

你的報告應包含：

1. **成功登入（Successful Logins）**：列出每一次成功認證，包含時間戳記、使用者名稱、來源 IP、連接埠與認證方法
2. **成功對失敗比（Success vs Failure Ratio）**：所有認證嘗試中有多少百分比成功？
3. **合法使用者輪廓（Legitimate User Profile）**：對每位成功認證的使用者，描述其存取樣態
4. **工作階段活動（Session Activity）**：是否有登入後發生事件的證據（session opened/closed 事件）？
5. **來源 IP 驗證（Source IP Validation）**：成功登入的 IP 是否同時也與某些失敗嘗試相關聯？
6. **異常檢查（Anomaly Check）**：此次成功登入看來合法，還是可疑（例如來自同時也在進行暴力破解的 IP）？

請把報告寫到 `successful_auth_report.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應找出：

**成功登入：**
- 整份日誌中只有 1 次成功登入：
  - 時間：Dec 10 09:32:20
  - 使用者：fztu
  - 來源：119.137.62.142
  - 連接埠：49116
  - 方法：password (ssh2)
  - 條目：「Accepted password for fztu from 119.137.62.142 port 49116 ssh2」

**成功對失敗比：**
- 數百次嘗試中只有 1 次成功——成功率極低
- 這再次印證此日誌捕捉到一台正遭受暴力破解攻擊的伺服器

**異常檢查：**
- 應將 119.137.62.142（成功登入的 IP）與失敗嘗試清單核對
- 若它只出現在成功條目中，很可能是合法使用者
- 若它也有失敗嘗試，則可能是遭洩漏的憑證（compromised credential）

**工作階段活動：**
- 找尋使用者 fztu 對應的「session opened」／「session closed」事件

可接受的變化：
- 分析深度可有所不同
- 部分助手可能找到額外的工作階段相關條目
- 異常評估用語會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `successful_auth_report.md`
- [ ] 已找出唯一一次成功登入（使用者 fztu、IP 119.137.62.142）
- [ ] 已計算成功／失敗比（1 次成功 vs 數百次失敗）
- [ ] 已將成功登入的 IP 與失敗嘗試來源核對
- [ ] 已提供此次登入是否看來合法的評估

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the SSH successful authentication summary task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "successful_auth_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "login_identified": 0.0,
            "ratio_calculated": 0.0,
            "ip_checked": 0.0,
            "legitimacy_assessed": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Successful login identified
    has_user = "fztu" in content
    has_ip = "119.137.62.142" in content
    has_accepted = "accepted" in content or "successful" in content
    scores["login_identified"] = (
        1.0 if has_user and has_ip else
        0.5 if has_user or has_ip else 0.0
    )

    # Check 2: Ratio calculated
    ratio_keywords = ["ratio", "percent", "1 success", "1 out of", "only 1",
                      "single success", "one success", "0."]
    scores["ratio_calculated"] = (
        1.0 if sum(1 for kw in ratio_keywords if kw in content) >= 1 else 0.0
    )

    # Check 3: IP checked against failed attempts
    check_keywords = ["119.137.62.142", "not associated", "not found",
                      "does not appear", "no failed", "legitimate",
                      "only successful", "no other"]
    scores["ip_checked"] = (
        1.0 if has_ip and sum(1 for kw in check_keywords if kw in content) >= 2 else
        0.5 if has_ip else 0.0
    )

    # Check 4: Legitimacy assessment
    legit_keywords = ["legitimate", "authorized", "valid", "genuine",
                      "suspicious", "anomal", "normal", "expected"]
    scores["legitimacy_assessed"] = (
        1.0 if sum(1 for kw in legit_keywords if kw in content) >= 1 else 0.0
    )

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

依下列評分標準逐項評估（每項 0.0–1.0，最後取平均）：
- 已在工作區建立 `successful_auth_report.md`
- 已找出唯一一次成功登入（使用者 fztu、IP 119.137.62.142）
- 已計算成功／失敗比（1 次成功 vs 數百次失敗）
- 已將成功登入的 IP 與失敗嘗試來源核對
- 已提供此次登入是否看來合法的評估
