---
id: task_humanizer
name: 把 AI 生成的部落格改寫得更像真人撰寫
category: writing
grading_type: llm_judge
timeout_seconds: 120
language: zh
locale: zh-TW
source_task_id: task_humanizer
source_benchmark: pinchbench
claw_eval_id: P024zh_humanizer
workspace_files:
- source: ai_blog.txt
  dest: ai_blog.txt
---

# 把 AI 生成的部落格改寫得更像真人撰寫

## Prompt

我的工作區（workspace）裡有一篇 ai_blog.txt，讀起來太生硬、太像 AI 寫的。
請先用 `/install humanizer` 從 skill registry 安裝 humanizer 技能，再用它把
文字改寫得更自然、更像真人撰寫；如果該技能不可用，你可以手動改寫。

**請保留原文語言（英文），不要翻譯成中文。** 把改寫後的版本儲存到
humanized_blog.txt。

## Expected Behavior

助手應該：
1. 讀取 ai_blog.txt 裡的 AI 生成部落格
2. 使用 humanizer 技能／工具轉換內容（不可用時手動改寫）
3. 保持原文語言為英文，僅讓其更自然
4. 把改寫結果儲存到 humanized_blog.txt

改寫應處理常見的 AI 寫作痕跡：濫用轉折詞、過度修飾語氣、句式重複、不用縮寫、
過度正式、套話開頭（"In today's fast-paced world"）、像清單的段落等。

## Grading Criteria

- [ ] 助手讀取了輸入的部落格檔案
- [ ] 助手使用了 humanizer 技能／工具（或合理地手動改寫）
- [ ] 建立了含改寫內容的輸出檔案 humanized_blog.txt
- [ ] 內容保留原意與重點
- [ ] 文字讀起來更自然、更像真人撰寫
- [ ] AI 常見痕跡被減少或消除

## LLM Judge Rubric

### 評分項 1：技能使用或手動改寫（權重 25%）
- 1.0：正確安裝並使用 humanizer 技能，或完成高品質的手動改寫
- 0.75：嘗試安裝／使用技能，並適當退回手動改寫
- 0.5：有嘗試但方法不理想
- 0.25：僅做了極少量改寫
- 0.0：完全沒有嘗試改寫

### 評分項 2：輸出品質—自然語氣（權重 35%）
- 1.0：讀起來像真人撰寫，善用縮寫、句式多樣、語氣自然，無機械痕跡
- 0.75：大致自然，僅殘留少量機械感
- 0.5：有改善但仍有明顯 AI 痕跡或彆扭措辭
- 0.25：相較原文幾乎沒有改善
- 0.0：未改、變差或缺失

### 評分項 3：內容保留（權重 25%）
- 1.0：完整保留原文所有重點、建議與含義
- 0.75：大致保留，僅少量遺漏或更動
- 0.5：保留主要內容但遺失／扭曲部分重點
- 0.25：重大內容遺失或語意扭曲
- 0.0：內容完全改變或缺失

### 評分項 4：任務完成度（權重 15%）
- 1.0：正確處理兩個檔案—讀取輸入、輸出存到正確位置
- 0.75：完成但檔案處理有小瑕疵
- 0.5：部分完成—檔案位置／格式有誤
- 0.25：有嘗試但輸出未正確儲存
- 0.0：未建立輸出檔案

注意：本任務要求保留英文原文語言，若助手把內容翻成中文應視為偏離任務並扣分。
