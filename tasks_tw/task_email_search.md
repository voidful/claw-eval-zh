---
id: task_email_search
name: 郵件搜尋與摘要（鼎峰科技 Project Alpha 信件串）
category: analysis
grading_type: hybrid
timeout_seconds: 240
language: zh
locale: zh-TW
region: TW
source_task_id: task_email_search
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: context_replace
claw_eval_tw_id: T045tw_email_search
workspace_files:
- path: emails/2026-01-15_project_alpha_kickoff.txt
  content: |
    寄件者：lin.jy@dingfeng.com.tw（林佳穎，專案負責人）
    收件者：engineering-team@dingfeng.com.tw
    日期：2026-01-15（星期四）09:00 Asia/Taipei
    主旨：Project Alpha——啟動與時程

    各位團隊夥伴，

    很高興正式宣布 Project Alpha 已經拍板啟動！這是我們全新的、面向客戶的
    分析儀表板（analytics dashboard），將取代舊有的報表系統。以下是你需要知道的重點：

    時程：
    - 第一階段（資料管線）：1/20 – 2/14
    - 第二階段（API 層）：2/17 – 3/14
    - 第三階段（前端）：3/17 – 4/18
    - Beta 上線：4/21
    - 正式發行（GA）：5/12

    規劃會議的關鍵決策：
    - 時序資料採用 PostgreSQL + TimescaleDB
    - API 以 FastAPI（Python）開發
    - 前端使用 React 搭配新的圖表函式庫（Recharts）
    - 身分驗證整合現有 SSO，走 OAuth2

    總預算已核准為新臺幣 340 萬元，分配如下：
    - 基礎設施：NT$85 萬
    - 工程（6 名專職人力，4 個月）：NT$220 萬
    - QA 與測試：NT$35 萬

    我會在本週結束前發出個別的角色分工。請先看一下這份 PRD：
    https://docs.dingfeng.com.tw/alpha-prd

    這個專案我們一定要做成！
    佳穎
- path: emails/2026-01-22_alpha_data_pipeline.txt
  content: |
    寄件者：chang.cw@dingfeng.com.tw（張哲瑋，資深資料工程師）
    收件者：lin.jy@dingfeng.com.tw
    副本：engineering-team@dingfeng.com.tw
    日期：2026-01-22（星期四）14:30 Asia/Taipei
    主旨：Re：Project Alpha——資料管線架構提案

    佳穎你好，

    這是第一階段的資料管線架構提案：

    擷取層（Ingestion）：
    - 以 Apache Kafka 處理來自客戶端應用的即時事件串流
    - 歷史資料遷移採 Airflow DAG 做批次擷取
    - 預估尖峰吞吐量：約每秒 5 萬筆事件

    處理層（Processing）：
    - 以 Apache Flink 做串流處理與彙總
    - 以 dbt 做批次轉換與資料建模
    - 資料品質檢查使用 Great Expectations

    儲存層（Storage）：
    - 時序指標用 TimescaleDB（如先前決議）
    - 以 Redis 快取高頻存取的彙總結果
    - 原始資料湖（data lake）放在 S3

    有一個疑慮：估算的資料量（約每天 2TB）比當初預期高，這會讓我們的基礎設施
    成本每月再增加約 NT$15 萬，超出原始預算。建議我們在星期五的站立會議討論。

    另外，我發現 Kafka 叢集規模有潛在風險。為了安全地承受尖峰負載，我們可能需要
    佈署 6 個 broker，而不是原本的 3 個，這會讓雲端支出每月再多 NT$8 萬。

    所有細節我都記在這裡：https://docs.dingfeng.com.tw/alpha-pipeline-arch

    哲瑋
- path: emails/2026-02-03_alpha_budget_concern.txt
  content: |
    寄件者：chao.lc@dingfeng.com.tw（趙麗娟，財務長）
    收件者：lin.jy@dingfeng.com.tw
    副本：kao.cm@dingfeng.com.tw
    日期：2026-02-03（星期二）10:15 Asia/Taipei
    主旨：Re：Project Alpha——預算超支風險

    佳穎，

    我看了你轉寄過來、哲瑋更新的基礎設施成本預估。每月額外的 NT$23 萬
    （NT$15 萬資料量 + NT$8 萬 Kafka 擴充），換算到 4 個月的專案期間大約是
    NT$92 萬。這會把預算從 340 萬推到可能 432 萬——超支 27%。

    在我能核准擴編預算之前，我需要：

    1. 一份詳細的成本效益分析，說明在較高支出水準下的投資報酬率（ROI）
    2. 業務團隊確認分析產品預估的 NT$2.1 億 ARR（年度經常性收入）仍然成立
    3. 探討成本最佳化選項——我們能不能用 spot instance？資料保存能不能分層，
       以降低儲存成本？

    這件事我也已經提報給志明（技術長）。我們這週安排一場 30 分鐘的預算審查會議吧。
    我星期四下午 2 點可以。

    這不是「不行」，而是「把數字給我看」。我希望這個專案成功，但我們需要財務紀律。

    麗娟
- path: emails/2026-02-05_alpha_api_design.txt
  content: |
    寄件者：wang.ch@dingfeng.com.tw（王俊宏，後端主管）
    收件者：engineering-team@dingfeng.com.tw
    日期：2026-02-05（星期四）16:45 Asia/Taipei
    主旨：Project Alpha——API 設計審查請求

    團隊，

    我完成了 Alpha 分析儀表板的初版 API 設計。想在第二階段開始實作前先收集回饋。

    主要端點：

    GET /api/v1/dashboards——列出使用者的儀表板
    POST /api/v1/dashboards——建立自訂儀表板
    GET /api/v1/metrics/{metric_id}/timeseries——查詢時序資料
    POST /api/v1/reports/generate——產生可匯出的報表（PDF/CSV）
    GET /api/v1/alerts——列出已設定的警示
    POST /api/v1/alerts——建立門檻型警示
    WebSocket /ws/v1/live-metrics——即時指標串流

    身分驗證：透過現有 SSO 的 OAuth2 bearer token
    流量限制：每租戶每秒 100 次請求，全域每秒 1000 次
    分頁：所有清單端點皆採游標式（cursor-based）分頁

    我對即時 WebSocket 端點有個疑慮。我們目前的基礎設施不支援 WebSocket 連線的
    sticky session。我們得在以下方案中擇一：
    a) 加入 Redis pub/sub 來分發 WebSocket 訊息
    b) 另外佈署一個獨立的 WebSocket 閘道服務
    c) 改用 Server-Sent Events（SSE）（較簡單，但只能單向）

    就擴充性來說我比較傾向方案（b），但它會讓第二階段時程多出約 2 週。大家覺得呢？

    完整 API 規格：https://docs.dingfeng.com.tw/alpha-api-spec

    俊宏
- path: emails/2026-02-10_alpha_security_review.txt
  content: |
    寄件者：security@dingfeng.com.tw（資安團隊）
    收件者：lin.jy@dingfeng.com.tw，wang.ch@dingfeng.com.tw
    日期：2026-02-10（星期二）11:00 Asia/Taipei
    主旨：Project Alpha——強制資安審查發現

    佳穎、俊宏你們好，

    我們完成了 Project Alpha 架構與 API 設計的初步資安審查，以下是我們的發現：

    重大（CRITICAL，上線前必須修正）：
    1. 若 metric_id 可被猜測，/api/v1/metrics/{metric_id}/timeseries 端點會允許
       跨租戶（cross-tenant）資料存取。必須在查詢層（而非僅 API 層）落實租戶隔離。
    2. WebSocket 連線必須實作逐訊息（per-message）的驗證權杖，而非僅在連線建立時
       驗證。長連線是已知的攻擊向量。

    高（HIGH，上線前應修正）：
    3. 流量限制應同時做到「每租戶」與「每使用者」，以防租戶內單一使用者濫用。
    4. 報表產生端點（POST /reports/generate）若未妥善驗證 format 參數，可能被利用
       進行 SSRF 攻擊。
    5. 儀表板建立與警示設定變更缺少稽核日誌（audit log）。

    中（MEDIUM，上線後 30 天內修正）：
    6. 考慮為 API 實作請求簽章，以防重放攻擊（replay attack）。
    7. 補上 CORS 設定文件，並確保 allowlist 設定嚴格。

    在重大與高風險項目處理完之後，我們需要再做一次後續審查。請至少在 Beta 上線日
    的 2 週前安排。

    完整報告：https://docs.dingfeng.com.tw/alpha-security-review

    資安團隊
- path: emails/2026-02-12_alpha_phase1_complete.txt
  content: |
    寄件者：chang.cw@dingfeng.com.tw（張哲瑋，資深資料工程師）
    收件者：lin.jy@dingfeng.com.tw
    副本：engineering-team@dingfeng.com.tw
    日期：2026-02-12（星期四）17:00 Asia/Taipei
    主旨：Project Alpha——第一階段完成！資料管線已上線

    各位好，

    很高興回報：第一階段（資料管線）已正式完成，而且如期達成！

    已上線項目：
    - Kafka 叢集（6 個 broker）平均每秒處理約 4.8 萬筆事件
    - Flink 串流處理，端到端延遲低於 200ms
    - TimescaleDB 已灌入 3 週的歷史資料
    - dbt 模型以每小時排程執行
    - Great Expectations 資料品質套件以 99.7% 門檻通過

    預算更新：
    - 與麗娟開會後，我們取得擴編預算的核准（NT$410 萬）
    - 我們把 Flink 處理節點改用 spot instance，省下 NT$22 萬
    - 第一階段基礎設施實際支出：NT$78 萬（相對於編列的 NT$85 萬）

    一個小插曲：2/8 那天我們遇到 4 小時的中斷，原因是某個 broker 重啟時 Kafka 叢集
    觸發了 rebalancing 風暴。我們之後已實作優雅關機程序並加上監控警示。事件報告在這：
    https://docs.dingfeng.com.tw/alpha-incident-feb8

    下星期一進入第二階段。哲瑋會把管線維運交接給 SRE 團隊。

    大家辛苦了，做得很好！
    哲瑋
- path: emails/2026-02-14_alpha_client_feedback.txt
  content: |
    寄件者：chen.yc@dingfeng.com.tw（陳怡君，業務主管）
    收件者：lin.jy@dingfeng.com.tw，kao.cm@dingfeng.com.tw
    日期：2026-02-14（星期五）13:20 Asia/Taipei
    主旨：Project Alpha——Beta 候補名單客戶的早期回饋

    佳穎、志明，

    想跟你們分享 Beta 候補名單客戶的一些好消息。我們和 5 家企業潛在客戶做了初步
    展示，反應非常正面：

    宏遠企業（潛在 NT$5,000 萬 ARR）：
    - 「這個即時儀表板正是我們一直在找的東西」
    - 希望能依商業 KPI（而非僅技術指標）做自訂警示
    - 詢問能否與他們的 Okta 做 SSO 整合

    全球通科技（NT$3,500 萬 ARR）：
    - 對資料管線的延遲數字印象深刻
    - 合規報表需要 CSV 與 PDF 匯出
    - 希望有 API 存取，做程式化的資料拉取

    源資料股份有限公司（NT$2,800 萬 ARR）：
    - 很喜歡 UI 設計稿
    - 擔心多地區資料落地（data residency）的法遵要求（個資法／GDPR）
    - 詢問即時串流的 SLA 保證

    鼎泰金融（NT$4,200 萬 ARR）：
    - 對異常偵測功能（尚未開發）非常有興趣
    - 簽約前需要 SOC 2 Type II 合規
    - 希望有白標（white-labeling）選項，提供給他們自己的客戶

    雲匯科技（NT$3,000 萬 ARR）：
    - 想與他們既有的 Snowflake 資料倉儲整合
    - 詢問能否透過 API 自訂指標定義
    - 預算核准取決於第二季董事會

    光是這 5 家的總管線就有 NT$1.85 億 ARR。加上既有的潛在客戶，我們正朝
    NT$2.8 億 ARR 邁進——超前我們 NT$2.1 億的預估。

    所有潛在客戶共同的前幾大功能需求：
    1. 自訂警示／異常偵測
    2. 合規可用的匯出（PDF/CSV）
    3. 程式化使用的 API 存取
    4. 多地區／資料落地支援
    5. 白標能力

    如果你想要我加入下一次的衝刺規劃來排這些功能的優先順序，再跟我說。

    怡君
- path: emails/2026-02-18_alpha_timeline_slip.txt
  content: |
    寄件者：lin.jy@dingfeng.com.tw（林佳穎，專案負責人）
    收件者：engineering-team@dingfeng.com.tw
    副本：kao.cm@dingfeng.com.tw
    日期：2026-02-18（星期三）09:30 Asia/Taipei
    主旨：Project Alpha——更新時程（第二階段延後）

    團隊，

    在檢視資安發現與俊宏的 WebSocket 提案之後，我需要向大家說明 Project Alpha 的
    一項時程調整：

    變更內容：
    - 資安重大項目（跨租戶隔離、WebSocket 驗證）增加約 1.5 週
    - WebSocket 閘道服務（方案 b）增加約 2 週
    - 綜合影響：第二階段延長約 2.5 週（部分工作可平行進行）

    更新後時程：
    - 第二階段（API 層）：2/17 – 4/1（原為 3/14）
    - 第三階段（前端）：4/2 – 5/3（原為 3/17 – 4/18）
    - Beta 上線：5/6（原為 4/21）
    - 正式發行（GA）：5/27（原為 5/12）

    Beta 上線往後延 15 天。我已經和志明討論過，他支持這個決定——「安全地交付」
    沒有妥協空間。

    為了部分抵銷延誤，我們會：
    1. 引入吳承翰作為第 7 名工程師，協助處理資安修正
    2. 把合規匯出功能移到第三階段，讓第二階段更聚焦
    3. 在第二階段後期就平行展開前端元件開發

    業務的怡君已經確認，我們 Beta 候補名單的客戶在 5/6 之前都沒有硬性截止日，
    所以對客戶的影響很小。

    我知道延誤令人沮喪，但這是正確的決定。資安團隊的發現是站得住腳的，我們寧可
    現在就修好，也不要在上線後手忙腳亂。

    更新後的甘特圖：https://docs.dingfeng.com.tw/alpha-timeline-v2

    佳穎
- path: emails/2026-02-20_unrelated_team_lunch.txt
  content: |
    寄件者：office-admin@dingfeng.com.tw（行政總務）
    收件者：all-staff@dingfeng.com.tw
    日期：2026-02-20（星期五）11:00 Asia/Taipei
    主旨：員工感謝餐會——下星期五

    大家好！

    為了慶祝第一季的好表現，我們將在下星期五（2/27）中午於一樓員工餐廳舉辦員工
    感謝餐會。請在星期三前填寫飲食偏好表單：
    https://forms.dingfeng.com.tw/lunch-prefs

    菜色選項包含地中海風、亞洲創意料理，以及燒烤站。

    餐會見！
    行政總務
- path: emails/2026-02-22_unrelated_conference.txt
  content: |-
    寄件者：noreply@techconference.tw
    收件者：lin.jy@dingfeng.com.tw
    日期：2026-02-22（星期日）08:00 Asia/Taipei
    主旨：早鳥優惠即將結束——台灣科技高峰會 2026

    別錯過台灣科技高峰會 2026——專為工程領導者打造的年度盛會！

    2026 年 6 月 15–17 日｜台北南港展覽館

    專題講者：
    - AI 上線實戰：擴展 ML 流水線
    - 即時分析的未來
    - 打造具韌性的分散式系統

    早鳥票價：NT$8,000（原價：NT$13,000）
    結帳輸入優惠碼 EARLYBIRD26，再享 9 折。

    立即報名：https://techsummit2026.tw/register
- path: emails/2026-02-25_alpha_frontend_progress.txt
  content: |-
    寄件者：huang.st@dingfeng.com.tw（黃詩婷，前端主管）
    收件者：lin.jy@dingfeng.com.tw
    副本：engineering-team@dingfeng.com.tw
    日期：2026-02-25（星期三）15:45 Asia/Taipei
    主旨：Project Alpha——前端早期進度更新

    佳穎你好，

    照你的建議，我們在第二階段期間就平行展開了前端工作。目前進度如下：

    已完成：
    - 設計系統與元件庫建置完成（Storybook）
    - 支援拖放擺放 widget 的儀表板版面引擎
    - 以 Recharts 製作的圖表元件（折線、長條、面積、圓餅）
    - 身分驗證流程已整合 SSO
    - 平板與桌機的響應式版面

    進行中：
    - 即時資料串流 UI（等俊宏的 WebSocket 閘道）
    - 報表匯出介面（PDF 預覽 + CSV 下載）
    - 警示設定精靈

    受阻：
    - 即時指標 widget 需要 WebSocket API 端點
    - 自訂指標建構器需要指標定義 API（俊宏預計 3/10 提供）

    有一件關於客戶回饋的事——鼎泰金融的白標需求，其實比我預期的簡單。我們的設計
    系統本來就支援主題 token，第三階段大概只要 3 天工作量就能加上白標支援。值得
    優先處理嗎？

    前端展示環境：https://alpha-staging.dingfeng.com.tw

    詩婷
grading_weights:
  automated: 0.4
  llm_judge: 0.6
---

# 郵件搜尋與摘要（鼎峰科技 Project Alpha 信件串）

## Prompt

你的工作區 `emails/` 資料夾裡有一批郵件（11 個郵件檔，檔名中含有日期，內容為繁體
中文）。請搜尋所有郵件，找出所有與「Project Alpha」相關的內容，並建立一份完整的
摘要文件。

請把摘要存到 `alpha_summary.md`（請以繁體中文撰寫），包含以下區段：

1. **專案概述（Project Overview）**：Project Alpha 是什麼、使用哪些技術、預算多少？
2. **時程（Timeline）**：原始時程與任何變更，包含目前預期的日期
3. **關鍵風險與問題（Key Risks and Issues）**：預算疑慮、資安發現、技術挑戰
4. **客戶／業務影響（Client/Business Impact）**：銷售管線、客戶回饋與營收預測
5. **目前狀態（Current Status）**：根據最新進度，專案目前處於什麼階段

請只依據郵件中實際出現的資訊撰寫，不要臆測郵件未提及的細節。

備註：所有時間皆為 Asia/Taipei 時區，金額為新臺幣（NT$）。

## Expected Behavior

助手應該：

1. 探索並讀取 `emails/` 目錄裡的所有郵件檔（繁體中文內容）
2. 辨識哪些郵件與 Project Alpha 相關（11 封中有 9 封相關；2 封是不相關的雜訊）
3. 過濾掉不相關的郵件（員工感謝餐會、研討會宣傳）
4. 把多封郵件的資訊綜整成連貫的敘事
5. 追蹤資訊隨時間如何演變（例如預算從 NT$340 萬變為 NT$410 萬、時程延後）
6. 交叉參照細節（例如資安發現導致時程變更、客戶回饋影響了優先順序）
7. 產出一份結構良好的摘要文件，存到 `alpha_summary.md`

本任務測試助手能否：

- 搜尋並過濾一批文件
- 區分相關與不相關內容
- 綜整多個來源的資訊
- 追蹤隨時間演變的事實
- 產出結構化、準確的摘要

## Grading Criteria

- [ ] 助手探索並讀取了 emails/ 目錄裡的郵件
- [ ] 已建立 alpha_summary.md 檔案
- [ ] 摘要正確辨識 Project Alpha 為分析儀表板（analytics dashboard）
- [ ] 提及技術堆疊（PostgreSQL/TimescaleDB、FastAPI、React、Kafka 等）
- [ ] 同時提及原始預算（NT$340 萬）與修訂後預算（NT$410 萬）
- [ ] 同時掌握原始時程與更新後時程
- [ ] 摘要資安審查（security review）的發現
- [ ] 掌握客戶回饋與營收管線（NT$1.85 億–2.8 億 ARR）
- [ ] 摘要中排除了不相關郵件（員工感謝餐會、研討會）
- [ ] 目前專案狀態準確反映最新進度
- [ ] 資訊跨郵件綜整，而非逐封條列

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """郵件搜尋與摘要 grader（繁中台灣化：鼎峰科技 Project Alpha 信件串）。

    檢查 agent 產生的中文摘要 alpha_summary.md。盡量從 emails/ 動態推導應有事實
    （中文寄件者姓名、客戶公司名）再比對報告，避免硬寫；其餘以維持不變的數字錨點
    （預算 340/410/432 萬、ARR 1.85/2.8/2.1 億、日期 4/21、5/12、5/6、5/27）與
    技術 identifier 比對。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)
    summary_file = workspace / "alpha_summary.md"

    keys = [
        "file_created", "project_identified", "tech_stack", "budget_tracking",
        "timeline_tracking", "security_findings", "client_revenue",
        "noise_filtered", "has_required_sections", "cross_referencing",
    ]
    if not summary_file.exists():
        return {k: 0.0 for k in keys}

    scores["file_created"] = 1.0
    content = summary_file.read_text(encoding="utf-8", errors="ignore")
    cl = content.lower()

    # --- 從 emails/ 動態推導應有事實（寄件者中文姓名、客戶公司名），fallback 用預設 ---
    emails_dir = workspace / "emails"

    def _read(name):
        p = emails_dir / name
        return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

    def _sender_name(text):
        # 寄件者：lin.jy@…（林佳穎，專案負責人）-> 取「林佳穎」
        m = re.search(r"寄件者：[^（(]*[（(]([一-鿿]{2,4})[，,]", text)
        return m.group(1) if m else ""

    lead_name = _sender_name(_read("2026-01-15_project_alpha_kickoff.txt")) or "林佳穎"
    data_eng = _sender_name(_read("2026-01-22_alpha_data_pipeline.txt")) or "張哲瑋"
    cfo_name = _sender_name(_read("2026-02-03_alpha_budget_concern.txt")) or "趙麗娟"

    # 客戶公司名：從 client_feedback 郵件抓「（…ARR）」前的中文公司名
    e_clients = _read("2026-02-14_alpha_client_feedback.txt")
    client_companies = re.findall(
        r"([一-鿿]{2,8}(?:企業|科技|金融|股份有限公司))（[^）]*ARR）",
        e_clients,
    )
    if not client_companies:
        client_companies = ["宏遠企業", "全球通科技", "源資料股份有限公司",
                            "鼎泰金融", "雲匯科技"]

    # --- 1. 專案正確辨識為分析儀表板 ---
    if re.search(r"analytics\s+dashboard", cl) or "分析儀表板" in content:
        scores["project_identified"] = 1.0
    elif re.search(r"analytics|dashboard", cl) or re.search(r"分析|儀表板|報表", content):
        scores["project_identified"] = 0.5
    else:
        scores["project_identified"] = 0.0

    # --- 2. 技術堆疊涵蓋率（技術 identifier 維持英文）---
    tech_keywords = [
        r"postgresql|postgres|timescaledb",
        r"fastapi",
        r"react",
        r"kafka",
        r"flink",
        r"redis",
        r"recharts",
        r"dbt",
    ]
    tech_found = sum(1 for kw in tech_keywords if re.search(kw, cl))
    if tech_found >= 6:
        scores["tech_stack"] = 1.0
    elif tech_found >= 4:
        scores["tech_stack"] = 0.75
    elif tech_found >= 2:
        scores["tech_stack"] = 0.5
    else:
        scores["tech_stack"] = 0.25 if tech_found >= 1 else 0.0

    # --- 3. 預算追蹤（原始 340 萬與修訂 410 萬；432 萬亦計入修訂）---
    has_original = bool(re.search(r"340\s*萬|340\s*k|340,?000", cl))
    has_revised = bool(re.search(r"410\s*萬|432\s*萬|410\s*k|432\s*k|410,?000|432,?000", cl))
    if has_original and has_revised:
        scores["budget_tracking"] = 1.0
    elif has_original or has_revised:
        scores["budget_tracking"] = 0.5
    elif re.search(r"預算|成本|花費|支出|nt\$|\$\d", cl):
        scores["budget_tracking"] = 0.25
    else:
        scores["budget_tracking"] = 0.0

    # --- 4. 時程追蹤（原始與更新後日期，月份數值維持）---
    original_dates = [r"4\s*[/／月]\s*21", r"5\s*[/／月]\s*12"]
    updated_dates = [r"5\s*[/／月]\s*6", r"5\s*[/／月]\s*27"]
    orig_found = sum(1 for d in original_dates if re.search(d, cl))
    updated_found = sum(1 for d in updated_dates if re.search(d, cl))
    if orig_found >= 1 and updated_found >= 1:
        scores["timeline_tracking"] = 1.0
    elif orig_found >= 1 or updated_found >= 1:
        scores["timeline_tracking"] = 0.5
    elif re.search(r"延後|延遲|延誤|順延|延長|slip|delay|extend|push", cl):
        scores["timeline_tracking"] = 0.25
    else:
        scores["timeline_tracking"] = 0.0

    # --- 5. 資安發現（技術 identifier 維持英文 + 中文同義）---
    security_keywords = [
        r"cross.?tenant|跨租戶",
        r"websocket.{0,12}(auth|驗證|安全)|逐訊息.{0,6}驗證",
        r"rate.?limit|流量限制",
        r"ssrf",
        r"audit.?log|稽核日誌",
    ]
    sec_found = sum(1 for kw in security_keywords if re.search(kw, cl))
    if sec_found >= 3:
        scores["security_findings"] = 1.0
    elif sec_found >= 2:
        scores["security_findings"] = 0.75
    elif sec_found >= 1:
        scores["security_findings"] = 0.5
    elif re.search(r"security|資安|安全", cl):
        scores["security_findings"] = 0.25
    else:
        scores["security_findings"] = 0.0

    # --- 6. 客戶回饋與營收管線 ---
    has_client_names = sum(1 for name in client_companies if name and name in content)
    has_revenue = bool(re.search(
        r"1\.85\s*億|2\.8\s*億|2\.1\s*億|arr|年度經常性收入|營收", cl))
    if has_client_names >= 3 and has_revenue:
        scores["client_revenue"] = 1.0
    elif has_client_names >= 2 or has_revenue:
        scores["client_revenue"] = 0.75
    elif has_client_names >= 1:
        scores["client_revenue"] = 0.5
    elif re.search(r"客戶|顧客|業務|銷售|管線|潛在客戶", cl):
        scores["client_revenue"] = 0.25
    else:
        scores["client_revenue"] = 0.0

    # --- 7. 不相關郵件已被過濾掉 ---
    noise_indicators = [
        r"員工感謝餐會|感謝餐會|team\s*appreciation\s*lunch",
        r"科技高峰會\s*2026|techsummit\s*2026",
        r"早鳥票價|早鳥優惠|early\s*bird",
        r"地中海風.*燒烤|地中海.*亞洲.*燒烤",
        r"飲食偏好|dietary\s*preferences",
    ]
    noise_found = sum(1 for n in noise_indicators if re.search(n, cl))
    if noise_found == 0:
        scores["noise_filtered"] = 1.0
    elif noise_found == 1:
        scores["noise_filtered"] = 0.5
    else:
        scores["noise_filtered"] = 0.0

    # --- 8. 必要區段是否存在 ---
    required_sections = [
        r"概述|overview|專案簡介",
        r"時程|timeline|時間軸",
        r"風險|問題|risk|issue",
        r"客戶|業務|營收|client|business|revenue",
        r"狀態|現況|目前|status",
    ]
    sections_found = sum(1 for s in required_sections if re.search(s, cl))
    scores["has_required_sections"] = sections_found / len(required_sections)

    # --- 9. 跨郵件交叉參照 ---
    cross_ref_indicators = [
        # 資安發現導致時程延後
        r"(資安|安全|security).{0,120}(延後|延誤|延遲|順延|時程|延長|delay|slip|timeline|extend)",
        # 預算因基礎設施成本而增加
        r"(預算|成本|budget|cost).{0,120}(增加|上升|超支|擴編|擴充|修訂|調整|increas|overrun|expan|revis)",
        # 客戶回饋影響優先順序
        r"(客戶|顧客|回饋|client|customer|feedback).{0,120}(優先|功能|需求|排序|priorit|feature|request)",
        # spot instance 省下成本
        r"spot\s*instance.{0,120}(省|節省|降低|減少|sav|reduc|cost)",
    ]
    cross_refs = sum(1 for cr in cross_ref_indicators if re.search(cr, cl))
    if cross_refs >= 3:
        scores["cross_referencing"] = 1.0
    elif cross_refs >= 2:
        scores["cross_referencing"] = 0.75
    elif cross_refs >= 1:
        scores["cross_referencing"] = 0.5
    else:
        scores["cross_referencing"] = 0.0

    return scores


# --- Bilingual report normalization (中文 report -> English keywords) ---
# See docs/claw_eval_zh_schema.md §8 and scripts/lib_zh.py. The English-only
# path is unchanged (no CJK in reports -> direct passthrough, no shadow copy).
try:
    from lib_zh import normalize_zh_to_en as _zh_normalize
except Exception:  # noqa: BLE001
    def _zh_normalize(_text):
        return _text

_GRADE_IMPL = grade


def grade(transcript, workspace_path):  # noqa: F811
    """Shadow-normalize Chinese report text, then run the original grade()."""
    import shutil
    import tempfile
    from pathlib import Path as _P

    text_exts = (".md", ".txt", ".rst", ".markdown")
    ws = workspace_path
    try:
        src = _P(workspace_path)
        if src.exists() and src.is_dir():
            needs = False
            for f in src.rglob("*"):
                if f.is_file() and f.suffix.lower() in text_exts:
                    try:
                        if any("一" <= c <= "鿿" for c in f.read_text(encoding="utf-8")):
                            needs = True
                            break
                    except (OSError, UnicodeDecodeError):
                        pass
            if needs:
                shadow = _P(tempfile.mkdtemp(prefix="cez_ws_")) / "ws"
                shutil.copytree(src, shadow, dirs_exist_ok=True)
                for f in shadow.rglob("*"):
                    if f.is_file() and f.suffix.lower() in text_exts:
                        try:
                            f.write_text(
                                _zh_normalize(f.read_text(encoding="utf-8")),
                                encoding="utf-8",
                            )
                        except (OSError, UnicodeDecodeError):
                            pass
                ws = str(shadow)
    except Exception:  # noqa: BLE001
        ws = workspace_path
    return _GRADE_IMPL(transcript, ws)

```

## LLM Judge Rubric

### 評分項 1：資訊完整性（權重 25%）

**1.0 分**：摘要從全部 9 封相關郵件掌握 Project Alpha 的所有主要面向：專案定義、
技術堆疊、預算（原始與修訂）、時程（原始與修訂）、資料管線架構、API 設計、資安
發現、第一階段完成、含具體潛在客戶的客戶回饋，以及前端進度。沒有重大資訊缺口。

**0.75 分**：摘要掌握多數主要面向，僅有 1-2 個小遺漏。可能漏掉細節如特定客戶名稱
或精確預算數字，但整體輪廓正確。

**0.5 分**：摘要掌握主要敘事，但漏掉數個重要細節。可能只涵蓋 9 封相關郵件中 6-7 封
的內容。基本正確但缺乏深度。

**0.25 分**：摘要流於表面，只涵蓋 3-4 封郵件份量的內容。漏掉如資安審查或客戶回饋
等重大進展。

**0.0 分**：摘要缺失、為空，或未能掌握專案敘事。

### 評分項 2：資訊綜整品質（權重 25%）

**1.0 分**：摘要把跨郵件的資訊綜整成連貫敘事，而非逐封條列摘要。連結相關事實：
資安發現導致時程延後、預算經由特定協商過程從 NT$340 萬演變為 NT$410 萬、客戶回饋
回饋到功能優先順序、提早展開的前端工作緩解了時程延誤。並追蹤事實隨時間如何演變。

**0.75 分**：綜整良好，多數跨郵件連結都有做到。可能有些資訊是逐封依時間呈現而非
依主題，但展現出對事件關聯的理解。

**0.5 分**：部分綜整。做了一些連結，但大致讀起來像依時間排列的郵件摘要清單。漏掉
事件之間的關鍵關聯。

**0.25 分**：綜整極少。基本上是個別郵件摘要的清單，彼此之間鮮有連結。

**0.0 分**：沒有綜整。要嘛缺失，要嘛只是原始內容堆疊。

### 評分項 3：雜訊過濾與相關性（權重 15%）

**1.0 分**：正確辨識並排除 2 封不相關郵件（員工感謝餐會、研討會宣傳），同時納入
全部 9 封 Project Alpha 郵件。摘要中沒有出現不相關內容。清楚展現對相關性的判斷。

**0.75 分**：過濾大致正確。可能簡短提及某封不相關郵件，或漏掉一個邊緣的 Alpha
細節，但摘要明顯聚焦在 Project Alpha。

**0.5 分**：納入了一些來自非 Alpha 郵件的不相關內容，或漏掉 1-2 封相關的 Alpha
郵件。過濾判斷不一致。

**0.25 分**：過濾不佳。納入大量不相關內容或漏掉多封相關郵件。

**0.0 分**：未做過濾——所有郵件一視同仁，或只納入不相關內容。

### 評分項 4：結構與可讀性（權重 20%）

**1.0 分**：摘要依要求的 5 個區段架構（專案概述、時程、關鍵風險與問題、客戶／業務
影響、目前狀態）。各區段聚焦且組織良好，易於瀏覽。使用適當格式（標題、項目符號等）。
相關人員讀完即能快速掌握完整專案狀態。

**0.75 分**：結構良好且遵循要求格式，僅有少許組織問題。整體易讀、易瀏覽。

**0.5 分**：具備基本結構，但區段可能雜亂、重疊，或未遵循要求格式。需要較多力氣才能
取得關鍵資訊。

**0.25 分**：結構不佳。區段不清或缺失。文件難以導覽。

**0.0 分**：沒有可辨識的結構，或文件缺失。

### 評分項 5：準確性（權重 15%）

**1.0 分**：所有事實、數字與日期都準確呈現。預算數字、時程日期、客戶名稱、ARR
數字、技術選型與資安發現皆與原始郵件相符。沒有捏造資訊。

**0.75 分**：幾乎所有事實準確，僅有 1-2 個小錯誤（例如日期略誤、數字近似）。沒有
重大捏造。

**0.5 分**：有數個事實錯誤或不精確呈現。可能混淆不同郵件的細節，或在有精確數字
可用時給出近似資訊。

**0.25 分**：有重大事實錯誤，誤導了專案狀態。可能含有原始郵件中沒有的捏造細節。

**0.0 分**：通篇不準確或捏造內容。
