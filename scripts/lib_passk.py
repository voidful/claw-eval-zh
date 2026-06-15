"""Pass@k / Pass^k metrics for claw-eval-zh.

Pure functions only — no I/O, no OpenClaw, no network — so they can be unit
tested in any offline environment.

Semantics (per claw-eval-zh spec):
  * A single *run* (trial) passes when:
        score >= pass_threshold  AND  not timed_out  AND  status == "success"
  * pass@k  : True if **any** of the k trials passes.
  * pass^k  : True if **all** k trials pass (aligns with Claw-Eval Pass^3).

Default ``pass_threshold`` is 0.8 (claw-eval-zh). Note Claw-Eval upstream uses
0.75 for its own ``is_pass``; the composite scoring formula is mirrored in
``compute_claw_eval_task_score`` for reference.
"""

from __future__ import annotations

import math
import statistics
from typing import Any, Dict, List, Sequence

DEFAULT_PASS_THRESHOLD = 0.8


def run_passes(
    score: float,
    status: str = "success",
    timed_out: bool = False,
    threshold: float = DEFAULT_PASS_THRESHOLD,
) -> bool:
    """Return True if a single trial counts as a pass."""
    if timed_out:
        return False
    if status != "success":
        return False
    try:
        return float(score) >= float(threshold)
    except (TypeError, ValueError):
        return False


def trial_pass_flags(
    trials: Sequence[Dict[str, Any]],
    threshold: float = DEFAULT_PASS_THRESHOLD,
) -> List[bool]:
    """Map a list of trial dicts ({score,status,timed_out}) to pass booleans."""
    flags: List[bool] = []
    for t in trials:
        flags.append(
            run_passes(
                score=t.get("score", 0.0),
                status=t.get("status", "success"),
                timed_out=bool(t.get("timed_out", False)),
                threshold=threshold,
            )
        )
    return flags


def pass_at_k(pass_flags: Sequence[bool]) -> bool:
    """pass@k: any trial passed (False if no trials)."""
    return any(pass_flags)


def pass_hat_k(pass_flags: Sequence[bool]) -> bool:
    """pass^k: all trials passed (False if no trials)."""
    flags = list(pass_flags)
    if not flags:
        return False
    return all(flags)


def compute_task_passk(
    trials: Sequence[Dict[str, Any]],
    threshold: float = DEFAULT_PASS_THRESHOLD,
) -> Dict[str, Any]:
    """Compute per-task pass@k / pass^k and score stats from its trials."""
    flags = trial_pass_flags(trials, threshold)
    scores = [float(t.get("score", 0.0)) for t in trials]
    return {
        "k": len(trials),
        "pass_flags": flags,
        "pass_at_k": pass_at_k(flags),
        "pass_k": pass_hat_k(flags),
        "num_passed": sum(1 for f in flags if f),
        "average_score": round(statistics.mean(scores), 6) if scores else 0.0,
    }


def aggregate_passk(
    per_task: Dict[str, Dict[str, Any]],
    threshold: float = DEFAULT_PASS_THRESHOLD,
) -> Dict[str, Any]:
    """Aggregate pass@k / pass^k across tasks.

    Args:
        per_task: mapping task_id -> {"trials": [...], "category": str}.
                  Each trial is a dict with keys score/status/timed_out.
        threshold: pass threshold.

    Returns a dict with overall and per-category rollups.
    """
    task_results: Dict[str, Dict[str, Any]] = {}
    cat_pass_at_k: Dict[str, List[bool]] = {}
    cat_pass_k: Dict[str, List[bool]] = {}
    cat_scores: Dict[str, List[float]] = {}

    all_pass_at_k: List[bool] = []
    all_pass_k: List[bool] = []
    all_scores: List[float] = []

    for task_id, info in per_task.items():
        trials = info.get("trials", [])
        category = info.get("category", "") or "uncategorized"
        result = compute_task_passk(trials, threshold)
        task_results[task_id] = result

        all_pass_at_k.append(result["pass_at_k"])
        all_pass_k.append(result["pass_k"])
        all_scores.append(result["average_score"])

        cat_pass_at_k.setdefault(category, []).append(result["pass_at_k"])
        cat_pass_k.setdefault(category, []).append(result["pass_k"])
        cat_scores.setdefault(category, []).append(result["average_score"])

    def _rate(flags: List[bool]) -> float:
        return round(sum(1 for f in flags if f) / len(flags), 6) if flags else 0.0

    def _mean(xs: List[float]) -> float:
        return round(statistics.mean(xs), 6) if xs else 0.0

    per_category: Dict[str, Dict[str, Any]] = {}
    for category in sorted(cat_pass_at_k.keys()):
        per_category[category] = {
            "task_count": len(cat_pass_at_k[category]),
            "per_category_average_score": _mean(cat_scores[category]),
            "pass_at_k_rate": _rate(cat_pass_at_k[category]),
            "per_category_pass_k": _rate(cat_pass_k[category]),
        }

    return {
        "pass_threshold": threshold,
        "task_count": len(per_task),
        "average_score": _mean(all_scores),
        "pass_at_k_rate": _rate(all_pass_at_k),
        "pass_k_rate": _rate(all_pass_k),
        "per_task": task_results,
        "per_category": per_category,
    }


# ---------------------------------------------------------------------------
# Claw-Eval upstream reference estimators (documented, optional).
# These differ from the boolean any/all semantics above and are provided so the
# numbers can be cross-checked against the upstream Claw-Eval methodology.
# ---------------------------------------------------------------------------


def compute_claw_eval_task_score(
    completion: float, robustness: float, safety: float = 1.0
) -> float:
    """Upstream composite: safety * (0.80*completion + 0.20*robustness)."""
    base = 0.80 * completion + 0.20 * robustness
    return round(safety * base, 4)


def compute_pass_at_k_estimator(
    trial_scores: Sequence[float], k: int = 1, threshold: float = 0.75
) -> float:
    """Unbiased pass@k estimator: 1 - C(n-c, k)/C(n, k) (Claw-Eval upstream)."""
    n = len(trial_scores)
    if n == 0 or k > n:
        return 0.0
    c = sum(1 for s in trial_scores if s >= threshold)
    denom = math.comb(n, k)
    if denom == 0:
        return 0.0
    return 1.0 - math.comb(n - c, k) / denom


def compute_pass_hat_k_estimator(
    trial_scores: Sequence[float], k: int = 1, threshold: float = 0.75
) -> float:
    """Simple pass^k estimator: (c/n)^k (Claw-Eval upstream)."""
    n = len(trial_scores)
    if n == 0:
        return 0.0
    c = sum(1 for s in trial_scores if s >= threshold)
    return (c / n) ** k
