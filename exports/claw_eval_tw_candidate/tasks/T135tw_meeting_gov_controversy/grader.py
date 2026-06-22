"""Grader for T135tw_meeting_gov_controversy (Taiwan-localized from PinchBench `task_meeting_gov_controversy`).

Phase 2 source: tasks_zh/task_meeting_gov_controversy.md
Original file: tasks/task_meeting_gov_controversy.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會公聽會（虛構）爭議性發言分析 grader。

    以工作區內的台灣逐字稿（dest=transcript.md）動態推導「應有事實」
    （異常比例、每月通報件數、案例庫規模、具名發言者等），再比對 agent 產生的
    中文報告 controversy_analysis.md。共九個查核項，皆改查
    台灣逐字稿推導之事實。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "harassment", "anomalous_pct", "no_autonomy_evidence",
        "classified_tension", "non_scientific_sensors", "debunked_case",
        "audience_perspectives", "tone_analysis",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "controversy_analysis.md"
    if not report.exists():
        for alt in ["controversies.md", "notable_statements.md", "controversy.md",
                    "controversial.md", "爭議分析.md", "爭議性發言.md",
                    "controversy_analysis.txt"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")
    c_low = c.lower()

    # --- 從逐字稿動態讀出可查核事實（避免硬寫英文原版） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "meeting_transcript.md", "逐字稿.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def first(pattern, text, default=None, group=1):
        m = re.search(pattern, text)
        return m.group(group) if m else default

    # 真正異常比例：逐字稿「2% 到 5%」/「2%–5%」/「2%-5%」
    pct_lo = first(r'(\d+)\s*%\s*(?:到|–|-|~|至)\s*\d+\s*%', t) or "2"
    pct_hi = first(r'\d+\s*%\s*(?:到|–|-|~|至)\s*(\d+)\s*%', t) or "5"

    scores = {"report_created": 1.0}

    # --- 1) 網路騷擾／恐嚇／威脅 ---
    harass_patterns = [r'騷擾', r'恐嚇', r'威脅', r'霸凌']
    n_harass = sum(bool(re.search(p, c)) for p in harass_patterns)
    scores["harassment"] = (
        1.0 if n_harass >= 2
        else 0.5 if n_harass >= 1
        else 0.0)

    # --- 2) 2%–5% 真正異常比例 ---
    pct_pat = r'%s\s*[%%％]?\s*(?:到|–|-|~|至|—)\s*%s\s*[%%％]' % (
        re.escape(pct_lo), re.escape(pct_hi))
    has_pct_range = bool(re.search(pct_pat, c)) or (
        bool(re.search(r'%s\s*[%%％]' % re.escape(pct_lo), c))
        and bool(re.search(r'%s\s*[%%％]' % re.escape(pct_hi), c)))
    has_anomaly_word = bool(re.search(r'異常|難以.*解釋|未知', c))
    scores["anomalous_pct"] = (
        1.0 if (has_pct_range and has_anomaly_word)
        else 0.5 if has_pct_range
        else 0.0)

    # --- 3) 並無自主意圖／非人類智慧的決定性證據 ---
    ev_patterns = [
        r'(?:沒有|並無|無)(?:任何)?決定性(?:的)?證據',
        r'非凡的?(?:主張|證據)',
        r'(?:沒有|並無|無).*(?:自主意圖|非人類(?:的)?(?:智慧|智能))',
        r'尚未.*(?:非凡|決定性).*證據',
    ]
    n_ev = sum(bool(re.search(p, c)) for p in ev_patterns)
    scores["no_autonomy_evidence"] = (
        1.0 if n_ev >= 1
        else 0.0)

    # --- 4) 機敏分級造成的資料侷限 ---
    class_patterns = [
        r'機敏.*(?:系統|平台|分級|資料)|(?:系統|平台|感測).*機敏',
        r'(?:事故|描述).*非機敏|非機敏.*(?:事故|描述)',
        r'自由女神|戰機.*感測|感測.*戰機',
        r'無法取得.*機敏|機敏.*無法取得',
    ]
    n_class = sum(bool(re.search(p, c)) for p in class_patterns)
    scores["classified_tension"] = (
        1.0 if n_class >= 1
        else 0.5 if re.search(r'機敏|機密|機密分級', c)
        else 0.0)

    # --- 5) 監測系統「並非為科學分析設計」 ---
    sensor_patterns = [
        r'(?:不是|並非|並不是).*(?:為了)?.*科學(?:分析)?.*設計',
        r'(?:辨識|阻斷|反制).*威脅|威脅.*(?:辨識|阻斷|反制)',
        r'(?:資安|情資|軍用|監測).*(?:系統|感測).*(?:不是|並非).*科學',
        r'(?:不是|並非).*(?:精確量測|可重現)',
    ]
    n_sensor = sum(bool(re.search(p, c)) for p in sensor_patterns)
    scores["non_scientific_sensors"] = (
        1.0 if n_sensor >= 1
        else 0.5 if re.search(r'(?:資安|情資|軍用|監測)(?:系統|感測)', c)
        else 0.0)

    # --- 6) 被誤判／被破解的案例 ---
    debunk_patterns = [
        r'(?:自動化)?測試流量',
        r'誤判',
        r'(?:記錄|紀錄)系統假影|假影',
        r'排程',
        r'(?:對話)?(?:紀錄|記錄).*(?:刪除|刪光|湮滅)',
        r'並(?:不|非).*自主行為|實際上是|其實是',
    ]
    n_debunk = sum(bool(re.search(p, c)) for p in debunk_patterns)
    scores["debunked_case"] = (
        1.0 if n_debunk >= 2
        else 0.5 if n_debunk >= 1
        else 0.0)

    # --- 7) 多受眾視角 ---
    audience_patterns = [
        r'科學(?:家|界|社群)|研究(?:者|員|界)|學界',
        r'(?:一般)?(?:公眾|民眾|大眾)',
        r'媒體|記者|新聞',
        r'(?:ai|人工智慧|科技|陰謀論)\s*(?:社群|圈|愛好者|支持者)|相信者',
        r'業者|產業|廠商|企業',
        r'(?:懷疑|質疑)(?:者|論)',
    ]
    aud_count = sum(1 for p in audience_patterns if re.search(p, c_low))
    scores["audience_perspectives"] = (
        1.0 if aud_count >= 3
        else 0.5 if aud_count >= 2
        else 0.0)

    # --- 8) 語氣／框架分析 ---
    tone_patterns = [
        r'語氣', r'框架|框定', r'(?:選擇|刻意).*(?:強調|迴避|淡化|保留|不(?:談|說))',
        r'(?:謹慎|小心|委婉|外交)(?:的)?(?:平衡|措辭|態度|語言)?',
        r'去污名|污名', r'敘事|訊息(?:傳遞|策略)|定調', r'強調.*(?:資料品質|可重現)',
    ]
    n_tone = sum(bool(re.search(p, c)) for p in tone_patterns)
    scores["tone_analysis"] = (
        1.0 if n_tone >= 2
        else 0.5 if n_tone >= 1
        else 0.0)

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
