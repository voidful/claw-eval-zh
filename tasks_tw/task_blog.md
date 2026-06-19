---
id: task_blog
name: 部落格文章撰寫
category: writing
grading_type: llm_judge
timeout_seconds: 300
language: zh
locale: zh-TW
region: TW
source_task_id: task_blog
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: language_polish
claw_eval_tw_id: T021tw_blog
workspace_files: []
---

# 部落格文章撰寫

## Prompt

請撰寫一篇約 500 字、主題為「遠端工作對台灣軟體開發者的好處」的部落格文章，
並儲存到 blog_post.md。

請以**繁體中文**撰寫，語氣自然、貼近台灣讀者，內容請具體（可舉台灣的情境，
例如通勤、工時彈性、人才市場等）。

## Expected Behavior

助手應撰寫一篇結構完整、約 500 字的繁體中文部落格文章，主題為遠端工作對台灣
軟體開發者的好處，內容具體、語氣自然，並儲存到 `blog_post.md`。

## Grading Criteria

- [ ] 已建立檔案 `blog_post.md`
- [ ] 文章以繁體中文撰寫
- [ ] 主題切合「遠端工作對軟體開發者的好處」
- [ ] 篇幅約 500 字
- [ ] 結構清楚（有開頭、主體、結尾）
- [ ] 內容具體、可讀性佳

## LLM Judge Rubric

### 評分項 1：主題切合與內容深度（權重 40%）

**1.0 分**：緊扣主題，提出具體、有說服力的論點（如通勤時間、工時彈性、人才
市場、跨縣市協作等），並貼近台灣情境。
**0.5 分**：切題但論點空泛或重複。
**0.0 分**：離題或內容貧乏。

### 評分項 2：語言與可讀性（權重 35%）

**1.0 分**：通順自然的繁體中文，無翻譯腔、無中國用語，標點正確。
**0.5 分**：大致通順，但有生硬措辭或用詞問題。
**0.0 分**：難以閱讀，或並非繁體中文。

### 評分項 3：結構與篇幅（權重 25%）

**1.0 分**：結構清楚（開頭、主體、結尾），篇幅約 500 字。
**0.5 分**：結構或篇幅有明顯問題。
**0.0 分**：無明確結構，或嚴重偏離篇幅。
