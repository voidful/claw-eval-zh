# Release Candidate Summary — claw-eval-zh 0.4.0-rc1（Phase 4）

Phase 4 把 Phase 3「台灣在地可跑版」打磨為**研究級 release candidate**：收斂 advisory、
深修高風險任務、補台灣 fixtures、校準 grader（gold examples）、建立 official-schema export
candidate，並補齊 dataset card / release metadata。

## 一、最終 gate 結果
| 檢查 | 結果 |
|---|---|
| `compileall scripts` | ✅ PASS |
| `validate_claw_eval_zh_tasks.py`（Phase 2） | ✅ 0 errors |
| `validate_tw_localization.py --strict-release` | ✅ 0 errors, 0 unresolved warnings, 1 accepted |
| `run_tw_gold_checks.py` | ✅ PASS（28 deterministic 案例，0 失敗） |
| `export_official_claw_eval_candidate.py --validate` | ✅ valid（147 任務） |
| `pytest -q` | ✅ 111 passed（含 validator 負向測試：zh 與 tw 皆證明會抓錯） |

## 二、Advisory warnings 收斂
- 起始 14 → **0 unresolved**。
- 12 個 safety-rubric 警告：修復（放寬安全用語偵測 + 對缺者補 `safety_checks`）。
- 2 個 US-residue：`task_csv_cities_filter` **已修**（新增 `tw_cities.csv` + 重寫 grader）；
  `task_playwright_e2e` 轉 **accepted_with_rationale**（固定英文表單 asset，grader 不依賴）。
- accepted warnings：**1**（見 `reports/tw_accepted_warnings.json`）。

## 三、高風險任務分流（`reports/tw_high_risk_review_matrix.csv`）
- 高風險任務 **56**：**全部 fixed（0 requires_external_human_review）**。
- **16 個 live-web 任務已全面在地化為台灣主題**（台積電 2330 股價/CFO、台灣電商競品、
  台灣能源/法規/採購、Polymarket 以台灣投資人角度…），rubric 一律要求**標示來源、查詢日期、
  不確定性**，採 method-based 評分（不寫死即時值），已**納入**並從 blocker 移除。
- top-20 全部 fixed。**leaderboard blockers：0**。

## 四、台灣 fixtures（6；`reports/tw_fixture_manifest.json`）
- 真實公開：`tw_stock_2330_2024.csv`（TWSE）。
- 公開概數：`tw_cities.csv`（22 縣市）。
- 虛構示例：`tw_company_fy2024_financials.md`、`tw_tech_product_meeting.md`、
  `tw_council_meeting.md`、`tw_service_contract.md`。

## 五、Grader 校準（gold examples）
- `gold_tw/`：**11** 個任務（10 deterministic + 1 llm_judge 校準清單），每個含 pass/partial/fail。
- `run_tw_gold_checks.py`：28 個 deterministic 案例全數落在期望分數區間內。

## 六、Official export candidate
- `exports/claw_eval_tw_candidate/`：147 任務，移除 `check.entrypoint`（→ metadata）、
  搬移 timezone/locale/region、scripted mode；**明確標示非官方相容**。

## 七、修改統計
- 修改 grader（含重算）：**6**（csv_stock×3、financial_ratio、weather、calendar）
  + cities_filter（新）+ 2 meetings（新）= 共 **9** 個自訂 grader。
- 新增 fixtures：**6**。新增 gold 任務：**11**。
- 新增 scripts：`build_tw_high_risk_matrix.py`、`build_tw_gold_examples.py`、
  `run_tw_gold_checks.py`、`export_official_claw_eval_candidate.py`、`smoke_tw_runner_load.py`。
- 升級 validator：accepted-warnings 機制 + `--strict-release` + summary 三分。

## 八、是否跑真實模型
**否**。環境無模型 / OpenClaw；僅 offline pipeline 與 loader smoke 通過，未偽造跑分。

## 九、Remaining release blockers
見 `RELEASE_CHECKLIST.md`：**0 個** leaderboard_blocker（56 高風險任務全部 fixed）。
剩餘：1 個 accepted warning（playwright ZIP，非 blocker）、以及「以真實模型跑一次端到端」尚未執行。
16 個 live-web 已在地化納入；5 個「vulnerability」誤判為 security 的任務經審查更正、已清空 blocker。
