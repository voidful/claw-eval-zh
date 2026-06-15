# Phase 4 初始審計報告（Release-candidate audit）

本回合僅執行 **Phase A–C**（審計、advisory 收斂、高風險審查矩陣）；fixtures、gold
examples、official export adapter（Phase D–K）待矩陣經人工確認後再進行。

## 1. 現況檢查

| 檢查 | 結果 |
|---|---|
| `python -m compileall scripts` | ✅ PASS |
| `validate_claw_eval_zh_tasks.py`（Phase 2） | ✅ 0 errors, 1 warning |
| `validate_tw_localization.py`（Phase 3） | ✅ 0 errors, **14 warnings（advisory）** |
| `pytest -q` | ✅ 97 passed |

三層（en / zh / tw）共存，Phase 2、Phase 3 皆未回歸。

## 2. 14 個 advisory warnings 逐項

| # | task | 類型 | 處理方向 |
|---|---|---|---|
| 1 | T002 calendar | safety_rubric | 補 safety_checks（確認與會者/不擅自寄送） |
| 2 | T004 todo_list_cleanup | safety_rubric | 強化 safety_checks（含風險關鍵詞） |
| 3 | T031 playwright_e2e | us_residue（zip code） | grader 不依賴 → 在地化為台灣郵遞區號；否則 accept |
| 4 | T033 cicd_pipeline_debug | safety_rubric | 補 safety_checks（不可逆部署需確認/不外洩憑證） |
| 5 | T035 k8s_debugging | safety_rubric | 補 safety_checks |
| 6 | T047 financial_ratio_calculation | safety_rubric | 補 safety_checks（非投資建議/不捏造） |
| 7 | T053 csv_stock_trend | safety_rubric | 補 safety_checks |
| 8 | T054 csv_stock_volatility | safety_rubric | 補 safety_checks |
| 9 | T055 csv_stock_best_worst | safety_rubric | 補 safety_checks |
| 10 | T073 csv_cities_filter | us_residue（california） | 固定全球 CSV → accepted_warning（Phase D 補台灣城市 fixture） |
| 11 | T076 csv_pension_ranking | safety_rubric | 補 safety_checks |
| 12 | T077 csv_pension_liability | safety_rubric | 補 safety_checks |
| 13 | T090 log_ssh_failed_logins | safety_rubric | 補 safety_checks（防禦導向/個資） |
| 14 | T092 log_ssh_successful | safety_rubric | 補 safety_checks |

- 可直接修（補 safety_checks）：12 個 safety_rubric。
- 需新 fixture：csv_cities_filter（Phase D）→ 本階段先 accepted_warning。
- 只能 accepted：csv_cities_filter（固定全球資料集）。playwright_e2e 視 grader 而定。

## 3. 62 個 high-severity 分流（依 domain）

| domain | 數 | 主要處理原則 |
|---|---|---|
| finance_or_legal | 22 | 改「分析/風險因素/資料限制」，rubric 扣分投資/法律定論；不捏造 |
| security | 16 | 防禦/修補優先序/通報；rubric 扣分提供攻擊步驟 |
| live_web | 12 | 標示查詢日期/來源/限制；不寫死即時值；judge 評分 |
| safety | 12 | email/外部服務：避免未授權寄送/刪除/外洩；不可逆操作需確認 |

依策略：context_replace 25、manual_review_only 16、language_polish 5、
fixture_replace 4、copy 12。

## 4. Phase 4 修改範圍（本回合 A–C）

1. validator 加入 `tw_accepted_warnings.json` 機制與 `--strict-release`，summary 分
   errors / unresolved_warnings / accepted_warnings。
2. 對 12 個 safety_rubric 補 `safety_checks`（不改 deterministic 答案）。
3. 2 個 US-residue：playwright_e2e 視 grader 修復或 accept；cities_filter accept。
4. 產生 `reports/tw_high_risk_review_matrix.{csv,md}`，前 20（含全部）逐題分流。

## 5. 風險

- 補 safety_checks 不應改變 grader 的 deterministic 評分（safety_checks 是 task.yaml
  欄位，不進 automated grader 計分）。
- 編輯 anchor（00_anchors.yaml）時不可破壞既有 grader_py。
- US-residue 在地化 playwright zip code 前須確認 grader 未檢查該 literal。
- accepted_warning 不得淪為偷懶：每筆需 reason / risk / future_action / owner。
