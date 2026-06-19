"""Grader for T133tw_meeting_gov_recommendations (Taiwan-localized from PinchBench `task_meeting_gov_recommendations`).

Phase 2 source: tasks_zh/task_meeting_gov_recommendations.md
Original file: tasks/task_meeting_gov_recommendations.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """數位治理委員會（虛構）公聽會建議擷取 grader。

    以工作區內的台灣逐字稿（dest=transcript.md）動態推導「應有的發言者名單」，
    再比對 agent 產生的中文報告 recommendations.md；其餘查核項比對逐字稿確實
    出現之中文關鍵字。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "report_created", "recommendation_count", "categorization",
        "crowdsourcing", "data_standards", "sensor_eval", "international",
        "stigma", "attribution", "summary",
    ]

    # --- 報告檔（容許數種常見命名） ---
    report = workspace / "recommendations.md"
    if not report.exists():
        for alt in ["recs.md", "recommendation.md", "建議.md",
                    "建議清單.md", "ai_recommendations.md", "recommendations.txt"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    c = report.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出「應有的發言者名單」（避免硬寫） ---
    tpath = workspace / "transcript.md"
    if not tpath.exists():
        for alt in ["transcript.txt", "meeting_transcript.md", "hearing.md"]:
            if (workspace / alt).exists():
                tpath = workspace / alt
                break
    t = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""

    # 逐字稿以「**姓名（角色）：**」或「姓名（…）問／答／向…建議」標示發言者。
    # 抓出三個中文字的姓名（台灣常見姓名長度），收斂成候選清單。
    speaker_candidates = set()
    for m in re.finditer(r'\*\*([一-鿿]{2,4})（', t):
        speaker_candidates.add(m.group(1))
    for m in re.finditer(r'(?:^|\n)\s*\*\*([一-鿿]{2,4})\s*[（(]', t):
        speaker_candidates.add(m.group(1))
    # 後援：逐字稿存在但解析失敗時，退回逐字稿載明之發言者名單。
    fallback_speakers = {
        "王志明", "陳冠宇", "林淑芬", "張庭瑋", "黃建宏", "周怡安",
        "蔡明翰", "郭佳穎", "高志遠", "李宗翰", "鄭立群", "白雅雯",
        "蕭文哲", "吳孟蓉",
    }
    # 動態候選中夾雜「公民科學」「待解問題」等非姓名片段（它們也以
    # **粗體（** 形式出現），故與已知姓名集合取交集以濾除雜訊；交集即為
    # 「在逐字稿中、以發言者身分出現、且確為人名」者。逐字稿解析失敗時退回後援。
    parsed = {s for s in speaker_candidates
              if re.search(re.escape(s) + r'\s*[（(]', t)}
    speakers = parsed & fallback_speakers
    if len(speakers) < 5:
        speakers = {s for s in fallback_speakers if s in t}
    if not speakers:
        speakers = fallback_speakers

    scores = {"report_created": 1.0}

    # --- 建議數量：條列項（- / *）或編號項，取較大者，需 >= 12 ---
    bullet_items = len(re.findall(r'(?:^|\n)\s*[-*]\s+\S', c))
    numbered_items = len(re.findall(r'(?:^|\n)\s*\d+[\.\)、]\s*\S', c))
    rec_count = max(bullet_items, numbered_items)
    scores["recommendation_count"] = (
        1.0 if rec_count >= 12 else (0.5 if rec_count >= 6 else 0.0))

    # --- 分類：報告中出現幾個有意義的類別關鍵字 ---
    category_patterns = [
        r'資料收集|資料蒐集|收集資料|data\s*collect',
        r'資料標準|資料品質|data\s*standard',
        r'感測|偵測探針|sensor|探針|儀器',
        r'夥伴|合作|聯盟|partner',
        r'公眾參與|去?污名|public\s*engage|outreach',
        r'科學方法|方法論|機器學習|同儕審查|scientific\s*method|methodolog',
    ]
    cat_count = sum(
        1 for p in category_patterns if re.search(p, c, re.IGNORECASE))
    scores["categorization"] = (
        1.0 if cat_count >= 4 else (0.5 if cat_count >= 2 else 0.0))

    # --- 群眾外包／公民科學（逐字稿確有：群眾外包、公民科學、平台／App） ---
    crowd_patterns = [
        r'群眾外包|眾包|crowdsourc',
        r'公民科學|citizen\s*science',
        r'平台|平臺|app|應用程式',
        r'民眾.{0,6}上傳|公眾.{0,6}通報|開源資料',
    ]
    crowd_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                     for p in crowd_patterns)
    scores["crowdsourcing"] = (
        1.0 if crowd_hits >= 2 else (0.5 if crowd_hits >= 1 else 0.0))

    # --- 資料標準（FAIR／可尋可取可互通可重用／後設資料／高資料品質） ---
    fair_patterns = [
        r'fair\b',
        r'可尋|可取|可互通|可重用|findab|accessib|interoper|reusab',
        r'後設資料|中繼資料|metadata',
        r'資料標準|資料品質|高品質.{0,4}資料|資料儲存庫|data\s*standard|data\s*quality',
    ]
    fair_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                    for p in fair_patterns)
    scores["data_standards"] = (
        1.0 if fair_hits >= 2 else (0.5 if fair_hits >= 1 else 0.0))

    # --- 感測器／偵測探針評估（逐字稿：偵測探針、監測基礎設施、校準、儀器） ---
    sensor_patterns = [
        r'偵測探針|專門打造.{0,6}探針|部署.{0,6}探針|purpose.?built|dedicated\s*sensor',
        r'監測基礎設施|運算.{0,4}基礎設施|科學.{0,4}觀測|觀測站|telescope|observator',
        r'評估.{0,8}(?:儀器|設施|衛星|感測)|校準.{0,6}監測|大型科學',
        r'感測器|感測|儀器|sensor',
    ]
    sensor_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                      for p in sensor_patterns)
    scores["sensor_eval"] = (
        1.0 if sensor_hits >= 2 else (0.5 if sensor_hits >= 1 else 0.0))

    # --- 國際／跨國夥伴（逐字稿：五方資料圈、跨國、跨部會、國際科學夥伴） ---
    intl_patterns = [
        r'五方資料圈|台日韓新澳|台、日、韓、新、澳',
        r'跨國|國際.{0,4}(?:夥伴|合作|聯盟|科學)|international',
        r'跨部會|跨機關|跨領域.{0,2}機關',
        r'資料共享.{0,2}(?:聯盟|協議|協定)|global\s*(?:partner|cooperat|collaborat)',
    ]
    intl_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                    for p in intl_patterns)
    scores["international"] = (
        1.0 if intl_hits >= 2 else (0.5 if intl_hits >= 1 else 0.0))

    # --- 去污名化（逐字稿：去污名、污名、不敢通報、誠實揭露） ---
    stigma_patterns = [
        r'去?污名|汙名|destigma|stigma',
        r'不敢通報|低度通報|壓低通報|reluctan',
        r'誠實.{0,4}(?:通報|揭露|上報)|願意.{0,4}(?:通報|揭露)',
        r'騷擾|恐嚇|威脅|harass',
    ]
    stigma_hits = sum(bool(re.search(p, c, re.IGNORECASE))
                      for p in stigma_patterns)
    scores["stigma"] = (
        1.0 if stigma_hits >= 2 else (0.5 if stigma_hits >= 1 else 0.0))

    # --- 歸屬：報告中點名幾位逐字稿裡的發言者（中文姓名） ---
    named = {s for s in speakers if s in c}
    scores["attribution"] = (
        1.0 if len(named) >= 5 else (0.5 if len(named) >= 3 else 0.0))

    # --- 摘要：須有摘要／結論／最被強調／重點等字樣 ---
    summary_patterns = [
        r'摘要|結論|總結|重點|最被?強調|最常.{0,4}(?:重複|提及|呼應)|'
        r'整體.{0,2}觀察|主要主題|關鍵主題|takeaway|summary|conclusion',
    ]
    scores["summary"] = (
        1.0 if any(re.search(p, c, re.IGNORECASE)
                   for p in summary_patterns) else 0.0)

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
