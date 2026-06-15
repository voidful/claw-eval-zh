---
id: task_log_nginx_status_codes
name: Nginx 存取日誌 — HTTP 狀態碼分布
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_nginx_status_codes
source_benchmark: pinchbench
claw_eval_id: P085zh_log_nginx_status_codes
workspace_files:
- dest: nginx_access.log
  source: logs/nginx_access_json.log
---

# Nginx 存取日誌 — HTTP 狀態碼分布

## Prompt

請分析位於 `nginx_access.log` 的 Nginx JSON 存取日誌，並產生一份 HTTP 狀態碼分布報告。每一行都是一個 JSON 物件，欄位有：`time`、`remote_ip`、`remote_user`、`request`、`response`、`bytes`、`referrer`、`agent`。

你的報告應包含：

1. **請求總數（Total Requests）**：日誌條目總數
2. **狀態碼分布（Status Code Breakdown）**：每個出現過的 HTTP 狀態碼的計數與百分比
3. **狀態碼類別（Status Code Categories）**：依類別分組（2xx 成功、3xx 重新導向、4xx 用戶端錯誤、5xx 伺服器錯誤），並附各類總計
4. **主要肇因者（Top Offenders）**：對於 4xx 與 5xx 錯誤，列出產生最多錯誤的前 5 個用戶端 IP
5. **請求路徑（Requested Paths）**：對於每個狀態碼，列出被請求最多的前 3 個路徑
6. **評估（Assessment）**：根據狀態碼分布，對伺服器健康狀況做簡短評估

請把報告寫到 `status_code_report.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應解析全部 1000 筆 JSON 日誌條目，並產生：

**請求總數：** 1000

**狀態碼分布：**
- 200：35（3.5%）
- 206：1（0.1%）
- 304：274（27.4%）
- 403：2（0.2%）
- 404：688（68.8%）

**狀態碼類別：**
- 2xx：36（3.6%）
- 3xx：274（27.4%）
- 4xx：690（69.0%）

**關鍵觀察：**
- 此日誌涵蓋 2015 年 5 月 17 日，約 08:05–16:05 UTC
- 404 錯誤居多——將近占全部請求的 69%
- 路徑主要為 `/downloads/product_1` 與 `/downloads/product_2`
- 大多數流量來自 Debian APT 套件管理工具用戶端
- 80.91.33.133 是最活躍的 IP，約有 210 次請求

可接受的變化：
- 精確百分比可能因四捨五入而不同
- 評估用語會有所不同
- 歡迎額外分析

## Grading Criteria

- [ ] 已在工作區建立 `status_code_report.md`
- [ ] 已回報請求總數（1000）
- [ ] 已列出所有出現過的狀態碼及其計數（200、206、304、403、404）
- [ ] 狀態碼已依類別分組（2xx、3xx、4xx）
- [ ] 已找出產生最多錯誤的 IP

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Nginx status code distribution task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "status_code_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "total_count": 0.0,
            "status_codes_listed": 0.0,
            "categories_grouped": 0.0,
            "top_error_ips": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Total request count
    scores["total_count"] = 1.0 if "1000" in content or "1,000" in content else 0.0

    # Check 2: All status codes listed
    has_200 = "200" in content
    has_304 = "304" in content
    has_404 = "404" in content
    has_403 = "403" in content
    codes_found = sum([has_200, has_304, has_404, has_403])
    scores["status_codes_listed"] = (
        1.0 if codes_found >= 4 else
        0.5 if codes_found >= 3 else 0.0
    )

    # Check 3: Categories grouped
    has_2xx = "2xx" in content or "success" in content
    has_3xx = "3xx" in content or "redirect" in content
    has_4xx = "4xx" in content or "client error" in content
    scores["categories_grouped"] = (
        1.0 if sum([has_2xx, has_3xx, has_4xx]) >= 3 else
        0.5 if sum([has_2xx, has_3xx, has_4xx]) >= 2 else 0.0
    )

    # Check 4: Top error IPs identified
    top_ips = ["80.91.33.133", "5.83.131.103", "202.143.95.26", "50.57.209.92"]
    ips_found = sum(1 for ip in top_ips if ip in content)
    scores["top_error_ips"] = (
        1.0 if ips_found >= 2 else
        0.5 if ips_found >= 1 else 0.0
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
- 已在工作區建立 `status_code_report.md`
- 已回報請求總數（1000）
- 已列出所有出現過的狀態碼及其計數（200、206、304、403、404）
- 狀態碼已依類別分組（2xx、3xx、4xx）
- 已找出產生最多錯誤的 IP
