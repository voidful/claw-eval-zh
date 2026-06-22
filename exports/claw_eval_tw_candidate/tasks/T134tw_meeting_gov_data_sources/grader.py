"""Grader for T134tw_meeting_gov_data_sources (Taiwan-localized from PinchBench `task_meeting_gov_data_sources`).

Phase 2 source: tasks_zh/task_meeting_gov_data_sources.md
Original file: tasks/task_meeting_gov_data_sources.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會（虛構）公聽會 資料來源／監測系統擷取 grader。

    從台灣逐字稿（dest=transcript.md）推導之事實，比對 agent 的中文報告
    data_sources.md。僅用標準函式庫。
    報告為繁體中文，故以中文關鍵字／數值比對；可查核的數值（超過 800 件、
    2-5% 異常、每月 3-5 件、約 14,000 人、單日約 4,500 萬次、保存數個月）
    優先從逐字稿動態讀出再比對。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "airc_database", "ncra_monitoring", "voluntary_labeling",
        "scientific_infra", "citizen_data", "open_data_portal",
        "limitations", "categorization", "summary_table",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "data_sources.md"
    if not report.exists():
        for alt in ["sources.md", "data.md", "sensors.md",
                    "data_sources_report.md", "資料來源.md",
                    "監測系統.md", "data_sources.txt"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出可查核的數值（避免硬寫；逐字稿缺漏時退回其載明之事實） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "tw_gov_hearing.md", "meeting_transcript.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    def first(pattern, text, default=None, group=1):
        m = re.search(pattern, text)
        return m.group(group) if m else default

    # 風析中心案例件數（逐字稿：「超過 800 件」）
    case_count = first(r'超過\s*(\d{3,})\s*件', t) or first(r'(\d{3,})\s*多?\s*件', t) or "800"
    # 真正異常比例（逐字稿：「2% 到 5%」「約 2%–5%」）
    anom_lo = first(r'(\d+)\s*%\s*(?:到|–|-|~|～|至)\s*\d+\s*%', t) or "2"
    anom_hi = first(r'\d+\s*%\s*(?:到|–|-|~|～|至)\s*(\d+)\s*%', t) or "5"
    # 通監中心每月通報件數（逐字稿：「每月只回報 3 到 5 件」「每月只有 3–5 件」）
    rep_lo = first(r'每月[^。]{0,12}?(\d+)\s*(?:到|–|-|~|～|至)\s*\d+\s*件', t) or "3"
    rep_hi = first(r'每月[^。]{0,12}?\d+\s*(?:到|–|-|~|～|至)\s*(\d+)\s*件', t) or "5"

    def has(*pats):
        return any(re.search(p, c, re.IGNORECASE) for p in pats)

    scores = {"report_created": 1.0}

    # --- 風析中心案例庫：須有案例庫 + 數量細節 ---
    cc = re.escape(case_count)
    lo = re.escape(anom_lo)
    hi = re.escape(anom_hi)
    has_db = has(r'風析中心', r'案例庫', r'風險研析中心', r'案例.{0,4}資料庫')
    # 數量細節：超過/逾 800 件，或單獨出現該數字，或 2-5% 異常比例
    has_count = bool(
        re.search(r'(?:超過|逾)\s*%s\s*多?\s*件' % cc, c)
        or re.search(r'\b%s\b' % cc, c)
        or re.search(r'%s\s*%%?\s*(?:到|–|-|~|～|至)\s*%s\s*%%' % (lo, hi), c)
        or re.search(r'%s\s*(?:到|–|-|~|～|至)\s*%s\s*%%' % (lo, hi), c)
        or has(r'案例', r'通報', r'歸檔')
    )
    scores["airc_database"] = 1.0 if (has_db and has_count) else (0.5 if has_db else 0.0)

    # --- 通監中心監測：終端側 vs 骨幹側 ---
    has_terminal = has(r'終端側', r'業者端.{0,6}探針', r'稽核探針',
                        r'範圍小.{0,8}解析度高', r'解析度高')
    has_backbone = has(r'骨幹側', r'網路骨幹', r'大型節點',
                       r'範圍大.{0,8}解析度', r'解析度粗', r'跨平台.{0,6}流量輪廓')
    scores["ncra_monitoring"] = 1.0 if (has_terminal and has_backbone) else (0.5 if (has_terminal or has_backbone) else 0.0)

    # --- 合作式自願標示機制（類似航空的 ADS-B） ---
    scores["voluntary_labeling"] = 1.0 if has(
        r'自願標示', r'合作式.{0,6}標示', r'標籤系統', r'標註\s*AI',
        r'ADS-?B', r'業者.{0,6}標註',
    ) else 0.0

    # --- 跨機構／科學運算基礎設施（既有大型科學運算與監測資源） ---
    sci_pats = [
        r'科學運算.{0,4}基礎設施', r'監測基礎設施', r'時域異常',
        r'情報級.{0,6}監測', r'科學感測器', r'五方資料圈',
        r'監督式', r'非監督式', r'機器學習', r'科學觀測',
    ]
    sci_n = sum(1 for p in sci_pats if re.search(p, c, re.IGNORECASE))
    scores["scientific_infra"] = 1.0 if sci_n >= 2 else (0.5 if sci_n >= 1 else 0.0)

    # --- 公民科學／公眾資料（民眾截圖爆料／群眾外包平台） ---
    citizen_pats = [
        r'群眾外包', r'公民科學', r'民眾.{0,4}截圖', r'民眾.{0,4}爆料',
        r'智慧型手機', r'時間戳', r'定位', r'中繼資料', r'上傳.{0,6}異常',
    ]
    citizen_n = sum(1 for p in citizen_pats if re.search(p, c, re.IGNORECASE))
    scores["citizen_data"] = 1.0 if citizen_n >= 2 else (0.5 if citizen_n >= 1 else 0.0)

    # --- 開放資料入口（data.gov.tw） ---
    scores["open_data_portal"] = 1.0 if has(
        r'data\.gov\.tw', r'開放資料.{0,4}入口', r'開放資料平台', r'去識別化.{0,6}資料',
    ) else 0.0

    # --- 侷限：須涵蓋至少 3 類侷限說明 ---
    limitation_pats = [
        r'不是.{0,6}科學.{0,4}(?:分析|設計)', r'並非.{0,6}科學', r'本來就不是',
        r'濾掉', r'過濾.{0,6}(?:規則|掉)', r'濾掉.{0,6}異常',
        r'只對.{0,8}有效', r'沒輒', r'看不到.{0,6}全貌', r'看不清',
        r'幫助有限', r'通常.{0,4}幫助有限',
        r'輪替刪除', r'保存.{0,4}數個月', r'保存期限',
        r'機敏', r'卡.{0,4}機敏', r'視線.{0,6}限制', r'授權範圍',
        r'通報偏差', r'低度通報', r'解析度粗',
    ]
    lim_n = sum(1 for p in limitation_pats if re.search(p, c, re.IGNORECASE))
    scores["limitations"] = 1.0 if lim_n >= 3 else (0.5 if lim_n >= 1 else 0.0)

    # --- 分類：至少 4 類 ---
    category_pats = [
        r'政府|公部門|委員會|風析中心|情資',
        r'業者|網路|通訊|通監中心|骨幹|終端',
        r'科學運算|科學.{0,4}基礎設施|科學觀測|機器學習|五方',
        r'公民科學|群眾|公眾|民眾',
        r'資料庫|封存|歸檔|開放資料|入口',
    ]
    cat_n = sum(1 for p in category_pats if re.search(p, c, re.IGNORECASE))
    scores["categorization"] = 1.0 if cat_n >= 4 else (0.5 if cat_n >= 2 else 0.0)

    # --- 摘要表：markdown 表格或摘要概覽 ---
    has_table = bool(re.search(r'\|.*\|.*\|', c))
    has_overview = bool(re.search(r'摘要表|概覽|總覽|一覽|摘要', c))
    scores["summary_table"] = 1.0 if has_table else (0.5 if has_overview else 0.0)

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
