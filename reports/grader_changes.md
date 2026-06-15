# Grader 繁中適配記錄（grader_changes）

本檔記錄 Phase 2 為了讓**繁體中文報告也能被 automated grader 評分**所做的調整。
核心原則：**保留原 PinchBench 確定性評分邏輯**，僅以 additive 方式讓中文等價詞也能命中。

## 機制總覽

claw-eval-zh 用兩種互補機制達成 grader 雙語化：

### 1. 中→英正規化 wrapper（預設，套用到所有 automated／hybrid grader）

- 來源：`scripts/lib_zh.py::normalize_zh_to_en` + 由 converter 嵌入每個 `grader.py`
  的 wrapper（見 `GRADER_NORMALIZE_WRAPPER`）。
- 行為：grading 前，若報告檔（`.md`/`.txt`/`.rst`/`.markdown`）含 CJK，建立一份
  shadow 複本，在**檔尾附加**該報告出現過的中文關鍵詞對應的英文 canonical
  （例如「看漲」→`bullish`、「平均」→`average mean`、「異常」→`anomaly`、
  「錯誤」→`error`、「與會者」→`attendee`），再餵給**原始**grader。
- 原文完整保留（不 inline 插入），因此：
  - 順序敏感、含中文 phrase 的手寫 grader 仍能對原中文比對；
  - 原英文 keyword 檢查（`re.search('bullish', content)`）也能命中中文報告。
- **英文路徑位元組相同**：報告若無 CJK，wrapper 直接 passthrough、不複製、不更動，
  原英文 benchmark 行為完全不變（已由 `test_english_path_still_loads` 驗證）。
- 僅做 additive：**不改動**任何數值／檔案存在／工具呼叫／指令等語言無關檢查。

涵蓋範圍：所有 grading_type 為 `automated` 或 `hybrid` 的任務（含 coverage 報告
標記的 63 個「grader 仰賴英文自然語言關鍵字」任務）皆由 wrapper 自動雙語化。

### 2. 手寫雙語 grader（順序敏感的特例）

| task_id | 原本檢查什麼 | 新增哪些中文 pattern | 為什麼不改其他部分 |
|---|---|---|---|
| `task_csv_stock_trend`（`P053zh_csv_stock_trend`） | 報告中的趨勢方向、月度拆解、最長連漲/連跌、關鍵區段，以及起始/結束價、漲跌幅等**數值** | 趨勢方向加 `看漲\|看涨\|多頭\|多头\|上升趨勢…\|牛市`；連漲加 `連續上漲\|连续上涨\|8月…`；連跌加 `連續下跌\|连续下跌\|1月…`；月度加 `N月`；區段加 `1月…回落/突破`、`11月…新高` 等（繁＋簡並列） | 數值 regex（`77\.4[45]`、`110\.0[23]`、`4[12]\.\d+%`）與報告檔名 fallback 清單**完全不動**；只在「自然語言描述」這類 criterion 上增補中文，確保分數仍反映實際完成度 |

> 之所以對 `csv_stock_trend` 手寫，是因為其連漲/連跌判斷是**順序敏感**
> （`9 … consecutive`、`down … 5 … consecutive`），wrapper 的「檔尾附加英文」無法
> 保證順序，故直接在 grader 內以中文 phrase（順序自然）比對。其餘自然語言任務多為
> 「關鍵詞存在性」檢查，wrapper 即可正確覆蓋。

## 未改動的部分（刻意保留）

- 所有**數值期望值**（價格、百分比、計數、IP、ID、日期）一律不動。
- 所有**檔名／CSV 欄名／指令／工具名／identifier**比對不動。
- `llm_judge`-only 任務的 `grader.py` 維持回傳 `{}`（無確定性分數），語意評分交給
  `task.yaml` 的 `judge_rubric`。
- transcript-based 檢查（如 `gws messages list`、`drafts create` 等指令偵測）為英文
  CLI token，語言無關，不需改動。

## 驗證

- `test_generated_graders_full.py`：147 個 grader 全部可 import；對
  `sanity`/`weather`/`csv_stock_trend` 做 smoke grading；並驗證
  `csv_gdp_ranking` 的**中文報告得分 == 英文報告得分**（wrapper parity）。
- `test_english_path_still_loads.py`：原英文 `task_weather` grader 對英文工作區仍
  正常評分（> 0.5）。

## 風險與後續

- wrapper 對「順序敏感」或「英文片語結構」的 criterion 可能漏分（少數）；這些任務已在
  `reports/manual_review_required.json` 以「grader 仰賴英文自然語言關鍵字」標記
  （severity 至少 medium），建議人工抽查並在必要時改為手寫雙語 grader。
- 任何被修改的 grader（目前僅 `csv_stock_trend`）在 manual-review 報告標 high。
