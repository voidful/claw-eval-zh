---
id: task_csv_cities_filter
name: 美國城市多條件篩選
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_cities_filter
source_benchmark: pinchbench
claw_eval_id: P073zh_csv_cities_filter
workspace_files:
- source: csvs/us_cities_top1000.csv
  dest: us_cities_top1000.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 美國城市多條件篩選

## Prompt

我的工作區裡有一個 CSV 檔案 `us_cities_top1000.csv`，內含美國人口最多的 1,000 個城市的資料。檔案欄位有：`City`、`State`、`Population`、`lat`、`lon`。

請執行下列篩選分析，並把結果寫到 `cities_filter_report.md`：

1. **California 大城市**：列出 California 中人口 ≥ 200,000 的所有城市，依人口由大到小排序。包含此篩選結果集的數量與總人口。

2. **南部城市**：找出緯度低於北緯 33°N（即 `lat < 33.0`）且人口 ≥ 100,000 的所有城市。列出它們的州別與人口。

3. **州別比較——Texas 對 Florida**：比較這兩個州，列出各州在資料集中的城市總數、總人口、平均城市人口，以及各自人口前 5 大城市。

4. **中型城市**：找出人口介於 75,000 到 125,000（含）之間的所有城市。回報共有幾個，並依字母順序列出前 10 個。

5. **西岸各州**：篩選 California、Oregon、Washington 的城市。回報這個合併區域的城市總數、總人口，以及人口前 10 大城市。

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案
2. 使用欄位值正確套用每一項篩選
3. 對篩選後的子集進行彙總
4. 為每個區段清楚呈現結果

關鍵預期數值：

- California 人口 ≥ 200k：21 個城市（最高為 Los Angeles 3,884,307；最低為 Moreno Valley 201,175）
- CA ≥ 200k 子集的總人口：~12,343,323
- 南部城市（lat < 33.0、pop ≥ 100k）：包含 San Diego、Phoenix、Tucson、El Paso，以及數個 Texas/Florida/Arizona 城市
- Texas：83 個城市，總人口 14,836,230，最大城市 Houston（2,195,914）
- Florida：73 個城市，總人口 7,410,114，最大城市 Jacksonville（842,583）
- Texas 平均城市人口（~178,749）高於 Florida（~101,508）
- 中型城市（75k-125k）：此區間城市數量可觀
- 西岸（CA+OR+WA）：254 個城市，總人口 32,548,214

## Grading Criteria

- [ ] 已建立報告檔案 `cities_filter_report.md`
- [ ] California ≥ 200k 篩選回傳 21 個城市，清單正確
- [ ] 正確套用南部城市篩選（lat < 33.0、pop ≥ 100k）
- [ ] Texas 對 Florida 的比較含城市數、總計與平均
- [ ] 正確呈現 Texas 平均人口高於 Florida
- [ ] 已套用中型城市篩選（75k-125k）並列出結果
- [ ] 西岸各州篩選含全部三個州
- [ ] 各項篩選的數值皆正確
- [ ] 報告結構清晰，每項篩選各有清楚分區

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the US cities multi-criteria filtering task.

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

    report_path = workspace / "cities_filter_report.md"
    if not report_path.exists():
        for alt in ["filter_report.md", "report.md", "cities_report.md", "filtering_report.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "california_filter": 0.0,
            "southern_filter": 0.0,
            "texas_florida_comparison": 0.0,
            "midsize_filter": 0.0,
            "western_coastal_filter": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # California >= 200k: 21 cities
    ca_patterns = [r'21\s*cit', r'twenty.?one\s*cit']
    has_ca_count = any(re.search(p, content_lower) for p in ca_patterns)
    has_ca_cities = "moreno valley" in content_lower and "los angeles" in content_lower
    scores["california_filter"] = 1.0 if (has_ca_count and has_ca_cities) else (0.5 if has_ca_cities else 0.0)

    # Southern cities filter — should mention San Diego, Phoenix, Tucson, El Paso
    southern_cities = ["san diego", "phoenix", "tucson", "el paso"]
    found_southern = sum(1 for c in southern_cities if c in content_lower)
    scores["southern_filter"] = 1.0 if found_southern >= 3 else (0.5 if found_southern >= 2 else 0.0)

    # Texas vs Florida comparison
    has_tx = re.search(r'texas.*83\s*cit|83.*cit.*texas', content_lower)
    has_fl = re.search(r'florida.*73\s*cit|73.*cit.*florida', content_lower)
    has_houston = "houston" in content_lower
    has_jacksonville = "jacksonville" in content_lower
    tx_fl_score = sum([
        bool(has_tx),
        bool(has_fl),
        has_houston,
        has_jacksonville,
    ])
    scores["texas_florida_comparison"] = 1.0 if tx_fl_score >= 4 else (0.5 if tx_fl_score >= 2 else 0.0)

    # Mid-size filter (75k-125k)
    midsize_patterns = [r'75[,.]?000.*125[,.]?000', r'75k.*125k', r'mid.?size', r'medium.?size']
    scores["midsize_filter"] = 1.0 if any(re.search(p, content_lower) for p in midsize_patterns) else 0.0

    # Western coastal filter (CA + OR + WA)
    has_all_states = all(s in content_lower for s in ["california", "oregon", "washington"])
    has_254 = re.search(r'254\s*cit', content_lower) or "254" in content
    scores["western_coastal_filter"] = 1.0 if (has_all_states and has_254) else (0.5 if has_all_states else 0.0)

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

### 評分項 1：篩選正確性（權重 40%）

- 1.0：五項篩選皆正確套用，數量與數值準確。邊界條件處理正確（≥ 對 >、含端點區間）。
- 0.75：多數篩選正確，僅有一處數量或邊界處理小錯。
- 0.5：部分篩選正確，但有多項結果錯誤。
- 0.25：多個區段有重大篩選錯誤。
- 0.0：未套用篩選，或完全錯誤。

### 評分項 2：完整性（權重 25%）

- 1.0：五個篩選區段皆具備，含要求的數量、清單與彙總等完整結果。
- 0.75：所有區段具備，但缺少部分要求的細節（例如總計或平均）。
- 0.5：有區段完全缺漏。
- 0.25：只有一兩個區段。
- 0.0：報告缺漏或空白。

### 評分項 3：比較品質（權重 20%）

- 1.0：Texas 對 Florida 的比較詳盡，資料清楚並列，且助手指出儘管兩州城市數相近，Texas 的平均城市人口仍較高。
- 0.75：比較良好，多數指標具備，但缺少部分洞見。
- 0.5：基本比較，指標有限。
- 0.25：比較淺薄。
- 0.0：未進行比較。

### 評分項 4：報告結構（權重 15%）

- 1.0：每項篩選有清楚的區段標題，適當使用表格，組織合理。
- 0.75：組織良好，僅有小幅排版問題。
- 0.5：有結果但組織不佳。
- 0.25：不易閱讀或缺乏結構。
- 0.0：沒有報告或無法使用。
