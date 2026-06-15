# claw-eval-zh 驗證報告（Phase 2：全繁體中文）

本報告為 Phase 2 完成後的狀態快照。機器可讀版本見
[`reports/translation_coverage.json`](../reports/translation_coverage.json)、
[`reports/validation_zh.json`](../reports/validation_zh.json) 與
[`reports/manual_review_required.json`](../reports/manual_review_required.json)。

驗證指令：

```bash
python -m compileall scripts                       # 全部 scripts 可編譯
python scripts/validate_claw_eval_zh_tasks.py      # 0 errors（產生 validation_zh.*）
pytest -q                                          # 全部 offline 測試通過
```

---

## 1. 覆蓋率（全量）

| 指標 | 數值 |
|---|---|
| 原始 manifest 任務數 | **147** |
| `tasks_zh/`（PinchBench markdown，繁體中文） | **147 / 147** |
| `tasks_claw_eval_zh/`（Claw-Eval 風格 folder） | **147 / 147** |
| `translation_status: complete` | **147** |
| `translation_status: scaffold` | 0 |
| TODO / placeholder 殘留（required fields） | **0** |
| 簡體字殘留（required user-facing fields，OpenCC 偵測） | **0** |
| English leakage（prompt，>0.65） | **0**（reference/rubric 有 1 個警告，見下） |

## 2. 繁體中文檢查

- 偵測工具：`scripts/lib_zh.py`，OpenCC 可用時以 `t2s` 往返判定，否則使用內建
  簡體字表；並排除「一簡多繁」與台灣標準異體（干/里/面/群/台/峰/吃/雇…）避免誤判。
- 結果：147 個 `task.yaml` 的 user-facing 欄位與 147 個 `tasks_zh/*.md` 的內文
  （已排除 code fence／URL／檔名）**皆無簡體字殘留**。
- 防呆：`test_no_simplified_required_fields.py` 同時驗證偵測器**會**抓到真簡體、
  且**不會**誤判繁體與異體字（避免 validator 永遠 pass）。

## 3. Runner / 指標

- `--language en|zh`、`--tasks-dir`、`--trials`（= `--runs`）、`--pass-threshold`
  皆支援；結果 JSON 含 `passk`（pass@k / pass^k）區塊與每任務 `pass_at_k`/`pass_k`，
  並保留原 `mean/std/min/max`。
- 英文路徑（`--language en`，預設）行為與上游一致，未被破壞。

## 4. Grader 狀態

- 147 個 `grader.py` **全部可 import**、`grade()` 可呼叫。
- 自然語言輸出任務以中→英正規化 wrapper 自動雙語化；`csv_stock_trend` 為手寫三語
  grader。詳見 [`reports/grader_changes.md`](../reports/grader_changes.md)。
- 驗證：中文報告得分 == 英文報告得分（`csv_gdp_ranking` parity 測試通過）。

## 5. 分類統計（來自 coverage 報告）

| 類別 | 數量 |
|---|---|
| 安全敏感（safety-sensitive） | 38 |
| live web 依賴 | 16 |
| 多輪（multi-turn） | 4 |
| 多模態（multimodal） | 12 |
| 整合 / 外部服務（integration） | 4 |
| grader 被修改 | 1（`csv_stock_trend`） |
| grader 仰賴英文自然語言關鍵字（靠 wrapper 對應） | 63 |

## 6. 需要人工審查（manual review）

- 總計 **138** 個任務列入 `reports/manual_review_required.json`
  （high：**50**，medium：**88**）。
- High severity 觸發條件：安全敏感領域、grader 被修改、live web 依賴、destructive
  指令／憑證處理、原本主觀的 LLM judge rubric。
- High severity 清單（節錄；完整見 JSON）：
  - 金融：`task_stock`、`task_financial_ratio_calculation`、`task_earnings_analysis`、
    `task_csv_finance_report`、`task_csv_pension_*`、`task_csv_stock_*`
  - 法律：`task_contract_analysis`、`task_eu_regulation_research`
  - 資安：`task_log_ssh_failed_logins`、`task_cve_security_triage`（medium 起）、
    `task_log_ssh_*`
  - email／外部服務：`task_email*`、`task_gws_*`、`task_gh_issue_triage`
  - live web：`task_*_research`、`task_polymarket_briefing`、`task_weather`
  - grader 修改：`task_csv_stock_trend`

## 7. 已知限制 / 風險

1. **wrapper 對順序敏感的英文片語 criterion 可能漏分**（少數自然語言 grader）；
   已在 manual-review 標記，建議人工抽查或改手寫雙語 grader。
2. **schema 對上游的偏離**：`task.yaml` 採 `check.entrypoint: grader.py`、
   擴充 `source`/`fixtures`/`metadata`、`user_agent.mode: scripted`+`sessions`。
   接官方 Claw-Eval harness 前需轉換（見 `docs/claw_eval_zh_schema.md` §9）。
   本專案僅宣稱「**參考 Claw-Eval 風格**」，非官方 runner 可直接執行。
3. **live web 任務**只翻指令、保留 ticker/city/date/source，未凍結資料來源，
   重跑結果可能變動（影響可重現性）。
4. **English-output 任務**（如 `task_humanizer`、英文 blog/email/README/commit）
   prompt 明確要求保留英文輸出；其 reference/rubric 可能含較多英文（屬預期），
   validator 對 reference/rubric 的 leakage 僅以 warning 呈現。
5. **批次翻譯由多個 subagent 平行產生**並經 OpenCC 簡體掃描與 schema 驗證；
   高風險領域仍建議人工逐項覆核（見第 6 節）。
