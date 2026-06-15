---
id: task_log_nginx_slow_requests
name: Nginx 存取日誌 — 找出最大回應
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_log_nginx_slow_requests
source_benchmark: pinchbench
claw_eval_id: P087zh_log_nginx_slow_requests
workspace_files:
- dest: nginx_access.log
  source: logs/nginx_access_json.log
---

# Nginx 存取日誌 — 找出最大回應

## Prompt

請分析位於 `nginx_access.log` 的 Nginx JSON 存取日誌，並找出產生最大回應（以傳輸位元組數計）的請求。每一行都是一個 JSON 物件，欄位有：`time`、`remote_ip`、`remote_user`、`request`、`response`、`bytes`、`referrer`、`agent`。

你的報告應包含：

1. **前 10 大回應（Top 10 Largest Responses）**：列出位元組數最高的請求，包含時間戳記、用戶端 IP、請求路徑、狀態碼與位元組數
2. **位元組分布摘要（Byte Distribution Summary）**：整體統計——傳輸位元組的最小值、最大值、平均數、中位數（排除零位元組回應）
3. **零位元組回應（Zero-Byte Responses）**：零位元組回應的計數，以及哪些狀態碼會產生這類回應
4. **大型回應分析（Large Response Analysis）**：哪些路徑與用戶端 IP 與最大的傳輸相關？
5. **效率評估（Efficiency Assessment）**：有多少百分比的請求造成實際資料傳輸，相對於快取命中（304）？

請把報告寫到 `large_responses_report.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應解析全部 1000 筆 JSON 日誌條目，並產生：

**最大回應：**
- 觀察到的最大位元組數：~3318 位元組
- 最大回應為針對 `/downloads/product_1` 與 `/downloads/product_2` 的 200 OK 回應
- 最高的位元組值包括：3318、3316、3301、2582、2578 等

**零位元組分析：**
- 304 Not Modified 回應全部為 0 位元組（274 筆）
- 404 回應的位元組數很小（通常落在 300-340 範圍）

**效率：**
- 1000 次請求中約有 274 次為 304（快取命中）—— 27.4%
- 帶資料的 200 OK：約 35 次請求 —— 3.5%
- 404 錯誤：688 次請求——這些傳輸的是小型錯誤頁面

可接受的變化：
- 精確的位元組值由日誌決定，具確定性
- 評估用語會有所不同
- 列前 10 名或前 20 名皆可

## Grading Criteria

- [ ] 已在工作區建立 `large_responses_report.md`
- [ ] 已列出最大的回應及其位元組數
- [ ] 已將零位元組／304 回應另外分析
- [ ] 已提供分布統計（最小值、最大值、平均數或中位數）
- [ ] 已找出與最大回應相關的路徑

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Nginx largest responses task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "large_responses_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "top_responses_listed": 0.0,
            "zero_byte_analysis": 0.0,
            "distribution_stats": 0.0,
            "paths_identified": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Top responses listed with byte counts
    has_max_bytes = any(b in content for b in ["3318", "3316", "3301"])
    has_ranking = any(kw in content for kw in ["top", "largest", "biggest", "highest"])
    scores["top_responses_listed"] = (
        1.0 if has_max_bytes and has_ranking else
        0.5 if has_max_bytes else 0.0
    )

    # Check 2: Zero-byte / 304 analysis
    has_zero = "0 byte" in content or "zero byte" in content or "zero-byte" in content or "no data" in content
    has_304 = "304" in content
    scores["zero_byte_analysis"] = (
        1.0 if has_304 and has_zero else
        0.5 if has_304 else 0.0
    )

    # Check 3: Distribution statistics
    stat_keywords = ["min", "max", "mean", "median", "average", "total bytes",
                     "distribution", "range"]
    scores["distribution_stats"] = (
        1.0 if sum(1 for kw in stat_keywords if kw in content) >= 3 else
        0.5 if sum(1 for kw in stat_keywords if kw in content) >= 1 else 0.0
    )

    # Check 4: Paths identified
    has_product_1 = "product_1" in content
    has_product_2 = "product_2" in content
    has_downloads = "downloads" in content or "/download" in content
    scores["paths_identified"] = (
        1.0 if has_product_1 and has_product_2 else
        0.5 if has_downloads else 0.0
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
- 已在工作區建立 `large_responses_report.md`
- 已列出最大的回應及其位元組數
- 已將零位元組／304 回應另外分析
- 已提供分布統計（最小值、最大值、平均數或中位數）
- 已找出與最大回應相關的路徑
