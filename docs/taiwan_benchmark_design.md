# 台灣在地 Claw-style Benchmark 設計（Taiwan Benchmark Design）

本文件說明 Phase 3「台灣在地版」`tasks_tw/` 與 `tasks_claw_eval_tw/` 的設計與架構。

> 定位：**參考 Claw-Eval 任務結構的 Claw-style 台灣 benchmark**。非官方 Claw-Eval，
> 亦非可直接被官方 runner 執行的複製品。

---

## 1. 三層語言/語系並存

| 層 | 目錄 | 內容 | runner |
|---|---|---|---|
| 英文原版 | `tasks/` | PinchBench 原始英文（未改） | `--language en`（預設） |
| 繁中直譯版 | `tasks_zh/` + `tasks_claw_eval_zh/` | Phase 2 全繁體中文 | `--language zh` |
| **台灣在地版** | `tasks_tw/` + `tasks_claw_eval_tw/` | Phase 3 台灣情境繁中 | `--language tw`（或 `--region TW`） |

三者**可各自重跑、可互相比較**（同一 task_id 對映）。Phase 3 **不覆蓋** Phase 2；
台灣版是獨立的第三層。

## 2. 為什麼要 `tasks_tw/` 而不是直接改 `tasks_zh/`

- `tasks_zh/` 是**語言版**（把英文翻成繁中），保留原始情境（美國城市、公司、市場）。
- `tasks_tw/` 是**在地版**（把情境換成台灣使用者會遇到的真實場景）。
- 兩者目的不同、評估面向不同（語言能力 vs 在地情境能力），且需**可比較**：
  保留 `tasks_zh/` 才能對照「同一任務在直譯 vs 在地化下的表現差異」。

## 3. 在地化策略（localization_strategy）

由 `scripts/build_tw_localization_map.py` 確定性分類，存於
`reports/tw_localization_map.json`（147 題逐題）。分佈：

| strategy | 數 | 作法 |
|---|---|---|
| `copy` | 53 | 技術日誌、全球/科學 CSV；沿用 Phase 2 繁中，僅加 region/timezone 標記 |
| `context_replace` | 56 | 改地點/人名/公司/Email/會議語境；核心資料與 grader 不變 |
| `manual_review_only` | 16 | live web research；只在地化語言框架，保留研究標的，judge 評分 |
| `language_polish` | 15 | coding / 英文輸出寫作；潤飾用語，程式碼不動 |
| `fixture_replace` | 4 | 置換為台灣資料（台積電 2330 真實股價、示例財報），重算 expected values |
| `new_tw_variant` | 3 | meeting 任務以台灣（虛構）組織框架，保留固定英文 transcript |

## 4. 資料置換（fixture_replace）— 真實公開資料

- **台股**：`assets/tw/csvs/tw_stock_2330_2024.csv` 由 `scripts/fetch_twse_stock.py`
  從**臺灣證券交易所（TWSE）STOCK_DAY 公開 API** 擷取台積電（2330）2024 全年日收盤價
  （242 個交易日，ROC 日期轉 `YYYY-MM-DD`）。一次性擷取後**寫死為固定 fixture**，
  測試不連網、完全可重現。
- 三個台股任務（trend / volatility / best-worst）共用此 fixture，各自**用程式重算**
  起訖價、漲跌幅、波動率、連漲連跌、最佳最差日，並更新 grader 與 reference solution。
- **財報比率**：`assets/tw/docs/tw_company_fy2024_financials.md` 為**明確標示的示例
  （synthetic）台灣公司財報**，使存貨周轉率 = 84,000 / 14,000 = **6.0** 可確定性驗算。
- 全部登錄於 `reports/tw_fixture_manifest.json`。

## 5. Grader 設計

- 沿用 Phase 2 的雙語機制（中→英正規化 wrapper + 可選 Claw-Eval adapter）。
- 只有 6 個 grader 因 fixture/情境字串改動而重寫（見 `reports/tw_grader_changes.md`）。
- **改 fixture 必同步改 grader 與 reference**；expected values 一律由程式重算。
- 全球資料集（GDP/城市/退休金）保留美國資料作為分析標的（grader 內的美國地名是
  **資料內容**，非情境字串）。

## 6. 安全與可重現性

- 金融/法律/醫療/資安/Email/外部服務/憑證任務 → `primary_dimensions` 含 `safety`，
  rubric/safety_checks 要求風險提示、不捏造、不給專業定論（見
  `docs/taiwan_localization_policy.md` §6）。
- live web 任務 → 不寫死即時數值，judge 評分，`robustness` 維度，列高風險人工審查。

## 7. 驗證鏈

- `scripts/validate_tw_localization.py`：結構/locale/region/timezone/簡體/TODO/
  英文洩漏/safety 為**硬性錯誤**；美國殘留與台灣訊號為**advisory 警告**（部分任務
  合理保留固定美國 asset）。輸出 `reports/validation_tw.{json,md}`。
- `tests/test_tw_*.py`：覆蓋率、schema、簡體、TODO、map、US 殘留、grader import、
  anchor 任務、runner 選 `tasks_tw/`。

## 8. 已知限制

- 翻譯/在地化由多個平行 subagent 產生並經 OpenCC + schema 驗證；**高風險領域仍需人工
  逐項覆核**（`reports/tw_manual_review_required.json`，high 62）。
- 部分 `context_replace`/`copy` 任務的分析 asset 為固定英文/美國內容（會議 transcript、
  美國城市 CSV、美國學校行事曆 PDF）；在地化僅在語言/框架層，asset 未改（避免破壞
  grader 與可重現性）。這些以 US-residue 警告標示。
- 非官方 Claw-Eval 相容（schema 採 `check.entrypoint` 等擴充，見
  `docs/claw_eval_zh_schema.md` §9）。
