---
id: task_executive_lookup
name: 查詢台積電現任財務長（CFO）
category: research
grading_type: automated
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_executive_lookup
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: manual_review_only
claw_eval_tw_id: T013tw_executive_lookup
workspace_files: []
---

# 查詢台積電現任財務長（CFO）

## Prompt

請查詢台灣積體電路製造公司（台積電 / TSMC，股票代號 2330）目前的財務長（CFO）是誰。

請把答案存到 tsmc_cfo.txt，內容包含：該主管的姓名與職稱，以及一段**來源說明或查詢
日期**，以佐證此資訊為查詢當下最新。

注意：公司高階主管屬公開資訊；這是即時資料，請標明查詢日期與來源，若不確定請說明，
不要捏造。檔名 tsmc_cfo.txt 不可更改。

## Expected Behavior

助手應透過網路查詢台積電（2330）目前的財務長，並把姓名、職稱與來源／查詢日期寫入
tsmc_cfo.txt。因為高層人事可能異動，正確行為是**標明查詢日期與來源並說明不確定性**，
而非寫死某個過期答案。

## Grading Criteria

- [ ] 建立檔案 tsmc_cfo.txt
- [ ] 提及台積電 / TSMC / 2330 與財務長 / CFO
- [ ] 提供一位主管姓名
- [ ] 包含查詢日期或來源說明

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """TW executive lookup (台積電 CFO). Live data: checks company+role+source
    presence, not a hard-coded name value (reproducibility)."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    f = workspace / "tsmc_cfo.txt"
    if not f.exists():
        for alt in ["cfo.txt", "executive.txt"]:
            if (workspace / alt).exists():
                f = workspace / alt
                break
    if not f.exists():
        return {"file_created": 0.0, "mentions_role": 0.0,
                "has_name": 0.0, "has_date_or_source": 0.0}
    content = f.read_text(encoding="utf-8", errors="ignore")
    low = content.lower()
    scores = {"file_created": 1.0}
    company = bool(re.search(r'台積電|臺積電|tsmc|2330', low))
    role = bool(re.search(r'cfo|財務長|財務主管', low))
    scores["mentions_role"] = 1.0 if (company and role) else (0.5 if (company or role) else 0.0)
    # a plausible name token (Chinese 2-4 chars or a Latin capitalized name)
    scores["has_name"] = 1.0 if re.search(r'[一-鿿]{2,4}\s*(?:先生|女士|執行|財務長|CFO)|[A-Z][a-z]+\s+[A-Z][a-z]+', content) else 0.0
    scores["has_date_or_source"] = 1.0 if re.search(
        r'\d{4}|查詢日期|來源|source|press|investor|官網|公開資訊', low) else 0.0
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
