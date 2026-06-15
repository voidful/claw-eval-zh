# 台灣在地版驗證報告（tw_validation_report）

Phase 3 完成後狀態快照。機器可讀版本：
[`reports/validation_tw.json`](../reports/validation_tw.json)、
[`reports/tw_localization_coverage.json`](../reports/tw_localization_coverage.json)、
[`reports/tw_manual_review_required.json`](../reports/tw_manual_review_required.json)。

驗證指令：

```bash
python -m compileall scripts
python scripts/validate_claw_eval_zh_tasks.py     # Phase 2，仍通過
python scripts/validate_tw_localization.py        # Phase 3，0 errors
pytest -q
```

## 1. 覆蓋率（全量）

| 指標 | 數值 |
|---|---|
| 原始 manifest 任務數 | 147 |
| `tasks_tw/` | **147 / 147** |
| `tasks_claw_eval_tw/` | **147 / 147** |
| 每題皆在 localization map | ✅ |
| 簡體字殘留（user-facing） | **0** |
| TODO / placeholder 殘留 | **0** |
| TW validator 錯誤 | **0** |
| TW validator 警告（advisory） | 14（US 殘留 + 風險語言提示） |

## 2. 在地化策略分佈

| strategy | 數 | degree |
|---|---|---|
| copy | 53 | none |
| language_polish | 15 | light |
| context_replace | 56 | medium |
| manual_review_only | 16 | heavy |
| fixture_replace | 4 | heavy |
| new_tw_variant | 3 | heavy |

degree：none 53 / light 15 / medium 56 / heavy 23。

## 3. Anchor 任務（深度台灣化，已完成）

| 任務 | 在地化重點 | grader |
|---|---|---|
| `task_sanity` | 台灣自然繁中；只檢查有回覆 | 不變 |
| `task_weather` | 地點改台北（Taipei）；保留 weather.py / wttr.in | 重寫（Taipei regex） |
| `task_calendar` | 台灣同事/標題/Asia/Taipei 時區 | 重寫（+ 非美國時區檢查） |
| `task_csv_stock_trend` | 台積電 2330 真實 TWSE 資料 | 重寫（重算全部數值） |
| `task_csv_stock_volatility` | 同上 fixture，波動率重算 | 重寫 |
| `task_csv_stock_best_worst` | 同上 fixture，最佳/最差日重算 | 重寫 |
| `task_financial_ratio_calculation` | 示例台灣公司財報 fixture（周轉率 6.0） | 重寫（+ safety_note） |
| `task_email` / `task_email_reply_drafting` | 台灣商務 Email 語氣 | 不變（llm_judge） |
| `task_subway_navigation` | 框架在地化（asset 為固定地圖） | 不變（llm_judge） |
| `task_contract_analysis` | 繁中合約審閱，不給法律定論 | 不變（llm_judge） |
| `task_cve_security_triage` | 台灣企業 IT 通報/修補優先 | 不變 |
| `task_byok_best_practices` | 台灣個資法/資安合規背景 | 不變（llm_judge） |
| `task_gws_*`（3） | 台灣職場 Email/行事曆/任務 | 不變（保留 gws 指令） |
| `task_meeting_*`（3 new_tw_variant） | 台灣組織框架，保留英文 transcript | 不變 |

## 4. 新增 fixtures（見 `reports/tw_fixture_manifest.json`）

- `assets/tw/csvs/tw_stock_2330_2024.csv` — 台積電 2330 2024 真實 TWSE 公開資料
  （242 日；起 593／結 1,075／+81.28%）。
- `assets/tw/docs/tw_company_fy2024_financials.md` — 示例（synthetic）台灣公司財報。

## 5. 需人工審查（`reports/tw_manual_review_required.json`）

> **Phase 4 更新**：高風險已重新分流為 **58 fixed / 5 requires_external_human_review**
> （見 `reports/tw_high_risk_review_matrix.{csv,md}`），leaderboard blockers 由 21 降為 **5**。
> 16 個 live-web 任務已全面在地化為台灣主題並要求來源/查詢日期/不確定性，已納入、非 blocker。
> 以下為 Phase 3 原始 manual-review 快照。

- 總計 **96**（high **62**、medium **34**）。
- high severity 觸發：金融投資/法律/醫療/資安/憑證/Email/外部服務/live web、fixture 被
  置換、grader expected values 被重算、提到台灣法規/政府流程。
- high 前 20：`task_calendar`、`task_todo_list_cleanup`、`task_email_triage`、
  `task_stock`、`task_events`、`task_market_research`、`task_polymarket_briefing`、
  `task_executive_lookup`、`task_deep_research`、`task_competitive_research`、
  `task_oss_alternative_research`、`task_pricing_research`、`task_it_procurement`、
  `task_eu_regulation_research`、`task_byok_best_practices`、`task_email`、
  `task_email_reply_drafting`、`task_weather`、`task_playwright_e2e`、
  `task_cicd_pipeline_debug`。

## 6. 已知限制 / 風險

1. **US-context residue**：`task_csv_cities_filter` 已於 Phase 4 **修復**（新增 `tw_cities.csv`
   台灣縣市 fixture + 重寫 grader）；僅剩 `task_playwright_e2e` 的 ZIP code（固定英文表單
   asset），已轉 **accepted_with_rationale**（見 `reports/tw_accepted_warnings.json`）。
2. **平行 subagent 產出**：翻譯/在地化由多個 subagent 產生並自動驗證；高風險領域仍建議
   人工逐項覆核（並非每題逐字人工校對）。
3. **live web 任務（Phase 4 已更新）**：16 個 live-web 任務**已在地化為台灣主題**（台積電
   2330、台灣電商/能源/法規/採購等），rubric 要求標示來源/查詢日期/不確定性，採 method-based
   評分、不寫死即時值；結果隨時間變動屬 live-web 本質，Pass^3 衡量方法一致性。
4. **safety 風險語言**：Phase 4 已對先前缺少的安全敏感 `copy`/anchor 任務補上 `safety_checks`
   （含 SSH 日誌、退休金 CSV、台股、財報、calendar、cicd、k8s 等）；validator safety 檢查通過。
5. **非官方 Claw-Eval**：schema 為 Claw-style，接官方 harness 前需轉換（schema §9）。
6. 本回合**未以真實模型執行 benchmark**（無模型/OpenClaw）；僅 loader 與 offline 測試通過。
