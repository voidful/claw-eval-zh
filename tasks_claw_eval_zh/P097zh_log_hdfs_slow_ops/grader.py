"""Grader for P097zh_log_hdfs_slow_ops (adapted from PinchBench task `task_log_hdfs_slow_ops`).

Original file: tasks/task_log_hdfs_slow_ops.md
grading_type: hybrid

Contract (see docs/claw_eval_zh_schema.md §8):
  * grade(transcript, workspace_path) -> dict[str, float]
      Deterministic check, stdlib-only, importable without claw_eval.
  * ClawEvalZhGrader (AbstractGrader subclass) — only when claw_eval
      is importable; adapts grade() into DimensionScores.
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the HDFS slow operation detection task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "hdfs_slow_ops_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "lifecycle_timing": 0.0,
            "size_correlation": 0.0,
            "time_range": 0.0,
            "performance_assessment": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Block lifecycle timing calculated
    has_timing = any(kw in content for kw in ["1 second", "2 second", "3 second",
                                                "elapsed", "duration", "latency",
                                                "took", "completed in"])
    has_block = "blk_" in content or "blk-" in content or "block" in content
    scores["lifecycle_timing"] = (
        1.0 if has_timing and has_block else
        0.5 if has_timing or has_block else 0.0
    )

    # Check 2: Block sizes mentioned
    sizes = ["91178", "233217", "11971", "11977"]
    sizes_found = sum(1 for s in sizes if s in content)
    has_correlation = any(kw in content for kw in ["size", "bytes", "larger", "smaller"])
    scores["size_correlation"] = (
        1.0 if sizes_found >= 2 and has_correlation else
        0.5 if sizes_found >= 1 else 0.0
    )

    # Check 3: Time range identified
    has_28s = any(kw in content for kw in ["28 second", "~28", "30 second",
                                            "half a minute", "less than a minute"])
    has_timestamps = "203518" in content or "20:35:18" in content or "20:35" in content
    scores["time_range"] = (
        1.0 if has_28s or has_timestamps else
        0.5 if any(kw in content for kw in ["short", "brief", "seconds"]) else 0.0
    )

    # Check 4: Performance assessment
    perf_keywords = ["healthy", "normal", "fast", "no slow", "performing well",
                     "efficient", "optimal", "good performance"]
    scores["performance_assessment"] = (
        1.0 if sum(1 for kw in perf_keywords if kw in content) >= 1 else 0.0
    )

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
