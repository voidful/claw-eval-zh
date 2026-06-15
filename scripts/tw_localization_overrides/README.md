# scripts/tw_localization_overrides/

台灣在地化（Phase 3）的**人工／LLM 覆寫**放這裡，每個批次一個 YAML 檔，由 Phase D
的轉換器（`scripts/convert_zh_to_tw_localized.py`，**Phase D 才建立**）合併。

> 本目錄在 **Phase A–C（審計／分類表／policy）** 階段刻意保持空白（僅此 README）。
> 待 `reports/tw_localization_map.json` 經人工審查後，Phase D 才會在此填入翻譯／在地化。

## 檔案格式（Phase D 使用）

```yaml
tasks:
  task_calendar:
    task_name: "台灣在地任務名稱（繁體中文）"
    prompt: |
      台灣在地繁體中文 prompt…
    expected_behavior: |
      …
    grading_criteria:
      - "…"
    llm_judge_rubric: |        # llm_judge / hybrid 任務
      …
    safety_checks:            # 安全敏感任務
      - "…"
    sessions:                 # 多輪任務，依原順序
      - prompt: |
          …
    grader_py: |              # 僅需重算 expected values 或順序敏感雙語 grader 時
      def grade(transcript, workspace_path):
          ...
    fixtures:                 # 僅 fixture_replace 任務；source/dest 不翻譯
      - source: "tw/csvs/tw_stock_0050_2024.csv"
        dest: "tw_stock_0050_2024.csv"
```

## 規則

- 一律**台灣自然繁體中文**，不得殘留簡體字、不得留 TODO（見
  `docs/taiwan_localization_policy.md`）。
- **不翻譯**檔名／CSV 欄名／URL／API／程式碼 identifier／shell 指令／環境變數／品牌名／
  股票代號。
- `localization_strategy` 以 `reports/tw_localization_map.json` 為準；`copy` 任務可
  不需要 override（轉換器會沿用 Phase 2 `tasks_zh/` 內容）。
- 改 fixture 必同步改 grader 與 reference solution；改 prompt 必同步改 reference solution。
