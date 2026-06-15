# 台灣在地化政策（Taiwan Localization Policy）

本文件是 Phase 3「台灣在地 Claw-style benchmark」的唯一準則。轉換器
（`scripts/convert_zh_to_tw_localized.py`，Phase D 建立）、人工覆寫
（`scripts/tw_localization_overrides/*.yaml`）與驗證器
（`scripts/validate_tw_localization.py`，Phase I 建立）都必須遵守。

> **語言／語系**：全程**台灣慣用繁體中文**。`task.yaml` 以
> `prompt.language: zh` + `metadata.locale: zh-TW` + `metadata.region: TW` +
> `environment.timezone: Asia/Taipei` 標記。
>
> **定位**：本專案是「**參考 Claw-Eval 任務結構的 Claw-style 台灣 benchmark**」，
> **非**官方 Claw-Eval，亦非其可直接執行的複製品。

---

## 1. 什麼是台灣在地化

把任務的**情境**換成台灣使用者會遇到的真實情境，同時**保留可重現性與 grader 正確性**：

- 地點／地址／電話／交通／貨幣／日期／時區換成台灣慣例。
- 人名、公司、部門、職稱、Email 語氣換成台灣職場風格。
- 會議、政府、金融、資安、企業流程的語境台灣化。
- 領域詞精確（股票、ETF、勞退、捷運、發票、個資法…），不可含糊。

## 2. 什麼**不是**台灣在地化

- ❌ 只把 `San Francisco` 換成 `台北` 這種單純地名替換。
- ❌ 把不可重現的即時資料（今天股價、即時天氣、班次）硬寫成 expected answer。
- ❌ 改 fixture 卻不改 grader / reference solution。
- ❌ 改 prompt 卻不改 reference solution。
- ❌ 為了「台灣味」而降低任務的工具使用、檔案輸出、資料分析或多輪難度。
- ❌ 把法規／醫療講成定論、捏造機關或法條。

## 3. 不翻譯、不更改的 token（whitelist）

以下保持原樣（翻了會破壞 grader / fixture / 執行）：

- 檔名（`weather.py`、`stock_trend_report.md`…）、目錄名、asset 檔名
- CSV 欄位名（`AAPL_x`…）、JSON 欄位名
- URL、API endpoint、shell 指令、環境變數名
- Python / JS identifier、function 名、CLI 子指令
- 套件／函式庫／模型／品牌／廠商名（Docker、Gmail、Google Workspace…）
- 股票代號（如 `0050`、`2330`、`AAPL`）、CVE 編號
- exact required output strings（grader 比對的固定字串）

## 4. 台灣常見語彙（一致性）

> 「避免」欄為**簡體／中國大陸用語**示例，以行內代碼標示，僅供對照，不得出現在任務內容。

| 概念 | 採用 | 避免（簡體／陸用語） |
|---|---|---|
| information / data | 資訊 / 資料 | `信息` / `数据` |
| software / hardware | 軟體 / 硬體 | `软件` / `硬件` |
| network | 網路 | `网络` |
| video | 影片 | `视频` |
| account | 帳號 | `账户` |
| email | 電子郵件 / Email | `邮件` |
| metro / bus / taxi | 捷運 / 公車 / 計程車 | `地铁` / `公交` / `出租车` |
| currency | 新臺幣 / NT$ | `人民币` / RMB |
| file | 檔案（document 可用「文件」） | `文件`（陸指 file） |
| program / run | 程式 / 執行 | `程序` / `运行` |
| default / setting | 預設 / 設定 | `默认` / `设置` |

技術詞首次出現可中英並列一次：`工作區 workspace`、`工具呼叫 tool call`、
`執行軌跡 transcript`、`測試素材 fixture`、`評分規準 rubric`、`評分器 grader`、
`基準測試 benchmark`、`模擬服務 mock service`、`即時網路資料 live web`、
`三次皆通過 Pass^3`。

## 5. 台灣格式

- **時區**：`Asia/Taipei`（ICS / 排程 / 行事曆任務務必使用，不得殘留美國時區）。
- **貨幣**：新臺幣，書面用 `NT$`（如 `NT$1,200`）。
- **日期**：優先 `YYYY-MM-DD`；必要時可附台灣常見格式（如「114 年」民國年僅在語境需要時）。
- **地址**：台灣格式，例「台北市信義區市府路 1 號」。
- **電話**：手機 `0912-345-678`；市話 `02-2345-6789`。
- **交通**：台北捷運、高雄捷運、台鐵、高鐵、公車、YouBike 可入 prompt，但**不依賴即時
  班次／營運狀態**（除非任務本身就是 live web research）。
- **專案標準**：內文用「**台灣**」；正式機關名稱保留原名（如「臺北市政府」「臺灣證券交易所」）。

## 6. 安全準則（金融 / 法律 / 醫療 / 資安 / Email / 外部服務 / 憑證 / 刪除）

- 這些任務 `primary_dimensions` 必須含 `safety`，且 `judge_rubric` 或 `safety_checks`
  必須明確提到風險／限制，並對下列行為**扣分**：
  - 過度自信、未提示風險
  - 捏造來源、法條、醫療或金融定論
  - 未詢問關鍵資訊就下結論
- 金融：須註明「資訊性參考，不構成投資建議」。
- 法律：須要求「列出疑義與風險、建議諮詢律師，不提供法律定論」。
- 醫療：須要求「資訊性說明，不取代專業醫療意見」。
- 資安：保留技術語境，但**不要求**非法 exploit；著重影響評估、修補優先序、內部通報。
- 刪除／憑證／外部服務：須提示不可逆風險、避免外洩。

## 7. live web 任務的可重現性

- 依賴即時資料者（即時股價、即時天氣、即時新聞、即時班次）**不得**用固定 expected
  numeric answer 評分。
- 作法：用 **LLM judge** 評估方法與結構，或明確標 `live_web: true` 並由 judge 評估。
- 在地化只改**指令／框架**（改問台灣標的／城市），保留資料來源；`primary_dimensions`
  加 `robustness`，並列入 manual review（high）。

## 8. fixture 置換規則

- 新 fixture 放 `assets/tw/`（`csvs/`、`docs/`、`logs/`、`meetings/`、`contracts/`）。
- 每個新 fixture 登錄 `reports/tw_fixture_manifest.json`：path、來源任務、
  generated/adapted、deterministic、expected values、授權、風險。
- synthetic fixture 必須**明確標示 synthetic**；不得使用受版權限制的真實內容；
  不得引入大型檔案；測試**不得**依賴網路下載 fixture。
- 改 fixture → **必須**用程式重算 expected values，並同步更新 grader、prompt、
  Expected Behavior、reference solution、LLM judge rubric。

## 9. grader 更新規則

1. 保留原 PinchBench 確定性評分邏輯；台灣化僅以 additive 方式新增中文／台灣關鍵詞。
2. 沿用 Phase 2 的「中→英正規化 wrapper」（`lib_zh.normalize_zh_to_en`）讓中文報告
   也能命中英文 keyword；英文路徑位元組相同。
3. 若任務要求繁體中文輸出，LLM judge rubric 對英文輸出**扣分**。
4. grader **不可**因中文措辭不同而錯殺；也**不可**寬鬆到「只要出現『台灣』就給分」。
5. 改 fixture 的任務，expected values 由程式重算（不得手寫猜測）。
6. 每個被改的 grader 記錄於 `reports/tw_grader_changes.md`。

## 10. 人工 review 等級

| severity | 觸發條件 |
|---|---|
| **high** | 金融投資 / 法律 / 醫療 / 資安 / 憑證 / Email / 外部服務 / live web；fixture 被置換；grader expected values 被重算；提到台灣法規或政府流程；可能影響使用者金錢、權利、隱私或帳號安全 |
| **medium** | `context_replace` / `new_tw_variant`；grader 新增中文 regex；會議分析（英文 transcript 固定） |
| **low** | `copy` / `language_polish`，且無上述風險 |

所有需人工 review 的任務列入 `reports/tw_manual_review_required.json`，**不隱藏**。

## 11. 台灣用語一致性規則

- 全專案以本文件 §4 語彙表為準；驗證器以 OpenCC + 內建表掃描**簡體字殘留**（0 容忍）。
- 「台灣」為內文標準寫法；機關正式名稱（臺北市政府、臺灣證券交易所…）保留原名。
- 驗證器另檢查**美國語境殘留**（San Francisco / New York / USD / ZIP code / state /
  California / Apple stock…），依 `localization_strategy` 判定 warning 或 error
  （`copy`／刻意處理美國資料者可 whitelist）。

---

## 附錄：localization_strategy 對照（見 `reports/tw_localization_map.json`）

| strategy | 說明 | degree | fixture | grader |
|---|---|---|---|---|
| `copy` | 純技術／全球資料；沿用 Phase 2 繁中，台灣化無意義或會破壞 fixture | none | 否 | 否 |
| `language_polish` | 已繁中，潤飾為台灣自然用語；不改資料/期望值 | light | 否 | 否 |
| `context_replace` | 改地點/人名/公司/Email/會議語境；核心數據不變 | medium | 否 | 可能加中文 regex |
| `fixture_replace` | 置換資料集（如台股 ETF）；重算 expected values | heavy | 是 | 是（重算） |
| `new_tw_variant` | 原任務太美國語境，建立等價台灣版 | heavy | 視情況 | 視情況 |
| `manual_review_only` | 法律/金融/醫療/資安/live web；先在地化但標 high 風險人工審查 | heavy | 否 | 視情況 |
