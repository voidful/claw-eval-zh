"""Grader for T066tw_csv_stations_by_elevation (Taiwan-localized from PinchBench `task_csv_stations_by_elevation`).

Phase 2 source: tasks_zh/task_csv_stations_by_elevation.md
Original file: tasks/task_csv_stations_by_elevation.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣氣象站海拔排名 grader。

    所有「應有事實」皆由台灣 CSV tw_weather_stations.csv 動態計算後，再比對 agent
    產出的中文報告 elevation_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import csv
    import re

    workspace = Path(workspace_path)

    checks = ["report_created", "highest_station", "lowest_station",
              "summary_stats", "agency_comparison", "county_analysis",
              "summary_paragraph"]

    # --- 1. 從台灣 CSV 動態算出正解（避免硬寫） ---
    csv_path = workspace / "tw_weather_stations.csv"
    rows = []
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                try:
                    r["_elev"] = int(str(r.get("Elevation (meters)", "")).strip())
                except (ValueError, TypeError):
                    continue
                rows.append(r)

    def _median(vals):
        s = sorted(vals)
        n = len(s)
        if n == 0:
            return 0.0
        if n % 2:
            return float(s[n // 2])
        return (s[n // 2 - 1] + s[n // 2]) / 2.0

    def _mean(vals):
        return sum(vals) / len(vals) if vals else 0.0

    # 預設值（萬一 CSV 缺漏時的保底，數值來自此台灣 CSV）
    highest_name, highest_elev = "玉山主峰測站", 3952
    lowest_name, lowest_elev = "安平海濱潮位站", 2
    elev_min, elev_max = 2, 3952
    elev_mean, elev_median = 961.0, 575.0
    agency_means = {"林業署": 1889.65, "中央氣象署": 432.4, "水利署": 963.0}
    top_county, top_county_mean = "南投縣", 1970.76
    bot_county, bot_county_mean = "澎湖縣", 37.5

    if rows:
        elevs = [r["_elev"] for r in rows]
        shi = sorted(rows, key=lambda r: -r["_elev"])
        slo = sorted(rows, key=lambda r: r["_elev"])
        highest_name = shi[0]["Station Name"].strip()
        highest_elev = shi[0]["_elev"]
        lowest_name = slo[0]["Station Name"].strip()
        lowest_elev = slo[0]["_elev"]
        elev_min, elev_max = min(elevs), max(elevs)
        elev_mean, elev_median = _mean(elevs), _median(elevs)

        # 各管理機構平均
        ag = {}
        for r in rows:
            ag.setdefault(r["Managing Agency"].strip(), []).append(r["_elev"])
        agency_means = {k: _mean(v) for k, v in ag.items()}

        # 各縣市（County）平均，僅限 3 站以上且非空白
        cc = {}
        for r in rows:
            c = r["County"].strip()
            if c:
                cc.setdefault(c, []).append(r["_elev"])
        elig = {c: _mean(v) for c, v in cc.items() if len(v) >= 3}
        if elig:
            top_county = max(elig, key=elig.get)
            top_county_mean = elig[top_county]
            bot_county = min(elig, key=elig.get)
            bot_county_mean = elig[bot_county]

    # 找出機構平均的最高與最低者（用於彈性比對機構差異）
    if agency_means:
        hi_agency = max(agency_means, key=agency_means.get)
        lo_agency = min(agency_means, key=agency_means.get)
    else:
        hi_agency, lo_agency = "林業署", "中央氣象署"

    def _num_variants(value):
        """產生整數值的正則，容許千分位逗號（如 3952 / 3,952）。"""
        iv = int(round(value))
        s = str(iv)
        if len(s) > 3:
            comma = s[:-3] + "," + s[-3:]
            return r"(?:%s|%s)" % (re.escape(s), re.escape(comma))
        return re.escape(s)

    def _near_int(value, tol):
        """產生「value±tol 範圍內任一整數」的比對函式（容許千分位逗號）。"""
        iv = int(round(value))
        cands = list(range(iv - tol, iv + tol + 1))
        def _hit(text):
            for c in cands:
                if re.search(r"(?<!\d)" + _num_variants(c) + r"(?!\d)", text):
                    return True
            return False
        return _hit

    # --- 2. 找出 agent 的報告檔 ---
    report_path = workspace / "elevation_report.md"
    if not report_path.exists():
        for alt in ["elevation.md", "report.md", "stations_elevation.md",
                    "analysis.md", "海拔報告.md", "海拔分析.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in checks}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 3. 逐項比對中文關鍵字／數值 ---
    # 最高測站：名稱 + 海拔數值。
    has_hi_name = highest_name in content
    has_hi_val = bool(re.search(
        r"(?<!\d)" + _num_variants(highest_elev) + r"(?!\d)", content))
    scores["highest_station"] = (
        1.0 if (has_hi_name and has_hi_val)
        else (0.5 if (has_hi_name or has_hi_val) else 0.0))

    # 最低測站：名稱 + 海拔數值。
    has_lo_name = lowest_name in content
    has_lo_val = bool(re.search(
        r"(?<!\d)" + _num_variants(lowest_elev) + r"(?!\d)", content))
    scores["lowest_station"] = (
        1.0 if (has_lo_name and has_lo_val)
        else (0.5 if (has_lo_name or has_lo_val) else 0.0))

    # 摘要統計：最小、最大、平均、中位數，命中 3 項以上滿分。
    stats_found = 0
    if re.search(r"(?<!\d)" + _num_variants(elev_min) + r"(?!\d)", content):
        stats_found += 1
    if re.search(r"(?<!\d)" + _num_variants(elev_max) + r"(?!\d)", content):
        stats_found += 1
    if _near_int(elev_mean, 3)(content):   # 平均約 961
        stats_found += 1
    if _near_int(elev_median, 1)(content):  # 中位數 575
        stats_found += 1
    scores["summary_stats"] = min(1.0, stats_found / 3.0)

    # 機構比較：須出現平均最高與最低機構名稱，且各自平均數值接近正解。
    has_hi_agency_name = hi_agency in content
    has_lo_agency_name = lo_agency in content
    has_hi_agency_val = _near_int(agency_means[hi_agency], 5)(content)
    has_lo_agency_val = _near_int(agency_means[lo_agency], 5)(content)
    agency_names_ok = has_hi_agency_name and has_lo_agency_name
    agency_vals_ok = has_hi_agency_val and has_lo_agency_val
    scores["agency_comparison"] = (
        1.0 if (agency_names_ok and agency_vals_ok)
        else (0.5 if agency_names_ok else 0.0))

    # 縣市分析：須出現「縣／市」字樣與平均海拔最高／最低的縣市名。
    county_kw = bool(re.search(r"縣|市", content))
    has_top_county = top_county in content
    has_bot_county = bot_county in content
    county_found = (
        (1 if county_kw else 0)
        + (1 if has_top_county else 0)
        + (1 if has_bot_county else 0))
    scores["county_analysis"] = (
        1.0 if county_found >= 3
        else (0.5 if county_found >= 1 else 0.0))

    # 總結／解讀段落：須有總結字樣，並對高海拔（林業署／高山）與低海拔
    # （中央氣象署／平原海濱）型態作出解讀。
    summary_kw = bool(re.search(
        r"總結|結論|摘要|解讀|型態|分布|綜觀|整體", content))
    high_pattern = bool(re.search(
        r"(?:林業署|高山|山區|稜線|野溪|林班).{0,40}"
        r"(?:高|海拔較高|地勢高|偏高)", content)) or bool(re.search(
        r"(?:高|海拔較高|地勢高|偏高).{0,40}(?:林業署|高山|山區|稜線)",
        content))
    low_pattern = bool(re.search(
        r"(?:中央氣象署|平原|市區|海濱|沿海|低地).{0,40}"
        r"(?:低|海拔較低|地勢低|偏低)", content)) or bool(re.search(
        r"(?:低|海拔較低|地勢低|偏低).{0,40}"
        r"(?:中央氣象署|平原|市區|海濱|沿海)", content))
    summary_found = (
        (1 if summary_kw else 0)
        + (1 if high_pattern else 0)
        + (1 if low_pattern else 0))
    scores["summary_paragraph"] = (
        1.0 if summary_found >= 2
        else (0.5 if summary_found >= 1 else 0.0))

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
