---
id: task_csv_stock_best_worst
name: 台積電（2330）2024 最佳與最差交易日
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_stock_best_worst
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: fixture_replace
claw_eval_tw_id: T055tw_csv_stock_best_worst
workspace_files:
- source: tw/csvs/tw_stock_2330_2024.csv
  dest: tw_stock_2330_2024.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 台積電（2330）2024 最佳與最差交易日

## Prompt

我的工作區裡有一個 CSV 檔案 tw_stock_2330_2024.csv，內含台積電（2330）2024 年的
每日收盤價（來源：TWSE 公開資料）。檔案有兩欄：date（日期）與 close（收盤價，NT$），
共 242 個交易日。

請找出台積電 2024 年表現最好與最差的交易日，並把結果寫入 best_worst_days_report.md。
報告需包含：

- **單日漲幅最大的交易日**（依收盤對收盤的日報酬率）與其日期、漲幅
- **單日跌幅最大的交易日**與其日期、跌幅
- **全年最高與最低收盤價**及其日期
- 一段簡短的**分析與總結**

注意：CSV 檔名、欄名與報告檔名 best_worst_days_report.md 不可更改。

## Expected Behavior

助手應找出（已由程式從 TWSE 真實資料驗算）：
- 單日最大漲幅約 +7.98%，發生於 2024-08-06
- 單日最大跌幅約 -9.75%，發生於 2024-08-05
- 全年最高收盤價 NT$1,090.00（2024-11-08）、最低 NT$576.00（2024-01-05）
並輸出結構清晰的 markdown 報告與簡短分析。

## Grading Criteria

- [ ] 建立報告檔案 best_worst_days_report.md
- [ ] 找出單日最大漲幅交易日（2024-08-06）
- [ ] 報告最大漲幅數值（約 +7.98%）
- [ ] 找出單日最大跌幅交易日（2024-08-05）
- [ ] 報告最大跌幅數值（約 -9.75%）
- [ ] 報告全年最高（NT$1,090）與最低（NT$576）收盤價
- [ ] 含分析或總結

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """2330 best/worst-day grader. Values recomputed from real TWSE fixture."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    report = workspace / "best_worst_days_report.md"
    if not report.exists():
        for alt in ["best_worst_report.md", "best_worst.md", "report.md",
                    "best_worst_days.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in ["report_created", "best_day_date", "best_day_value",
                                 "worst_day_date", "worst_day_value", "extremes",
                                 "summary_analysis"]}
    scores = {"report_created": 1.0}
    content = report.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()
    scores["best_day_date"] = 1.0 if ('2024-08-06' in content or re.search(r'8月\s*6', content)) else 0.0
    scores["best_day_value"] = 1.0 if re.search(r'7\.9[78]', content) else 0.0
    scores["worst_day_date"] = 1.0 if ('2024-08-05' in content or re.search(r'8月\s*5', content)) else 0.0
    scores["worst_day_value"] = 1.0 if re.search(r'9\.7[45]', content) else 0.0
    ext = sum(1 for p in [r'1[,]?090', r'576'] if re.search(p, content))
    scores["extremes"] = 1.0 if ext >= 2 else (0.5 if ext == 1 else 0.0)
    sm = [r'分析', r'總結', r'总结', r'摘要', r'summary', r'群聚', r'cluster']
    scores["summary_analysis"] = 1.0 if any(re.search(p, cl) for p in sm) else 0.0
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

### 評分項 1：日期與數值準確度（權重 60%）
- 1.0：最佳/最差日的日期與漲跌幅、最高/最低收盤價皆正確
- 0.5：部分正確
- 0.0：未正確找出
### 評分項 2：分析品質（權重 20%）
- 1.0：合理分析（如極端日成因或群聚）
- 0.0：無分析
### 評分項 3：報告結構（權重 20%）
- 1.0：markdown 清楚
- 0.0：缺失
