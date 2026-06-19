"""Grader for T074tw_csv_cities_density (Taiwan-localized from PinchBench `task_csv_cities_density`).

Phase 2 source: tasks_zh/task_csv_cities_density.md
Original file: tasks/task_csv_cities_density.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣各縣市鄉鎮人口集中度 grader。

    正解一律從工作區內的 tw_townships_density.csv 動態實算，再比對 agent 的中文
    報告 cities_density_report.md。fixture 無 Region 欄，五大區域由縣市名以對照表
    推導。僅用標準函式庫。報告為中文，故以中文關鍵字／數值比對；轉換器會在其後
    接上中→英正規化 wrapper。
    """
    import csv
    import re
    from collections import defaultdict
    from pathlib import Path

    # 縣市 -> 五大區域（與題目一致）
    REGION = {
        "臺北市": "北部", "新北市": "北部", "桃園市": "北部", "基隆市": "北部",
        "新竹市": "北部", "新竹縣": "北部", "宜蘭縣": "北部",
        "臺中市": "中部", "苗栗縣": "中部", "彰化縣": "中部",
        "南投縣": "中部", "雲林縣": "中部",
        "高雄市": "南部", "臺南市": "南部", "嘉義市": "南部",
        "嘉義縣": "南部", "屏東縣": "南部",
        "花蓮縣": "東部", "臺東縣": "東部",
        "澎湖縣": "外島", "金門縣": "外島", "連江縣": "外島",
    }

    workspace = Path(workspace_path)

    # --- 找報告 ---
    report_path = workspace / "cities_density_report.md"
    if not report_path.exists():
        for alt in [
            "density_report.md", "report.md",
            "concentration_report.md", "cities_report.md",
        ]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = [
        "report_created", "avg_pop_ranking", "township_dominance",
        "county_count", "fewest_counties", "inequality_ratios",
        "regional_summary",
    ]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    c = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 從 fixture 實算正解 ---
    csv_path = workspace / "tw_townships_density.csv"
    if not csv_path.exists():
        # 容錯：接受其他可能 dest 名
        for alt in ["tw_townships.csv", "townships.csv"]:
            if (workspace / alt).exists():
                csv_path = workspace / alt
                break
    if not csv_path.exists():
        return {k: (1.0 if k == "report_created" else 0.0) for k in keys}

    rows = []
    with csv_path.open(encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            try:
                r["Population"] = int(r["Population"])
            except (TypeError, ValueError, KeyError):
                continue
            if not r.get("County"):
                continue
            rows.append(r)

    if not rows:
        return {k: (1.0 if k == "report_created" else 0.0) for k in keys}

    by_county = defaultdict(list)
    for r in rows:
        by_county[r["County"]].append(r)

    county_count = len(by_county)

    # [1] 各縣市每鄉鎮平均人口排名
    avg = []
    for county, v in by_county.items():
        tot = sum(x["Population"] for x in v)
        avg.append((county, tot / len(v)))
    avg.sort(key=lambda x: -x[1])
    top_avg_county = avg[0][0]      # 臺北市
    bottom_avg_county = avg[-1][0]  # 連江縣

    # [2] 單一鄉鎮主導（鄉鎮數>=5）
    dom = []
    for county, v in by_county.items():
        if len(v) >= 5:
            tot = sum(x["Population"] for x in v)
            mx = max(v, key=lambda x: x["Population"])
            dom.append((county, mx["Population"] / tot * 100))
    dom.sort(key=lambda x: -x[1])
    top_dom_county = dom[0][0] if dom else ""  # 臺東縣

    # [3] 代表性
    counts = sorted(
        ((county, len(v)) for county, v in by_county.items()),
        key=lambda x: -x[1],
    )
    most_county = counts[0][0]     # 新北市
    fewest_county = counts[-1][0]  # 嘉義市

    # [4] 不均比值（鄉鎮數>=10）
    ineq = []
    for county, v in by_county.items():
        if len(v) >= 10:
            mx = max(x["Population"] for x in v)
            mn = min(x["Population"] for x in v)
            if mn > 0:
                ineq.append((county, mx / mn))
    ineq.sort(key=lambda x: -x[1])
    most_unequal = ineq[0][0] if ineq else ""  # 高雄市
    most_equal = ineq[-1][0] if ineq else ""    # 臺北市

    scores = {"report_created": 1.0}

    # avg_pop_ranking：點出每鄉鎮平均最高的縣市（臺北市），且涉及「平均」概念
    has_avg_word = ("平均" in c) or ("每鄉鎮" in c) or ("每個鄉鎮" in c)
    scores["avg_pop_ranking"] = 1.0 if (top_avg_county in c and has_avg_word) else 0.0

    # township_dominance：指出主導度最高的縣市（臺東縣），並有主導／集中相關語彙
    dom_word = any(w in c for w in ["主導", "集中", "占", "佔", "比例", "百分比"])
    scores["township_dominance"] = (
        1.0 if (top_dom_county and top_dom_county in c and dom_word)
        else (0.5 if dom_word else 0.0)
    )

    # county_count：報告需出現正確縣市數（22）
    cc = str(county_count)
    cc_hit = bool(
        re.search(cc + r"\s*(?:個|個縣市|縣市)", c)
        or re.search(r"(?:縣市|不同).{0,8}" + cc, c)
    )
    scores["county_count"] = 1.0 if cc_hit else 0.0

    # fewest_counties：指出鄉鎮最多（新北）與最少（嘉義市）的縣市
    found_most = most_county in c
    found_few = fewest_county in c
    scores["fewest_counties"] = (
        1.0 if (found_most and found_few)
        else (0.5 if (found_most or found_few) else 0.0)
    )

    # inequality_ratios：有比值／不均語彙，且點出最不均(高雄市)或最均(臺北市)
    ratio_word = any(w in c for w in ["比值", "倍", "不均", "差距", "ratio"])
    named = (most_unequal and most_unequal in c) or (most_equal and most_equal in c)
    scores["inequality_ratios"] = (
        1.0 if (ratio_word and named)
        else (0.5 if ratio_word else 0.0)
    )

    # regional_summary：至少出現 3 個區域名稱
    found_regions = sum(1 for rg in ["北部", "中部", "南部", "東部", "外島"] if rg in c)
    scores["regional_summary"] = (
        1.0 if found_regions >= 3
        else (0.5 if found_regions >= 2 else 0.0)
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
