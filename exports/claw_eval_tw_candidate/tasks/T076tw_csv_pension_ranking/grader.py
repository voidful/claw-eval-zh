"""Grader for T076tw_csv_pension_ranking (Taiwan-localized from PinchBench `task_csv_pension_ranking`).

Phase 2 source: tasks_zh/task_csv_pension_ranking.md
Original file: tasks/task_csv_pension_ranking.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣各縣市公教退休給付排名 grader。

    應有事實「從 tw_pension.csv（佈署的台灣 CSV）動態實算」——聚合縣市總計、
    依金額與人數排序、篩選後段，再比對 agent 產生的中文報告
    pension_ranking_report.md。僅用標準函式庫，不沿用任何美國數值。
    """
    from pathlib import Path
    import csv
    import re

    keys = [
        "report_created", "top_10_listed", "rank1_taichung",
        "rank2_newtaipei", "rank3_kaohsiung", "bottom_states",
        "grand_total", "payee_count_ranking", "geographic_analysis",
    ]
    workspace = Path(workspace_path)

    # --- 找報告檔 ---
    report_path = workspace / "pension_ranking_report.md"
    if not report_path.exists():
        for alt in ["ranking_report.md", "report.md", "pension_report.md",
                    "pension_ranking.md", "退休給付報告.md", "排名報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    # --- 從 CSV 動態實算正解 ---
    csv_path = workspace / "tw_pension.csv"

    def to_int(s):
        d = re.sub(r"[^\d]", "", s or "")
        return int(d) if d else 0

    grand = None
    totals = []  # [(縣市名, 金額, 領取人數, 遞延人數)]
    if csv_path.exists():
        with csv_path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                name = (row.get("STATE_ABBREV_NAME") or "").strip()
                amt = to_int(row.get("PAYEE_AMOUNT"))
                pc = to_int(row.get("PAYEE_COUNT"))
                dc = to_int(row.get("DEFERRED_COUNT"))
                if name == "Grand Total":
                    grand = (amt, pc, dc)
                elif name.endswith("Total"):
                    # 去掉「簡碼-縣市名」中的簡碼與末尾 Total，只留中文縣市/機關名
                    label = name[: -len("Total")].strip()
                    if "-" in label:
                        label = label.split("-", 1)[1].strip()
                    totals.append((label, amt, pc, dc))

    by_amt = sorted(totals, key=lambda t: t[1], reverse=True)
    by_amt_asc = sorted([t for t in totals if t[1] > 0], key=lambda t: t[1])
    by_pc = sorted(totals, key=lambda t: t[2], reverse=True)

    # --- 讀報告，準備數字比對（去千分位逗號與空白）---
    c = report_path.read_text(encoding="utf-8", errors="ignore")
    nospace = re.sub(r"[\s,]", "", c)

    def has_name(name):
        return bool(name) and name in c

    def has_amount(amt):
        # 接受 561,035,674 / 561035674 / 5.61 億 等寫法皆視為命中（以無逗號全額為準）
        return amt > 0 and str(amt) in nospace

    scores = {"report_created": 1.0}

    # 前 10 大（金額）：實算前 10 名縣市名至少出現 8 個
    top10_names = [t[0] for t in by_amt[:10]]
    mentioned = sum(1 for n in top10_names if has_name(n))
    scores["top_10_listed"] = (
        1.0 if mentioned >= 8 else (0.5 if mentioned >= 5 else 0.0)
    )

    # 第 1 名（金額）：名稱 + 金額皆需命中
    if by_amt:
        n1, a1 = by_amt[0][0], by_amt[0][1]
        scores["rank1_taichung"] = (
            1.0 if (has_name(n1) and has_amount(a1)) else 0.0
        )
    else:
        scores["rank1_taichung"] = 0.0

    # 第 2 名（金額）
    if len(by_amt) >= 2:
        n2, a2 = by_amt[1][0], by_amt[1][1]
        scores["rank2_newtaipei"] = (
            1.0 if (has_name(n2) and has_amount(a2)) else 0.0
        )
    else:
        scores["rank2_newtaipei"] = 0.0

    # 第 3 名（金額）
    if len(by_amt) >= 3:
        n3, a3 = by_amt[2][0], by_amt[2][1]
        scores["rank3_kaohsiung"] = (
            1.0 if (has_name(n3) and has_amount(a3)) else 0.0
        )
    else:
        scores["rank3_kaohsiung"] = 0.0

    # 後 5 名（金額非零，由小到大）：實算後 5 名至少提及 3 個
    bottom5 = [t[0] for t in by_amt_asc[:5]]
    bottom_hit = sum(1 for n in bottom5 if has_name(n))
    scores["bottom_states"] = (
        1.0 if bottom_hit >= 3 else (0.5 if bottom_hit >= 2 else 0.0)
    )

    # Grand Total：總金額／總領取人數／總遞延人數三項命中其二即滿分
    if grand:
        g_amt, g_pc, g_dc = grand
        g_hits = sum(
            1 for v in (g_amt, g_pc, g_dc) if v > 0 and str(v) in nospace
        )
        scores["grand_total"] = (
            1.0 if g_hits >= 2 else (0.5 if g_hits >= 1 else 0.0)
        )
    else:
        scores["grand_total"] = 0.0

    # 領取人數排名：前 2 名（依人數）之名稱 + 人數命中其一即可，另接受出現「領取人數」段落
    pc_hit = False
    for nm, _amt, pc, _dc in by_pc[:2]:
        if has_name(nm) and pc > 0 and str(pc) in nospace:
            pc_hit = True
            break
    if pc_hit:
        scores["payee_count_ranking"] = 1.0
    elif re.search(r"(領取(者)?人數|領取人口|現職領取)", c):
        scores["payee_count_ranking"] = 0.5
    else:
        scores["payee_count_ranking"] = 0.0

    # 地理／人口分析：命中關鍵分析詞彙的數量
    geo_patterns = [
        r"(六都|都會區|直轄市|人口規模|人口數)",
        r"(地理|區域|分布|集中|模式|趨勢)",
        r"(公教|退休人口|軍公教|公務人力)",
        r"(離島|偏鄉|北部|中部|南部|東部)",
    ]
    geo_count = sum(1 for p in geo_patterns if re.search(p, c))
    scores["geographic_analysis"] = (
        1.0 if geo_count >= 2 else (0.5 if geo_count >= 1 else 0.0)
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
