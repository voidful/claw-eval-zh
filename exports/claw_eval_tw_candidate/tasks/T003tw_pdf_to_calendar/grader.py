"""Grader for T003tw_pdf_to_calendar (Taiwan-localized from PinchBench `task_pdf_to_calendar`).

Phase 2 source: tasks_zh/task_pdf_to_calendar.md
Original file: tasks/task_pdf_to_calendar.md
grading_type: automated

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """T003 中興大學 114 學年度行事曆 → ICS grader（台灣在地版）。

    檢查 agent 產出的 school-calendar.ics 是否含正確的西元日期；重點在民國年→西元年
    換算（114=2025、115=2026）。以日期為主要訊號（PDF 內各日期幾乎一對一對應到單一
    事件），輔以結構檢查。僅用標準函式庫。
    """
    from pathlib import Path

    ws = Path(workspace_path)
    ics = ws / "school-calendar.ics"
    if not ics.exists():
        cands = sorted(ws.glob("**/*.ics"))
        ics = cands[0] if cands else None

    # (check_name, ISO 日期) — 取自 PDF 之實際重要記事
    KEY = [
        ("fall_classes_begin", "2025-09-08"),
        ("mid_autumn", "2025-10-06"),
        ("national_day", "2025-10-10"),
        ("fall_final_exam", "2025-12-22"),
        ("winter_break", "2025-12-29"),
        ("new_year_day", "2026-01-01"),
        ("spring_classes_begin", "2026-02-23"),
        ("peace_memorial", "2026-02-28"),
        ("graduation", "2026-05-30"),
        ("dragon_boat", "2026-06-19"),
    ]
    scores = {"ics_created": 0.0, "ics_valid": 0.0, "min_events": 0.0}
    for name, _ in KEY:
        scores[name] = 0.0
    if not ics or not ics.exists():
        return scores

    text = ics.read_text(encoding="utf-8", errors="ignore")
    up = text.upper()
    scores["ics_created"] = 1.0
    scores["ics_valid"] = 1.0 if ("VCALENDAR" in up and "VEVENT" in up) else 0.0
    n = up.count("BEGIN:VEVENT")
    scores["min_events"] = 1.0 if n >= 10 else round(min(n, 10) / 10.0, 2)

    for name, iso in KEY:
        compact = iso.replace("-", "")          # 20250908
        scores[name] = 1.0 if (compact in text or iso in text) else 0.0
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
