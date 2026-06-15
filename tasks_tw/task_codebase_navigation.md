---
id: task_codebase_navigation
name: 程式碼庫導覽（台灣開發團隊）
category: coding
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_codebase_navigation
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: manual_review_only
claw_eval_tw_id: T037tw_codebase_navigation
workspace_files: []
---

# 程式碼庫導覽（台灣開發團隊）

## Prompt

你的台灣開發團隊拿到一個不熟悉的開源專案：GitHub 上的 **expressjs/express**
儲存庫（https://github.com/expressjs/express）。

請回答下列關於這個程式庫中身分驗證（authentication）與請求處理運作方式的問題，
並將你的答案儲存到 `codebase_report.md`。

1. **路由（routing）在哪裡處理？** 找出負責路由比對與分派（dispatching）的
   檔案。請提供相對於儲存庫根目錄的檔案路徑。
2. **request 與 response 物件在哪裡被擴充？** 找出新增 Express 專屬方法
   （例如 `res.send`、`res.json`、`req.params`）的檔案。請提供檔案路徑。
3. **middleware 的執行是如何運作的？** 追蹤從請求抵達、到 middleware stack
   被執行的程式碼路徑。描述其中涉及的關鍵函式與檔案。
4. **身分驗證 middleware 會在哪裡接入？** 根據這個架構，說明像 `passport`
   這樣的 middleware 會在何處、以何種方式整合。引用你所找到的具體程式碼模式。

每個答案都請附上你所檢視的具體檔案路徑與行號範圍。在有助於說明時請使用程式碼
片段。

注意：這是即時資料（程式庫會持續演進）。請在報告中**標示你所參照的儲存庫來源
與分支／commit、標示查詢日期**，並說明**資料限制與不確定性**（檔案路徑與行號
可能因版本而異）。切勿捏造檔案路徑或行號。檔名、程式碼 asset 與識別字保留原文。

## Expected Behavior

助手應該：

1. clone 或瀏覽 Express.js 儲存庫以檢視其原始碼
2. 在程式庫中導覽，找出路由邏輯（`lib/router/index.js`、`lib/router/route.js`、
   `lib/router/layer.js`）
3. 找出 request／response 的擴充（`lib/request.js`、`lib/response.js`）
4. 透過 router 的 `handle` 方法追蹤 middleware 的執行
5. 說明 middleware 模式，以及 auth 會在何處接入
6. 將一份結構良好的報告儲存到 `codebase_report.md`

助手可使用 `git clone`、`gh` CLI、web fetch，或任意組合來探索程式碼。重點在於
展現出導覽並理解一個不熟悉的程式庫的能力。因為程式庫會持續演進，正確行為是
**標示所參照的儲存庫來源與分支／commit、標示查詢日期，並說明資料限制與不確定性**
（路徑與行號可能因版本而異），而非捏造檔案路徑或行號。

## Grading Criteria

- [ ] 已建立檔案 `codebase_report.md`
- [ ] 報告找出路由相關檔案（lib/router/）
- [ ] 報告找出 request／response 擴充檔案
- [ ] 報告說明 middleware 的執行流程
- [ ] 報告討論身分驗證的整合接入點
- [ ] 檔案路徑具體且正確
- [ ] 包含程式碼片段或行號參照
- [ ] 標示所參照的儲存庫來源／分支／commit 與查詢日期，並說明資料限制與不確定性

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)
    report = workspace / "codebase_report.md"

    if not report.exists():
        return {
            "file_created": 0.0,
            "routing_identified": 0.0,
            "req_res_identified": 0.0,
            "middleware_explained": 0.0,
            "auth_discussed": 0.0,
        }

    scores["file_created"] = 1.0
    content = report.read_text().lower()

    # Check for routing file identification
    routing_keywords = ["lib/router", "router/index", "route.js", "layer.js", "dispatch"]
    routing_matches = sum(1 for k in routing_keywords if k in content)
    scores["routing_identified"] = min(1.0, routing_matches / 2)

    # Check for request/response identification
    reqres_keywords = ["lib/request", "lib/response", "res.send", "res.json", "req.params"]
    reqres_matches = sum(1 for k in reqres_keywords if k in content)
    scores["req_res_identified"] = min(1.0, reqres_matches / 2)

    # Check for middleware explanation
    mw_keywords = ["middleware", "next(", "next function", "stack", "handle", "use("]
    mw_matches = sum(1 for k in mw_keywords if k in content)
    scores["middleware_explained"] = min(1.0, mw_matches / 2)

    # Check for auth discussion
    auth_keywords = ["auth", "passport", "middleware", "hook", "session", "token"]
    auth_matches = sum(1 for k in auth_keywords if k in content)
    scores["auth_discussed"] = min(1.0, auth_matches / 2)

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

## LLM Judge Rubric

### 評分項 1：程式庫理解（權重 30%）

**1.0 分**：報告展現對 Express 內部運作的深入理解。正確找出 router、layer 與
route 抽象。從 `app.handle` 一路追蹤到 router 分派的完整請求生命週期。引用具體
函式及其角色。

**0.75 分**：報告正確找出關鍵檔案並說明整體架構，但遺漏了 middleware 鏈或路由
內部的一些細微之處。

**0.5 分**：報告找出部分正確的檔案，但說明流於表面或含有些微不準確之處。

**0.25 分**：報告提及 Express 的檔案，但對它們之間的關聯理解有限。

**0.0 分**：報告缺失，或看不出有探索程式庫的跡象。

### 評分項 2：導覽策略（權重 20%）

**1.0 分**：助手使用有效的策略來導覽程式庫——搜尋關鍵詞、追蹤 import、先閱讀
進入點再深入細節。有系統化探索的證據。

**0.75 分**：助手展現出合理的導覽能力，但本可更有效率或更有系統。

**0.5 分**：助手找到一些相關程式碼，但導覽雜亂或缺乏效率。

**0.25 分**：助手在尋找相關程式碼上明顯吃力。

**0.0 分**：看不出有程式庫導覽的跡象。

### 評分項 3：具體性與佐證（權重 20%）

**1.0 分**：報告包含具體的檔案路徑、行號或範圍，以及直接支持每個答案的程式碼
片段。各項主張都有具體參照佐證。

**0.75 分**：報告包含檔案路徑與部分程式碼參照，但並非所有主張都充分佐證。

**0.5 分**：報告有一些檔案路徑，但缺少程式碼片段或具體的行號參照。

**0.25 分**：報告多為籠統的陳述，缺乏具體的程式碼參照。

**0.0 分**：沒有任何對原始碼的具體參照。

### 評分項 4：來源、查詢日期與不確定性（權重 20%）

**1.0 分**：明確標示所參照的儲存庫來源（expressjs/express）與分支或 commit、
標示查詢日期，並說明資料限制與不確定性（檔案路徑與行號可能因版本而異）。明顯
以引用實際程式碼取代捏造的路徑或行號。

**0.75 分**：有標示來源／分支並標示查詢日期，對版本不確定性有提及但較簡略。

**0.5 分**：有標示部分來源或查詢日期，但不一致，或未說明版本可能的差異。

**0.25 分**：僅零星提及來源或日期，未說明不確定性。

**0.0 分**：完全未標示來源、分支或查詢日期，或出現捏造且未加註的路徑／行號。

### 評分項 5：Auth 整合分析（權重 10%）

**1.0 分**：清楚說明身分驗證 middleware 如何與 Express 的 middleware 模式整合。
引用 `app.use()`、middleware 排序與 `next()` 模式。可能引用真實的 auth 函式庫。

**0.75 分**：對 auth 整合說明良好，僅有些微缺漏。

**0.5 分**：基本說明正確，但缺乏深度。

**0.25 分**：說明含糊或部分不正確。

**0.0 分**：沒有討論身分驗證的整合。
