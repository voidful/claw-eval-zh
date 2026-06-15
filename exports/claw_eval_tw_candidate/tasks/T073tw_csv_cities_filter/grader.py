"""Grader for T073tw_csv_cities_filter (Taiwan-localized from PinchBench `task_csv_cities_filter`).

Phase 2 source: tasks_zh/task_csv_cities_filter.md
Original file: tasks/task_csv_cities_filter.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """Taiwan cities multi-filter grader. Values recomputed from tw_cities.csv."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    report = workspace / "cities_filter_report.md"
    if not report.exists():
        for alt in ["filter_report.md", "report.md", "cities_report.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in ["report_created", "six_cities_filter", "southern_filter",
                                 "taipei_kaohsiung", "midsize_filter", "northern_filter"]}
    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")
    # F1 六都>=2M: 5 cities incl 新北/臺中/高雄/臺北/桃園
    six = sum(1 for x in ["新北", "臺中", "高雄", "臺北", "桃園"] if x in c)
    has5 = bool(re.search(r'(?:5|五)\s*(?:個|縣市|都)', c))
    scores["six_cities_filter"] = 1.0 if (six >= 5 and has5) else (0.5 if six >= 4 else 0.0)
    # F2 南部>=1M: 高雄 + 臺南
    scores["southern_filter"] = 1.0 if ("高雄" in c and "臺南" in c) else 0.0
    # F3 臺北 vs 高雄
    tk = ("臺北" in c and "高雄" in c)
    # accept stating 高雄 larger, or both populations present
    kbig = bool(re.search(r'高雄.{0,12}(?:多|大|高|>|超過)', c)) or "2,738,041" in c or "2738041" in c
    scores["taipei_kaohsiung"] = 1.0 if (tk and kbig) else (0.5 if tk else 0.0)
    # F4 中型 500k-1M: 屏東/新竹縣/苗栗/雲林, count 4
    mid = sum(1 for x in ["屏東", "新竹縣", "苗栗", "雲林"] if x in c)
    scores["midsize_filter"] = 1.0 if mid >= 4 else (0.5 if mid >= 2 else 0.0)
    # F5 北部: 7 cities + 新北/臺北/桃園
    n7 = bool(re.search(r'(?:7|七)\s*(?:個|縣市)', c))
    ncities = sum(1 for x in ["新北", "臺北", "桃園"] if x in c)
    scores["northern_filter"] = 1.0 if (n7 and ncities >= 3) else (0.5 if ncities >= 2 else 0.0)
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
