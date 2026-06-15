---
id: task_csv_iris_summary
name: 鳶尾花統計摘要
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_iris_summary
source_benchmark: pinchbench
claw_eval_id: P069zh_csv_iris_summary
workspace_files:
- source: csvs/iris_flowers.csv
  dest: iris_flowers.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 鳶尾花統計摘要

## Prompt

我的工作區裡有一個 CSV 檔案 `iris_flowers.csv`，內含經典的鳶尾花（Iris）資料集。它有 150 列、5 個欄位：`SepalLength`、`SepalWidth`、`PetalLength`、`PetalWidth`，以及 `Name`（物種）。

請計算統計摘要並寫到 `iris_summary.md`。你的報告應包含：

- **資料集概覽（dataset overview）**：總列數、欄位數，以及三個物種名稱與各自的數量
- 每個數值欄位的**整體統計（overall statistics）**：平均值（mean）、中位數（median）、標準差（standard deviation）、最小值（min）、最大值（max）
- **各物種統計（per-species statistics）**：依物種分組，計算每個數值欄位的平均值與標準差
- **相關性洞見（correlation insight）**：哪一對數值特徵之間的線性相關最強，這代表什麼意義
- 一個簡短的**關鍵發現（key findings）**區段，點出資料中最值得注意的模式

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案
2. 確認共 150 列、三個物種（Iris-setosa、Iris-versicolor、Iris-virginica），各 50 列
3. 計算整體統計：
   - SepalLength：mean≈5.84、median=5.80、stdev≈0.83、min=4.3、max=7.9
   - SepalWidth：mean≈3.05、median=3.00、stdev≈0.43、min=2.0、max=4.4
   - PetalLength：mean≈3.76、median=4.35、stdev≈1.76、min=1.0、max=6.9
   - PetalWidth：mean≈1.20、median=1.30、stdev≈0.76、min=0.1、max=2.5
4. 計算各物種平均值（例如 setosa PetalLength mean≈1.46、virginica PetalLength mean≈5.55）
5. 指出 PetalLength 與 PetalWidth 之間的相關性最強
6. 注意到 setosa 可依花瓣量測值清楚與其他兩個物種區分
7. 撰寫一份結構清晰的 markdown 報告

關鍵預期數值：

- 150 列、3 個物種、各 50 列
- 整體 SepalLength 平均值：~5.84
- 整體 PetalLength 平均值：~3.76
- Setosa PetalLength 平均值：~1.46
- Virginica PetalLength 平均值：~5.55
- 相關性最強：PetalLength–PetalWidth

## Grading Criteria

- [ ] 已建立報告檔案 `iris_summary.md`
- [ ] 資料集概覽：正確說明 150 列、3 個物種、各 50 列
- [ ] 每個數值欄位都有報告整體 mean、median、stdev、min、max
- [ ] 每個數值欄位都有報告各物種統計（至少平均值）
- [ ] 已指出相關性最強者（PetalLength–PetalWidth）
- [ ] 關鍵發現：setosa 可依花瓣量測值與 versicolor/virginica 區分
- [ ] 報告結構清晰、有 markdown 排版

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the Iris statistical summary task.

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

    # Check if report exists
    report_path = workspace / "iris_summary.md"
    if not report_path.exists():
        alternatives = ["summary.md", "report.md", "iris_report.md", "iris_statistics.md", "iris_analysis.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "dataset_overview": 0.0,
            "overall_stats": 0.0,
            "per_species_stats": 0.0,
            "correlation": 0.0,
            "separability_insight": 0.0,
            "formatting": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check dataset overview (150 rows, 3 species, 50 each)
    has_150 = bool(re.search(r'150', content))
    has_3_species = bool(re.search(r'(?:three|3)\s*(?:species|class)', content_lower))
    has_50_each = bool(re.search(r'50\s*(?:each|samples|rows|per|observations)', content_lower))
    species_names = sum(1 for s in ['setosa', 'versicolor', 'virginica'] if s in content_lower)
    overview_score = 0.0
    if has_150:
        overview_score += 0.25
    if has_3_species or species_names >= 3:
        overview_score += 0.25
    if has_50_each:
        overview_score += 0.25
    if species_names >= 3:
        overview_score += 0.25
    scores["dataset_overview"] = overview_score

    # Check overall statistics (means for key columns)
    stats_score = 0.0
    if re.search(r'5\.8[0-9]', content):  # SepalLength mean ~5.84
        stats_score += 0.25
    if re.search(r'3\.0[0-9]', content):  # SepalWidth mean ~3.05
        stats_score += 0.25
    if re.search(r'3\.7[56]', content):  # PetalLength mean ~3.76
        stats_score += 0.25
    if re.search(r'1\.1[89]|1\.20', content):  # PetalWidth mean ~1.20
        stats_score += 0.25
    scores["overall_stats"] = stats_score

    # Check per-species statistics
    species_score = 0.0
    # Setosa PetalLength mean ~1.46
    if re.search(r'1\.46', content):
        species_score += 0.34
    # Versicolor PetalLength mean ~4.26
    if re.search(r'4\.26', content):
        species_score += 0.33
    # Virginica PetalLength mean ~5.55
    if re.search(r'5\.5[45]', content):
        species_score += 0.33
    scores["per_species_stats"] = min(species_score, 1.0)

    # Check correlation identification
    corr_patterns = [
        r'petal\s*length.*petal\s*width.*corr',
        r'corr.*petal\s*length.*petal\s*width',
        r'petal\s*width.*petal\s*length.*corr',
        r'strongest.*corr.*petal',
        r'high(?:est|ly)?\s*corr.*petal',
        r'petal.*strong.*corr',
    ]
    scores["correlation"] = 1.0 if any(re.search(p, content_lower) for p in corr_patterns) else 0.0

    # Check separability insight
    sep_patterns = [
        r'setosa.*(?:separab|distinct|clearly\s*different|easily\s*distinguish|linearly\s*separab)',
        r'(?:separab|distinct|clearly\s*different|easily\s*distinguish).*setosa',
        r'setosa.*(?:smaller|shorter)\s*petal',
        r'petal.*(?:separate|distinguish|differentiate).*setosa',
    ]
    scores["separability_insight"] = 1.0 if any(re.search(p, content_lower) for p in sep_patterns) else 0.0

    # Check formatting (headers, tables or structured data)
    has_headers = len(re.findall(r'^#{1,3}\s+', content, re.MULTILINE)) >= 3
    has_table = bool(re.search(r'\|.*\|.*\|', content))
    has_lists = len(re.findall(r'^[\s]*[-*]\s+', content, re.MULTILINE)) >= 3
    fmt_score = 0.0
    if has_headers:
        fmt_score += 0.5
    if has_table or has_lists:
        fmt_score += 0.5
    scores["formatting"] = fmt_score

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

### 評分項 1：統計正確性（權重 35%）

- 1.0：所有統計值（mean、median、stdev、min/max）在整體與各物種層級皆數值正確。
- 0.75：多數統計正確，僅有一兩處小幅四捨五入差異。
- 0.5：部分統計正確，但有多項關鍵數值錯誤或缺漏。
- 0.25：僅少數統計正確，存在重大計算錯誤。
- 0.0：沒有正確統計，或未進行分析。

### 評分項 2：分析洞見（權重 30%）

- 1.0：正確指出 PetalLength–PetalWidth 相關性最強，注意到 setosa 的可分性，並對資料模式做出有意義的詮釋。
- 0.75：指出關鍵相關性與物種差異，有合理的細節。
- 0.5：提到相關性或物種差異，但分析淺薄或部分有誤。
- 0.25：洞見模糊或不正確。
- 0.0：沒有提供洞見，或分析完全錯誤。

### 評分項 3：報告結構與呈現（權重 20%）

- 1.0：markdown 組織良好，分區清楚，統計以表格呈現，且從概覽到細部分析再到關鍵發現流程合理。
- 0.75：組織良好、易讀，僅有小幅排版問題。
- 0.5：有分析，但組織不佳、不易閱讀。
- 0.25：雜亂或缺少主要區段。
- 0.0：沒有報告，或空白／無法使用。

### 評分項 4：完整性（權重 15%）

- 1.0：所有要求的元素皆具備：概覽、整體統計、各物種統計、相關性、關鍵發現。
- 0.75：多數元素具備，僅有一兩處小幅缺漏。
- 0.5：有多項要求的元素缺漏。
- 0.25：只有少數元素。
- 0.0：報告缺漏或幾乎空白。
