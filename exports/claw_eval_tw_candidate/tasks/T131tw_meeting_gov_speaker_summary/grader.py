"""Grader for T131tw_meeting_gov_speaker_summary (Taiwan-localized from PinchBench `task_meeting_gov_speaker_summary`).

Phase 2 source: tasks_zh/task_meeting_gov_speaker_summary.md
Original file: tasks/task_meeting_gov_speaker_summary.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會（虛構）公聽會 發言者摘要 grader。

    對應原版 grader 的查核項，但改查台灣逐字稿（dest=transcript.md）
    推導之事實 + agent 的中文報告 speaker_summary.md。僅用標準函式庫。
    報告為繁體中文，故以中文關鍵字／數值比對；可查核的數值（800、2-5%、
    每月 3-5 件、14000、4500 萬）優先從逐字稿動態讀出再比對。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "wang_zhiming", "lin_shufen", "chen_guanyu",
        "zhang_tingwei", "ncra_speaker", "additional_panelists",
        "quotes_included", "speaker_order",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "speaker_summary.md"
    if not report.exists():
        for alt in ["speakers.md", "summary.md", "speaker_summaries.md",
                    "發言者摘要.md", "speaker_summary.txt"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出可查核的數值（避免硬寫；逐字稿缺漏時退回其載明之事實） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "tw_gov_hearing.md", "meeting_transcript.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def first(pattern, text, default=None, group=1):
        m = re.search(pattern, text)
        return m.group(group) if m else default

    # AIRC 案例件數（逐字稿：「超過 800 件」）
    case_count = first(r'超過\s*(\d{3,})\s*件', t) or first(r'(\d{3,})\s*多?\s*件', t) or "800"
    # 真正異常比例（逐字稿：「2% 到 5%」「約 2%–5%」）
    anom_lo = first(r'(\d+)\s*%\s*(?:到|–|-|~|～)\s*\d+\s*%', t) or "2"
    anom_hi = first(r'\d+\s*%\s*(?:到|–|-|~|～)\s*(\d+)\s*%', t) or "5"
    # NCRA 每月通報件數（逐字稿：「每月只回報 3 到 5 件」「每月只有 3–5 件」）
    rep_lo = first(r'每月[^。]{0,12}?(\d+)\s*(?:到|–|-|~|～)\s*\d+\s*件', t) or "3"
    rep_hi = first(r'每月[^。]{0,12}?\d+\s*(?:到|–|-|~|～)\s*(\d+)\s*件', t) or "5"
    # NCRA 第一線人力（逐字稿：「約 14,000 名」）
    staff = first(r'約\s*([\d,]{4,})\s*名', t)
    staff = staff.replace(",", "") if staff else "14000"

    def has(*pats):
        return any(re.search(p, c, re.IGNORECASE) for p in pats)

    scores = {"report_created": 1.0}

    # --- 王志明（指定主辦官員）：開場、騷擾、無常設計畫／無計畫性經費 ---
    has_wang = has(r'王志明', r'執行秘書', r'指定主辦官員')
    wang_pts = sum([
        bool(has(r'騷擾', r'恐嚇', r'威脅', r'harass')),
        bool(has(r'公聽會', r'行政程序法', r'指定主辦官員')),
        bool(has(r'沒有.{0,6}(?:計畫性)?經費', r'並未設立.{0,8}計畫', r'常設.{0,6}計畫',
                 r'無.{0,6}經費', r'去污名|污名')),
    ])
    scores["wang_zhiming"] = 1.0 if (has_wang and wang_pts >= 2) else (0.5 if has_wang else 0.0)

    # --- 林淑芬（副主任委員）：資料品質、機敏分級、開放資料 ---
    has_lin = has(r'林淑芬', r'副主任委員', r'副主委')
    lin_pts = sum([
        bool(has(r'機敏', r'機密', r'分級', r'classif')),
        bool(has(r'校準', r'可重現', r'資料品質', r'calibrat')),
        bool(has(r'開放資料', r'data\.gov\.tw', r'open\s*data', r'去識別化')),
    ])
    scores["lin_shufen"] = 1.0 if (has_lin and lin_pts >= 2) else (0.5 if has_lin else 0.0)

    # --- 陳冠宇（召集人）：FRB 比喻、校準、公民科學、異常是發現的引擎 ---
    has_chen = has(r'陳冠宇', r'召集人')
    chen_pts = sum([
        bool(has(r'快速電波爆發', r'電波爆發', r'\bFRB\b')),
        bool(has(r'校準', r'高品質.{0,4}資料', r'可重現', r'calibrat')),
        bool(has(r'公民科學', r'群眾參與', r'citizen\s*science')),
        bool(has(r'異常.{0,8}引擎', r'發現的引擎', r'先把.{0,4}正常')),
    ])
    scores["chen_guanyu"] = 1.0 if (has_chen and chen_pts >= 2) else (0.5 if has_chen else 0.0)

    # --- 張庭瑋／AIRC：800+ 件、2-5% 異常、解密影像 ---
    has_zhang = has(r'張庭瑋', r'AIRC', r'風險研析中心')
    cc = re.escape(case_count)
    lo = re.escape(anom_lo)
    hi = re.escape(anom_hi)
    # 比例需出現「lo…hi%」對應（如 2% 到 5%、2-5%、2–5%）
    anom_num = re.search(r'%s\s*%%?\s*(?:到|–|-|~|～|至)\s*%s\s*%%' % (lo, hi), c) \
        or re.search(r'%s\s*(?:到|–|-|~|～|至)\s*%s\s*%%' % (lo, hi), c)
    zhang_pts = sum([
        bool(re.search(r'(?:超過\s*)?%s\s*多?\s*件' % cc, c) or re.search(r'\b%s\b' % cc, c)),
        bool(anom_num),
        bool(has(r'解密', r'解密.{0,4}影像', r'案例影像', r'誤判', r'測試流量')),
        bool(has(r'五方資料圈', r'群眾外包', r'非監督式', r'監督式', r'同儕審查', r'假影')),
    ])
    scores["zhang_tingwei"] = 1.0 if (has_zhang and zhang_pts >= 2) else (0.5 if has_zhang else 0.0)

    # --- 黃建宏／NCRA：監測、每月 3-5 件、人力、過濾／保存限制 ---
    has_ncra = has(r'黃建宏', r'NCRA', r'通訊傳播監理署', r'監理組')
    rl = re.escape(rep_lo)
    rh = re.escape(rep_hi)
    rep_num = re.search(r'每月[^。\n]{0,12}?%s\s*(?:到|–|-|~|～|至)\s*%s\s*件' % (rl, rh), c) \
        or re.search(r'%s\s*(?:到|–|-|~|～|至)\s*%s\s*件' % (rl, rh), c)
    st = re.escape(staff)
    ncra_pts = sum([
        bool(has(r'監測', r'監看', r'監理', r'稽核探針', r'surveillance')),
        bool(rep_num),
        bool(re.search(r'%s' % st, c.replace(",", "")) or has(r'14[,，]?000', r'14000')),
        bool(has(r'過濾', r'濾掉', r'輪替刪除', r'保存.{0,4}數個月', r'骨幹', r'終端側', r'ADS-B', r'自願標示')),
    ])
    scores["ncra_speaker"] = 1.0 if (has_ncra and ncra_pts >= 2) else (0.5 if has_ncra else 0.0)

    # --- 其餘小組成員（至少 3 位：周怡安、蔡明翰、郭佳穎、高志遠、蕭文哲、白雅雯、鄭立群、吳孟蓉、李宗翰） ---
    additional = 0
    for name in [r'周怡安', r'蔡明翰', r'郭佳穎', r'高志遠', r'蕭文哲',
                 r'白雅雯', r'鄭立群', r'吳孟蓉', r'李宗翰']:
        if re.search(name, c):
            additional += 1
    scores["additional_panelists"] = 1.0 if additional >= 4 else (0.5 if additional >= 2 else 0.0)

    # --- 直接引言：尋找成對引號（「…」或 "…"）且含實質內容 ---
    quote_patterns = re.findall(r'[「『“"].{8,}?[」』”"]', c)
    scores["quotes_included"] = 1.0 if len(quote_patterns) >= 3 else (0.5 if len(quote_patterns) >= 1 else 0.0)

    # --- 出場順序：王志明／林淑芬／陳冠宇在前 -> 張庭瑋居中 -> 黃建宏／NCRA 在後 ---
    def pos(*pats):
        best = -1
        for p in pats:
            m = re.search(p, c)
            if m and (best < 0 or m.start() < best):
                best = m.start()
        return best
    early = pos(r'王志明', r'林淑芬', r'陳冠宇')
    mid = pos(r'張庭瑋')
    late = pos(r'黃建宏', r'NCRA', r'通訊傳播監理署')
    if early >= 0 and mid >= 0 and late >= 0:
        scores["speaker_order"] = 1.0 if early < mid < late else 0.5
    elif early >= 0 and mid >= 0:
        scores["speaker_order"] = 1.0 if early < mid else 0.5
    else:
        scores["speaker_order"] = 0.0

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
PRIMARY_DIMENSIONS = ['completion', 'safety']


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
