---
id: task_log_apache_timeline
name: Apache 錯誤日誌 — 建立錯誤時間軸
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_apache_timeline
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T083tw_log_apache_timeline
workspace_files:
- dest: apache_error.log
  source: logs/apache_error.log
---

# Apache 錯誤日誌 — 建立錯誤時間軸

## Prompt

請分析位於 `apache_error.log` 的 Apache 錯誤日誌，並建立一份重要事件的時間軸。此日誌涵蓋 2005 年 6 月 9 日（星期四）至 6 月 16 日（星期四）。

對於每一天，請找出：

1. error 等級條目的數量
2. 值得注意的事件（伺服器重啟、攻擊爆發、異常活動高峰）
3. 任何活動集中的時段（短時間內出現大量錯誤）

此外，請找出整份日誌中**單一最劇烈的活動爆發**——也就是包含最多錯誤條目的最短時間窗——並描述該爆發期間發生了什麼。

請把你的發現寫到 `error_timeline.json`，採用如下結構：

```json
{
  "date_range": "2005-06-09 to 2005-06-16",
  "daily_summary": [
    {
      "date": "2005-06-09",
      "day_of_week": "Thursday",
      "error_count": 50,
      "notable_events": ["Description of what happened"]
    }
  ],
  "peak_burst": {
    "start_time": "2005-06-11 03:03:03",
    "end_time": "2005-06-11 03:04:02",
    "duration_seconds": 59,
    "error_count": 150,
    "description": "What caused this burst"
  }
}
```

## Expected Behavior

助手應解析時間戳記並依日分組條目。預期的每日分布（約略）：

| 日期 | 星期 | 錯誤數 | 值得注意的事件 |
|---|---|---|---|
| Jun 9 | Thu | ~50 | 伺服器啟動、JK connector 錯誤、目錄掃描開始 |
| Jun 10 | Fri | ~80 | 11:32 伺服器重啟、IIS 蠕蟲探測（Invalid method）、210.22.201.x 子網掃描 |
| Jun 11 | Sat | ~350+ | 03:03 來自 202.133.98.6 的**大規模爆發**（awstats 掃描導致 scoreboard 耗盡與 mod_jk2 關閉）、IIS 蠕蟲探測持續 |
| Jun 12 | Sun | ~100 | 04:04 平順重啟（graceful restart）、210.91.137.35 探測 _vti_bin、URI too long 攻擊 |
| Jun 13 | Mon | ~90 | 195.23.79.241 大規模掃描（~22 條錯誤）、218.68.233.47 掃描、218.82.188.130 掃描 |
| Jun 14 | Tue | ~80 | 81.214.165.213 探測 _vti_bin（23 次請求）、60.191.134.226 大規模掃描（19 次請求） |
| Jun 15 | Wed | ~50 | 219.133.247.159 掃描（18 次請求）、URI too long 攻擊、一般目錄掃描 |
| Jun 16 | Thu | ~3 | 僅 2-3 條條目（日誌可能在當天稍早即截斷） |

**最高峰爆發**為 6 月 11 日（星期六）來自 202.133.98.6 的 awstats 掃描，約於 03:03:03 開始，在 10 分鐘內產生約 150+ 條錯誤條目。此爆發極為劇烈，導致 Apache 衍生（spawn）大量新的子處理程序（從 jk2_init scoreboard 插槽訊息可見），並引發一連串 mod_jk2 關閉。

可接受的變化：
- 視邊界處理方式而定，每日計數可能有 ±15 的差異
- 最高峰爆發的辨識為關鍵洞見——時間與 IP 應吻合
- 星期標籤可省略

## Grading Criteria

- [ ] 已在工作區建立 `error_timeline.json`
- [ ] 每日分布涵蓋 8 天中至少 5 天，並附錯誤數
- [ ] 已將 6 月 11 日（星期六）判定為錯誤最多的一天
- [ ] 已將最高峰爆發歸因於 6 月 11 日約 03:03 來自 202.133.98.6 或 awstats 的掃描
- [ ] 已記錄伺服器重啟事件（Jun 9、Jun 10、Jun 12 啟動中至少一項）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Apache error log timeline task."""
    from pathlib import Path
    import json

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "error_timeline.json"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "daily_breakdown": 0.0,
            "peak_day_identified": 0.0,
            "peak_burst_identified": 0.0,
            "server_restarts_noted": 0.0,
        }

    scores["output_created"] = 1.0

    try:
        data = json.loads(report_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return {
            "output_created": 1.0,
            "daily_breakdown": 0.0,
            "peak_day_identified": 0.0,
            "peak_burst_identified": 0.0,
            "server_restarts_noted": 0.0,
        }

    full_text = json.dumps(data).lower()

    # Check 1: Daily breakdown with at least 5 days
    daily = data.get("daily_summary", [])
    if not isinstance(daily, list):
        daily = []
    days_with_counts = sum(
        1 for d in daily
        if isinstance(d, dict) and isinstance(d.get("error_count"), (int, float)) and d.get("error_count", 0) > 0
    )
    scores["daily_breakdown"] = (
        1.0 if days_with_counts >= 5 else
        0.5 if days_with_counts >= 3 else 0.0
    )

    # Check 2: June 11 identified as peak day
    jun11_found = False
    max_count = 0
    max_date = ""
    for d in daily:
        if not isinstance(d, dict):
            continue
        date_str = str(d.get("date", ""))
        count = d.get("error_count", 0)
        if isinstance(count, (int, float)) and count > max_count:
            max_count = count
            max_date = date_str
        if "06-11" in date_str or "jun 11" in date_str.lower():
            jun11_found = True

    scores["peak_day_identified"] = (
        1.0 if ("06-11" in max_date or "jun 11" in max_date.lower()) else
        0.5 if jun11_found else 0.0
    )

    # Check 3: Peak burst identified (202.133.98.6 or awstats on Jun 11 ~03:03)
    burst = data.get("peak_burst", {})
    burst_text = json.dumps(burst).lower() if isinstance(burst, dict) else full_text
    has_burst_ip = "202.133.98.6" in burst_text
    has_burst_awstats = "awstats" in burst_text
    has_burst_time = any(t in burst_text for t in ["03:03", "jun 11", "06-11", "saturday"])
    scores["peak_burst_identified"] = (
        1.0 if (has_burst_ip or has_burst_awstats) and has_burst_time else
        0.5 if has_burst_ip or has_burst_awstats else 0.0
    )

    # Check 4: Server restarts noted
    restart_keywords = ["restart", "startup", "configured -- resuming", "startup",
                        "graceful", "resuming normal operations"]
    scores["server_restarts_noted"] = (
        1.0 if any(kw in full_text for kw in restart_keywords) else 0.0
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
- 已在工作區建立 `error_timeline.json`
- 每日分布涵蓋 8 天中至少 5 天，並附錯誤數
- 已將 6 月 11 日（星期六）判定為錯誤最多的一天
- 已將最高峰爆發歸因於 6 月 11 日約 03:03 來自 202.133.98.6 或 awstats 的掃描
- 已記錄伺服器重啟事件（Jun 9、Jun 10、Jun 12 啟動中至少一項）
