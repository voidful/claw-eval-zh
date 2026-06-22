"""Grader for T113tw_meeting_council_contact_info (Taiwan-localized from PinchBench `task_meeting_council_contact_info`).

Phase 2 source: tasks_zh/task_meeting_council_contact_info.md
Original file: tasks/task_meeting_council_contact_info.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """南港市議會（虛構）人物與聯絡資訊 grader。

    事實全部由台灣逐字稿 transcript.md 動態推導後，再比對 agent 產出的中文報告
    contacts_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 1. 從台灣逐字稿動態讀出「應有事實」（避免硬寫） ---
    transcript_path = workspace / "transcript.md"
    tcontent = ""
    if transcript_path.exists():
        tcontent = transcript_path.read_text(encoding="utf-8", errors="ignore")

    # 議會議員：從「出席議員名單」區塊的條列推導；推導失敗則回退到已知名單。
    council_fallback = ["周明德", "陳秀蓮", "高文彬", "林淑芬",
                        "楊乃文", "韋立群", "卡爾森"]
    council = []
    for name in council_fallback:
        if name in tcontent:
            council.append(name)
    if not council:
        council = council_fallback
    # 卡爾森的本名 蔡明憲 任一出現即視為涵蓋第 7 選區議員。
    carlson_aliases = [a for a in ("卡爾森", "蔡明憲") if a in tcontent] or ["卡爾森"]

    # 市民公眾發言人：從「市民公眾意見發言」各小節標題（### N. 姓名（…））推導。
    # 名字須以中文字開頭，藉此排除像「5.1 自來水…」這種小數編號的子標題。
    speakers = re.findall(
        r'^###\s*\d+\.\s*([一-鿿][^\s（(]*)', tcontent, re.MULTILINE)
    speakers = [s.strip() for s in speakers if s.strip()]
    if len(speakers) < 8:  # 推導不足時回退到已知名單
        speakers = ["詹明慧", "任薇", "海曉光", "簡珮如", "高德森", "紀志中",
                    "莫雅淳", "班奈特", "蒲怡婷", "米其里尼", "賈明德",
                    "駱明潔", "卜雅玲", "潘思妤", "任明哲", "羅志安"]

    # 升任警務正的四位巡佐（從逐字稿推導，回退用已知名單）。
    promoted = [n for n in ("戴飛理", "梅斯莫", "普瑟爾", "馬可銘") if n in tcontent]
    if len(promoted) < 4:
        promoted = ["戴飛理", "梅斯莫", "普瑟爾", "馬可銘"]

    checks = ["report_created", "council_members", "shelby_attorney",
              "hamilton_raftelis", "bercaw_chief", "mcneil_officer",
              "public_speakers", "tpd_promotions", "organized_sections",
              "milo_related"]

    # --- 2. 找出 agent 的報告檔 ---
    report_path = workspace / "contacts_report.md"
    if not report_path.exists():
        for alt in ["contacts.md", "people.md", "directory.md",
                    "人物清單.md", "聯絡資訊.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in checks}

    scores = {"report_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 3. 逐項比對中文關鍵字／人物 ---
    # 議員：7 位全到才滿分（卡爾森以別名任一計入）。
    council_hit = sum(1 for c in council if c != "卡爾森" and c in content)
    if any(a in content for a in carlson_aliases):
        council_hit += 1
    scores["council_members"] = 1.0 if council_hit >= 7 else (
        0.5 if council_hit >= 4 else 0.0)

    # 議會法律顧問 謝佩玲。
    scores["shelby_attorney"] = 1.0 if (
        "謝佩玲" in content
        and re.search(r'法律顧問|法制顧問|法律|法務|顧問', content)
    ) else 0.0

    # 外部顧問 韓明翰／瑞富緯顧問。
    scores["hamilton_raftelis"] = 1.0 if (
        "韓明翰" in content and re.search(r'瑞富緯|顧問', content)
    ) else 0.0

    # 警察局長 包柯偉。
    scores["bercaw_chief"] = 1.0 if (
        "包柯偉" in content and re.search(r'警察局長|警察局|局長|警政', content)
    ) else 0.0

    # 本月模範員警 麥尼爾。
    scores["mcneil_officer"] = 1.0 if (
        "麥尼爾" in content
        and re.search(r'本月模範員警|模範員警|本月最佳員警|表揚|頒獎|獲獎',
                      content)
    ) else 0.0

    # 市民公眾發言人：命中 12 位以上滿分。
    spk_hit = sum(1 for s in speakers if s and s in content)
    scores["public_speakers"] = 1.0 if spk_hit >= 12 else (
        0.5 if spk_hit >= 6 else 0.0)

    # 升任警務正四位巡佐：命中 3 位以上滿分。
    promo_hit = sum(1 for p in promoted if p in content)
    scores["tpd_promotions"] = 1.0 if promo_hit >= 3 else (
        0.5 if promo_hit >= 1 else 0.0)

    # 分區段整理：至少命中 3 類區段標題。
    section_patterns = [
        r'議員',
        r'市府職員|局處|幕僚|職員|首長',
        r'市民|公眾|發言|陳情',
        r'簡報|顧問|專家|外部',
    ]
    sec_hit = sum(1 for p in section_patterns if re.search(p, content))
    scores["organized_sections"] = 1.0 if sec_hit >= 3 else (
        0.5 if sec_hit >= 2 else 0.0)

    # 米羅／鼎峰都更開發（社區致贈紀念品代表）。
    scores["milo_related"] = 1.0 if (
        "米羅" in content
        and re.search(r'鼎峰都更開發|鼎峰都更|鼎峰|董事長|總裁', content)
    ) else 0.0

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
