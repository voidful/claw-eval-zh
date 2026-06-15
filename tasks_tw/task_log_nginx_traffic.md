---
id: task_log_nginx_traffic
name: Nginx 存取日誌 — 依時間的流量樣態
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_nginx_traffic
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T086tw_log_nginx_traffic
workspace_files:
- dest: nginx_access.log
  source: logs/nginx_access_json.log
---

# Nginx 存取日誌 — 依時間的流量樣態

## Prompt

請分析位於 `nginx_access.log` 的 Nginx JSON 存取日誌，並產生一份隨時間變化的流量樣態報告。每一行都是一個 JSON 物件，欄位有：`time`、`remote_ip`、`remote_user`、`request`、`response`、`bytes`、`referrer`、`agent`。

你的報告應包含：

1. **時間範圍（Time Range）**：日誌涵蓋的完整日期／時間範圍
2. **每小時流量分布（Hourly Traffic Breakdown）**：每小時的請求數
3. **流量高峰與低谷（Peak and Low Traffic）**：找出最繁忙與最清閒的時段
4. **隨時間的頻寬（Bandwidth Over Time）**：每小時傳輸的總位元組數
5. **請求速率趨勢（Request Rate Trends）**：請求是平穩、突發，還是呈現某種趨勢？
6. **各 IP 隨時間的活動（Per-IP Activity Over Time）**：找出跨多個小時出現的 IP，以及只在突發時段出現的 IP

請把報告寫到 `traffic_report.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應解析全部 1000 筆 JSON 日誌條目，並產生：

**時間範圍：** 2015 年 5 月 17 日，08:05:01 至 16:05:10 UTC（約 8 小時）

**每小時分布（約略）：**
- 08:xx —— 日誌從該小時中途開始
- 流量分布於這 8 小時的時間窗中
- 日誌包含時間戳記介於 08:05 與 16:05 之間的條目

**關鍵觀察：**
- 此期間共有 73 個不重複用戶端 IP
- 80.91.33.133 是最持續的用戶端（約 210 次請求，分散於整段時間範圍）
- 大多數流量為 Debian APT 套件管理工具流量（自動更新）
- 傳輸位元組數不一——304（Not Modified）回應為 0 位元組；200 回應最高可達約 3318 位元組
- 此伺服器看來是一台軟體下載／儲存庫鏡像站

可接受的變化：
- 視解析方式而定，每小時計數可能有所不同
- 任何合理的分箱方式（每小時、每 30 分鐘等）皆可接受
- 趨勢分析用語會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `traffic_report.md`
- [ ] 已找出時間範圍（2015 年 5 月 17 日；約 08:05–16:05 UTC）
- [ ] 流量已依時段分解（每小時或類似方式）
- [ ] 已找出流量高峰／最繁忙時段
- [ ] 已分析頻寬或傳輸位元組數

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Nginx traffic patterns task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "traffic_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "time_range": 0.0,
            "hourly_breakdown": 0.0,
            "peak_identified": 0.0,
            "bandwidth_analysis": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Time range identified
    has_date = any(d in content for d in ["may 17", "2015-05-17", "17/may/2015", "may 2015"])
    has_range = any(t in content for t in ["08:05", "16:05", "8 hour", "eight hour"])
    scores["time_range"] = (
        1.0 if has_date and has_range else
        0.5 if has_date else 0.0
    )

    # Check 2: Traffic broken down by time period
    time_keywords = ["hour", "period", "interval", "08:", "09:", "10:", "11:", "12:",
                     "13:", "14:", "15:", "16:"]
    time_sections = sum(1 for kw in time_keywords if kw in content)
    scores["hourly_breakdown"] = (
        1.0 if time_sections >= 4 else
        0.5 if time_sections >= 2 else 0.0
    )

    # Check 3: Peak/busiest periods identified
    peak_keywords = ["peak", "busiest", "highest", "most active", "maximum",
                     "lowest", "quietest", "least"]
    scores["peak_identified"] = (
        1.0 if sum(1 for kw in peak_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in peak_keywords if kw in content) >= 1 else 0.0
    )

    # Check 4: Bandwidth/bytes analysis
    bandwidth_keywords = ["bytes", "bandwidth", "transfer", "data", "0 bytes",
                          "304", "not modified"]
    scores["bandwidth_analysis"] = (
        1.0 if sum(1 for kw in bandwidth_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in bandwidth_keywords if kw in content) >= 1 else 0.0
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
- 已在工作區建立 `traffic_report.md`
- 已找出時間範圍（2015 年 5 月 17 日；約 08:05–16:05 UTC）
- 流量已依時段分解（每小時或類似方式）
- 已找出流量高峰／最繁忙時段
- 已分析頻寬或傳輸位元組數
