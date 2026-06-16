# Release Checklist — claw-eval-zh 0.4.0-rc1

狀態圖示：✅ 完成　🔶 部分／待人工　⬜ 未做

## 驗證與測試
- ✅ `python -m compileall scripts` 通過
- ✅ `python scripts/validate_claw_eval_zh_tasks.py`（Phase 2）：0 errors
- ✅ `python scripts/validate_tw_localization.py --strict-release`：0 errors, 0 unresolved warnings
- ✅ `python scripts/run_tw_gold_checks.py`：PASS（28 deterministic 案例，0 失敗）
- ✅ `python scripts/export_official_claw_eval_candidate.py --validate`：valid（143 任務）
- ✅ `pytest -q`：111 passed（含 zh 與 tw validator 的「真的會抓錯」負向測試）

## 內容品質
- ✅ 三層共存（en / zh / tw），各 143 任務（自原始 147 移除 4 個需非-HF 基建的任務：
  3 GWS + task_image_gen，三層含英文一併移除）
- ✅ 簡體字殘留（required user-facing fields）：0
- ✅ TODO / placeholder 殘留：0
- ✅ accepted warnings 已逐筆審查（reason/risk/owner/future_action）：1 筆（playwright zip）
- ✅ 高風險矩陣已建立並分流（`reports/tw_high_risk_review_matrix.csv`）：**56 題全部 fixed，0 blocker**
  （16 個 live-web 已在地化；5 個先前因「vulnerability」誤判為 security 的任務經審查更正）
- ✅ fixture manifest 完整（6 筆，含來源/授權/deterministic/expected values）
- ✅ grader 變更已記錄（`reports/tw_grader_changes.md`）
- ✅ docs 全繁體中文掃描通過（OpenCC）
- ✅ 未偽造任何真實模型跑分

## Release blockers（發佈到 leaderboard 前需處理）
- ✅ **leaderboard_blocker = 0**。56 個高風險任務全部 `fixed`。
- ✅ 16 個 live-web 任務已全面在地化為台灣主題、要求來源/查詢日期/不確定性、method-based 評分。
- ✅ 先前 5 個 `requires_external_human_review`（被「vulnerability」關鍵字誤判為 security 的
  log/meeting 摘要任務）經逐題審查更正，已清空。
- 🔶 1 個 accepted warning（`task_playwright_e2e` 的 ZIP code，固定英文表單 asset；非 blocker）。
- ⬜ 以真實模型 + OpenClaw 跑一次端到端 benchmark（本環境無模型，未執行）。

## 執行環境（可跑性）
- ✅ 一鍵 HF 執行器 `scripts/run_hf_benchmark.py`：給一個 HuggingFace model id 即可跑
  （router / 本機 vLLM / 自訂端點三模式；見 [docs/run_with_huggingface.md](docs/run_with_huggingface.md)）。
- ✅ 前置檢查 `scripts/preflight_env.py`：逐任務列出就緒/缺項與補法；可自動安裝 `fws` mock。
- ✅ 修正：在地化 gws/github 任務的 `prerequisites` 已隨 `--language zh/tw` 保留，
  `lib_fws.is_fws_task` 會正確啟動 fws mock（先前會在 zh/tw 漏啟動而失敗）。
- ✅ 裝好 OpenClaw 後 **142/143 題只需模型**即可跑；唯一需額外前置者為 task_gh_issue_triage
  （fws 本地 mock + gh，不需真實憑證，--auto-install 會補 fws）。
- ✅ 未就緒任務由執行器**跳過**（不計入分母），不再出現「整類 0% 失敗」假象。

## 發佈動作
- ⬜ 打 tag `v0.4.0-rc1`（本回合未自動 commit/tag）
