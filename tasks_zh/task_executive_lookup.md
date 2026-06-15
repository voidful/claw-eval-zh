---
id: task_executive_lookup
name: 高階主管查詢
category: research
grading_type: automated
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_executive_lookup
source_benchmark: pinchbench
claw_eval_id: P013zh_executive_lookup
workspace_files: []
---

# 高階主管查詢

## Prompt

截至 2026 年 4 月 7 日，GitLab 的 CFO 是誰？

請研究答案，並將其儲存至 `gitlab_cfo.txt`。內容須包含該高階主管的全名，以及
一段簡短的來源說明或日期參照，以佐證該答案在 2026 年 4 月 7 日為現任資訊。

## Expected Behavior

助手應該：

1. 找出截至 2026 年 4 月 7 日 GitLab 的財務長（chief financial officer）
2. 使用可靠來源，例如 GitLab 投資人關係（investor relations）、新聞稿，
   或具公信力的財經報導
3. 在工作區建立 `gitlab_cfo.txt`
4. 寫入該 CFO 的全名與一段簡短的日期／來源說明

答案應簡潔且符合事實。若助手使用了網路工具，應依據 2026 年的最新資訊，而非
過時的歷史資料。

## Grading Criteria

- [ ] 已建立檔案 gitlab_cfo.txt
- [ ] 檔案指出 Jessica Ross 為 GitLab CFO
- [ ] 檔案提及 GitLab 與 CFO 職位
- [ ] 檔案包含 2026 年的日期或來源說明
- [ ] 答案簡潔且易讀

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    workspace = Path(workspace_path)
    answer_file = workspace / "gitlab_cfo.txt"

    if not answer_file.exists():
        return {
            "file_created": 0.0,
            "correct_name": 0.0,
            "mentions_role": 0.0,
            "has_date_or_source": 0.0,
            "readable": 0.0,
        }

    content = answer_file.read_text(encoding="utf-8", errors="ignore")
    lowered = content.lower()

    scores = {
        "file_created": 1.0,
        "correct_name": 1.0 if "jessica ross" in lowered else 0.0,
        "mentions_role": 1.0 if ("gitlab" in lowered and "cfo" in lowered) else 0.0,
        "has_date_or_source": 1.0 if re.search(r"2026|march 3, 2026|april 7, 2026|source|press release|investor", lowered) else 0.0,
        "readable": 1.0 if len(content.strip()) >= 20 and len(content.splitlines()) >= 1 else 0.0,
    }
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
