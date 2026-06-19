"""Grader for T004tw_todo_list_cleanup (Taiwan-localized from PinchBench `task_todo_list_cleanup`).

Phase 2 source: tasks_zh/task_todo_list_cleanup.md
Original file: tasks/task_todo_list_cleanup.md
grading_type: automated

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """待辦清單整理 grader（繁中台灣職場待辦）。

    設計重點：
      - 重複配對與逾期清單一律「從工作區的 todos.json 動態推導」，不硬寫英文原版事實。
        這樣即使日後微調 fixture（標題／日期／重複組），grader 仍能自動跟著對。
      - 比對 agent 產生的 todos_cleaned.json（中文標題、依專案分組）。
      - 僅用標準函式庫。

    重複偵測：中文同義改寫的字面字元重疊低，純字元相似度不可靠。改以「概念錨點」
    推導：每一組重複配對在同一 project 底下，共享一個具辨識度的概念關鍵字（即使標題
    被改寫，只要錨點還在就抓得到）。錨點清單對應 fixture 的四組重複：
      - backend／「單元測試」（id 1 與 4）
      - docs／「README」（id 2 與 7）
      - frontend／「登入」（id 3 與 10）
      - devops／CI（「CI/CD」或「持續整合」）（id 8 與 13）
    每組保留 id 最小者，其餘標記為應 completed。逾期清單則由日期動態比對得出。
    若 fixture 結構大改、動態偵測抓不到任何重複組，才退回已知的 {4,7,10,13}。
    """
    import json
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    keys = [
        "file_created",
        "all_items_present",
        "duplicates_marked_partial",
        "duplicates_marked_all",
        "no_false_completions",
        "overdue_flagged",
        "overdue_not_over_flagged",
        "organized_by_project",
    ]

    output_file = workspace / "todos_cleaned.json"
    if not output_file.exists():
        return {k: 0.0 for k in keys}

    scores = {"file_created": 1.0}

    try:
        data = json.loads(output_file.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {k: (1.0 if k == "file_created" else 0.0) for k in keys}

    # ---- 從 todos.json 動態推導正解 ----
    src_path = workspace / "todos.json"
    src_todos = []
    ref_date = "2026-04-10"
    if src_path.exists():
        try:
            src = json.loads(src_path.read_text(encoding="utf-8"))
            src_todos = src.get("todos", []) if isinstance(src, dict) else []
            ref_date = src.get("reference_date", ref_date) if isinstance(src, dict) else ref_date
        except Exception:  # noqa: BLE001
            src_todos = []

    by_id = {}
    for it in src_todos:
        if isinstance(it, dict) and "id" in it:
            by_id[it["id"]] = it

    # 概念錨點：(project, 命中函式)。同一 project 底下命中同一錨點的項目視為一組重複。
    # 錨點直接讀標題判斷，因此標題即使被改寫，只要保有錨點概念仍抓得到。
    def _has(title, *needles):
        return any(n in title for n in needles)

    anchors = [
        ("backend", lambda s: _has(s, "單元測試")),
        ("docs", lambda s: _has(s, "README")),
        ("frontend", lambda s: _has(s, "登入")),
        ("devops", lambda s: _has(s, "CI/CD", "持續整合")),
    ]

    dup_ids = set()          # 應被標記 completed 的 id（每組除 id 最小者外）
    for proj, hit in anchors:
        members = sorted(
            tid for tid, it in by_id.items()
            if it.get("project") == proj and hit(it.get("title", ""))
        )
        if len(members) >= 2:
            for d in members[1:]:
                dup_ids.add(d)

    # 後援：若 fixture 大改、動態偵測抓不到任何重複組，退回 fixture 已知的重複組。
    if not dup_ids:
        dup_ids = {4, 7, 10, 13}
    # 每組保留者（id 最小）＋ 所有非重複項，皆應維持非 completed。
    canonical_ids = set(by_id) - dup_ids

    # 逾期應旗標者：pending 且 due_date < ref_date 且不是重複組（重複組會被標 completed）
    expected_overdue = set()
    should_not_overdue = set()
    for tid, it in by_id.items():
        due = it.get("due_date", "")
        is_dup = tid in dup_ids
        if (not is_dup) and due and due < ref_date:
            expected_overdue.add(tid)
        else:
            should_not_overdue.add(tid)

    total_items = len(by_id) if by_id else 15

    # ---- 蒐集輸出項目 ----
    all_items = []
    if isinstance(data, dict) and "projects" in data:
        scores["organized_by_project"] = 1.0
        for _proj, items in data["projects"].items():
            if isinstance(items, list):
                all_items.extend(items)
    elif isinstance(data, dict) and "todos" in data:
        scores["organized_by_project"] = 0.0
        all_items = data["todos"] if isinstance(data["todos"], list) else []
    elif isinstance(data, list):
        scores["organized_by_project"] = 0.0
        all_items = data
    else:
        scores["organized_by_project"] = 0.0

    item_ids = set()
    items_by_id = {}
    for item in all_items:
        if isinstance(item, dict) and "id" in item:
            item_ids.add(item["id"])
            items_by_id[item["id"]] = item

    n = len(item_ids)
    if n >= total_items:
        scores["all_items_present"] = 1.0
    elif n >= total_items - 2:
        scores["all_items_present"] = 0.75
    elif n >= total_items - 5:
        scores["all_items_present"] = 0.5
    elif n >= 5:
        scores["all_items_present"] = 0.25
    else:
        scores["all_items_present"] = 0.0

    # ---- 重複項目標記 ----
    dup_list = sorted(dup_ids)
    dups_done = sum(
        1 for d in dup_list
        if items_by_id.get(d, {}).get("status") == "completed"
    )
    ndup = len(dup_list) if dup_list else 1
    if dups_done >= max(ndup - 1, 1):
        scores["duplicates_marked_partial"] = 1.0
    elif dups_done >= max(ndup - 2, 1):
        scores["duplicates_marked_partial"] = 0.75
    elif dups_done >= 1:
        scores["duplicates_marked_partial"] = 0.5
    else:
        scores["duplicates_marked_partial"] = 0.0

    scores["duplicates_marked_all"] = 1.0 if dups_done == ndup else 0.0

    # ---- 沒有把非重複項誤標 completed ----
    false_completions = sum(
        1 for cid in canonical_ids
        if items_by_id.get(cid, {}).get("status") == "completed"
    )
    if false_completions == 0:
        scores["no_false_completions"] = 1.0
    elif false_completions <= 1:
        scores["no_false_completions"] = 0.5
    else:
        scores["no_false_completions"] = 0.0

    # ---- 逾期旗標 ----
    exp_over = sorted(expected_overdue)
    correctly_flagged = sum(
        1 for oid in exp_over
        if items_by_id.get(oid, {}).get("overdue") is True
    )
    need = len(exp_over)
    if need == 0:
        scores["overdue_flagged"] = 1.0
    else:
        frac = correctly_flagged / need
        if frac >= 0.875:
            scores["overdue_flagged"] = 1.0
        elif frac >= 0.625:
            scores["overdue_flagged"] = 0.75
        elif frac >= 0.375:
            scores["overdue_flagged"] = 0.5
        elif frac >= 0.125:
            scores["overdue_flagged"] = 0.25
        else:
            scores["overdue_flagged"] = 0.0

    # ---- 不該逾期者未被誤標 ----
    false_overdue = sum(
        1 for nid in should_not_overdue
        if items_by_id.get(nid, {}).get("overdue") is True
    )
    if false_overdue == 0:
        scores["overdue_not_over_flagged"] = 1.0
    elif false_overdue <= 1:
        scores["overdue_not_over_flagged"] = 0.5
    else:
        scores["overdue_not_over_flagged"] = 0.0

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
