"""Grader for P096zh_log_hdfs_connections (adapted from PinchBench task `task_log_hdfs_connections`).

Original file: tasks/task_log_hdfs_connections.md
grading_type: hybrid

Contract (see docs/claw_eval_zh_schema.md §8):
  * grade(transcript, workspace_path) -> dict[str, float]
      Deterministic check, stdlib-only, importable without claw_eval.
  * ClawEvalZhGrader (AbstractGrader subclass) — only when claw_eval
      is importable; adapts grade() into DimensionScores.
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the HDFS connection pattern analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "hdfs_connections_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "ips_listed": 0.0,
            "subnets_grouped": 0.0,
            "active_nodes": 0.0,
            "components_separated": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: IPs listed/counted
    has_count = any(n in content for n in ["202", "200", "~200", "over 200"])
    has_ips = "10.250" in content and "10.251" in content
    scores["ips_listed"] = (
        1.0 if has_count and has_ips else
        0.5 if has_ips else 0.0
    )

    # Check 2: Subnets grouped
    subnet_keywords = ["subnet", "10.250", "10.251", "rack", "network segment",
                       "address range", "ip range"]
    scores["subnets_grouped"] = (
        1.0 if "10.250" in content and "10.251" in content and
              sum(1 for kw in subnet_keywords if kw in content) >= 2 else
        0.5 if "10.250" in content and "10.251" in content else 0.0
    )

    # Check 3: Active nodes identified
    active_ips = ["10.250.19.102", "10.251.215.16", "10.250.14.224", "10.250.10.6"]
    ips_found = sum(1 for ip in active_ips if ip in content)
    scores["active_nodes"] = (
        1.0 if ips_found >= 2 else
        0.5 if ips_found >= 1 else 0.0
    )

    # Check 4: Components separated
    component_keywords = ["dataxceiver", "dataxeceiver", "fsnamesystem",
                          "packetresponder", "namenode", "datanode"]
    scores["components_separated"] = (
        1.0 if sum(1 for kw in component_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in component_keywords if kw in content) >= 1 else 0.0
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
