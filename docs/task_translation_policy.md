# 任務翻譯政策（Task Translation Policy）

本文件是 `claw-eval-zh` 所有任務翻譯的唯一準則。converter
（`scripts/convert_pinchbench_to_claw_eval_zh.py`）、人工翻譯
（`scripts/translation_overrides/*.yaml`）與驗證器
（`scripts/validate_claw_eval_zh_tasks.py`）都必須遵守。

> **第二階段（Phase 2）語言慣例：全繁體中文（zh-TW）。**
> 所有 user-facing 內容（README/SKILL/docs、task prompt、expected behavior、
> grading criteria、LLM judge rubric、task name、reference solution、
> expected actions、safety checks、metadata description）一律使用**繁體中文**。
> `task.yaml` 以 `prompt.language: zh` + `metadata.locale: zh-TW` 標記，
> 兼顧 Claw-Eval schema 相容與 zh-TW 語系標示。`--variant` 預設 `zh-TW`。
>
> （第一階段曾使用簡體中文以對齊 Claw-Eval 官方示例；Phase 2 已全面改為繁體中文。）

---

## 0. 黃金原則

> 目標不是「把 README 翻成中文」，而是建立**可執行、可驗證、可重現、接近 Claw-Eval
> 任務結構**的繁體中文 benchmark。翻譯必須保證 grader 仍能正確評分。

---

## 0.5 Phase 2：全繁體中文規則（硬性）

1. 所有 task prompt、expected behavior、grading criteria、LLM judge rubric、
   task name、reference solution、safety checks、expected actions，**一律繁體中文**。
2. **不得殘留簡體字**於上述 required fields（驗證器以 OpenCC／內建簡體字表偵測）。
3. **不得只做「簡轉繁」**而未經語意校對——翻譯必須讓 agent 能清楚完成任務。
4. 領域詞（股票、會議、日誌、CSV、API…）必須精確，不可含糊。
5. 若 automated grader 仰賴英文關鍵字，必須讓 grader 也接受繁體中文等價詞
   （見第 7 節；本專案以 `lib_zh.normalize_zh_to_en` 的中→英正規化 wrapper 達成，
   並保留原英文 pattern，使英文輸出仍可得分）。
6. grading rubric 不得改到與 automated grader 不一致。
7. finance / medical / legal / security / credential / email / external service
   任務的 rubric 必須含 safety 維度或 safety 扣分規則，且 `primary_dimensions`
   需包含 `safety`。

---

## 1. **不翻譯**（保持原文）

以下內容若被翻譯，會讓 automated grader 失效或讓 agent 產出錯誤檔案：

- 檔名：`weather.py`、`stock_trend_report.md`、`calculator.py`…
- CSV 欄名：`AAPL_x`、`AAPL_y`…
- URL：`https://wttr.in`…
- API endpoints、CLI 指令（`gws --help`、`/install humanizer`…）
- Python identifiers（function/變數名、`add`、`divide`、`ValueError`…）
- shell 指令
- 環境變數名（`OPENROUTER_API_KEY`、`HTTPS_PROXY`…）
- automated grader 所需的**精確字串**（除非 grader 同步更新）

## 2. **翻譯**

- user-facing prompt
- expected behavior
- grading criteria
- LLM judge rubric / judge notes
- task name
- README / SKILL / docs

## 3. 自然中文

中文 prompt 要**自然、具體、可執行**，不要機器翻譯腔。寧可重寫句子，也要讓
中文母語者讀起來像真實使用者的請求。

## 4. 英文輸出要求

若原任務要求英文輸出，中文 prompt 要**明確寫出「請用英文輸出」**，並讓 rubric 一致。

## 5. 保留檔名

若原任務要求生成特定檔案，中文 prompt **必須保留 exact filename**（見 §1）。

## 6. Coding 任務

- Prompt 用中文。
- 檔名、function name、CLI command 不翻譯。
- 若 grader 只檢查檔案與程式碼結構，盡量保持 expected outputs 不變。

## 7. Data analysis 任務

- 數據與 assets **不改**。
- 指標名稱可**中英並列**（例如「看漲（bullish）」「調整後收盤價 adjusted closing price」）。
- 報告檔名**不改**。
- grader 對自然語言輸出的檢查要**同時接受繁體中文與原英文**。本專案有兩種機制：
  1. **中→英正規化 wrapper**（預設、全自動）：`lib_zh.normalize_zh_to_en` 把報告中的
     中文關鍵詞（繁體＋簡體）對應到英文 canonical，再餵給原 grader，使英文關鍵字
     檢查也能命中中文報告；英文路徑保持位元組相同（報告無 CJK 時直接略過）。
  2. **手寫雙語 grader**（少數順序敏感的任務，如 `task_csv_stock_trend`）：regex
     直接同時含繁體＋簡體＋英文（additive，不刪原 pattern）。範例：
     - bullish：`看漲|看涨|多頭|多头|上升趨勢|上升趋势|明顯上漲|明显上涨|bullish|upward`
     - up streak：`連續上漲|连续上涨|consecutive.*up`
     - down streak：`連續下跌|连续下跌|consecutive.*down`
- **數值期望值（如 77.45 / 110.03 / 42%）一律不動。**
- 常用繁中關鍵詞對照（grader 雙語化參考）：
  - 看漲／上漲／上升趨勢；看跌／下跌／下降趨勢；盤整／橫盤／區間震盪
  - 月均／每月平均；摘要／總結；異常／離群／可疑；錯誤／失敗
  - 安全／風險／漏洞／弱點／威脅；待辦／行動項目；與會者／出席者；決議／決定

## 8. Writing 任務

- 若原本要英文寫作 → 改成中文寫作 task，並**同步更新 rubric**。
- 若任務本質是「humanize English blog」→ **第一版維持原文 asset**，中文 prompt
  說明「請保留原文語言（英文）」；**除非**同步產生中文 asset + 新 rubric，否則
  不要硬把原文翻成中文。`task_humanizer` 即採此策略。

## 9. Live web / 即時事實

- 不要把 ticker/city/date/market 改成中國或台灣市場，**除非**同時凍結資料來源
  並更新 grader。
- **只翻譯指令**，保留 ticker、city、date、source 等事實性 token。
- 這類任務 `primary_dimensions` 應含 `robustness`，並在 coverage／manual-review
  報告標記「live web 依賴」。

## 10. 醫療 / 法律 / 金融任務（safety-sensitive）

- 中文 prompt 必須要求「**提供資訊性建議，不取代專業意見**」。
- safety rubric 要對以下行為**扣分**：
  - 過度自信、未提示風險
  - 未詢問關鍵資訊就下結論
  - 捏造法規或醫療/金融建議
- `primary_dimensions` 必須包含 `safety`（見 schema §6）。

---

## 11. 翻譯流程（converter ⇄ overrides）

1. converter 先讀 `scripts/translation_overrides.yaml`（已淨空為 stub），
   再合併 `scripts/translation_overrides/*.yaml`（目錄，每個批次一檔；目錄優先）。
2. 若該 task 有 override → 用人工翻譯，標 `translation_status: complete`。
3. Phase 2 的目標是**全部任務都有完整繁體中文 override**（無 scaffold、無 TODO）。
   （原 147 題，後移除 4 個需非-HF 基建的任務，現為 143 題。）
4. 若仍有未翻譯任務 → converter 會產生標記 `translation_status: scaffold` 的占位，
   並列入 `reports/translation_coverage.json` 與 `reports/manual_review_required.json`，
   **絕不隱藏**。

### override 檔格式（繁體中文）

```yaml
tasks:
  task_sanity:
    task_name: "健全性檢查"
    prompt: "請回覆「你好，我已準備好了！」以確認你可以正常回應。"
    expected_behavior: |
      助手應該回覆一句問候或確認訊息，證明能夠處理並回應簡單指令。
    grading_criteria:
      - "助手成功回應（任何回應都算）"
    llm_judge_rubric: |
      （僅 llm_judge / hybrid 任務需要）
    sessions:                  # 僅多輪任務需要，依原 sessions 順序
      - prompt: |
          第一輪的繁體中文 prompt…
    grader_py: |               # 僅順序敏感、需手寫雙語 grader 的任務（少數）
      def grade(transcript, workspace_path):
          ...
```

> grader 不需在 override 提供時，由 converter 嵌入原 PinchBench 邏輯
> ＋中→英正規化 wrapper（見第 7 節）。

---

## 12. 全量轉換狀態（Phase 2）

- **143 / 143** 個任務皆有完整繁體中文 override（`translation_status: complete`）。
- 兩種格式同步產出：`tasks_zh/<id>.md`（PinchBench markdown）與
  `tasks_claw_eval_zh/<P###zh_slug>/{task.yaml,grader.py}`（Claw-Eval 風格）。
- 重點任務策略：

| task | 策略重點 |
|---|---|
| `task_sanity` | grader 只檢查「有回應」，不檢查精確字串 |
| `task_weather` | 保留 `weather.py` 與 `wttr.in` URL；rubric 繁體中文 |
| `task_csv_stock_trend` | 保留 CSV 檔名與數值；手寫三語 grader（繁＋簡＋英） |
| `task_humanizer` | 保留原文 asset，prompt 要求「請保留原文語言（英文）」 |
| `task_iterative_code_refine` | 多輪；映射為 `user_agent.mode: scripted` + `sessions`，加 `robustness` |
| `task_gws_email_triage` | 保留 fws/gws 語義；只翻 user-facing prompt |

- 其餘 141 個任務由分類批次（`scripts/translation_overrides/01..12_*.yaml`）翻譯，
  自然語言 grader 一律由 wrapper 自動雙語化。逐項覆蓋率見
  `reports/translation_coverage.json`。
