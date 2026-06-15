---
id: task_csv_iris_outliers
name: 鳶尾花離群值偵測
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_iris_outliers
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T071tw_csv_iris_outliers
workspace_files:
- source: csvs/iris_flowers.csv
  dest: iris_flowers.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 鳶尾花離群值偵測

## Prompt

我的工作區裡有一個 CSV 檔案 `iris_flowers.csv`，內含經典的鳶尾花（Iris）資料集，共 150 個樣本。欄位：`SepalLength`、`SepalWidth`、`PetalLength`、`PetalWidth`，以及 `Name`（物種：Iris-setosa、Iris-versicolor、Iris-virginica）。

請分析資料集中的離群值（outlier）與異常觀測值，並把你的發現寫到 `iris_outliers.md`。你的報告應包含：

- **離群值偵測方法（outlier detection method）**：說明所使用的統計方法（例如 IQR、z-score，或兩者）
- **整體離群值（overall outliers）**：在整個資料集中對每個數值欄位偵測到的離群值，附上具體數值與所屬列的辨識
- **物種內離群值（within-species outliers）**：在各物種群組內偵測到的離群值（某個數值在整體上可能正常，但對其所屬物種而言屬於極端值）
- **異常觀測值（unusual observations）**：同時考量多個特徵時，對其物種而言屬於非典型的樣本（例如花瓣異常小的 virginica）
- **摘要（summary）**：共找到多少離群值、哪些特徵與物種受影響最多，以及是否有任何樣本可能被標錯類別

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案
2. 對每個數值欄位套用以 IQR 或 z-score 為基礎的離群值偵測
3. 找出整體資料集中的 SepalWidth 離群值：
   - 第 16 列：Iris-setosa，SepalWidth=4.4（高於上界）
   - 第 33 列：Iris-setosa，SepalWidth=4.1（高於上界）
   - 第 34 列：Iris-setosa，SepalWidth=4.2（高於上界）
   - 第 61 列：Iris-versicolor，SepalWidth=2.0（低於下界）
4. 進行物種內分析，找出對其群組而言屬於極端值的觀測
5. 注意多特徵的異常觀測，例如：
   - 第 42 列：Iris-setosa，SepalWidth=2.3（setosa 中最低，遠離 setosa 平均值 3.42）
   - 第 107 列：Iris-virginica，SepalLength=4.9，是最小的 virginica（平均值 6.59）
6. 討論是否有任何離群值可能代表標錯類別
7. 撰寫一份結構清晰的 markdown 報告

關鍵預期數值：

- SepalWidth IQR 離群值：第 16、33、34 列（高）、第 61 列（低）
- SepalWidth Q1=2.8、Q3=3.3、IQR=0.5、界限：[2.05, 4.05]
- 對整個資料集以 IQR 計算時，SepalLength、PetalLength、PetalWidth 皆無離群值
- 物種內分析會揭露整體資料中看不到的額外離群值

## Grading Criteria

- [ ] 已建立報告檔案 `iris_outliers.md`
- [ ] 已清楚說明離群值偵測方法（IQR、z-score 或類似）
- [ ] 已指出 SepalWidth 是整體離群值最多的欄位
- [ ] 已回報具體離群值與列號（4 個 SepalWidth 離群值中至少 2 個）
- [ ] 已進行物種內離群值分析
- [ ] 已討論多特徵異常觀測（例如對其物種而言非典型的樣本）
- [ ] 有摘要，含離群值數量與受影響的特徵／物種

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the Iris outlier detection task.

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
    report_path = workspace / "iris_outliers.md"
    if not report_path.exists():
        alternatives = ["outliers.md", "report.md", "iris_report.md", "outlier_analysis.md", "iris_outlier_report.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "method_explained": 0.0,
            "sepalwidth_outliers": 0.0,
            "specific_values": 0.0,
            "within_species": 0.0,
            "unusual_observations": 0.0,
            "summary": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check method explanation
    method_patterns = [
        r'iqr|inter\s*-?\s*quartile\s*range',
        r'z\s*-?\s*score',
        r'(?:1\.5|1\.5\s*[*×x]\s*iqr)',
        r'(?:standard\s*deviation|sigma).*(?:outlier|threshold)',
        r'(?:upper|lower)\s*(?:fence|bound|whisker)',
    ]
    method_count = sum(1 for p in method_patterns if re.search(p, content_lower))
    scores["method_explained"] = 1.0 if method_count >= 2 else (0.5 if method_count >= 1 else 0.0)

    # Check SepalWidth identified as having outliers
    sw_patterns = [
        r'sepal\s*width.*outlier',
        r'outlier.*sepal\s*width',
        r'sepalwidth.*outlier',
        r'outlier.*sepalwidth',
    ]
    scores["sepalwidth_outliers"] = 1.0 if any(re.search(p, content_lower) for p in sw_patterns) else 0.0

    # Check specific outlier values reported
    specific_score = 0.0
    # SepalWidth = 4.4 (row 16, setosa)
    if re.search(r'4\.4', content) and re.search(r'sepal\s*width|sepalwidth', content_lower):
        specific_score += 0.25
    # SepalWidth = 4.1 or 4.2 (rows 33, 34)
    if re.search(r'4\.[12]', content):
        specific_score += 0.25
    # SepalWidth = 2.0 (row 61, versicolor)
    if re.search(r'(?:sepal\s*width|sepalwidth).*2\.0|2\.0.*(?:sepal\s*width|sepalwidth)', content_lower):
        specific_score += 0.25
    # Any row numbers mentioned
    if re.search(r'(?:row|sample|observation|index)\s*(?:#?\s*)?(?:16|33|34|42|61|107)', content_lower):
        specific_score += 0.25
    scores["specific_values"] = min(specific_score, 1.0)

    # Check within-species analysis
    within_patterns = [
        r'within[- ]species.*outlier',
        r'(?:per|each|by)[- ]species.*outlier',
        r'outlier.*(?:within|per|each|by)[- ](?:species|group|class)',
        r'(?:setosa|versicolor|virginica).*(?:outlier|extreme|unusual).*(?:within|for\s+(?:its|the)\s+species)',
        r'(?:group|species|class)[- ](?:level|specific|wise).*outlier',
    ]
    scores["within_species"] = 1.0 if any(re.search(p, content_lower) for p in within_patterns) else 0.0

    # Check unusual multi-feature observations
    unusual_patterns = [
        r'(?:unusual|atypical|anomal).*(?:observ|sample|row|specimen)',
        r'(?:row|sample)\s*(?:#?\s*)?(?:42|107).*(?:unusual|atypical|extreme|outlier)',
        r'(?:virginica|setosa).*(?:small|low|unusual|atypical)',
        r'sepal\s*width\s*(?:=|of|:)?\s*2\.3.*setosa',
        r'(?:mislabel|misclassif|wrong\s*(?:label|species))',
    ]
    unusual_count = sum(1 for p in unusual_patterns if re.search(p, content_lower))
    scores["unusual_observations"] = 1.0 if unusual_count >= 2 else (0.5 if unusual_count >= 1 else 0.0)

    # Check summary
    summary_patterns = [
        r'(?:total|found)\s*\d+\s*outlier',
        r'\d+\s*outlier.*(?:found|detected|identified)',
        r'(?:summary|conclusion|overall)',
        r'(?:most|primarily).*(?:sepal\s*width|affected)',
    ]
    summary_count = sum(1 for p in summary_patterns if re.search(p, content_lower))
    scores["summary"] = 1.0 if summary_count >= 2 else (0.5 if summary_count >= 1 else 0.0)

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

### 評分項 1：離群值偵測品質（權重 35%）

- 1.0：使用定義良好的統計方法（IQR 或 z-score），正確找出所有 SepalWidth 離群值並附具體數值，且指出以整體 IQR 方法時其他欄位並無離群值。
- 0.75：使用有效方法，正確找出多數離群值並附具體數值。
- 0.5：找出部分離群值，但漏掉關鍵者，或方法套用不佳。
- 0.25：嘗試偵測離群值，但結果多半錯誤或不完整。
- 0.0：沒有進行離群值偵測，或完全錯誤。

### 評分項 2：物種內與多特徵分析（權重 30%）

- 1.0：進行物種內離群值偵測，找出對其物種屬極端但整體上不極端的樣本（例如 SepalWidth=2.3 的 setosa、SepalLength=4.9 的 virginica），並討論多特徵的異常模式。
- 0.75：物種內分析良好，並有部分多特徵討論。
- 0.5：基本的物種內分析，但多特徵洞見有限。
- 0.25：物種內分析極少。
- 0.0：沒有進行物種內分析。

### 評分項 3：詮釋與脈絡（權重 20%）

- 1.0：討論離群值的生物學合理性、是否可能代表量測誤差或標錯類別，解釋為何某些物種受影響較多，並提出可執行的結論。
- 0.75：詮釋良好，並有一些關於離群值意義的脈絡。
- 0.5：基本詮釋，深度不足。
- 0.25：詮釋極少；只列數字而無脈絡。
- 0.0：沒有對發現做詮釋。

### 評分項 4：報告完整性與清晰度（權重 15%）

- 1.0：所有要求的區段皆具備（方法、整體離群值、物種內、異常觀測、摘要），排版良好（表格或結構化清單），清楚易讀。
- 0.75：多數區段具備，排版良好。
- 0.5：部分區段缺漏或組織不佳。
- 0.25：主要區段缺漏或不易閱讀。
- 0.0：沒有報告，或空白／無法使用。
