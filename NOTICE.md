# NOTICE

`claw-eval-zh` 是一個中文 agent benchmark 專案，由既有開源專案改編而成。本檔案記錄出處與致謝。

## 出處與致謝（Attribution）

- **Based on PinchBench.**
  本專案的 runner、task markdown 格式、自動評分函式（automated graders）、
  以及 `assets/` 內的 fixtures，皆改編自
  [PinchBench](https://github.com/pinchbench/skill)（原 `pinchbench-skill`）。
  PinchBench 以 MIT License 授權，原始版權與 `LICENSE` 一併保留於本倉庫。

- **Chinese task format inspired by Claw-Eval.**
  `tasks_claw_eval_zh/` 下的 `task.yaml` + `grader.py` 資料夾格式，
  參考自 [Claw-Eval](https://github.com/claw-eval/claw-eval)（*Claw-Eval: Towards
  Trustworthy Evaluation of Autonomous Agents*）公開的中文任務範例
  （例如 `tasks/C01zh_mortgage_prepay`、`tasks/C02zh_personal_finance`）與其
  `src/claw_eval/` 評分／模型程式碼。`task.yaml` 的欄位、`DimensionScores`
  維度（completion / safety / robustness）、composite 計分公式
  （`safety * (0.80*completion + 0.20*robustness)`）、以及 Pass^k / Pass@k
  指標，均對齊 Claw-Eval 的公開設計。Claw-Eval 以 MIT License 授權。

- **Automated graders and fixtures derived from PinchBench unless otherwise stated.**
  除非個別檔案另有說明，`tasks_claw_eval_zh/<id>/grader.py` 內的確定性檢查邏輯
  （deterministic checks）皆由對應 PinchBench 任務的 `## Automated Checks`
  區塊轉寫而來，並以 `convert_pinchbench_to_claw_eval_zh.py` 產生。
  數值期望值（expected values）與 fixtures 內容保持與原 PinchBench 一致，
  僅在 fixture 同步變更時才會修改。

## 與 PinchBench 的關係

- 本專案**不刪除、不破壞**原 PinchBench 英文 benchmark。原 `tasks/` 與
  `scripts/benchmark.py --language en`（預設）行為與上游一致。
- 中文任務集（`tasks_zh/`、`tasks_claw_eval_zh/`）為**平行新增**，不覆蓋英文任務。

## 與 Claw-Eval 的關係

- 本專案**不是** Claw-Eval 官方倉庫，亦非其分支。我們僅在格式與評分哲學上對齊
  Claw-Eval，使產出的中文任務未來能較低成本接上 Claw-Eval harness。
- `tasks_claw_eval_zh/` 的 schema 以 Claw-Eval `src/claw_eval/models/task.py`
  的 `TaskDefinition` 為相容目標；任何刻意的偏離都記錄在
  [docs/claw_eval_zh_schema.md](docs/claw_eval_zh_schema.md)。

## 台灣在地版（Phase 3）資料來源

- **台股 fixture**：`assets/tw/csvs/tw_stock_2330_2024.csv` 擷取自
  **臺灣證券交易所（TWSE）STOCK_DAY 公開 API**（政府公開市場資料），僅取台積電
  （2330）2024 日收盤價，寫死為固定 fixture 以確保可重現；非投資建議。
- **示例財報 fixture**：`assets/tw/docs/tw_company_fy2024_financials.md` 為**虛構示例
  （synthetic）**，明確標示、非真實公司財報。
- 台灣在地版僅在語言與情境層在地化；會議 transcript 等固定英文 asset 未更動。

## 授權

本專案沿用 PinchBench 的 MIT License（見 [LICENSE](LICENSE)）。改編內容同樣以
MIT License 釋出。TWSE 資料為政府公開資訊。
