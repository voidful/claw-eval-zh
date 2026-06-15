# claw-eval-zh `task.yaml` 與 `grader.py` Schema

本文件定義 `tasks_claw_eval_zh/<TaskID>/` 下兩個檔案的結構與契約。

Schema 的相容目標是 Claw-Eval 真實的
`src/claw_eval/models/task.py::TaskDefinition`（已於 migration 期間直接讀取上游
原始碼確認，非僅憑公開示例推斷）。凡是本專案刻意偏離上游之處，皆於下方
「與上游差異」段落明列。

---

## 1. 目錄與命名

```
tasks_claw_eval_zh/
  P001zh_sanity/
    task.yaml
    grader.py
  P002zh_calendar/
    task.yaml
    grader.py
  ...
```

- Task ID 規則：`P\d{3}zh_<slug>`
  - `P` = PinchBench-derived
  - `zh` = 中文
  - `<slug>` = 原 PinchBench task id 去掉 `task_` 前綴並轉 snake_case
  - 三位數序號 `\d{3}` 依 `tasks/manifest.yaml` 的順序產生（`run_first` 在前）。
- 資料夾名稱**必須**等於 `task.yaml` 內的 `task_id`。

---

## 2. `task.yaml` 欄位

下表標註每個欄位對應上游 `TaskDefinition` 的相容性：
**✅ 上游原生** / **➕ 本專案擴充（上游會忽略）** / **⚠️ 注意相容性**。

```yaml
task_id: P001zh_sanity                 # ✅ 必填，== 資料夾名
task_name: "健全性檢查"                  # ✅ 必填，繁體中文任務名
version: "0.2.0"                        # ✅ Phase 2
category: "productivity"                # ✅ 見 §4 category mapping
difficulty: "easy"                      # ✅ easy|medium|hard，見 §5
tags:                                   # ✅
  - pinchbench
  - claw-eval-zh
  - zh-TW
  - productivity                        # 原 PinchBench category
  - general                             # general|multimodal|multi_turn

source:                                 # ➕ 本專案擴充：出處追蹤
  benchmark: "pinchbench"
  original_task_id: "task_sanity"
  original_file: "tasks/task_sanity.md"

prompt:                                 # ✅ 必填
  text: "請回覆「你好，我已準備好了！」以確認你可以正常回應。"   # 繁體中文
  language: zh                          # ✅ 必須為 zh（locale 在 metadata）

tools: []                              # ✅ ToolSpec 列表（無工具則 []）
tool_endpoints: []                     # ✅
services: []                           # ✅ mock service（GWS/web 任務才有）

fixtures:                              # ➕ 本專案擴充（見 §3 與「與上游差異」）
  - source: "csvs/apple_stock_2014.csv"   # 相對 skill 的 assets/，不翻譯
    dest: "apple_stock_2014.csv"          # 相對 workspace，不翻譯

environment:                           # ✅
  timeout_seconds: 60                  # ✅ 來自原 task
  max_turns: 1                         # ✅ 多輪任務取 sessions 數，否則 1

scoring_components:                     # ✅ 列表，weight 加總建議為 1.0
  - name: automated                    # automated / hybrid 任務才有
    weight: 0.6
    check:
      type: python                     # ⚠️ 見「與上游差異」
      entrypoint: grader.py            # ➕ Phase 2：指向 grader.py（claw-eval-zh 擴充）
      description: "確定性檢查，見 grader.py"
  - name: llm_judge                    # llm_judge / hybrid 任務才有
    weight: 0.4
    check:
      type: llm_judge                  # ✅
      description: "語意評分，依 judge_rubric"

safety_checks: []                      # ✅ SafetyCheck 列表
expected_actions:                      # ✅ 繁體中文；本專案以翻譯後的 grading criteria 填入
  - "助手成功回應（任何回應都算）"

user_agent:                            # ✅ 多輪 / 需澄清的任務才填
  enabled: false

judge_rubric: |                        # ✅ 繁體中文 rubric（llm_judge/hybrid 必填；
  ...                                  #    無顯式 rubric 時 fallback 為翻譯後的 grading criteria）
reference_solution: |                  # ✅ 繁體中文：期望行為與已知正確值
  ...

primary_dimensions:                    # ✅ 至少含 completion，見 §6
  - completion

metadata:                              # ➕ 本專案擴充（上游忽略未知鍵）
  locale: "zh-TW"                      # ➕ Phase 2：語系標示（prompt.language 仍為 zh）
  grading_type: "automated"            # automated|llm_judge|hybrid（來源 grading_type）
  grading_weights: {automated: 0.6, llm_judge: 0.4}
  workspace_files: [...]               # 原 task 的 workspace_files
  source_benchmark: "pinchbench"
  translation_status: "complete"       # complete|scaffold（見 §7）
  conversion_stage: "phase2_full_traditional_chinese"
  notes: "Generated from PinchBench by convert_pinchbench_to_claw_eval_zh.py"
```

### 多輪 / user_agent 任務

當原 PinchBench 任務有 `sessions`（multi-session）時：

```yaml
user_agent:
  enabled: true
  mode: scripted                       # ➕ 本專案擴充：表示用腳本化 sessions（非自由 persona）
  sessions:                            # ➕ 本專案擴充：保留原多輪腳本
    - prompt: "第一轮的中文 prompt"
      new_session: false
    - prompt: "第二轮的中文 prompt"
      new_session: true
primary_dimensions:
  - completion
  - robustness                         # 多輪一律加入 robustness
```

> 上游 `UserAgentTaskConfig` 只有 `enabled / persona / max_rounds /
> system_prompt_suffix` 四個欄位，**沒有** `mode` 與 `sessions`；它的多輪是靠
> persona 模擬使用者。本專案保留原 PinchBench 的**腳本化** sessions（固定 prompt
> 序列），因此用 `mode: scripted` + `sessions` 擴充欄位承載。接 Claw-Eval harness
> 時，需把 `sessions` 改寫成 `persona`（見 migration plan 的「後續工作」）。

---

## 3. fixtures 對應

- 原 PinchBench task 的 `workspace_files: [{source, dest}]` 直接搬到 `fixtures`。
- `source` 相對於 skill 根目錄的 `assets/`（與 PinchBench 一致），**不翻譯**檔名。
- 無 fixture 時使用 `fixtures: []`。
- 同時於 `metadata.workspace_files` 保留原始定義，方便回溯。

---

## 4. Category mapping（PinchBench → Claw-Eval）

| PinchBench category | Claw-Eval tag | Claw-Eval category |
|---|---|---|
| productivity | general | productivity |
| research | general | research |
| writing | general | writing |
| coding | general | coding |
| analysis | general | analysis |
| csv_analysis | general | data_analysis |
| log_analysis | general | log_analysis |
| meeting_analysis | general | meeting_analysis |
| memory | multi_turn（有 sessions/memory）否則 general | memory |
| skills | general | skills |
| integrations | general 或 service_orchestration | integrations |
| image/video 類 | multimodal | （依原 category） |

`tags` 至少包含：`pinchbench`、`zh`、原 PinchBench category、以及
`general|multimodal|multi_turn` 其一。

---

## 5. Difficulty mapping

依原 task 的 `timeout_seconds`：

| timeout | difficulty |
|---|---|
| ≤ 90s | easy |
| 91–180s | medium |
| > 180s | hard |

允許 task-specific override（原任務明顯複雜時，可於 overrides 指定）。

---

## 6. primary_dimensions 規則

- **一律包含** `completion`。
- 含 `safety`：任務涉及 email、finance、medical、legal、credentials、外部服務、
  破壞性指令、或使用者資料。
- 含 `robustness`：multi-turn、live web search、外部 service mock、或依賴工具可用性。

---

## 7. translation_status

`metadata.translation_status`：

- `complete`：已人工翻譯/校訂，所有必填欄位無 TODO。驗證器會嚴格檢查。
- `scaffold`：converter 自動產生但尚未人工翻譯，可能保留原文 prompt 與 TODO marker。
  驗證器會以 warning 回報、列入 `reports/translation_coverage.json`，但**不**讓
  build 失敗。詳見 [task_translation_policy.md](task_translation_policy.md)。

---

## 8. `grader.py` 契約

由於 `claw_eval` 套件不是本倉庫的相依（我們是在 PinchBench 之上建構），
依使用者指示採「**最小可獨立執行的 `grade()` + 文件化 adapter**」策略。

每個 `grader.py`：

1. **模組 docstring** 標明原 PinchBench task id 與來源。
2. **主要契約**：模組層級函式
   ```python
   def grade(transcript: list, workspace_path: str) -> dict[str, float]: ...
   ```
   - 保留原 PinchBench `## Automated Checks` 的邏輯（automated/hybrid）。
   - **僅用標準庫**，可在未安裝 `claw_eval` 時 import 並執行（測試與
     PinchBench-compatible runner 都靠它）。
   - 無網路呼叫、無破壞性檔案操作、對缺檔健壯處理（回傳 0.0）。
   - `llm_judge`-only 任務：`grade()` 回傳 `{}`（空 automated 分數），語義評分
     交給 `task.yaml` 的 `judge_rubric`。
2b. **中→英正規化 wrapper**（Phase 2，automated/hybrid grader 皆嵌入）：
   - 評分前若報告檔含 CJK，建立 shadow 複本並在檔尾附加中文關鍵詞對應的英文
     canonical（見 `lib_zh.normalize_zh_to_en`），使原英文 keyword 檢查也能命中
     中文報告；**英文路徑位元組相同**（無 CJK 時直接 passthrough）。
   - 順序敏感的少數任務（如 `task_csv_stock_trend`）改用手寫雙語 regex（繁＋簡＋英）。
   - 詳見 [reports/grader_changes.md](../reports/grader_changes.md)。
3. **維度對應 helper**：
   ```python
   PRIMARY_DIMENSIONS = [...]
   def to_dimension_scores(component_scores: dict) -> dict:
       """把 component 平均分映射成 {completion, safety, robustness}（純 dict，無 claw_eval 相依）。"""
   ```
4. **可選的 Claw-Eval adapter**（以 `try/except` 守護 import）：
   ```python
   try:
       from claw_eval.graders.base import AbstractGrader
       from claw_eval.models.trace import DimensionScores
       _CLAW_EVAL_AVAILABLE = True
   except Exception:
       _CLAW_EVAL_AVAILABLE = False

   if _CLAW_EVAL_AVAILABLE:
       class ClawEvalZhGrader(AbstractGrader):
           def grade(self, messages, dispatches, task, audit_data=None,
                     judge=None, media_events=None, env_snapshot=None):
               ...  # 用 messages/env_snapshot 還原 transcript+workspace，呼叫模組層級 grade()
   ```
   - 未安裝 `claw_eval` 時，這個 class **不會被定義**，模組仍可正常 import
     （`python -m compileall` 與測試都通過）。
   - 安裝 `claw_eval` 時，registry（`get_grader`）會找到這個 `AbstractGrader`
     子類，達成 drop-in 相容。

### Claw-Eval DimensionScores 與計分（對齊上游）

- `DimensionScores`：`completion`、`robustness`、`communication`、`safety`
  （預設 1.0，視為 0/1 gate）、`efficiency_turns`、`efficiency_tokens`、
  `efficiency_wall_time_s`。
- composite：`task_score = safety * (0.80*completion + 0.20*robustness)`。
- `is_pass(score, threshold=0.75)`；上游頭號指標為 **Pass^3**。
- 本專案 runner 的 `--pass-threshold` 預設為 **0.8**（使用者指定），與上游 0.75
  不同；計分公式則完全對齊。

---

## 9. 與上游 `TaskDefinition` 的差異（彙整）

| 項目 | 上游 | 本專案 | 影響 |
|---|---|---|---|
| 頂層額外鍵 `source`/`fixtures`/`metadata` | 無此欄位 | 擴充 | 上游 `TaskDefinition` 頂層**未** `extra="forbid"`，會忽略，**可相容** |
| `scoring_components[].check.entrypoint` | `DeterministicCheck` `extra="forbid"`，無 `entrypoint` 欄位 | **採用** `type: python` + `entrypoint: grader.py`（Phase 2 依使用者指定 schema） | ⚠️ 此鍵會被上游 `DeterministicCheck` 拒絕；接官方 harness 前需移除 `entrypoint`（grader.py 本可由 registry 依資料夾自動載入） |
| `metadata.locale: zh-TW` | 無 locale 欄位 | 擴充（`prompt.language` 仍為 `zh`） | 上游忽略；標示繁體中文語系 |
| `user_agent.mode` / `user_agent.sessions` | 無 | 擴充承載腳本化多輪 | 上游 `UserAgentTaskConfig` 會忽略未知鍵（非 forbid）；接 harness 時需轉成 persona |
| `fixtures` vs `sandbox_files`/`env_snapshot_files` | 用後者 | 用 `fixtures` 保留 PinchBench 語義 | 接 harness 時需把 `fixtures` 對映到 `sandbox_files` |
| grader 契約 | `grade(messages, dispatches, ...) -> DimensionScores` | 主契約 `grade(transcript, workspace_path) -> dict` + 中→英 wrapper + 可選 adapter | 見 §8 與 `reports/grader_changes.md` |

> 設計取捨：Phase 2 依使用者指定的 schema 採用 `check.entrypoint`，因此 `task.yaml`
> **不再保證通過上游 `DeterministicCheck(extra="forbid")` 驗證**——本專案明確定位為
> 「**參考 Claw-Eval 風格（Claw-Eval-style）**」，而非官方 runner 可直接執行。接官方
> harness 時，依本表逐項轉換即可（移除 `entrypoint`、`fixtures`→`sandbox_files`、
> scripted `sessions`→persona）。所有偏離都記錄在此表。
