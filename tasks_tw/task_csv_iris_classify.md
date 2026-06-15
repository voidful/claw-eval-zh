---
id: task_csv_iris_classify
name: 鳶尾花物種分類規則
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_csv_iris_classify
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T070tw_csv_iris_classify
workspace_files:
- source: csvs/iris_flowers.csv
  dest: iris_flowers.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 鳶尾花物種分類規則

## Prompt

我的工作區裡有一個 CSV 檔案 `iris_flowers.csv`，內含經典的鳶尾花（Iris）資料集，共 150 個樣本。欄位：`SepalLength`、`SepalWidth`、`PetalLength`、`PetalWidth`，以及 `Name`（物種：Iris-setosa、Iris-versicolor、Iris-virginica）。

請分析資料，並發展出一組可由量測值預測物種的簡單分類規則。把結果寫到 `iris_classification.md`。你的報告應包含：

- **特徵分析（feature analysis）**：哪些特徵對區分物種最有用，並附上佐證的統計值或數值範圍
- **分類規則（classification rules）**：一套清楚的決策樹式或門檻式規則（例如「若 PetalLength < X 則物種為 Y」）
- **準確度評估（accuracy evaluation）**：把你的規則套用到整個資料集，回報每條規則正確分類了多少樣本，以及整體準確度
- **誤分類分析（misclassification analysis）**：列出被你的規則誤分類的樣本（若有），並說明為何它們是困難案例
- 一個**混淆矩陣（confusion matrix）**或等效的彙總，呈現預測物種與實際物種的對照

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案
2. 發現 PetalLength 與 PetalWidth 是最具區分力的特徵
3. 發現 setosa 完全可分（PetalLength < 2.5 可涵蓋全部 50 個 setosa 且不含其他物種）
4. 發展出區分 versicolor 與 virginica 的規則（例如 PetalLength < 4.9 或 PetalWidth < 1.7）
5. 達到高準確度（>= 90%，理想為 95%+）
6. 指出 versicolor/virginica 的邊界是多數錯誤發生之處
7. 回報混淆矩陣或各物種準確度
8. 撰寫一份結構清晰的 markdown 報告

關鍵預期數值：

- PetalLength < 2.5 → Iris-setosa（100% 正確，全部 50 個皆對）
- versicolor/virginica 邊界約在 PetalLength ~4.8–5.0 或 PetalWidth ~1.6–1.8
- 以簡單門檻規則可達到的整體準確度：94–97%
- 多數誤分類發生在 versicolor 與 virginica 之間

## Grading Criteria

- [ ] 已建立報告檔案 `iris_classification.md`
- [ ] 已指出 PetalLength（或 PetalWidth）為最具區分力的特徵
- [ ] 已正確指出 setosa 可用一個簡單門檻完全分離
- [ ] 已明確列出帶數值門檻的分類規則
- [ ] 準確度評估：規則套用到整個資料集並回報整體準確度
- [ ] 準確度 >= 90%
- [ ] 有討論或列出誤分類的樣本
- [ ] 有混淆矩陣或各物種準確度細項

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the Iris classification rules task.

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
    report_path = workspace / "iris_classification.md"
    if not report_path.exists():
        alternatives = ["classification.md", "report.md", "iris_rules.md", "iris_report.md", "classification_rules.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "discriminating_feature": 0.0,
            "setosa_separable": 0.0,
            "explicit_rules": 0.0,
            "accuracy_reported": 0.0,
            "high_accuracy": 0.0,
            "misclassification_analysis": 0.0,
            "confusion_matrix": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check discriminating feature identification
    petal_patterns = [
        r'petal\s*length.*(?:most|best|key|primary|strongest|discriminat|import)',
        r'(?:most|best|key|primary|strongest|discriminat|import).*petal\s*length',
        r'petal\s*width.*(?:most|best|key|primary|strongest|discriminat|import)',
        r'(?:most|best|key|primary|strongest|discriminat|import).*petal\s*width',
        r'petal.*(?:useful|effective|powerful|informative).*(?:feature|variable|predictor)',
    ]
    scores["discriminating_feature"] = 1.0 if any(re.search(p, content_lower) for p in petal_patterns) else 0.0

    # Check setosa separability
    setosa_patterns = [
        r'setosa.*(?:perfect|100|complete|linear).*(?:separ|classif|distinguish)',
        r'(?:perfect|100|complete|linear).*(?:separ|classif|distinguish).*setosa',
        r'petal\s*length\s*[<≤]\s*2\.[0-5].*setosa',
        r'setosa.*petal\s*length\s*[<≤]\s*2\.[0-5]',
        r'petal\s*width\s*[<≤]\s*0\.[5-8].*setosa',
    ]
    scores["setosa_separable"] = 1.0 if any(re.search(p, content_lower) for p in setosa_patterns) else 0.0

    # Check explicit rules with thresholds
    threshold_patterns = [
        r'(?:if|when|where)\s+.*(?:petal|sepal)\s*(?:length|width)\s*[<>≤≥]=?\s*\d+\.?\d*',
        r'(?:petal|sepal)\s*(?:length|width)\s*[<>≤≥]=?\s*\d+\.?\d*\s*(?:→|->|then|:)',
        r'threshold.*\d+\.?\d*',
    ]
    rule_count = sum(1 for p in threshold_patterns if re.search(p, content_lower))
    scores["explicit_rules"] = 1.0 if rule_count >= 2 else (0.5 if rule_count >= 1 else 0.0)

    # Check accuracy reported
    accuracy_patterns = [
        r'(?:accuracy|correct)\s*(?::|=|of|is)?\s*\d{2,3}[.%]',
        r'\d{2,3}\.?\d*\s*%\s*(?:accuracy|correct)',
        r'(?:9[0-9]|100)\s*(?:out of|/)\s*150',
        r'(?:accuracy|correct).*(?:9[0-9]|100)%',
    ]
    scores["accuracy_reported"] = 1.0 if any(re.search(p, content_lower) for p in accuracy_patterns) else 0.0

    # Check high accuracy (>= 90%)
    acc_values = re.findall(r'(\d{2,3}\.?\d*)\s*%', content)
    high_acc = False
    for val in acc_values:
        try:
            if 90 <= float(val) <= 100:
                high_acc = True
                break
        except ValueError:
            pass
    # Also check fraction form
    frac_match = re.search(r'(\d{2,3})\s*/\s*150', content)
    if frac_match:
        try:
            if int(frac_match.group(1)) >= 135:
                high_acc = True
        except ValueError:
            pass
    scores["high_accuracy"] = 1.0 if high_acc else 0.0

    # Check misclassification analysis
    misclass_patterns = [
        r'mis(?:classif|label)',
        r'(?:incorrect|wrong|error).*(?:classif|predict)',
        r'(?:classif|predict).*(?:incorrect|wrong|error)',
        r'versicolor.*virginica.*(?:overlap|confus|difficult|hard)',
        r'(?:overlap|confus|difficult|hard).*versicolor.*virginica',
    ]
    scores["misclassification_analysis"] = 1.0 if any(re.search(p, content_lower) for p in misclass_patterns) else 0.0

    # Check confusion matrix
    confusion_patterns = [
        r'confusion\s*matrix',
        r'\|\s*(?:setosa|versicolor|virginica)\s*\|.*\d+.*\|',
        r'(?:predicted|actual).*(?:setosa|versicolor|virginica)',
        r'(?:true|false)\s*(?:positive|negative)',
        r'(?:tp|fp|fn|tn)\b',
        r'per[- ]?species.*(?:accuracy|precision|recall)',
    ]
    scores["confusion_matrix"] = 1.0 if any(re.search(p, content_lower) for p in confusion_patterns) else 0.0

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

### 評分項 1：分類規則品質（權重 35%）

- 1.0：規則明確列出具體數值門檻，能完全分離 setosa，且在 versicolor/virginica 上達到 95%+ 準確度。規則如決策樹或流程圖般易於依循。
- 0.75：規則清楚、有門檻，能分離 setosa，整體準確度達 90%+。
- 0.5：有規則但模糊、缺乏具體門檻，或僅達中等準確度。
- 0.25：規則定義不良或準確度偏低。
- 0.0：沒有提供分類規則，或規則完全錯誤。

### 評分項 2：資料分析深度（權重 25%）

- 1.0：完整的特徵分析，含各物種數值範圍，以統計佐證指出 PetalLength/PetalWidth 為最佳區分特徵，並解釋為何 setosa 可分而 versicolor/virginica 重疊。
- 0.75：特徵分析良好，有物種比較與所選特徵的合理理由。
- 0.5：基本特徵分析，但缺少關鍵比較或統計佐證。
- 0.25：分析極少；規則看似武斷、缺乏資料依據。
- 0.0：沒有特徵分析。

### 評分項 3：評估嚴謹度（權重 25%）

- 1.0：評估完整，含混淆矩陣、各物種準確度、具體列出誤分類樣本，並解釋邊界案例為何困難。
- 0.75：評估良好，有準確度與混淆矩陣，並有部分錯誤討論。
- 0.5：有回報準確度，但錯誤分析有限。
- 0.25：準確度宣稱模糊，缺乏佐證。
- 0.0：沒有對規則表現做評估。

### 評分項 4：報告清晰度（權重 15%）

- 1.0：組織良好，分區清楚，規則易於依循，表格排版良好，且從分析到規則再到評估流程合理。
- 0.75：組織良好、易讀，僅有小問題。
- 0.5：有分析但不易依循。
- 0.25：雜亂或缺少主要區段。
- 0.0：沒有報告，或空白／無法使用。
