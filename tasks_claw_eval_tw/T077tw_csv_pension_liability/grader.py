"""Grader for T077tw_csv_pension_liability (Taiwan-localized from PinchBench `task_csv_pension_liability`).

Phase 2 source: tasks_zh/task_csv_pension_liability.md
Original file: tasks/task_csv_pension_liability.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """縣市退休金負債分析 grader（台灣 CSV 版）。

    以工作區內的台灣 CSV（dest=tw_pension.csv）動態實算正解，再比對 agent
    產生的中文報告 pension_liability_report.md。僅用標準函式庫。
    報告為繁體中文，故比對中文縣市名與數值關鍵字。
    """
    from pathlib import Path
    import csv
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "avg_payout_ranking", "top_avg_county",
        "deferred_ranking", "top_deferred_county", "projected_liability",
        "national_summary", "total_projected", "exposure_analysis",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "pension_liability_report.md"
    if not report.exists():
        for alt in [
            "liability_report.md", "report.md", "pension_report.md",
            "pension_liability.md", "pension_liability_report.txt",
        ]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從台灣 CSV 動態實算正解（避免硬寫美國數值） ---
    def num(s):
        s = (s or "").strip().strip('"').replace("$", "").replace(",", "").strip()
        try:
            return float(s)
        except ValueError:
            return 0.0

    csv_path = workspace / "tw_pension.csv"
    if not csv_path.exists():
        for alt in ["pension.csv", "tw_pension_by_county.csv"]:
            if (workspace / alt).exists():
                csv_path = workspace / alt
                break

    counties = []
    grand = None
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = (row.get("STATE_ABBREV_NAME") or "").strip()
                amount = num(row.get("PAYEE_AMOUNT"))
                count = num(row.get("PAYEE_COUNT"))
                deferred = num(row.get("DEFERRED_COUNT"))
                if name == "Grand Total":
                    grand = {"amount": amount, "count": count, "deferred": deferred}
                    continue
                if name.endswith("Total"):
                    label = name[: -len("Total")].strip()
                    # 取中文縣市名（去掉 "TPE-" 之類前綴）
                    zh = label.split("-")[-1].strip() if "-" in label else label
                    avg = amount / count if count else 0.0
                    counties.append({
                        "label": label, "zh": zh, "amount": amount,
                        "count": count, "deferred": deferred,
                        "avg": avg, "projected": avg * deferred,
                    })

    def topn(key, n=10):
        return sorted(counties, key=lambda x: -x[key])[:n]

    top_avg = topn("avg")
    top_def = topn("deferred")
    top_proj = topn("projected")

    # 全國摘要（以縣市彙總列加總；若有 Grand Total 列則優先採用）
    tot_amount = sum(x["amount"] for x in counties)
    tot_count = sum(x["count"] for x in counties)
    tot_deferred = sum(x["deferred"] for x in counties)
    if grand:
        tot_amount = grand["amount"] or tot_amount
        tot_count = grand["count"] or tot_count
        tot_deferred = grand["deferred"] or tot_deferred
    overall_avg = tot_amount / tot_count if tot_count else 0.0
    total_projected = overall_avg * tot_deferred

    def zh_present(name):
        # 報告可能寫 "臺北市" 或 "台北市"；做臺/台等值處理
        variants = {name, name.replace("臺", "台"), name.replace("台", "臺")}
        return any(v and v in c for v in variants)

    scores = {"report_created": 1.0}

    # 平均給付排名：前 5 大平均給付縣市中至少命中 3 個，且有「平均」語境
    has_avg_ctx = bool(re.search(r"平均給付|每位領取者|平均.{0,4}給付|average|avg", c, re.I))
    avg_hits = sum(1 for x in top_avg[:5] if zh_present(x["zh"]))
    scores["avg_payout_ranking"] = (
        1.0 if (avg_hits >= 3 and has_avg_ctx)
        else (0.5 if avg_hits >= 2 else 0.0)
    )

    # 最高平均給付縣市（動態：實算 top1）須出現，且鄰近有「最高／第一／平均」語境或其數值
    if top_avg:
        t = top_avg[0]
        tname_variants = [t["zh"], t["zh"].replace("臺", "台"), t["zh"].replace("台", "臺")]
        tname_re = "(?:%s)" % "|".join(re.escape(v) for v in set(tname_variants) if v)
        avg_int = int(round(t["avg"]))
        # 數值容忍：四捨五入到整數附近（容許千分位逗號）
        avg_num_re = r"%s[,]?%s" % (str(avg_int // 1000), "%03d" % (avg_int % 1000))
        top_avg_ok = bool(
            re.search(tname_re + r".{0,40}(?:最高|第一|第 1|#1|top|平均給付|" + avg_num_re + r")",
                      c, re.I)
            or re.search(r"(?:最高|第一|#1|top).{0,40}(?:平均|給付).{0,20}" + tname_re, c, re.I)
            or re.search(tname_re + r".{0,40}" + avg_num_re, c)
        )
    else:
        top_avg_ok = False
    scores["top_avg_county"] = 1.0 if top_avg_ok else 0.0

    # 遞延人數排名：前 5 大遞延縣市中至少命中 3 個，且有「遞延」語境
    has_def_ctx = bool(re.search(r"遞延|deferred", c, re.I))
    def_hits = sum(1 for x in top_def[:5] if zh_present(x["zh"]))
    scores["deferred_ranking"] = (
        1.0 if (def_hits >= 3 and has_def_ctx)
        else (0.5 if def_hits >= 2 else 0.0)
    )

    # 遞延最多縣市（動態 top1）須出現，且鄰近有「最多／第一／遞延」語境或其數值
    if top_def:
        t = top_def[0]
        tname_variants = [t["zh"], t["zh"].replace("臺", "台"), t["zh"].replace("台", "臺")]
        tname_re = "(?:%s)" % "|".join(re.escape(v) for v in set(tname_variants) if v)
        dval = int(round(t["deferred"]))
        dnum_re = r"%s[,]?%s" % (str(dval // 1000), "%03d" % (dval % 1000))
        top_def_ok = bool(
            re.search(tname_re + r".{0,40}(?:最多|最高|第一|#1|top|" + dnum_re + r")",
                      c, re.I)
            or re.search(r"(?:最多|最高|第一|#1|top).{0,40}遞延.{0,20}" + tname_re, c, re.I)
            or re.search(tname_re + r".{0,40}" + dnum_re, c)
        )
    else:
        top_def_ok = False
    scores["top_deferred_county"] = 1.0 if top_def_ok else 0.0

    # 預估未來負債：須出現「預估／預測／未來」+「負債／曝險」語境，或乘法說明
    proj_ok = bool(
        re.search(r"(?:預估|預測|未來|推估).{0,12}(?:負債|曝險|成本|給付)", c)
        or re.search(r"(?:平均給付|平均).{0,12}(?:乘以|×|x|\*).{0,12}遞延", c, re.I)
        or re.search(r"遞延.{0,12}(?:乘以|×|x|\*).{0,12}(?:平均給付|平均)", c, re.I)
    )
    scores["projected_liability"] = 1.0 if proj_ok else 0.0

    # 全國摘要：在領取者總數、遞延總數、整體平均、給付總額中至少命中 3 項數值
    def has_int(value, slack_digits=True):
        v = int(round(value))
        hi = str(v // 1000)
        lo = "%03d" % (v % 1000)
        return bool(re.search(r"%s[,]?%s" % (hi, lo), c))

    nat_count = 0
    if has_int(tot_count):
        nat_count += 1
    if has_int(tot_deferred):
        nat_count += 1
    if has_int(overall_avg):
        nat_count += 1
    # 給付總額：以 billion 或前幾位數字命中
    amt_billions = tot_amount / 1e9
    if (re.search(r"3[.,]5\d*\s*billion", c, re.I)
            or re.search(r"35[\d,.]{0,3}\s*億", c)
            or has_int(tot_amount)):
        nat_count += 1
    scores["national_summary"] = (
        1.0 if nat_count >= 3 else (0.5 if nat_count >= 2 else 0.0)
    )

    # 總預估未來負債（動態，約 NT$2.14B）：命中 billion 表述、約 21.4 億、或整數金額
    tp_billions = total_projected / 1e9
    tp_int = int(round(total_projected))
    tp_ok = bool(
        re.search(r"2[.,]1\d*\s*billion", c, re.I)
        or re.search(r"21[.,]?\d?\s*億", c)
        or re.search(r"2[,]?1\d\d[,]?\d{3}[,]?\d{3}", c)
        or re.search(r"%s[,]?%s" % (str(tp_int // 1000000), "%06d" % (tp_int % 1000000)), c)
    )
    # 也接受報告寫整體平均(約6,453)乘遞延(332,084)約2.14B的口語近似
    if not tp_ok and re.search(r"(?:總|全國).{0,10}(?:預估|未來).{0,10}負債", c):
        if re.search(r"2[.,]1", c) or re.search(r"21[.,]?\d?\s*億", c):
            tp_ok = True
    scores["total_projected"] = 1.0 if tp_ok else 0.0

    # 財務曝險分析：須有「曝險／風險／負債／財務」其一，且有實質分析語境
    ana = 0
    if re.search(r"曝險|風險|負債|財務|obligation|exposure|risk", c, re.I):
        ana += 1
    if re.search(r"(?:龐大|顯著|可觀|集中|最大).{0,12}(?:遞延|未來|負債|曝險)", c):
        ana += 1
    if re.search(r"六都|人口|公務|人力|離島|平均給付.{0,20}(?:不同|差異|並不相同)", c):
        ana += 1
    scores["exposure_analysis"] = (
        1.0 if ana >= 2 else (0.5 if ana >= 1 else 0.0)
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
