---
id: task_earnings_analysis
name: |
  財報分析
category: analysis
grading_type: automated
timeout_seconds: 240
language: zh
locale: zh-TW
region: TW
source_task_id: task_earnings_analysis
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T048tw_earnings_analysis
workspace_files: []
---

# 財報分析


## Prompt

GitLab 在 2025 年第三季（Q3 2025）的利潤率（margin）指引（guidance）上，超出或未達多少個基點（basis points）？

請研究相關的財報發布（earnings release）或法說會逐字稿（transcript），判斷相關的指引利潤率與實際回報的利潤率，並把你的答案存到 `gitlab_margin_guidance.txt`。

請附上實際利潤率、指引利潤率，以及超出或未達的基點數。

（提醒：本任務僅供資訊與分析參考，不構成投資建議或財務建議，亦不取代專業財務意見。請務必在輸出中標明此為非投資建議，並僅根據查得的公開財報數據作答。）

## Expected Behavior

助手應該：

1. 辨識出 GitLab 所指的季度，以及管理層說明中相關的利潤率指標。
2. 找出指引水準與實際回報結果。
3. 把兩者差異換算成基點（basis points）。
4. 把答案存到 `gitlab_margin_guidance.txt`。

GitLab 的 Q3 FY2026 說明指出，非 GAAP 營業利潤率（non-GAAP operating margin）達到約 18%，比指引高出約 5 個百分點，因此優秀的答案會回報超出約 500 個基點。

助手應僅根據實際查得的公開財報數據作答，並標明此為資訊性分析、非投資建議。

## Grading Criteria

- [ ] 已建立 gitlab_margin_guidance.txt 檔案
- [ ] 檔案辨識出 GitLab 與該利潤率指標
- [ ] 檔案含有實際與指引的利潤率數值
- [ ] 檔案結論為 GitLab 超出指引約 500 個基點
- [ ] 說明精簡且易讀

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    workspace = Path(workspace_path)
    answer_file = workspace / "gitlab_margin_guidance.txt"

    if not answer_file.exists():
        return {
            "file_created": 0.0,
            "mentions_metric": 0.0,
            "has_actual_and_guidance": 0.0,
            "bp_conclusion": 0.0,
            "readable": 0.0,
        }

    content = answer_file.read_text(encoding="utf-8", errors="ignore")
    lowered = content.lower()

    scores = {"file_created": 1.0}
    scores["mentions_metric"] = 1.0 if ("gitlab" in lowered and "margin" in lowered and ("operating" in lowered or "non-gaap" in lowered)) else 0.0

    has_actual = bool(re.search(r"17\.9%|18%", lowered))
    has_guide = bool(re.search(r"13\.2%|13%|31\.0\s*-\s*32\.0|238\.0\s*-\s*239\.0", lowered))
    scores["has_actual_and_guidance"] = 1.0 if has_actual and has_guide else (0.5 if has_actual or has_guide else 0.0)

    bp_score = 0.0
    if re.search(r"500\s*basis points|500\s*bps|beat by 500|beat guidance by 500", lowered):
        bp_score = 1.0
    elif re.search(r"470\s*basis points|470\s*bps|469\s*basis points|469\s*bps|5\s*points above guidance|beat by 5 points", lowered):
        bp_score = 0.75
    elif re.search(r"beat", lowered) and re.search(r"basis points|bps", lowered):
        bp_score = 0.5
    scores["bp_conclusion"] = bp_score

    scores["readable"] = 1.0 if len(content.strip()) >= 35 else 0.0
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
