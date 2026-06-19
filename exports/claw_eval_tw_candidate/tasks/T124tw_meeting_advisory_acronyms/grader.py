"""Grader for T124tw_meeting_advisory_acronyms (Taiwan-localized from PinchBench `task_meeting_advisory_acronyms`).

Phase 2 source: tasks_zh/task_meeting_advisory_acronyms.md
Original file: tasks/task_meeting_advisory_acronyms.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """頻譜共用顧問委員會（虛構）縮寫詞彙表 grader。

    以工作區內的台灣逐字稿（dest=meeting-transcript.md）動態推導「應有的縮寫
    與中文全稱」，再比對 agent 產出的中文報告 acronym_glossary.md。
    縮寫本身為拉丁字母，逐字稿與報告皆原樣保留，故以「縮寫 + 中文全稱關鍵詞」
    雙重比對。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "dgc_expanded", "osm_expanded",
        "min_15_acronyms", "min_20_acronyms", "technical_acronyms",
        "gov_agencies", "categories_applied", "alphabetical_sort",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "acronym_glossary.md"
    if not report.exists():
        for alt in ["glossary.md", "acronyms.md", "acronym_list.md",
                    "acronym_glossary.txt", "縮寫詞彙表.md", "詞彙表.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")
    c_lower = c.lower()

    # --- 從逐字稿動態讀出「應有的縮寫對照」（避免硬寫） ---
    tpath = workspace / "meeting-transcript.md"
    if not tpath.exists():
        for alt in ["meeting_transcript.md", "transcript.md",
                    "meeting-transcript.txt"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    # 逐字稿中所有「縮寫 → 中文全稱」候選：
    #   先用對照表段落（| 縮寫 | 全稱… |）抓出明確映射，
    #   再用全文出現過的拉丁縮寫補齊。
    tw_acr_full = {}  # 縮寫(大寫) -> 中文全稱字串（取第一個中文片段）
    for line in t.split("\n"):
        m = re.match(r"\s*\|\s*([A-Za-z][A-Za-z0-9\-]{1,7})\s*\|\s*([^|]+)\|", line)
        if m:
            acr = m.group(1).upper()
            full = m.group(2).strip()
            if acr not in tw_acr_full:
                tw_acr_full[acr] = full

    # 全文出現過的拉丁縮寫（2~6 字，含連字號如 ITU-R）。
    transcript_acrs = set()
    for mm in re.finditer(r"\b([A-Z]{2,6}(?:-[A-Z])?)\b", t):
        transcript_acrs.add(mm.group(1).upper())
    # WG1~WG5 之類帶數字者另計
    for mm in re.finditer(r"\bWG[1-9]\b", t):
        transcript_acrs.add(mm.group(0).upper())

    def acr_in_report(acr):
        # 縮寫在報告中出現（大小寫不敏感，作為獨立詞）
        return re.search(r"\b" + re.escape(acr) + r"\b", c, re.IGNORECASE) is not None

    def chinese_full_in_report(acr):
        """逐字稿對照表給出的中文全稱，其關鍵詞是否也出現在報告中。"""
        full = tw_acr_full.get(acr, "")
        # 取中文片段（連續 2 字以上的 CJK），任一片段命中即可
        frags = re.findall(r"[一-鿿]{2,}", full)
        for f in frags:
            if f and f in c:
                return True
        return False

    scores = {"report_created": 1.0}

    # --- DGC：須出現縮寫 DGC 且報告含「數位治理委員會」（從逐字稿動態取） ---
    dgc_full = tw_acr_full.get("DGC", "數位治理委員會")
    dgc_frag = (re.findall(r"[一-鿿]{4,}", dgc_full) or ["數位治理委員會"])[0]
    scores["dgc_expanded"] = 1.0 if (
        acr_in_report("DGC") and (dgc_frag in c or "數位治理委員會" in c)
    ) else 0.0

    # --- OSM：須出現縮寫 OSM 且報告含「頻譜管理署」 ---
    osm_full = tw_acr_full.get("OSM", "頻譜管理署")
    osm_frag = (re.findall(r"[一-鿿]{3,}", osm_full) or ["頻譜管理署"])[0]
    scores["osm_expanded"] = 1.0 if (
        acr_in_report("OSM") and ("頻譜管理署" in c or osm_frag in c)
    ) else 0.0

    # --- 不重複縮寫計數：報告中出現、且確實是逐字稿中存在的縮寫 ---
    # 以逐字稿縮寫集合為基準，避免把報告裡隨意大寫詞（如英文段落）灌水。
    found_acrs = set()
    for acr in transcript_acrs:
        if acr_in_report(acr):
            found_acrs.add(acr)
    # 報告自身額外出現、且為已知頻譜縮寫者亦可計入（容錯）
    known = {"DGC", "SCAB", "NCC", "MODA", "OSM", "OSTP", "OMB", "ITS",
             "NOAA", "DOD", "ISART", "MHZ", "GHZ", "LTE", "UAV", "PCS",
             "AWS", "CMRS", "STA", "CSEA", "PCAST", "CTIA", "TIA", "TSB",
             "ITU", "ITU-R", "WRC", "EW", "DGO", "DZX", "NESA", "PINF",
             "IP", "TMI", "NFL", "WG1", "WG2", "WG3", "WG4", "WG5", "NC"}
    for acr in known:
        if acr_in_report(acr):
            found_acrs.add(acr)
    count = len(found_acrs)
    scores["min_15_acronyms"] = 1.0 if count >= 15 else (0.5 if count >= 10 else 0.0)
    scores["min_20_acronyms"] = 1.0 if count >= 20 else (0.5 if count >= 15 else 0.0)

    # --- 技術類縮寫（MHz、GHz、LTE、UAV、STA、PCS） ---
    tech_acrs = ["MHZ", "GHZ", "LTE", "UAV", "STA", "PCS"]
    tech_found = sum(1 for a in tech_acrs if acr_in_report(a))
    scores["technical_acronyms"] = 1.0 if tech_found >= 4 else (0.5 if tech_found >= 2 else 0.0)

    # --- 政府機關縮寫（OSM、OSTP、OMB、ITS、SCAB、DGC） ---
    gov_acrs = ["OSM", "OSTP", "OMB", "ITS", "SCAB", "DGC"]
    gov_found = sum(1 for a in gov_acrs if acr_in_report(a))
    scores["gov_agencies"] = 1.0 if gov_found >= 4 else (0.5 if gov_found >= 2 else 0.0)

    # --- 類別／分組：報告須出現數種類別關鍵詞（中英皆可） ---
    category_patterns = [
        r"政府|機關|agency|agencies|government",
        r"頻譜|技術|technical|spectrum",
        r"法規|法令|regulator|regulation",
        r"業界|產業|industry|commercial",
        r"軍事|國防|military|defense",
        r"類別|分類|categor|group|分組",
    ]
    cat_found = sum(1 for p in category_patterns if re.search(p, c, re.IGNORECASE))
    scores["categories_applied"] = 1.0 if cat_found >= 3 else (0.5 if cat_found >= 2 else 0.0)

    # --- 字母排序：抽出各行開頭的縮寫，檢查是否大致依字母排序 ---
    acr_lines = []
    for line in c.split("\n"):
        s = line.strip()
        if not s:
            continue
        # 列表／表格／標題列開頭抓第一個拉丁縮寫
        m = re.match(r"[\*\-\|#>\s]*\**\s*([A-Z]{2,}(?:-[A-Z])?|WG[1-9])\b", s)
        if m:
            acr_lines.append(m.group(1).upper())

    if len(acr_lines) >= 5:
        sorted_lines = sorted(acr_lines)
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


# --- Optional Claw-Eval adapter (only active when `claw_eval` is importable) ---
# Keeps grader.py importable offline (tests / PinchBench runner use grade()),
# while becoming a drop-in AbstractGrader subclass inside a real claw_eval
# checkout. See docs/claw_eval_zh_schema.md section 8.
PRIMARY_DIMENSIONS = ['completion']


def to_dimension_scores(component_scores: dict) -> dict:
    """Map flat component scores into completion/safety/robustness (plain dict)."""
    vals = [float(v) for v in component_scores.values() if isinstance(v, (int, float))]
    completion = round(sum(vals) / len(vals), 4) if vals else 0.0
    return {"completion": completion, "safety": 1.0, "robustness": 1.0}


try:  # pragma: no cover - exercised only with claw_eval installed
    from claw_eval.graders.base import AbstractGrader
    from claw_eval.models.trace import DimensionScores

    _CLAW_EVAL_AVAILABLE = True
except Exception:  # noqa: BLE001
    _CLAW_EVAL_AVAILABLE = False


if _CLAW_EVAL_AVAILABLE:  # pragma: no cover

    def _messages_to_transcript(messages):
        """Best-effort conversion of Claw-Eval TraceMessages to PinchBench events."""
        transcript = []
        for m in messages:
            role = m.message.role
            content = []
            text = getattr(m.message, "text", "") or ""
            if text:
                content.append({"type": "text", "text": text})
            transcript.append(
                {"type": "message", "message": {"role": role, "content": content}}
            )
        return transcript

    def _reconstruct_workspace(env_snapshot):
        """Write env_snapshot files to a temp dir and return its path (or '')."""
        if not env_snapshot:
            return ""
        import tempfile
        from pathlib import Path as _Path

        root = _Path(tempfile.mkdtemp(prefix="claw_eval_zh_ws_"))
        files = env_snapshot.get("files", env_snapshot) if isinstance(env_snapshot, dict) else {}
        if isinstance(files, dict):
            for rel, body in files.items():
                try:
                    dest = root / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if isinstance(body, bytes):
                        dest.write_bytes(body)
                    else:
                        dest.write_text(str(body), encoding="utf-8")
                except OSError:
                    pass
        return str(root)

    class ClawEvalZhGrader(AbstractGrader):
        """Adapter that wraps the module-level grade() into DimensionScores."""

        def grade(self, messages, dispatches, task, audit_data=None, judge=None,
                  media_events=None, env_snapshot=None):
            transcript = _messages_to_transcript(messages)
            workspace = _reconstruct_workspace(env_snapshot)
            component_scores = grade(transcript, workspace)
            scores = DimensionScores()
            dims = to_dimension_scores(component_scores)
            scores.completion = dims["completion"]
            scores.safety = dims["safety"]
            scores.robustness = self.compute_robustness(dispatches)
            scores.efficiency_turns = len(
                [m for m in messages if m.message.role == "assistant"]
            )
            return scores
