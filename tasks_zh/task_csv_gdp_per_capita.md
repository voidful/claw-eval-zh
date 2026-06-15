---
id: task_csv_gdp_per_capita
name: 世界人均 GDP 估算
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_gdp_per_capita
source_benchmark: pinchbench
claw_eval_id: P064zh_csv_gdp_per_capita
workspace_files:
- source: csvs/world_gdp_2014.csv
  dest: world_gdp_2014.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 世界人均 GDP 估算

## Prompt

我的工作區中有一個 CSV 檔 `world_gdp_2014.csv`，內含全球各國與屬地的 GDP 資料。
該檔有三個欄位：`COUNTRY`、`GDP (BILLIONS)`（單位為美元）與 `CODE`（ISO 國家
代碼）。共有 222 筆。

此資料集含有總 GDP，但沒有人口。請運用你對 2014 年**GDP 前 30 大經濟體**約略
人口的知識，為每一國估算人均 GDP (GDP per capita)，並將你的發現寫入
`gdp_per_capita_report.md`。你的報告應包含：

- **依總 GDP 排序的前 30 大經濟體**，欄位包含：排名、國家、GDP（單位 billions）、
  估計人口，以及估計人均 GDP
- **依人均 GDP 重新排名**：將同樣這 30 國依人均 GDP 由高至低重新排序
- **關鍵觀察**：哪些大型經濟體在人均上排名最高、哪些最低，以及這對生活水準
  相對於經濟規模透露了什麼
- **離群值與意外之處**：找出人均排名與其總 GDP 排名差異極大的國家（例如某前 10
  大經濟體在人均上卻排得很低，或某較小經濟體在人均上排得很高）
- 一段簡短的**方法論說明**，闡明由於 CSV 缺乏人口資料，人口是依一般知識估算的

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔
2. 依 GDP 排序以找出前 30 大經濟體
3. 套用合理的 2014 年人口估計（依一般知識）
4. 為每一國計算人均 GDP（GDP in billions × 1,000,000,000 / 人口）
5. 依人均 GDP 重新排名
6. 找出關於經濟規模相對於人均財富的關鍵洞見
7. 撰寫一份含方法論說明、結構良好的 markdown 報告

預期關鍵數值（約略，使用 2014 年人口）：

依總 GDP 的前 30 大以下列開頭：US ($17,420B)、China ($10,360B)、Japan ($4,770B)、
Germany ($3,820B)、France ($2,902B)

前 30 國依人均排名大致應呈現：
- 前 30 中人均最高者：Australia（約 $62k）、Sweden（約 $58k）、
  United States（約 $55k）、Netherlands（約 $52k）、Switzerland 不在內
  （依總 GDP 不在前 30）
- 前 30 中人均最低者：India（約 $1.6k）、Nigeria（約 $3.4k）、Indonesia
  （約 $3.5k）、Pakistan（約 $1.3k，若在前 30 內）
- China 人均：約 $7.5k，儘管總 GDP 排第 2
- India 人均：約 $1.6k，儘管總 GDP 排第 10

## Grading Criteria

- [ ] 已建立報告檔 `gdp_per_capita_report.md`
- [ ] 依總 GDP 列出前 30 大經濟體並附 GDP 數值
- [ ] 為每一國提供人口估計
- [ ] 為每一國計算人均 GDP
- [ ] 包含依人均 GDP 的重新排名
- [ ] 含關於規模相對於人均財富的關鍵觀察
- [ ] 找出離群值（例如 India／China 總 GDP 高但人均低）
- [ ] 含關於估計人口的方法論說明

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the GDP per capita estimation task.

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

    report_path = workspace / "gdp_per_capita_report.md"
    if not report_path.exists():
        for alt in ["per_capita_report.md", "report.md", "gdp_per_capita.md", "per_capita.md", "analysis.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "top30_by_gdp": 0.0,
            "population_estimates": 0.0,
            "per_capita_calculated": 0.0,
            "per_capita_ranking": 0.0,
            "key_observations": 0.0,
            "outliers": 0.0,
            "methodology_note": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check top 30 by GDP listed
    top_countries = ["united states", "china", "japan", "germany", "france",
                     "united kingdom", "brazil", "italy", "russia", "india"]
    found_top = sum(1 for c in top_countries if c in content_lower)
    scores["top30_by_gdp"] = 1.0 if found_top >= 8 else (0.5 if found_top >= 5 else 0.0)

    # Check population estimates present
    pop_patterns = [
        r'(?:population|pop\.?).*(?:million|billion|[0-9]{6,})',
        r'(?:318|319|320)\s*(?:million|m\b)',   # US ~318-320M
        r'(?:1[,.]?3[56]\d|1[,.]?36[0-9])\s*(?:million|billion|m\b|b\b)',  # China ~1.36B
        r'(?:1[,.]?2[567]\d)\s*(?:million|m\b|b\b)',  # India ~1.25B
    ]
    pop_found = sum(1 for p in pop_patterns if re.search(p, content_lower))
    scores["population_estimates"] = 1.0 if pop_found >= 2 else (0.5 if pop_found >= 1 else 0.0)

    # Check per capita values calculated
    per_capita_patterns = [
        r'per\s*capita',
        r'(?:54|55|56)[,.]?\d*\s*(?:k|thousand|,\d{3})',  # US per capita ~$55k
        r'(?:7[,.]?[345]\d{2}|7[,.]?5\d{2})',  # China per capita ~$7,500
        r'(?:1[,.]?[56]\d{2}|1[,.]?6\d{2})',  # India per capita ~$1,600
    ]
    pc_found = sum(1 for p in per_capita_patterns if re.search(p, content_lower + content))
    scores["per_capita_calculated"] = 1.0 if pc_found >= 3 else (0.5 if pc_found >= 1 else 0.0)

    # Check re-ranking by per capita
    rerank_patterns = [
        r'(?:rank|sort|order|re-?rank).*per\s*capita',
        r'per\s*capita.*(?:rank|sort|order)',
        r'(?:highest|top).*per\s*capita',
    ]
    scores["per_capita_ranking"] = 1.0 if any(re.search(p, content_lower) for p in rerank_patterns) else 0.0

    # Check key observations
    obs_patterns = [
        r'(?:living\s*standard|wealth|prosperity)',
        r'(?:economic\s*size|total\s*gdp).*(?:per\s*capita|per\s*person)',
        r'(?:large|big|populous).*(?:low|lower).*per\s*capita',
    ]
    obs_found = sum(1 for p in obs_patterns if re.search(p, content_lower))
    scores["key_observations"] = 1.0 if obs_found >= 2 else (0.5 if obs_found >= 1 else 0.0)

    # Check outliers identified (India, China as large GDP but low per capita)
    outlier_found = 0
    if re.search(r'(?:india|china).*(?:low|lower|bottom|despite|contrast)', content_lower):
        outlier_found += 1
    if re.search(r'(?:despite|although|while|but).*(?:per\s*capita|per\s*person)', content_lower):
        outlier_found += 1
    if re.search(r'(?:australia|sweden|netherlands).*(?:high|higher|top).*per\s*capita', content_lower):
        outlier_found += 1
    scores["outliers"] = 1.0 if outlier_found >= 2 else (0.5 if outlier_found >= 1 else 0.0)

    # Check methodology note
    method_patterns = [
        r'(?:methodolog|approach|note|caveat|limitation)',
        r'(?:estimat|approximat).*(?:population|pop)',
        r'(?:population).*(?:not\s*(?:in|available|included|provided)|missing|absent|lack)',
    ]
    method_found = sum(1 for p in method_patterns if re.search(p, content_lower))
    scores["methodology_note"] = 1.0 if method_found >= 2 else (0.5 if method_found >= 1 else 0.0)

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

### 評分項 1：人口估計品質（權重 30%）

**1.0 分**：人口估計對 2014 年而言合理（例如 US 約 318M、China 約 1.36B、
India 約 1.25B、Japan 約 127M、Germany 約 81M）。可接受小幅不準，但應落在
合理範圍內。
**0.75 分**：多數估計合理，僅少數明顯偏差。
**0.5 分**：有提供估計，但數個明顯錯誤（偏差 >20%）。
**0.25 分**：許多估計嚴重不準。
**0.0 分**：未提供人口估計或完全捏造。

### 評分項 2：人均分析品質（權重 30%）

**1.0 分**：在給定人口估計下，人均計算正確，重新排名做得妥當，且分析正確指出
人口眾多的開發中國家（India、China、Indonesia）人均排名低得多，而較小的富裕
國家排名較高。
**0.75 分**：計算與重新排名大致正確，分析良好。
**0.5 分**：算出部分人均值，但重新排名不完整或分析流於表面。
**0.25 分**：有人均值但計算有重大錯誤。
**0.0 分**：未嘗試人均分析。

### 評分項 3：洞見品質（權重 25%）

**1.0 分**：清楚說明總 GDP 反映經濟規模、人均反映個人富裕程度。指出具體意外
（例如 India 以 GDP 排第 10 但人均近墊底、Australia 為中型經濟體卻人均居頂）。
討論人口在此分歧中的作用。
**0.75 分**：洞見良好，僅有小缺漏。
**0.5 分**：有基本觀察但缺乏更深入的解讀。
**0.25 分**：觀察流於表面或不正確。
**0.0 分**：未提供任何洞見。

### 評分項 4：方法論與呈現（權重 15%）

**1.0 分**：方法論說明清楚、表格排版良好，並坦承估計上的侷限。承認人口數字
為約略值。
**0.75 分**：呈現良好，僅有小幅排版問題或方法論說明較簡短。
**0.5 分**：可讀，但缺少方法論說明或表格排版不佳。
**0.25 分**：不易閱讀或方法論不清楚。
**0.0 分**：無報告或無法閱讀。
