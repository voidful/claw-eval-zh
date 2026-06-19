"""Grader for T072tw_csv_cities_ranking (Taiwan-localized from PinchBench `task_csv_cities_ranking`).

Phase 2 source: tasks_zh/task_csv_cities_ranking.md
Original file: tasks/task_csv_cities_ranking.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣鄉鎮市區人口排名 grader。

    正解一律從工作區內的 tw_townships.csv 動態計算，再比對 agent 產生的
    中文報告 cities_ranking_report.md，不沿用任何美國數值。
    僅用標準函式庫。
    """
    import csv
    import re
    import statistics
    from pathlib import Path

    workspace = Path(workspace_path)

    report_path = workspace / "cities_ranking_report.md"
    if not report_path.exists():
        for alt in ["ranking_report.md", "report.md", "cities_report.md",
                    "townships_ranking_report.md", "population_ranking.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = ["report_created", "top_10_townships", "bottom_10_townships",
            "total_population", "mean_population", "median_population",
            "county_rankings", "distribution_brackets"]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 從 CSV 動態計算正解 ---
    csv_path = workspace / "tw_townships.csv"
    if not csv_path.exists():
        for f in workspace.rglob("*.csv"):
            if "township" in f.name.lower():
                csv_path = f
                break
    if not csv_path.exists():
        # 無 CSV 可比對：只能確認報告存在
        for k in keys[1:]:
            scores[k] = 0.0
        return scores

    rows = []
    with csv_path.open(encoding="utf-8") as f:
        for d in csv.DictReader(f):
            try:
                rows.append((d["Township"].strip(), d["County"].strip(),
                             int(float(d["Population"]))))
            except (KeyError, ValueError):
                continue

    n = len(rows)
    pops = [p for _, _, p in rows]
    total = sum(pops)
    mean = total / n if n else 0
    median = statistics.median(pops) if pops else 0

    srt_desc = sorted(rows, key=lambda x: x[2], reverse=True)
    srt_asc = sorted(rows, key=lambda x: x[2])
    top10 = srt_desc[:10]
    bottom10 = srt_asc[:10]

    county_agg = {}
    for _, c, p in rows:
        tp, cnt = county_agg.get(c, (0, 0))
        county_agg[c] = (tp + p, cnt + 1)
    county_srt = sorted(county_agg.items(), key=lambda x: x[1][0], reverse=True)
    top_counties = county_srt[:10]

    def in_report(s):
        return s in content

    def num_present(value, tol=0):
        """數字以千分位或無千分位形式出現於報告（允許 +/- tol 容差）。"""
        candidates = set()
        for v in range(value - tol, value + tol + 1):
            candidates.add(str(v))
            candidates.add(f"{v:,}")
        return any(c in content for c in candidates)

    # --- 前 10 大鄉鎮市區：至少前 5 名出現，且第 1 名須出現 ---
    top5_names = [t for t, _, _ in top10[:5]]
    found_top = sum(1 for name in top5_names if in_report(name))
    first_name = top10[0][0]
    if in_report(first_name) and found_top >= 5:
        scores["top_10_townships"] = 1.0
    elif found_top >= 3:
        scores["top_10_townships"] = 0.5
    else:
        scores["top_10_townships"] = 0.0

    # --- 後 10 小：最小者須出現 ---
    smallest_name = bottom10[0][0]
    found_bottom = sum(1 for t, _, _ in bottom10[:5] if in_report(t))
    if in_report(smallest_name) and found_bottom >= 3:
        scores["bottom_10_townships"] = 1.0
    elif in_report(smallest_name):
        scores["bottom_10_townships"] = 0.5
    else:
        scores["bottom_10_townships"] = 0.0

    # --- 總人口（容差 +/- 1，並接受「約 X 萬」表述）---
    total_ok = num_present(total, tol=2)
    wan_total = round(total / 10000)  # 約 1928 萬
    if not total_ok:
        total_ok = bool(re.search(rf'{wan_total}\s*萬', content)) or \
            bool(re.search(rf'{round(total/10000, 1)}'.replace('.', r'\.') + r'\s*萬', content))
    scores["total_population"] = 1.0 if total_ok else 0.0

    # --- 平均人口（四捨五入，容差 +/- 50）---
    mean_int = round(mean)
    mean_ok = any(num_present(mean_int + d) for d in range(-50, 51))
    # 接受千位四捨五入（例如 94,000 / 9.4 萬 / 9.45 萬）
    if not mean_ok:
        mean_ok = bool(re.search(r'9[.,]?4\d?\s*萬', content)) or \
            num_present(round(mean / 100) * 100, tol=0)
    scores["mean_population"] = 1.0 if mean_ok else 0.0

    # --- 中位數（55,500；接受 53,000~58,000 區間任一值或「約 5.5 萬」）---
    median_int = int(round(median))
    median_ok = any(num_present(v) for v in range(median_int - 50, median_int + 51))
    if not median_ok:
        lo = min(p for p in pops if p >= median) if pops else median_int
        hi = max(p for p in pops if p <= median) if pops else median_int
        median_ok = num_present(lo) or num_present(hi)
    if not median_ok:
        median_ok = bool(re.search(r'5[.,]?5\s*萬', content))
    scores["median_population"] = 1.0 if median_ok else 0.0

    # --- 縣市排名：加總最高縣市須為第 1 名 ---
    top_county = top_counties[0][0]
    top_county_pop = top_counties[0][1][0]
    top_county_cnt = top_counties[0][1][1]
    patterns = [
        rf'{top_county}.{{0,20}}(?:第\s*1|第一|#1|最高|最多|榜首|居首|冠軍)',
        rf'(?:第\s*1|第一|#1|最高|最多|排名第一).{{0,20}}{top_county}',
        rf'{top_county}.{{0,30}}{top_county_cnt}\s*個',
    ]
    county_ok = any(re.search(p, content) for p in patterns)
    if not county_ok:
        county_ok = in_report(top_county) and num_present(top_county_pop, tol=2)
    scores["county_rankings"] = 1.0 if county_ok else 0.0

    # --- 分布區間 ---
    bracket_kw = ["萬", "5 萬", "10 萬", "25 萬", "50 萬", "100 萬",
                  "50k", "100k", "250k", "500k", "1m", "分布", "區間",
                  "<5", "5萬", "10萬", "25萬", "50萬", "100萬"]
    bracket_count = sum(1 for k in bracket_kw if k in content)
    # 也可比對實際區間計數（95 / 42 / 53 / 13 / 1）
    br = {"<5萬": 0, "5-10萬": 0, "10-25萬": 0, "25-50萬": 0, "50-100萬": 0, ">100萬": 0}
    for p in pops:
        if p < 50000:
            br["<5萬"] += 1
        elif p < 100000:
            br["5-10萬"] += 1
        elif p < 250000:
            br["10-25萬"] += 1
        elif p < 500000:
            br["25-50萬"] += 1
        elif p < 1000000:
            br["50-100萬"] += 1
        else:
            br[">100萬"] += 1
    # 只有「真的呈現分布區間」（出現萬/區間/分布等關鍵詞）才給分；
    # 單純出現某個小數字（如 1、13）不算，避免美國報告誤判得分。
    matched_counts = sum(1 for v in br.values() if str(v) in content)
    if bracket_count >= 3 and matched_counts >= 2:
        scores["distribution_brackets"] = 1.0
    elif bracket_count >= 3:
        scores["distribution_brackets"] = 0.5
    else:
        scores["distribution_brackets"] = 0.0

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
