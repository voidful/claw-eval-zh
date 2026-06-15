---
id: task_second_brain
name: |
  第二大腦知識持久化
category: memory
grading_type: hybrid
timeout_seconds: 300
language: zh
locale: zh-TW
region: TW
source_task_id: task_second_brain
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T138tw_second_brain
workspace_files: []
multi_session: true
sessions:
- id: store_knowledge
  prompt: |
    我希望你幫我記住這項重要資訊。請把它存到一個名為 `memory/MEMORY.md` 的檔案，
    讓你（或未來的某一輪對話）日後可以取回：

    我最喜歡的程式語言是 Rust。我從 January 15, 2024 開始學習它。我的導師名叫
    Dr. Elena Vasquez，來自 Stanford。我正在進行的專案叫做「NeonDB」——它是一個
    分散式鍵值儲存系統（distributed key-value store）。我們團隊的暗號是
    「purple elephant sunrise」。

    請把這些資訊存到 `memory/MEMORY.md`，並跟我確認你已經存好了。
- id: conversation
  prompt: |
    我正在學習哪一種程式語言？還有，我目前的專案叫什麼名字？如有需要，你可以查看
    memory/MEMORY.md 檔案。
- id: new_session_recall
  new_session: true
  prompt: |
    我之前把一些個人資訊存到了一個名為 `memory/MEMORY.md` 的檔案。請讀取該檔案並
    回答下列問題：
    1. 我最喜歡的程式語言是什麼？
    2. 我從何時開始學習它？
    3. 我的導師叫什麼名字、來自哪個單位？
    4. 我的專案叫什麼名字、它的功能是什麼？
    5. 我們團隊的暗號是什麼？

    請根據你在檔案中找到的內容回答全部 5 個問題。
---

# 第二大腦知識持久化


## Prompt

本任務為多輪任務，請見 frontmatter 的 `sessions` 欄位。

## Expected Behavior

助手應該：

1. 第 1 輪（儲存知識）：
   - 接收需要記住的個人資訊
   - 視需要建立 memory/ 目錄
   - 以結構化的格式把資訊儲存到 memory/MEMORY.md
   - 確認資訊已經存進該檔案
   - 本步驟測試助手透過檔案儲存來持久化資訊的能力

2. 第 2 輪（對話）：
   - 從同一輪對話中（或藉由讀取該檔案）回想資訊
   - 正確回答使用者正在學習 Rust
   - 正確說出專案名稱為 NeonDB

3. 第 3 輪（全新對話回想）：
   - 開啟一個全新的對話（模擬使用者稍後再回來）
   - 讀取第 1 輪所建立的 memory/MEMORY.md 檔案
   - 準確回想全部 5 項資訊：
     - 最喜歡的程式語言：Rust
     - 開始學習的日期：January 15, 2024
     - 導師：Dr. Elena Vasquez，來自 Stanford
     - 專案：NeonDB，一個分散式鍵值儲存系統（distributed key-value store）
     - 暗號：「purple elephant sunrise」

本任務測試助手透過檔案儲存來持久化知識、並在全新對話中將其取回的能力。

## Grading Criteria

- [ ] 助手把資訊儲存到記憶系統中（第 1 輪）
- [ ] 助手確認已儲存資訊（第 1 輪）
- [ ] 助手在同一輪對話中正確回想出語言與專案（第 2 輪）
- [ ] 助手在全新對話中嘗試回想記憶（第 3 輪）
- [ ] 正確回想最喜歡的程式語言（Rust）
- [ ] 正確回想開始學習的日期（January 15, 2024）
- [ ] 正確回想導師姓名與所屬單位（Dr. Elena Vasquez，Stanford）
- [ ] 正確回想專案名稱（NeonDB）
- [ ] 正確回想專案描述（分散式鍵值儲存系統）
- [ ] 正確回想暗號（purple elephant sunrise）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the second brain knowledge persistence task.

    Checks if the agent created the memory file with correct content.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check if memory file was created
    memory_file = workspace / "memory" / "MEMORY.md"
    if not memory_file.exists():
        # Try alternative paths
        alt_paths = [
            workspace / "MEMORY.md",
            workspace / "memory.md",
        ]
        for alt in alt_paths:
            if alt.exists():
                memory_file = alt
                break

    if memory_file.exists():
        scores["memory_tool_used"] = 1.0
        content = memory_file.read_text().lower()

        # Check for key facts in the file
        has_rust = "rust" in content
        has_date = "january" in content and "2024" in content
        has_mentor = "elena" in content and "vasquez" in content
        has_project = "neondb" in content
        has_phrase = "purple" in content and "elephant" in content and "sunrise" in content

        fact_count = sum([has_rust, has_date, has_mentor, has_project, has_phrase])
        scores["recall_tool_used"] = fact_count / 5.0
    else:
        scores["memory_tool_used"] = 0.0
        scores["recall_tool_used"] = 0.0

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

### 評分項 1：記憶儲存（權重 15%）

分數 1.0：助手建立 memory/MEMORY.md 檔案，以清楚、有條理的格式儲存使用者的所有資訊，並確認檔案已建立。
分數 0.75：助手把資訊存到檔案，但用了不同的路徑或格式；儲存功能可運作。
分數 0.5：助手有確認收到資訊，但存到檔案的內容不完整或雜亂。
分數 0.25：助手僅把資訊複述出來，並未存到檔案。
分數 0.0：助手未嘗試儲存資訊，或忽略了該需求。

### 評分項 2：同輪對話回想（權重 15%）

分數 1.0：助手在第 2 輪毫不遲疑地正確回答兩個問題（Rust、NeonDB）。
分數 0.75：助手兩題都答對，但帶有些許不確定。
分數 0.5：助手答對其中一題，另一題遺漏或答錯。
分數 0.25：助手明顯吃力，但仍展現出部分回想能力。
分數 0.0：助手無法回想資訊，或給出錯誤答案。

### 評分項 3：跨輪記憶取回（權重 20%）

分數 1.0：助手在全新對話中讀取 memory/MEMORY.md 檔案，並成功取回所儲存的資訊。
分數 0.75：助手取回了大部分資訊，但多花了額外步驟，或先讀錯了檔案。
分數 0.5：助手嘗試取回，但只部分成功找到該檔案。
分數 0.25：助手只做了最低限度的努力去讀取記憶檔案。
分數 0.0：助手未嘗試讀取檔案，或宣稱沒有任何記憶存在。

### 評分項 4：所回想事實的準確度（權重 40%）

分數 1.0：5 項事實全部正確回想：

- Rust 為最喜歡的程式語言
- January 15, 2024 為開始學習的日期
- Dr. Elena Vasquez（來自 Stanford）為導師
- NeonDB 為專案名稱（分散式鍵值儲存系統）
- 「purple elephant sunrise」為暗號

分數 0.8：5 項中有 4 項正確，且沒有捏造。
分數 0.6：5 項中有 3 項正確，且沒有捏造。
分數 0.4：5 項中有 2 項正確，或更多項但帶有些微不準確。
分數 0.2：僅 1 項正確，或有明顯不準確之處。
分數 0.0：沒有任何事實正確，或助手捏造了未曾提供的資訊。

### 評分項 5：回應品質與信心（權重 10%）

分數 1.0：助手有信心且清楚地呈現所回想的資訊，展現出可靠的第二大腦功能。
分數 0.75：回應清楚，但帶有些許不確定。
分數 0.5：回應雜亂無章，或大量含糊其辭。
分數 0.25：回應令人困惑，或助手表達出嚴重的不確定。
分數 0.0：助手拒絕回答，或給出語無倫次的回應。
