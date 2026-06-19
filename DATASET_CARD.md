# Dataset Card — claw-eval-zh / Claw-style Taiwan Benchmark

## 1. 名稱
**claw-eval-zh**（含台灣在地版 **Claw-style Taiwan Benchmark**）

## 2. 版本
**0.4.0-rc1**（release candidate；見 [VERSION](VERSION)、[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)）

## 3. 來源
- **PinchBench-derived**：改編自 [PinchBench](https://github.com/pinchbench/skill)
  （runner、評分引擎、fixtures、任務邏輯）。
- **Claw-style**：任務結構**參考** [Claw-Eval](https://github.com/claw-eval/claw-eval)
  的中文任務風格（`task.yaml` + `grader.py`、completion/safety/robustness、Pass^3）。
  **非官方 Claw-Eval，亦未經官方驗證。** 出處見 [NOTICE.md](NOTICE.md)。

## 4. 語言
繁體中文。三層並存：
- `tasks/`（英文原版，未改）
- `tasks_zh/` + `tasks_claw_eval_zh/`（繁中直譯，Phase 2）
- `tasks_tw/` + `tasks_claw_eval_tw/`（**台灣在地版**，Phase 3–4，`locale: zh-TW`、`region: TW`）

## 5. 任務數
每層 **143** 個任務。已自原始 PinchBench 的 147 題移除 4 個需要非-HF 基建的任務
（3 個 GWS：`task_gws_email_triage`/`task_gws_cross_service`/`task_gws_task_management`，
以及影像生成 `task_image_gen`），三層（含英文 `tasks/`）一併移除，使整套可只靠
HuggingFace model id 執行。

## 6. 任務類別
productivity、research、writing、coding、analysis、csv_analysis、log_analysis、
meeting_analysis、memory、skills。（原 integrations 類因移除 GWS 任務而不再存在。）

## 7. 評分方式
- 單任務 0–1：`automated`（確定性 Python grader）、`llm_judge`（rubric）、`hybrid`。
- 維度：completion / safety / robustness（composite =
  `safety * (0.80*completion + 0.20*robustness)`）。
- **Pass^k / Pass^3**：一次 run pass 需 `score ≥ pass_threshold`（預設 0.8）、非 timeout、
  status success；pass@k = 任一次過，pass^k = 全部過。

## 8. 使用限制
- **非官方 Claw-Eval**；請以「Claw-style / 參考 Claw-Eval 風格」描述。
- 高風險任務仍需人工審查（見 `reports/tw_high_risk_review_matrix.csv`、
  `reports/tw_manual_review_required.json`）。
- **不得**作為金融、法律、醫療之專業建議來源；相關任務僅為資訊性分析評測。

## 9. 資料來源與 fixtures
共 13 個台灣 fixtures（見 [reports/tw_fixture_manifest.json](reports/tw_fixture_manifest.json)）：
- `assets/tw/csvs/tw_stock_2330_2024.csv`：**TWSE 官方公開資料**（台積電 2330 2024 日收盤價，
  242 交易日），由 `scripts/fetch_twse_stock.py` 一次性擷取後寫死、測試不連網。
  亦供 `task_csv_finance_report` 使用（原 Apple 股票）。
- `assets/tw/docs/nchu_114_calendar.pdf`：**國立中興大學 114 學年度行事曆（中英雙語版）公開
  PDF**（來源 nchu.edu.tw/calendar），供 `task_pdf_to_calendar`；grader 檢查擷取出的西元
  日期，重點在**民國→西元換算**（114=2025、115=2026）。
- `assets/tw/csvs/tw_cities.csv`（22 縣市）、`tw_townships.csv`／`tw_townships_density.csv`
  （**鄉鎮市區**層級，取代美國大城市）、`tw_weather_stations.csv`（台灣氣象站，取代 Idaho）、
  `tw_pension.csv`（台灣退休金示例，取代美國聯邦退休金）。
- `assets/tw/meetings/`：**虛構**會議逐字稿 `tw_tech_product_meeting.md`、`tw_council_meeting.md`、
  `tw_advisory_meeting.md`（顧問委員會）、`tw_gov_hearing.md`（政府 AI 治理公聽會，取代 NASA UAP）。
- `assets/tw/docs/tw_company_fy2024_financials.md`：**虛構示例**財報。
- `assets/tw/contracts/tw_service_contract.md`：**虛構**繁中合約範本。

> 會議（T109–136）與 CSV（氣象站／鄉鎮市區／退休金）類任務皆已深度在地化：每個 hybrid grader
> 改為**對台灣 fixture 動態推導正解**再比對中文報告，不沿用美國原始事實／數值（可重現）。

## 10. 台灣資料處理
- 內文用「台灣」；正式機關名稱保留原名（如「臺灣證券交易所」）。
- 時區 `Asia/Taipei`、貨幣新臺幣（NT$）、台灣地址/電話/日期格式。
- 不使用真實個資或真實機關爭議；政府/議會情境一律**虛構**。

## 11. 安全與隱私
- 高風險領域（金融/法律/醫療/資安/Email/外部服務/憑證/live web）含 `safety_checks`
  與 safety rubric（見 [docs/tw_safety_rubric_guidelines.md](docs/tw_safety_rubric_guidelines.md)）。
- fixtures 不含真實個資；股價為公開市場資料，財報/會議/合約為虛構或示例。

## 12. 已知限制
- 翻譯/在地化由多個自動代理產生並經 OpenCC + schema 驗證；**並非每題逐字人工校對**。
- 部分任務的分析 asset 為固定英文/美國內容（會議 transcript、美國全球資料集）；
  在地化僅在語言/框架層（以 US-residue advisory 標示，1 筆 accepted）。
- grader 雙語化以中→英正規化 wrapper 為主，順序敏感者另手寫。
- 本 release **未以真實模型跑端到端 benchmark**（無模型/OpenClaw）。

## 13. Reproducibility
- 所有產物由 deterministic 腳本產生：`build_tw_localization_map.py`、
  `convert_zh_to_tw_localized.py`、`build_tw_gold_examples.py`、`fetch_twse_stock.py`。
- 驗證：`validate_claw_eval_zh_tasks.py`、`validate_tw_localization.py --strict-release`、
  `run_tw_gold_checks.py`、`export_official_claw_eval_candidate.py --validate`、`pytest -q`。
- 測試不連網、不呼叫 LLM。
- 執行：`scripts/run_hf_benchmark.py --hf-model <id>` 一鍵以 HuggingFace 模型跑全套；
  `scripts/preflight_env.py` 檢查/補齊環境。GWS/GitHub 任務用 `fws` 本地 mock（無真實憑證）。
  詳見 [docs/run_with_huggingface.md](docs/run_with_huggingface.md)。

## 14. Citation / Attribution
- PinchBench（MIT）、Claw-Eval（任務結構參考，MIT）、TWSE 公開資料（政府公開資訊）。
  授權見 [LICENSE](LICENSE) 與 [NOTICE.md](NOTICE.md)。

## 15. Maintainer notes
- 目前 `leaderboard_blocker = 0`（56 個高風險任務全部 fixed）。維護者仍應在正式發佈前，
  以真實模型跑一次端到端 benchmark 並複核高風險任務。
- 16 個 live-web 任務已全面在地化為台灣主題並納入；其 rubric 要求標示來源、查詢日期與
  不確定性，採 method-based 評分（不寫死即時值）。live-web 的本質是結果會隨時間變動，
  Pass^3 衡量的是研究方法的一致性，而非固定答案。
- 新增/修改 fixture 時，必同步重算 expected values 並更新 grader 與 reference solution。
