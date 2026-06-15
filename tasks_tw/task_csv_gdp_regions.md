---
id: task_csv_gdp_regions
name: 世界 GDP 區域分析
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_gdp_regions
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T065tw_csv_gdp_regions
workspace_files:
- source: csvs/world_gdp_2014.csv
  dest: world_gdp_2014.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 世界 GDP 區域分析

## Prompt

我的工作區中有一個 CSV 檔 `world_gdp_2014.csv`，內含全球各國與屬地的 GDP 資料。
該檔有三個欄位：`COUNTRY`、`GDP (BILLIONS)`（單位為美元）與 `CODE`（ISO 國家
代碼）。共有 222 筆。

此資料集不含區域（region）欄位。請運用你的世界地理知識，將每一國歸入下列其中
一個區域：**North America**、**Europe**、**East Asia & Pacific**、
**South Asia**、**Latin America & Caribbean**、
**Middle East & North Africa**、**Sub-Saharan Africa** 與
**Central Asia & Caucasus**。接著將區域分析寫入 `gdp_regions_report.md`。你的
報告應包含：

- **各區域 GDP 總額**，附上各區域的合計 GDP、國家數，以及佔世界 GDP 的百分比
  份額，並依總 GDP 由高至低排序
- **各區域前 3 大經濟體**（國名與 GDP）
- **區域比較**：哪 3 個區域主導全球經濟，其合計份額為何
- **各區域平均每國 GDP**：哪個區域平均每國 GDP 最高、哪個最低，這代表什麼
- **差距分析**：對每個區域計算最大與最小經濟體之間的比值——哪個區域呈現最大的
  內部差距
- 一段簡短的**總結段落**，說明全球經濟產出的地理分布

注意：部分國家可能存在歸類上的模糊（例如 Russia、Turkey）。請將它們歸入你認為
最合適的區域，並註明任何邊界案例。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔（222 筆）
2. 運用地理知識將每一國歸入某區域
3. 依區域聚合 GDP
4. 計算百分比份額與平均
5. 找出各區域前幾大經濟體
6. 分析區域內部差距
7. 撰寫一份結構良好的 markdown 報告

預期關鍵數值（約略，視區域歸類而定）：

- East Asia & Pacific：約 $21,000–27,000B（最大區域，由 China 與 Japan 帶動）
- North America：約 $20,500B（3 國：US、Canada、Mexico）
- Europe：約 $18,000–22,000B（視 Russia/Turkey 歸類，30–40 國）
- South Asia：約 $2,500B（7 國，由 India 主導）
- Latin America & Caribbean：約 $4,500B（20+ 國，由 Brazil 領銜）
- Middle East & North Africa：約 $3,000–4,000B（由 Saudi Arabia 領銜）
- Sub-Saharan Africa：約 $1,700B（40+ 國，由 Nigeria 領銜）
- Central Asia & Caucasus：約 $400–500B（8 國，由 Kazakhstan 領銜）

前 3 大區域合計應佔世界 GDP 約 75-80%。
North America 平均每國 GDP 最高（僅 3 國，約 $6,800B/國）。
Sub-Saharan Africa 平均最低（約 $35B/國，儘管筆數最多）。

## Grading Criteria

- [ ] 已建立報告檔 `gdp_regions_report.md`
- [ ] 計算各區域 GDP 總額並附百分比份額
- [ ] 列出各區域前 3 大經濟體
- [ ] 找出三個主導區域並附合計份額
- [ ] 分析各區域平均每國 GDP
- [ ] 為各區域計算內部差距比值
- [ ] 註明邊界案例（Russia、Turkey 等）
- [ ] 含關於地理分布的總結段落

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the GDP regional analysis task.

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

    report_path = workspace / "gdp_regions_report.md"
    if not report_path.exists():
        for alt in ["regions_report.md", "report.md", "gdp_regions.md", "regional_report.md", "regional_analysis.md", "analysis.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "regional_totals": 0.0,
            "top_per_region": 0.0,
            "dominant_regions": 0.0,
            "avg_per_country": 0.0,
            "disparity": 0.0,
            "borderline_cases": 0.0,
            "summary_paragraph": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check regional totals present
    regions_found = 0
    region_names = [
        r'north\s*america', r'europe', r'east\s*asia', r'south\s*asia',
        r'latin\s*america', r'middle\s*east', r'sub[- ]saharan', r'central\s*asia'
    ]
    for rn in region_names:
        if re.search(rn, content_lower):
            regions_found += 1
    has_pct = bool(re.search(r'\d+\.?\d*\s*%', content))
    scores["regional_totals"] = 1.0 if (regions_found >= 7 and has_pct) else (0.5 if regions_found >= 4 else 0.0)

    # Check top economies per region
    top_econ_patterns = [
        r'united\s*states',  # North America
        r'germany',          # Europe
        r'china',            # East Asia
        r'india',            # South Asia
        r'brazil',           # Latin America
        r'saudi\s*arabia',   # MENA
        r'nigeria',          # SSA
        r'kazakhstan',       # Central Asia
    ]
    top_found = sum(1 for p in top_econ_patterns if re.search(p, content_lower))
    scores["top_per_region"] = 1.0 if top_found >= 7 else (0.5 if top_found >= 4 else 0.0)

    # Check dominant regions identified
    dominant_patterns = [
        r'(?:dominat|largest|top\s*(?:3|three)).*(?:region|area)',
        r'(?:north\s*america|europe|east\s*asia).*(?:combin|together|account)',
        r'(?:7[5-9]|80)\s*[\.\d]*%.*(?:combin|together|three|3)',
    ]
    dom_found = sum(1 for p in dominant_patterns if re.search(p, content_lower))
    scores["dominant_regions"] = 1.0 if dom_found >= 1 else 0.0

    # Check average GDP per country analysis
    avg_patterns = [
        r'(?:average|mean)\s*(?:gdp)?\s*(?:per\s*country|per\s*economy)',
        r'north\s*america.*(?:highest|largest).*(?:average|mean)',
        r'(?:africa|sub[- ]saharan).*(?:lowest|smallest).*(?:average|mean)',
    ]
    avg_found = sum(1 for p in avg_patterns if re.search(p, content_lower))
    scores["avg_per_country"] = 1.0 if avg_found >= 2 else (0.5 if avg_found >= 1 else 0.0)

    # Check disparity analysis
    disp_patterns = [
        r'(?:dispar|ratio|inequal|gap|range)',
        r'(?:largest|biggest).*(?:smallest|lowest)',
        r'(?:ratio|factor|times)',
    ]
    disp_found = sum(1 for p in disp_patterns if re.search(p, content_lower))
    scores["disparity"] = 1.0 if disp_found >= 2 else (0.5 if disp_found >= 1 else 0.0)

    # Check borderline cases mentioned
    border_patterns = [
        r'(?:russia|turkey).*(?:border|ambiguous|classify|assign|debat|could)',
        r'(?:border|ambiguous|transcontinental).*(?:russia|turkey)',
        r'(?:classif|assign|categori).*(?:challeng|difficult|judgment|borderline)',
    ]
    scores["borderline_cases"] = 1.0 if any(re.search(p, content_lower) for p in border_patterns) else 0.0

    # Check summary paragraph
    summary_patterns = [
        r'(?:concentrat|cluster|dominat).*(?:global|world)',
        r'(?:global|world).*(?:output|gdp).*(?:concentrat|dominat|cluster)',
        r'(?:africa|developing|south).*(?:small|fraction|marginal)',
    ]
    summary_found = sum(1 for p in summary_patterns if re.search(p, content_lower))
    scores["summary_paragraph"] = 1.0 if summary_found >= 1 else 0.0

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

### 評分項 1：區域歸類正確性（權重 25%）

**1.0 分**：各國歸入合理的區域。8 個區域涵蓋全部或近乎全部 222 筆。邊界案例
（Russia、Turkey、Cyprus）獲得承認並說明理由。小型屬地處理合理。
**0.75 分**：多數歸類正確，僅少數放錯且對邊界案例有所承認。
**0.5 分**：大致正確，但漏掉重要國家或將數國放錯區域。
**0.25 分**：許多歸類錯誤或涵蓋有大量缺口。
**0.0 分**：未嘗試歸類或根本性錯誤。

### 評分項 2：量化分析（權重 30%）

**1.0 分**：各區域總額、百分比、平均與差距比值皆正確計算。數字內部一致
（百分比合計約 100%、各區域總額相加等於世界 GDP）。
**0.75 分**：多數計算正確，僅有小幅落差。
**0.5 分**：部分計算正確，但有明顯錯誤或缺少指標。
**0.25 分**：有重大計算錯誤。
**0.0 分**：未嘗試任何計算。

### 評分項 3：分析深度（權重 25%）

**1.0 分**：對全球 GDP 分布提供具意義的洞見——North America 何以在平均上領先
（僅 3 個大型經濟體）、Sub-Saharan Africa 何以平均偏低（眾多小型經濟體）、
East Asia 總額何以由 China/Japan 帶動，以及差距比值透露的區域經濟結構。
**0.75 分**：洞見良好，僅有小缺漏。
**0.5 分**：有基本觀察但缺乏更深入的解讀。
**0.25 分**：分析流於表面。
**0.0 分**：未提供任何分析。

### 評分項 4：完整性與呈現（權重 20%）

**1.0 分**：所有要求章節皆齊備，表格或清單排版良好，標題清楚、脈絡合乎邏輯。
各區域前 3、平均、差距、主導區域與總結皆齊備。
**0.75 分**：多數章節齊備且排版良好。
**0.5 分**：缺少數個章節或排版不佳。
**0.25 分**：內容極少。
**0.0 分**：報告缺漏或為空。
