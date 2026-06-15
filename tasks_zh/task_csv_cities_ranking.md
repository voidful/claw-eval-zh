---
id: task_csv_cities_ranking
name: 美國城市人口排名
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_cities_ranking
source_benchmark: pinchbench
claw_eval_id: P072zh_csv_cities_ranking
workspace_files:
- source: csvs/us_cities_top1000.csv
  dest: us_cities_top1000.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 美國城市人口排名

## Prompt

我的工作區裡有一個 CSV 檔案 `us_cities_top1000.csv`，內含美國人口最多的 1,000 個城市的資料。檔案欄位有：`City`、`State`、`Population`、`lat`、`lon`。

請分析人口排名，並把你的發現寫到名為 `cities_ranking_report.md` 的檔案。你的報告應包含：

- **人口前 10 大城市（top 10 cities）**：附上所屬州別與確切人口
- **資料集中人口最少的 10 個城市（bottom 10 cities）**（即前 1,000 大中最小的）
- 全部 1,000 個城市的**總人口（total population）**
- 人口的**平均值與中位數（mean and median）**
- 依該州在資料集中各城市人口加總排名的**人口前 10 大州（top 10 states）**，包含各州的城市數
- **人口分布（population distribution）**：有多少城市落在下列各區間：<50k、50k-100k、100k-250k、250k-500k、500k-1M、>1M

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案（1,000 列資料、5 個欄位）
2. 依人口排序城市以找出排名
3. 計算彙總統計
4. 依州分組以進行州級排名
5. 建立人口分布區間
6. 撰寫一份結構清晰的 markdown 報告

關鍵預期數值：

- 第 1 名城市：New York, New York — 8,405,837
- 第 2 名：Los Angeles, California — 3,884,307
- 第 3 名：Chicago, Illinois — 2,718,782
- 第 4 名：Houston, Texas — 2,195,914
- 第 5 名：Philadelphia, Pennsylvania — 1,553,165
- 資料集中最小的城市：Panama City, Florida — 36,877
- 總人口：131,132,443
- 平均人口：~131,132
- 中位數人口：~68,224
- 人口加總最高的州：California（212 個城市，27,910,620）
- 人口 > 1M 的城市：10 個
- 人口 >= 500k 的城市：34 個

## Grading Criteria

- [ ] 已建立報告檔案 `cities_ranking_report.md`
- [ ] 正確列出人口前 10 大城市，且 New York 為第 1 名
- [ ] 列出人口最少的 10 個城市，且 Panama City, FL 為最小者
- [ ] 正確回報總人口（~131,132,443）
- [ ] 正確計算平均人口（~131,132）
- [ ] 正確計算中位數人口（~68,224）
- [ ] 列出人口加總最高的州，且 California 為第 1 名
- [ ] 已包含人口分布區間
- [ ] 報告結構清晰、分區明確

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the US cities population ranking task.

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

    report_path = workspace / "cities_ranking_report.md"
    if not report_path.exists():
        for alt in ["ranking_report.md", "report.md", "cities_report.md", "population_ranking.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "top_10_cities": 0.0,
            "bottom_10_cities": 0.0,
            "total_population": 0.0,
            "mean_population": 0.0,
            "median_population": 0.0,
            "state_rankings": 0.0,
            "distribution_brackets": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Top 10 cities — check for the top 5 at minimum
    top_cities = ["new york", "los angeles", "chicago", "houston", "philadelphia"]
    found_top = sum(1 for c in top_cities if c in content_lower)
    scores["top_10_cities"] = 1.0 if found_top >= 5 else (0.5 if found_top >= 3 else 0.0)

    # Bottom 10 — check for Panama City as smallest
    scores["bottom_10_cities"] = 1.0 if "panama city" in content_lower else 0.0

    # Total population (~131,132,443)
    total_patterns = [r'131[,.]?132[,.]?443', r'131[,.]?132[,.]?4', r'131\.1\s*million']
    scores["total_population"] = 1.0 if any(re.search(p, content) for p in total_patterns) else 0.0

    # Mean population (~131,132)
    mean_patterns = [r'131[,.]?132(?!\d{3})', r'131[,.]?1\d{2}(?!\d{3})']
    scores["mean_population"] = 1.0 if any(re.search(p, content) for p in mean_patterns) else 0.0

    # Median population (~68,224)
    median_patterns = [r'68[,.]?2[12]\d', r'68[,.]?224', r'68[,.]?225', r'68[,.]?223']
    scores["median_population"] = 1.0 if any(re.search(p, content) for p in median_patterns) else 0.0

    # State rankings — California should be #1
    california_patterns = [
        r'california.*(?:1st|#1|first|top|highest|most)',
        r'(?:1st|#1|first|top|highest).*california',
        r'california.*212.*cit',
        r'california.*27[,.]?910',
    ]
    scores["state_rankings"] = 1.0 if any(re.search(p, content_lower) for p in california_patterns) else 0.0

    # Distribution brackets
    bracket_keywords = ["50k", "100k", "250k", "500k", "1m", "million",
                        "50,000", "100,000", "250,000", "500,000", "1,000,000",
                        "bracket", "distribution", "range", "bin"]
    bracket_count = sum(1 for k in bracket_keywords if k in content_lower)
    scores["distribution_brackets"] = 1.0 if bracket_count >= 3 else (0.5 if bracket_count >= 1 else 0.0)

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

- 1.0：所有排名、總計、平均值、中位數與州級彙總皆數值正確。
- 0.75：多數數值正確，僅有一兩處小幅數值錯誤。
- 0.5：部分數值正確，但有多項關鍵數字錯誤。
- 0.25：多項指標有重大計算錯誤。
- 0.0：沒有正確計算，或未進行分析。

### 評分項 2：完整性（權重 30%）

- 1.0：所有要求的元素皆具備：前 10、後 10、總計／平均／中位數、州級排名、分布區間。
- 0.75：多數元素具備，僅有一處小幅缺漏。
- 0.5：有多項要求的元素缺漏。
- 0.25：只有少數元素。
- 0.0：報告缺漏或幾乎空白。

### 評分項 3：報告品質（權重 20%）

- 1.0：markdown 組織良好，分區清楚，排名以表格呈現，流程合理。
- 0.75：組織良好、易讀，僅有小幅排版問題。
- 0.5：有分析但組織不佳。
- 0.25：雜亂或不易閱讀。
- 0.0：沒有報告或無法使用。

### 評分項 4：洞見品質（權重 15%）

- 1.0：超越原始數字，指出模式——例如 California 的主導地位、第 1 名與第 2 名之間的巨大差距、小型城市的長尾現象。
- 0.75：對資料中的模式有一些觀察。
- 0.5：大多是原始數字，詮釋極少。
- 0.25：純數字、無評論。
- 0.0：沒有進行分析。
