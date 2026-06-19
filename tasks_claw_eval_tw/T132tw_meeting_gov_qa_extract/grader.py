"""Grader for T132tw_meeting_gov_qa_extract (Taiwan-localized from PinchBench `task_meeting_gov_qa_extract`).

Phase 2 source: tasks_zh/task_meeting_gov_qa_extract.md
Original file: tasks/task_meeting_gov_qa_extract.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會公聽會（虛構）問答擷取 grader。

    以工作區內的台灣逐字稿（dest=transcript.md）動態推導「應有事實」
    （案例數、異常比例、發言者名單、NCRA 監測等），再比對 agent 產生的
    中文報告 qa_exchanges.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "qa_exchanges.md"
    if not report.exists():
        for alt in ["qa.md", "questions_answers.md", "q_and_a.md",
                    "qa_extract.md", "qa_exchanges.txt", "問答交流.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = [
        "report_created", "exchange_count", "section_separation",
        "case_numbers_qa", "case_stats", "ncra_qa", "nhi_question",
        "attribution", "numbering",
    ]
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

    # 案例庫規模：逐字稿「超過 800 件」/「800 多件」
    case_total = first(r'(?:超過|逾)?\s*(\d{3,})\s*多?\s*件', t) or "800"
    # 真正異常比例：逐字稿「2% 到 5%」/「2%–5%」/「2%-5%」
    pct_lo = first(r'(\d+)\s*%\s*(?:到|–|-|~|至)\s*\d+\s*%', t) or "2"
    pct_hi = first(r'\d+\s*%\s*(?:到|–|-|~|至)\s*(\d+)\s*%', t) or "5"
    # NCRA 第一線每月通報件數：逐字稿「每月只回報 3 到 5 件」
    rep_lo = first(r'每月只?\s*回?報\s*(\d+)\s*(?:到|–|-|~|至)\s*\d+\s*件', t) or "3"
    rep_hi = first(r'每月只?\s*回?報\s*\d+\s*(?:到|–|-|~|至)\s*(\d+)\s*件', t) or "5"

    scores = {"report_created": 1.0}

    # --- 交流筆數：報告中編號項或問答區塊／提問者標記 ≥ 10 ---
    numbered = re.findall(r'(?:^|\n)\s*(?:\d+\s*[.\):、]|第\s*\d+\s*(?:筆|題|案|則))', c)
    headed = re.findall(
        r'(?:^|\n)#{2,4}\s*.*?(?:交流|問答|q\s*&?\s*a|提問|exchange)', c_low)
    qmark = re.findall(r'提問者|回答者|提問|問\s*[:：]|q\s*[:：]', c_low)
    n_units = max(len(numbered), len(headed))
    scores["exchange_count"] = (
        1.0 if (n_units >= 10 or len(qmark) >= 10)
        else 0.5 if (n_units >= 5 or len(qmark) >= 5)
        else 0.0)

    # --- 區段分隔：須同時出現「小組問答」與「公眾問答」兩類標記 ---
    has_panel = bool(re.search(r'小組問答|小組\s*提問|報告者|小組成員', c))
    has_public = bool(re.search(r'公眾問答|公眾\s*提問|public\s*q', c_low)
                      or re.search(r'公眾問答|公眾\s*提問', c))
    scores["section_separation"] = (
        1.0 if (has_panel and has_public)
        else 0.5 if (has_panel or has_public)
        else 0.0)

    # --- 周怡安 ↔ 張庭瑋 案例庫數字問答：須點名雙方且問及規模／年數／數量 ---
    has_zhou = bool(re.search(r'周怡安', c))
    has_zhang = bool(re.search(r'張庭瑋', c))
    ask_size = bool(re.search(r'多大|多少|規模|案例庫|資料庫|幾年|涵蓋', c))
    scores["case_numbers_qa"] = (
        1.0 if (has_zhou and has_zhang and ask_size)
        else 0.5 if (has_zhou and has_zhang)
        else 0.0)

    # --- 案例庫統計事實：報告須含逐字稿推導之 800 件 與 2%–5% 異常比例 ---
    # 800（容許「超過 800」「800 多」「800 件」等）
    has_total = bool(re.search(r'%s' % re.escape(case_total), c))
    # 2%–5%（容許 2%~5%、2-5%、2% 到 5%、2％至5％ 等寫法）
    pct_pat = r'%s\s*[%%％]?\s*(?:到|–|-|~|至|—)\s*%s\s*[%%％]' % (
        re.escape(pct_lo), re.escape(pct_hi))
    has_pct = bool(re.search(pct_pat, c)) or (
        bool(re.search(r'%s\s*[%%％]' % re.escape(pct_lo), c))
        and bool(re.search(r'%s\s*[%%％]' % re.escape(pct_hi), c)))
    scores["case_stats"] = (
        1.0 if (has_total and has_pct)
        else 0.5 if (has_total or has_pct)
        else 0.0)

    # --- NCRA／黃建宏 相關問答：須點名黃建宏或 NCRA，且至少觸及兩個 NCRA 主題 ---
    has_ncra = bool(re.search(r'黃建宏|ncra|國家通訊傳播監理署', c, re.IGNORECASE))
    ncra_topics = sum([
        # 原始資料保存／輪替刪除
        bool(re.search(r'保存|輪替|刪除|數個月|原始(?:流量|資料|紀錄)', c)),
        # 探針部署／涵蓋／長尾
        bool(re.search(r'探針|部署|涵蓋|長尾|高流量節點', c)),
        # 通報偏差
        bool(re.search(r'通報偏差|偏差', c)),
        # 每月 3–5 件 通報量
        bool(re.search(
            r'%s\s*(?:到|–|-|~|至)\s*%s\s*件' % (
                re.escape(rep_lo), re.escape(rep_hi)), c)
            or re.search(r'每月.{0,6}件', c)),
    ])
    scores["ncra_qa"] = (
        1.0 if (has_ncra and ncra_topics >= 2)
        else 0.5 if has_ncra
        else 0.0)

    # --- 非人類智慧／自主意圖 公眾提問：至少命中兩個關鍵概念 ---
    nhi_hits = sum([
        bool(re.search(r'非人類(?:的)?(?:智慧|智能)', c)),
        bool(re.search(r'自主(?:意圖|意識|智慧)', c)),
        bool(re.search(r'外星', c)),
        bool(re.search(r'非凡的?(?:主張|證據)', c)),
        bool(re.search(r'(?:沒有|無)決定性(?:的)?證據', c)),
    ])
    scores["nhi_question"] = (
        1.0 if nhi_hits >= 2
        else 0.5 if nhi_hits >= 1
        else 0.0)

    # --- 歸屬：逐字稿中的具名發言者，報告須命中 ≥ 6 位 ---
    # 動態從逐字稿擷取「**姓名（…）：**」或「姓名 問／答」的中文人名作參考，
    # 並輔以一份逐字稿確有的具名發言者清單交集，避免空集合。
    roster = set(re.findall(r'([一-鿿]{2,3})（[^）]*?(?:委員|主任|秘書|'
                            r'學者|記者|專家|研究員|長|顧問|召集人|科學家|'
                            r'監理|代表)', t))
    known = ["陳冠宇", "林淑芬", "蔡明翰", "李宗翰", "張庭瑋", "周怡安",
             "蕭文哲", "白雅雯", "黃建宏", "郭佳穎", "吳孟蓉", "鄭立群",
             "高志遠", "王志明"]
    roster |= {k for k in known if k in t}
    named = {nm for nm in roster if nm in c}
    scores["attribution"] = (
        1.0 if len(named) >= 6
        else 0.5 if len(named) >= 3
        else 0.0)

    # --- 編號／分隔：報告須有清楚的編號、標題或分隔線 ---
    n_numbered = len(re.findall(
        r'(?:^|\n)\s*(?:\d+\s*[.\):、]|第\s*\d+\s*(?:筆|題|案|則))', c))
    n_headed = len(re.findall(r'(?:^|\n)#{2,4}\s', c))
    n_sep = len(re.findall(r'(?:^|\n)---', c))
    scores["numbering"] = (
        1.0 if (n_numbered >= 5 or n_headed >= 5)
        else 0.5 if n_sep >= 3
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
