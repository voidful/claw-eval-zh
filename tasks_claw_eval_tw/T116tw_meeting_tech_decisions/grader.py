"""Grader for T116tw_meeting_tech_decisions (Taiwan-localized from PinchBench `task_meeting_tech_decisions`).

Phase 2 source: tasks_zh/task_meeting_tech_decisions.md
Original file: tasks/task_meeting_tech_decisions.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣鼎峰科技產品會議「決議擷取」grader（固定虛構逐字稿）。

    對應原 PinchBench task_meeting_tech_decisions 的九個查核項，但改查台灣逐字稿
    (dest=meeting_transcript.md) 推導之事實 + agent 的中文報告 decisions.md。
    僅用標準函式庫。報告為繁體中文，故以中文關鍵字／數值比對；轉換器會在其後自動
    接上中→英正規化 wrapper（附加英文關鍵字、保留原中文），不影響中文比對。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "decisions.md"
    if not report_path.exists():
        for alt in ["meeting_decisions.md", "decision_log.md",
                    "decisions_summary.md", "decisions_report.md",
                    "會議決議.md", "決議.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    if not report_path.exists():
        return {
            "report_created": 0.0,
            "min_decisions": 0.0,
            "event_assignments": 0.0,
            "announcement_approach": 0.0,
            "competitive_methodology": 0.0,
            "messaging_tagline": 0.0,
            "infographic_colors": 0.0,
            "context_provided": 0.0,
            "status_indicated": 0.0,
        }

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    low = content.lower()

    # --- 從逐字稿動態讀出「應有事實」以供比對（避免硬寫）---
    tpath = workspace / "meeting_transcript.md"
    tx = ""
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")
    tx_low = tx.lower()

    # 1) 最少決議數量：中文標題/條列/含「決議|決定」的行
    decision_markers = re.findall(
        r'(?:^|\n)\s*(?:[-*•]|\d+[.)、]|決議|決定) .{4,}', content)
    headers = re.findall(r'(?:^|\n)#+\s+.+', content)
    decision_word_lines = re.findall(r'(?:^|\n)[^\n]*(?:決議|決定)[^\n]{2,}', content)
    n_dec = max(len(decision_markers), len(decision_word_lines))
    if n_dec >= 5 or len(headers) >= 5:
        scores["min_decisions"] = 1.0
    elif n_dec >= 3 or len(headers) >= 3:
        scores["min_decisions"] = 0.5
    else:
        scores["min_decisions"] = 0.0

    # 2) 活動贊助分工：三場台灣研討會（COSCUP / DevOpsDays Taipei / Kubernetes Day）
    #    從逐字稿動態抓出實際出現的活動名，再看報告命中幾個。
    event_terms = []
    for pat in [r'coscup', r'devopsdays', r'kubernetes day']:
        if re.search(pat, tx_low):
            event_terms.append(pat)
    if not event_terms:  # 逐字稿缺失時的保險預設
        event_terms = [r'coscup', r'devopsdays', r'kubernetes day']
    # 中文別名也接受（開源人年會 ~ COSCUP）
    event_hits = 0
    if re.search(r'coscup|開源人年會', low):
        event_hits += 1
    if re.search(r'devopsdays', low):
        event_hits += 1
    if re.search(r'kubernetes day|k8s day', low):
        event_hits += 1
    scores["event_assignments"] = (
        1.0 if event_hits >= 2 else (0.5 if event_hits >= 1 else 0.0))

    # 3) 產品發布整合方式：把多個 MVC 包成主題（如漏洞管理），重用 5.0 版內容
    announce_a = bool(re.search(r'整合|包成|彙整|歸納|bundle|綁成一(?:包|個)|打包|主題敘事', content, re.IGNORECASE))
    announce_b = bool(re.search(r'漏洞管理|vulnerability\s*management|mvc|5\.0', content, re.IGNORECASE))
    announce_hits = int(announce_a) + int(announce_b)
    scores["announcement_approach"] = (
        1.0 if announce_hits >= 2 else (0.5 if announce_hits >= 1 else 0.0))

    # 4) 競品方法論：只用 tier 1、每個 stage 只放相關對手、新增鼎峰一列
    comp_a = bool(re.search(r'tier\s*(?:1|one|一)|第一層|一級', content, re.IGNORECASE))
    comp_b = bool(re.search(r'鼎峰.{0,8}(?:一列|一行|加[一上]|列|row|line)|新增.{0,6}鼎峰|加上.{0,6}鼎峰|gitlab', content, re.IGNORECASE))
    comp_c = bool(re.search(r'(?:相關|適用|對應)[^\n]{0,12}(?:stage|對手|競爭|競品)|每個\s*stage|各\s*stage', content, re.IGNORECASE))
    comp_hits = int(comp_a) + int(comp_b) + int(comp_c)
    scores["competitive_methodology"] = (
        1.0 if comp_hits >= 2 else (0.5 if comp_hits >= 1 else 0.0))

    # 5) 訊息主標語：選定「更快交付，更低風險」
    tagline = bool(re.search(r'更快交付[，,、\s]*更低風險|more\s*speed\s*less\s*risk', content, re.IGNORECASE))
    scores["messaging_tagline"] = 1.0 if tagline else 0.0

    # 6) 資訊圖配色：只用綠色、不放紅色（保持比較調性）
    color = bool(re.search(
        r'(?:只用|維持|保留|沿用).{0,6}綠|綠色.{0,10}(?:不[用放]|沒有|避免).{0,4}紅|不[用放].{0,4}紅|避免.{0,4}紅|綠色.{0,6}比較|green.*(?:no\s*red|without\s*red)',
        content, re.IGNORECASE))
    scores["infographic_colors"] = 1.0 if color else 0.0

    # 7) 背景脈絡：報告中有解釋性敘述
    ctx_a = bool(re.search(r'因為|原因|背景|脈絡|理由|為了|由於|考量|緣由|since|because|rationale|context', content, re.IGNORECASE))
    ctx_b = bool(re.search(r'討論|考慮|權衡|評估|爭論|斟酌|替代方案|候選|discuss|debate|consider', content, re.IGNORECASE))
    ctx_hits = int(ctx_a) + int(ctx_b)
    scores["context_provided"] = (
        1.0 if ctx_hits >= 2 else (0.5 if ctx_hits >= 1 else 0.0))

    # 8) 決議狀態：final / tentative / needs follow-up（暫定、待確認、定案…）
    st_a = bool(re.search(r'final|定案|確定|拍板|tentative|暫定|待確認|待後續|follow.?up|needs?\s*follow|待跟進|待確定|未定案', content, re.IGNORECASE))
    st_b = bool(re.search(r'狀態|status|共識|consensus|已通過|議定|達成|agreed', content, re.IGNORECASE))
    st_hits = int(st_a) + int(st_b)
    scores["status_indicated"] = (
        1.0 if st_hits >= 2 else (0.5 if st_hits >= 1 else 0.0))

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
