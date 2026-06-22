"""Grader for T136tw_meeting_gov_next_steps (Taiwan-localized from PinchBench `task_meeting_gov_next_steps`).

Phase 2 source: tasks_zh/task_meeting_gov_next_steps.md
Original file: tasks/task_meeting_gov_next_steps.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會（虛構）公聽會後續步驟擷取 grader。

    查核項皆改查工作區內的台灣逐字稿
    （dest=transcript.md）動態推導之事實，再與 agent 產生的中文報告
    next_steps.md 比對。報告為中文（轉換器會在其後接上中→英正規化 wrapper，
    但中文原文會被保留），故以中文關鍵字為主、英文為輔。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "final_report_timeline", "annual_report",
        "sensor_deployment", "data_sharing_circle", "budget_status",
        "open_questions", "timeframe_org", "responsible_parties",
        "timeline_viz",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "next_steps.md"
    if not report.exists():
        for alt in ["next_steps.txt", "後續步驟.md", "後續行動.md",
                    "follow_up.md", "followup.md", "action_items.md",
                    "actions.md", "後續步驟與行動.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出可查核事實（避免硬寫） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "meeting_transcript.md", "hearing.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    # 逐字稿以「**姓名（角色）：**」或「姓名（…）問／答／向…建議」標示發言者。
    speaker_candidates = set()
    for m in re.finditer(r'\*\*([一-鿿]{2,4})（', t):
        speaker_candidates.add(m.group(1))
    fallback_speakers = {
        "王志明", "陳冠宇", "林淑芬", "張庭瑋", "黃建宏", "周怡安",
        "蔡明翰", "郭佳穎", "高志遠", "李宗翰", "鄭立群", "白雅雯",
        "蕭文哲", "吳孟蓉",
    }
    speakers = {s for s in speaker_candidates
                if re.search(re.escape(s) + r'\s*[（(]', t)}
    if len(speakers) < 5:
        speakers = {s for s in fallback_speakers if s in t}
    if not speakers:
        speakers = fallback_speakers

    # 從逐字稿動態取出年度報告的提交日期（如「8 月 1 日」）。
    annual_date_re = (
        r'(\d{1,2})\s*月\s*(\d{1,2})\s*日|august\s*1|august\s*first|8\s*/\s*1')
    annual_date_in_t = bool(re.search(annual_date_re, t, re.IGNORECASE))

    # 從逐字稿動態取出資料共享聯盟的名稱（如「五方資料圈」）。
    circle_name = None
    mcir = re.search(r'(五方資料圈|[一-鿿]{1,4}資料圈)', t)
    if mcir:
        circle_name = mcir.group(1)

    scores = {"report_created": 1.0}

    # --- 1) 最終報告時程：今年夏天／7 月底前／發布於官方網站 ---
    report_patterns = [
        r'最終報告|final\s*report',
        r'今年夏天|這個?夏天|夏季|summer',
        r'7\s*月底|七月底|月底前|end\s*of\s*july|july',
        r'(?:發布|公布|刊登|上傳).{0,8}(?:官方)?網站|publish.*website|官方網站',
    ]
    rhits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in report_patterns)
    scores["final_report_timeline"] = (
        1.0 if rhits >= 2 else (0.5 if rhits >= 1 else 0.0))

    # --- 2) 年度報告須於提交日期（逐字稿之 8 月 1 日）前提交 ---
    annual_patterns = [
        r'年度(?:風險)?報告|annual\s*report',
        r'8\s*月\s*1\s*日|八月一日|八月\s*1\s*日|august\s*1|august\s*first|8\s*/\s*1',
        r'提交.{0,6}委員會|送交?.{0,6}委員會|呈報.{0,6}委員會|submit.*committee',
    ]
    ahits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in annual_patterns)
    # 至少要點到「年度報告」並帶到日期或提交對象；逐字稿確有 8 月 1 日才給滿分門檻。
    has_date_match = bool(
        re.search(r'8\s*月\s*1\s*日|八月一日|八月\s*1\s*日|august\s*1|august\s*first',
                  c, re.IGNORECASE))
    if re.search(r'年度(?:風險)?報告|annual\s*report', c, re.IGNORECASE):
        if annual_date_in_t and has_date_match:
            scores["annual_report"] = 1.0
        elif ahits >= 2:
            scores["annual_report"] = 1.0
        else:
            scores["annual_report"] = 0.5
    else:
        scores["annual_report"] = 0.0

    # --- 3) 偵測探針部署：專門打造的偵測探針／風險熱點／部署 ---
    sensor_patterns = [
        r'偵測探針|專門打造.{0,6}探針|專屬.{0,4}探針|purpose.?built|dedicated\s*sensor',
        r'部署.{0,6}(?:探針|感測|偵測)|deploy.*(?:sensor|probe)',
        r'風險熱點|熱點(?:領域|地區)|hotspot|surveillance',
        r'探針|感測器|sensor|probe',
    ]
    shits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in sensor_patterns)
    scores["sensor_deployment"] = (
        1.0 if shits >= 1 else 0.0)

    # --- 4) 跨國資料共享聯盟（逐字稿之「五方資料圈」／台日韓新澳） ---
    circle_patterns = [
        r'五方資料圈|[一-鿿]{1,4}資料圈',
        r'台日韓新澳|台、日、韓、新、澳|台.{0,2}日.{0,2}韓.{0,2}新.{0,2}澳',
        r'跨國.{0,4}資料共享|資料共享.{0,2}(?:聯盟|協議|協定)|data.?sharing',
    ]
    # 若能從逐字稿取出聯盟名稱，優先比對該名稱是否出現在報告。
    chits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in circle_patterns)
    if circle_name and circle_name in c:
        scores["data_sharing_circle"] = 1.0
    else:
        scores["data_sharing_circle"] = 1.0 if chits >= 1 else 0.0

    # --- 5) 預算／計畫狀態（未設常設計畫、無專屬經費、現在說還太早） ---
    budget_patterns = [
        r'未設立.{0,6}(?:常設)?.{0,4}計畫|沒有.{0,6}常設.{0,4}計畫|尚未.{0,4}設立.{0,4}計畫',
        r'(?:無|沒有|尚無).{0,6}(?:專屬|計畫性|常設).{0,4}經費|no\s*(?:dedicated|formal)?\s*fund',
        r'現在說(?:還)?太早|言之過早|為時尚早|too\s*early\s*to\s*say',
        r'(?:收到.{0,6}建議.{0,6}(?:再|後).{0,4}決定|再決定.{0,2}預算).{0,4}',
    ]
    bhits = sum(bool(re.search(p, c, re.IGNORECASE)) for p in budget_patterns)
    if bhits >= 1:
        scores["budget_status"] = 1.0
    elif re.search(r'預算|經費|計畫性|budget|fund', c, re.IGNORECASE):
        scores["budget_status"] = 0.5
    else:
        scores["budget_status"] = 0.0

    # --- 6) 待解問題：須有「待解／開放／尚無共識／辯論」+ 具體議題 ---
    open_markers = [
        r'待解|未解|尚未解決|開放問題|尚無共識|沒有共識|懸而未決|待釐清|有待',
        r'辯論|爭議|仍在(?:討論|辯論)|debate|unresolved|open\s*question|tbd',
    ]
    has_open = any(re.search(p, c, re.IGNORECASE) for p in open_markers)
    # 具體議題：範圍辯論 / 異常定義 / 原始資料 / 群眾外包串接 / 正式計畫
    has_scope = bool(re.search(
        r'範圍.{0,6}(?:辯論|爭議|界定)|生成式?內容.{0,8}(?:代理|跨系統)|聚焦.{0,4}範圍|scope',
        c, re.IGNORECASE))
    has_def = bool(re.search(
        r'(?:精確)?定義.{0,4}異常|異常.{0,4}(?:精確)?定義',
        c, re.IGNORECASE))
    has_raw = bool(re.search(
        r'原始.{0,4}(?:監測)?資料|未過濾.{0,4}資料|raw\s*data', c, re.IGNORECASE))
    has_specific = has_scope or has_def or has_raw
    if has_open and has_specific:
        scores["open_questions"] = 1.0
    elif has_open or has_specific:
        scores["open_questions"] = 0.5
    else:
        scores["open_questions"] = 0.0

    # --- 7) 依時間範圍組織 ---
    time_patterns = [
        r'即將進行|立即|數週|數周|未來幾週|短期',
        r'近期|數月|未來幾個?月|near.?term',
        r'長期|持續|數年|long.?term|ongoing',
        r'里程碑|時間軸|時程|milestone|timeline',
    ]
    tcount = sum(1 for p in time_patterns if re.search(p, c, re.IGNORECASE))
    scores["timeframe_org"] = (
        1.0 if tcount >= 3 else (0.5 if tcount >= 2 else 0.0))

    # --- 8) 負責方：報告中點名幾位逐字稿發言者，或幾個機關 ---
    named = {s for s in speakers if s in c}
    org_patterns = [
        r'數位治理委員會|本委員會|委員會',
        r'風析中心|風險研析中心',
        r'研析小組|本小組|小組',
        r'通監中心|通訊傳播監理中心',
    ]
    org_hits = sum(1 for p in org_patterns if re.search(p, c, re.IGNORECASE))
    party_total = len(named) + org_hits
    scores["responsible_parties"] = (
        1.0 if party_total >= 5 else (0.5 if party_total >= 3 else 0.0))

    # --- 9) 時間軸視覺化／里程碑摘要 + 至少 2 個日期關鍵字 ---
    viz_patterns = [r'時間軸', r'里程碑', r'milestone', r'timeline', r'時程表', r'路線圖']
    has_viz = any(re.search(p, c, re.IGNORECASE) for p in viz_patterns)
    date_hits = len(re.findall(
        r'8\s*月\s*1\s*日|八月一日|7\s*月底|七月底|今年夏天|夏季|數週|數月|數年|'
        r'august|july|summer',
        c, re.IGNORECASE))
    has_table = bool(re.search(r'\n\s*\|.*\|.*\n\s*\|?\s*[-:|\s]+\|', c))
    has_dates = date_hits >= 2
    if (has_viz or has_table) and has_dates:
        scores["timeline_viz"] = 1.0
    elif has_viz or has_table or has_dates:
        scores["timeline_viz"] = 0.5
    else:
        scores["timeline_viz"] = 0.0

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
