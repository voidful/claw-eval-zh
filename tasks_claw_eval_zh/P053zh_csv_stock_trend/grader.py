"""Grader for P053zh_csv_stock_trend (adapted from PinchBench task `task_csv_stock_trend`).

Original file: tasks/task_csv_stock_trend.md
grading_type: hybrid

Contract (see docs/claw_eval_zh_schema.md §8):
  * grade(transcript, workspace_path) -> dict[str, float]
      Deterministic check, stdlib-only, importable without claw_eval.
  * ClawEvalZhGrader (AbstractGrader subclass) — only when claw_eval
      is importable; adapts grade() into DimensionScores.
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """Stock trend analysis grader (trilingual: 繁體 + 简体 + English).

    Numeric expectations (77.45 / 110.03 / 42%) are unchanged from
    PinchBench. Natural-language regex additionally accepts Chinese.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "stock_trend_report.md"
    if not report_path.exists():
        alternatives = [
            "trend_report.md", "report.md", "stock_report.md",
            "analysis.md", "stock_trend.md", "趨勢報告.md", "趋势报告.md",
        ]
        for alt in alternatives:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0, "trend_direction": 0.0,
            "starting_price": 0.0, "ending_price": 0.0,
            "percentage_change": 0.0, "monthly_breakdown": 0.0,
            "up_streak": 0.0, "down_streak": 0.0, "trend_periods": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    bullish_patterns = [
        r'bullish', r'upward\s*trend', r'positive\s*trend',
        r'strong\s*uptrend', r'significant.*(?:gain|increase|growth|rise)',
        r'看漲', r'看涨', r'多頭', r'多头', r'上升趨勢', r'上升趋势',
        r'明顯上漲', r'明显上涨', r'上漲趨勢', r'上涨趋势', r'牛市',
    ]
    scores["trend_direction"] = 1.0 if any(
        re.search(p, content_lower) for p in bullish_patterns) else 0.0

    scores["starting_price"] = 1.0 if re.search(r'77\.4[45]', content) else 0.0
    scores["ending_price"] = 1.0 if re.search(r'110\.0[23]', content) else 0.0
    pct_patterns = [r'4[12]\.\d+%', r'4[12]\.0\d*%', r'42\.07', r'42%', r'~42']
    scores["percentage_change"] = 1.0 if any(
        re.search(p, content) for p in pct_patterns) else 0.0

    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']
    month_abbrs = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                   'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    month_nums = ['2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06',
                  '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']
    month_count = 0
    for i, (mn, ma, mnum) in enumerate(zip(month_names, month_abbrs, month_nums), start=1):
        cn = "%d月" % i
        if mn in content_lower or ma in content_lower or mnum in content or cn in content:
            month_count += 1
    scores["monthly_breakdown"] = 1.0 if month_count >= 10 else (
        0.5 if month_count >= 6 else 0.0)

    up_streak_patterns = [
        r'(?:9|nine)\s*(?:consecutive|day|trading)',
        r'(?:consecutive|streak).*(?:9|nine)',
        r'aug(?:ust)?.*(?:up|gain|positive).*(?:streak|consecutive)',
        r'(?:up|gain|positive).*(?:streak|consecutive).*aug(?:ust)?',
        r'2014-08-1[1-9].*2014-08-2[01]',
        r'(?:連續|连续|連漲|连涨).*(?:9|九)',
        r'(?:9|九).*(?:連續|连续|天).*(?:上漲|上涨)',
        r'8月.*(?:連續上漲|连续上涨|連漲|连涨)',
        r'(?:連續上漲|连续上涨).*8月',
    ]
    scores["up_streak"] = 1.0 if any(
        re.search(p, content_lower) for p in up_streak_patterns) else 0.0

    down_streak_patterns = [
        r'(?:5|five)\s*(?:consecutive|day|trading).*(?:down|decline|loss|negative|drop)',
        r'(?:down|decline|loss|negative|drop).*(?:5|five)\s*(?:consecutive|day|trading)',
        r'(?:down|decline|loss|negative|drop).*(?:streak|consecutive).*jan(?:uary)?',
        r'jan(?:uary)?.*(?:down|decline|loss|negative|drop).*(?:streak|consecutive)',
        r'2014-01-2[789].*2014-01-3[01]',
        r'(?:連續|连续).*(?:5|五).*(?:下跌)',
        r'(?:5|五).*(?:連續|连续|天).*(?:下跌)',
        r'1月.*(?:連續下跌|连续下跌|連跌|连跌)',
        r'(?:連續下跌|连续下跌).*1月',
    ]
    scores["down_streak"] = 1.0 if any(
        re.search(p, content_lower) for p in down_streak_patterns) else 0.0

    trend_indicators = 0
    if (re.search(r'jan(?:uary)?.*(?:dip|drop|decline|sell-?off|fall)', content_lower)
            or re.search(r'1月.*(?:下跌|回調|回调|拋售|抛售|下挫)', content)):
        trend_indicators += 1
    if (re.search(r'apr(?:il)?.*(?:breakout|rally|surge|jump|spike)', content_lower)
            or re.search(r'4月.*(?:突破|大漲|大涨|反彈|反弹|飆升|飙升)', content)):
        trend_indicators += 1
    if (re.search(r'(?:rally|climb|rise|growth|upward).*(?:may|summer|q[23])', content_lower)
            or re.search(r'(?:5月|夏|三季度|第三季).*(?:上漲|上涨|攀升|爬升)', content)):
        trend_indicators += 1
    if (re.search(r'(?:nov(?:ember)?|q4).*(?:high|peak|rally|climb)', content_lower)
            or re.search(r'(?:11月|12月|四季度|第四季).*(?:新高|高點|高点|峰值)', content)):
        trend_indicators += 1
    scores["trend_periods"] = 1.0 if trend_indicators >= 2 else (
        0.5 if trend_indicators >= 1 else 0.0)

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
