"""Grader for T110tw_meeting_council_public_comment (Taiwan-localized from PinchBench `task_meeting_council_public_comment`).

Phase 2 source: tasks_zh/task_meeting_council_public_comment.md
Original file: tasks/task_meeting_council_public_comment.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """對台灣化逐字稿（transcript.md）動態推導應有事實，比對 agent 的中文報告。

    只用標準函式庫。報告為中文 public_comments_report.md。
    """
    from pathlib import Path
    import re

    keys = [
        "report_created",
        "williams_zion",
        "iman_8million",
        "cannella_stormwater",
        "poole_tpd",
        "poynor_romeyard",
        "speaker_count",
        "thematic_summary",
        "zion_multiple",
    ]
    scores = {k: 0.0 for k in keys}
    workspace = Path(workspace_path)

    # 找出 agent 報告
    report_path = workspace / "public_comments_report.md"
    if not report_path.exists():
        for alt in [
            "public_comments_report.md",
            "public_comments.md",
            "comments_report.md",
            "comments.md",
            "公眾意見報告.md",
            "公眾意見.md",
        ]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return scores

    scores["report_created"] = 1.0
    try:
        content = report_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return scores

    # --- 從逐字稿動態推導「應有的 16 位公眾發言者姓名」 ---
    speaker_names = []
    try:
        tpath = workspace / "transcript.md"
        if tpath.exists():
            ttext = tpath.read_text(encoding="utf-8")
            in_pc = False
            for line in ttext.splitlines():
                # 進入「市民公眾意見發言」段落
                if re.search(r"市民公眾意見發言", line):
                    in_pc = True
                    continue
                # 離開該段落（進入「五、預算」等下一大段）
                if in_pc and re.match(r"^##\s*[五六七八]", line):
                    break
                if not in_pc:
                    continue
                # 形如：### 1. 詹明慧（西港里居民）
                m = re.match(r"^###\s*\d+\.\s*([^\s（(]+)", line.strip())
                if m:
                    nm = m.group(1).strip()
                    if nm and nm not in speaker_names:
                        speaker_names.append(nm)
    except (OSError, UnicodeDecodeError):
        speaker_names = []

    # 萬一逐字稿解析失敗，退回固定名單（與逐字稿一致）
    if len(speaker_names) < 16:
        speaker_names = [
            "詹明慧", "任薇", "海曉光", "簡珮如", "高德森", "紀志中",
            "莫雅淳", "班奈特", "蒲怡婷", "米其里尼", "賈明德", "駱明潔",
            "卜雅玲", "潘思妤", "任明哲", "羅志安",
        ]

    # --- 個別事實查核（中文關鍵字/數值）---
    zion = r"義塚"  # 義塚公園／義塚紀念園區／義塚紀念館
    scores["williams_zion"] = (
        1.0 if ("詹明慧" in content and re.search(zion, content)) else 0.0
    )

    # 8,000 萬元 / NT$80,000,000 / 8000萬 等多種寫法
    eight_million = re.search(
        r"8[,，]?000\s*萬|8000\s*萬|八千萬|80[,，]?000[,，]?000",
        content,
    )
    scores["iman_8million"] = (
        1.0 if ("任薇" in content and eight_million) else 0.0
    )

    stormwater = re.search(r"雨水|颱風|豪雨|積水|淹水|防災|凱米", content)
    scores["cannella_stormwater"] = (
        1.0 if ("簡珮如" in content and stormwater) else 0.0
    )

    tpd = re.search(r"警|密錄器|員警|盤查|少年|兒子|未成年|執法", content)
    scores["poole_tpd"] = (
        1.0 if ("蒲怡婷" in content and tpd) else 0.0
    )

    romeyard = re.search(r"中崙倉庫|1436", content)
    scores["poynor_romeyard"] = (
        1.0 if ("潘思妤" in content and romeyard) else 0.0
    )

    # --- 發言者辨識數量 ---
    found = sum(1 for nm in speaker_names if nm and nm in content)
    if found >= 14:
        scores["speaker_count"] = 1.0
    elif found >= 12:
        scores["speaker_count"] = 0.75
    elif found >= 8:
        scores["speaker_count"] = 0.5
    else:
        scores["speaker_count"] = 0.0

    # --- 主題摘要：須有「分組/主題」措辭 + 至少一個主題領域詞 ---
    has_grouping = re.search(r"主題|分類|分組|歸納|領域|彙整|歸類", content)
    has_topic = re.search(
        r"基礎建設|基礎設施|住宅|住房|文史|歷史|保存|警政|警察|治安|交通|"
        r"運輸|環境|防災|遊民|街友|分區|都市計畫|公共建設",
        content,
    )
    scores["thematic_summary"] = (
        1.0 if (has_grouping and has_topic) else 0.0
    )

    # --- 義塚 為多位發言者共同提及 ---
    # 動態：在逐字稿中找出提及「義塚」的公眾發言者，於報告中檢查其與「義塚」同段出現。
    zion_candidates = ["詹明慧", "任薇", "駱明潔", "羅志安"]
    # 以「段落」為單位（以兩個以上換行或 ### 標題切段較難，採行/區塊鄰近法）
    blocks = re.split(r"\n\s*\n|\n#{1,6}\s", content)
    zion_speakers = 0
    for nm in zion_candidates:
        for blk in blocks:
            if nm in blk and "義塚" in blk:
                zion_speakers += 1
                break
    if zion_speakers >= 2:
        scores["zion_multiple"] = 1.0
    elif zion_speakers >= 1:
        scores["zion_multiple"] = 0.5
    else:
        scores["zion_multiple"] = 0.0

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
