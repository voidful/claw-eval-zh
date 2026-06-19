"""Grader for T118tw_meeting_tech_messaging (Taiwan-localized from PinchBench `task_meeting_tech_messaging`).

Phase 2 source: tasks_zh/task_meeting_tech_messaging.md
Original file: tasks/task_meeting_tech_messaging.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """TW 鼎峰科技 訊息架構擷取 grader（依台灣逐字稿動態推導應有事實）。

    讀 meeting_transcript.md 推導「應有的標語／支柱／最終選定」，再比對 agent 的
    中文報告 messaging_framework.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    # --- 1) 定位 agent 報告 ---
    report = workspace / "messaging_framework.md"
    if not report.exists():
        for alt in ["messaging.md", "framework.md", "taglines.md",
                    "messaging_options.md", "訊息架構.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break

    keys = [
        "report_created", "three_pillars", "multiple_candidates",
        "chosen_speed_tagline", "chosen_transparency_tagline",
        "chosen_e2e_tagline", "rejected_alternatives",
        "evaluation_criteria", "security_subtagline", "finals_distinguished",
    ]
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"report_created": 1.0}
    content = report.read_text(encoding="utf-8", errors="ignore")

    # --- helper：把全形標點、空白統一掉，方便寬鬆比對 ---
    def norm(s):
        s = s.replace("，", "").replace("、", "").replace("。", "")
        s = s.replace("「", "").replace("」", "").replace("（", "").replace("）", "")
        s = s.replace("(", "").replace(")", "").replace(",", "")
        s = re.sub(r"\s+", "", s)
        return s

    c_norm = norm(content)

    def has(*phrases):
        return any(norm(p) in c_norm for p in phrases)

    # --- 2) 從逐字稿動態讀出「應有事實」（避免硬寫英文原版）---
    tpath = workspace / "meeting_transcript.md"
    tx = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""
    tx_norm = norm(tx)

    def in_tx(*phrases):
        return any(norm(p) in tx_norm for p in phrases)

    # 三大支柱的代表語句（逐字稿原文）
    pillar_transparency = ["單一真相來源，無限可能", "人人都能用的一體式平台",
                           "從路線圖到公司願景，我們都透明"]
    pillar_e2e = ["端到端掌控你的軟體工廠", "幾乎什麼都能自動化，凡事都能協作"]
    pillar_speed = ["更快交付，更低風險", "自信地快速前進", "規模拉大、速度拉快、測試拉滿",
                    "加速並維持在軌道上", "帶著自信的速度", "零取捨"]

    # 最終選定（逐字稿宣布）
    final_transparency = "單一真相來源，無限可能"
    final_e2e = "端到端掌控你的軟體工廠"
    final_speed = "更快交付，更低風險"
    security_sub = "守護工廠與每一次交付"

    # 只保留「確實出現在台灣逐字稿裡」的事實當查核基準（動態推導，不硬寫）
    present_transparency = [p for p in pillar_transparency if in_tx(p)]
    present_e2e = [p for p in pillar_e2e if in_tx(p)]
    present_speed = [p for p in pillar_speed if in_tx(p)]

    # --- 3) 三個支柱是否都被辨識（用各支柱任一代表語句 / 支柱名稱判定）---
    pillar_hits = 0
    if has(*present_transparency) or re.search(r"透明|單一平台|單一真相|一體式", content):
        pillar_hits += 1
    if has(*present_e2e) or re.search(r"端到端|掌控|自動化", content):
        pillar_hits += 1
    if has(*present_speed) or re.search(r"速度|資安|風險|安全|取捨", content):
        pillar_hits += 1
    scores["three_pillars"] = 1.0 if pillar_hits >= 3 else (0.5 if pillar_hits >= 2 else 0.0)

    # --- 4) 多個候選語句（從逐字稿出現的所有候選裡，數報告命中幾個）---
    all_candidates = present_transparency + present_e2e + present_speed + ["更快交付、更低風險，帶著自信"]
    # 去重
    seen = set()
    uniq_candidates = []
    for p in all_candidates:
        k = norm(p)
        if k and k not in seen:
            seen.add(k)
            uniq_candidates.append(p)
    phrase_count = sum(1 for p in uniq_candidates if has(p))
    scores["multiple_candidates"] = (
        1.0 if phrase_count >= 6 else
        0.75 if phrase_count >= 4 else
        0.5 if phrase_count >= 3 else 0.0
    )

    # --- 5) 速度／資安最終選定：「更快交付，更低風險」並標為選定／最愛 ---
    speed_chosen_marker = re.search(
        r"(更快交付[，,]?\s*更低風險)[^\n]{0,40}?(最終|選定|採用|主標語|共識|最愛|決定|定案|首選)|"
        r"(最終|選定|採用|主標語|共識|最愛|決定|定案|首選)[^\n]{0,40}?(更快交付[，,]?\s*更低風險)",
        content,
    )
    if has(final_speed) and speed_chosen_marker:
        scores["chosen_speed_tagline"] = 1.0
    elif has(final_speed):
        scores["chosen_speed_tagline"] = 0.5
    else:
        scores["chosen_speed_tagline"] = 0.0

    # --- 6) 透明支柱最終選定：「單一真相來源，無限可能」 ---
    scores["chosen_transparency_tagline"] = 1.0 if has(final_transparency) else 0.0

    # --- 7) 端到端支柱最終選定：「端到端掌控你的軟體工廠」 ---
    scores["chosen_e2e_tagline"] = 1.0 if has(final_e2e) else 0.0

    # --- 8) 被否決的替代方案及原因 ---
    rejected_hits = 0
    # 「測試拉滿 / 規模拉大…」被否決（蠢／討厭）
    if re.search(r"(測試拉滿|規模拉大[^\n]{0,20}測試拉滿)", content) and \
       re.search(r"(超蠢|蠢|討厭|不喜歡|否決|不愛|goofy)", content):
        rejected_hits += 1
    # 「零取捨」被否決（永遠有取捨／工程師心態／不準確）
    if re.search(r"零取捨|no\s*trade", content, re.IGNORECASE) and \
       re.search(r"(否決|永遠都有取捨|永遠有取捨|工程師|不準確|絕對)", content):
        rejected_hits += 1
    # 「自信地快速前進」因對等性／動詞片語被排除
    if re.search(r"自信地快速前進", content) and \
       re.search(r"(對等性|對不齊|動詞片語|parity|名詞片語)", content):
        rejected_hits += 1
    scores["rejected_alternatives"] = (
        1.0 if rejected_hits >= 2 else (0.5 if rejected_hits >= 1 else 0.0)
    )

    # --- 9) 評估準則 ---
    criteria_hits = 0
    if re.search(r"對等性|對不齊|調性|平行句構|parity|parallel", content):
        criteria_hits += 1
    if re.search(r"朗朗上口|精煉|有力|catch|pith", content, re.IGNORECASE):
        criteria_hits += 1
    if re.search(r"名詞片語|動詞片語|技術準確|準確性|絕對化|絕對話|100\s*%\s*安全", content):
        criteria_hits += 1
    scores["evaluation_criteria"] = (
        1.0 if criteria_hits >= 2 else (0.5 if criteria_hits >= 1 else 0.0)
    )

    # --- 10) 資安子標語 ---
    scores["security_subtagline"] = 1.0 if has(security_sub) else 0.0

    # --- 11) 最終 vs 否決是否清楚區分 ---
    final_word = bool(re.search(r"最終|選定|採用|決定|定案|主標語|final", content, re.IGNORECASE))
    reject_word = bool(re.search(r"否決|被否決|不採用|替代方案|淘汰|捨棄|排除|reject", content, re.IGNORECASE))
    fin = (1 if final_word else 0) + (1 if reject_word else 0)
    scores["finals_distinguished"] = 1.0 if fin >= 2 else (0.5 if fin >= 1 else 0.0)

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
