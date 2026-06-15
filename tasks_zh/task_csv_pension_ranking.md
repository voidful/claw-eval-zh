---
id: task_csv_pension_ranking
name: 美國退休金各州排名
category: csv_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_csv_pension_ranking
source_benchmark: pinchbench
claw_eval_id: P076zh_csv_pension_ranking
workspace_files:
- source: csvs/us_pension_by_state.csv
  dest: us_pension_by_state.csv
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 美國退休金各州排名

## Prompt

我的工作區裡有一個 CSV 檔案 `us_pension_by_state.csv`，內含按州與國會選區（congressional district）細分的美國聯邦退休金給付資料。欄位如下：

- `STATE_ABBREV_NAME` — 州縮寫與名稱（例如州總計列為 "OH-OHIO Total"、選區列為 "OH-OHIO"）
- `DISTRICT` — 國會選區號碼、"At Large" 或年份（Grand Total 列使用 "2018"）
- `PAYEE_AMOUNT` — 給付給退休人員的總金額（以 $ 與逗號格式化）
- `PAYEE_COUNT` — 目前領取者人數（以逗號格式化）
- `DEFERRED_COUNT` — 遞延（未來）領取者人數（以逗號格式化）

以 "Total" 結尾的列為州級彙總。第一列資料是跨所有州的 Grand Total。

請分析這份資料，並把你的發現寫到 `pension_ranking_report.md`。你的報告應包含：

- 依總給付金額（payee amount）由大到小排名的**前 10 大州（top 10 states）**，附上金額與領取人數
- 依總給付金額排名的**後 5 名州（bottom 5 states）**（排除領地與金額為 $0 的項目）
- 依目前領取者人數排名的**前 10 大州（top 10 states）**
- 跨所有州的**總計（grand total）**（總金額、總領取人數、總遞延人數）
- 一段簡短的**分析**：說明哪些區域在聯邦退休金給付上占主導，以及可能的原因

## Expected Behavior

助手應該：

1. 讀取並解析 CSV 檔案，處理以美元格式化的金額（去除 `$` 與逗號）
2. 篩選州級 "Total" 列，取出金額、領取人數與遞延人數
3. 依總給付金額排序各州，產生前 10 名排名
4. 找出金額非零的後 5 名州／領地
5. 依領取人數排序，做出領取人數排名
6. 取出 Grand Total 列
7. 撰寫一份結構清晰、含分析的 markdown 報告

關鍵預期數值：

- Grand Total：~$5,711,533,247，跨 877,305 名領取者，遞延 483,720 人
- 金額前 3 名：Ohio（~$536.2M）、Pennsylvania（~$456.4M）、Florida（~$429.0M）
- 金額第 4-5 名：Michigan（~$389.7M）、California（~$357.7M）
- 領取人數前 3 名：Pennsylvania（78,119）、Ohio（77,679）、Florida（59,857）
- 後段州包含：Northern Mariana Islands（~$5,894）、American Samoa（~$39,962）、Armed Forces Pacific（~$103,423）

## Grading Criteria

- [ ] 已建立報告檔案 `pension_ranking_report.md`
- [ ] 正確列出依總給付金額排名的前 10 大州
- [ ] 已指出 Ohio 為金額第 1 名（~$536M）
- [ ] 已指出 Pennsylvania 為金額第 2 名（~$456M）
- [ ] 已指出 Florida 為金額第 3 名（~$429M）
- [ ] 已指出後 5 名州／領地
- [ ] 已回報總計數字（~$5.7B、~877K 領取者、~484K 遞延）
- [ ] 已包含依領取人數排名的前段州
- [ ] 已提供地理模式分析

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the pension fund ranking task.

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
    report_path = workspace / "pension_ranking_report.md"
    if not report_path.exists():
        alternatives = ["ranking_report.md", "report.md", "pension_report.md", "pension_ranking.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "top_10_listed": 0.0,
            "ohio_first": 0.0,
            "pennsylvania_second": 0.0,
            "florida_third": 0.0,
            "bottom_states": 0.0,
            "grand_total": 0.0,
            "payee_count_ranking": 0.0,
            "geographic_analysis": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # Check top 10 listing — at least 8 of the actual top 10 states mentioned
    top_10_states = ["ohio", "pennsylvania", "florida", "michigan", "california",
                     "new york", "illinois", "indiana", "north carolina", "georgia"]
    mentioned = sum(1 for s in top_10_states if s in content_lower)
    scores["top_10_listed"] = 1.0 if mentioned >= 8 else (0.5 if mentioned >= 5 else 0.0)

    # Ohio as #1 by amount
    ohio_patterns = [
        r'ohio.*(?:536|first|#1|highest|top|rank.*1|largest)',
        r'(?:first|#1|highest|top|rank.*1|largest).*ohio',
        r'1[\.\)]\s*(?:oh[- ])?ohio',
        r'ohio.*\$?536',
    ]
    scores["ohio_first"] = 1.0 if any(re.search(p, content_lower) for p in ohio_patterns) else 0.0

    # Pennsylvania as #2
    pa_patterns = [
        r'pennsylvania.*(?:456|second|#2|rank.*2)',
        r'(?:second|#2|rank.*2).*pennsylvania',
        r'2[\.\)]\s*(?:pa[- ])?pennsylvania',
        r'pennsylvania.*\$?456',
    ]
    scores["pennsylvania_second"] = 1.0 if any(re.search(p, content_lower) for p in pa_patterns) else 0.0

    # Florida as #3
    fl_patterns = [
        r'florida.*(?:429|third|#3|rank.*3)',
        r'(?:third|#3|rank.*3).*florida',
        r'3[\.\)]\s*(?:fl[- ])?florida',
        r'florida.*\$?429',
    ]
    scores["florida_third"] = 1.0 if any(re.search(p, content_lower) for p in fl_patterns) else 0.0

    # Bottom states mentioned
    bottom_terms = ["northern mariana", "american samoa", "armed forces", "guam", "palau"]
    bottom_count = sum(1 for t in bottom_terms if t in content_lower)
    scores["bottom_states"] = 1.0 if bottom_count >= 3 else (0.5 if bottom_count >= 2 else 0.0)

    # Grand total
    grand_patterns = [
        r'5[,.]7\d*\s*billion',
        r'\$?5[,.]711',
        r'877[,.]?\d*\s*(?:thousand|payee|recipient)',
        r'483[,.]?\d*\s*(?:thousand|deferred)',
    ]
    grand_count = sum(1 for p in grand_patterns if re.search(p, content_lower))
    scores["grand_total"] = 1.0 if grand_count >= 2 else (0.5 if grand_count >= 1 else 0.0)

    # Payee count ranking (PA and OH should be top by count)
    payee_patterns = [
        r'pennsylvania.*78[,.]?119',
        r'ohio.*77[,.]?679',
        r'payee.*count.*pennsylvania',
        r'(?:most|highest).*(?:payee|recipient).*pennsylvania',
    ]
    scores["payee_count_ranking"] = 1.0 if any(re.search(p, content_lower) for p in payee_patterns) else 0.5 if "payee" in content_lower and "count" in content_lower else 0.0

    # Geographic analysis
    geo_patterns = [
        r'(?:rust\s*belt|midwest|industrial)',
        r'(?:geographic|regional|pattern)',
        r'(?:federal|government|military).*(?:employ|presence|base)',
        r'(?:northeast|southeast|sunbelt)',
    ]
    geo_count = sum(1 for p in geo_patterns if re.search(p, content_lower))
    scores["geographic_analysis"] = 1.0 if geo_count >= 2 else (0.5 if geo_count >= 1 else 0.0)

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

### 評分項 1：資料解析與正確性（權重 35%）

- 1.0：所有金額、領取人數與排名皆正確解析並回報。州總計精確符合預期值。
- 0.75：多數數值正確，僅有小幅四捨五入差異，或排名中有一州位置擺錯。
- 0.5：排名大致正確，但有多項數值解析錯誤，或將選區列與州總計混淆。
- 0.25：重大解析錯誤——金額錯誤、列類型混淆，或排名明顯不正確。
- 0.0：未能解析 CSV，或產出完全錯誤的結果。

### 評分項 2：排名完整性（權重 30%）

- 1.0：所有要求的排名皆具備：依金額的前 10、後 5、依領取人數的前段、Grand Total——每項都有佐證數字。
- 0.75：多數排名具備，僅有小幅缺漏（例如缺一種排名類型或缺佐證數字）。
- 0.5：只提供依金額的前 10，其他排名缺漏或不完整。
- 0.25：只有部分排名且資料缺漏。
- 0.0：沒有提供排名。

### 評分項 3：分析品質（權重 20%）

- 1.0：地理分析有洞見，將退休金集中與聯邦就業模式、軍事基地或歷史因素連結。指出有趣模式，如鏽帶（Rust Belt）的主導地位。
- 0.75：分析合理，有一些地理觀察。
- 0.5：表面觀察，缺乏更深入分析。
- 0.25：分析極少或模糊。
- 0.0：沒有提供分析。

### 評分項 4：報告結構（權重 15%）

- 1.0：markdown 組織良好，分區清楚，排名以表格或清單呈現，可讀性佳。
- 0.75：結構良好，僅有小幅排版問題。
- 0.5：有內容但組織不佳。
- 0.25：雜亂或不易閱讀。
- 0.0：沒有報告或空白檔案。
