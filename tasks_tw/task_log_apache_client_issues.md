---
id: task_log_apache_client_issues
name: Apache 錯誤日誌 — 找出有問題的用戶端 IP
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_apache_client_issues
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T079tw_log_apache_client_issues
workspace_files:
- dest: apache_error.log
  source: logs/apache_error.log
---

# Apache 錯誤日誌 — 找出有問題的用戶端 IP

## Prompt

請分析位於 `apache_error.log` 的 Apache 錯誤日誌，並找出最有問題的用戶端 IP 位址。此日誌來自一台執行於 Fedora、版本為 Apache 2.0.49 的伺服器，涵蓋 2005 年 6 月 9 日至 16 日。

對於**錯誤數最多的前 5 個用戶端 IP**，請回報：

1. IP 位址
2. 錯誤條目（error entry）總數
3. 該 IP 所產生的主要錯誤類型
4. 該用戶端是否疑似在進行惡意活動（掃描、漏洞利用嘗試等）——並說明原因

請把你的發現寫到 `client_issues_report.md`，以 markdown 文件呈現，先放一個摘要表格，接著對每個 IP 做簡短分析。文末請加上一個區段，列出所有送出 **Invalid method** 請求的 IP（這些是使用畸形 HTTP 方法的漏洞利用嘗試），因為它們代表最高嚴重性的威脅。

## Expected Behavior

助手應該解析日誌檔，並依用戶端 IP 統計錯誤條目數。錯誤數最多的前 5 個 IP 為：

| 排名 | IP | 錯誤數 | 主要活動 |
|---|---|---|---|
| 1 | 202.133.98.6 | ~184 | 掃描 awstats／統計類腳本（檔案不存在、找不到腳本） |
| 2 | 81.214.165.213 | ~23 | 探測 `_vti_bin`（FrontPage extensions） |
| 3 | 81.199.21.119 | ~23 | 反覆請求 `/var/www/html/sumthin` |
| 4 | 194.116.250.2 | ~23 | 反覆請求 `/var/www/html/sumthin` |
| 5 | 195.23.79.241 | ~22 | 目錄索引被禁止（大規模掃描） |

助手也應找出送出 Invalid method 請求的 IP，其中包含針對 Windows IIS 漏洞的利用嘗試（透過 Unicode／雙重編碼路徑穿越攻擊 cmd.exe、root.exe）。送出 Invalid method 請求的不重複 IP 約有 13 個，包括：63.203.254.140、213.61.135.6、201.252.246.11、62.221.237.83、202.118.167.71、64.147.69.59 等。

可接受的變化：
- 由於非用戶端錯誤行的解析存在模糊性，計數有小幅差異（±5）可接受
- 若採用不同計數方法，助手對 IP 的排序可能略有不同
- 列出前 5 名以外的額外 IP 無妨
- 描述的詳盡程度可有所不同

## Grading Criteria

- [ ] 已在工作區建立 `client_issues_report.md`
- [ ] 已將 IP `202.133.98.6` 判定為最有問題的用戶端（錯誤數最高）
- [ ] 報告指出 `202.133.98.6` 在掃描 awstats 或統計相關腳本
- [ ] 前 5 個 IP 中至少有 3 個被正確找出，並附上約略錯誤數
- [ ] 已列出送出 Invalid method 請求的 IP，並判定為漏洞利用／攻擊嘗試

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Apache error log client issues analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "client_issues_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "top_client_identified": 0.0,
            "awstats_scanning_noted": 0.0,
            "top5_accuracy": 0.0,
            "invalid_method_ips": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: 202.133.98.6 identified as top problematic client
    scores["top_client_identified"] = (
        1.0 if "202.133.98.6" in content else 0.0
    )

    # Check 2: awstats scanning noted for 202.133.98.6
    has_awstats = any(kw in content for kw in ["awstats", "statistics", "stats"])
    has_top_ip = "202.133.98.6" in content
    scores["awstats_scanning_noted"] = (
        1.0 if has_awstats and has_top_ip else 0.0
    )

    # Check 3: At least 3 of top 5 IPs present
    top5_ips = ["202.133.98.6", "81.214.165.213", "81.199.21.119", "194.116.250.2", "195.23.79.241"]
    found_count = sum(1 for ip in top5_ips if ip in content)
    scores["top5_accuracy"] = min(found_count / 3.0, 1.0)

    # Check 4: Invalid method IPs identified as attacks
    invalid_method_ips = [
        "63.203.254.140", "213.61.135.6", "201.252.246.11",
        "62.221.237.83", "202.118.167.71", "64.147.69.59"
    ]
    invalid_found = sum(1 for ip in invalid_method_ips if ip in content)
    has_attack_keyword = any(kw in content for kw in [
        "invalid method", "exploit", "attack", "malicious",
        "cmd.exe", "root.exe", "traversal", "worm"
    ])
    scores["invalid_method_ips"] = (
        1.0 if invalid_found >= 3 and has_attack_keyword else
        0.5 if invalid_found >= 1 and has_attack_keyword else 0.0
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
- 已在工作區建立 `client_issues_report.md`
- 已將 IP `202.133.98.6` 判定為最有問題的用戶端（錯誤數最高）
- 報告指出 `202.133.98.6` 在掃描 awstats 或統計相關腳本
- 前 5 個 IP 中至少有 3 個被正確找出，並附上約略錯誤數
- 已列出送出 Invalid method 請求的 IP，並判定為漏洞利用／攻擊嘗試
