"""Grader for T045tw_email_search (Taiwan-localized from PinchBench `task_email_search`).

Phase 2 source: tasks_zh/task_email_search.md
Original file: tasks/task_email_search.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """郵件搜尋與摘要 grader（繁中台灣化：鼎峰科技 Project Alpha 信件串）。

    檢查 agent 產生的中文摘要 alpha_summary.md。盡量從 emails/ 動態推導應有事實
    （中文寄件者姓名、客戶公司名）再比對報告，避免硬寫；其餘以維持不變的數字錨點
    （預算 340/410/432 萬、ARR 1.85/2.8/2.1 億、日期 4/21、5/12、5/6、5/27）與
    技術 identifier 比對。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)
    summary_file = workspace / "alpha_summary.md"

    keys = [
        "file_created", "project_identified", "tech_stack", "budget_tracking",
        "timeline_tracking", "security_findings", "client_revenue",
        "noise_filtered", "has_required_sections", "cross_referencing",
    ]
    if not summary_file.exists():
        return {k: 0.0 for k in keys}

    scores["file_created"] = 1.0
    content = summary_file.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()

    # --- 從 emails/ 動態推導應有事實（寄件者中文姓名、客戶公司名），fallback 用預設 ---
    emails_dir = workspace / "emails"

    def _read(name):
        p = emails_dir / name
        return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

    def _sender_name(text):
        # 寄件者：lin.jy@…（林佳穎，專案負責人）-> 取「林佳穎」
        m = re.search(r"寄件者：[^（(]*[（(]([一-鿿]{2,4})[，,]", text)
        return m.group(1) if m else ""

    lead_name = _sender_name(_read("2026-01-15_project_alpha_kickoff.txt")) or "林佳穎"
    data_eng = _sender_name(_read("2026-01-22_alpha_data_pipeline.txt")) or "張哲瑋"
    cfo_name = _sender_name(_read("2026-02-03_alpha_budget_concern.txt")) or "趙麗娟"

    # 客戶公司名：從 client_feedback 郵件抓「（…ARR）」前的中文公司名
    e_clients = _read("2026-02-14_alpha_client_feedback.txt")
    client_companies = re.findall(
        r"([一-鿿]{2,8}(?:企業|科技|金融|股份有限公司))（[^）]*ARR）",
        e_clients,
    )
    if not client_companies:
        client_companies = ["宏遠企業", "全球通科技", "源資料股份有限公司",
                            "鼎泰金融", "雲匯科技"]

    # --- 1. 專案正確辨識為分析儀表板 ---
    if re.search(r"analytics\s+dashboard", cl) or "分析儀表板" in content:
        scores["project_identified"] = 1.0
    elif re.search(r"analytics|dashboard", cl) or re.search(r"分析|儀表板|報表", content):
        scores["project_identified"] = 0.5
    else:
        scores["project_identified"] = 0.0

    # --- 2. 技術堆疊涵蓋率（技術 identifier 維持英文）---
    tech_keywords = [
        r"postgresql|postgres|timescaledb",
        r"fastapi",
        r"react",
        r"kafka",
        r"flink",
        r"redis",
        r"recharts",
        r"dbt",
    ]
    tech_found = sum(1 for kw in tech_keywords if re.search(kw, cl))
    if tech_found >= 6:
        scores["tech_stack"] = 1.0
    elif tech_found >= 4:
        scores["tech_stack"] = 0.75
    elif tech_found >= 2:
        scores["tech_stack"] = 0.5
    else:
        scores["tech_stack"] = 0.25 if tech_found >= 1 else 0.0

    # --- 3. 預算追蹤（原始 340 萬與修訂 410 萬；432 萬亦計入修訂）---
    has_original = bool(re.search(r"340\s*萬|340\s*k|340,?000", cl))
    has_revised = bool(re.search(r"410\s*萬|432\s*萬|410\s*k|432\s*k|410,?000|432,?000", cl))
    if has_original and has_revised:
        scores["budget_tracking"] = 1.0
    elif has_original or has_revised:
        scores["budget_tracking"] = 0.5
    elif re.search(r"預算|成本|花費|支出|nt\$|\$\d", cl):
        scores["budget_tracking"] = 0.25
    else:
        scores["budget_tracking"] = 0.0

    # --- 4. 時程追蹤（原始與更新後日期，月份數值維持）---
    original_dates = [r"4\s*[/／月]\s*21", r"5\s*[/／月]\s*12"]
    updated_dates = [r"5\s*[/／月]\s*6", r"5\s*[/／月]\s*27"]
    orig_found = sum(1 for d in original_dates if re.search(d, cl))
    updated_found = sum(1 for d in updated_dates if re.search(d, cl))
    if orig_found >= 1 and updated_found >= 1:
        scores["timeline_tracking"] = 1.0
    elif orig_found >= 1 or updated_found >= 1:
        scores["timeline_tracking"] = 0.5
    elif re.search(r"延後|延遲|延誤|順延|延長|slip|delay|extend|push", cl):
        scores["timeline_tracking"] = 0.25
    else:
        scores["timeline_tracking"] = 0.0

    # --- 5. 資安發現（技術 identifier 維持英文 + 中文同義）---
    security_keywords = [
        r"cross.?tenant|跨租戶",
        r"websocket.{0,12}(auth|驗證|安全)|逐訊息.{0,6}驗證",
        r"rate.?limit|流量限制",
        r"ssrf",
        r"audit.?log|稽核日誌",
    ]
    sec_found = sum(1 for kw in security_keywords if re.search(kw, cl))
    if sec_found >= 3:
        scores["security_findings"] = 1.0
    elif sec_found >= 2:
        scores["security_findings"] = 0.75
    elif sec_found >= 1:
        scores["security_findings"] = 0.5
    elif re.search(r"security|資安|安全", cl):
        scores["security_findings"] = 0.25
    else:
        scores["security_findings"] = 0.0

    # --- 6. 客戶回饋與營收管線 ---
    has_client_names = sum(1 for name in client_companies if name and name in content)
    has_revenue = bool(re.search(
        r"1\.85\s*億|2\.8\s*億|2\.1\s*億|arr|年度經常性收入|營收", cl))
    if has_client_names >= 3 and has_revenue:
        scores["client_revenue"] = 1.0
    elif has_client_names >= 2 or has_revenue:
        scores["client_revenue"] = 0.75
    elif has_client_names >= 1:
        scores["client_revenue"] = 0.5
    elif re.search(r"客戶|顧客|業務|銷售|管線|潛在客戶", cl):
        scores["client_revenue"] = 0.25
    else:
        scores["client_revenue"] = 0.0

    # --- 7. 不相關郵件已被過濾掉 ---
    noise_indicators = [
        r"員工感謝餐會|感謝餐會|team\s*appreciation\s*lunch",
        r"科技高峰會\s*2026|techsummit\s*2026",
        r"早鳥票價|早鳥優惠|early\s*bird",
        r"地中海風.*燒烤|地中海.*亞洲.*燒烤",
        r"飲食偏好|dietary\s*preferences",
    ]
    noise_found = sum(1 for n in noise_indicators if re.search(n, cl))
    if noise_found == 0:
        scores["noise_filtered"] = 1.0
    elif noise_found == 1:
        scores["noise_filtered"] = 0.5
    else:
        scores["noise_filtered"] = 0.0

    # --- 8. 必要區段是否存在 ---
    required_sections = [
        r"概述|overview|專案簡介",
        r"時程|timeline|時間軸",
        r"風險|問題|risk|issue",
        r"客戶|業務|營收|client|business|revenue",
        r"狀態|現況|目前|status",
    ]
    sections_found = sum(1 for s in required_sections if re.search(s, cl))
    scores["has_required_sections"] = sections_found / len(required_sections)

    # --- 9. 跨郵件交叉參照 ---
    cross_ref_indicators = [
        # 資安發現導致時程延後
        r"(資安|安全|security).{0,120}(延後|延誤|延遲|順延|時程|延長|delay|slip|timeline|extend)",
        # 預算因基礎設施成本而增加
        r"(預算|成本|budget|cost).{0,120}(增加|上升|超支|擴編|擴充|修訂|調整|increas|overrun|expan|revis)",
        # 客戶回饋影響優先順序
        r"(客戶|顧客|回饋|client|customer|feedback).{0,120}(優先|功能|需求|排序|priorit|feature|request)",
        # spot instance 省下成本
        r"spot\s*instance.{0,120}(省|節省|降低|減少|sav|reduc|cost)",
    ]
    cross_refs = sum(1 for cr in cross_ref_indicators if re.search(cr, cl))
    if cross_refs >= 3:
        scores["cross_referencing"] = 1.0
    elif cross_refs >= 2:
        scores["cross_referencing"] = 0.75
    elif cross_refs >= 1:
        scores["cross_referencing"] = 0.5
    else:
        scores["cross_referencing"] = 0.0

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
PRIMARY_DIMENSIONS = ['completion', 'safety']


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
