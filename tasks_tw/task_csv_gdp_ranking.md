---
id: task_csv_gdp_ranking
name: 世界 GDP 各國排名
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_gdp_ranking
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T063tw_csv_gdp_ranking
workspace_files:
- source: csvs/world_gdp_2014.csv
  dest: world_gdp_2014.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 世界 GDP 各國排名

## Prompt

我的工作區中有一個 CSV 檔 `world_gdp_2014.csv`，內含全球各國與屬地的 GDP 資料。
該檔有三個欄位：`COUNTRY`、`GDP (BILLIONS)`（單位為美元）與 `CODE`（ISO 國家
代碼）。共有 222 筆。

請分析 GDP 排名，並將你的發現寫入 `gdp_ranking_report.md`。你的報告應包含：

- **前 20 大經濟體**，依 GDP 由高至低排名，附上國名、GDP 數值，以及其佔世界 GDP
  的百分比份額
- **後 10 小經濟體**，由 GDP 最低者往上排名
- **摘要統計**：世界 GDP 總額、平均 GDP、中位數 GDP、最小值與最大值
- **集中度分析**：前 5、前 10 與前 20 大經濟體各佔世界 GDP 總額的百分比
- **「1 兆美元俱樂部」（$1 trillion club）**：列出所有 GDP 超過 1 兆美元的國家
  及其合計佔世界 GDP 的份額
- 一段簡短的**總結段落**，解讀全球 GDP 的分布

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔（222 列）
2. 依 GDP 由高至低排序
3. 找出最大經濟體：United States，$17,420.0B
4. 計算世界 GDP 總額（約 $78,285.45B）
5. 計算各國的百分比份額
6. 計算集中度指標（前 5、前 10、前 20 的份額）
7. 找出 GDP 超過 1 兆美元的 15 個國家
8. 計算摘要統計（平均約 $352.64B、中位數約 $21.52B）
9. 撰寫一份結構良好的 markdown 報告

預期關鍵數值：

- 世界 GDP 總額：約 $78,285.45B
- 第 1：United States（$17,420.0B，約 22.3%）
- 第 2：China（$10,360.0B，約 13.2%）
- 第 3：Japan（$4,770.0B，約 6.1%）
- 第 4：Germany（$3,820.0B，約 4.9%）
- 第 5：France（$2,902.0B，約 3.7%）
- 前 5 份額：約 50.2%
- 前 10 份額：約 64.6%
- 前 20 份額：約 79.2%
- 平均 GDP：約 $352.64B
- 中位數 GDP：約 $21.52B
- $1T+ 俱樂部：15 個國家
- 最小經濟體：Niue（$0.01B）

## Grading Criteria

- [ ] 已建立報告檔 `gdp_ranking_report.md`
- [ ] 正確列出前 20 大經濟體，第 1 為 United States
- [ ] 正確列出後 10 小經濟體，最小為 Niue
- [ ] 摘要統計包含總額、平均、中位數、最小值與最大值
- [ ] 集中度分析呈現前 5、前 10 與前 20 的份額
- [ ] 找出 1 兆美元俱樂部（15 個國家）
- [ ] 排名國家附上百分比份額
- [ ] 含解讀分布的總結段落

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the GDP ranking task.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "gdp_ranking_report.md"
    if not report_path.exists():
        for alt in ["gdp_report.md", "report.md", "ranking_report.md", "gdp_ranking.md", "analysis.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "top_economy": 0.0,
            "bottom_economy": 0.0,
            "summary_stats": 0.0,
            "concentration": 0.0,
            "trillion_club": 0.0,
            "pct_shares": 0.0,
            "summary_paragraph": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check top economy (United States, $17,420B)
    has_us = bool(re.search(r'united\s*states', content_lower))
    has_17420 = bool(re.search(r'17[,.]?420', content))
    scores["top_economy"] = 1.0 if (has_us and has_17420) else (0.5 if has_us or has_17420 else 0.0)

    # Check bottom economy (Niue, $0.01B)
    has_niue = bool(re.search(r'niue', content_lower))
    has_001 = bool(re.search(r'0\.01', content))
    scores["bottom_economy"] = 1.0 if (has_niue and has_001) else (0.5 if has_niue or has_001 else 0.0)

    # Check summary statistics
    stats_found = 0
    if re.search(r'78[,.]?285', content):  # total
        stats_found += 1
    if re.search(r'35[12]\.\d|352\.6', content):  # mean ~352.64
        stats_found += 1
    if re.search(r'21\.5[0-9]', content):  # median ~21.52
        stats_found += 1
    if re.search(r'(?:mean|average|median)', content_lower):
        stats_found += 1
    scores["summary_stats"] = 1.0 if stats_found >= 3 else (0.5 if stats_found >= 2 else 0.0)

    # Check concentration analysis
    conc_found = 0
    if re.search(r'(?:top\s*5|five).*(?:50|49|51)\s*[\.\d]*%', content_lower):
        conc_found += 1
    if re.search(r'(?:top\s*10|ten).*(?:64|65)\s*[\.\d]*%', content_lower):
        conc_found += 1
    if re.search(r'(?:top\s*20|twenty).*(?:79|80)\s*[\.\d]*%', content_lower):
        conc_found += 1
    # Also accept the numbers without the "top N" prefix nearby
    if re.search(r'50\.?[12]%', content):
        conc_found += 1
    if re.search(r'64\.?[56]%', content):
        conc_found += 1
    if re.search(r'79\.?[12]%', content):
        conc_found += 1
    scores["concentration"] = 1.0 if conc_found >= 3 else (0.5 if conc_found >= 1 else 0.0)

    # Check $1 trillion club
    has_trillion = bool(re.search(r'(?:trillion|1[,.]?000|\$1t|\$1,000)', content_lower))
    has_15 = bool(re.search(r'(?:15|fifteen)\s*(?:countries|economies|nations|members)', content_lower))
    scores["trillion_club"] = 1.0 if (has_trillion and has_15) else (0.5 if has_trillion else 0.0)

    # Check percentage shares present
    pct_patterns = [r'22\.?[23]%', r'13\.?[23]%', r'6\.?[01]%']  # US, China, Japan shares
    pct_found = sum(1 for p in pct_patterns if re.search(p, content))
    scores["pct_shares"] = 1.0 if pct_found >= 2 else (0.5 if pct_found >= 1 else 0.0)

    # Check for summary/interpretation paragraph
    summary_patterns = [
        r'(?:concentrat|dominat|inequal|dispar|skew)',
        r'(?:united states|u\.?s\.?).*(?:largest|dominant|leading)',
        r'(?:median|mean).*(?:gap|difference|disparity|skew)',
    ]
    summary_found = sum(1 for p in summary_patterns if re.search(p, content_lower))
    scores["summary_paragraph"] = 1.0 if summary_found >= 2 else (0.5 if summary_found >= 1 else 0.0)

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

### 評分項 1：資料正確性（權重 35%）

**1.0 分**：所有排名皆正確，統計符合預期值（總額約 $78,285B、平均約 $353B、
中位數約 $21.5B），且百分比份額準確計算。
**0.75 分**：排名與統計大致正確，僅有小幅四捨五入差異。
**0.5 分**：頂端經濟體正確，但統計或較後排名有錯誤。
**0.25 分**：排名或統計有數個重大錯誤。
**0.0 分**：未嘗試分析或根本性錯誤。

### 評分項 2：分析深度（權重 30%）

**1.0 分**：對 GDP 集中度提供具意義的解讀（平均與中位數間巨大差距反映極端偏態），
討論美中主導地位，指出多數經濟體規模偏小，並為 $1T 俱樂部提供脈絡。
**0.75 分**：解讀良好，僅有小缺漏。
**0.5 分**：陳述事實，但解讀或洞見有限。
**0.25 分**：除列出數字外幾無分析。
**0.0 分**：未提供任何分析或解讀。

### 評分項 3：報告完整性（權重 20%）

**1.0 分**：所有要求章節皆齊備：前 20、後 10、摘要統計、集中度分析、$1T 俱樂部、
總結段落。
**0.75 分**：多數章節齊備，僅有一處小缺漏。
**0.5 分**：缺少數個章節。
**0.25 分**：僅有一、兩個章節。
**0.0 分**：報告缺漏或為空。

### 評分項 4：呈現品質（權重 15%）

**1.0 分**：markdown 排版良好，以表格呈現排名，標題清楚、版面有條理。百分比份額
清楚顯示於 GDP 數值旁。
**0.75 分**：排版良好，僅有小問題。
**0.5 分**：可讀但組織不佳。
**0.25 分**：不易閱讀。
**0.0 分**：無報告或無法閱讀。
