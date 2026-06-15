# Official Claw-Eval Export Candidate — 說明（official_claw_eval_export_notes）

> ⚠️ **重要定位**：`exports/claw_eval_tw_candidate/` 是「**官方 schema 匯出候選
> （official-schema export candidate）**」，**並非**官方 Claw-Eval 相容格式，也**未經
> 官方驗證**。請勿宣稱 official-compatible。

由 `scripts/export_official_claw_eval_candidate.py` 從 `tasks_claw_eval_tw/` 轉出，
目的是把本專案的擴充 schema 推近上游 Claw-Eval 的形狀，並**記錄每一處轉換**，方便未來
真要對接官方 harness 時參考。

## 為什麼需要候選匯出

`tasks_claw_eval_tw/` 為求承載 PinchBench 與台灣在地語義，使用了若干**非官方欄位**
（見 `docs/claw_eval_zh_schema.md` §9）。候選匯出把這些欄位轉換或搬移，使其更接近
上游 `claw_eval.models.task.TaskDefinition`。

## 轉換對照

| 來源（tasks_claw_eval_tw） | 候選（export） | 理由 |
|---|---|---|
| `scoring_components[].check.entrypoint: grader.py` | 移除；改放 `metadata.grader_entrypoint` | 上游 `DeterministicCheck` 為 `extra="forbid"`，不接受 `entrypoint`；官方靠 registry 依資料夾自動載入 `grader.py` |
| `environment.timezone` | `metadata.timezone` | 上游 `Environment` 無 `timezone` 欄位 |
| `environment.locale` / `environment.region` | `metadata.env_locale` / `metadata.env_region` | 同上 |
| `user_agent.mode`（scripted） | `metadata.user_agent_mode` | 上游 `UserAgentTaskConfig` 無 `mode`；保留 `enabled` / `sessions` |
| `fixtures`（list of {source,dest}） | 保留為 fixture list | 官方若需要可再對映為 `sandbox_files`；本候選先保留並驗證路徑存在 |
| `grader.py` | 一併複製到 `tasks/<id>/grader.py` | 對應官方「資料夾內 grader.py 自動探索」慣例 |

並在每個候選 task 的 `metadata` 標記 `export_candidate: true`、`official_compat: false`。

## 輸出結構

```
exports/claw_eval_tw_candidate/
  tasks/<T###tw_slug>/task.yaml
  tasks/<T###tw_slug>/grader.py        # 若該任務有 automated/hybrid grader
  manifest.json                        # 任務清單 + 每題 language/locale/grading_type/fixtures
  README.md
reports/official_export_candidate_report.json   # 轉換 + 驗證結果
```

## 驗證

`python scripts/export_official_claw_eval_candidate.py --validate` 會檢查每個候選任務：
`task_id`、`prompt.text`、`prompt.language == zh`、`metadata.locale == zh-TW`、
`category` 非空、`check` 內已無 `entrypoint`、所有 `fixtures.source` 存在。
有任何錯誤即 exit 非零。對應測試：`tests/test_official_export_candidate.py`。

## 後續（真要對接官方時）

1. 確認官方最新 `TaskDefinition` 欄位，將 `fixtures` 對映為官方的 `sandbox_files` /
   `env_snapshot_files`。
2. 確認官方 grader 介面（`grade(messages, dispatches, ...) -> DimensionScores`），
   啟用 `grader.py` 內的 `ClawEvalZhGrader` adapter（安裝 `claw_eval` 套件後 registry
   會自動載入）。
3. 將 scripted `sessions` 轉為官方 `user_agent.persona` 流程。
4. 重新以官方 harness 驗證並標記真正的相容性。
