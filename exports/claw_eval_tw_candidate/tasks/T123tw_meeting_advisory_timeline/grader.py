"""Grader for T123tw_meeting_advisory_timeline (Taiwan-localized from PinchBench `task_meeting_advisory_timeline`).

Phase 2 source: tasks_zh/task_meeting_advisory_timeline.md
Original file: tasks/task_meeting_advisory_timeline.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """TW (fictional) advisory-committee timeline grader.

    查核項（presidential_memo / october_report / next_meeting /
    september_target / january_target / ten_year_transition / isart_meeting /
    chronological_order），但事實改由台灣逐字稿（dest=meeting-transcript.md）動態
    推導，再比對 agent 產生的中文報告 timeline.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 找出 agent 報告檔（容許常見替代檔名）---
    report = workspace / "timeline.md"
    if not report.exists():
        for alt in ["timeline_report.md", "deadlines.md", "milestones.md",
                    "schedule.md", "時間軸.md", "時程.md", "期限.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["report_created", "presidential_memo", "october_report",
            "next_meeting", "september_target", "january_target",
            "ten_year_transition", "isart_meeting", "chronological_order"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態確認「應有事實」確實存在（避免硬寫；逐字稿缺失則不卡關）---
    tx = ""
    tpath = workspace / "meeting-transcript.md"
    if not tpath.exists():
        for alt in ["transcript.md", "meeting_transcript.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    def tx_has(*pats):
        # 逐字稿須含全部 pattern，才視為該事實可查核；無逐字稿時不阻擋
        return all(re.search(p, tx) for p in pats) if tx else True

    # 1) 六月備忘錄：2023 年 6 月，總統府／行政院備忘錄，500 MHz 十年目標
    fact = tx_has(r"2023\s*年\s*6\s*月", r"備忘錄", r"500\s*MHz")
    ok = bool(re.search(r"2023\s*年\s*6\s*月|2023[/\-]0?6|六月備忘錄", c)) and bool(
        re.search(r"備忘錄|總統府|行政院|memo|500\s*MHz|五百兆赫", c, re.IGNORECASE))
    scores["presidential_memo"] = 1.0 if (fact and ok) else 0.0

    # 2) 十月一日報告：2024 年 10 月 1 日法定期限（1755-1850 評估報告）
    fact = tx_has(r"2024\s*年\s*10\s*月\s*1\s*日")
    ok = bool(re.search(r"2024\s*年\s*10\s*月\s*1\s*日|2024[/\-]10[/\-]0?1|十月一日|10\s*月\s*1\s*日",
                        c)) and bool(
        re.search(r"報告|期限|deadline|惡名昭彰|十月一日|1755", c, re.IGNORECASE))
    scores["october_report"] = 1.0 if (fact and ok) else 0.0

    # 3) 下次會議：2025 年 7 月 24 日，台中
    fact = tx_has(r"7\s*月\s*24\s*日", r"台中")
    ok = bool(re.search(r"7\s*月\s*24\s*日|2025[/\-]0?7[/\-]24|July\s*24", c)) and bool(
        re.search(r"台中|下次會議|下次本委員會|next\s*meeting", c, re.IGNORECASE))
    scores["next_meeting"] = 1.0 if (fact and ok) else 0.0

    # 4) WG1 氣象衛星（1695-1710）目標 2025 年 9 月完成
    fact = tx_has(r"2025\s*年\s*9\s*月")
    ok = bool(re.search(r"2025\s*年\s*9\s*月|2025[/\-]0?9|9\s*月.*(?:完成|目標)|September",
                        c, re.IGNORECASE)) and bool(
        re.search(r"氣象衛星|氣象|1695|WG\s*1|WG1|第\s*1\s*工作小組|工作小組\s*1", c, re.IGNORECASE))
    scores["september_target"] = 1.0 if (fact and ok) else 0.0

    # 5) WG2~WG5（1755-1850）目標 2026 年 1 月完成
    fact = tx_has(r"2026\s*年\s*1\s*月")
    ok = bool(re.search(r"2026\s*年\s*1\s*月|2026[/\-]0?1|明年\s*1\s*月|January",
                        c, re.IGNORECASE)) and bool(
        re.search(r"WG\s*[2-5]|WG[2-5]|工作小組|1755|完成|target", c, re.IGNORECASE))
    scores["january_target"] = 1.0 if (fact and ok) else 0.0

    # 6) 十年過渡期：全面遷出本頻段
    fact = tx_has(r"十年", r"過渡")
    ok = bool(re.search(r"十年|10\s*年|10[\-\s]?year", c, re.IGNORECASE)) and bool(
        re.search(r"過渡|遷出|遷移|轉換|搬遷|relocat|transition", c, re.IGNORECASE))
    scores["ten_year_transition"] = 1.0 if (fact and ok) else 0.0

    # 7) ISART 研討會：7 月 25-26 日，於電信技術研究所（ITS）
    fact = tx_has(r"ISART")
    ok = bool(re.search(r"ISART", c, re.IGNORECASE)) and bool(
        re.search(r"7\s*月\s*25|25\s*(?:日|至|到|[\-~])\s*26|研討會|ITS|電信技術|頻譜共用|spectrum\s*sharing",
                  c, re.IGNORECASE))
    scores["isart_meeting"] = 1.0 if (fact and ok) else 0.0

    # 8) 依時間先後組織：年份大致遞增，或出現足夠多不同年份／日期錨點
    years = [int(m.group()) for m in re.finditer(r"20[12]\d", c)]
    if len(years) >= 3:
        ordered = sum(1 for i in range(len(years) - 1) if years[i] <= years[i + 1])
        ratio = ordered / (len(years) - 1)
        scores["chronological_order"] = 1.0 if ratio >= 0.6 else (0.5 if ratio >= 0.4 else 0.0)
    else:
        anchors = re.findall(
            r"(?:2023|2024|2025|2026|7\s*月\s*24|7\s*月\s*25|9\s*月|10\s*月\s*1|1\s*月|十年)", c)
        scores["chronological_order"] = (
            1.0 if len(set(anchors)) >= 4 else (0.5 if re.search(r"\d{4}", c) else 0.0))

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
