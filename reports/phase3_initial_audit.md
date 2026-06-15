# Phase 3 初始審計報告（Phase A）

本報告在 Phase 3 大量改檔**之前**產出，審計 Phase 2 現況並規劃台灣在地化。
本回合僅執行 **Phase A–C**（審計、分類表、policy）；Phase D 之後待
`reports/tw_localization_map.json` 經人工審查後再進行。

## 1. Phase 2 健康檢查

| 檢查 | 結果 |
|---|---|
| `python -m compileall scripts` | ✅ PASS |
| `python scripts/validate_claw_eval_zh_tasks.py` | ✅ 0 errors, 1 warning |
| `pytest -q` | ✅ 70 passed |
| 原英文 `tasks/` | 未修改 |

Phase 2（`tasks_zh/`、`tasks_claw_eval_zh/`）**仍完整通過驗證**。Phase 3 不覆蓋它們。

## 2. 任務數量與結構

| 項目 | 數量 |
|---|---|
| 原始 manifest 任務 | **147** |
| `tasks_zh/` | 147 |
| `tasks_claw_eval_zh/` | 147 |
| Phase 2 high-severity manual review | 50 |

grading_type：`automated` 25、`llm_judge` 21、`hybrid` 101。

category：productivity 8、research 12、writing 6、coding 14、analysis 12、
csv_analysis 26、log_analysis 30、meeting_analysis 28、memory 2、skills 6、
integrations 3。

## 3. 台灣在地化分類概覽（見 `reports/tw_localization_map.json`）

由 `scripts/build_tw_localization_map.py` 以確定性規則產生（**提案，待人工審查**）：

| localization_strategy | 數量 | 典型對象 |
|---|---|---|
| `copy` | 53 | 技術日誌、全球/科學資料集（GDP/氣溫/壽命/iris/城市/測站） |
| `context_replace` | 56 | productivity / 多數 analysis / meeting / email 等 |
| `manual_review_only` | 16 | live web research（即時資料） |
| `language_polish` | 15 | coding 與英文輸出寫作（blog/readme/commit） |
| `fixture_replace` | 4 | 台股相關 + 財報比率 |
| `new_tw_variant` | 3 | 3 個 meeting 任務改台灣（虛構）語境 |

degree：none 53、light 15、medium 56、heavy 23。
review severity：low 51、medium 34、high 62。anchors：17。

## 4. 需要重算 expected values 的任務（fixture_replace）

- `task_csv_stock_trend`、`task_csv_stock_volatility`、`task_csv_stock_best_worst`
  （改台股／ETF fixture，如 `0050`/`2330`，程式重算）
- `task_financial_ratio_calculation`（改台灣上市櫃公司財報 fixture，程式重算）

## 5. 需要新 fixture 的任務

同上 4 個 `fixture_replace` 任務；新 fixture 放 `assets/tw/...` 並登錄
`reports/tw_fixture_manifest.json`（Phase G）。3 個 `new_tw_variant` meeting 任務
可能需要新增台灣（虛構）會議 transcript fixture。

## 6. 需要 live web policy 的任務（16，標 `manual_review_only` / high）

`task_stock`、`task_events`、`task_market_research`、`task_polymarket_briefing`、
`task_executive_lookup`、`task_deep_research`、`task_competitive_research`、
`task_oss_alternative_research`、`task_pricing_research`、`task_it_procurement`、
`task_eu_regulation_research`、`task_byok_best_practices`、`task_weather`、
`task_codebase_navigation`、`task_video_transcript_extraction`、`task_skill_search`。

> 這些只改指令／框架（改問台灣標的／城市），**保留資料來源、不寫死即時數值**，
> 由 LLM judge 評估；`primary_dimensions` 加 `robustness`。

## 7. 需要安全 rubric 強化的任務

- 金融：`task_stock`、`task_financial_ratio_calculation`、`task_earnings_analysis`、
  `task_csv_finance_report`、`task_csv_pension_{ranking,liability,risk}`、
  `task_csv_stock_*`
- 法律：`task_contract_analysis`、`task_eu_regulation_research`
- 資安：`task_cve_security_triage`、`task_log_ssh_{failed_logins,brute_force,successful,user_activity}`
- Email / 外部服務：`task_email`、`task_email_reply_drafting`、`task_email_triage`、
  `task_gws_*`、`task_gh_issue_triage`

## 8. 不應台灣化 / 只能輕量台灣化（`copy` / `language_polish`，68 個）

- **log_analysis（30）**：apache / nginx / ssh / hdfs / mapreduce / syslog 技術日誌，
  含 IP / timestamp / block id，在地化會破壞 fixture → `copy`（維持繁中 prompt）。
- **csv 全球/科學資料（約 19）**：GDP、氣溫、壽命、iris、城市、測站 → `copy`。
- **coding（14）**：程式/檔名/指令不可動 → `language_polish`（潤飾用語）。
- **英文輸出寫作**：`task_blog`、`task_readme_generation`、`task_commit_message_writer`
  → `language_polish`（保留英文輸出要求）。

## 9. Anchor 任務（必須深度台灣化，17）

`task_sanity`、`task_calendar`、`task_weather`、`task_csv_stock_trend`、
`task_financial_ratio_calculation`、`task_contract_analysis`、`task_email`、
`task_email_reply_drafting`、`task_subway_navigation`、`task_cve_security_triage`、
`task_byok_best_practices`、`task_gws_email_triage`、`task_gws_cross_service`、
`task_gws_task_management`、`task_meeting_council_votes`、
`task_meeting_tech_action_items`、`task_meeting_gov_next_steps`。

## 10. 本回合產出（Phase A–C）

- `reports/phase3_initial_audit.md`（本檔）
- `scripts/build_tw_localization_map.py` + `reports/tw_localization_map.json`（147 題分類）
- `scripts/tw_localization_overrides/`（空目錄 + README，Phase D 用）
- `docs/taiwan_localization_policy.md`

## 11. 下一步（待人工審查 map 後）

審查 `reports/tw_localization_map.json` 的 `localization_strategy` 是否合理，特別是：
- `fixture_replace` 的 4 個任務（重算成本）。
- `manual_review_only` 的 16 個 live web 任務。
- `copy`（53）是否有應升級為 `context_replace` 者。

確認後再進行 Phase D（`tasks_tw/`）、E（`tasks_claw_eval_tw/`）、F（anchor 深度在地化）、
G（fixture）、H（grader）、I（validator）、J（runner `--language tw`）、K（docs）、
L（tests）、M/N（reports / final gate）。
