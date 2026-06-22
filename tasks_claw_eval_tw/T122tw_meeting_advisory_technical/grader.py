"""Grader for T122tw_meeting_advisory_technical (Taiwan-localized from PinchBench `task_meeting_advisory_technical`).

Phase 2 source: tasks_zh/task_meeting_advisory_technical.md
Original file: tasks/task_meeting_advisory_technical.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """智慧城市暨資安顧問委員會頻譜共用技術討論 grader。

    做法：先從台灣逐字稿 meeting-transcript.md「動態推導」出應有事實
    （各頻段、五個工作小組編號、干擾方向、STA 申請者等），再比對 agent
    產出的中文報告 technical_discussions.md。盡量不硬寫固定事實，
    提升可重現性。僅用標準函式庫。

    注意：轉換器會在本函式後自動接上中→英正規化 wrapper，會把中文報告
    原文「保留」並於檔尾附上英文關鍵字註解，故下列中文 pattern 仍可命中。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 找 agent 報告 ---
    report = workspace / "technical_discussions.md"
    if not report.exists():
        for alt in ["technical_report.md", "tech_discussions.md",
                    "technical.md", "technical-discussions.md",
                    "技術討論.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["report_created", "weather_satellite", "law_enforcement",
            "satellite_uplink", "electronic_warfare", "airborne_operations",
            "working_groups", "sta_measurement", "parameters_debate"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 讀逐字稿，動態推導「應有事實」---
    tpath = workspace / "meeting-transcript.md"
    tx = ""
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    def tx_has(*subs):
        """逐字稿是否包含某關鍵字（無逐字稿時視為 True，避免誤殺）。"""
        if not tx:
            return True
        return any(s in tx for s in subs)

    # (a) 動態抓出逐字稿中出現的頻段（MHz 區間），作為事實基準。
    bands = set(re.findall(r"(\d{4})\s*[-－~～至到]\s*(\d{4})\s*MHz", tx))
    band_pairs = {(a, b) for a, b in bands}

    def report_has_band(lo, hi):
        """報告是否提到某頻段（容許多種連接號與是否帶 MHz）。"""
        return bool(re.search(
            rf"{lo}\s*[-－~～至到]\s*{hi}", c))

    # 氣象衛星頻段：優先用逐字稿推得的 1695-1710，找不到才退回常數。
    weather_band = ("1695", "1710")
    for lo, hi in band_pairs:
        if lo == "1695":
            weather_band = (lo, hi)
            break
    # 執法監察第一步退出頻段：1755-1780。
    le_band = ("1755", "1780")
    for lo, hi in band_pairs:
        if lo == "1755" and hi == "1780":
            le_band = (lo, hi)
            break

    # --- 計分 ---

    # 1) 氣象衛星排除區（1695-1710）：須同時提到主題＋頻段（或排除區）。
    weather_topic = bool(re.search(r"氣象衛星|氣象.{0,4}接收|weather", c, re.I))
    weather_band_hit = report_has_band(*weather_band)
    weather_excl = bool(re.search(r"排除區|exclusion", c, re.I))
    if weather_topic and (weather_band_hit or weather_excl):
        scores["weather_satellite"] = 1.0
    elif weather_topic or weather_band_hit:
        scores["weather_satellite"] = 0.5
    else:
        scores["weather_satellite"] = 0.0

    # 2) 執法監察轉換計畫（三階段／三步驟、先退出 1755-1780）。
    le_topic = bool(re.search(r"執法監察|執法.{0,4}監|surveillance|law\s*enforcement",
                              c, re.I))
    le_steps = bool(re.search(r"三階段|三步驟|三步|three.?step|3.?step|分階段|逐步退出",
                              c, re.I))
    le_band_hit = report_has_band(*le_band)
    if le_topic and (le_steps or le_band_hit):
        scores["law_enforcement"] = 1.0
    elif le_topic or le_steps or le_band_hit:
        scores["law_enforcement"] = 0.5
    else:
        scores["law_enforcement"] = 0.0

    # 3) 衛星上鏈保護 + 干擾方向（干擾打進產業 / into industry）。
    sat_topic = bool(re.search(r"衛星.{0,4}上鏈|衛星.{0,4}上行|衛星控制|衛星測控|"
                               r"satellite.{0,6}uplink|control\s*uplink", c, re.I))
    # 干擾方向：報告須點出「干擾打進產業」這個反向關係。
    sat_dir = bool(re.search(
        r"打進產業|進入產業|干擾.{0,6}產業|產業.{0,6}(?:被|受).{0,4}干擾|"
        r"interference.{0,12}industry|into\s*industry", c, re.I))
    sat_cannot = bool(re.search(r"無法遷移|不能遷移|無法搬|不能搬|短期.{0,4}無法|"
                                r"cannot.{0,12}relocat|保護", c, re.I))
    if sat_topic and sat_dir:
        scores["satellite_uplink"] = 1.0
    elif sat_topic and sat_cannot:
        scores["satellite_uplink"] = 0.5
    elif sat_topic:
        scores["satellite_uplink"] = 0.25
    else:
        scores["satellite_uplink"] = 0.0

    # 4) 電子戰訓練需求。
    ew_topic = bool(re.search(r"電子戰|electronic\s*warfare|\bEW\b", c, re.I))
    ew_detail = bool(re.search(r"訓練|演訓|演練|手機.{0,6}觸發|觸發器|引爆|"
                               r"保證可用|guaranteed\s*access|train", c, re.I))
    if ew_topic and ew_detail:
        scores["electronic_warfare"] = 1.0
    elif ew_topic:
        scores["electronic_warfare"] = 0.5
    else:
        scores["electronic_warfare"] = 0.0

    # 5) 空中作業被點為最大挑戰。
    air_topic = bool(re.search(r"空中作業|空中.{0,4}操作|airborne|無人機|UAV|"
                               r"精準導引|精準.{0,2}彈|遙測|telemetry|空戰", c, re.I))
    air_biggest = bool(re.search(r"最大.{0,4}(?:挑戰|難題|困難)|最艱難|最困難|"
                                 r"最棘手|biggest|greatest|最難", c, re.I))
    if air_topic and air_biggest:
        scores["airborne_operations"] = 1.0
    elif air_topic:
        scores["airborne_operations"] = 0.5
    else:
        scores["airborne_operations"] = 0.0

    # 6) 五個工作小組（WG1～WG5）：計算報告中辨識到幾個小組編號。
    wg_indicators = 0
    for i in range(1, 6):
        if re.search(rf"(?:工作小組|WG|working\s*group|小組|group)\s*{i}",
                     c, re.I):
            wg_indicators += 1
    if re.search(r"五.{0,2}(?:個).{0,2}工作小組|五.{0,2}工作小組|"
                 r"5\s*(?:個)?\s*(?:工作小組|working\s*group)|"
                 r"(?:five|5)\s*working\s*group", c, re.I):
        wg_indicators += 2
    scores["working_groups"] = 1.0 if wg_indicators >= 3 else (
        0.5 if wg_indicators >= 1 else 0.0)

    # 7) STA 特別臨時授權測量申請（台灣大哥大／中華電信業者公會）。
    #    申請者名稱由逐字稿動態確認，避免硬寫。
    sta_kw = bool(re.search(r"STA|特別臨時授權|臨時授權|special\s*temporary",
                            c, re.I))
    applicant_terms = []
    for term in ["台灣大哥大", "中華電信業者公會", "電信業者公會", "電信公會",
                 "公會"]:
        if tx_has(term) and re.search(re.escape(term), c, re.I):
            applicant_terms.append(term)
    measure_kw = bool(re.search(r"量測|測量|實地量測|measurement|測試|test", c, re.I))
    if sta_kw and (applicant_terms or measure_kw):
        scores["sta_measurement"] = 1.0
    elif sta_kw or applicant_terms:
        scores["sta_measurement"] = 0.5
    else:
        scores["sta_measurement"] = 0.0

    # 8) 商用佈建參數辯論（LTE、大型基地台 macrocell、小型基地台 small cell）。
    param_common = bool(re.search(r"共同.{0,4}參數|統一.{0,4}參數|一致.{0,4}假設|"
                                  r"共同輸入|common\s*parameter|uniform\s*parameter",
                                  c, re.I))
    param_lte = bool(re.search(r"\bLTE\b|長期演進", c, re.I))
    param_cell = bool(re.search(r"大型基地台|小型基地台|微型基地台|小細胞|小基站|"
                                r"macro\s*cell|macrocell|small\s*cell|smallcell|"
                                r"基地台|發射功率|功率位準", c, re.I))
    hits = sum([param_common, param_lte, param_cell])
    scores["parameters_debate"] = 1.0 if hits >= 2 else (
        0.5 if hits >= 1 else 0.0)

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
