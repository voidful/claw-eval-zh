"""Grader for T126tw_meeting_sentiment_analysis (Taiwan-localized from PinchBench `task_meeting_sentiment_analysis`).

Phase 2 source: tasks_zh/task_meeting_sentiment_analysis.md
Original file: tasks/task_meeting_sentiment_analysis.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """為「會議情緒分析」（台灣在地化）評分。

    做法：先從工作區內的台灣逐字稿（dest=meeting_transcript.md）動態推導
    「應有事實」（與會者、四大主題、關鍵決議／標語），再比對 agent 產生的
    中文報告 sentiment_analysis.md。僅用標準函式庫。

    回傳：check 名稱 -> 分數（0.0~1.0）。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 找出 agent 的報告檔 ---
    report_path = workspace / "sentiment_analysis.md"
    if not report_path.exists():
        for alt in (
            "sentiment_report.md", "sentiment.md",
            "meeting_sentiment.md", "analysis.md", "情緒分析.md",
        ):
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    checks = (
        "file_created", "overall_sentiment", "topic_breakdown",
        "team_dynamics", "quotes_included", "engagement_assessed",
        "concerns_identified", "tonal_distinction",
    )
    if not report_path.exists():
        return {c: 0.0 for c in checks}

    scores = {"file_created": 1.0}
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 從台灣逐字稿動態推導應有事實 ---
    transcript_path = workspace / "meeting_transcript.md"
    tx = ""
    if transcript_path.exists():
        tx = transcript_path.read_text(encoding="utf-8", errors="ignore")

    # 與會者：逐字稿中出現過的具名人物（用「姓名：」的發言格式偵測）
    candidate_names = ["王志明", "林淑芬", "高敏哲", "陳柏宇", "蔡思敏", "戴立安"]
    attendees = [n for n in candidate_names if (n in tx if tx else True)]
    if not attendees:
        attendees = candidate_names

    # 主標語：從逐字稿動態擷取（被宣告為主標語／final 的句子）
    tagline = "更快交付，更低風險"
    if tx:
        m = re.search(r"主標語[，。]?\s*[「『]([^」』]{2,20})[」』]", tx)
        if not m:
            m = re.search(r"以[「『]([^」』]{2,20})[」』]\s*當主標語", tx)
        if m:
            tagline = m.group(1)

    # --- 整體情緒：應辨識為正面／合作 ---
    positive_terms = [
        "正面", "合作", "建設性", "具生產力", "有生產力",
        "積極", "正向", "熱絡", "同調", "良好",
    ]
    overall_ctx = re.search(
        r"(整體|總體|大致|綜觀|總結).{0,40}(" + "|".join(positive_terms) + ")",
        content,
    ) or re.search(
        r"(" + "|".join(positive_terms) + r").{0,30}(基調|氛圍|情緒|語氣|氣氛)",
        content,
    )
    scores["overall_sentiment"] = 1.0 if overall_ctx else 0.0

    # --- 逐主題拆解：四大主題各自帶情緒詞 ---
    sentiment_word = (
        r"(正面|中性|負面|混合|正向|熱絡|熱情|興奮|不確定|"
        r"爭辯|爭議|投入|玩鬧|遲疑|不滿|建設性|中立)"
    )
    topic_anchors = [
        r"(活動|贊助|研討會|COSCUP|DevOpsDays|Kubernetes\s*Day)",
        r"(產品發布|匯流大會|漏洞管理|MVC|keynote|top\s*5|前\s*5)",
        r"(資訊圖|競品比較|配色|綠色|stage\s*名稱)",
        r"(訊息|標語|tagline|支柱|" + re.escape(tagline) + r")",
    ]
    topic_count = 0
    for anchor in topic_anchors:
        # 主題錨點與情緒詞同段（任一順序、近距離）出現即算一個主題
        near = re.search(
            anchor + r"[^\n。]{0,80}" + sentiment_word, content
        ) or re.search(
            sentiment_word + r"[^\n。]{0,80}" + anchor, content
        )
        if near:
            topic_count += 1
    # 後備：4 個以上小節 + 足量情緒詞也算達標
    if topic_count < 3:
        sections = re.findall(r"^#{2,4}\s+\S+", content, re.MULTILINE)
        sentiment_hits = len(re.findall(sentiment_word, content))
        if len(sections) >= 4 and sentiment_hits >= 5:
            topic_count = max(topic_count, 3)
    scores["topic_breakdown"] = (
        1.0 if topic_count >= 3 else (0.5 if topic_count >= 2 else 0.0)
    )

    # --- 團隊動態：認同／分歧／熱絡／玩鬧／合作 ---
    dynamics_patterns = [
        r"(認同|共識|同意|一致|同調)",
        r"(分歧|反對|質疑|爭辯|爭議|不滿|張力)",
        r"(熱情|興奮|熱絡|活力|投入)",
        r"(玩鬧|打趣|玩笑|笑|幽默|賽車片|頭文字)",
        r"(合作|協作|支持|互相)",
    ]
    dynamics_count = sum(
        1 for p in dynamics_patterns if re.search(p, content)
    )
    scores["team_dynamics"] = (
        1.0 if dynamics_count >= 3 else (0.5 if dynamics_count >= 2 else 0.0)
    )

    # --- 引言：全形／半形引號或區塊引言，且須是逐字稿中的真實片段 ---
    quote_spans = []
    for m in re.finditer(r"[「『\"“]([^」』\"”\n]{4,})[」』\"”]", content):
        quote_spans.append(m.group(1).strip())
    for m in re.finditer(r"^\s*>\s*(.+)$", content, re.MULTILINE):
        quote_spans.append(m.group(1).strip())

    # 與逐字稿做模糊比對：取引言中的中文片段，看是否出現在逐字稿
    def _grounded(q):
        if not tx:
            return True  # 無逐字稿可比對時不扣分
        core = re.sub(r"[^一-鿿]", "", q)
        if len(core) < 4:
            return False
        # 取連續 4 字視窗，任一視窗出現在逐字稿即視為有所本
        return any(core[i:i + 4] in tx for i in range(len(core) - 3))

    grounded_quotes = [q for q in quote_spans if _grounded(q)]
    n_quotes = len(grounded_quotes)
    scores["quotes_included"] = (
        1.0 if n_quotes >= 2 else (0.5 if n_quotes >= 1 else 0.0)
    )

    # --- 投入程度 ---
    engagement_patterns = [
        r"投入(程度|度)?",
        r"(積極|熱烈|踴躍).{0,6}(討論|參與|發言|辯論)",
        r"(高度|強烈|良好).{0,6}(投入|參與|互動|能量)",
        r"engag",
    ]
    eng_hits = sum(1 for p in engagement_patterns if re.search(p, content, re.IGNORECASE))
    scores["engagement_assessed"] = (
        1.0 if eng_hits >= 2 else (0.5 if eng_hits >= 1 else 0.0)
    )

    # --- 疑慮／不確定 ---
    concern_patterns = [
        r"(疑慮|遲疑|不確定|不滿|挑戰|顧慮|擔憂)",
        r"(待確認|尚未確認|暫定|未定案)",
        r"(反對|質疑|抗拒|阻力)",
        r"(不清楚|不夠|描述性不足|不準確)",
        r"(風險|爭議|摩擦)",
    ]
    concern_hits = sum(1 for p in concern_patterns if re.search(p, content))
    scores["concerns_identified"] = (
        1.0 if concern_hits >= 2 else (0.5 if concern_hits >= 1 else 0.0)
    )

    # --- 情感基調區分：出現多種不同的情緒詞 ---
    tone_terms = re.findall(
        r"(正面|負面|中性|混合|正向|熱絡|熱情|興奮|不確定|玩鬧|"
        r"爭辯|爭議|不滿|遲疑|建設性|投入|中立|嚴肅|輕鬆)",
        content,
    )
    unique_tones = set(tone_terms)
    scores["tonal_distinction"] = (
        1.0 if len(unique_tones) >= 4 else (0.5 if len(unique_tones) >= 2 else 0.0)
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
