---
id: task_meeting_advisory_acronyms
name: NTIA 諮詢委員會縮寫詞彙表
category: meeting_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_meeting_advisory_acronyms
source_benchmark: pinchbench
claw_eval_id: P124zh_meeting_advisory_acronyms
workspace_files:
- source: meetings/2012-05-30-meeting-transcript-ntia-csmac.md
  dest: meeting-transcript.md
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# NTIA 諮詢委員會縮寫詞彙表

## Prompt

我有一份政府諮詢委員會的會議逐字稿，存放在 `meeting-transcript.md`。這是商務部頻譜管理諮詢委員會（Commerce Spectrum Management Advisory Committee, CSMAC）於 2012 年 5 月 30 日召開的會議，討論聯邦頻譜管理與共享。

請分析這份逐字稿，並在一個名為 `acronym_glossary.md` 的檔案中建立一份完整的縮寫詞彙表。對於每個找到的縮寫或簡稱，請列出：

- **縮寫（Acronym）**：逐字稿中使用的簡稱
- **全稱（Full form）**：它所代表的完整名稱
- **脈絡（Context）**：簡述它在本次會議中的使用方式（1-2 句）
- **類別（Category）**：政府機關（Government Agency）、頻譜／技術（Spectrum/Technical）、法規（Regulatory）、業界（Industry）、軍事（Military）或其他（Other）

請依縮寫的字母順序排序，並在最後附上找到的縮寫總數。

注意：有些縮寫可能在逐字稿中本身就有展開；其他則可能需要頻譜管理與電信政策的領域知識才能解讀。請擷取所有出現的縮寫，包含只出現一次的。

## Expected Behavior

助手應該：

1. 讀取並解析會議逐字稿
2. 辨識所有縮寫與簡稱
3. 由脈絡或領域知識判斷其全稱
4. 加以分類並排序

預期的關鍵縮寫（最低集合）：

| Acronym | Full Form | Category |
|---------|-----------|----------|
| CSMAC | Commerce Spectrum Management Advisory Committee | Government Agency |
| NTIA | National Telecommunications and Information Administration | Government Agency |
| FCC | Federal Communications Commission | Government Agency |
| NOAA | National Oceanic and Atmospheric Administration | Government Agency |
| DoD | Department of Defense | Government Agency |
| DHS | Department of Homeland Security | Government Agency |
| OMB | Office of Management and Budget | Government Agency |
| OSTP | Office of Science and Technology Policy | Government Agency |
| ITS | Institute for Telecommunication Sciences | Government Agency |
| ISART | International Symposium on Advanced Radio Technologies | Spectrum/Technical |
| MHz | Megahertz | Spectrum/Technical |
| GHz | Gigahertz | Spectrum/Technical |
| UAV | Unmanned Aerial Vehicle | Military |
| LTE | Long-Term Evolution | Industry |
| PCS | Personal Communications Service | Spectrum/Technical |
| AWS | Advanced Wireless Services | Spectrum/Technical |
| CMRS | Commercial Mobile Radio Service | Industry |
| STA | Special Temporary Authority | Regulatory |
| CSEA | Commercial Spectrum Enhancement Act | Regulatory |
| PCAST | President's Council of Advisors on Science and Technology | Government Agency |
| CTIA | Cellular Telecommunications Industry Association | Industry |
| TIA | Telecommunications Industry Association | Industry |
| TSB | Telecommunications Systems Bulletin | Spectrum/Technical |
| ITU-R | International Telecommunication Union - Radiocommunication | Spectrum/Technical |
| WRC | World Radiocommunication Conference | Spectrum/Technical |
| IP | Intellectual Property | Other |
| TMI | Too Much Information | Other |
| NFL | National Football League（隱喻指代大城市）| Other |

總計：約 25-30 個縮寫

## Grading Criteria

- [ ] 已建立 `acronym_glossary.md` 檔案
- [ ] CSMAC 正確展開
- [ ] NTIA 正確展開
- [ ] 辨識出至少 15 個不重複的縮寫
- [ ] 辨識出至少 20 個不重複的縮寫（加分門檻）
- [ ] 包含技術類縮寫（MHz、GHz、LTE、UAV、STA）
- [ ] 包含政府機關（FCC、DoD、DHS、OMB、OSTP）
- [ ] 對各項目套用類別或分組
- [ ] 採用字母順序排序

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the acronym glossary task.

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

    report_path = workspace / "acronym_glossary.md"
    if not report_path.exists():
        alternatives = ["glossary.md", "acronyms.md", "acronym_list.md"]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "csmac_expanded": 0.0,
            "ntia_expanded": 0.0,
            "min_15_acronyms": 0.0,
            "min_20_acronyms": 0.0,
            "technical_acronyms": 0.0,
            "gov_agencies": 0.0,
            "categories_applied": 0.0,
            "alphabetical_sort": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text()
    content_lower = content.lower()

    # CSMAC correctly expanded
    csmac_patterns = [
        r'commerce spectrum management advisory committee',
    ]
    scores["csmac_expanded"] = 1.0 if any(re.search(p, content_lower) for p in csmac_patterns) else 0.0

    # NTIA correctly expanded
    ntia_patterns = [
        r'national telecommunications and information administration',
        r'national telecommunications & information administration',
    ]
    scores["ntia_expanded"] = 1.0 if any(re.search(p, content_lower) for p in ntia_patterns) else 0.0

    # Count unique acronyms found (look for patterns like "ACRONYM" followed by expansion or in a list)
    # Count uppercase sequences of 2+ chars that appear as standalone entries
    acronym_candidates = set()
    known_acronyms = [
        "csmac", "ntia", "fcc", "noaa", "dod", "dhs", "omb", "ostp",
        "its", "isart", "mhz", "ghz", "uav", "lte", "pcs", "aws",
        "cmrs", "sta", "csea", "pcast", "ctia", "tia", "tsb",
        "itu", "wrc", "nfl", "ip", "tmi", "int"
    ]
    for acr in known_acronyms:
        if acr in content_lower:
            acronym_candidates.add(acr)

    # Also look for capitalized abbreviations in the content
    for match in re.finditer(r'\b[A-Z]{2,6}\b', content):
        acronym_candidates.add(match.group().lower())

    count = len(acronym_candidates)
    scores["min_15_acronyms"] = 1.0 if count >= 15 else (0.5 if count >= 10 else 0.0)
    scores["min_20_acronyms"] = 1.0 if count >= 20 else (0.5 if count >= 15 else 0.0)

    # Technical acronyms
    tech_acrs = ["mhz", "ghz", "lte", "uav", "sta", "pcs"]
    tech_found = sum(1 for t in tech_acrs if t in content_lower)
    scores["technical_acronyms"] = 1.0 if tech_found >= 4 else (0.5 if tech_found >= 2 else 0.0)

    # Government agencies
    gov_acrs = ["fcc", "dod", "dhs", "omb", "ostp", "noaa"]
    gov_found = sum(1 for g in gov_acrs if g in content_lower)
    scores["gov_agencies"] = 1.0 if gov_found >= 4 else (0.5 if gov_found >= 2 else 0.0)

    # Categories applied
    category_patterns = [
        r'(?:government|agency|agencies)',
        r'(?:technical|spectrum)',
        r'(?:regulatory|regulation)',
        r'(?:industry|commercial)',
        r'(?:military|defense)',
        r'(?:categor|type|group|classification)',
    ]
    cat_found = sum(1 for cp in category_patterns if re.search(cp, content_lower))
    scores["categories_applied"] = 1.0 if cat_found >= 3 else (0.5 if cat_found >= 2 else 0.0)

    # Alphabetical sorting check
    # Extract lines that start with acronyms and check if they're sorted
    acr_lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and re.match(r'[\*\-\|#]*\s*\**[A-Z]{2,}', stripped):
            # Extract the acronym
            match = re.search(r'[A-Z]{2,}', stripped)
            if match:
                acr_lines.append(match.group())

    if len(acr_lines) >= 5:
        sorted_lines = sorted(acr_lines)
        # Check if the order roughly matches alphabetical
        matches = sum(1 for a, b in zip(acr_lines, sorted_lines) if a == b)
        ratio = matches / len(acr_lines)
        scores["alphabetical_sort"] = 1.0 if ratio >= 0.7 else (0.5 if ratio >= 0.4 else 0.0)
    elif len(acr_lines) >= 2:
        scores["alphabetical_sort"] = 0.5
    else:
        scores["alphabetical_sort"] = 0.0

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

### 評分項 1：縮寫涵蓋度（權重 35%）

**1.0 分**：辨識出 25 個以上縮寫，包含冷僻的如 CSEA、ISART、TSB、CMRS，以及脈絡性用法如 NFL（隱喻）與 TMI。既涵蓋明顯的政府縮寫，也涵蓋技術性頻譜術語。

**0.75 分**：辨識出 20-24 個縮寫，涵蓋多數主要類別。

**0.5 分**：辨識出 15-19 個縮寫，涵蓋明顯的縮寫，但漏掉數個領域專有術語。

**0.25 分**：辨識出 10-14 個縮寫，大多只是廣為人知的政府機關。

**0.0 分**：辨識出的縮寫少於 10 個。

### 評分項 2：展開準確性（權重 30%）

**1.0 分**：所有縮寫展開皆正確。領域專有術語（CSEA、CSMAC、CMRS、ISART、TSB 10F）準確展開。

**0.75 分**：多數展開正確，僅有一兩處小錯。

**0.5 分**：常見縮寫正確，但數個領域專有縮寫錯誤或缺少展開。

**0.25 分**：多處展開錯誤。

**0.0 分**：展開大多錯誤或捏造。

### 評分項 3：脈絡品質（權重 20%）

**1.0 分**：每筆項目都包含有意義且貼合本次會議的脈絡描述，說明該縮寫與此次 CSMAC 討論的關聯。

**0.75 分**：多數項目有實用的脈絡。

**0.5 分**：有脈絡但偏籠統（只是重述展開，而非會議脈絡）。

**0.25 分**：脈絡極少或為樣板文字。

**0.0 分**：完全沒有提供脈絡。

### 評分項 4：組織與分類（權重 15%）

**1.0 分**：依字母排序，分類清楚（Government、Technical、Regulatory、Industry、Military、Other），全篇格式一致。

**0.75 分**：組織良好，僅有少許格式不一致。

**0.5 分**：有一些組織，但分類或排序不完整。

**0.25 分**：組織不佳。

**0.0 分**：沒有組織。
