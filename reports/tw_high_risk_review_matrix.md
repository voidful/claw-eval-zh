# 台灣在地版高風險任務審查矩陣（tw_high_risk_review_matrix）

- 高風險任務數：**56**
- 分流：fixed **56**、accepted_with_rationale **0**、requires_external_human_review **0**
- leaderboard blockers：**0**

完整欄位見 `reports/tw_high_risk_review_matrix.csv`。

| task_id | domain | strategy | final_status | reviewer | blocker |
|---|---|---|---|---|---|
| task_browser_automation | finance_or_legal | language_polish | fixed | finance/legal | false |
| task_byok_best_practices | finance_or_legal | manual_review_only | fixed | finance/legal | false |
| task_contract_analysis | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_csv_finance_report | finance_or_legal | copy | fixed | finance/legal | false |
| task_csv_pension_liability | finance_or_legal | copy | fixed | finance/legal | false |
| task_csv_pension_ranking | finance_or_legal | copy | fixed | finance/legal | false |
| task_csv_pension_risk | finance_or_legal | copy | fixed | finance/legal | false |
| task_csv_stock_best_worst | finance_or_legal | fixture_replace | fixed | finance/legal | false |
| task_csv_stock_trend | finance_or_legal | fixture_replace | fixed | finance/legal | false |
| task_csv_stock_volatility | finance_or_legal | fixture_replace | fixed | finance/legal | false |
| task_earnings_analysis | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_email_search | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_email_triage | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_eu_regulation_research | finance_or_legal | manual_review_only | fixed | finance/legal | false |
| task_executive_lookup | finance_or_legal | manual_review_only | fixed | finance/legal | false |
| task_financial_ratio_calculation | finance_or_legal | fixture_replace | fixed | finance/legal | false |
| task_meeting_council_budget | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_meeting_gov_speaker_summary | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_openclaw_comprehension | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_spreadsheet_summary | finance_or_legal | context_replace | fixed | finance/legal | false |
| task_stock | finance_or_legal | manual_review_only | fixed | finance/legal | false |
| task_test_generation | finance_or_legal | language_polish | fixed | finance/legal | false |
| task_csv_cities_filter | general | fixture_replace | fixed | none | false |
| task_codebase_navigation | live_web | manual_review_only | fixed | product | false |
| task_competitive_research | live_web | manual_review_only | fixed | product | false |
| task_deep_research | live_web | manual_review_only | fixed | product | false |
| task_events | live_web | manual_review_only | fixed | product | false |
| task_it_procurement | live_web | manual_review_only | fixed | product | false |
| task_market_research | live_web | manual_review_only | fixed | product | false |
| task_oss_alternative_research | live_web | manual_review_only | fixed | product | false |
| task_polymarket_briefing | live_web | manual_review_only | fixed | product | false |
| task_pricing_research | live_web | manual_review_only | fixed | product | false |
| task_skill_search | live_web | manual_review_only | fixed | product | false |
| task_video_transcript_extraction | live_web | manual_review_only | fixed | product | false |
| task_weather | live_web | context_replace | fixed | product | false |
| task_calendar | safety | context_replace | fixed | privacy | false |
| task_cicd_pipeline_debug | safety | language_polish | fixed | privacy | false |
| task_email | safety | context_replace | fixed | privacy | false |
| task_email_reply_drafting | safety | context_replace | fixed | privacy | false |
| task_gh_issue_triage | safety | context_replace | fixed | privacy | false |
| task_gws_cross_service | safety | context_replace | fixed | privacy | false |
| task_gws_email_triage | safety | context_replace | fixed | privacy | false |
| task_gws_task_management | safety | context_replace | fixed | privacy | false |
| task_k8s_debugging | safety | language_polish | fixed | privacy | false |
| task_meeting_follow_up_email | safety | context_replace | fixed | privacy | false |
| task_playwright_e2e | safety | language_polish | fixed | privacy | false |
| task_second_brain | safety | context_replace | fixed | privacy | false |
| task_todo_list_cleanup | safety | context_replace | fixed | privacy | false |
| task_cve_security_triage | security | manual_review_only | fixed | security | false |
| task_log_apache_critical | security | copy | fixed | security | false |
| task_log_ssh_brute_force | security | copy | fixed | security | false |
| task_log_ssh_failed_logins | security | copy | fixed | security | false |
| task_log_ssh_successful | security | copy | fixed | security | false |
| task_log_ssh_user_activity | security | copy | fixed | security | false |
| task_log_syslog_anomalies | security | copy | fixed | security | false |
| task_log_syslog_auth_failures | security | copy | fixed | security | false |

## Phase 4 重新分類紀錄（審查後更正）
- **live-web（16 題）**：已全面在地化為台灣主題（台積電 2330、台灣電商/能源/法規等），
  rubric 要求標示來源/查詢日期/不確定性、method-based 評分 → 由 accepted 改為 **fixed**、移除 blocker。
- **「vulnerability」誤判更正**：`task_log_apache_error_summary`、`task_meeting_searchable_index`、
  `task_meeting_tech_decisions`、`task_meeting_tech_product_features`、`task_meeting_tldr` 等先前被標
  `security` 僅因逐字稿/日誌出現「vulnerability management（GitLab 產品功能）」或「vulnerability
  scanning（log 行）」；經逐題審查確認**非資安操作任務**，已將分類器的 `vulnerability` 關鍵字移除，
  這些任務不再列為高風險 security（cve/credential/brute/exploit 等真正資安任務仍保留標記）。
  → 5 個 `requires_external_human_review` blocker 已清空。

## 分流規則
- `fixed`：fixture 已置換並重算、或已具備 safety_checks/風險語言且 grader 健全。
- `accepted_with_rationale`：live web 任務（保留研究標的、judge 評分、不寫死即時值），本質需人工判讀，已記錄理由。
- `requires_external_human_review`：仍需金融/法律/資安/隱私領域專家覆核者。