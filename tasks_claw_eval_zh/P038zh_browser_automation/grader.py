"""Grader for P038zh_browser_automation (adapted from PinchBench task `task_browser_automation`).

Original file: tasks/task_browser_automation.md
grading_type: hybrid

Contract (see docs/claw_eval_zh_schema.md §8):
  * grade(transcript, workspace_path) -> dict[str, float]
      Deterministic check, stdlib-only, importable without claw_eval.
  * ClawEvalZhGrader (AbstractGrader subclass) — only when claw_eval
      is importable; adapts grade() into DimensionScores.
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)
    test_file = workspace / "test_shop.py"

    if not test_file.exists():
        return {
            "file_created": 0.0,
            "uses_playwright": 0.0,
            "tests_disabled_button": 0.0,
            "tests_add_to_cart": 0.0,
            "tests_cart_total": 0.0,
            "tests_remove_item": 0.0,
            "tests_checkout": 0.0,
            "uses_assertions": 0.0,
        }

    scores["file_created"] = 1.0
    content = test_file.read_text()
    content_lower = content.lower()

    # Uses playwright sync API
    scores["uses_playwright"] = 1.0 if "playwright.sync_api" in content else 0.0

    # Tests disabled button / out of stock
    disabled_kw = ["disabled", "out of stock", "webcam", "is_disabled", "to_be_disabled"]
    scores["tests_disabled_button"] = 1.0 if sum(1 for k in disabled_kw if k in content_lower) >= 2 else 0.0

    # Tests adding to cart
    add_kw = ["add to cart", "wireless mouse", "mechanical keyboard", "addtocart", "click"]
    scores["tests_add_to_cart"] = 1.0 if sum(1 for k in add_kw if k in content_lower) >= 3 else 0.0

    # Tests cart total
    total_kw = ["149.97", "59.98", "total"]
    scores["tests_cart_total"] = 1.0 if sum(1 for k in total_kw if k in content_lower) >= 2 else 0.0

    # Tests remove from cart
    remove_kw = ["remove", "mechanical keyboard"]
    scores["tests_remove_item"] = 1.0 if all(k in content_lower for k in remove_kw) else 0.0

    # Tests checkout
    checkout_kw = ["checkout", "order", "ord-", "confirmation"]
    scores["tests_checkout"] = 1.0 if sum(1 for k in checkout_kw if k in content_lower) >= 2 else 0.0

    # Uses assertions
    assert_kw = ["expect", "assert", "to_have_text", "to_be_visible", "to_be_disabled", "to_contain_text"]
    scores["uses_assertions"] = 1.0 if sum(1 for k in assert_kw if k in content_lower) >= 2 else 0.0

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
