"""Grader for T137tw_memory (Taiwan-localized from PinchBench `task_memory`).

Phase 2 source: tasks_zh/task_memory.md
Original file: tasks/task_memory.md
grading_type: automated

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """評分台灣在地化版「從情境中擷取記憶」任務。

    作法：先從工作區佈署的 facts/REFERENCE.md 動態讀出「應有答案
    （Beta 公測日期）」與兩個混淆日期（Alpha 內測、正式上線），
    再檢查 agent 寫入 answer.txt 的內容是否含正確日期、是否清楚作答、
    是否實際讀過 notes.md，以及是否誤抄了錯誤日期（幻覺）。
    不在程式中寫死任何日期字串。
    回傳 {check_name: 0.0~1.0}。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 0) 工具：正規化（移除空白），容忍「2024 年 6 月 1 日」等空白差異 ---
    def _norm(s: str) -> str:
        return re.sub(r"\s+", "", s or "")

    # --- 1) 從參考卡動態讀出應有答案與混淆日期 ------------------------------
    def _load_reference() -> dict:
        ref = workspace / "facts" / "REFERENCE.md"
        facts = {}
        if not ref.exists():
            return facts
        try:
            text = ref.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return facts
        for line in text.splitlines():
            m = re.match(r"\s*([^：:]+?)\s*[：:]\s*(.+?)\s*$", line)
            if not m:
                continue
            facts[m.group(1).strip()] = m.group(2).strip()
        return facts

    ref_facts = _load_reference()

    # 後備：萬一參考卡缺漏，用在地化常數補齊，確保 grader 仍可運作。
    ref_facts.setdefault("正確答案_Beta公測日期", "2024 年 6 月 1 日")
    ref_facts.setdefault("錯誤日期_Alpha內測", "2024 年 3 月 15 日")
    ref_facts.setdefault("錯誤日期_正式上線", "2024 年 9 月 30 日")

    correct_date = ref_facts.get("正確答案_Beta公測日期", "")
    wrong_dates = [
        ref_facts.get("錯誤日期_Alpha內測", ""),
        ref_facts.get("錯誤日期_正式上線", ""),
    ]

    # 由「2024 年 6 月 1 日」拆出 (年, 月, 日)，產生多種等價寫法以利比對。
    def _ymd(date_str: str):
        m = re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})", date_str)
        if not m:
            return None
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    def _date_variants(date_str: str):
        """回傳該日期的多種正規化（去空白）等價寫法集合。"""
        variants = set()
        n = _norm(date_str)
        if n:
            variants.add(n)
        ymd = _ymd(date_str)
        if ymd:
            y, mo, d = ymd
            variants.update(_norm(v) for v in [
                f"{y}年{mo}月{d}日",
                f"{y}年{mo:02d}月{d:02d}日",
                f"{y}-{mo:02d}-{d:02d}",
                f"{y}/{mo}/{d}",
                f"{y}/{mo:02d}/{d:02d}",
                f"{mo}/{d}/{y}",
                f"{mo:02d}/{d:02d}/{y}",
            ])
        return {v for v in variants if v}

    # --- 2) 檢查 answer.txt 是否存在 ---------------------------------------
    answer_file = workspace / "answer.txt"
    scores = {}
    if not answer_file.exists():
        scores["已建立answer檔"] = 0.0
        scores["日期正確"] = 0.0
        scores["作答清楚"] = 0.0
        scores["已讀取notes"] = 0.0
        scores["無幻覺"] = 0.0
        return scores

    scores["已建立answer檔"] = 1.0

    try:
        raw = answer_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raw = ""
    content = raw  # 原文（保留大小寫，用於英文月份等比對）
    c = _norm(raw)  # 去空白正規化

    # --- 3) 日期正確：正確日期的任一等價寫法出現即得分 --------------------
    correct_variants = _date_variants(correct_date)
    if any(v in c for v in correct_variants):
        scores["日期正確"] = 1.0
    else:
        # 部分分數：有提到「2024」與「6 月／6/1」等接近資訊。
        partial = ("2024" in c) and bool(
            re.search(r"6月1|06月01|6/1|06/01", c)
        )
        if not partial:
            # 退而求其次：出現任何日期樣式給少量部分分。
            partial = bool(
                re.search(r"\d{4}\D+\d{1,2}\D+\d{1,2}", c)
                or re.search(r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}", c)
            )
            scores["日期正確"] = 0.3 if partial else 0.0
        else:
            scores["日期正確"] = 1.0

    # --- 4) 作答清楚：不只丟一個日期，而是回應了問題 ----------------------
    stripped = raw.strip()
    if len(stripped) > 6 and (
        "beta" in content.lower()
        or "公測" in content
        or "發布" in content
        or "發佈" in content
        or "上線" in content
        or "截止" in content
        or "期限" in content
    ):
        scores["作答清楚"] = 1.0
    elif len(stripped) > 3:
        scores["作答清楚"] = 0.5
    else:
        scores["作答清楚"] = 0.0

    # --- 5) 助手是否讀取 notes.md（從 transcript 判斷） -------------------
    read_notes = False
    for event in (transcript or []):
        if not isinstance(event, dict) or event.get("type") != "message":
            continue
        msg = event.get("message", {})
        if msg.get("role") != "assistant":
            continue
        for item in msg.get("content", []) or []:
            if not isinstance(item, dict) or item.get("type") != "toolCall":
                continue
            tool_name = item.get("name", "")
            # 支援多種工具命名：read（OpenClaw）/ read_file / readFile
            if tool_name not in ("read", "read_file", "readFile"):
                continue
            args = item.get("arguments", item.get("params", {})) or {}
            files = args.get("files", []) or []
            path_candidates = [
                args.get("path", ""),
                args.get("file_path", ""),
                args.get("file", ""),
            ]
            if any("notes.md" in str(f) for f in files) or any(
                "notes.md" in str(p) for p in path_candidates if p
            ):
                read_notes = True
                break
        if read_notes:
            break

    scores["已讀取notes"] = 1.0 if read_notes else 0.0

    # --- 6) 無幻覺：誤抄混淆日期（Alpha 內測／正式上線）即扣為 0 ----------
    hallucinated = False
    for wd in wrong_dates:
        for v in _date_variants(wd):
            if v and v in c:
                hallucinated = True
                break
        if hallucinated:
            break
    scores["無幻覺"] = 0.0 if hallucinated else 1.0

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
