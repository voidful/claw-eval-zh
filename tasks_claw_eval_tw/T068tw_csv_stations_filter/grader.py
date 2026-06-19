"""Grader for T068tw_csv_stations_filter (Taiwan-localized from PinchBench `task_csv_stations_filter`).

Phase 2 source: tasks_zh/task_csv_stations_filter.md
Original file: tasks/task_csv_stations_filter.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣氣象站多條件篩選 grader。所有「應有事實」皆從工作區的
    tw_weather_stations.csv 動態計算，不沿用美國數值。報告為中文，
    故比對中文關鍵字與數值。"""
    import csv
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # ---- 定位報告檔 ----
    report_path = workspace / "filter_report.md"
    if not report_path.exists():
        for alt in [
            "report.md", "filter_results.md", "filtering_report.md",
            "analysis.md", "stations_filter.md", "氣象站篩選報告.md",
        ]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = [
        "report_created", "forestry_high_count", "forestry_highest",
        "wra_kaohsiung_count", "southern_mid_count", "southern_mid_stations",
        "cross_tabulation",
    ]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    # ---- 從 CSV 動態計算正解 ----
    csv_path = workspace / "tw_weather_stations.csv"
    if not csv_path.exists():
        return {k: 0.0 for k in keys}

    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig")))

    def dms_to_dd(s):
        parts = (s or "").split()
        d, m, sec = (parts + ["0", "0", "0"])[:3]
        return int(d) + int(m) / 60 + int(sec) / 3600

    for r in rows:
        r["elev"] = int(r["Elevation (meters)"])
        r["lat_dd"] = dms_to_dd(r["Latitude"])

    # F1: 林業署, 海拔 >= 3000 公尺, 由高到低
    f1 = sorted(
        [r for r in rows if r["Managing Agency"] == "林業署" and r["elev"] >= 3000],
        key=lambda r: -r["elev"],
    )
    f1_count = len(f1)
    f1_top_name = f1[0]["Station Name"] if f1 else ""
    f1_top_elev = f1[0]["elev"] if f1 else 0

    # F2: 水利署 in 高雄市
    f2 = [r for r in rows if r["Managing Agency"] == "水利署" and r["County"] == "高雄市"]
    f2_count = len(f2)

    # F3: 海拔 1000-2000 公尺(含) 且 緯度 23.5°N 以南
    f3 = sorted(
        [r for r in rows if 1000 <= r["elev"] <= 2000 and r["lat_dd"] < 23.5],
        key=lambda r: -r["elev"],
    )
    f3_count = len(f3)
    f3_names = [r["Station Name"] for r in f3]

    # 各機構合計
    forestry_total = sum(1 for r in rows if r["Managing Agency"] == "林業署")
    cwb_total = sum(1 for r in rows if r["Managing Agency"] == "中央氣象署")
    wra_total = sum(1 for r in rows if r["Managing Agency"] == "水利署")

    # ---- 讀報告 ----
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    digits = re.sub(r"[,\s]", "", content)  # 去掉千分位與空白便於比數字

    def has_count(n):
        """報告中是否把數量 n 當成「測站總數」陳述。
        需數字 n 與計數量詞相鄰（N 個／N 站／N 座／N 處／N 筆／N 測站，
        或「共 N」「總共 N」「計 N」），不接受報告中任意出現的裸數字，
        以免只把數字撒進無關文字就拿分。"""
        pat = (
            rf"(?<!\d){n}(?!\d)\s*(?:個|站|座|處|筆|測站)"
            rf"|(?:共|總共|計|合計|數量為|為)\s*(?<!\d){n}(?!\d)\s*(?:個|站|座|處|筆|測站)?"
        )
        return bool(re.search(pat, content))

    scores = {"report_created": 1.0}

    # F1 數量
    scores["forestry_high_count"] = 1.0 if has_count(f1_count) else 0.0

    # F1 最高站：站名 + 海拔
    has_top_name = bool(f1_top_name) and (f1_top_name in content)
    has_top_elev = str(f1_top_elev) in digits
    scores["forestry_highest"] = (
        1.0 if (has_top_name and has_top_elev)
        else (0.5 if has_top_name else 0.0)
    )

    # F2 數量（需同時提及「高雄」）
    scores["wra_kaohsiung_count"] = (
        1.0 if (has_count(f2_count) and "高雄" in content) else 0.0
    )

    # F3 數量
    scores["southern_mid_count"] = 1.0 if has_count(f3_count) else 0.0

    # F3 站名命中率（正解 12 站，命中 >=8 給滿分）
    found = sum(1 for nm in f3_names if nm in content)
    scores["southern_mid_stations"] = (
        1.0 if found >= max(8, int(0.66 * f3_count))
        else (0.5 if found >= max(4, int(0.33 * f3_count)) else 0.0)
    )

    # 交叉統計表
    ct_hits = 0
    # (a) 出現交叉統計表的結構性字眼
    if re.search(r"交叉|統計表|矩陣|機構.{0,6}海拔|海拔.{0,6}機構|管理機構", content):
        ct_hits += 1
    # (b) 三個機構各自的「合計」需與機構名相鄰出現（避免只把 54/95/41 撒進文字）。
    #     在每個機構名之後 12 個字內找到對應總數，才算數。
    def agency_total_near(name, total):
        for m in re.finditer(re.escape(name), content):
            window = re.sub(r"[,\s]", "", content[m.end():m.end() + 24])
            if re.search(rf"(?<!\d){total}(?!\d)", window):
                return True
        return False
    if (
        agency_total_near("林業署", forestry_total)
        and agency_total_near("中央氣象署", cwb_total)
        and agency_total_near("水利署", wra_total)
    ):
        ct_hits += 1
    # (c) 出現海拔分帶的欄位標籤
    if re.search(r"未滿\s*1,?000|below\s*1000|<\s*1000|3,?000\s*以上|3000\+", content, re.IGNORECASE):
        ct_hits += 1
    scores["cross_tabulation"] = 1.0 if ct_hits >= 2 else (0.5 if ct_hits >= 1 else 0.0)

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
