"""Grader for T125tw_meeting_executive_summary (Taiwan-localized from PinchBench `task_meeting_executive_summary`).

Phase 2 source: tasks_zh/task_meeting_executive_summary.md
Original file: tasks/task_meeting_executive_summary.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """高階主管摘要 grader（台灣虛構逐字稿：鼎峰科技產品行銷週會）。

    應有事實盡量從 meeting_transcript.md 動態推導，再比對 agent 的中文報告
    executive_summary.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 讀取 agent 報告 ---
    report_path = workspace / "executive_summary.md"
    if not report_path.exists():
        for alt in ["exec_summary.md", "summary.md", "meeting_summary.md", "摘要.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = [
        "file_created", "meeting_date", "topics_identified", "events_covered",
        "announcements_covered", "decisions_documented", "attendees_named",
        "action_items_present", "concise",
    ]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態推導應有事實 ---
    src = workspace / "meeting_transcript.md"
    src_text = src.read_text(encoding="utf-8", errors="ignore") if src.exists() else ""

    # 日期：抓逐字稿裡的 YYYY-MM-DD（取第一個）
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})", src_text)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        date_variants = [
            rf"{y}-{mo}-{d}",
            rf"{y}\s*年\s*{int(mo)}\s*月\s*{int(d)}\s*日",
            rf"{y}/{int(mo)}/{int(d)}",
            rf"{y}/{mo}/{d}",
        ]
    else:
        date_variants = [r"2025-03-18"]

    # 與會者：抓逐字稿裡反覆出現的三字中文人名
    known_owners = ["王志明", "林淑芬", "高敏哲", "陳柏宇", "蔡思敏", "戴立安"]
    attendees = [n for n in known_owners if n in src_text]
    if not attendees:
        attendees = known_owners

    scores = {"file_created": 1.0}

    # --- 會議日期 ---
    scores["meeting_date"] = (
        1.0 if any(re.search(p, content) for p in date_variants) else 0.0
    )

    # --- 關鍵主題數 ---
    topic_count = 0
    if re.search(r"(?:企業活動|活動贊助|贊助分工|研討會|COSCUP|DevOpsDays|Kubernetes\s*Day)",
                 content, re.IGNORECASE):
        topic_count += 1
    if re.search(r"(?:鼎峰匯流|DingFeng\s*Connect|產品發布|前\s*5\s*名|前五名|top\s*5|漏洞管理)",
                 content, re.IGNORECASE):
        topic_count += 1
    if re.search(r"(?:競品|比較|資訊圖|infographic)", content, re.IGNORECASE):
        topic_count += 1
    if re.search(r"(?:訊息架構|標語|支柱|更快交付|單一真相來源)", content):
        topic_count += 1
    if re.search(r"(?:tier\s*1|分層|試算表|每個\s*stage)", content, re.IGNORECASE):
        topic_count += 1
    scores["topics_identified"] = (
        1.0 if topic_count >= 3 else (0.5 if topic_count >= 2 else 0.0)
    )

    # --- 企業活動分工涵蓋 ---
    event_patterns = [
        r"COSCUP|開源人年會",
        r"DevOpsDays\s*Taipei|DevOpsDays",
        r"Kubernetes\s*Day\s*Taiwan|Kubernetes\s*Day",
        r"活動\s*(?:贊助|分工|主線)|研討會",
    ]
    ev = sum(1 for p in event_patterns if re.search(p, content, re.IGNORECASE))
    scores["events_covered"] = 1.0 if ev >= 2 else (0.5 if ev >= 1 else 0.0)

    # --- 產品發布題材涵蓋 ---
    announce_patterns = [
        r"鼎峰匯流|DingFeng\s*Connect",
        r"產品發布|keynote|發布題材",
        r"前\s*5\s*名|前五名|top\s*5",
        r"漏洞管理|vulnerability\s*management",
        r"MVC|主題敘事|整合\s*(?:成|為)?\s*主題",
    ]
    an = sum(1 for p in announce_patterns if re.search(p, content, re.IGNORECASE))
    scores["announcements_covered"] = 1.0 if an >= 2 else (0.5 if an >= 1 else 0.0)

    # --- 決議記載 ---
    decision_count = 0
    if re.search(r"更快交付[，,、\s]*更低風險", content):
        decision_count += 1
    if re.search(r"(?:只用綠色|綠色|不用紅色|不放紅色|綠色配色)", content):
        decision_count += 1
    if re.search(r"漏洞管理", content):
        decision_count += 1
    if re.search(r"(?:平台.*COSCUP|CI/?CD.*DevOpsDays|GitOps.*Kubernetes\s*Day)",
                 content, re.IGNORECASE | re.DOTALL):
        decision_count += 1
    if re.search(r"(?:每個\s*stage\s*只|相關.*對手|新增鼎峰|鼎峰一列|加上鼎峰)",
                 content, re.IGNORECASE):
        decision_count += 1
    scores["decisions_documented"] = (
        1.0 if decision_count >= 2 else (0.5 if decision_count >= 1 else 0.0)
    )

    # --- 與會者姓名 ---
    named = sum(1 for n in attendees if n in content)
    scores["attendees_named"] = (
        1.0 if named >= 2 else (0.5 if named >= 1 else 0.0)
    )

    # --- 行動項目／後續步驟 ---
    action_patterns = [
        r"行動項目|action\s*item",
        r"後續步驟|後續|next\s*step",
        r"待辦|follow[\s-]*up|追蹤",
        r"星期二|截止|下次會議",
        r"負責人|指派|負責",
        r"(?:王志明|戴立安|高敏哲|蔡思敏|陳柏宇|林淑芬).{0,12}(?:負責|要|將|需|補|確認|定稿|修改)",
    ]
    ac = sum(1 for p in action_patterns if re.search(p, content, re.IGNORECASE))
    scores["action_items_present"] = 1.0 if ac >= 2 else (0.5 if ac >= 1 else 0.0)

    # --- 精簡度（中文以字元數估算，約 1200 字以內）---
    cjk = len(re.findall(r"[一-鿿]", content))
    length = cjk if cjk > 0 else len(content.split())
    scores["concise"] = (
        1.0 if length <= 1200 else (0.5 if length <= 1800 else 0.0)
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
