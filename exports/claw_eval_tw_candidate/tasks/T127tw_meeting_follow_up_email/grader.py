"""Grader for T127tw_meeting_follow_up_email (Taiwan-localized from PinchBench `task_meeting_follow_up_email`).

Phase 2 source: tasks_zh/task_meeting_follow_up_email.md
Original file: tasks/task_meeting_follow_up_email.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """鼎峰科技產品週會「會後追蹤郵件」grader。

    做法：先從台灣逐字稿 meeting_transcript.md「動態推導」出應有事實
    （被指派的負責人、活動名稱、選定的主標語、星期幾的期限），再比對 agent
    產出的中文追蹤郵件 follow_up_email.md。盡量不硬寫英文原版事實，提升可重現性。
    僅用標準函式庫。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 找 agent 報告（郵件）---
    report = workspace / "follow_up_email.md"
    if not report.exists():
        for alt in ["followup_email.md", "follow_up.md", "email.md",
                    "meeting_followup.md", "後續追蹤郵件.md", "追蹤郵件.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["file_created", "has_subject", "decisions_section",
            "decisions_count", "action_items_with_owners", "action_items_count",
            "deadline_mentioned", "tone_appropriate", "concise"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"file_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 讀逐字稿，動態推導「應有事實」---
    tpath = workspace / "meeting_transcript.md"
    tx = ""
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    han = re.compile(r"[一-鿿]{2,3}")

    # (a) 與會者姓名白名單（逐字稿「與會者」區塊：行首為 - 姓名（角色…）
    attendees = set(re.findall(r"[-\s]([一-鿿]{2,3})（", tx)) if tx else set()

    # (b) 真正在「**行動項目…**」句子裡被點名的負責人
    assigned = []
    for m in re.finditer(r"行動項目[（(]?[^）)]*[）)]?[：:]\s*([^\n*。]{0,40})", tx):
        for nm in han.findall(m.group(1)):
            if nm in attendees and nm not in assigned:
                assigned.append(nm)
    if not assigned and attendees:
        assigned = list(attendees)
    if not assigned:
        assigned = ["戴立安", "高敏哲", "蔡思敏", "王志明", "陳柏宇", "林淑芬"]

    # (c) 從逐字稿動態抓出三場活動名稱（查核決議用）
    event_terms = [t for t in ["COSCUP", "DevOpsDays", "Kubernetes Day"]
                   if (not tx or t in tx)]

    # (d) 選定的主標語（會議結尾複習句／「…當主標語」）
    tagline = ""
    mt = re.search(r"主標語[，、\s]*「([^」]{2,20})」", tx) if tx else None
    if not mt and tx:
        mt = re.search(r"「([^」]{2,20})」\s*當主標語", tx)
    tagline = mt.group(1) if mt else "更快交付，更低風險"

    # --- 計分 ---

    # 1) 主旨行
    subject_patterns = [r"主旨", r"subject\s*[:：]", r"^#\s",
                        r"\*\*主旨\*\*", r"re\s*[:：]"]
    scores["has_subject"] = 1.0 if any(
        re.search(p, c, re.MULTILINE | re.IGNORECASE)
        for p in subject_patterns) else 0.0

    # 2) 決議／關鍵結論區段
    decision_section = [r"決議", r"決定", r"結論", r"關鍵結論", r"做成的決議",
                        r"共識", r"decision"]
    scores["decisions_section"] = 1.0 if any(
        re.search(p, c, re.IGNORECASE) for p in decision_section) else 0.0

    # 3) 具體決議計數（盡量以逐字稿動態詞彙比對）
    decision_count = 0
    # 活動分工：抓到任一動態活動名稱，或泛指「平台/CI/CD/GitOps + 活動」
    if any(t in c for t in event_terms) or re.search(
            r"(?:平台|Platform).{0,12}(?:COSCUP|開源人)", c, re.IGNORECASE):
        decision_count += 1
    # 主標語
    if (tagline in c) or re.search(r"更快交付|更低風險", c):
        decision_count += 1
    # 資訊圖只用綠色
    if re.search(r"只用綠色|僅用綠色|綠色.{0,6}配色|不用紅色|不放紅色|配色", c):
        decision_count += 1
    # 漏洞管理（資安主打）
    if re.search(r"漏洞管理|vulnerability\s*management", c, re.IGNORECASE):
        decision_count += 1
    # 競品方法論：只比 tier 1 ／新增鼎峰一列 ／每個 stage 只放相關對手
    if re.search(r"tier\s*1|只.{0,4}相關.{0,4}對手|鼎峰一列|鼎峰.{0,4}列|"
                 r"每個\s*stage|每個分頁", c, re.IGNORECASE):
        decision_count += 1
    scores["decisions_count"] = 1.0 if decision_count >= 3 else (
        0.5 if decision_count >= 2 else 0.0)

    # 4) 行動項目＋負責人（用逐字稿推導出的被指派負責人）
    names_found = sum(1 for nm in assigned if nm in c)
    action_patterns = [r"行動項目", r"待辦", r"to[\s-]*do", r"負責",
                       r"(?:請|需|要|會|應|將)\s*\S"]
    has_actions = any(re.search(p, c, re.IGNORECASE) for p in action_patterns)
    scores["action_items_with_owners"] = 1.0 if (
        names_found >= 2 and has_actions) else (
        0.5 if (names_found >= 1 or has_actions) else 0.0)

    # 5) 行動項目數量（條列／編號）
    action_list_items = re.findall(
        r"(?:^|\n)\s*(?:[-*+•]|\d+[.)、])\s*\S.{6,}", c)
    n = len(action_list_items)
    scores["action_items_count"] = 1.0 if n >= 5 else (0.5 if n >= 3 else 0.0)

    # 6) 期限：星期二（Tuesday）／截止／期限
    deadline_patterns = [r"星期二", r"週二", r"禮拜二", r"tuesday",
                        r"截止", r"期限", r"下班前", r"本週", r"deadline",
                        r"end\s*of\s*(?:the\s*)?day"]
    scores["deadline_mentioned"] = 1.0 if any(
        re.search(p, c, re.IGNORECASE) for p in deadline_patterns) else 0.0

    # 7) 語氣：開頭有稱呼語、結尾有結語
    head = c[:200]
    tail = c[-300:]
    has_greeting = bool(re.search(
        r"團隊|大家|各位|嗨|您好|你好|敬啟|親愛的|dear|hi|hello", head,
        re.IGNORECASE))
    has_closing = bool(re.search(
        r"謝謝|感謝|辛苦了|敬上|祝|順頌|此致|best|regards|thanks", tail,
        re.IGNORECASE))
    scores["tone_appropriate"] = 1.0 if (has_greeting and has_closing) else (
        0.5 if (has_greeting or has_closing) else 0.0)

    # 8) 精簡度（中文以字元數估算，約 600 字 ≈ 600 個中文字）
    han_chars = len(re.findall(r"[一-鿿]", c))
    scores["concise"] = 1.0 if han_chars <= 700 else (
        0.5 if han_chars <= 1100 else 0.0)

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
