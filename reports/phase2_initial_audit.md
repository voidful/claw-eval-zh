# Phase 2 初始審計報告（Phase A）

審計時間基準：2026-06-15。本報告在**未修改任何資料**前產出，記錄第一階段
（Phase 1）交付狀態。

## 1. 基礎檢查結果

| 檢查 | 指令 | 結果 |
|---|---|---|
| 編譯 | `python -m compileall scripts` | ✅ COMPILE OK |
| 測試 | `pytest -q` | ✅ 69 passed |
| 驗證 | `python scripts/validate_claw_eval_zh_tasks.py` | ✅ 0 errors / 0 warnings |
| 轉換器 dry-run | `convert ... --dry-run` | ✅ 147 selected，coverage 6/147 |

## 2. 第一階段產物存在性

| 期望檔案 / 資料夾 | 狀態 |
|---|---|
| `tasks_zh/` | ✅ 存在（6 個 `.md`） |
| `tasks_zh/manifest.yaml` | ✅ 存在（過濾為已產生的 6 個） |
| `tasks_claw_eval_zh/` | ✅ 存在（6 個 folder） |
| `docs/claw_eval_zh_migration_plan.md` | ✅ |
| `docs/task_translation_policy.md` | ✅ |
| `docs/claw_eval_zh_schema.md` | ✅ |
| `scripts/convert_pinchbench_to_claw_eval_zh.py` | ✅ |
| `scripts/validate_claw_eval_zh_tasks.py` | ✅ |
| `scripts/translation_overrides.yaml` | ✅（6 個 smoke 任務） |
| `reports/translation_coverage.json` | ✅ |

結論：第一階段**確實完成了骨架**（非空殼），但只實際落地 6 個 smoke 任務。

## 3. Runner CLI 支援

| 需求 | 狀態 |
|---|---|
| `--language en\|zh` | ✅ |
| `--tasks-dir PATH` | ✅ |
| `--trials INT`（= `--runs` 別名） | ✅ |
| `--pass-threshold` | ✅（預設 0.8） |
| pass@k / pass^k metrics | ✅（`lib_passk.py` + 結果 JSON `passk` 區塊） |

## 4. 英文原始 benchmark 可用性

- `tasks/`（147 個英文任務）**未被修改**。
- 既有測試（`test_lib_grading`、`test_multi_session` 等）+ 新增 loader 測試皆通過，
  證明英文路徑可載入。
- 註：完整執行 `benchmark.py` 需要可用的 OpenClaw 與模型，離線環境無法執行真實 run；
  本審計只驗證 loader / 純函式路徑。

## 5. 覆蓋率與待辦

| 指標 | 數值 |
|---|---|
| 原始 manifest 任務數 | **147** |
| `tasks_zh/` 已落地 | **6**（4%） |
| `tasks_claw_eval_zh/` 已落地 | **6**（4%） |
| 尚未落地（連 scaffold 都沒寫到磁碟） | **141** |
| `translation_coverage.json` 標記 translated | 6 |
| `translation_coverage.json` 標記 TODO | 141 |

## 6. 簡體字殘留（Phase 2 重大發現）

第一階段依其自身規格採用**簡體中文** prompt（對齊 Claw-Eval 官方 zh 示例）。
Phase 2 要求**全繁體中文**，因此**全部 6 個既有任務都需重新轉為繁體**：

| 任務 | 簡體字命中數（task.yaml） |
|---|---|
| `P001zh_sanity` | 14 |
| `P024zh_humanizer` | 23 |
| `P027zh_weather` | 17 |
| `P040zh_iterative_code_refine` | 29 |
| `P053zh_csv_stock_trend` | 27 |
| `P145zh_gws_email_triage` | 28 |

對應的 `tasks_zh/*.md` 同樣為簡體（14–29 命中）。

## 7. 英文 user-facing 殘留

- 已落地的 6 個任務 user-facing 內容為中文（簡體），無英文殘留。
- 但 141 個未落地任務一旦以 scaffold 產生，prompt 將是英文 + TODO marker。
  Phase 2 不接受此狀態，必須全部翻成繁體中文。

## 8. Grader import 狀態

- 6 個已產生的 `grader.py` 全部可 `compileall` 並可 import，`grade()` 可呼叫。
- `P053`（csv_stock_trend）與 `P040`（iterative_code_refine）已是雙語 grader。

## 9. Phase 2 待補項目（據此規劃 B–L）

1. **全量翻譯**：147 個任務的兩種格式全部落地，且為**繁體中文**（含重做 6 個簡體 smoke）。
2. **locale**：所有 `task.yaml` 加 `metadata.locale: zh-TW`；`tasks_zh` frontmatter 加
   `locale: zh-TW`、`source_task_id`、`source_benchmark`。
3. **驗證器強化**：簡體字偵測、英文洩漏偵測、TODO/placeholder 偵測、locale 檢查、
   輸出 `reports/validation_zh.{json,md}`。
4. **轉換器強化**：支援 overrides 目錄、`--strict`、`--variant zh-TW`、idempotent、
   擴充 coverage 欄位。
5. **Grader 雙語化**：自然語言輸出任務（約 63 個）的 grader 增補繁中同義詞 regex。
6. **文件全繁體中文**：README/SKILL/docs/NOTICE。
7. **測試**：新增 Phase 2 測試（locale、簡體、TODO、full schema、idempotent、english-path）。
8. **報告**：`manual_review_required.json`、`grader_changes.md`、`validation_zh.*`。

第一階段無「假完成」或空殼問題；Phase 2 的工作是**從 6 個簡體 smoke 擴充為 147 個
繁體全量**，並建立能真正抓錯的繁中驗證鏈。
