"""Grader for T117tw_meeting_tech_competitors (Taiwan-localized from PinchBench `task_meeting_tech_competitors`).

Phase 2 source: tasks_zh/task_meeting_tech_competitors.md
Original file: tasks/task_meeting_tech_competitors.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """TW tech-meeting competitor-analysis grader.

    查核項對應原始英文 grader，但事實改自台灣逐字稿 meeting_transcript.md
    （虛構公司「鼎峰科技」／產品「鼎峰」；tier 1 六家對手為微宇 DevOps、群智協作、
    碼倉、自動流、制品庫、雲蜂）。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    report_path = workspace / "competitor_analysis.md"
    if not report_path.exists():
        for alt in ["competitors.md", "competitive_analysis.md",
                    "competitor_report.md", "競品分析.md", "競爭對手分析.md"]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    keys = ["report_created", "tier1_competitors", "tier_system", "stage_relevance",
            "platform_distinction", "host_line_item", "market_lens",
            "infographic_philosophy", "tier1_focus"]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8", errors="ignore")

    # --- 從逐字稿動態讀出「應有的 tier 1 對手」，避免硬寫 ---
    transcript_path = workspace / "meeting_transcript.md"
    tier1_expected = []
    if transcript_path.exists():
        ttext = transcript_path.read_text(encoding="utf-8", errors="ignore")
        # 只擷取「Tier 1 一共…家」那句之後、緊接著的 1.~6. 編號清單，避免抓到
        # 後段（如訊息架構評估準則）同樣是編號清單的條目。
        anchor = re.search(r'[Tt]ier\s*1[^\n]{0,12}?(?:六家|6\s*家|共[^\n]{0,4}家)', ttext)
        region = ttext[anchor.end():] if anchor else ""
        for line in region.splitlines():
            m = re.match(r'\s*\d+\.\s*\*{0,2}([^（(*]+?)\*{0,2}\s*(?:[（(]|$)', line)
            if m:
                name = m.group(1).strip()
                # 只收形似競品名稱（中文／英數混合、長度合理）的條目
                if 2 <= len(name) <= 12 and re.search(r'[一-鿿]', name):
                    tier1_expected.append(name)
                # 連續編號清單一旦遇到空白行就停（避免吃到後面段落）
            elif tier1_expected and not line.strip():
                break
    # 後援：逐字稿讀不到時才退回已知清單
    if len(tier1_expected) < 6:
        tier1_expected = ["微宇 DevOps", "群智協作", "碼倉", "自動流", "制品庫", "雲蜂"]
    # 去重、保序、取前六
    seen = set()
    uniq = []
    for n in tier1_expected:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    tier1_expected = uniq[:6]

    # 1) Tier 1 對手是否列出（用核心關鍵字比對，容忍 DevOps 大小寫與全形空白）
    def _match(name: str, text: str) -> bool:
        core = name.replace("DevOps", "").replace(" ", "").replace("　", "").strip()
        if core and core in text:
            return True
        # 含英文部分者（如「微宇 DevOps」）再寬鬆比對中文核心
        if "DevOps" in name and core and core in text:
            return True
        return name in text
    comp_count = sum(1 for n in tier1_expected if _match(n, content))
    scores["tier1_competitors"] = (
        1.0 if comp_count >= 5 else
        0.75 if comp_count >= 4 else
        0.5 if comp_count >= 3 else 0.0
    )

    # 2) 層級分類系統（tier 1/2/3）
    scores["tier_system"] = 1.0 if re.search(
        r'tier\s*[123一二三]|第?\s*[123一二三]\s*層|層級|分層', content, re.IGNORECASE
    ) else 0.0

    # 3) 各 stage 相關性：並非所有對手都適用所有 stage（提監控 Monitor 更佳）
    has_stage = bool(re.search(r'stage|監控|Monitor|設定|Configure|階段', content, re.IGNORECASE))
    has_not_all = bool(re.search(r'並非所有|不是每|不適用|不一定|未必|不是所有|只放相關|只列相關|相關的對手', content))
    if has_stage and has_not_all:
        scores["stage_relevance"] = 1.0
    elif has_stage and re.search(r'監控|Monitor', content, re.IGNORECASE) and re.search(r'雲蜂|碼倉', content):
        scores["stage_relevance"] = 1.0
    elif has_stage:
        scores["stage_relevance"] = 0.5
    else:
        scores["stage_relevance"] = 0.0

    # 4) platform 與非 platform 的區分（自動流／雲蜂不是平台）
    has_platform = bool(re.search(r'平台|platform', content, re.IGNORECASE))
    has_non_platform = bool(
        re.search(r'(?:自動流|雲蜂)[^。\n]{0,30}?(?:不是|並非|不算|非)[^。\n]{0,6}?(?:平台|platform)', content, re.IGNORECASE)
        or re.search(r'(?:不是|並非|不算|非)[^。\n]{0,6}?(?:平台|platform)[^。\n]{0,30}?(?:自動流|雲蜂)', content, re.IGNORECASE)
    )
    scores["platform_distinction"] = (
        1.0 if has_platform and has_non_platform else (0.5 if has_platform else 0.0)
    )

    # 5) 在比較表加入「鼎峰」自己一列（line item）
    scores["host_line_item"] = 1.0 if re.search(
        r'(?:加入|加上|新增|增加|放上)[^。\n]{0,20}?鼎峰[^。\n]{0,12}?(?:一列|一欄|一行|列|欄|line\s*item)'
        r'|鼎峰[^。\n]{0,12}?(?:一列|一欄|一行|line\s*item)',
        content, re.IGNORECASE
    ) else 0.0

    # 6) 功能挑選的市場視角（market lens）
    market_hits = 0
    if re.search(r'市場視角|market\s*lens', content, re.IGNORECASE):
        market_hits += 1
    if re.search(r'買家|客戶|選購|採購|購買', content):
        market_hits += 1
    if re.search(r'誠實|可信|公正|客觀|對手.{0,6}才有|只有對手', content):
        market_hits += 1
    scores["market_lens"] = 1.0 if market_hits >= 2 else (0.5 if market_hits >= 1 else 0.0)

    # 7) 資訊圖設計理念（只用綠色、是比較而非攻擊）
    info_hits = 0
    if re.search(r'(?:只用|僅用|單用|只.{0,2}綠|綠色)', content) and re.search(r'比較|產業|參考|有幫助', content):
        info_hits += 1
    if re.search(r'不(?:用|放|加).{0,2}紅|不要紅|避免紅|無紅|不用紅色', content):
        info_hits += 1
    if re.search(r'(?:比較|有幫助|產業).{0,12}?(?:而非|不是|不要)?.{0,6}?攻擊|不是攻擊|非攻擊|不打對手|attack', content, re.IGNORECASE):
        info_hits += 1
    scores["infographic_philosophy"] = 1.0 if info_hits >= 2 else (0.5 if info_hits >= 1 else 0.0)

    # 8) 先聚焦 tier 1 的決議
    scores["tier1_focus"] = 1.0 if re.search(
        r'(?:只|先|聚焦|專注|現階段|目前)[^。\n]{0,12}?tier\s*[1一]'
        r'|tier\s*[1一][^。\n]{0,12}?(?:聚焦|為主|優先|先|現階段|目前)',
        content, re.IGNORECASE
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
