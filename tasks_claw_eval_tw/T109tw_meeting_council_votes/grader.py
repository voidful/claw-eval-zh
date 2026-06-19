"""Grader for T109tw_meeting_council_votes (Taiwan-localized from PinchBench `task_meeting_council_votes`).

Phase 2 source: tasks_zh/task_meeting_council_votes.md
Original file: tasks/task_meeting_council_votes.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """南港市議會（虛構）表決彙整 grader。

    以工作區內的台灣逐字稿（dest=transcript.md）動態推導「應有事實」，
    再比對 agent 產生的中文報告 votes_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "votes_report.md"
    if not report.exists():
        for alt in ["votes.md", "motions.md", "vote_report.md", "vote_report.txt"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = [
        "report_created", "budget_vote", "recuse_item", "rollcall_item",
        "unanimous_item", "first_reading_item", "continued_item",
        "item25_dissent", "summary_count",
    ]
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出可查核事實（避免硬寫） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "meeting_transcript.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def first(pattern, text, default=None, group=1):
        m = re.search(pattern, text)
        return m.group(group) if m else default

    def section(text, anchors, window=220):
        """取報告中第一個命中任一錨點關鍵字之後的片段（僅向後看，避免跨議案誤判）。

        票數通常寫在議案標題之後，故自錨點起向後取一段窗口，不向前回看，以免
        抓到上一個議案的票數而誤判。
        """
        for a in anchors:
            m = re.search(a, text)
            if m:
                return text[m.start():m.end() + window]
        return ""

    # 預算案票數：逐字稿「N 票贊成、0 票反對，全體一致通過」（跨行抓取）
    budget_for = first(
        r'年度總預算追加案[\s\S]{0,120}?(\d+)\s*票贊成、(\d+)\s*票反對', t) \
        or first(r'(\d+)\s*票贊成、0\s*票反對，全體一致通過', t)
    budget_against = first(
        r'年度總預算追加案[\s\S]{0,120}?\d+\s*票贊成、(\d+)\s*票反對', t,
        group=1) or "0"
    # 第二十五案票數：逐字稿「贊成 N 票，反對 M 票（卡爾森 反對）」（跨行抓取）
    item25_for = first(
        r'前瞻補助[\s\S]{0,200}?贊成\s*(\d+)\s*票，反對\s*(\d+)\s*票（卡爾森', t) \
        or first(r'贊成\s*(\d+)\s*票，反對\s*1\s*票（卡爾森', t)
    item25_against = first(
        r'前瞻補助[\s\S]{0,200}?贊成\s*\d+\s*票，反對\s*(\d+)\s*票（卡爾森', t) or "1"
    # 記名表決比數：逐字稿「記名表決 5 比 2 通過」
    rc_a = first(r'記名表決\s*(\d+)\s*比\s*\d+', t)
    rc_b = first(r'記名表決\s*\d+\s*比\s*(\d+)', t)

    # 後援預設值（逐字稿存在時應抓到；逐字稿缺漏時退回其載明之事實）
    budget_for = budget_for or "7"
    item25_for = item25_for or "6"
    item25_against = item25_against or "1"
    rc_a = rc_a or "5"
    rc_b = rc_b or "2"

    scores = {"report_created": 1.0}

    # 預算案：須提到「預算」且報告中的贊成／反對票數與逐字稿一致（N 比 0）。
    # 須出現「N…0」的對應（如 7 票贊成 0 票反對、7 比 0、7-0），不接受
    # 報告中其他案子任意出現的「N 票」誤判。
    bf = re.escape(budget_for)
    bg = re.escape(budget_against)
    budget_sec = section(c, [r'總預算', r'預算追加', r'預算'])
    budget_num = re.search(
        r'%s\s*票?\s*贊成[\s、,]*%s\s*票?\s*反對' % (bf, bg), budget_sec
    ) or re.search(r'%s\s*(?:比|[-:：])\s*%s\b' % (bf, bg), budget_sec)
    scores["budget_vote"] = 1.0 if (re.search(r'預算', c) and budget_num) else 0.0

    # 道路拓寬案：須提到拓寬／道路 且 利益迴避相關詞 且 點名卡爾森
    scores["recuse_item"] = 1.0 if (
        re.search(r'拓寬|道路', c)
        and re.search(r'迴避|回避|利益|abstain|recus', c, re.IGNORECASE)
        and re.search(r'卡爾森|蔡明憲', c)
    ) else 0.0

    # 羅馬倉庫園區：須提到羅馬倉庫／園區 且 記名表決 5 比 2（或 5-2）
    rc_pat = r'%s\s*(?:比|[-:：])\s*%s\b' % (re.escape(rc_a), re.escape(rc_b))
    rc_sec = section(c, [r'羅馬倉庫', r'園區', r'十四', r'十五', r'14', r'15'])
    scores["rollcall_item"] = 1.0 if (
        re.search(r'羅馬倉庫|園區|十四|十五|14|15', c)
        and re.search(rc_pat, rc_sec)
    ) else 0.0

    # 分區變更：須提到分區／公道五路／十九案 且 全體一致／無異議
    scores["unanimous_item"] = 1.0 if (
        re.search(r'分區|公道五路|十九|19', c)
        and re.search(r'一致|無異議|unanimou', c, re.IGNORECASE)
    ) else 0.0

    # 容量費：須提到容量費／自來水／污水／清運 且 一讀（first reading）
    scores["first_reading_item"] = 1.0 if (
        re.search(r'容量費|容量接管費|自來水|污水|清運', c)
        and re.search(r'一讀|first\s*read', c, re.IGNORECASE)
    ) else 0.0

    # 退輔委員會：須提到退輔／退伍軍人／二十二案 且 延期／續審／保留
    scores["continued_item"] = 1.0 if (
        re.search(r'退輔|退伍軍人|諮詢委員會|二十二|22', c)
        and re.search(r'延期|續審|保留|改期|continu|defer', c, re.IGNORECASE)
    ) else 0.0

    # 第二十五案：須提到二十五案／前瞻補助 且 N 比 M（逐字稿 6 比 1）且 卡爾森反對。
    # 須出現「N…M」的對應（如 6 比 1、6-1、贊成 6 票 反對 1 票），避免誤判。
    item_for = re.escape(item25_for)
    item_against = re.escape(item25_against)
    i25_sec = section(c, [r'二十五', r'前瞻補助', r'決議文'])
    dissent_num = re.search(
        r'%s\s*(?:比|[-:：])\s*%s\b' % (item_for, item_against), i25_sec
    ) or re.search(
        r'贊成\s*%s\s*票[\s、,]*反對\s*%s\s*票' % (item_for, item_against), i25_sec)
    scores["item25_dissent"] = 1.0 if (
        re.search(r'二十五|25|前瞻補助|決議文', c)
        and dissent_num
        and re.search(r'卡爾森|蔡明憲', i25_sec)
        and re.search(r'反對|dissent|nay', i25_sec, re.IGNORECASE)
    ) else 0.0

    # 統計摘要：須有「摘要／統計／合計／總計」字樣 且 接近某個議案件數
    has_summary_word = re.search(r'摘要|統計|合計|總計|彙整摘要|統計摘要', c)
    has_count = re.search(r'(?:合計|總計|共)\D{0,8}\d+\s*(?:件|案|表決|議案)', c) \
        or re.search(r'\d+\s*(?:件|案)\D{0,8}(?:議案|表決)', c) \
        or re.search(r'(?:議案|表決)\D{0,8}\d+\s*(?:件|案)', c)
    scores["summary_count"] = 1.0 if (has_summary_word and has_count) else 0.0

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
