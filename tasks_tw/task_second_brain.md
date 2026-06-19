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
workspace_files:
- path: facts/REFERENCE.md
  content: |
    # 第二大腦・應有事實參考卡（grader 用）

    本檔由評分程式讀取，列出使用者在第 1 輪口述、應被寫入
    `memory/MEMORY.md` 的標準事實。每列格式為「欄位：值」。

    最愛語言：Rust
    開始日期：2024 年 1 月 15 日
    導師姓名：林淑芬 教授
    導師單位：國立臺灣大學
    專案名稱：NeonDB
    專案描述：分散式鍵值儲存系統
    團隊暗號：紫色大象日出
multi_session: true
sessions:
- id: store_knowledge
  prompt: |
    我希望你幫我記住這項重要資訊。請把它存到一個名為 `memory/MEMORY.md` 的檔案，
    讓你（或未來的某一輪對話）日後可以取回：

    我最喜歡的程式語言是 Rust。我從 2024 年 1 月 15 日開始學習它。我的導師名叫
    林淑芬 教授，來自國立臺灣大學。我正在進行的專案叫做「NeonDB」——它是一個
    分散式鍵值儲存系統。我們團隊的暗號是「紫色大象日出」。

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
     - 開始學習的日期：2024 年 1 月 15 日
     - 導師：林淑芬 教授，來自國立臺灣大學
     - 專案：NeonDB，一個分散式鍵值儲存系統
     - 暗號：「紫色大象日出」

本任務測試助手透過檔案儲存來持久化知識、並在全新對話中將其取回的能力。

## Grading Criteria

- [ ] 助手把資訊儲存到記憶系統中（第 1 輪）
- [ ] 助手確認已儲存資訊（第 1 輪）
- [ ] 助手在同一輪對話中正確回想出語言與專案（第 2 輪）
- [ ] 助手在全新對話中嘗試回想記憶（第 3 輪）
- [ ] 正確回想最喜歡的程式語言（Rust）
- [ ] 正確回想開始學習的日期（2024 年 1 月 15 日）
- [ ] 正確回想導師姓名與所屬單位（林淑芬 教授，國立臺灣大學）
- [ ] 正確回想專案名稱（NeonDB）
- [ ] 正確回想專案描述（分散式鍵值儲存系統）
- [ ] 正確回想暗號（紫色大象日出）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """評分台灣在地化版「第二大腦」記憶持久化任務。

    作法：先從工作區佈署的 facts/REFERENCE.md 動態讀出「應有事實」，
    再檢查 agent 產生的 memory/MEMORY.md 是否含有這些中文事實，
    不在程式中寫死任何台灣導師姓名／單位等內容。
    回傳 {check_name: 0.0~1.0}。
    """
    import re
    from pathlib import Path

    workspace = Path(workspace_path)

    # --- 1) 從參考卡動態讀出應有事實 ------------------------------------
    def _load_reference():
        ref = workspace / "facts" / "REFERENCE.md"
        facts = {}
        if not ref.exists():
            return facts
        try:
            text = ref.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return facts
        # 接受全形或半形冒號
        for line in text.splitlines():
            m = re.match(r"\s*([^：:]+?)\s*[：:]\s*(.+?)\s*$", line)
            if not m:
                continue
            key, val = m.group(1).strip(), m.group(2).strip()
            facts[key] = val
        return facts

    ref_facts = _load_reference()

    # 解析後備：萬一參考卡缺漏，用在地化常數補齊，確保 grader 仍可運作。
    fallback = {
        "最愛語言": "Rust",
        "開始日期": "2024 年 1 月 15 日",
        "導師姓名": "林淑芬 教授",
        "導師單位": "國立臺灣大學",
        "專案名稱": "NeonDB",
        "專案描述": "分散式鍵值儲存系統",
        "團隊暗號": "紫色大象日出",
    }
    for k, v in fallback.items():
        ref_facts.setdefault(k, v)

    # --- 2) 找出 agent 產生的記憶檔 -------------------------------------
    memory_file = workspace / "memory" / "MEMORY.md"
    if not memory_file.exists():
        for alt in (workspace / "MEMORY.md", workspace / "memory.md"):
            if alt.exists():
                memory_file = alt
                break

    scores = {}

    if not memory_file.exists():
        scores["記憶檔已建立"] = 0.0
        scores["回想_最愛語言"] = 0.0
        scores["回想_開始日期"] = 0.0
        scores["回想_導師"] = 0.0
        scores["回想_專案名稱"] = 0.0
        scores["回想_專案描述"] = 0.0
        scores["回想_暗號"] = 0.0
        return scores

    scores["記憶檔已建立"] = 1.0
    try:
        content = memory_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        content = ""

    # --- 3) 比對各項事實（中文關鍵字 / 數值） --------------------------
    def _norm(s):
        # 去掉空白以容忍「2024 年 1 月 15 日」vs「2024年1月15日」等差異。
        return re.sub(r"\s+", "", s)

    c = _norm(content)

    # 最愛語言：Rust（不分大小寫）
    scores["回想_最愛語言"] = 1.0 if "rust" in content.lower() else 0.0

    # 開始日期：容忍空白差異，並接受 2024 + 1 月 15 為核心數值。
    date_val = _norm(ref_facts.get("開始日期", ""))
    has_date = bool(date_val) and date_val in c
    if not has_date:
        has_date = ("2024" in c) and ("1月15" in c or "01月15" in c)
    scores["回想_開始日期"] = 1.0 if has_date else 0.0

    # 導師：姓名（去頭銜後的核心姓名）+ 單位皆須出現。
    mentor_name = ref_facts.get("導師姓名", "")
    mentor_core = _norm(re.sub(r"(教授|老師|博士|Dr\.?|博士後)", "", mentor_name)).strip()
    mentor_unit = _norm(ref_facts.get("導師單位", ""))
    has_name = bool(mentor_core) and mentor_core in c
    # 單位容忍「國立臺灣大學」與簡稱「臺灣大學」/「台灣大學」。
    unit_variants = {mentor_unit}
    if mentor_unit:
        unit_variants.add(mentor_unit.replace("國立", ""))
        unit_variants.add(mentor_unit.replace("臺", "台"))
        unit_variants.add(mentor_unit.replace("國立", "").replace("臺", "台"))
    has_unit = any(u and u in c for u in unit_variants)
    if has_name and has_unit:
        scores["回想_導師"] = 1.0
    elif has_name or has_unit:
        scores["回想_導師"] = 0.5
    else:
        scores["回想_導師"] = 0.0

    # 專案名稱：NeonDB（不分大小寫）
    proj_name = ref_facts.get("專案名稱", "")
    scores["回想_專案名稱"] = (
        1.0 if proj_name and proj_name.lower() in content.lower() else 0.0
    )

    # 專案描述：分散式鍵值儲存系統（容忍空白）
    proj_desc = _norm(ref_facts.get("專案描述", ""))
    scores["回想_專案描述"] = 1.0 if proj_desc and proj_desc in c else 0.0

    # 暗號：紫色大象日出（容忍空白）
    phrase = _norm(ref_facts.get("團隊暗號", ""))
    scores["回想_暗號"] = 1.0 if phrase and phrase in c else 0.0

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
- 2024 年 1 月 15 日 為開始學習的日期
- 林淑芬 教授（來自國立臺灣大學）為導師
- NeonDB 為專案名稱（分散式鍵值儲存系統）
- 「紫色大象日出」為暗號

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
