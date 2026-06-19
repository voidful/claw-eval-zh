# 台灣在地版 Grader 變更記錄（tw_grader_changes）

記錄 Phase 3（台灣在地化）對 grader 的改動。**只有 fixture 被置換或情境字串被檢查的
任務才改 grader**；其餘任務沿用 Phase 2 的 grader（含中→英正規化 wrapper），未改動。

## 改動原則

1. 保留原 PinchBench 確定性評分邏輯與結構。
2. 改 fixture 的任務 → expected values **由程式重算**（見
   `reports/tw_fixture_manifest.json` 與 `scripts/fetch_twse_stock.py`）。
3. 自然語言檢查維持繁體＋簡體＋英文 additive（不刪原 pattern）。
4. 不讓中文 regex 過度寬鬆（仍需命中正確數值／日期）。

## 被改動的 grader（6 個）

| task | 原本檢查 | 台灣化後檢查 | 改 expected? | 新增中文/台灣 pattern | safety 檢查 | 需人工 review |
|---|---|---|---|---|---|---|
| `task_csv_stock_trend`（T053） | Apple 2014：起 77.45／結 110.03／+42%／連漲9連跌5 | 台積電 2330 2024：起 **593**／結 **1,075**／**+81.28%**／連漲 **6**（9/18–9/26）連跌 **4**（5/27–5/31）／高 1,090 低 576 | ✅（TWSE 真實資料重算） | 看漲/連續上漲/連續下跌/N月/2024-MM…（繁＋簡＋英） | — | 是（high） |
| `task_csv_stock_volatility`（T054） | Apple 2014：日 std 1.47%／年化 23% | 2330：日 std **2.17%**／年化 **34.5%**／最劇烈日 **2024-08-05 -9.75%／08-06 +7.98%** | ✅ | 波動/標準差/年化…（繁＋英） | — | 是（high） |
| `task_csv_stock_best_worst`（T055） | Apple 2014 最佳/最差日 | 2330：最佳 **2024-08-06 +7.98%**／最差 **2024-08-05 -9.75%**／高 1,090 低 576 | ✅ | 最佳/最差/分析（繁＋英） | — | 是（high） |
| `task_financial_ratio_calculation`（T047） | U.S. Steel FY2024 存貨周轉率（web research） | 示例台灣公司 fixture：COGS 84,000,000,000 / 平均存貨 14,000,000,000 = **6.0**；輸出檔改 `inventory_turnover.txt` | ✅（示例 fixture，確定性） | 公式/數值/比率（繁＋英）＋ `safety_note` 檢查「示例/非投資建議」 | ✅ | 是（high） |
| `task_weather`（T027） | 地點 `San Francisco`/`SF` | 地點 `Taipei`/`台北`/`臺北`；保留 weather.py 與 wttr.in、HTTP、錯誤處理檢查 | ❌（無數值答案） | Taipei/台北/臺北 | — | 是（high，live web） |
| `task_calendar`（T002） | `john@example.com`／`Project Sync`／`roadmap`／T1500 | `zhiming.wang@example.com.tw`／`專案同步`／`roadmap\|藍圖`／T1500 ＋**新增 timezone_not_us 檢查**（不得用 America/、US/、EST…） | ❌ | 專案同步/藍圖；timezone 檢查 | — | 是（high） |

## 未改動的 grader

- 其餘 141 個任務的 grader **沿用 Phase 2**（含中→英正規化 wrapper，可同時接受繁中、
  簡中、英文報告；英文路徑位元組相同）。
- `copy` 的全球/科學 CSV（GDP/城市/退休金…）保留**美國資料集**作為分析標的，grader 內的
  `United States`/`California`/`New York` 是**資料內容**而非情境字串，故不改（在地化僅在語言層）。
- 會議分析任務的英文 transcript 為固定 asset，grader 檢查 transcript 衍生事實，未改；
  prompt 以台灣語境框架（繁中）。

## 驗證

- `tests/test_tw_anchor_tasks.py`：weather/calendar/csv_stock_trend 對正確報告得分正確。
- 5 個 fixture/weather/calendar grader 已對「正確答案報告」smoke 測試，全項 1.0。
- `scripts/validate_tw_localization.py`：147 個 grader 全部可 import。

---

## Phase 4 追加的 grader 變更

| task | 原本檢查 | 台灣化後檢查 | 改 expected? | 新增中文/台灣 pattern | safety | 需人工 review |
|---|---|---|---|---|---|---|
| `task_csv_cities_filter`（T073） | 美國城市 5 項篩選（California/New York…） | 台灣 22 縣市 fixture（`tw_cities.csv`）的 5 項篩選：六都≥200萬、南部≥100萬、臺北 vs 高雄、中型、北部合計 | ✅（由 fixture 程式驗算） | 六都/縣市名/南部/北部（繁中） | — | 是 |
| `task_meeting_tech_action_items`（T115） | GitLab 英文逐字稿行動項目（GitLab 人名） | 虛構台灣公司逐字稿（`tw_tech_product_meeting.md`）：6 個行動項目、台灣負責人、活動/公告標註 | ✅（對新逐字稿） | 林佳蓉/王志明…、發表會/公告（繁中） | — | 是 |
| `task_meeting_council_votes`（T109） | Tampa 市議會英文逐字稿表決 | 虛構台灣議會（`tw_council_meeting.md`）：預算 12:0、利益迴避、一致通過、一讀、延期 | ✅（對新逐字稿） | 預算/迴避/一致/一讀/延期（繁中） | — | 是 |
| `task_stock`（T009） | Apple `AAPL` 即時股價 | 台積電 `2330` 即時股價；ticker 檢查改 `2330\|台積電\|TSMC` | ❌（即時資料不寫死價格） | 2330/台積電；查詢日期；NT$ | ✅ | 是（live web） |
| `task_executive_lookup`（T013） | GitLab CFO；輸出 `gitlab_cfo.txt` | 台積電 CFO；輸出檔改 `tsmc_cfo.txt`；檢查 `台積電\|TSMC\|2330` + `CFO\|財務長` + 來源/日期 | ❌（即時人事不寫死） | 台積電/財務長/來源/查詢日期 | ✅ | 是（live web） |

> live-web grader（stock / executive_lookup）刻意**不檢查即時數值/人名**，只檢查
> 「查對正確標的 + 提供查詢日期與來源」，符合可重現性原則（method-based）。
> 其餘 14 個 live-web 任務為 llm_judge/hybrid，未改 grader；改的是 prompt/rubric
> （在地化主題 + 要求來源/查詢日期/不確定性）。

## 深化批次（deepening）— 會議 / CSV / asset 同步 grader

把剩餘約 35 個任務做台灣在地化，並對其中 **36 個 hybrid 任務同步改寫 grader**（寫於
`scripts/tw_localization_overrides/z_<task>.yaml` 的 `grader_py`，重生後即 tasks_claw_eval_tw 的
grader.py）：

| 群組 | 任務 | 取代 | grader 改法 |
|---|---|---|---|
| 會議·議會 | council_votes/public_comment/budget/upcoming/contact_info/neighborhood（T109-114） | Tampa 市議會 → 虛構南港市議會 | 改查台灣逐字稿（dest=transcript.md）動態推導之事實 |
| 會議·公司 | tech_*／executive_summary/sentiment/follow_up/blog/tldr/searchable（T115-130） | 英文產品會議 → 鼎峰科技 | 同上（dest=meeting_transcript.md） |
| 會議·顧問 | advisory_*（T120-124） | 英文顧問會議 → 虛構技術顧問委員會 | 同上 |
| 會議·政府 | gov_*（T131-136） | NASA UAP 公聽會 → 數位治理委員會 AI 公聽會 | 同上 |
| CSV | csv_stations_*（T066-68）、csv_cities_*（T072/74/75）、csv_pension_*（T076-78） | Idaho/美國城市/美國退休金 → 台灣氣象站/鄉鎮市區/退休金 | grader 對台灣 CSV 動態計算正解 |
| asset | todo_list_cleanup/email_triage/second_brain（hybrid）；daily_summary/summary/humanizer/email_reply/video（llm_judge） | 英文 asset → 繁中台灣 asset | hybrid 改查中文內容；T138 導師 `Elena Vasquez·Stanford`→`林淑芬·臺大` + 同步 grader |
| PDF | `task_pdf_to_calendar`（T003，automated） | 英文學校行事曆 PDF → **國立中興大學 114 學年度行事曆（真實公開雙語 PDF）** | grader 改查擷取出的西元日期（民國114學年=2025–2026）：開學/中秋/國慶/期末考/寒假/元旦/第二學期開學/和平紀念/畢業典禮/端午 等，重點在**民國→西元換算**。已實測 GOOD=1.0／PARTIAL=0.5／EMPTY=0.0 |

> 驗證：143 個 grader 全部可 import；對全部 hybrid grader 做「鑑別測試」（正確中文報告高分、
> 空白/錯誤報告趨近 0）皆通過；council_votes、tech_action_items 兩個 gold 範例已對新逐字稿重建。
> 並做殘留掃描：tasks_tw 無 NASA/Tampa/Idaho/Apple 等美國殘留、無簡體、無大陸用語（數據/點擊…）。
