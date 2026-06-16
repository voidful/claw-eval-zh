# claw-eval-zh Migration Plan

把 [PinchBench](https://github.com/pinchbench/skill) 改造成中文 agent benchmark
`claw-eval-zh`，並讓任務同時以 **PinchBench markdown** 與 **Claw-Eval-style
`task.yaml`+`grader.py`** 兩種格式存在。

本文件說明架構決策；schema 細節見
[claw_eval_zh_schema.md](claw_eval_zh_schema.md)，翻譯規則見
[task_translation_policy.md](task_translation_policy.md)。

---

## 1. 為什麼同時有 `tasks_zh/` 與 `tasks_claw_eval_zh/`

| | `tasks_zh/` | `tasks_claw_eval_zh/` |
|---|---|---|
| 格式 | PinchBench markdown（frontmatter + `## Prompt/...`） | Claw-Eval 資料夾（`task.yaml`+`grader.py`） |
| 立即可跑？ | ✅ 現有 `scripts/benchmark.py --language zh` 直接支援 | ⚠️ 需 Claw-Eval harness（或本專案的 validator/loader） |
| 風險 | 低（沿用既有 runner、grader exec 路徑） | 較高（對齊外部 schema） |
| 目的 | **低風險**地讓現有 runner 跑中文 | **未來**接 Claw-Eval harness，做 trajectory-aware 評估 |

兩者由**同一個 converter** 從 `tasks/*.md` 產生，確保 prompt / grader 邏輯一致，
不會各自漂移。英文 `tasks/` 原樣保留，不破壞上游 benchmark。

---

## 2. 整體資料流

```
tasks/manifest.yaml + tasks/*.md   (PinchBench, 英文, 原樣)
            │
            │  scripts/lib_tasks.py::TaskLoader  (重用 parser)
            ▼
   convert_pinchbench_to_claw_eval_zh.py
            │   讀 scripts/translation_overrides.yaml（人工翻譯優先）
            ├──────────────► tasks_zh/<task_id>.md            (PinchBench md, 中文)
            │                tasks_zh/manifest.yaml
            ├──────────────► tasks_claw_eval_zh/<P###zh_slug>/task.yaml
            │                tasks_claw_eval_zh/<P###zh_slug>/grader.py
            └──────────────► reports/translation_coverage.json

執行：
  scripts/benchmark.py --language zh ──► 載入 tasks_zh/ ──► OpenClaw agent ──►
      transcript + workspace ──► lib_grading（automated/llm_judge/hybrid）──►
      results JSON（+ language / benchmark_family / pass@k / pass^k）

驗證：
  scripts/validate_claw_eval_zh_tasks.py ──► 檢查 tasks_claw_eval_zh/ 與 tasks_zh/
```

---

## 3. 元件清單

| 檔案 | 角色 | 狀態 |
|---|---|---|
| `scripts/benchmark.py` | runner；新增 `--language/--tasks-dir/--trials/--pass-threshold/--export-format`、pass@k/pass^k | 修改（向後相容） |
| `scripts/lib_tasks.py` | `TaskLoader`，重用解析 | 不改（converter 直接 import） |
| `scripts/lib_passk.py` | **新增**：pass@k / pass^k 純函式（可單元測試） | 新增 |
| `scripts/convert_pinchbench_to_claw_eval_zh.py` | **新增**：轉換器 | 新增 |
| `scripts/translation_overrides.yaml` | **新增**：人工翻譯覆寫 | 新增 |
| `scripts/validate_claw_eval_zh_tasks.py` | **新增**：驗證/lint | 新增 |
| `tasks_zh/` `tasks_claw_eval_zh/` | 中文任務輸出 | 新增 |
| `docs/*.md` `reports/translation_coverage.json` | 文件與覆蓋報告 | 新增 |
| `tests/test_*` | 新增測試 | 新增 |

> 設計原則：把可單元測試的純邏輯（pass@k、tasks_dir 解析、轉換）抽成獨立模組或
> 函式，因為跑真實 benchmark 需要 OpenClaw，CI/離線環境只能測純函式。

---

## 4. 計分與 Pass^k

- 沿用 PinchBench 的單任務 0–1 分（automated / llm_judge / hybrid）。
- 新增 Pass^k（對齊 Claw-Eval 的 **Pass^3** 哲學）：
  - 一次 run 為 pass：`score >= pass_threshold`（預設 0.8）且 **非 timeout** 且
    `status == success`。
  - **pass@k**：k 次中任一次 pass。
  - **pass^k**：k 次**全部** pass。
  - 聚合：`average_score`、`pass_at_k_rate`、`pass_k_rate`、
    `per_category_average_score`、`per_category_pass_k`。
- 保留原 `mean/std/min/max` 與 `category_scores`，**向後相容**。
- Claw-Eval composite（`safety*(0.8*completion+0.2*robustness)`）記錄於 schema，
  供 `grader.py` 的維度 adapter 使用；PinchBench-compatible runner 仍以單一 0–1
  分為主。

---

## 5. 相容性與安全邊界

- **不破壞英文路徑**：`--language en`（預設）行為與上游一致；`tasks/`、
  既有 tests、upload 流程不動。
- **不移除 upload**：保留 `--register/--upload/--no-upload`；文件範例一律
  `--no-upload`。
- **不引入外部翻譯 API**：converter 為 deterministic scaffold + 人工 override。
- **不改數值期望值**，除非 fixture 同步變更。
- **不翻譯**檔名 / 程式碼識別字（見翻譯政策 §1）。
- **不隱藏 TODO**：scaffold 與未完成項目一律進 coverage 報告。

---

## 6. 已完成

### 第一階段（Phase 1，骨架 / smoke）
- 專案身份（SKILL/pyproject/NOTICE）改為 `claw-eval-zh`，保留 PinchBench 致謝。
- 三份 docs + schema、converter / overrides / validator / `lib_passk`。
- runner 支援 `--language/--tasks-dir/--trials/--pass-threshold/--export-format`
  與 pass@k/pass^k。
- 6 個 smoke 任務（當時為**簡體中文**，對齊 Claw-Eval 官方示例）。

### 第二階段（Phase 2，全量繁體中文）
- **全部 143 個任務**翻成**繁體中文（zh-TW）**，兩種格式同步產出：
  `tasks_zh/`（143）與 `tasks_claw_eval_zh/`（143）。`translation_status` 全為
  `complete`，TODO 與簡體字殘留皆為 0。
- 翻譯由分類批次的 `scripts/translation_overrides/01..12_*.yaml` 提供
  （由多個平行 subagent 產生並逐一 OpenCC 簡體掃描 + schema 驗證）。
- `task.yaml` 升級為 Phase 2 schema：`version: 0.2.0`、`metadata.locale: zh-TW`、
  `check.entrypoint: grader.py`、`tags` 含 `claw-eval-zh`/`zh-TW`、
  `conversion_stage: phase2_full_traditional_chinese`。
- 新增 `scripts/lib_zh.py`：簡體偵測（OpenCC optional + 內建表 + 異體字排除）、
  English leakage heuristic、中→英 grader 正規化 map。
- validator 強化：簡體/English-leakage/TODO/locale/difficulty/safety/robustness
  檢查，輸出 `reports/validation_zh.{json,md}`，且**真的會抓錯**（測試守護）。
- grader 雙語化：所有 automated/hybrid grader 嵌入中→英正規化 wrapper；
  `csv_stock_trend` 為手寫三語 grader。詳見 `reports/grader_changes.md`。
- 測試：8 個 Phase 2 測試檔（loader_full / no_simplified / no_todo /
  full_schema / graders_full / converter_idempotent / pass3 / english_path），
  加上游既有測試全數通過。

---

## 7. 後續工作 / 接官方 Claw-Eval harness

1. **人工覆核高風險任務**：依 `reports/manual_review_required.json`（high：50）逐項檢查
   金融／法律／醫療／資安／email／外部服務任務的翻譯語意與 safety rubric。
2. **修訂某任務翻譯**：編輯對應的 `scripts/translation_overrides/<batch>.yaml`，
   再跑 `convert ... --write --overwrite --tasks <id>`，最後跑 validator。
3. **grader 雙語準確度**：對 coverage 標記「grader 仰賴英文自然語言關鍵字」(63) 的任務
   抽查；順序敏感者改為手寫雙語 grader（參考 `csv_stock_trend`）。
4. **接官方 harness**（依 schema §9 轉換）：
   - 移除 `scoring_components[].check.entrypoint`；
   - `fixtures` → `sandbox_files`；
   - `user_agent.mode: scripted` + `sessions` → `persona`；
   - 安裝 `claw_eval` 後，`grader.py` 的 `ClawEvalZhGrader`（AbstractGrader 子類）
     會被 registry 自動載入。
