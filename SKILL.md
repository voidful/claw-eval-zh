---
name: claw-eval-zh
description: 執行 claw-eval-zh 中文 agent benchmark，評估 OpenClaw agent 在中文真實任務上的表現。可用於測試模型的中文 agentic 能力、比較模型、跑 Pass^k 一致性評估，或匯出 Claw-Eval 風格的中文任務集。改編自 PinchBench，任務格式參考 Claw-Eval 中文任務風格。
metadata:
  author: claw-eval-zh
  version: "0.1.0"
  based_on: pinchbench
  task_format_inspired_by: claw-eval
  repository: https://github.com/pinchbench/skill
---

# claw-eval-zh 中文 Agent Benchmark Skill

`claw-eval-zh` 評估「以某個 LLM 作為 OpenClaw agent 大腦」時，在**中文真實任務**上的
完成度（completion）、安全性（safety）與穩健度（robustness）。

本專案**改編自 [PinchBench](https://github.com/pinchbench/skill)**：沿用其 runner、
評分引擎與 fixtures。**任務格式參考 [Claw-Eval](https://github.com/claw-eval/claw-eval)
的中文任務風格**（`tasks/<TaskID>/task.yaml` + `grader.py`）。完整出處見
[NOTICE.md](NOTICE.md)。

> **全繁體中文（zh-TW）**：文件與全部 143 個任務的 user-facing 內容皆為繁體中文。
> `task.yaml` 以 `prompt.language: zh` + `metadata.locale: zh-TW` 標記。詳見
> [docs/task_translation_policy.md](docs/task_translation_policy.md)。

## 三層任務輸出

| 目錄 | 格式 | 用途 |
|------|------|------|
| `tasks/` | PinchBench markdown（英文，原樣保留） | 既有英文 benchmark，`--language en`（預設） |
| `tasks_zh/` / `tasks_claw_eval_zh/` | 繁中直譯（Phase 2） | `--language zh` |
| `tasks_tw/` / `tasks_claw_eval_tw/` | 台灣在地版（Phase 3） | `--language tw`（或 `--region TW`） |

`tasks_claw_eval_*` 為 Claw-Eval 風格 `task.yaml` + `grader.py`，方便未來接 Claw-Eval harness。
台灣在地版設計見 [docs/taiwan_benchmark_design.md](docs/taiwan_benchmark_design.md)。

## 前置需求

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- OpenClaw instance（實際跑 agent 時才需要）

## 快速開始

```bash
cd <skill_directory>

# 跑中文 smoke 任務（PinchBench-compatible runner）
uv run scripts/benchmark.py --language zh --suite task_sanity --model anthropic/claude-sonnet-4 --no-upload

# 跑原本的英文 benchmark（行為與上游一致）
uv run scripts/benchmark.py --language en --suite task_sanity --model anthropic/claude-sonnet-4 --no-upload

# Pass^3 一致性評估（每個任務跑 3 次，全過才算 pass^k）
uv run scripts/benchmark.py --language zh --trials 3 --pass-threshold 0.8 --suite task_sanity --model anthropic/claude-sonnet-4 --no-upload
```

## 轉換 / 驗證 / 工具

```bash
# 把 PinchBench 任務轉成中文（兩種格式），先 dry-run
uv run scripts/convert_pinchbench_to_claw_eval_zh.py --dry-run --tasks task_sanity,task_weather

# 實際寫出
uv run scripts/convert_pinchbench_to_claw_eval_zh.py --write --tasks task_sanity,task_weather --overwrite

# 驗證 Claw-Eval 風格任務
uv run scripts/validate_claw_eval_zh_tasks.py
```

## 主要 CLI 選項（新增）

| 選項 | 說明 |
|------|------|
| `--language en\|zh` | 選擇任務語言；`en`→`tasks/`，`zh`→`tasks_zh/`（預設 `en`） |
| `--tasks-dir PATH` | 直接指定任務目錄，覆蓋 `--language` |
| `--trials N` | 每個任務跑 N 次（`--runs` 的別名），用於 Pass^k |
| `--pass-threshold F` | 單次 run 視為 pass 的分數門檻（預設 0.8） |
| `--export-format pinchbench\|claw-eval` | 結果 JSON 的格式標記 |

其餘 PinchBench 原有選項（`--model`、`--suite`、`--core`、`--judge`、`--no-upload`…）
皆保留。

## 計分與 Pass^k

- 單一任務分數 0–1。沿用 PinchBench 的 automated / llm_judge / hybrid 評分。
- **pass@k**：k 次 trial 中**任一次** `score >= pass_threshold` 且非 timeout、status 為
  success，即為 pass@k。
- **pass^k**：k 次 trial **全部**通過才為 pass^k（對齊 Claw-Eval 的 Pass^3 哲學）。
- 聚合報告含 `average_score`、`pass_at_k_rate`、`pass_k_rate`、
  `per_category_average_score`、`per_category_pass_k`，並保留原有 `mean/std/min/max`。

## 新增自訂中文任務

- PinchBench-compatible：在 `tasks_zh/` 新增 markdown，並登錄到 `tasks_zh/manifest.yaml`。
- Claw-Eval-style：在 `tasks_claw_eval_zh/<P\d{3}zh_slug>/` 放 `task.yaml` + `grader.py`，
  schema 見 [docs/claw_eval_zh_schema.md](docs/claw_eval_zh_schema.md)。

完整架構與後續手動翻譯指引見
[docs/claw_eval_zh_migration_plan.md](docs/claw_eval_zh_migration_plan.md)。
