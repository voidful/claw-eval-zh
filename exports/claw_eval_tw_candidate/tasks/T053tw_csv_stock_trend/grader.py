"""Grader for T053tw_csv_stock_trend (Taiwan-localized from PinchBench `task_csv_stock_trend`).

Phase 2 source: tasks_zh/task_csv_stock_trend.md
Original file: tasks/task_csv_stock_trend.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """2330 2024 trend grader. Values recomputed from real TWSE fixture."""
    from pathlib import Path
    import re
    workspace = Path(workspace_path)
    report = workspace / "stock_trend_report.md"
    if not report.exists():
        for alt in ["trend_report.md", "report.md", "stock_report.md",
                    "analysis.md", "趨勢報告.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in ["report_created", "trend_direction", "starting_price",
                                 "ending_price", "percentage_change", "monthly_breakdown",
                                 "up_streak", "down_streak", "extremes"]}
    scores = {"report_created": 1.0}
    content = report.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()
    bull = [r'bullish', r'upward', r'看漲', r'看涨', r'多頭', r'多头',
            r'上升趨勢', r'上升趋势', r'明顯上漲', r'明显上涨', r'牛市', r'大漲', r'大涨']
    scores["trend_direction"] = 1.0 if any(re.search(p, cl) for p in bull) else 0.0
    scores["starting_price"] = 1.0 if re.search(r'593(\.0+)?', content) else 0.0
    scores["ending_price"] = 1.0 if re.search(r'1[,]?075(\.0+)?', content) else 0.0
    scores["percentage_change"] = 1.0 if re.search(r'8[01]\.\d|81\.28|81\s*%|~?\s*81', content) else 0.0
    months = 0
    for i in range(1, 13):
        if ("%d月" % i) in content or ("2024-%02d" % i) in content:
            months += 1
    scores["monthly_breakdown"] = 1.0 if months >= 10 else (0.5 if months >= 6 else 0.0)
    up = [r'(?:6|六)\s*(?:天|個交易日|consecutive|day)',
          r'(?:連續|连续|consecutive).*(?:6|六)', r'9月.*(?:連續上漲|连续上涨|連漲)',
          r'2024-09-1[89].*2024-09-2[0-6]']
    scores["up_streak"] = 1.0 if any(re.search(p, cl) for p in up) else 0.0
    down = [r'(?:4|四)\s*(?:天|個交易日|consecutive|day).*(?:下跌|down|decline)',
            r'(?:下跌|down|decline).*(?:4|四)\s*(?:天|consecutive)',
            r'5月.*(?:連續下跌|连续下跌|連跌)', r'2024-05-2[7-9].*2024-05-3[01]']
    scores["down_streak"] = 1.0 if any(re.search(p, cl) for p in down) else 0.0
    ext = 0
    if re.search(r'1[,]?090', content):
        ext += 1
    if re.search(r'576', content):
        ext += 1
    scores["extremes"] = 1.0 if ext >= 2 else (0.5 if ext == 1 else 0.0)
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
