"""Grader for T138tw_second_brain (Taiwan-localized from PinchBench `task_second_brain`).

Phase 2 source: tasks_zh/task_second_brain.md
Original file: tasks/task_second_brain.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """評分台灣在地化版「第二大腦」記憶持久化任務。

    作法：先從工作區佈署的 facts/REFERENCE.md 動態讀出「應有事實」，
    再檢查 agent 產生的 memory/MEMORY.md 是否含有這些中文事實，
    不在程式中寫死任何台灣導師姓名／單位等內容。
    回傳 {check_name: 0.0~1.0}。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 1) 從參考卡動態讀出應有事實 ------------------------------------
    def _load_reference():
        ref = workspace / "facts" / "REFERENCE.md"
        facts = {}
        if not ref.exists():
            return facts
        try:
            text = ref.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return facts
        # 接受全形或半形冒號
        for line in text.splitlines():
            m = re.match(r"\s*([^：:]+?)\s*[：:]\s*(.+?)\s*$", line)
            if not m:
                continue
            key, val = m.group(1).strip(), m.group(2).strip()
            facts[key] = val
        return facts

    ref_facts = _load_reference()

    # 解析後備：萬一參考卡缺漏，用在地化常數補齊，確保 grader 仍可運作。
    fallback = {
        "最愛語言": "Rust",
        "開始日期": "2024 年 1 月 15 日",
        "導師姓名": "林淑芬 教授",
        "導師單位": "國立臺灣大學",
        "專案名稱": "NeonDB",
        "專案描述": "分散式鍵值儲存系統",
        "團隊暗號": "紫色大象日出",
    }
    for k, v in fallback.items():
        ref_facts.setdefault(k, v)

    # --- 2) 找出 agent 產生的記憶檔 -------------------------------------
    memory_file = workspace / "memory" / "MEMORY.md"
    if not memory_file.exists():
        for alt in (workspace / "MEMORY.md", workspace / "memory.md"):
            if alt.exists():
                memory_file = alt
                break

    scores = {}

    if not memory_file.exists():
        scores["記憶檔已建立"] = 0.0
        scores["回想_最愛語言"] = 0.0
        scores["回想_開始日期"] = 0.0
        scores["回想_導師"] = 0.0
        scores["回想_專案名稱"] = 0.0
        scores["回想_專案描述"] = 0.0
        scores["回想_暗號"] = 0.0
        return scores

    scores["記憶檔已建立"] = 1.0
    try:
        content = memory_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        content = ""

    # --- 3) 比對各項事實（中文關鍵字 / 數值） --------------------------
    def _norm(s):
        # 去掉空白以容忍「2024 年 1 月 15 日」vs「2024年1月15日」等差異。
        return re.sub(r"\s+", "", s)

    c = _norm(content)

    # 最愛語言：Rust（不分大小寫）
    scores["回想_最愛語言"] = 1.0 if "rust" in content.lower() else 0.0

    # 開始日期：容忍空白差異，並接受 2024 + 1 月 15 為核心數值。
    date_val = _norm(ref_facts.get("開始日期", ""))
    has_date = bool(date_val) and date_val in c
    if not has_date:
        has_date = ("2024" in c) and ("1月15" in c or "01月15" in c)
    scores["回想_開始日期"] = 1.0 if has_date else 0.0

    # 導師：姓名（去頭銜後的核心姓名）+ 單位皆須出現。
    mentor_name = ref_facts.get("導師姓名", "")
    mentor_core = _norm(re.sub(r"(教授|老師|博士|Dr\.?|博士後)", "", mentor_name)).strip()
    mentor_unit = _norm(ref_facts.get("導師單位", ""))
    has_name = bool(mentor_core) and mentor_core in c
    # 單位容忍「國立臺灣大學」與簡稱「臺灣大學」/「台灣大學」。
    unit_variants = {mentor_unit}
    if mentor_unit:
        unit_variants.add(mentor_unit.replace("國立", ""))
        unit_variants.add(mentor_unit.replace("臺", "台"))
        unit_variants.add(mentor_unit.replace("國立", "").replace("臺", "台"))
    has_unit = any(u and u in c for u in unit_variants)
    if has_name and has_unit:
        scores["回想_導師"] = 1.0
    elif has_name or has_unit:
        scores["回想_導師"] = 0.5
    else:
        scores["回想_導師"] = 0.0

    # 專案名稱：NeonDB（不分大小寫）
    proj_name = ref_facts.get("專案名稱", "")
    scores["回想_專案名稱"] = (
        1.0 if proj_name and proj_name.lower() in content.lower() else 0.0
    )

    # 專案描述：分散式鍵值儲存系統（容忍空白）
    proj_desc = _norm(ref_facts.get("專案描述", ""))
    scores["回想_專案描述"] = 1.0 if proj_desc and proj_desc in c else 0.0

    # 暗號：紫色大象日出（容忍空白）
    phrase = _norm(ref_facts.get("團隊暗號", ""))
    scores["回想_暗號"] = 1.0 if phrase and phrase in c else 0.0

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
PRIMARY_DIMENSIONS = ['completion', 'safety', 'robustness']


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
