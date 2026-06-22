"""Grader for T111tw_meeting_council_budget (Taiwan-localized from PinchBench `task_meeting_council_budget`).

Phase 2 source: tasks_zh/task_meeting_council_budget.md
Original file: tasks/task_meeting_council_budget.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """南港市議會預算報告 grader。

    應有事實「從 transcript.md（佈署的台灣逐字稿）動態推導」，再比對 agent 產生
    的中文報告 budget_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    keys = [
        "report_created", "capacity_fee_amounts", "three_billion",
        "annual_revenue_increase", "zhonglun_yard_94m", "annex_34m",
        "phase1_7m", "gas_settlement_650k", "yizhong_8m", "financial_summary",
    ]
    workspace = Path(workspace_path)

    # --- 找報告檔 ---
    report_path = workspace / "budget_report.md"
    if not report_path.exists():
        for alt in ["budget.md", "financial_report.md", "finances.md",
                    "預算報告.md", "財務報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    # --- 讀逐字稿，動態推導應有金額 ---
    tpath = workspace / "transcript.md"
    tx = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def digits(s):
        """只保留數字，方便比對 1,020 / 1020 / NT$1,020 等寫法。"""
        return re.sub(r"\D", "", s)

    # 從逐字稿抓出關鍵金額（抓不到時退回已知預設值，避免逐字稿格式變動就壞掉）
    def find_amount(pattern, default):
        m = re.search(pattern, tx)
        return digits(m.group(1)) if m else default

    water_now = find_amount(r"自來水\s*\*{0,2}NT\$?([\d,]+)", "1020")    # 1020
    sewer_now = find_amount(r"污水\s*\*{0,2}NT\$?([\d,]+)", "1237")      # 1237
    water_new = find_amount(r"調整為\s*自來水\s*\*{0,2}NT\$?([\d,]+)", "1530")  # 1530
    sewer_new = "1847"  # 提議之污水費率（逐字稿第二筆污水數字）
    three_b = find_amount(r"NT\$?([\d,]+)，3 billion", "3000000000")    # 30 億
    zhonglun = find_amount(r"中崙倉庫園區.{0,40}?NT\$?([\d,]+)，94 million", "94000000")
    annex = find_amount(r"行政園區增建案.{0,20}?NT\$?([\d,]+)，34", "34200000")
    phase1 = find_amount(r"第一期已支用約\s*\*{0,2}NT\$?([\d,]+)", "7000000")
    gas = find_amount(r"和解金\s*新臺幣[^（]*（NT\$?([\d,]+)", "650000")  # 650000
    yizhong = find_amount(r"請求編列\s*\*{0,2}NT\$?([\d,]+)\s*萬", "8000")   # 8000(萬)

    # --- 讀報告並去除空白，便於數字比對 ---
    raw = report_path.read_text(encoding="utf-8", errors="ignore")
    c = raw  # 原文（保留漢字）
    nospace = re.sub(r"[\s,]", "", raw)  # 去空白與千分位逗號

    def has_num(*nums):
        return all(n and n in nospace for n in nums)

    scores = {"report_created": 1.0}

    # 容量費：現行(自來水/污水) 與 提議(自來水/污水) 至少各出現一組
    now_ok = has_num(water_now) and has_num(sewer_now)
    new_ok = has_num(water_new) and has_num(sewer_new)
    scores["capacity_fee_amounts"] = 1.0 if (now_ok and new_ok) else 0.0

    # 30 億資本投資：接受「30億」「3,000,000,000」「3 billion」等寫法
    scores["three_billion"] = 1.0 if (
        re.search(r"30\s*億", c) or has_num(three_b) or re.search(r"3\s*billion", c.lower())
    ) else 0.0

    # 每年增加約 1,500 萬至 2,000 萬元收入
    rev_amt = (re.search(r"1[,，]?500\s*萬", c) or re.search(r"1500萬", nospace)
               or "15000000" in nospace)
    rev_ctx = re.search(r"(收入|增加|每年|額外|挹注)", c)
    scores["annual_revenue_increase"] = 1.0 if (rev_amt and rev_ctx) else 0.0

    # 中崙倉庫園區 9,400 萬元（NT$94,000,000）
    zhonglun_amt = (re.search(r"9[,，]?400\s*萬", c) or has_num(zhonglun)
                or re.search(r"94\s*million", c.lower()))
    zhonglun_ctx = re.search(r"中崙倉庫", c)
    scores["zhonglun_yard_94m"] = 1.0 if (zhonglun_amt and zhonglun_ctx) else 0.0

    # 行政園區增建 3,420 萬元（NT$34,200,000）
    annex_amt = (re.search(r"3[,，]?420\s*萬", c) or has_num(annex)
                 or re.search(r"34\.?2?\s*million", c.lower()))
    annex_ctx = re.search(r"(行政園區增建|南港大道.{0,6}增建)", c)
    scores["annex_34m"] = 1.0 if (annex_amt and annex_ctx) else 0.0

    # 第一期已支出 NT$700 萬元（NT$7,000,000）
    phase_amt = (re.search(r"700\s*萬", c) or has_num(phase1)
                 or re.search(r"7\s*million", c.lower()))
    phase_ctx = re.search(r"(第一期|已支用|已支出|Phase\s*1)", c)
    scores["phase1_7m"] = 1.0 if (phase_amt and phase_ctx) else 0.0

    # 天然氣和解金 NT$65 萬元（NT$650,000）
    gas_amt = (re.search(r"65\s*萬", c) or has_num(gas)
               or re.search(r"650[,.]?000", c))
    gas_ctx = re.search(r"(和解金|天然氣|管線損鄰)", c)
    scores["gas_settlement_650k"] = 1.0 if (gas_amt and gas_ctx) else 0.0

    # 義塚紀念館請求 NT$8,000 萬元（NT$80,000,000）；yizhong 為逐字稿推導之「萬元」數字
    # （例 "8000"）；接受 8,000 萬 / 80,000,000 / 8 million 等寫法
    yizhong_amount = ((yizhong + "萬") in nospace or (yizhong + "0000") in nospace
                   or "80000000" in nospace or re.search(r"8\s*million", c.lower()))
    yizhong_ctx = re.search(r"(義塚|紀念館)", c)
    scores["yizhong_8m"] = 1.0 if (yizhong_amount and yizhong_ctx) else 0.0

    # 財務彙總（財務摘要）
    scores["financial_summary"] = 1.0 if re.search(
        r"(財務|預算)\s*(彙總|摘要|概要|總覽|總結)|財務概要", c
    ) else 0.0

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
