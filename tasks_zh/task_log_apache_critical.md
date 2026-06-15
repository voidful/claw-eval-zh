---
id: task_log_apache_critical
name: Apache 錯誤日誌 — 找出關鍵資安問題
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_apache_critical
source_benchmark: pinchbench
claw_eval_id: P082zh_log_apache_critical
workspace_files:
- dest: apache_error.log
  source: logs/apache_error.log
---

# Apache 錯誤日誌 — 找出關鍵資安問題

## Prompt

你是一名資安分析師，正在檢視位於 `apache_error.log` 的 Apache 錯誤日誌。你的任務是找出所有**與資安相關**的條目——也就是顯示針對此伺服器的主動攻擊、漏洞掃描或漏洞利用嘗試的條目。

請將每個發現分類到下列其中一個嚴重性等級：

| 嚴重性 | 定義 |
|---|---|
| `critical` | 主動的漏洞利用嘗試（例如命令執行、帶編碼酬載的目錄路徑穿越） |
| `high` | 針對特定已知漏洞的漏洞掃描 |
| `medium` | 偵察活動（目錄探測、來自單一 IP 反覆的 forbidden 請求） |
| `low` | 可能代表組態錯誤、但並非攻擊的偶發錯誤 |

請把你的發現寫到 `security_findings.json`，以 JSON 陣列呈現。每個元素必須是一個物件，包含：

```json
{
  "severity": "critical",
  "category": "Brief category name",
  "source_ips": ["1.2.3.4", "5.6.7.8"],
  "evidence": "Description of what was found and why it's a security concern",
  "sample_entry": "One example log line"
}
```

請依嚴重性由 critical 到 low 排序。

## Expected Behavior

助手至少應找出下列發現：

**Critical：**
- **IIS 目錄路徑穿越／命令執行嘗試**：多個 IP 送出含有如 `/scripts/..%c0%af../winnt/system32/cmd.exe?/c+dir` 路徑的「Invalid method」請求。這些利用 Unicode 編碼漏洞（CVE-2000-0884、CVE-2001-0333）嘗試遠端命令執行。來源 IP 包括：63.203.254.140、213.61.135.6、201.252.246.11、62.221.237.83、213.205.73.192、64.147.69.59、207.181.126.3、12.216.230.125、220.228.80.199、64.60.251.53、63.197.230.242、61.72.66.8、202.118.167.71。
- **IIS 蠕蟲傳播探測**：IP 掃描 root.exe、MSADC、_vti_bin、_mem_bin、msadc，以及路徑穿越路徑（`..%5c..`、`..\xc1\x1c..`、`..\xc0\xaf..`、`..\xc1\x9c..`、`..%2f..`）。這些符合 Nimda/Code Red 蠕蟲行為。

**High：**
- **Awstats 漏洞掃描**：202.133.98.6 送出約 184 次請求，在多個路徑（cgi-bin、/awstats/、/stats/、/cgi/）探測 awstats.pl。AWStats 曾有已知的遠端命令執行漏洞。
- **OpenWebMail 掃描**：212.238.198.203 探測 /var/www/cgi-bin/openwebmail 共 20 次。
- **緩衝區溢位（buffer overflow）嘗試**：IP 210.91.137.35、211.211.14.224 與 150.161.187.25 送出觸發「URI too long (longer than 8190)」錯誤的請求，並伴隨 _vti_bin 探測。

**Medium：**
- **大規模目錄探測**：多個 IP 反覆請求目錄索引（195.23.79.241 約 22 次、219.133.246.207 約 15 次、218.82.188.130 約 13 次等）

可接受的變化：
- 嚴重性分類可略有不同（例如將 awstats 列為「critical」而非「high」）
- 超出預期清單之外的額外發現無妨
- 只要關鍵攻擊者被找出，IP 清單不完整亦可

## Grading Criteria

- [ ] 已在工作區建立 `security_findings.json`
- [ ] 已將命令執行／目錄路徑穿越嘗試判定為 critical（cmd.exe、root.exe 樣式）
- [ ] 已找出 Awstats 掃描（202.133.98.6 或 awstats 關鍵字）
- [ ] 至少找出 3 種不同的攻擊類別
- [ ] 發現結果使用嚴重性分類系統

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Apache error log critical security issues task."""
    from pathlib import Path
    import json

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "security_findings.json"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "cmd_traversal_critical": 0.0,
            "awstats_scanning": 0.0,
            "multiple_categories": 0.0,
            "severity_classification": 0.0,
        }

    scores["output_created"] = 1.0

    try:
        data = json.loads(report_file.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            data = data.get("findings", data.get("security_findings", []))
        if not isinstance(data, list):
            data = []
    except (json.JSONDecodeError, Exception):
        return {
            "output_created": 1.0,
            "cmd_traversal_critical": 0.0,
            "awstats_scanning": 0.0,
            "multiple_categories": 0.0,
            "severity_classification": 0.0,
        }

    full_text = json.dumps(data).lower()

    # Check 1: Command execution / directory traversal identified
    traversal_keywords = ["cmd.exe", "root.exe", "traversal", "command execution",
                          "invalid method", "nimda", "code red", "worm", "unicode"]
    has_traversal = sum(1 for kw in traversal_keywords if kw in full_text) >= 2
    has_critical = "critical" in full_text
    scores["cmd_traversal_critical"] = (
        1.0 if has_traversal and has_critical else
        0.5 if has_traversal else 0.0
    )

    # Check 2: Awstats scanning identified
    has_awstats = "awstats" in full_text
    has_scanner_ip = "202.133.98.6" in full_text
    scores["awstats_scanning"] = (
        1.0 if has_awstats or has_scanner_ip else 0.0
    )

    # Check 3: At least 3 distinct attack categories
    categories_found = 0
    category_patterns = [
        ["cmd.exe", "root.exe", "traversal", "command", "invalid method"],
        ["awstats", "202.133.98.6"],
        ["_vti_bin", "frontpage", "iis"],
        ["openwebmail", "212.238.198.203"],
        ["directory", "forbidden", "scanning", "probing", "reconnaissance"],
        ["uri too long", "buffer", "overflow", "8190"],
    ]
    for patterns in category_patterns:
        if any(p in full_text for p in patterns):
            categories_found += 1
    scores["multiple_categories"] = (
        1.0 if categories_found >= 3 else
        0.5 if categories_found >= 2 else 0.0
    )

    # Check 4: Severity classification used
    severity_levels = ["critical", "high", "medium", "low"]
    levels_used = sum(1 for s in severity_levels if s in full_text)
    scores["severity_classification"] = (
        1.0 if levels_used >= 3 else
        0.5 if levels_used >= 2 else 0.0
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
- 已在工作區建立 `security_findings.json`
- 已將命令執行／目錄路徑穿越嘗試判定為 critical（cmd.exe、root.exe 樣式）
- 已找出 Awstats 掃描（202.133.98.6 或 awstats 關鍵字）
- 至少找出 3 種不同的攻擊類別
- 發現結果使用嚴重性分類系統
