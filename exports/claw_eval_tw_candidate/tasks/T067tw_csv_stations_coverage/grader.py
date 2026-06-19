"""Grader for T067tw_csv_stations_coverage (Taiwan-localized from PinchBench `task_csv_stations_coverage`).

Phase 2 source: tasks_zh/task_csv_stations_coverage.md
Original file: tasks/task_csv_stations_coverage.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """全臺氣象站涵蓋缺口分析 grader（台灣 CSV）。

    以工作區內的台灣 CSV（dest=tw_weather_stations.csv）動態計算「應有的
    涵蓋／密度／海拔／機關」正解，再比對 agent 產出的中文報告 coverage_report.md。
    不沿用原始美國資料集數值。僅用標準函式庫。
    轉換器會在其後自動接上中→英正規化 wrapper，毋須自行處理。
    """
    from pathlib import Path
    import csv as _csv
    import re
    from collections import Counter

    workspace = Path(workspace_path)
    keys = [
        "report_created", "missing_county_identified", "county_counts",
        "elevation_bands", "agency_comparison", "missing_data", "recommendations",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report_path = workspace / "coverage_report.md"
    if not report_path.exists():
        for alt in ["coverage.md", "report.md", "gap_analysis.md", "analysis.md",
                    "coverage_analysis.md", "涵蓋分析.md", "涵蓋報告.md",
                    "氣象站涵蓋分析.md", "coverage_report.txt"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    content = report_path.read_text(encoding="utf-8", errors="ignore")
    content_lower = content.lower()
    scores = {"report_created": 1.0}

    # --- 從台灣 CSV 動態讀出正解（避免硬寫；以實際 fixture 為準） ---
    csv_path = workspace / "tw_weather_stations.csv"
    if not csv_path.exists():
        for alt in ["weather_stations.csv", "stations.csv"]:
            if (workspace / alt).exists():
                csv_path = workspace / alt
                break

    rows = []
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig", errors="ignore") as f:
            reader = _csv.DictReader(f)
            for r in reader:
                rows.append({(k or "").strip(): (v.strip() if v else "")
                             for k, v in r.items()})

    # 台灣 22 個直轄市／縣／市
    tw22 = [
        "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
        "宜蘭縣", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
        "屏東縣", "臺東縣", "花蓮縣", "澎湖縣", "金門縣", "連江縣",
        "基隆市", "新竹市", "嘉義市",
    ]

    counties = [r.get("County", "") for r in rows]
    nonblank = [c for c in counties if c]
    blank_rows = [r for r in rows if not r.get("County", "")]
    cc = Counter(nonblank)
    present = set(nonblank)
    missing_counties = [c for c in tw22 if c not in present]  # 應為 ['連江縣']
    top_counties = [c for c, _ in cc.most_common(6)]          # 南投縣居首
    single_counties = sorted([c for c, n in cc.items() if n == 1])
    n_blank = len(blank_rows)                                 # 應為 5
    blank_station_names = [r.get("Station Name", "") for r in blank_rows]

    # 若 CSV 缺失，退回硬編碼正解（以實際 fixture 計算所得）作為保底
    if not rows:
        missing_counties = ["連江縣"]
        top_counties = ["南投縣", "花蓮縣", "高雄市", "臺中市", "臺東縣", "宜蘭縣"]
        single_counties = ["基隆市", "新竹市", "金門縣"]
        cc = Counter({"南投縣": 17})
        n_blank = 5
        blank_station_names = ["大霸尖山站", "拉拉山野溪站", "南湖大山林道站",
                               "玉山保線所站", "關山山站"]

    # === 1. 缺漏縣市（連江縣）已被指認 ===
    miss_score = 0.0
    for mc in missing_counties:
        if mc and mc in content:
            # 報告中應指出此縣市「沒有／零」氣象站
            near = re.search(re.escape(mc) + r"[^。\n]{0,40}(?:沒有|零|0|缺|無|未設|不足)",
                             content)
            near2 = re.search(r"(?:沒有|零|缺|無|未設)[^。\n]{0,40}" + re.escape(mc),
                              content)
            miss_score = 1.0 if (near or near2) else 0.6
            break
    scores["missing_county_identified"] = miss_score

    # === 2. 各縣市氣象站數，且最多的縣市（南投縣 17）正確 ===
    # 取實際前五多縣市，檢查報告中縣市名旁是否出現對應正確計數。
    top5 = cc.most_common(5)
    hit = 0
    for cname, cnum in top5:
        # 縣市名出現，且其正確計數（cnum）也出現在縣市名附近（任一方向，60 字內）
        pat1 = re.escape(cname) + r"[^\n]{0,60}\b" + str(cnum) + r"\b"
        pat2 = r"\b" + str(cnum) + r"\b[^\n]{0,30}" + re.escape(cname)
        if re.search(pat1, content) or re.search(pat2, content):
            hit += 1
    if hit >= 3:
        scores["county_counts"] = 1.0
    elif hit >= 1:
        scores["county_counts"] = 0.5
    else:
        scores["county_counts"] = 0.0

    # === 3. 海拔帶分布 ===
    elev_indicators = 0
    # 「海拔」要與分組概念詞鄰近（同一段、30 字內），避免「氣象站分布在全臺」
    # 之類泛用「分布」誤觸。
    if re.search(r"海拔[^\n]{0,30}(?:帶|分組|區間|級距)"
                 r"|(?:海拔)?(?:帶|分組|區間|級距)[^\n]{0,12}海拔"
                 r"|海拔[^\n]{0,12}分布", content):
        elev_indicators += 1
    # 出現多個海拔分組數字（公尺刻度）
    if re.search(r"(?:500|1[,.]?000|1[,.]?500|2[,.]?000|3[,.]?000)\s*(?:公尺|m|公里)?",
                 content):
        elev_indicators += 1
    # 指出低海拔密集 / 高海拔稀疏（涵蓋過多／不足）
    if (re.search(r"(?:低海拔|1[,.]?000\s*公尺以下|0[\-－~～]500)", content)
            and re.search(r"(?:集中|密集|最多|過多|偏多)", content)) or \
       re.search(r"(?:稀疏|不足|偏少|稀少|涵蓋過少)", content):
        elev_indicators += 1
    if elev_indicators >= 2:
        scores["elevation_bands"] = 1.0
    elif elev_indicators >= 1:
        scores["elevation_bands"] = 0.5
    else:
        scores["elevation_bands"] = 0.0

    # === 4. 機關比較（中央氣象署 / 林業署 / 水利署） ===
    agencies = Counter(r.get("Managing Agency", "") for r in rows if r)
    # 實際三大機關名稱（取出現的機關）
    agency_names = [a for a, _ in agencies.most_common() if a] or \
        ["中央氣象署", "林業署", "水利署"]
    agency_hit = sum(1 for a in agency_names[:3] if a and a in content)
    # 機關計數是否出現（任一機關名旁有其正確站數）
    count_hit = False
    for a, n in agencies.most_common(3):
        if a and re.search(re.escape(a) + r"[^\n]{0,40}\b" + str(n) + r"\b", content):
            count_hit = True
            break
    # 海拔／地理差異敘述
    geo_hit = bool(re.search(r"(?:平地|沿海|低海拔|高山|山區|高海拔|流域|中海拔)",
                             content))
    if agency_hit >= 2 and (count_hit or geo_hit):
        scores["agency_comparison"] = 1.0
    elif agency_hit >= 2:
        scores["agency_comparison"] = 0.5
    else:
        scores["agency_comparison"] = 0.0

    # === 5. 資料品質：縣市別空白的氣象站已被指認 ===
    md_score = 0.0
    # 報告提到「空白／缺漏的縣市別」與站數，或直接點名空白站
    name_hits = sum(1 for nm in blank_station_names if nm and nm in content)
    mentions_blank = bool(re.search(r"(?:縣市|county)[^\n]{0,20}"
                                    r"(?:空白|缺漏|缺失|遺漏|未填|無資料|空缺)", content)
                          or re.search(r"(?:空白|缺漏|缺失|遺漏|未填|空缺)[^\n]{0,20}"
                                       r"(?:縣市|county)", content))
    mentions_count = bool(re.search(r"\b" + str(n_blank) + r"\b[^\n]{0,20}"
                                    r"(?:個|站|筆|個站)", content)
                          and mentions_blank)
    if name_hits >= 3 or mentions_count:
        md_score = 1.0
    elif mentions_blank or name_hits >= 1:
        md_score = 0.6
    scores["missing_data"] = md_score

    # === 6. 建議區段 ===
    rec_patterns = [
        r"建議", r"增設", r"增點", r"補強", r"改善[^\n]{0,10}涵蓋",
        r"新增[^\n]{0,10}(?:氣象站|測站|站)", r"加強",
    ]
    scores["recommendations"] = 1.0 if any(re.search(p, content)
                                           for p in rec_patterns) else 0.0

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
