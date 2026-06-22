"""Grader for T130tw_meeting_searchable_index (Taiwan-localized from PinchBench `task_meeting_searchable_index`).

Phase 2 source: tasks_zh/task_meeting_searchable_index.md
Original file: tasks/task_meeting_searchable_index.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """鼎峰科技產品週會「可檢索索引」grader。

    做法：先從台灣逐字稿 meeting_transcript.md「動態推導」應有事實
    （日期、與會者姓名、各主題／競品關鍵字、決議與行動項目線索），再比對
    agent 產出的中文索引 meeting_index.md。盡量不硬寫死特定事實，
    提升可重現性。僅用標準函式庫。

    本任務的八項查核：
      file_created / metadata_present / topic_index / people_index /
      keyword_index / decisions_log / action_items_log / organized
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 找 agent 的索引報告 ---
    report = workspace / "meeting_index.md"
    if not report.exists():
        for alt in ["index.md", "searchable_index.md",
                    "meeting_searchable_index.md", "會議索引.md", "索引.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = ["file_created", "metadata_present", "topic_index",
            "people_index", "keyword_index", "decisions_log",
            "action_items_log", "organized"]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"file_created": 1.0}
    c = report.read_text(encoding="utf-8", errors="ignore")
    c_low = c.lower()

    # --- 讀逐字稿，動態推導「應有事實」---
    tpath = workspace / "meeting_transcript.md"
    tx = ""
    if tpath.exists():
        tx = tpath.read_text(encoding="utf-8", errors="ignore")

    # (a) 日期：從逐字稿動態抓 YYYY-MM-DD（會議的「日期：…」那行）
    date_str = ""
    md = re.search(r"日期[：:]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", tx) if tx else None
    if not md and tx:
        md = re.search(r"(20[0-9]{2}-[0-9]{2}-[0-9]{2})", tx)
    if md:
        date_str = md.group(1)
    if not date_str:
        date_str = "2025-03-18"

    # (b) 與會者姓名：從逐字稿「與會者」清單抓中文姓名（2–3 字，後接全形括號）。
    #     例：「- 王志明（產品行銷負責人…」
    names = []
    for nm in re.findall(r"[-*]\s*([一-鿿]{2,3})（", tx):
        if nm not in names:
            names.append(nm)
    # 後備：抓「行動項目：<姓名>…」裡的人名與全文常見人名
    if len(names) < 3 and tx:
        for nm in re.findall(r"行動項目[：:]\s*([一-鿿]{2,3})", tx):
            if nm not in names:
                names.append(nm)
    # 再後備：最小已知集合（理論上不會用到）
    if len(names) < 3:
        names = ["王志明", "林淑芬", "高敏哲", "陳柏宇", "蔡思敏", "戴立安"]

    # (c) 競品名稱：從逐字稿 tier 1 清單動態抓（編號 1.–6. 的 **粗體** 名稱）。
    competitors = []
    for nm in re.findall(r"\d+\.\s*\*\*([^*]{2,12})\*\*", tx):
        nm = nm.strip()
        if nm and nm not in competitors:
            competitors.append(nm)
    # 過濾掉太長或明顯非競品的字串，僅保留合理競品名稱
    competitors = [x for x in competitors if len(x) <= 8]

    # (d) 主標語：會議結尾複習句「…訊息主標語『更快交付，更低風險』」。
    tagline = ""
    mt = re.search(r"主標語[，、\s]*[「『]([^」』]{2,20})[」』]", tx) if tx else None
    if not mt and tx:
        mt = re.search(r"[「『]([^」』]{2,20})[」』]\s*當主標語", tx)
    if mt:
        tagline = mt.group(1)
    if not tagline:
        tagline = "更快交付，更低風險"

    # === 1) metadata_present：日期 + 至少 3 位與會者姓名 ===
    has_date = bool(date_str and date_str in c)
    names_found = sum(1 for n in names if n in c)
    if has_date and names_found >= 3:
        scores["metadata_present"] = 1.0
    elif has_date or names_found >= 2:
        scores["metadata_present"] = 0.5
    else:
        scores["metadata_present"] = 0.0

    # === 2) topic_index：至少 5 個主題 ===
    # 優先在「主題索引／議程／討論主題」段落底下數編號或條列項目。
    topic_count = 0
    ts = re.search(
        r"#+\s*[^\n]*(?:主題索引|議程|討論主題|topic\s*index)[^\n]*\n(.*?)"
        r"(?=\n#{1,6}\s|\Z)", c, re.DOTALL | re.IGNORECASE)
    if ts:
        body = ts.group(1)
        topic_count = len(re.findall(
            r"(?:^|\n)\s*(?:\d+[.)、]|[-*+•])\s+\S", body))
    if topic_count == 0:
        # 後備：全文找編號清單（看起來像主題敘述，≥4 字）
        topic_count = len(re.findall(
            r"\n\s*\d+[.)、]\s+\S{4,}", c))
    scores["topic_index"] = (
        1.0 if topic_count >= 5 else (0.5 if topic_count >= 3 else 0.0))

    # === 3) people_index：至少 3 位具名人士且有貢獻描述 ===
    # 條件：姓名後接冒號/破折號再接內容，或姓名出現在條列項目開頭。
    people_hit = []
    for nm in names:
        if re.search(rf"{re.escape(nm)}\s*[：:、\-—–]\s*\S{{4,}}", c):
            people_hit.append(nm)
        elif re.search(rf"(?:^|\n)\s*[-*+•]\s*\**{re.escape(nm)}\**", c):
            people_hit.append(nm)
    people_hit = list(dict.fromkeys(people_hit))
    scores["people_index"] = (
        1.0 if len(people_hit) >= 3 else (0.5 if len(people_hit) >= 2 else 0.0))

    # === 4) keyword_index：至少 10 個術語 ===
    # 先在關鍵字段落數條列項目。
    kw_count = 0
    ks = re.search(
        r"#+\s*[^\n]*(?:關鍵字|關鍵詞|術語|詞彙|名詞|keyword)[^\n]*\n(.*?)"
        r"(?=\n#{1,6}\s|\Z)", c, re.DOTALL | re.IGNORECASE)
    if ks:
        kw_count = len(re.findall(
            r"(?:^|\n)\s*(?:[-*+•]|\d+[.)、])\s+\S", ks.group(1)))
    # 再用「逐字稿推導的關鍵術語是否出現在報告」交叉查核並取較大值。
    key_terms = ["COSCUP", "DevOpsDays", "Kubernetes Day", "匯流大會",
                 "漏洞管理", "GitOps", "流水線編輯器", "史詩看板",
                 "里程碑燃盡圖", "資訊圖", "tier 1", "VS Code",
                 "Terraform", "模糊測試", "價值流", "事件管理"]
    # 動態補入逐字稿抓到的競品名稱與主標語
    key_terms = key_terms + competitors + [tagline]
    terms_found = 0
    seen_t = set()
    for t in key_terms:
        tl = t.lower()
        if tl in seen_t:
            continue
        seen_t.add(tl)
        if tl in c_low:
            terms_found += 1
    kw_count = max(kw_count, terms_found)
    scores["keyword_index"] = (
        1.0 if kw_count >= 10 else (0.5 if kw_count >= 5 else 0.0))

    # === 5) decisions_log：至少 3 項決議 ===
    dec_count = 0
    ds = re.search(
        r"#+\s*[^\n]*(?:決議|決定|decision)[^\n]*\n(.*?)"
        r"(?=\n#{1,6}\s|\Z)", c, re.DOTALL | re.IGNORECASE)
    if ds:
        dec_count = len(re.findall(
            r"(?:^|\n)\s*(?:\d+[.)、]|[-*+•])\s+\S", ds.group(1)))
    # 後備：即使沒有正式段落，也用逐字稿中明確的決議線索查核報告。
    specific = 0
    if re.search(r"只用綠色|綠色.{0,4}(?:不|別).{0,2}(?:用)?\s*紅色|不(?:用|放)\s*紅色", c):
        specific += 1
    if re.search(r"tier\s*1|tier\s*one|只.{0,4}(?:比|聚焦|做)\s*tier", c, re.IGNORECASE):
        specific += 1
    if re.search(r"鼎峰一列|新增.{0,6}列|加上.{0,4}列|line\s*item", c, re.IGNORECASE):
        specific += 1
    if re.search(r"COSCUP|DevOpsDays|Kubernetes Day|活動.{0,4}分工|主線.{0,4}分工", c):
        specific += 1
    if (tagline in c) or re.search(r"更快交付|更低風險|主標語", c):
        specific += 1
    if re.search(r"stage.{0,4}命名|命名.{0,4}(?:維持|現狀)|每個\s*stage", c, re.IGNORECASE):
        specific += 1
    dec_count = max(dec_count, specific)
    scores["decisions_log"] = (
        1.0 if dec_count >= 3 else (0.5 if dec_count >= 2 else 0.0))

    # === 6) action_items_log：至少 2 項 ===
    act_count = 0
    ascn = re.search(
        r"#+\s*[^\n]*(?:行動項目|待辦|action\s*item)[^\n]*\n(.*?)"
        r"(?=\n#{1,6}\s|\Z)", c, re.DOTALL | re.IGNORECASE)
    if ascn:
        act_count = len(re.findall(
            r"(?:^|\n)\s*(?:\d+[.)、]|[-*+•])\s+\S", ascn.group(1)))
    if act_count == 0:
        # 後備：全文找像行動項目的標記／動詞片語
        markers = re.findall(
            r"(?:行動項目|負責|指派|期限|截止|本週內|星期二|下班前|"
            r"will|should|assigned|owner|deadline)",
            c, re.IGNORECASE)
        act_count = min(len(markers), 5)
    scores["action_items_log"] = (
        1.0 if act_count >= 2 else (0.5 if act_count >= 1 else 0.0))

    # === 7) organized：清楚的區段標題 ===
    headings = re.findall(r"(?m)^#{1,4}\s+\S", c)
    # 也接受粗體當小標（例如 **後設資料**）作為次要組織訊號
    bold_heads = re.findall(r"(?m)^\s*\*\*[^*\n]{2,20}\*\*\s*$", c)
    h = len(headings) + (len(bold_heads) if len(headings) < 5 else 0)
    scores["organized"] = (
        1.0 if h >= 5 else (0.5 if h >= 3 else 0.0))

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
