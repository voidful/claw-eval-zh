---
id: task_memory
name: |
  從情境中擷取記憶
category: memory
grading_type: automated
timeout_seconds: 120
language: zh
locale: zh-TW
region: TW
source_task_id: task_memory
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T137tw_memory
workspace_files:
- path: notes.md
  content: |-
    # 鳳凰專案 — 開發筆記

    ## 時程

    - **Alpha 內測**：2024 年 3 月 15 日
    - **Beta 公測**：2024 年 6 月 1 日
    - **正式上線**：2024 年 9 月 30 日

    ## 團隊成員

    - 技術主導：陳思婷
    - 後端：林志豪、黃詩涵
    - 前端：王建宏、張雅婷
    - 測試（QA）：李俊毅

    ## 主要功能

    1. 即時協作
    2. 進階分析儀表板
    3. 行動 App 整合
    4. 支援 GraphQL 的 API v2

    ## 目前狀態

    我們目前處於 Alpha 內測階段，有 50 位內部使用者參與。回饋相當正面，
    尤其是對全新介面的評價。Beta 公測預定於 2024 年 6 月 1 日推出，
    目前進度順利，可如期達成這個期限。

    ## 技術棧

    - 前端：React 18、TypeScript
    - 後端：Node.js、Express、PostgreSQL
    - 基礎設施：AWS（ECS、RDS、S3）
    - CI/CD：GitHub Actions

    ## 待解決事項

    - Beta 公測前需完成 API 文件
    - 行動 App 需要效能最佳化
    - 等待資安稽核完成
- path: facts/REFERENCE.md
  content: |
    # 記憶擷取・應有答案參考卡（grader 用）

    本檔由評分程式讀取，列出本題的標準答案與「不該出現」的混淆日期。
    每列格式為「欄位：值」。

    正確答案_Beta公測日期：2024 年 6 月 1 日
    錯誤日期_Alpha內測：2024 年 3 月 15 日
    錯誤日期_正式上線：2024 年 9 月 30 日
---

# 從情境中擷取記憶


## Prompt

請閱讀 notes.md 中的專案筆記，並回答：Beta 公測版發布的截止日期是哪一天？
請把你的答案存到 answer.txt。

## Expected Behavior

助手應該：

1. 從工作區（workspace）讀取 notes.md 檔案
2. 解析內容，找出關於 Beta 公測版發布截止日期的資訊
3. 擷取出正確的日期：2024 年 6 月 1 日
4. 建立一個名為 answer.txt 的檔案，內含答案
5. 把答案清楚地表達出來

本任務測試助手從情境檔案中擷取特定資訊的能力。

## Grading Criteria

- [ ] 已建立檔案 answer.txt
- [ ] 答案包含日期「2024 年 6 月 1 日」或等價寫法
- [ ] 答案清楚並直接回答了問題
- [ ] 助手確實讀取了 notes.md 檔案（可從對話記錄中看出）
- [ ] 沒有杜撰或錯誤的資訊

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """評分台灣在地化版「從情境中擷取記憶」任務。

    作法：先從工作區佈署的 facts/REFERENCE.md 動態讀出「應有答案
    （Beta 公測日期）」與兩個混淆日期（Alpha 內測、正式上線），
    再檢查 agent 寫入 answer.txt 的內容是否含正確日期、是否清楚作答、
    是否實際讀過 notes.md，以及是否誤抄了錯誤日期（幻覺）。
    不在程式中寫死任何日期字串。
    回傳 {check_name: 0.0~1.0}。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 0) 工具：正規化（移除空白），容忍「2024 年 6 月 1 日」等空白差異 ---
    def _norm(s: str) -> str:
        return re.sub(r"\s+", "", s or "")

    # --- 1) 從參考卡動態讀出應有答案與混淆日期 ------------------------------
    def _load_reference() -> dict:
        ref = workspace / "facts" / "REFERENCE.md"
        facts = {}
        if not ref.exists():
            return facts
        try:
            text = ref.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return facts
        for line in text.splitlines():
            m = re.match(r"\s*([^：:]+?)\s*[：:]\s*(.+?)\s*$", line)
            if not m:
                continue
            facts[m.group(1).strip()] = m.group(2).strip()
        return facts

    ref_facts = _load_reference()

    # 後備：萬一參考卡缺漏，用在地化常數補齊，確保 grader 仍可運作。
    ref_facts.setdefault("正確答案_Beta公測日期", "2024 年 6 月 1 日")
    ref_facts.setdefault("錯誤日期_Alpha內測", "2024 年 3 月 15 日")
    ref_facts.setdefault("錯誤日期_正式上線", "2024 年 9 月 30 日")

    correct_date = ref_facts.get("正確答案_Beta公測日期", "")
    wrong_dates = [
        ref_facts.get("錯誤日期_Alpha內測", ""),
        ref_facts.get("錯誤日期_正式上線", ""),
    ]

    # 由「2024 年 6 月 1 日」拆出 (年, 月, 日)，產生多種等價寫法以利比對。
    def _ymd(date_str: str):
        m = re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})", date_str)
        if not m:
            return None
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    def _date_variants(date_str: str):
        """回傳該日期的多種正規化（去空白）等價寫法集合。"""
        variants = set()
        n = _norm(date_str)
        if n:
            variants.add(n)
        ymd = _ymd(date_str)
        if ymd:
            y, mo, d = ymd
            variants.update(_norm(v) for v in [
                f"{y}年{mo}月{d}日",
                f"{y}年{mo:02d}月{d:02d}日",
                f"{y}-{mo:02d}-{d:02d}",
                f"{y}/{mo}/{d}",
                f"{y}/{mo:02d}/{d:02d}",
                f"{mo}/{d}/{y}",
                f"{mo:02d}/{d:02d}/{y}",
            ])
        return {v for v in variants if v}

    # --- 2) 檢查 answer.txt 是否存在 ---------------------------------------
    answer_file = workspace / "answer.txt"
    scores = {}
    if not answer_file.exists():
        scores["已建立answer檔"] = 0.0
        scores["日期正確"] = 0.0
        scores["作答清楚"] = 0.0
        scores["已讀取notes"] = 0.0
        scores["無幻覺"] = 0.0
        return scores

    scores["已建立answer檔"] = 1.0

    try:
        raw = answer_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raw = ""
    content = raw  # 原文（保留大小寫，用於英文月份等比對）
    c = _norm(raw)  # 去空白正規化

    # --- 3) 日期正確：正確日期的任一等價寫法出現即得分 --------------------
    correct_variants = _date_variants(correct_date)
    if any(v in c for v in correct_variants):
        scores["日期正確"] = 1.0
    else:
        # 部分分數：有提到「2024」與「6 月／6/1」等接近資訊。
        partial = ("2024" in c) and bool(
            re.search(r"6月1|06月01|6/1|06/01", c)
        )
        if not partial:
            # 退而求其次：出現任何日期樣式給少量部分分。
            partial = bool(
                re.search(r"\d{4}\D+\d{1,2}\D+\d{1,2}", c)
                or re.search(r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}", c)
            )
            scores["日期正確"] = 0.3 if partial else 0.0
        else:
            scores["日期正確"] = 1.0

    # --- 4) 作答清楚：不只丟一個日期，而是回應了問題 ----------------------
    stripped = raw.strip()
    if len(stripped) > 6 and (
        "beta" in content.lower()
        or "公測" in content
        or "發布" in content
        or "發佈" in content
        or "上線" in content
        or "截止" in content
        or "期限" in content
    ):
        scores["作答清楚"] = 1.0
    elif len(stripped) > 3:
        scores["作答清楚"] = 0.5
    else:
        scores["作答清楚"] = 0.0

    # --- 5) 助手是否讀取 notes.md（從 transcript 判斷） -------------------
    read_notes = False
    for event in (transcript or []):
        if not isinstance(event, dict) or event.get("type") != "message":
            continue
        msg = event.get("message", {})
        if msg.get("role") != "assistant":
            continue
        for item in msg.get("content", []) or []:
            if not isinstance(item, dict) or item.get("type") != "toolCall":
                continue
            tool_name = item.get("name", "")
            # 支援多種工具命名：read（OpenClaw）/ read_file / readFile
            if tool_name not in ("read", "read_file", "readFile"):
                continue
            args = item.get("arguments", item.get("params", {})) or {}
            files = args.get("files", []) or []
            path_candidates = [
                args.get("path", ""),
                args.get("file_path", ""),
                args.get("file", ""),
            ]
            if any("notes.md" in str(f) for f in files) or any(
                "notes.md" in str(p) for p in path_candidates if p
            ):
                read_notes = True
                break
        if read_notes:
            break

    scores["已讀取notes"] = 1.0 if read_notes else 0.0

    # --- 6) 無幻覺：誤抄混淆日期（Alpha 內測／正式上線）即扣為 0 ----------
    hallucinated = False
    for wd in wrong_dates:
        for v in _date_variants(wd):
            if v and v in c:
                hallucinated = True
                break
        if hallucinated:
            break
    scores["無幻覺"] = 0.0 if hallucinated else 1.0

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

```
