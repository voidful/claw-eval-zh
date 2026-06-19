"""Grader for T075tw_csv_cities_growth (Taiwan-localized from PinchBench `task_csv_cities_growth`).

Phase 2 source: tasks_zh/task_csv_cities_growth.md
Original file: tasks/task_csv_cities_growth.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣鄉鎮市區地理分布 grader。

    正解一律從工作區內的 tw_townships.csv 動態計算（不沿用任何原版英文數值），
    再比對 agent 產生的中文報告 townships_geographic_report.md。報告為中文，
    故以中文關鍵字／數值比對。轉換器會在其後接上中→英正規化 wrapper。
    """
    from pathlib import Path
    import csv as _csv
    import re
    import math

    workspace = Path(workspace_path)

    report_path = workspace / "townships_geographic_report.md"
    if not report_path.exists():
        for alt in ["geographic_report.md", "townships_report.md", "report.md",
                    "geo_report.md", "cities_geographic_report.md",
                    "townships_geographic.md", "distribution_report.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = ["report_created", "weighted_centroid", "geographic_extremes",
            "latitude_bands", "east_west_split", "county_spread"]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    content = report_path.read_text(encoding="utf-8", errors="ignore")
    low = content.lower()

    # --- 從 CSV 動態計算正解 ---
    csv_path = workspace / "tw_townships.csv"
    rows = []
    if csv_path.exists():
        with csv_path.open(encoding="utf-8", errors="ignore") as f:
            for r in _csv.DictReader(f):
                try:
                    rows.append({
                        "name": r["Township"], "county": r["County"],
                        "pop": int(r["Population"]),
                        "lat": float(r["lat"]), "lon": float(r["lon"]),
                    })
                except (KeyError, ValueError):
                    pass

    # 預設（萬一 CSV 缺失，仍給可運作的回退值，對應目前 fixture 實算結果）
    most_band_count = 76
    ew_east_count, ew_west_count = 84, 120
    north_county = south_county = east_county = west_county = ""
    widest_county = "高雄"
    narrow_county = "臺北"
    w_lat = w_lon = u_lat = u_lon = None
    if rows:
        n = len(rows)
        totpop = sum(r["pop"] for r in rows)
        w_lat = sum(r["lat"] * r["pop"] for r in rows) / totpop
        w_lon = sum(r["lon"] * r["pop"] for r in rows) / totpop
        u_lat = sum(r["lat"] for r in rows) / n
        u_lon = sum(r["lon"] for r in rows) / n

        north_county = max(rows, key=lambda r: r["lat"])["county"]
        south_county = min(rows, key=lambda r: r["lat"])["county"]
        east_county = max(rows, key=lambda r: r["lon"])["county"]
        west_county = min(rows, key=lambda r: r["lon"])["county"]

        def band(lat):
            if lat < 23:
                return 0
            if lat < 24:
                return 1
            if lat < 25:
                return 2
            if lat < 26:
                return 3
            return 4
        bcount = [0, 0, 0, 0, 0]
        bpop = [0, 0, 0, 0, 0]
        for r in rows:
            b = band(r["lat"])
            bcount[b] += 1
            bpop[b] += r["pop"]
        most_band_idx = max(range(5), key=lambda i: bcount[i])
        most_band_count = bcount[most_band_idx]

        DIV = 121.0
        ew_east_count = sum(1 for r in rows if r["lon"] >= DIV)
        ew_west_count = sum(1 for r in rows if r["lon"] < DIV)

        groups = {}
        for r in rows:
            groups.setdefault(r["county"], []).append(r)
        spreads = []
        for cty, rs in groups.items():
            if len(rs) < 10:
                continue
            lats = [r["lat"] for r in rs]
            lons = [r["lon"] for r in rs]
            sp = math.hypot(max(lats) - min(lats), max(lons) - min(lons))
            spreads.append((cty, sp))
        if spreads:
            spreads.sort(key=lambda x: -x[1])
            widest_county = spreads[0][0]
            narrow_county = spreads[-1][0]

    def has_any(*subs):
        return any(s and s in content for s in subs)

    def in_report(county):
        # 去掉「縣／市」字尾後也接受，報告可能只寫「花蓮」
        if not county:
            return False
        return county in content or county.rstrip("縣市") in content

    scores = {"report_created": 1.0}

    # 1) 加權重心：概念 + 數值（接近實算的加權緯度／經度）+ 與未加權比較。
    # 數值門檻一律以 CSV 實算的加權重心為準（±0.3° 容差），不寫死任何座標。
    centroid_concept = bool(re.search(r"加權|重心|人口.*中心|中心.*人口", content))
    nums = [float(x) for x in re.findall(r"\d{1,3}\.\d+", content)]
    if w_lat is not None:
        lat_val = any(abs(v - w_lat) <= 0.3 for v in nums)
        lon_val = any(abs(v - w_lon) <= 0.3 for v in nums)
    else:
        # 回退：CSV 缺失時退回對目前 fixture 的寬鬆範圍比對
        lat_val = bool(re.search(r"24\.[0-5]\d*", content))
        lon_val = bool(re.search(r"120\.[8-9]\d*|121\.0", content))
    unweighted = bool(re.search(r"未加權|簡單.*重心|不加權|未以.*加權", content))
    if centroid_concept and lat_val and lon_val and unweighted:
        scores["weighted_centroid"] = 1.0
    elif centroid_concept and (lat_val or lon_val):
        scores["weighted_centroid"] = 0.5
    else:
        scores["weighted_centroid"] = 0.0

    # 2) 地理極值：四個方向所屬縣市，皆由 CSV 動態判定（目前為最北連江、
    #    最南屏東、最東新北、最西金門），報告須同時寫出方向詞與正確縣市。
    ext = 0
    ext += 1 if (re.search(r"最北", content) and in_report(north_county)) else 0
    ext += 1 if (re.search(r"最南", content) and in_report(south_county)) else 0
    ext += 1 if (re.search(r"最東", content) and in_report(east_county)) else 0
    ext += 1 if (re.search(r"最西", content) and in_report(west_county)) else 0
    scores["geographic_extremes"] = 1.0 if ext >= 4 else (0.5 if ext >= 2 else 0.0)

    # 3) 緯度帶：帶標籤 ≥2 + 最多帶數值
    band_hits = sum(1 for p in [r"23.{0,3}24", r"24.{0,3}25", r"25.{0,3}26",
                                r"緯度帶", r"緯度.*分"] if re.search(p, content))
    has_most = str(most_band_count) in content
    if band_hits >= 2 and has_most:
        scores["latitude_bands"] = 1.0
    elif band_hits >= 2:
        scores["latitude_bands"] = 0.5
    else:
        scores["latitude_bands"] = 0.0

    # 4) 東西分割：東/西概念 + 121 分界 + 兩半計數
    ew = 0
    ew += 1 if re.search(r"東半|西半|東西|東.*西.*分|分.*東.*西", content) else 0
    ew += 1 if re.search(r"121", content) else 0
    ew += 1 if str(ew_east_count) in content else 0
    ew += 1 if str(ew_west_count) in content else 0
    scores["east_west_split"] = 1.0 if ew >= 3 else (0.5 if ew >= 2 else 0.0)

    # 5) 縣市跨幅：跨幅概念 + 最廣縣市（由 CSV 動態判定，目前為高雄）
    #    + 最集中縣市（目前為臺北），兩者皆從 fixture 實算後比對報告。
    #    為避免「把答案對調」也拿滿分，這裡要求方向詞與縣市名在鄰近範圍內
    #    出現（任一語序皆可），亦即最廣縣市須緊鄰「最廣／分布最廣」等敘述、
    #    最集中縣市須緊鄰「最集中／最密／分布最窄」等敘述。
    spread_concept = bool(re.search(r"跨幅|分布.*廣|地理.*範圍|範圍|對角|最廣|分散", content))

    def _county_forms(county):
        # 同時接受「高雄市」與「高雄」兩種寫法。
        if not county:
            return None
        short = county.rstrip("縣市")
        forms = {county, short}
        return "(?:" + "|".join(re.escape(f) for f in forms if f) + ")"

    def attributed(county, desc_pat, window=12):
        # 縣市名與方向敘述須在 window 字元內共現（任一語序），避免對調作答得分。
        # gap 內不得跨越標點（，。、；！？換行或表格分隔），以免兩個對調子句
        # 互相沾染（例如「跨幅最廣的是臺北市，最集中的是高雄市」不應讓高雄被判為最廣）。
        cf = _county_forms(county)
        if not cf:
            return False
        gap = r"[^，。、；！？\n\r|]{0,%d}" % window
        return bool(
            re.search(cf + gap + desc_pat, content)
            or re.search(desc_pat + gap + cf, content)
        )

    # 最廣縣市須與「最廣／分布最廣／跨幅最大／範圍最大」等敘述鄰近共現。
    widest_desc = r"(?:最廣|分布最廣|跨幅最大|範圍最大|跨距最大|分布範圍最大)"
    # 最集中縣市須與「最集中／最密／分布最窄／跨幅最小」等敘述鄰近共現。
    narrow_desc = r"(?:最集中|最密集|最密|分布最窄|範圍最小|跨幅最小|跨距最小|最緊密)"
    widest_ok = attributed(widest_county, widest_desc)
    narrow_ok = attributed(narrow_county, narrow_desc)
    if spread_concept and widest_ok and narrow_ok:
        scores["county_spread"] = 1.0
    elif spread_concept and (widest_ok or narrow_ok):
        scores["county_spread"] = 0.5
    else:
        scores["county_spread"] = 0.0

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
