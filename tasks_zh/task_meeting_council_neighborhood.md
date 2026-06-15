---
id: task_meeting_council_neighborhood
name: Tampa City Council — 辨識社區與行政區提及
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_council_neighborhood
source_benchmark: pinchbench
claw_eval_id: P114zh_meeting_council_neighborhood
workspace_files:
- source: meetings/2026-04-02-tampa-city-council-transcript.md
  dest: transcript.md
grading_weights:
  automated: 0.5
  llm_judge: 0.5
---

# Tampa City Council — 辨識社區與行政區提及

## Prompt

我這裡有一份 2026 年 4 月 2 日舉行的 Tampa City Council 會議逐字稿，存放在 `transcript.md`。請產生 `neighborhoods_report.md`，辨識出所有提及的社區、行政區、地理區域與特定地點。請包含地點名稱、背景脈絡、相關發言者/議項，以及相關議題。整理時請納入以行政區（district）為基礎的概覽、出現次數統計，以及主題交叉對照。

## Expected Behavior

關鍵地點：Districts 1-5、Tampa Heights、Temple Crest（犯罪下降/McNeil）、Highland Pines（遊民問題）、West Tampa（Rome Yard、Rays stadium）、South Howard（街道封閉、管線）、Culbreath Bayou（人行道）、East Tampa（22nd St 開發）、Downtown、Bayshore、MacDill AFB、Riverwalk、變更分區地址（4102 N 22nd St、2707 E 22nd Ave、110 S Boulevard）、Marion/Franklin Streets、區域比較（Orlando、Fort Myers、Fort Lauderdale）。

## Grading Criteria

- [ ] 已建立報告檔案 neighborhoods_report.md
- [ ] Temple Crest 與 McNeil / 犯罪
- [ ] West Tampa 與 Rome Yard / Rays
- [ ] South Howard 與街道封閉 / 管線
- [ ] East Tampa 與開發
- [ ] Highland Pines 與遊民問題
- [ ] 3 個以上變更分區地址
- [ ] 提及 MacDill AFB
- [ ] 已記下 Riverwalk 連通關係
- [ ] 出現次數統計或交叉對照
- [ ] 15 個以上不同地點

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    scores = {}
    workspace = Path(workspace_path)
    report_path = workspace / "neighborhoods_report.md"
    if not report_path.exists():
        for alt in ["neighborhoods.md", "locations.md", "districts.md", "areas.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in ["report_created", "temple_crest", "west_tampa", "south_howard", "east_tampa", "highland_pines", "rezoning_addresses", "macdill", "riverwalk", "frequency_or_crossref", "location_count"]}
    scores["report_created"] = 1.0
    content = report_path.read_text()
    cl = content.lower()
    scores["temple_crest"] = 1.0 if (re.search(r'temple\s*crest', cl) and re.search(r'(?:crime|mcneil|officer|50th|busch)', cl)) else 0.0
    scores["west_tampa"] = 1.0 if (re.search(r'west\s*tampa', cl) and re.search(r'(?:rome\s*yard|ray|stadium|develop)', cl)) else 0.0
    scores["south_howard"] = 1.0 if (re.search(r'(?:south\s*howard|soho)', cl) and re.search(r'(?:street|pipe|stormwater|michelini)', cl)) else 0.0
    scores["east_tampa"] = 1.0 if (re.search(r'east\s*tampa', cl) and re.search(r'(?:develop|construct|22nd|build|rezon)', cl)) else 0.0
    scores["highland_pines"] = 1.0 if (re.search(r'highland\s*pines', cl) and re.search(r'(?:homeless|cornell|broadway)', cl)) else 0.0
    addresses = [r'4102.*22nd', r'2707.*22nd', r'110\s*south\s*boulevard']
    scores["rezoning_addresses"] = 1.0 if sum(1 for a in addresses if re.search(a, cl)) >= 3 else (0.5 if sum(1 for a in addresses if re.search(a, cl)) >= 2 else 0.0)
    scores["macdill"] = 1.0 if re.search(r'macdill', cl) else 0.0
    scores["riverwalk"] = 1.0 if (re.search(r'riverwalk', cl) and re.search(r'(?:rome|connect|extension|west|develop)', cl)) else 0.0
    scores["frequency_or_crossref"] = 1.0 if re.search(r'(?:frequen|count|cross[\s-]*ref|most\s*discuss)', cl) else 0.0
    location_patterns = [r'temple\s*crest', r'west\s*tampa', r'south\s*howard|soho', r'east\s*tampa', r'highland\s*pines', r'tampa\s*heights', r'culbreath', r'downtown', r'drew\s*park', r'hyde\s*park', r'ybor', r'bayshore', r'macdill', r'rome\s*yard', r'riverwalk', r'marion', r'franklin', r'port\s*tampa']
    found = sum(1 for l in location_patterns if re.search(l, cl))
    scores["location_count"] = 1.0 if found >= 15 else (0.75 if found >= 10 else (0.5 if found >= 6 else 0.0))
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

### 評分項 1：完整度（權重 35%）
**1.0 分**：20 個以上地點。**0.75 分**：15-19 個。**0.5 分**：10-14 個。**0.0 分**：少於 5 個。

### 評分項 2：背景脈絡（權重 25%）
**1.0 分**：每一地點皆有準確的背景脈絡。**0.5 分**：部分含糊。**0.0 分**：完全沒有。

### 評分項 3：組織（權重 25%）
**1.0 分**：依行政區分組、有出現次數、有交叉對照。**0.5 分**：部分。**0.0 分**：完全沒有。

### 評分項 4：廣度（權重 15%）
**1.0 分**：涵蓋多種尺度（從門牌地址到區域）。**0.5 分**：單一尺度。**0.0 分**：極少。
