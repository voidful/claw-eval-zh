---
id: task_csv_cities_density
name: 美國城市各州人口集中度
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_cities_density
source_benchmark: pinchbench
claw_eval_id: P074zh_csv_cities_density
workspace_files:
- source: csvs/us_cities_top1000.csv
  dest: us_cities_top1000.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 美國城市各州人口集中度

## Prompt

我的工作區裡有一個 CSV 檔案 `us_cities_top1000.csv`，內含美國人口最多的 1,000 個城市的資料。檔案欄位有：`City`、`State`、`Population`、`lat`、`lon`。

請分析各州之間的人口集中（population concentration）模式，並把你的發現寫到 `cities_density_report.md`。你的報告應包含：

1. **各州人口集中度（population concentration by state）**：對每個州計算每城市平均人口（該州在資料集中的總人口 ÷ 城市數）。依此指標將各州排名，並列出前 10 與後 10。

2. **單一城市主導（single-city dominance）**：對於有 5 個（含）以上城市的州，計算該州在資料集中最大城市占該州總人口的百分比。找出最大城市主導程度最高的前 5 個州。

3. **州代表性（state representation）**：資料集中出現了多少個不同的州（加上 DC）？哪些州在資料集中的城市最多、哪些最少（只有 1 或 2 個）？

4. **州內人口不均（population inequality within states）**：對於有 10 個（含）以上城市的州，計算最大城市人口與最小城市人口的比值。哪些州的城市規模分布最均、哪些最不均？

5. **區域摘要（regional summary）**：將各州分組為區域（Northeast、Southeast、Midwest、West），比較各區域的總人口、城市數與平均城市規模。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案
2. 依州分組並計算各州指標
3. 計算集中度比值與主導百分比
4. 找出州內各城市人口分布的模式
5. 建立區域分組與比較

關鍵預期數值：

- 不同的州／領地：48 個（47 州 + DC）
- 每城市平均人口最高：DC（646,449 — 僅 1 個城市），其次 New York（584,314，17 個城市）
- 每城市平均人口最低：Vermont（42,284 — 1 個城市）、West Virginia（~50,000，2 個城市）
- 城市最多：California（212）、Texas（83）、Florida（73）
- 只有 1 個城市的州：DC、Hawaii、Alaska、Vermont、Maine（依確切計數而定）
- California 最大城市（LA 3,884,307）約占 CA 資料集總人口（27,910,620）的 13.9%
- New York 州：NYC（8,405,837）約占該州資料集總計（9,933,332）的 84.6% — 極端主導

## Grading Criteria

- [ ] 已建立報告檔案 `cities_density_report.md`
- [ ] 已計算每城市平均人口並依州排名
- [ ] 已指出 New York 州集中度高（NYC 主導）
- [ ] 已為符合資格的州計算單一城市主導百分比
- [ ] 正確回報不同的州／領地數量（~48）
- [ ] 已指出城市最少的州
- [ ] 已為符合資格的州計算人口不均比值
- [ ] 已建立區域分組並比較
- [ ] 報告結構清晰、分區明確

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the US cities population concentration task.

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

    report_path = workspace / "cities_density_report.md"
    if not report_path.exists():
        for alt in ["density_report.md", "report.md", "concentration_report.md", "cities_report.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "avg_pop_ranking": 0.0,
            "nyc_dominance": 0.0,
            "state_count": 0.0,
            "single_city_states": 0.0,
            "inequality_ratios": 0.0,
            "regional_summary": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Average population per city ranking — New York state should be near top
    ny_patterns = [
        r'new\s*york.*584',
        r'new\s*york.*highest.*average',
        r'new\s*york.*(?:concentration|dominat)',
    ]
    scores["avg_pop_ranking"] = 1.0 if any(re.search(p, content_lower) for p in ny_patterns) else 0.0

    # NYC dominance — ~84-85% of NY state's dataset population
    nyc_dom_patterns = [r'8[45][\.\d]*\s*%', r'84\.6', r'84\.5', r'8[45]\s*percent']
    has_nyc_dom = any(re.search(p, content_lower) for p in nyc_dom_patterns)
    has_nyc_mention = "new york" in content_lower and ("dominan" in content_lower or "concentrat" in content_lower or "largest" in content_lower)
    scores["nyc_dominance"] = 1.0 if has_nyc_dom else (0.5 if has_nyc_mention else 0.0)

    # State count (~48)
    state_count_patterns = [r'4[78]\s*(?:state|distinct|unique|territor|entri)', r'(?:state|distinct|unique|territor|entri)\w*\s*.*4[78]', r'4[78]\s+state']
    scores["state_count"] = 1.0 if any(re.search(p, content_lower) for p in state_count_patterns) else 0.0

    # Single-city states
    single_states = ["vermont", "maine", "alaska", "hawaii"]
    found_single = sum(1 for s in single_states if s in content_lower)
    scores["single_city_states"] = 1.0 if found_single >= 3 else (0.5 if found_single >= 2 else 0.0)

    # Inequality ratios (largest/smallest within state)
    ratio_patterns = [r'ratio', r'inequalit', r'largest.*smallest', r'most.*least.*equal']
    scores["inequality_ratios"] = 1.0 if any(re.search(p, content_lower) for p in ratio_patterns) else 0.0

    # Regional summary
    regions = ["northeast", "southeast", "midwest", "west"]
    alt_regions = ["south", "east", "pacific", "mountain", "atlantic", "central"]
    region_count = sum(1 for r in regions if r in content_lower)
    alt_count = sum(1 for r in alt_regions if r in content_lower)
    scores["regional_summary"] = 1.0 if region_count >= 3 else (0.5 if (region_count >= 2 or alt_count >= 3) else 0.0)

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

### 評分項 1：分析正確性（權重 35%）

- 1.0：所有集中度指標、主導百分比與比值皆正確計算。州分組與計數準確。
- 0.75：多數指標正確，僅有一兩處小錯。
- 0.5：部分指標正確，但有多項關鍵計算錯誤。
- 0.25：多數計算有重大錯誤。
- 0.0：沒有正確分析。

### 評分項 2：洞見品質（權重 30%）

- 1.0：指出關鍵模式，如 NYC 在 New York 州的極端主導、California 的分散人口、邊緣的單一城市州，以及有意義的區域差異，並對這些模式的意義做出結論。
- 0.75：模式辨識良好，掌握多數關鍵洞見。
- 0.5：有一些觀察，但漏掉主要模式。
- 0.25：大多是原始數字，詮釋很少。
- 0.0：沒有指出任何洞見或模式。

### 評分項 3：完整性（權重 20%）

- 1.0：五個要求的區段皆具備，每個都有充分分析。
- 0.75：所有區段具備，僅有小幅缺漏。
- 0.5：有區段缺漏。
- 0.25：多數區段缺漏。
- 0.0：報告缺漏或空白。

### 評分項 4：報告結構（權重 15%）

- 1.0：組織良好，分區清楚，使用適當表格，且從集中度指標到洞見流程合理。
- 0.75：組織良好，僅有小幅排版問題。
- 0.5：有分析但結構不佳。
- 0.25：不易閱讀。
- 0.0：沒有報告或無法使用。
