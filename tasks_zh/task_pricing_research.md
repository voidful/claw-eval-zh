---
id: task_pricing_research
name: 供應商定價比較
category: research
grading_type: llm_judge
timeout_seconds: 300
language: zh
locale: zh-TW
source_task_id: task_pricing_research
source_benchmark: pinchbench
claw_eval_id: P017zh_pricing_research
workspace_files: []
---

# 供應商定價比較

## Prompt

你的團隊需要為一個正式環境（production）應用程式選擇一項 **託管型 PostgreSQL
資料庫服務（managed PostgreSQL database service）**。請比較以下供應商的定價：

1. **AWS RDS for PostgreSQL**
2. **Google Cloud SQL for PostgreSQL**
3. **Azure Database for PostgreSQL**
4. **DigitalOcean Managed Databases**
5. **Neon**（serverless Postgres）

為了進行標準化比較，請為兩種配置估價：

**Config A（Small）：** 2 vCPUs、8 GB RAM、100 GB 儲存空間、單一可用區（single zone）
**Config B（Production）：** 4 vCPUs、16 GB RAM、500 GB 儲存空間、高可用性
（high availability，multi-AZ/replica）

針對每家供應商，記錄：
- Config A 與 Config B 的每月預估費用
- 包含哪些項目（備份、監控、連線池 connection pooling）
- 定價模式（per-hour、per-month、serverless/用量制）
- 隱藏成本（資料傳輸、IOPS、備份儲存等）
- 是否提供免費方案或試用

請將你的分析儲存至 `pricing_comparison.md`，內容須包含：
- 置於最上方的定價比較表格
- 各供應商的詳細拆解
- 點出隱藏成本的總體擁有成本（total cost of ownership）分析
- 一份附理由的建議

## Expected Behavior

助手應該：

1. 從各供應商的定價頁面研究目前的定價
2. 將兩種配置對應到最接近的可用機型（instance types）
3. 計算含相關附加項目的每月費用
4. 找出隱藏或容易被忽略的成本
5. 建立一份結構化的比較文件
6. 儲存至 `pricing_comparison.md`

## Grading Criteria

- [ ] 已建立檔案 pricing_comparison.md
- [ ] 5 家供應商皆有涵蓋
- [ ] 為每家估算 Config A 的價格
- [ ] 為每家估算 Config B 的價格
- [ ] 找出隱藏成本
- [ ] 包含定價表格
- [ ] 提及機型／SKU
- [ ] 包含免費方案資訊
- [ ] 附理由的建議
- [ ] 價格看起來合理且為最新

## LLM Judge Rubric

### 評分項 1：定價正確性（權重 30%）

**1.0 分**：每月費用估算具體（含金額），且落在目前市場行情的合理範圍內。有指明機型
或 SKU。估算涵蓋運算、儲存與 I/O。明顯取自定價頁面。
**0.75 分**：估算合理並指明機型。有小幅不準確，或遺漏部分成本項目。
**0.5 分**：估算的數量級正確，但缺乏具體性。定價籠統，未指明機型。
**0.25 分**：估算含糊，或定價明顯過時。
**0.0 分**：無定價資訊，或估算極度不準確。

### 評分項 2：隱藏成本分析（權重 25%）

**1.0 分**：找出各供應商特有的隱藏成本——資料傳輸出口（egress）、IOPS 費用、超出
免費額度的備份保留、連線數限制、監控附加項目、跨區複寫成本。並至少量化其中部分項目。
**0.75 分**：找出數項隱藏成本，並有部分量化。
**0.5 分**：提及存在隱藏成本，但未量化或流於含糊。
**0.25 分**：對額外成本幾乎未著墨。
**0.0 分**：未探討隱藏成本。

### 評分項 3：比較完整度（權重 20%）

**1.0 分**：兩種配置皆為 5 家供應商完成估價。包含哪些項目內含（備份、監控、HA）
vs. 哪些需額外付費。免費方案細節正確。定價模式說明清楚。
**0.75 分**：多數供應商皆完成兩種配置的估價。內含功能或免費方案資訊有小幅缺口。
**0.5 分**：一種配置涵蓋良好，另一種單薄。或所有供應商皆有涵蓋但流於表面。
**0.25 分**：涵蓋有重大缺口。
**0.0 分**：涵蓋少於 3 家供應商，或無針對特定配置的定價。

### 評分項 4：呈現與可用性（權重 15%）

**1.0 分**：乾淨的比較表格讓人能一目了然地比較。詳細拆解組織一致。可實際用於採購
決策。
**0.75 分**：表格與組織良好。有小幅排版問題。
**0.5 分**：有資訊，但難以跨供應商比較。
**0.25 分**：組織不佳。
**0.0 分**：無比較結構。

### 評分項 5：建議品質（權重 10%）

**1.0 分**：建議考量總體擁有成本，而不只是表面價格。依使用情境區分（新創 vs. 企業）。
坦承權衡取捨（價格 vs. 功能 vs. 維運簡易度）。
**0.75 分**：建議良好且附理由。細膩度有小幅缺口。
**0.5 分**：建議籠統，缺乏強有力的理由。
**0.25 分**：建議含糊或缺乏佐證。
**0.0 分**：無任何建議。
