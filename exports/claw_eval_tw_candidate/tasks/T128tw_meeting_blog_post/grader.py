"""Grader for T128tw_meeting_blog_post (Taiwan-localized from PinchBench `task_meeting_blog_post`).

Phase 2 source: tasks_zh/task_meeting_blog_post.md
Original file: tasks/task_meeting_blog_post.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """TW 鼎峰科技 會議轉部落格文章 grader（依台灣逐字稿動態推導應有策略）。

    讀 meeting_transcript.md 推導「應談到的核心挑戰與策略」，再比對 agent 的
    中文部落格文章 blog_post.md。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    workspace = Path(workspace_path)

    keys = [
        "file_created", "has_title", "core_challenge", "strategies_present",
        "standalone_post", "appropriate_length", "target_audience",
        "professional_tone",
    ]

    # --- 1) 定位 agent 部落格文章 ---
    report = workspace / "blog_post.md"
    if not report.exists():
        for alt in ["blog.md", "post.md", "article.md", "blogpost.md",
                    "部落格.md", "部落格文章.md"]:
            if (workspace / alt).exists():
                report = workspace / alt
                break
    if not report.exists():
        return {k: 0.0 for k in keys}

    scores = {"file_created": 1.0}
    content = report.read_text(encoding="utf-8", errors="ignore")

    # 中文字數（去掉空白與標點後的字元數，較貼近中文「字數」概念）
    cjk_chars = re.findall(r"[一-鿿]", content)
    char_count = len(cjk_chars)

    # --- helper：寬鬆比對（去全形標點與空白）---
    def norm(s):
        for ch in "，、。「」（）(),:：；;！？!? 　\n\t":
            s = s.replace(ch, "")
        return s

    c_norm = norm(content)

    def has(*phrases):
        return any(norm(p) in c_norm for p in phrases)

    # --- 2) 從逐字稿動態確認「應有事實確實存在於素材」 ---
    tpath = workspace / "meeting_transcript.md"
    tx = tpath.read_text(encoding="utf-8", errors="ignore") if tpath.exists() else ""
    tx_norm = norm(tx)

    def in_tx(*phrases):
        return any(norm(p) in tx_norm for p in phrases)

    # --- 3) 標題：第一個 # 標題，且不可是會議摘要型 ---
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
        is_recap_title = bool(re.search(
            r"會議(摘要|記錄|紀錄|回顧|筆記|備忘|重點整理)|逐字稿|meeting\s*(summary|recap|notes|minutes)",
            title, re.IGNORECASE))
        scores["has_title"] = 0.0 if is_recap_title else 1.0
    else:
        scores["has_title"] = 0.0

    # --- 4) 核心挑戰：持續交付／增量出貨 + 公告／路線圖公開 ---
    # 動態：只在逐字稿確有此挑戰時才作為查核基準
    challenge_terms_continuous = [
        "持續交付", "增量出貨", "持續出貨", "持續上線", "迭代", "一個個小", "MVC", "最小可行",
    ]
    challenge_terms_launch = [
        "大爆炸", "big-bang", "big bang", "傳統發布", "傳統的發布", "傳統公告", "一次端出",
    ]
    challenge_terms_roadmap = [
        "公開路線圖", "路線圖公開", "公開的路線圖", "開源模式", "公開路線",
    ]
    tx_has_challenge = (
        any(in_tx(t) for t in challenge_terms_continuous)
        and (any(in_tx(t) for t in challenge_terms_roadmap) or any(in_tx(t) for t in ["大爆炸", "big-bang"]))
    )

    challenge_hits = 0
    if has(*challenge_terms_continuous):
        challenge_hits += 1
    if has(*challenge_terms_launch) or re.search(r"傳統.{0,6}(發布|公告|上市|發表)", content):
        challenge_hits += 1
    if has(*challenge_terms_roadmap):
        challenge_hits += 1
    # 公告本身的困難（持續交付下難做公告）
    if re.search(r"(公告|上市|發表|發布).{0,12}(困難|難|挑戰|不容易|棘手)", content) or \
       re.search(r"(困難|難|挑戰|不容易|棘手).{0,12}(公告|上市|發表|發布)", content):
        challenge_hits += 1
    scores["core_challenge"] = (
        1.0 if challenge_hits >= 2 else (0.5 if challenge_hits >= 1 else 0.0)
    )

    # --- 5) 策略：對應逐字稿第二段「鼎峰匯流大會：產品發布題材」的策略 ---
    # 各策略的偵測子句（report 端）與其在逐字稿存在性（dynamic anchor）
    strategy_specs = [
        # (報告偵測 regex, 逐字稿錨點 phrases)
        (r"打包|整合|包成|彙整|合併|綑綁|歸納成.{0,4}主題|主題敘事|大主題|敘事桶|narrative\s*bucket",
         ["整合", "bundle", "敘事桶", "narrative bucket", "打包"]),
        (r"GA[\s-]*ready|回顧過去一年|回顧一年|年度回顧|成熟度|里程碑.{0,4}(成熟|功能)|已可正式|正式發布條件|達到正式",
         ["GA-ready", "回頭看過去一年", "回顧過去一年", "GA ready"]),
        (r"興奮度|堆疊排名|stack\s*rank|排序|優先序|挑出.{0,4}前\s*5|前五名|整體前\s*5|top\s*5",
         ["興奮度", "堆疊排名", "stack rank", "top 5", "前 5 名", "整體前 5"]),
        (r"敘事|主題|故事線|分桶|分類成主題|歸類|narrative|theme",
         ["敘事", "主題", "narrative", "故事"]),
        (r"(活動|研討會|大會|keynote|匯流大會).{0,20}(時機|前後|搭配|綁|爭取.{0,4}媒體|媒體關注|公關|press)|"
         r"(時機|前後|搭配|綁|媒體關注|公關).{0,20}(活動|研討會|大會|keynote|匯流大會)",
         ["鼎峰匯流大會", "keynote", "研討會", "媒體關注"]),
        (r"(正面|正向).{0,8}(框架|陳述|表述|包裝|說法)|新能力(?!.{0,4}清單)|"
         r"(講成|說成|框架成).{0,6}新能力|不(要|是).{0,8}(壞掉|修好|補好)|慶祝.{0,4}(成果|win|成績)",
         ["新能力", "正面框架", "壞掉的東西", "慶祝"]),
    ]
    strategy_count = 0
    for rgx, anchors in strategy_specs:
        # 動態門檻：策略錨點需確實出現在逐字稿；若逐字稿沒有則不計（保險）
        if not any(in_tx(a) for a in anchors):
            continue
        if re.search(rgx, content, re.IGNORECASE):
            strategy_count += 1
    scores["strategies_present"] = (
        1.0 if strategy_count >= 3 else (0.5 if strategy_count >= 2 else 0.0)
    )

    # --- 6) 獨立成篇（不應讀起來像會議回顧）---
    recap_signals = [
        r"在(這場|這次|本次|該次)?會議(中|裡|上)",
        r"(與會者|與會人員|出席者|參與者|團隊成員).{0,6}(討論|談到|提到|表示)",
        r"(會議|逐字稿)(摘要|記錄|紀錄|回顧|筆記|備忘)",
        r"(接著|然後|隨後|稍後)(團隊|大家|他們).{0,4}(討論|談到|進到|轉向)",
        r"王志明(說|表示|提到|認為)|林淑芬(說|表示|提到|認為)|陳柏宇(說|表示|提到|認為)",
    ]
    recap_count = sum(1 for p in recap_signals if re.search(p, content))
    scores["standalone_post"] = (
        1.0 if recap_count == 0 else (0.5 if recap_count <= 1 else 0.0)
    )

    # --- 7) 長度（中文字數）：700-1200 理想；450-1500 可接受 ---
    if 700 <= char_count <= 1200:
        scores["appropriate_length"] = 1.0
    elif 450 <= char_count <= 1500:
        scores["appropriate_length"] = 0.5
    else:
        scores["appropriate_length"] = 0.0

    # --- 8) 目標讀者（產品行銷／DevOps／持續交付術語）---
    audience_terms = [
        r"產品行銷", r"行銷團隊", r"DevOps", r"持續交付", r"持續部署",
        r"上市策略|發布策略|發布計畫|go[\s-]*to[\s-]*market|GTM",
        r"公關|媒體|press", r"CI/?CD|流水線|管線|pipeline",
        r"開源|路線圖|roadmap", r"產品(發布|上市|公告)|功能(發布|上市)",
    ]
    audience_score = sum(1 for p in audience_terms if re.search(p, content, re.IGNORECASE))
    scores["target_audience"] = (
        1.0 if audience_score >= 3 else (0.5 if audience_score >= 1 else 0.0)
    )

    # --- 9) 語氣專業 + 有結構（多個小標題）---
    casual_signals = [r"哈哈+", r"XD", r"嗯+\b", r"呃+", r"啦啦+", r"耶+\b"]
    casual_count = sum(1 for p in casual_signals if re.search(p, content))
    has_structure = len(re.findall(r"^#{1,3}\s+", content, re.MULTILINE)) >= 2
    scores["professional_tone"] = (
        1.0 if (casual_count == 0 and has_structure)
        else (0.5 if casual_count <= 1 else 0.0)
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
