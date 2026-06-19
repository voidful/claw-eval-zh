"""Grader for T114tw_meeting_council_neighborhood (Taiwan-localized from PinchBench `task_meeting_council_neighborhood`).

Phase 2 source: tasks_zh/task_meeting_council_neighborhood.md
Original file: tasks/task_meeting_council_neighborhood.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """南港市議會（虛構）里別／選區辨識 grader。

    查核項對應原版，但改查台灣逐字稿（dest=transcript.md）推導之事實，
    比對 agent 產出之中文報告 neighborhoods_report.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)
    report_path = workspace / "neighborhoods_report.md"
    if not report_path.exists():
        for alt in ["neighborhoods.md", "locations.md", "districts.md",
                    "areas.md", "里別報告.md", "社區報告.md", "報告.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break

    keys = ["report_created", "temple_crest", "west_tampa", "south_howard",
            "east_tampa", "highland_pines", "rezoning_addresses", "macdill",
            "riverwalk", "frequency_or_crossref", "location_count"]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report_path.read_text(encoding="utf-8", errors="ignore")

    # 廟前里（Temple Crest）：治安改善 / 麥尼爾巡佐 / 犯罪下降
    scores["temple_crest"] = 1.0 if (
        re.search(r"廟前里|廟前", c)
        and re.search(r"麥尼爾|治安|犯罪|竊盜|模範員警|Temple\s*Crest", c)
    ) else 0.0

    # 西港里：羅馬倉庫園區 / 職棒球場（猿隊）/ 開發
    scores["west_tampa"] = 1.0 if (
        re.search(r"西港里|西港", c)
        and re.search(r"羅馬倉庫園區|羅馬倉庫|Rome\s*Yard|猿隊|職棒|球場|開發", c)
    ) else 0.0

    # 南港大道（South Howard）：封街施工 / 老舊管線 / 雨水下水道
    scores["south_howard"] = 1.0 if (
        re.search(r"南港大道", c)
        and re.search(r"封街|施工|管線|下水道|米其里尼|South\s*Howard", c)
    ) else 0.0

    # 東港里：22 路廊 / 開發 / 分區變更 / 環評
    scores["east_tampa"] = 1.0 if (
        re.search(r"東港里|東港", c)
        and re.search(r"開發|建設|22\s*路廊|分區|環評", c)
    ) else 0.0

    # 高地里（Highland Pines）：街友 / 遊民 / 安置 / 中正路 / 高德森
    scores["highland_pines"] = 1.0 if (
        re.search(r"高地里|高地", c)
        and re.search(r"街友|遊民|安置|中正路|高德森|Highland\s*Pines", c)
    ) else 0.0

    # 分區變更門牌：公道五路 4102 / 市民大道二段 2707 / 南港大道 110
    addresses = [
        r"公道五路\s*4102|4102\s*號",
        r"市民大道(?:二段)?\s*2707|2707\s*號",
        r"南港大道\s*110|110\s*號",
    ]
    addr_hits = sum(1 for a in addresses if re.search(a, c))
    scores["rezoning_addresses"] = (
        1.0 if addr_hits >= 3 else (0.5 if addr_hits >= 2 else 0.0)
    )

    # 南港空軍基地（MacDill AFB）
    scores["macdill"] = 1.0 if re.search(r"南港空軍基地|空軍基地|MacDill", c) else 0.0

    # 河岸步道（Riverwalk）：與 羅馬倉庫園區 / 串聯 / 延伸 / 西側 / 開發
    scores["riverwalk"] = 1.0 if (
        re.search(r"河岸步道|Riverwalk", c)
        and re.search(r"羅馬倉庫|串聯|延伸|西側|連通|連結|開發|基隆河", c)
    ) else 0.0

    # 出現次數統計 或 議題交叉對照
    scores["frequency_or_crossref"] = 1.0 if re.search(
        r"提及\s*\d+\s*次|提及次數|提及頻次|頻次|次數統計|交叉對照|"
        r"cross[\s-]*ref|最熱門|最頻繁|最常|frequen", c
    ) else 0.0

    # 不同地點數（自台灣逐字稿推導之候選清單）
    location_patterns = [
        r"廟前里|廟前",
        r"西港里|西港",
        r"南港大道",
        r"東港里|東港",
        r"高地里|高地",
        r"社子里|社子",
        r"古堡里|古堡灣|古堡",
        r"市中心|商圈",
        r"河岸步道|基隆河",
        r"黃蜂里|黃蜂",
        r"羅馬倉庫園區|羅馬倉庫",
        r"南港空軍基地|空軍基地",
        r"公道五路",
        r"市民大道",
        r"忠孝東路",
        r"中正路",
        r"中興路",
        r"福橡活動中心|福橡",
        r"義塚公園|義塚",
        r"台中|臺中|嘉義|高雄",
    ]
    found = sum(1 for p in location_patterns if re.search(p, c))
    scores["location_count"] = (
        1.0 if found >= 15 else (0.75 if found >= 10 else (0.5 if found >= 6 else 0.0))
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
