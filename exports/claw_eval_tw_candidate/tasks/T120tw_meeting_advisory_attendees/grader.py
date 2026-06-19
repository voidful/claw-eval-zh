"""Grader for T120tw_meeting_advisory_attendees (Taiwan-localized from PinchBench `task_meeting_advisory_attendees`).

Phase 2 source: tasks_zh/task_meeting_advisory_attendees.md
Original file: tasks/task_meeting_advisory_attendees.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理顧問委員會（虛構）與會者名單 grader。

    事實全部由台灣逐字稿 meeting-transcript.md 動態推導後，再比對 agent 產出的
    中文報告 attendees.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 1. 從台灣逐字稿動態讀出「應有事實」（避免硬寫） ---
    transcript_path = workspace / "meeting-transcript.md"
    tcontent = ""
    if transcript_path.exists():
        tcontent = transcript_path.read_text(encoding="utf-8", errors="ignore")

    def _names(header_regex):
        """擷取某出席名單小節下，條列項中的『某某 委員/主席/…』中文姓名。"""
        m = re.search(header_regex + r"\*\*\n(.*?)\n\n", tcontent, re.DOTALL)
        if not m:
            return []
        out = []
        for line in m.group(1).splitlines():
            nm = re.match(
                r"-\s*([一-鿿]{2,4})\s*(?:委員|主席|政務次長|副署長|"
                r"指定聯絡官|先生|女士)", line)
            if nm:
                out.append(nm.group(1))
        return out

    # 主席
    chair_list = _names(r"委員會主席（Chair）") or ["王志明"]
    chair = chair_list[0] if chair_list else "王志明"

    # 親自到場委員（6 位）
    inperson = _names(r"委員（親自到場 in-person）")
    if len(inperson) < 5:
        inperson = ["林淑芬", "陳建宏", "周明德", "鄭雅文", "黃國昌", "吳孟儒"]

    # 視訊連線委員（9 位）
    remote = _names(r"委員（視訊連線 remote / phone）")
    if len(remote) < 6:
        remote = ["何信宏", "馮淑惠", "麥國輝", "史丹利", "雷瑞瑟",
                  "唐諾文", "包大維", "賴明達", "柯怡君"]

    # 列席官員（4 位，非委員）
    officials = _names(r"列席官員（Also Present，非委員）")
    if len(officials) < 3:
        officials = ["史國良", "聶必亞", "鮑威霖", "包柏特"]

    # 對應原版 6 位 remote 查核（Hatfield/Feldman/McGinnis/Stancil/Reaser/Donovan）。
    remote_core = remote[:6] if len(remote) >= 6 else [
        "何信宏", "馮淑惠", "麥國輝", "史丹利", "雷瑞瑟", "唐諾文"]

    # 全體委員（含主席）名單，用於 member_count。
    all_members = [chair] + inperson + remote

    checks = ["report_created", "chair_identified", "member_count",
              "remote_attendees", "officials_listed", "organizations_included",
              "attendance_mode", "public_participant", "summary_count"]

    # --- 2. 找出 agent 的報告檔 ---
    report_path = workspace / "attendees.md"
    if not report_path.exists():
        for alt in ["attendee_list.md", "attendees_list.md",
                    "meeting_attendees.md", "與會者名單.md", "出席名單.md",
                    "與會者.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in checks}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 3. 逐項比對中文關鍵字／人物 ---
    # 主席：王志明 + 「主席」+ NESA／鼎峰緊急救難協會。
    chair_ok = (
        chair in content
        and re.search(r"主席|Chair", content)
        and re.search(r"NESA|鼎峰緊急救難", content)
    )
    scores["chair_identified"] = 1.0 if chair_ok else 0.0

    # 委員具名人數（含主席，共 16 位）：命中 15 位以上滿分。
    found = sum(1 for m in all_members if m and m in content)
    scores["member_count"] = (
        1.0 if found >= 15 else (0.5 if found >= 10 else 0.0))

    # 視訊連線委員：須出現姓名且其附近有「視訊／連線／遠端／電話／線上／*」等標記。
    remote_kw = r"視訊|連線|遠端|遠距|電話|線上|remote|phone|virtual|dial|\*"
    remote_found = 0
    for rm in remote_core:
        if rm and rm in content:
            near = (
                re.search(rm + r".{0,30}(?:" + remote_kw + r")", content)
                or re.search(r"(?:" + remote_kw + r").{0,30}" + rm, content)
            )
            if near:
                remote_found += 1
            elif re.search(r"\*", content):
                remote_found += 0.5
    scores["remote_attendees"] = (
        1.0 if remote_found >= 4 else (0.5 if remote_found >= 2 else 0.0))

    # 列席非委員官員：命中 3 位以上滿分。
    officials_found = sum(1 for o in officials if o and o in content)
    scores["officials_listed"] = (
        1.0 if officials_found >= 3 else (0.5 if officials_found >= 2 else 0.0))

    # 所屬機關／公司：從逐字稿出現的關鍵組織名取交集後再比對報告。
    org_candidates = [
        "NESA", "鼎峰緊急救難", "鼎峰科技", "中華電信", "遠傳", "台電",
        "工研院", "雷神", "玉山防務", "南港大學", "中央科技大學",
        "資安署", "頻譜管理署", "經濟與數位發展部", "數位治理委員會",
        "公共利益網路基金會", "PINF", "有線電視業者協會", "南港市政府",
        "頻譜政策研究中心", "智慧城市辦公室",
    ]
    orgs = [o for o in org_candidates if o in tcontent] or org_candidates
    org_found = sum(1 for o in orgs if o in content)
    scores["organizations_included"] = (
        1.0 if org_found >= 8 else (0.5 if org_found >= 4 else 0.0))

    # 與會方式標記：須同時出現「親自到場」類與「視訊／連線／電話」類用語。
    inperson_kw = re.search(r"親自到場|現場|到場|實體|in[- ]?person", content)
    remote_mode = re.search(
        r"視訊|連線|遠端|遠距|電話|線上|remote|phone|virtual|dial", content)
    mode_found = (1 if inperson_kw else 0) + (1 if remote_mode else 0)
    scores["attendance_mode"] = (
        1.0 if mode_found >= 2 else (0.5 if mode_found >= 1 else 0.0))

    # 公眾參與者 史耐德。
    scores["public_participant"] = 1.0 if "史耐德" in content else 0.0

    # 彙總計數：報告中須出現「總數／合計／共 N 位」等含數字的彙總敘述。
    count_patterns = [
        r"總(?:數|計|人數).{0,12}\d+",
        r"\d+.{0,12}總(?:數|計|人數)",
        r"(?:合計|共|總共).{0,8}\d+\s*(?:位|人|名)",
        r"\d+\s*(?:位|人|名).{0,8}與會",
        r"與會(?:者|人數).{0,12}\d+",
    ]
    scores["summary_count"] = (
        1.0 if any(re.search(p, content) for p in count_patterns) else 0.0)

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
