"""Grader for T006tw_email_triage (Taiwan-localized from PinchBench `task_email_triage`).

Phase 2 source: tasks_zh/task_email_triage.md
Original file: tasks/task_email_triage.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """電子郵件收件匣分類 grader（繁中台灣化：鼎峰科技工程師收件匣）。

    檢查 agent 產生的中文報告 triage_report.md 的結構正確性與關鍵優先順序指派。
    應有事實盡量從工作區 inbox/email_XX.txt 動態推導（寄件者姓名、NT$ 金額、
    PR 編號）再比對報告，避免硬寫。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)
    report_file = workspace / "triage_report.md"

    keys = [
        "file_created", "all_emails_covered", "priorities_assigned",
        "categories_assigned", "actions_assigned", "outage_is_p0",
        "alert_linked_to_outage", "client_is_high_priority",
        "spam_is_low_priority", "sorted_by_priority", "has_summary_section",
    ]
    if not report_file.exists():
        for alt in ["triage.md", "分類報告.md", "report.md"]:
            if (workspace / alt).exists():
                report_file = workspace / alt
                break
    if not report_file.exists():
        return {k: 0.0 for k in keys}

    scores = {"file_created": 1.0}
    content = report_file.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()

    # --- 從 inbox 動態讀出應有事實（寄件者姓名等），fallback 用預設 ---
    inbox = workspace / "inbox"

    def _read(name):
        p = inbox / name
        return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

    # 從每封郵件抽出「（姓名，職稱）」中的中文人名作為辨識線索
    def _name(text):
        m = re.search(r"（([一-鿿]{2,4})[，,]", text)
        return m.group(1) if m else ""

    cto_name = _name(_read("email_01.txt")) or "王志明"
    client_name = _name(_read("email_05.txt")) or "陳建宏"
    reviewer_name = _name(_read("email_10.txt")) or "周立群"

    # 客戶郵件的金額（從 email_05 動態抓 NT$ 數字，如「6,000 萬」）
    e05 = _read("email_05.txt")
    m_amt = re.search(r"([0-9][0-9,]*\s*萬)", e05)
    client_amount = m_amt.group(1).replace(" ", "") if m_amt else "6,000萬"

    # 13 封郵件的辨識指標（中文關鍵字，含動態人名）
    email_indicators = [
        rf"(資料庫|服務中斷|當機|戰情室|p0\s*事故|{cto_name})",
        r"(部落格|技術審查|行銷|第四季|q4|淑芬)",
        r"(dependabot|pull\s*request\s*#?482|相依套件|相依更新)",
        r"(團體保險|福利|健檢|勞退|2\s*月\s*28|28\s*日)",
        rf"(南港數位|{client_name}|新臺幣|api\s*整合|6,?000\s*萬)",
        r"(linkedin|邀請聯繫|連結邀請)",
        r"(績效|自評|考核|雅婷)",
        r"(密碼|ssh\s*金鑰|資安合規|2\s*月\s*19|19\s*日前)",
        r"(科技週報|電子報|週報|ai\s*代理人)",
        rf"(auth\s*service|{reviewer_name}|oauth2?\s*pkce|pr\s*#?156|重構)",
        r"(快閃|特賣|4\s*折|saastools|垃圾|促銷)",
        r"(預算對帳|第一季|財務長|q1|明芳)",
        r"(api\s*延遲|監控警報|\[警報\]|p99|2000ms)",
    ]
    found = sum(1 for p in email_indicators if re.search(p, cl, re.IGNORECASE))
    scores["all_emails_covered"] = found / 13.0

    # --- 優先順序標籤（P0-P4）---
    prio = re.findall(r"\bP[0-4]\b", content, re.IGNORECASE)
    n = len(prio)
    scores["priorities_assigned"] = (
        1.0 if n >= 13 else 0.75 if n >= 10 else 0.5 if n >= 6 else 0.25 if n >= 1 else 0.0
    )

    # --- 分類（中文／英文皆計）---
    category_keywords = [
        r"事故|incident", r"客戶|client", r"內部請求|internal",
        r"行政|administrative|admin", r"程式碼審查|code.?review",
        r"自動通知|automated", r"電子報|newsletter", r"垃圾|促銷|spam",
    ]
    cats = sum(1 for kw in category_keywords if re.search(kw, cl, re.IGNORECASE))
    scores["categories_assigned"] = (
        1.0 if cats >= 6 else 0.75 if cats >= 4 else 0.5 if cats >= 2 else 0.0
    )

    # --- 建議行動（動作導向語彙，中英並計）---
    action_kw = (
        r"行動|回覆|回信|審查|安排|加入|忽略|歸檔|完成|送出|填寫|核准|合併|刪除|"
        r"取消訂閱|轉寄|委派|出席|閱讀|處理|建議|更換|確認|"
        r"respond|reply|review|schedule|join|ignore|archive|complete|submit|"
        r"fill|approve|merge|delete|unsubscribe|forward|delegate|attend|read|dismiss"
    )
    ac = len(re.findall(action_kw, cl, re.IGNORECASE))
    scores["actions_assigned"] = (
        1.0 if ac >= 13 else 0.75 if ac >= 8 else 0.5 if ac >= 4 else 0.25
    )

    # --- 取得某關鍵字附近的區段（中文無詞界，故用 window 切片）---
    def _section(patterns, before=200, after=320):
        for p in patterns:
            m = re.search(p, cl, re.IGNORECASE)
            if m:
                return cl[max(0, m.start() - before):min(len(cl), m.end() + after)]
        return ""

    # --- 服務中斷（郵件 01）為 P0 ---
    outage = _section([r"資料庫.*當機", r"服務中斷", r"當機", cto_name.lower(), r"戰情室", r"技術長"])
    scores["outage_is_p0"] = (
        1.0 if re.search(r"\bp0\b", outage, re.IGNORECASE)
        else 0.5 if re.search(r"\bp1\b", outage, re.IGNORECASE) else 0.0
    )

    # --- 監控警報（郵件 13）與服務中斷相連結 ---
    alert = _section([r"api\s*延遲", r"監控警報", r"\[警報\]", r"p99"], after=520)
    if re.search(r"相關|關連|關聯|連結|連動|同一.*事件|資料庫|事故|incident|correlat|relat", alert, re.IGNORECASE):
        scores["alert_linked_to_outage"] = 1.0
    elif re.search(r"\bp0\b", alert, re.IGNORECASE):
        scores["alert_linked_to_outage"] = 0.75
    else:
        scores["alert_linked_to_outage"] = 0.0

    # --- 客戶郵件（郵件 05）為高優先（P0/P1）---
    client = _section([r"南港數位", client_name.lower(), re.escape(client_amount.lower()), r"api\s*整合", r"6,?000\s*萬"])
    scores["client_is_high_priority"] = (
        1.0 if re.search(r"\bp[01]\b", client, re.IGNORECASE)
        else 0.5 if re.search(r"\bp2\b", client, re.IGNORECASE) else 0.0
    )

    # --- 垃圾促銷（郵件 11）為 P4 ---
    spam = _section([r"快閃", r"特賣", r"saastools", r"4\s*折"])
    scores["spam_is_low_priority"] = (
        1.0 if re.search(r"\bp4\b", spam, re.IGNORECASE)
        else 0.75 if re.search(r"\bp3\b", spam, re.IGNORECASE) else 0.0
    )

    # --- 依優先順序排序（P0 應出現在 P4 之前）---
    p0 = [m.start() for m in re.finditer(r"\bP0\b", content, re.IGNORECASE)]
    p4 = [m.start() for m in re.finditer(r"\bP4\b", content, re.IGNORECASE)]
    if p0 and p4:
        if max(p0) < min(p4):
            scores["sorted_by_priority"] = 1.0
        elif min(p0) < min(p4):
            scores["sorted_by_priority"] = 0.5
        else:
            scores["sorted_by_priority"] = 0.0
    elif p0 or p4:
        scores["sorted_by_priority"] = 0.25
    else:
        scores["sorted_by_priority"] = 0.0

    # --- 最上方摘要區段 ---
    head = cl[:max(len(cl) // 5, 200)]
    if re.search(r"摘要|總覽|重點|當日計畫|今日計畫|行動計畫|top\s*priorities|summary|overview", head):
        scores["has_summary_section"] = 1.0
    elif re.search(r"摘要|總覽|重點|summary|overview", cl):
        scores["has_summary_section"] = 0.5
    else:
        scores["has_summary_section"] = 0.0

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
