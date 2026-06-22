"""Grader for T112tw_meeting_council_upcoming (Taiwan-localized from PinchBench `task_meeting_council_upcoming`).

Phase 2 source: tasks_zh/task_meeting_council_upcoming.md
Original file: tasks/task_meeting_council_upcoming.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """TW (fictional) council upcoming-events grader.

    查核項依台灣逐字稿（dest=transcript.md）推導之事實比對，
    再比對 agent 產生的中文報告 upcoming_events.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 找出 agent 報告檔 ---
    report = workspace / "upcoming_events.md"
    if not report.exists():
        for alt in ["events.md", "deadlines.md", "upcoming.md", "timeline.md",
                    "後續事件.md", "後續議程.md", "重要日期.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["report_created", "april_16_items", "april_20_townhall",
            "may_7_ethics", "fire_station_gmp", "budget_workshops",
            "march_2027_fees", "rome_yard_sept2028", "chronological",
            "highlights_section"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態確認「應有事實」確實存在於 transcript（避免硬寫）---
    tx = ""
    tpath = workspace / "transcript.md"
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    def tx_has(*pats):
        # 逐字稿須含全部 pattern，才視為該事實可查核
        return all(re.search(p, tx) for p in pats) if tx else True

    # 1) 4 月 16 日次會：退輔委員會／第 26-28 案／NT$65 萬和解金
    fact = tx_has(r"4\s*月\s*16\s*日")
    ok = bool(re.search(r"4\s*月\s*16\s*日|0?4[/-]16|April\s*16", c)) and bool(
        re.search(r"退輔|退伍軍人|二十[六七八]|26|27|28|65\s*萬|和解金|重新分配", c))
    scores["april_16_items"] = 1.0 if (fact and ok) else 0.0

    # 2) 4 月 20 日：東港里里民座談會／福橡活動中心
    fact = tx_has(r"4\s*月\s*20\s*日", r"東港里", r"福橡")
    ok = bool(re.search(r"4\s*月\s*20\s*日|0?4[/-]20|April\s*20", c)) and bool(
        re.search(r"東港里|里民座談|座談會|Town\s*Hall|福橡", c))
    scores["april_20_townhall"] = 1.0 if (fact and ok) else 0.0

    # 3) 5 月 7 日：倫理自律報告／土管自治條例
    fact = tx_has(r"5\s*月\s*7\s*日", r"倫理")
    ok = bool(re.search(r"5\s*月\s*7\s*日|0?5[/-]7|May\s*7", c)) and bool(
        re.search(r"倫理|利益衝突|自律報告|土管|土地使用管理|LDC", c))
    scores["may_7_ethics"] = 1.0 if (fact and ok) else 0.0

    # 4) 5 月 15 日：第 24 號消防分隊 GMP
    fact = tx_has(r"5\s*月\s*15\s*日", r"24\s*號\s*消防")
    ok = bool(re.search(r"5\s*月\s*15\s*日|0?5[/-]15|May\s*15|GMP|工程上限價", c)) and bool(
        re.search(r"消防分隊|24\s*號消防|第\s*24\s*號|Fire\s*Station|Station\s*24", c))
    scores["fire_station_gmp"] = 1.0 if (fact and ok) else 0.0

    # 5) 8 月三場預算編列工作坊
    fact = tx_has(r"8\s*月\s*3\s*日")
    ok = bool(re.search(r"8\s*月\s*(?:3|10|17)\s*日|0?8[/-](?:3|10|17)|August\s*(?:3|10|17)", c)) and bool(
        re.search(r"預算|工作坊|workshop", c, re.IGNORECASE))
    scores["budget_workshops"] = 1.0 if (fact and ok) else 0.0

    # 6) 2027 年 3 月 1 日：容量費新費率上路
    fact = tx_has(r"2027\s*年\s*3\s*月")
    ok = bool(re.search(r"2027\s*年\s*3\s*月|2027[/-]0?3|March.*2027", c)) and bool(
        re.search(r"容量費|容量接管費|費率|自來水|污水|capacity|fee", c, re.IGNORECASE))
    scores["march_2027_fees"] = 1.0 if (fact and ok) else 0.0

    # 7) 2028 年 9 月：中崙倉庫園區第四期完工
    fact = tx_has(r"2028\s*年\s*9\s*月", r"中崙倉庫")
    ok = bool(re.search(r"2028\s*年\s*9\s*月|2028[/-]0?9|(?:September|Sept).*28", c)) and bool(
        re.search(r"中崙倉庫|園區|第四期|Phase\s*4|完工|completion", c, re.IGNORECASE))
    scores["rome_yard_sept2028"] = 1.0 if (fact and ok) else 0.0

    # 8) 依時間先後（至少出現 4 個不同月份／日期錨點）
    anchors = re.findall(
        r"(?:4\s*月\s*16|4\s*月\s*20|5\s*月\s*7|5\s*月\s*15|8\s*月\s*3|8\s*月\s*10|8\s*月\s*17|2027|2028|2030)",
        c)
    scores["chronological"] = 1.0 if len(set(anchors)) >= 4 else 0.0

    # 9) 重點／值得關注區段
    scores["highlights_section"] = 1.0 if re.search(
        r"值得關注|重點|關注重點|What\s*to\s*watch|提醒|留意|focus|watch|highlight",
        c, re.IGNORECASE) else 0.0

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
