"""Grader for T078tw_csv_pension_risk (Taiwan-localized from PinchBench `task_csv_pension_risk`).

Phase 2 source: tasks_zh/task_csv_pension_risk.md
Original file: tasks/task_csv_pension_risk.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """對台灣退休金 CSV 動態實算正解，再比對 agent 的中文報告。

    報告為中文（轉換器會在其後接上中→英關鍵字 wrapper），故本 grader 以
    中文關鍵字與數值為主進行比對；縣市名稱／代碼不在英譯字典內，必須直接
    比對中文。所有「應有事實」皆從工作區的 tw_pension.csv 即時推導。
    """
    import csv
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 找出報告檔 ---
    report_path = workspace / "pension_risk_report.md"
    if not report_path.exists():
        alternatives = [
            "risk_report.md", "report.md", "pension_report.md",
            "pension_risk.md", "risk_assessment.md", "退休金風險報告.md",
            "退休金風險評估.md", "風險評估報告.md",
        ]
        for alt in alternatives:
            p = workspace / alt
            if p.exists():
                report_path = p
                break
    # 退而求其次：任何含關鍵字的 .md
    if not report_path.exists():
        for p in workspace.rglob("*.md"):
            try:
                t = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if ("遞延" in t or "比值" in t) and ("風險" in t or "risk" in t.lower()):
                report_path = p
                break

    keys = [
        "report_created", "ratio_ranking", "outlier_highest_ratio",
        "second_ratio", "concentration_risk", "district_hotspots",
        "top_district", "risk_tiers", "high_risk_states",
        "summary_recommendations",
    ]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8")
    low = content.lower()

    # --- 從 CSV 動態實算正解 ---
    csv_path = workspace / "tw_pension.csv"
    if not csv_path.exists():
        for p in workspace.rglob("*.csv"):
            csv_path = p
            break

    def to_num(s):
        s = re.sub(r"[^0-9.]", "", s or "")
        return float(s) if s else 0.0

    totals = []        # 縣市總計（含特殊類別）
    districts = []     # 選區列
    grand = None
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("STATE_ABBREV_NAME") or "").strip()
            dist = (row.get("DISTRICT") or "").strip()
            amt = to_num(row.get("PAYEE_AMOUNT"))
            pc = to_num(row.get("PAYEE_COUNT"))
            dc = to_num(row.get("DEFERRED_COUNT"))
            if name == "Grand Total":
                grand = {"amt": amt, "pc": pc, "dc": dc}
                continue
            if name.endswith("Total"):
                short = name.replace("Total", "").strip()
                totals.append({"name": short, "amt": amt, "pc": pc, "dc": dc})
            elif name:
                districts.append({"name": name, "dist": dist, "amt": amt,
                                  "pc": pc, "dc": dc})

    # 純中文縣市名（去掉代碼前綴 "TXG-" 等）
    def zh_name(full):
        return full.split("-", 1)[1].strip() if "-" in full else full.strip()

    # 比值排名（PC>=100）
    ratios = []
    for t in totals:
        if t["pc"] >= 100:
            ratios.append((zh_name(t["name"]), t["dc"] / t["pc"] if t["pc"] else 0.0))
    ratios.sort(key=lambda x: -x[1])
    top10_names = [n for n, _ in ratios[:10]]
    outlier_name, outlier_ratio = ratios[0]          # 中央直轄機關, ~5.69
    second_name, second_ratio = ratios[1]            # 連江縣, ~0.89

    # 集中度（依金額）
    total_amt = sum(t["amt"] for t in totals) or 1.0
    by_amt = sorted(totals, key=lambda x: -x["amt"])
    top5_pct = sum(t["amt"] for t in by_amt[:5]) / total_amt * 100
    top10_pct = sum(t["amt"] for t in by_amt[:10]) / total_amt * 100
    top5_names = [zh_name(t["name"]) for t in by_amt[:5]]

    # 選區熱點（依金額）
    by_d = sorted(districts, key=lambda x: -x["amt"])
    top_districts = by_d[:5]
    top_d = top_districts[0]                          # 臺中市-13
    top_d_zh = zh_name(top_d["name"])
    top_d_dist = top_d["dist"]
    top_d_amt_m = top_d["amt"] / 1_000_000            # ~113.3

    # 風險等級
    high_tier = [n for n, r in ratios if r > 0.75]
    med_tier = [n for n, r in ratios if 0.50 <= r <= 0.75]
    low_tier = [n for n, r in ratios if r < 0.50]

    nat_avg = (grand["dc"] / grand["pc"]) if grand and grand["pc"] else 0.0

    # ---------- 1) 比值排名：前 10 大縣市有被提到 ----------
    ratio_ctx = bool(re.search(r"遞延|比值|ratio", low))
    named = sum(1 for n in top10_names if n in content)
    scores["ratio_ranking"] = (
        1.0 if (named >= 5 and ratio_ctx)
        else 0.5 if named >= 2
        else 0.0
    )

    # ---------- 2) 最高比值離群值（中央直轄機關 ~5.69）----------
    outlier_num = f"{outlier_ratio:.1f}"            # "5.7"
    outlier_num2 = f"{outlier_ratio:.2f}"           # "5.69"
    outlier_present = (outlier_name in content)
    outlier_val = bool(re.search(re.escape(outlier_num2), content)
                       or re.search(r"5\.[67]", content))
    outlier_ctx = bool(re.search(r"離群|最高|極端|outlier|highest", low))
    scores["outlier_highest_ratio"] = (
        1.0 if (outlier_present and (outlier_val or outlier_ctx))
        else 0.5 if outlier_present
        else 0.0
    )

    # ---------- 3) 第二高（地方縣市中最高，連江縣 ~0.89 / 臺北市 ~0.88）----------
    # 因 #2~#4 比值極接近（0.886/0.880/0.876，四捨五入皆 0.88~0.89），
    # 接受其中任一個被點名為地方縣市中比值最高者。
    near_top = [n for n, r in ratios[1:5]]
    second_present = sum(1 for n in near_top if n in content)
    second_val = bool(re.search(r"0\.8[5-9]", content))
    scores["second_ratio"] = (
        1.0 if (second_present >= 1 and second_val)
        else 0.5 if second_present >= 1
        else 0.0
    )

    # ---------- 4) 集中度風險 ----------
    # 從報告中抽出所有百分比數值，以 ±2 百分點容差比對實算值
    # （容許整數或一位小數，例如 61.6% / 62%）。
    conc_ctx = bool(re.search(r"集中度|concentration", low))
    report_pcts = [float(m) for m in re.findall(r"(\d+(?:\.\d+)?)\s*%", content)]

    def pct_hit(target):
        return any(target - 2 <= v <= target + 2 for v in report_pcts)

    top5_hit = pct_hit(top5_pct)
    top10_hit = pct_hit(top10_pct)
    scores["concentration_risk"] = (
        1.0 if (top5_hit and top10_hit)
        else 0.5 if (conc_ctx and (top5_hit or top10_hit))
        else 0.5 if conc_ctx
        else 0.0
    )

    # ---------- 5) 選區級熱點 ----------
    dist_ctx = bool(re.search(r"選區|熱點|district|hotspot", low))
    hot_hit = 0
    for d in top_districts:
        zn = zh_name(d["name"])
        # 例如「臺中市第 13 選區」「臺中市-13」「臺中市 13」
        pat = rf"{re.escape(zn)}[^0-9]{{0,6}}{re.escape(str(d['dist']))}\b"
        if re.search(pat, content):
            hot_hit += 1
    scores["district_hotspots"] = (
        1.0 if (hot_hit >= 3 and dist_ctx)
        else 0.5 if hot_hit >= 2
        else 0.0
    )

    # ---------- 6) 金額最高的選區（臺中市第 13）----------
    amt_m = round(top_d_amt_m)                       # 113
    top_d_pat = rf"{re.escape(top_d_zh)}[^0-9]{{0,6}}{re.escape(str(top_d_dist))}\b"
    top_d_named = bool(re.search(top_d_pat, content))
    top_d_amt_hit = bool(re.search(rf"{amt_m}", content)
                         or re.search(r"113", content))
    top_d_ctx = bool(re.search(r"最高|最大|first|top|highest|金額最", low))
    scores["top_district"] = (
        1.0 if (top_d_named and (top_d_amt_hit or top_d_ctx))
        else 0.5 if top_d_named
        else 0.0
    )

    # ---------- 7) 風險等級分類 ----------
    tier_terms = sum(bool(re.search(p, content)) for p in
                     [r"高風險", r"中風險", r"低風險"])
    tier_thresh = bool(re.search(r"0\.75", content) and re.search(r"0\.5", content))
    tier_counts = bool(re.search(rf"{len(high_tier)}", content)
                       and re.search(rf"{len(low_tier)}", content))
    tcount = (1 if tier_terms >= 2 else 0) + (1 if tier_thresh else 0) \
        + (1 if tier_counts else 0)
    scores["risk_tiers"] = (
        1.0 if tcount >= 2 else 0.5 if tcount >= 1 else 0.0
    )

    # ---------- 8) 高風險縣市清單 ----------
    hr_named = sum(1 for n in high_tier if n in content)
    hr_ctx = bool(re.search(r"高風險", content))
    scores["high_risk_states"] = (
        1.0 if (hr_named >= max(3, len(high_tier) - 1) and hr_ctx)
        else 0.5 if hr_named >= 2
        else 0.0
    )

    # ---------- 9) 摘要與建議 ----------
    rec_patterns = [
        r"建議|recommend",
        r"監測|監控|關注|留意|注意|monitor",
        r"管理|因應|處理|規劃|mitigat|manag",
        r"摘要|總體|整體|風險樣貌|summary",
    ]
    rec = sum(1 for p in rec_patterns if re.search(p, low))
    scores["summary_recommendations"] = (
        1.0 if rec >= 2 else 0.5 if rec >= 1 else 0.0
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
