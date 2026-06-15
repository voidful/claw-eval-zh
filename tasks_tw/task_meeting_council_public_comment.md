---
id: task_meeting_council_public_comment
name: |
  市議會逐字稿 — 摘要公眾意見
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_meeting_council_public_comment
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T110tw_meeting_council_public_comment
workspace_files:
- source: meetings/2026-04-02-tampa-city-council-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# 市議會逐字稿 — 摘要公眾意見


## Prompt

我手邊有一份 2026 年 4 月 2 日舉行的 Tampa City Council 會議逐字稿，存放在 `transcript.md`。這是一份即時聽打的字幕稿。

請幫我分析公眾意見（public comment）的部分，並產生一個名為 `public_comments_report.md` 的檔案，摘要每一位公眾發言者的意見。針對每位發言者，請包含：

- **發言者姓名**
- **提及的主題或議程項目**（若適用）
- **提出的重點或關切事項**
- **對議會提出的任何具體請求或要求**

最後也請附上一個**主題摘要（thematic summary）**，依主題領域（例如基礎建設、住房、歷史保存、警政、交通等）將意見分組，並指出哪些主題引發最多公眾關注。

## Expected Behavior

助手應辨識出公眾意見的部分，並擷取每位發言者的發言內容。關鍵發言者：

- **Jeraldine Williams** — Zion Cemetery（第 16 項），感謝議會
- **Reva Iman** — Zion Cemetery，請求 $8 million 用於紀念/族譜中心
- **Daryl Hych** — Veterans Advisory Committee（第 22 項），DEI 相關評論
- **Pam Cannella** — 雨水/颶風整備，市府疏於處理
- **David Moss Cornell** — Highland Pines（District 5）的遊民問題
- **Joseph Citro** — 交通、tri-county MPO、Rays stadium 交通
- **Ashley Morrow** — Tampa 黑人歷史（1877 Hernando County）
- **Carroll Ann Bennett** — 人行道法規漏洞、Culbreath Bayou
- **Tiffany Poole** — TPD 事件、15 歲的兒子、8 名警員對付兩名未成年人
- **Steve Michelini** — South Howard 街道封閉、管線/雨水
- **James Adair** — 市府自 2020 年起未使用的發電機
- **Robin Lockett** — Zion Cemetery 與 Yellow Jackets
- **Valerie Bullock** — 第 19-21 項分區、Aquino Property Management
- **Stephanie Poynor** — Rome Yard 延宕（1436 days）、veterans board
- **Michael Randolph**（線上）— West Tampa CDC、Rome Yard CBA
- **Adrian Rodriguez**（線上）— Colon Cemetery、Florida Statute 872

## Grading Criteria

- [ ] 已建立報告檔案 public_comments_report.md
- [ ] 已辨識 Jeraldine Williams 與 Zion Cemetery 的關聯
- [ ] 已辨識 Reva Iman 與 $8 million 請求
- [ ] 已辨識 Pam Cannella 與雨水/颶風
- [ ] 已辨識 Tiffany Poole 與 TPD 事件
- [ ] 已辨識 Stephanie Poynor 與 Rome Yard（1436 days）
- [ ] 16 位發言者中至少辨識出 12 位
- [ ] 依主題分組的主題摘要
- [ ] Zion Cemetery 被記為多位發言者共同提及的主題

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    scores = {}
    workspace = Path(workspace_path)
    report_path = workspace / "public_comments_report.md"
    if not report_path.exists():
        for alt in ["public_comments.md", "comments_report.md", "comments.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in ["report_created", "williams_zion", "iman_8million", "cannella_stormwater", "poole_tpd", "poynor_romeyard", "speaker_count", "thematic_summary", "zion_multiple"]}
    scores["report_created"] = 1.0
    content = report_path.read_text()
    cl = content.lower()
    scores["williams_zion"] = 1.0 if (re.search(r'jeraldine|j\.?\s*williams', cl) and re.search(r'zion', cl)) else 0.0
    scores["iman_8million"] = 1.0 if (re.search(r'reva|iman', cl) and re.search(r'(?:\$?8\s*million|8m)', cl)) else 0.0
    scores["cannella_stormwater"] = 1.0 if (re.search(r'cannella|pam\s*c', cl) and re.search(r'(?:stormwater|hurricane|flood)', cl)) else 0.0
    scores["poole_tpd"] = 1.0 if (re.search(r'(?:tiffany|poole)', cl) and re.search(r'(?:son|child|minor|tpd|police|officer|e-?bike|body\s*cam)', cl)) else 0.0
    scores["poynor_romeyard"] = 1.0 if (re.search(r'(?:stephanie|poynor)', cl) and re.search(r'(?:rome\s*yard|1436)', cl)) else 0.0
    speaker_names = [r'jeraldine', r'reva|iman', r'daryl|hych', r'cannella', r'cornell', r'citro', r'ashley\s*morrow', r'bennett', r'tiffany|poole', r'michelini', r'adair', r'lockett', r'bullock', r'poynor', r'randolph', r'rodriguez']
    found = sum(1 for pat in speaker_names if re.search(pat, cl))
    scores["speaker_count"] = 1.0 if found >= 14 else (0.75 if found >= 12 else (0.5 if found >= 8 else 0.0))
    themes = [r'(?:theme|thematic|topic|categor|group)', r'(?:infrastructure|housing|histor|polic|transport)']
    scores["thematic_summary"] = 1.0 if all(re.search(t, cl) for t in themes) else 0.0
    zion_speakers = sum(1 for pat in [r'(?:jeraldine|williams).*zion|zion.*(?:jeraldine|williams)', r'(?:reva|iman).*zion|zion.*(?:reva|iman)', r'(?:robin|lockett).*zion|zion.*(?:robin|lockett)'] if re.search(pat, cl))
    scores["zion_multiple"] = 1.0 if zion_speakers >= 2 else (0.5 if zion_speakers >= 1 else 0.0)
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

### 評分項 1：發言者辨識（權重 35%）
**1.0 分**：辨識出全部 16 位發言者且主題正確。**0.75 分**：12-15 位。**0.5 分**：8-11 位。**0.0 分**：完全沒有。

### 評分項 2：摘要品質（權重 30%）
**1.0 分**：準確掌握重點與請求。**0.5 分**：有附上但細節缺漏。**0.0 分**：完全沒有。

### 評分項 3：主題分組（權重 20%）
**1.0 分**：清楚辨識出主題。**0.5 分**：有部分分組。**0.0 分**：完全沒有。

### 評分項 4：組織（權重 15%）
**1.0 分**：格式良好、依時間先後。**0.5 分**：組織不佳。**0.0 分**：難以閱讀。
