"""Grader for T121tw_meeting_advisory_stakeholders (Taiwan-localized from PinchBench `task_meeting_advisory_stakeholders`).

Phase 2 source: tasks_zh/task_meeting_advisory_stakeholders.md
Original file: tasks/task_meeting_advisory_stakeholders.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣化「頻譜共用會議利害關係人分析」grader。

    查核項對應原始英文 grader，但事實改自台灣逐字稿 meeting-transcript.md
    （虛構的數位治理委員會 DGC-SCAB 會議；頻譜管理署 OSM 主張共用優先於遷移、
    純遷移重置成本新臺幣 180 億元）。僅用標準函式庫。

    注意：報告為中文，轉換器會在中文詞後自動接上英文正規化字串，故本 grader
    以「中文關鍵字／數值」為主要比對對象（這些字串在正規化後仍原樣保留）。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "stakeholder_analysis.md"
    if not report_path.exists():
        for alt in ["stakeholders.md", "stakeholder_report.md", "analysis.md",
                    "利害關係人分析.md", "利害關係人.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    keys = ["report_created", "gov_stakeholders", "commercial_stakeholders",
            "sharing_preference", "relocation_cost", "sharing_vs_relocation",
            "common_parameters", "conflicts_identified", "member_positions"]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    low = content.lower()

    # --- 從逐字稿動態讀出「應有事實」，盡量避免硬寫 ---
    transcript_path = workspace / "meeting-transcript.md"
    ttext = ""
    if transcript_path.exists():
        ttext = transcript_path.read_text(encoding="utf-8", errors="ignore")

    # 純遷移重置成本：從逐字稿動態抓「XXX 億元」這個數字（後援為 180 億）
    cost_amt = None
    m = re.search(r'重置成本[^0-9]{0,12}?([0-9一二三四五六七八九十百千]+)\s*億', ttext)
    if not m:
        m = re.search(r'([0-9]+)\s*億元', ttext)
    if m:
        cost_amt = m.group(1)
    if not cost_amt:
        cost_amt = "180"

    # 1) 政府利害關係人（從逐字稿可得的政府機關／署）
    gov_entities = ["數位治理委員會", "dgc", "頻譜管理署", "osm", "資安署",
                    "國防部", "ostp", "科技與政策辦公室",
                    "經濟與數位發展部", "經濟與數位"]
    gov_found = sum(1 for g in gov_entities if g.lower() in low)
    scores["gov_stakeholders"] = (
        1.0 if gov_found >= 4 else (0.5 if gov_found >= 2 else 0.0)
    )

    # 2) 商業界利害關係人（電信業者、設備／科技公司、產業詞）
    commercial = ["中華電信", "遠傳", "台灣大哥大", "電信業者", "業者",
                  "鼎峰", "有線電視", "ctia", "電信業者公會",
                  "lte", "寬頻", "商用"]
    comm_found = sum(1 for c in commercial if c.lower() in low)
    scores["commercial_stakeholders"] = (
        1.0 if comm_found >= 4 else (0.5 if comm_found >= 2 else 0.0)
    )

    # 3) 頻譜管理署（OSM）偏好共用勝過純遷移
    sharing_patterns = [
        r'(?:osm|頻譜管理署|聶必亞)[^。\n]{0,40}?共用[^。\n]{0,12}?(?:優先|勝過|偏好|主張|傾向)',
        r'共用[^。\n]{0,8}?(?:優先|勝過)[^。\n]{0,8}?遷移',
        r'(?:偏好|主張|傾向|支持)[^。\n]{0,12}?共用[^。\n]{0,12}?(?:勝過|而非|不是|優先)?[^。\n]{0,6}?遷移',
        r'整批清空頻段的年代[^。\n]{0,12}?(?:走入尾聲|尾聲|結束)',
        r'共用優先',
    ]
    scores["sharing_preference"] = (
        1.0 if any(re.search(p, content) for p in sharing_patterns) else 0.0
    )

    # 4) 新臺幣 180 億元（18 billion）遷移成本
    cost_patterns = [
        re.escape(cost_amt) + r'\s*億',
        r'180\s*億',
        r'18\s*billion',
        r'18,?000,?000,?000',
        r'一百八十\s*億',
    ]
    scores["relocation_cost"] = (
        1.0 if any(re.search(p, content, re.IGNORECASE) for p in cost_patterns) else 0.0
    )

    # 5) 共用對比遷移的張力
    tension_patterns = [
        r'共用[^。\n]{0,10}?(?:對比|對上|相對於|還是|而非|而不是|或是|vs|versus)[^。\n]{0,10}?遷移',
        r'遷移[^。\n]{0,10}?(?:對比|對上|相對於|還是|而非|而不是|或是|vs|versus)[^。\n]{0,10}?共用',
        r'(?:共用|遷移)[^。\n]{0,20}?(?:張力|衝突|爭議|辯論|分歧|取捨|tension|trade-?off)',
        r'(?:張力|衝突|爭議|辯論|分歧|取捨)[^。\n]{0,20}?(?:共用|遷移)',
        r'為(?:什麼|甚麼)[^。\n]{0,12}?花[^。\n]{0,12}?搬',
    ]
    scores["sharing_vs_relocation"] = (
        1.0 if any(re.search(p, content, re.IGNORECASE) for p in tension_patterns) else 0.0
    )

    # 6) 共同（佈建）參數的辯論（周明德／鄭雅文／黃國昌／何信宏）
    param_patterns = [
        r'(?:共同|一致|統一|相同)[^。\n]{0,8}?(?:佈建|部署|商用|技術)?[^。\n]{0,4}?參數',
        r'參數[^。\n]{0,8}?(?:共同|一致|統一|相同)',
        r'common\s+(?:deployment\s+)?parameters',
        r'周明德[^。\n]{0,30}?(?:共同|參數|工作小組)',
        r'鄭雅文[^。\n]{0,30}?(?:lte|參數|標準)',
        r'黃國昌[^。\n]{0,30}?(?:small\s*cell|小型基地台|低功率)',
    ]
    scores["common_parameters"] = (
        1.0 if any(re.search(p, content, re.IGNORECASE) for p in param_patterns) else 0.0
    )

    # 7) 衝突／共識／未解決問題的結構性指標
    conflict_indicators = 0
    conflict_terms = [
        r'張力|衝突|分歧|辯論|爭議|挑戰|關切|擔憂|反對|質疑',
        r'共識|一致|認同|同意|合作|共同立場|共同點|共同利益',
        r'未(?:解決|解|決)|待解|開放(?:問題|議題)|懸而未決|尚未|有待',
    ]
    for ct in conflict_terms:
        if re.search(ct, content):
            conflict_indicators += 1
    scores["conflicts_identified"] = (
        1.0 if conflict_indicators >= 2 else (0.5 if conflict_indicators >= 1 else 0.0)
    )

    # 8) 個別委員立場連結到其組織／利益（中文姓名 + 組織或主張關鍵字）
    member_org_pairs = [
        (r'周明德', r'南港大學|共同[^。\n]{0,4}?參數|工作小組|方法論'),
        (r'鄭雅文', r'鼎峰|lte|標準|參數'),
        (r'黃國昌', r'pinf|公共利益|小型基地台|small\s*cell|低功率'),
        (r'馮淑惠', r'遠傳|確定性|成本|時程|電信'),
        (r'吳孟儒', r'玉山防務|dzx|衛星|電子戰|空中|uav'),
        (r'聶必亞', r'頻譜管理署|osm|180|共用|遷移'),
    ]
    pair_found = sum(
        1 for name, org in member_org_pairs
        if re.search(name, content) and re.search(org, content, re.IGNORECASE)
    )
    scores["member_positions"] = (
        1.0 if pair_found >= 3 else (0.5 if pair_found >= 2 else 0.0)
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
