---
id: task_log_ssh_brute_force
name: SSH 認證日誌 — 暴力破解偵測
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_ssh_brute_force
source_benchmark: pinchbench
claw_eval_id: P091zh_log_ssh_brute_force
workspace_files:
- dest: auth.log
  source: logs/openssh_auth.log
---

# SSH 認證日誌 — 暴力破解偵測

## Prompt

你是一名資安分析師，正在檢視位於 `auth.log` 的 OpenSSH 認證日誌。你的任務是偵測暴力破解（brute-force）攻擊樣態，並產生一份威脅評估。

暴力破解攻擊的定義為：**在日誌期間內，來自單一 IP 位址的認證失敗嘗試超過 10 次**。

你的報告應包含：

1. **暴力破解來源（Brute Force Sources）**：列出所有達到暴力破解門檻的 IP，並附各 IP 的失敗嘗試總數
2. **攻擊強度（Attack Intensity）**：對每個暴力破解來源，計算約略的嘗試速率（每分鐘嘗試次數）
3. **使用者名稱樣態（Username Patterns）**：對每個攻擊 IP，他們嘗試了哪些使用者名稱？是字典攻擊（dictionary attack，眾多使用者名稱）還是定向攻擊（targeted，少數使用者名稱）？
4. **攻擊時間軸（Attack Timeline）**：每個攻擊何時開始與停止？攻擊者之間是否有重疊？
5. **反向 DNS 分析（Reverse DNS Analysis）**：哪些攻擊 IP 觸發了「POSSIBLE BREAK-IN ATTEMPT」警告？
6. **風險評估（Risk Assessment）**：評定整體威脅等級，並建議具體的對策

請把報告寫到 `brute_force_report.json`，採用如下結構的 JSON 文件：

```json
{
  "summary": "Brief summary",
  "brute_force_sources": [
    {
      "ip": "x.x.x.x",
      "total_attempts": 100,
      "first_seen": "Dec 10 HH:MM:SS",
      "last_seen": "Dec 10 HH:MM:SS",
      "usernames_tried": ["user1", "user2"],
      "attack_type": "dictionary|targeted",
      "reverse_dns_warning": true
    }
  ],
  "risk_level": "critical|high|medium|low",
  "recommendations": ["rec1", "rec2"]
}
```

## Expected Behavior

助手應找出這些暴力破解來源：

**主要攻擊者：**
- **183.62.140.253** —— 約 307 筆條目，最重度的攻擊者，很可能是字典攻擊
- **187.141.143.180** —— 約 189 筆條目，持續性攻擊
- **103.99.0.122** —— 約 83 筆條目
- **112.95.230.3** —— 約 54 筆條目
- **5.188.10.180** —— 約 30 筆條目
- **185.190.58.151** —— 約 26 筆條目

**關鍵發現：**
- 來自不同 IP 的多重並行暴力破解攻擊
- 攻擊橫跨約 4 小時（06:55–10:59）
- 使用者名稱樣態包含常見預設值（admin、root、test、oracle、support）
- 85 次「POSSIBLE BREAK-IN ATTEMPT」警告，顯示反向 DNS 遭偽造或設定錯誤
- 風險等級應評為 high 或 critical

可接受的變化：
- 暴力破解偵測的門檻可有所不同
- 速率計算取決於如何判定第一次／最後一次時間戳記
- 建議的具體內容會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `brute_force_report.json`
- [ ] 已找出至少 3 個暴力破解來源 IP
- [ ] 已將 183.62.140.253 判定為頭號攻擊者
- [ ] 已為每個來源分類攻擊類型（字典攻擊 vs 定向攻擊）
- [ ] 已提供對策建議

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the SSH brute force detection task."""
    from pathlib import Path
    import json

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "brute_force_report.json"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "sources_identified": 0.0,
            "top_attacker": 0.0,
            "attack_classified": 0.0,
            "recommendations": 0.0,
        }

    scores["output_created"] = 1.0

    try:
        data = json.loads(report_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return {
            "output_created": 1.0,
            "sources_identified": 0.0,
            "top_attacker": 0.0,
            "attack_classified": 0.0,
            "recommendations": 0.0,
        }

    full_text = json.dumps(data).lower()

    # Check 1: At least 3 brute-force sources identified
    sources = data.get("brute_force_sources", [])
    if not isinstance(sources, list):
        sources = []
    scores["sources_identified"] = (
        1.0 if len(sources) >= 3 else
        0.5 if len(sources) >= 1 else 0.0
    )

    # Check 2: Top attacker identified
    scores["top_attacker"] = 1.0 if "183.62.140.253" in full_text else 0.0

    # Check 3: Attack type classified
    has_classification = "dictionary" in full_text or "targeted" in full_text or "attack_type" in full_text
    scores["attack_classified"] = 1.0 if has_classification else 0.0

    # Check 4: Recommendations provided
    recs = data.get("recommendations", [])
    if not isinstance(recs, list):
        recs = []
    has_recs = len(recs) >= 2 or any(kw in full_text for kw in
        ["fail2ban", "rate limit", "firewall", "block", "key-based",
         "disable password", "allowlist", "whitelist", "deny"])
    scores["recommendations"] = 1.0 if has_recs else 0.5 if len(recs) >= 1 else 0.0

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
- 已在工作區建立 `brute_force_report.json`
- 已找出至少 3 個暴力破解來源 IP
- 已將 183.62.140.253 判定為頭號攻擊者
- 已為每個來源分類攻擊類型（字典攻擊 vs 定向攻擊）
- 已提供對策建議
