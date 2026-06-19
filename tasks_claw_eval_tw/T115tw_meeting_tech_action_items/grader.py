"""Grader for T115tw_meeting_tech_action_items (Taiwan-localized from PinchBench `task_meeting_tech_action_items`).

Phase 2 source: tasks_zh/task_meeting_tech_action_items.md
Original file: tasks/task_meeting_tech_action_items.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """鼎峰科技產品週會行動項目 grader。

    做法：先從台灣逐字稿 meeting_transcript.md「動態推導」出應有事實
    （被指派的負責人、各主題關鍵字、期限），再比對 agent 產出的中文報告
    action_items.md。盡量不硬寫英文原版事實，提升可重現性。僅用標準函式庫。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 找 agent 報告 ---
    report = workspace / "action_items.md"
    if not report.exists():
        for alt in ["actions.md", "action-items.md", "meeting_actions.md",
                    "action_item.md", "行動項目.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["report_created", "min_action_items", "owners_identified",
            "events_actions", "announcement_actions", "announcements_product",
            "competitive_actions", "messaging_actions", "deadlines_noted"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 讀逐字稿，動態推導「應有事實」---
    tpath = workspace / "meeting_transcript.md"
    tx = ""
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    # (a) 從逐字稿中「**行動項目…**」段落抓出被指派工作的負責人姓名。
    #     逐字稿格式如：**行動項目：戴立安在本週內整理…** / **行動項目：高敏哲…**
    name_re = re.compile(r"[一-鿿]{2,3}")
    # 已知的與會者姓名清單（從逐字稿「與會者」區塊取，作為過濾白名單）
    attendees = set(re.findall(
        r"[-\s]([一-鿿]{2,3})（", tx)) if tx else set()
    # 收斂出真正在行動項目句子裡被點名的負責人
    assigned = []
    for m in re.finditer(r"行動項目[：:]\s*([^\n*。]{0,40})", tx):
        seg = m.group(1)
        for nm in name_re.findall(seg):
            if nm in attendees and nm not in assigned:
                assigned.append(nm)
    # 後備：逐字稿解析不到時，採用會議與會者姓名
    if not assigned and attendees:
        assigned = list(attendees)
    # 再後備：連與會者都抓不到（理論上不會），用最小已知集合
    if not assigned:
        assigned = ["戴立安", "高敏哲", "蔡思敏", "王志明", "陳柏宇", "林淑芬"]

    # (b) 從逐字稿動態抓出活動／研討會名稱（用來查核 events 主題）
    event_terms = []
    for term in ["COSCUP", "DevOpsDays", "Kubernetes Day", "研討會", "贊助"]:
        if not tx or term in tx:
            event_terms.append(term)
    if not event_terms:
        event_terms = ["研討會", "贊助"]

    # (c) 主標語：從逐字稿動態抓出選定的主標語。會議結尾的複習句寫成
    #     「…訊息主標語『更快交付，更低風險』」，引號緊接在「主標語」之後，
    #     可避免誤抓中段玩笑句裡的引號內容。
    tagline = ""
    mt = re.search(r"主標語[，、\s]*「([^」]{2,20})」", tx) if tx else None
    if not mt and tx:
        # 後備：抓「…『X』當主標語」形式（引號在前）
        mt = re.search(r"「([^」]{2,20})」\s*當主標語", tx)
    if mt:
        tagline = mt.group(1)
    if not tagline:
        tagline = "更快交付，更低風險"

    # --- 計分 ---

    # 1) 行動項目數量（條列／編號／關鍵詞）
    markers = re.findall(
        r"(?:行動項目|待辦|action\s*item|^\s*[-*+]\s|^\s*\d+[.)]\s)",
        c, re.MULTILINE | re.IGNORECASE)
    n = len(markers)
    scores["min_action_items"] = 1.0 if n >= 5 else (0.5 if n >= 3 else 0.0)

    # 2) 負責人：報告中出現幾位逐字稿推導出的被指派負責人
    oc = sum(1 for nm in assigned if nm in c)
    scores["owners_identified"] = 1.0 if oc >= 3 else (0.5 if oc >= 2 else 0.0)

    # 3) 活動／研討會（發表會）主題
    ev_hits = sum(1 for t in event_terms if t in c)
    generic_ev = bool(re.search(r"活動|研討會|展會|發表會|贊助", c))
    scores["events_actions"] = 1.0 if (ev_hits >= 1 and generic_ev) else (
        0.5 if (ev_hits >= 1 or generic_ev) else 0.0)

    # 4) 對內公告（announcement）
    scores["announcement_actions"] = 1.0 if re.search(
        r"公告|announcement|通知各部門|對內通知|內部通知", c, re.IGNORECASE) else 0.0

    # 5) 產品發布：整體前 5 名 / top 5 / Plan 候選清單
    prod_a = bool(re.search(r"top\s*5|前\s*5|前五|整體前", c, re.IGNORECASE))
    prod_b = bool(re.search(r"產品發布|發布|keynote|匯流大會|Plan|規劃|試算表",
                            c, re.IGNORECASE))
    scores["announcements_product"] = 1.0 if (prod_a and prod_b) else (
        0.5 if (prod_a or prod_b) else 0.0)

    # 6) 競品分析：tier 1 對手 + 在比較表新增鼎峰一列
    comp_a = bool(re.search(r"tier\s*1|tier\s*one|分層|競品|競爭對手",
                            c, re.IGNORECASE))
    comp_b = bool(re.search(r"鼎峰一列|鼎峰.{0,4}列|新增.{0,6}列|line\s*item|加上.{0,4}列",
                            c, re.IGNORECASE))
    scores["competitive_actions"] = 1.0 if (comp_a and comp_b) else (
        0.5 if (comp_a or comp_b) else 0.0)

    # 7) 訊息架構：定稿 + 主標語（動態取得的 tagline）
    msg_a = bool(re.search(r"訊息架構|標語|messaging|tagline|定稿",
                           c, re.IGNORECASE))
    msg_b = (tagline in c) or bool(
        re.search(r"更快交付|更低風險", c))
    scores["messaging_actions"] = 1.0 if (msg_a and msg_b) else (
        0.5 if (msg_a or msg_b) else 0.0)

    # 8) 期限：星期二 / 本週(內) / 今天下班前 等
    deadline_terms = [r"星期二", r"週二", r"本週", r"這週", r"下班前",
                      r"今天.*下班", r"end\s*of\s*(?:the\s*)?day", r"期限", r"截止"]
    d_hits = sum(1 for p in deadline_terms if re.search(p, c, re.IGNORECASE))
    scores["deadlines_noted"] = 1.0 if d_hits >= 2 else (0.5 if d_hits >= 1 else 0.0)

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
