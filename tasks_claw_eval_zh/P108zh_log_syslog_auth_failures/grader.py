"""Grader for P108zh_log_syslog_auth_failures (adapted from PinchBench task `task_log_syslog_auth_failures`).

Original file: tasks/task_log_syslog_auth_failures.md
grading_type: hybrid

Contract (see docs/claw_eval_zh_schema.md §8):
  * grade(transcript, workspace_path) -> dict[str, float]
      Deterministic check, stdlib-only, importable without claw_eval.
  * ClawEvalZhGrader (AbstractGrader subclass) — only when claw_eval
      is importable; adapts grade() into DimensionScores.
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Linux syslog authentication failure summary task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "auth_failures_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "failures_counted": 0.0,
            "by_service": 0.0,
            "source_hosts": 0.0,
            "recommendations": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: Failures counted
    has_count = any(kw in content for kw in ["2000", "2,000", "1610", "1,610",
                                               "1655", "1,655", "thousand"])
    has_failure = "authentication failure" in content or "auth fail" in content or "failed" in content
    scores["failures_counted"] = (
        1.0 if has_count and has_failure else
        0.5 if has_failure else 0.0
    )

    # Check 2: Broken down by service
    services = ["sshd", "ftpd", "ftp", "su(pam", "su ", "login", "klogin", "pam_unix"]
    services_found = sum(1 for s in services if s in content)
    scores["by_service"] = (
        1.0 if services_found >= 3 else
        0.5 if services_found >= 2 else 0.0
    )

    # Check 3: Source hosts listed
    host_indicators = ["rhost", "source", "remote", "ip", "host", "209.184",
                       "sagonet", "iasi", "astral"]
    scores["source_hosts"] = (
        1.0 if sum(1 for kw in host_indicators if kw in content) >= 3 else
        0.5 if sum(1 for kw in host_indicators if kw in content) >= 1 else 0.0
    )

    # Check 4: Recommendations provided
    rec_keywords = ["recommend", "should", "implement", "consider", "disable",
                    "block", "firewall", "fail2ban", "key-based", "rate limit"]
    rec_lines = [l for l in content.split("\n") if any(kw in l for kw in rec_keywords)]
    scores["recommendations"] = (
        1.0 if len(rec_lines) >= 2 else
        0.5 if len(rec_lines) >= 1 else 0.0
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
