# claw-eval-zh

> 中文 agent benchmark。評估「以某個 LLM 作為 OpenClaw agent 大腦」時，在**中文真實任務**
> 上的完成度（completion）、安全性（safety）與穩健度（robustness）。

`claw-eval-zh` **改編自 [PinchBench](https://github.com/pinchbench/skill)**（沿用其 runner、
評分引擎與 fixtures），**任務格式參考 [Claw-Eval](https://github.com/claw-eval/claw-eval)**
的中文任務風格。完整出處與致謝見 [NOTICE.md](NOTICE.md)。

- **全繁體中文（zh-TW）**：文件與**全部 147 個任務**的 user-facing 內容皆為繁體中文。
- **三層並存**：英文原版 `tasks/`、繁中直譯版 `tasks_zh/`、**台灣在地版 `tasks_tw/`**，
  可各自重跑、可比較。
- **不破壞**原 PinchBench 英文 benchmark：`--language en`（預設）行為與上游一致。
- 本專案定位為「**參考 Claw-Eval 風格（Claw-Eval-style）**」，非官方 Claw-Eval runner
  可直接執行（差異見 [docs/claw_eval_zh_schema.md](docs/claw_eval_zh_schema.md) §9）。
- 用字標準：內文用「**台灣**」，正式機關名稱保留原名（如「臺北市政府」「臺灣證券交易所」）。

---

## 安裝

```bash
# Python 3.10+ 與 uv
uv venv && source .venv/bin/activate
uv pip install pyyaml pytest
```

## 三層語言／語系（可各自重跑、可比較）

| 層 | 目錄 | 內容 | runner |
|---|---|---|---|
| 英文原版 | `tasks/` | PinchBench 原始英文（未改） | `--language en`（預設） |
| 繁中直譯版（Phase 2） | `tasks_zh/`、`tasks_claw_eval_zh/` | 全繁體中文直譯，保留原情境 | `--language zh` |
| **台灣在地版（Phase 3）** | `tasks_tw/`、`tasks_claw_eval_tw/` | 台灣情境繁中（地點/貨幣/時區/法規…） | `--language tw`（或 `--region TW`） |

Phase 3 **不覆蓋** Phase 2；台灣版是獨立第三層。為什麼需要分開：`tasks_zh/` 測**語言**
能力（直譯、保留美國情境），`tasks_tw/` 測**台灣在地情境**能力——兩者需可對照比較，
所以不直接改 `tasks_zh/`。設計詳見
[docs/taiwan_benchmark_design.md](docs/taiwan_benchmark_design.md)。

## 目錄結構

| 目錄 / 檔案 | 說明 |
|---|---|
| `tasks/` | 原 PinchBench 英文任務（原樣保留） |
| `tasks_zh/` `tasks_claw_eval_zh/` | Phase 2 繁中（markdown / Claw-Eval 風格） |
| `tasks_tw/` `tasks_claw_eval_tw/` | Phase 3 台灣在地版 |
| `assets/tw/` | 台灣 fixtures（台積電 2330 TWSE 真實資料、示例財報…） |
| `scripts/benchmark.py` | runner（`--language en\|zh\|tw`、Pass^k） |
| `scripts/convert_pinchbench_to_claw_eval_zh.py` | Phase 2 轉換器 |
| `scripts/convert_zh_to_tw_localized.py` | Phase 3 台灣在地化轉換器 |
| `scripts/build_tw_localization_map.py` | 台灣化分類表產生器 |
| `scripts/fetch_twse_stock.py` | TWSE 公開資料擷取（build-time，產生固定 fixture） |
| `scripts/tw_localization_overrides/` | 台灣在地化人工／批次覆寫 |
| `scripts/validate_claw_eval_zh_tasks.py` `validate_tw_localization.py` | 驗證 / lint |
| `scripts/lib_zh.py` `scripts/lib_passk.py` | 簡體偵測等工具 / pass@k 純函式 |
| `reports/` | 覆蓋率、人工審查、grader 變更、驗證報告 |
| `docs/` | 遷移計畫、翻譯政策、台灣在地化政策、schema、驗證報告 |

---

## 如何跑中文 benchmark

> 範例一律加 `--no-upload`。實際執行 agent 需要可用的 OpenClaw 與模型。

```bash
# 跑單一中文 smoke 任務
uv run scripts/benchmark.py --language zh --suite task_sanity \
    --model anthropic/claude-sonnet-4 --no-upload

# 跑某個 category（中文）
uv run scripts/benchmark.py --language zh --suite coding \
    --model anthropic/claude-sonnet-4 --no-upload

# 直接指定任務目錄（覆蓋 --language）
uv run scripts/benchmark.py --tasks-dir tasks_zh --suite task_weather \
    --model anthropic/claude-sonnet-4 --no-upload

# 原英文 benchmark（行為與上游一致）
uv run scripts/benchmark.py --language en --suite task_sanity \
    --model anthropic/claude-sonnet-4 --no-upload
```

### 如何跑台灣在地任務（Phase 3）

```bash
# 台灣在地版（等同 --region TW）
uv run scripts/benchmark.py --language tw --suite task_sanity \
    --model anthropic/claude-sonnet-4 --no-upload

# 台灣 anchor 任務（台積電 2330 真實資料）
uv run scripts/benchmark.py --language tw --suite task_csv_stock_trend \
    --model anthropic/claude-sonnet-4 --no-upload

# 重建台灣在地版（讀 localization map + tw 覆寫；deterministic）
uv run scripts/convert_zh_to_tw_localized.py --write --overwrite

# 驗證台灣在地版
uv run scripts/validate_tw_localization.py
```

結果 JSON 在 `--language tw` 時額外標記 `benchmark_family: claw-style-taiwan`、
`locale: zh-TW`、`region: TW`、`localization: taiwan`。

### Pass^3 一致性評估

對齊 Claw-Eval 的 **Pass^3** 哲學：每個任務跑 3 次，**全部通過**才算 pass^3。

```bash
uv run scripts/benchmark.py --language zh --trials 3 --pass-threshold 0.8 \
    --suite task_sanity --model anthropic/claude-sonnet-4 --no-upload
```

---

## 如何匯出 / 產生 Claw-Eval 風格任務

```bash
# 先 dry-run 看會做什麼
uv run scripts/convert_pinchbench_to_claw_eval_zh.py --dry-run --tasks task_sanity,task_weather

# 寫出（兩種格式 + coverage 報告）
uv run scripts/convert_pinchbench_to_claw_eval_zh.py --write --overwrite \
    --tasks task_sanity,task_weather,task_csv_stock_trend

# 產生全部任務的 scaffold（未翻譯者標 translation_status: scaffold）
uv run scripts/convert_pinchbench_to_claw_eval_zh.py --write --overwrite

# 驗證
uv run scripts/validate_claw_eval_zh_tasks.py
```

轉換器選項：`--dry-run` / `--write` / `--limit N` / `--tasks a,b,c` /
`--variant zh-TW`（預設）/ `--strict` / `--overwrite` / `--report PATH`。
**不呼叫任何外部翻譯 API**：人工翻譯放在 `scripts/translation_overrides/*.yaml`
（目錄，每批一檔），converter deterministic 合併。`--strict` 在有任務缺完整翻譯時
回傳非零。

---

## 計分如何運作

- 沿用 PinchBench 單任務 0–1 分：`automated`（確定性 Python 檢查）、`llm_judge`
  （rubric 語義評分）、`hybrid`（兩者加權）。
- 結果 JSON 新增（向後相容）：`language`、`benchmark_family: claw-eval-zh`、
  `source_benchmark: pinchbench`、`pass_threshold`、`export_format`，以及 `passk`
  聚合區塊；每個任務 entry 新增 `pass_at_k` / `pass_k`。原有 `mean/std/min/max`
  與 `category_scores` 保留。
- Claw-Eval composite（供 `grader.py` 的維度 adapter 使用）：
  `task_score = safety * (0.80*completion + 0.20*robustness)`。

### Pass^k 如何運作

- 一次 run 視為 **pass** 的條件：`score >= pass_threshold`（預設 0.8）**且**非 timeout
  **且** `status == success`。
- **pass@3**：3 次 trial 中**至少一次**通過。
- **pass^3**：3 次 trial **全部**通過（衡量穩定性）。
- 一般化：**pass@k** = k 次中任一次通過；**pass^k** = k 次全部通過。
- 聚合報告含 `average_score`、`pass_at_k_rate`、`pass_k_rate`、
  `per_category_average_score`（= category_average_score）、
  `per_category_pass_k`（= category_pass_k_rate）。
- **Claw-Eval-style leaderboard 更重視 pass^3**，因為它測的是「不靠運氣、可重現的
  穩定通過」，而非單次僥倖。

> 註：Claw-Eval 上游 `is_pass` 門檻為 0.75；本專案 `--pass-threshold` 預設 0.8
> （可調），計分公式則與上游一致。

---

## 後續人工審查流程

**全部 147 個任務皆已翻成繁體中文**（`translation_status: complete`，0 TODO、
0 簡體殘留）。後續工作是**人工覆核**與微調：

1. 看 `reports/manual_review_required.json`（high：50、medium：88），優先覆核
   金融／法律／醫療／資安／email／外部服務／live-web／被修改 grader 的任務。
2. 要修訂某任務：編輯對應的 `scripts/translation_overrides/<batch>.yaml`，再跑
   `uv run scripts/convert_pinchbench_to_claw_eval_zh.py --write --overwrite --tasks <id>`。
3. 跑 `uv run scripts/validate_claw_eval_zh_tasks.py`，確認 0 error。
4. 追蹤 `reports/translation_coverage.json`、`reports/validation_zh.md`。

翻譯鐵則（節錄，完整見 [翻譯政策](docs/task_translation_policy.md)）：**不翻**檔名 /
CSV 欄名 / URL / API / 程式碼識別字 / shell 指令 / 環境變數名 / 品牌名；
**要翻** prompt / expected behavior / criteria / rubric / task name；
**不改**數值期望值（除非同步改 fixture）；**全繁體中文、不得殘留簡體字**。

---

## 測試

```bash
python -m compileall scripts
pytest -q
```

---

## 已知限制

- **147/147 任務皆完整繁體中文**，但**翻譯由多個平行 subagent 產生**並經 OpenCC 簡體
  掃描 + schema 驗證；高風險領域仍建議人工逐項覆核（見
  `reports/manual_review_required.json`）。並非每個任務都已逐字人工校對。
- grader 雙語化以中→英正規化 wrapper 為主；對「順序敏感的英文片語」criterion 可能漏分
  （已標 manual-review）。詳見 [reports/grader_changes.md](reports/grader_changes.md)。
- `tasks_claw_eval_zh/` 為 **Claw-Eval-style**，非官方可直接執行：schema 採
  `check.entrypoint`、擴充 `source`/`fixtures`/`metadata`、`user_agent.mode: scripted`
  +`sessions`。接官方 harness 前需轉換，見
  [docs/claw_eval_zh_schema.md](docs/claw_eval_zh_schema.md) §9。
- 實際執行 agent 需要 OpenClaw 與模型；CI / 離線環境只能跑純函式測試與轉換 / 驗證
  （本回合**未**實際以模型執行 benchmark）。
- live web 任務（如 `task_weather` 打 wttr.in、research 類）只翻指令、保留
  ticker/city/date/source，未凍結資料來源，重跑結果可能變動。

---

## 文件索引

**Phase 2（繁中直譯）**
- [docs/claw_eval_zh_migration_plan.md](docs/claw_eval_zh_migration_plan.md) — 架構與決策
- [docs/task_translation_policy.md](docs/task_translation_policy.md) — 翻譯規則
- [docs/claw_eval_zh_schema.md](docs/claw_eval_zh_schema.md) — task.yaml / grader.py schema
- [docs/validation_report.md](docs/validation_report.md)、
  [reports/grader_changes.md](reports/grader_changes.md)、
  [reports/translation_coverage.json](reports/translation_coverage.json)、
  [reports/validation_zh.md](reports/validation_zh.md)

**Phase 3（台灣在地）**
- [docs/taiwan_benchmark_design.md](docs/taiwan_benchmark_design.md) — 台灣版架構
- [docs/taiwan_localization_policy.md](docs/taiwan_localization_policy.md) — 在地化政策
- [docs/tw_validation_report.md](docs/tw_validation_report.md) — 完成度、待辦、風險
- [reports/phase3_initial_audit.md](reports/phase3_initial_audit.md)、
  [reports/tw_localization_map.json](reports/tw_localization_map.json)、
  [reports/tw_localization_coverage.json](reports/tw_localization_coverage.json)、
  [reports/tw_fixture_manifest.json](reports/tw_fixture_manifest.json)、
  [reports/tw_manual_review_required.json](reports/tw_manual_review_required.json)、
  [reports/tw_grader_changes.md](reports/tw_grader_changes.md)、
  [reports/validation_tw.md](reports/validation_tw.md)

**Phase 4（release candidate）**
- [DATASET_CARD.md](DATASET_CARD.md)、[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)、[VERSION](VERSION)
- [docs/tw_safety_rubric_guidelines.md](docs/tw_safety_rubric_guidelines.md) — 安全評分準則
- [docs/official_claw_eval_export_notes.md](docs/official_claw_eval_export_notes.md) — official-schema export candidate
- [reports/tw_high_risk_review_matrix.md](reports/tw_high_risk_review_matrix.md)、
  [reports/tw_accepted_warnings.json](reports/tw_accepted_warnings.json)、
  [reports/tw_gold_check_report.md](reports/tw_gold_check_report.md)、
  [reports/release_candidate_summary.md](reports/release_candidate_summary.md)
- `gold_tw/` — grader 校準 gold examples｜`exports/claw_eval_tw_candidate/` — 官方 schema 候選匯出

新增指令：`run_tw_gold_checks.py`（gold 校準）、`export_official_claw_eval_candidate.py --validate`、
`validate_tw_localization.py --strict-release`、`smoke_tw_runner_load.py`（離線 runner smoke）。

- [NOTICE.md](NOTICE.md) — 出處與致謝

---

## 授權

MIT（沿用 PinchBench）。見 [LICENSE](LICENSE)。
