---
id: task_log_nginx_errors
name: Nginx 存取日誌 — 錯誤樣態分析
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_nginx_errors
source_benchmark: pinchbench
claw_eval_id: P089zh_log_nginx_errors
workspace_files:
- dest: nginx_access.log
  source: logs/nginx_access_json.log
---

# Nginx 存取日誌 — 錯誤樣態分析

## Prompt

請分析位於 `nginx_access.log` 的 Nginx JSON 存取日誌，並針對錯誤樣態（4xx 與 5xx 回應）產生一份詳盡報告。每一行都是一個 JSON 物件，欄位有：`time`、`remote_ip`、`remote_user`、`request`、`response`、`bytes`、`referrer`、`agent`。

你的報告應包含：

1. **錯誤概觀（Error Overview）**：錯誤總數、錯誤率（占全部請求的百分比）、依狀態碼的分布
2. **404 分析（404 Analysis）**：哪些路徑回傳 404？這些是合理的資源遺失，還是組態錯誤的路由？
3. **403 分析（403 Analysis）**：什麼被禁止存取，來自哪些 IP？
4. **依用戶端 IP 的錯誤（Error by Client IP）**：哪些 IP 產生最多錯誤？列出前 10 名及計數
5. **依路徑的錯誤（Error by Path）**：哪些請求路徑產生最多錯誤？列出前 10 名及計數
6. **時間樣態（Temporal Pattern）**：錯誤集中在某些時段，還是均勻分布？
7. **修補建議（Remediation Recommendations）**：根據錯誤樣態，提出 3 項具體修正

請把報告寫到 `error_analysis.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應解析全部 1000 筆 JSON 日誌條目，並產生：

**錯誤概觀：**
- 錯誤總數：690（占全部請求的 69.0%）
- 404：688 個錯誤
- 403：2 個錯誤
- 未觀察到 5xx 錯誤

**404 分析：**
- 所有 404 皆指向 `/downloads/product_1` 與 `/downloads/product_2`
- 這些相同路徑在其他時間也回傳 200 與 304
- 這暗示是資源間歇性可用，而非永久遺失檔案

**403 分析：**
- 2 個 forbidden 請求——找出其 IP 與路徑

**主要錯誤 IP：**
- 80.91.33.133 是整體流量最高的 IP，也很可能是產生最多錯誤者
- 其他高頻 IP：5.83.131.103、202.143.95.26、50.57.209.92

**關鍵洞見：**
- 在一台套件下載伺服器上出現極高的 404 率（68.8%）並不尋常
- 套件管理工具會自動重試，因而放大了錯誤數
- 根本原因很可能是下載資源的暫時性不可用

可接受的變化：
- 精確計數具確定性
- 修補建議會有所不同
- 評估深度可有所不同

## Grading Criteria

- [ ] 已在工作區建立 `error_analysis.md`
- [ ] 已提供錯誤率與狀態碼分布（690 個錯誤、69%、404/403 拆分）
- [ ] 已依路徑分析 404 錯誤（/downloads/product_1、/downloads/product_2）
- [ ] 已列出產生最多錯誤的 IP
- [ ] 已提供至少 2 項修補建議

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Nginx error pattern analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "error_analysis.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "error_rate_breakdown": 0.0,
            "path_analysis": 0.0,
            "top_error_ips": 0.0,
            "recommendations": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Error rate and breakdown
    has_total = any(n in content for n in ["690", "688", "69%", "68.8%", "69.0%"])
    has_404 = "404" in content
    has_403 = "403" in content
    scores["error_rate_breakdown"] = (
        1.0 if has_total and has_404 and has_403 else
        0.5 if has_404 and has_total else 0.0
    )

    # Check 2: Path analysis
    has_product_1 = "product_1" in content
    has_product_2 = "product_2" in content
    scores["path_analysis"] = (
        1.0 if has_product_1 and has_product_2 else
        0.5 if has_product_1 or has_product_2 else 0.0
    )

    # Check 3: Top error IPs
    top_ips = ["80.91.33.133", "5.83.131.103", "202.143.95.26", "50.57.209.92"]
    ips_found = sum(1 for ip in top_ips if ip in content)
    scores["top_error_ips"] = (
        1.0 if ips_found >= 3 else
        0.5 if ips_found >= 1 else 0.0
    )

    # Check 4: Recommendations provided
    rec_keywords = ["recommend", "suggestion", "fix", "should", "consider",
                    "implement", "configure", "add", "improve"]
    lines = content.split("\n")
    rec_lines = [l for l in lines if any(kw in l for kw in rec_keywords)]
    scores["recommendations"] = (
        1.0 if len(rec_lines) >= 2 else
        0.5 if len(rec_lines) >= 1 else 0.0
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
- 已在工作區建立 `error_analysis.md`
- 已提供錯誤率與狀態碼分布（690 個錯誤、69%、404/403 拆分）
- 已依路徑分析 404 錯誤（/downloads/product_1、/downloads/product_2）
- 已列出產生最多錯誤的 IP
- 已提供至少 2 項修補建議
