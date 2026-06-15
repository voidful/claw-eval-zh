# 台灣 gold check 報告（tw_gold_check_report）

- 整體結果：✅ PASS
- deterministic 案例數：28（失敗 0）

| task | case | mean | bounds | pass |
|---|---|---|---|---|
| task_calendar | pass | 0.8571 | {'min_mean': 0.7} | ✅ |
| task_calendar | fail | 0.0 | {'max_mean': 0.0} | ✅ |
| task_contract_analysis | (llm_judge) | – | – | n/a |
| task_csv_cities_filter | pass | 1.0 | {'min_mean': 0.9} | ✅ |
| task_csv_cities_filter | partial | 0.5 | {'min_mean': 0.15, 'max_mean': 0.7} | ✅ |
| task_csv_cities_filter | fail | 0.0 | {'max_mean': 0.05} | ✅ |
| task_csv_stock_best_worst | pass | 1.0 | {'min_mean': 0.9} | ✅ |
| task_csv_stock_best_worst | partial | 0.2857 | {'min_mean': 0.15, 'max_mean': 0.7} | ✅ |
| task_csv_stock_best_worst | fail | 0.0 | {'max_mean': 0.05} | ✅ |
| task_csv_stock_trend | pass | 1.0 | {'min_mean': 0.95} | ✅ |
| task_csv_stock_trend | partial | 0.4444 | {'min_mean': 0.25, 'max_mean': 0.75} | ✅ |
| task_csv_stock_trend | fail | 0.0 | {'max_mean': 0.05} | ✅ |
| task_csv_stock_volatility | pass | 1.0 | {'min_mean': 0.9} | ✅ |
| task_csv_stock_volatility | partial | 0.5 | {'min_mean': 0.2, 'max_mean': 0.7} | ✅ |
| task_csv_stock_volatility | fail | 0.0 | {'max_mean': 0.05} | ✅ |
| task_financial_ratio_calculation | pass | 1.0 | {'min_mean': 0.9} | ✅ |
| task_financial_ratio_calculation | partial | 0.4167 | {'min_mean': 0.2, 'max_mean': 0.75} | ✅ |
| task_financial_ratio_calculation | fail | 0.0 | {'max_mean': 0.05} | ✅ |
| task_meeting_council_votes | pass | 1.0 | {'min_mean': 0.9} | ✅ |
| task_meeting_council_votes | partial | 0.5 | {'min_mean': 0.2, 'max_mean': 0.8} | ✅ |
| task_meeting_council_votes | fail | 0.0 | {'max_mean': 0.05} | ✅ |
| task_meeting_tech_action_items | pass | 1.0 | {'min_mean': 0.9} | ✅ |
| task_meeting_tech_action_items | partial | 0.8 | {'min_mean': 0.2, 'max_mean': 0.8} | ✅ |
| task_meeting_tech_action_items | fail | 0.0 | {'max_mean': 0.05} | ✅ |
| task_sanity | pass | 1.0 | {'min_mean': 1.0} | ✅ |
| task_sanity | fail | 0.0 | {'max_mean': 0.0} | ✅ |
| task_weather | pass | 1.0 | {'min_mean': 0.95} | ✅ |
| task_weather | partial | 0.6429 | {'min_mean': 0.2, 'max_mean': 0.75} | ✅ |
| task_weather | fail | 0.0 | {'max_mean': 0.05} | ✅ |
