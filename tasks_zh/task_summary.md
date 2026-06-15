---
id: task_summary
name: 文件摘要
category: analysis
grading_type: llm_judge
timeout_seconds: 240
language: zh
locale: zh-TW
source_task_id: task_summary
source_benchmark: pinchbench
claw_eval_id: P041zh_summary
workspace_files:
- path: summary_source.txt
  content: |-
    The Rise of Artificial Intelligence in Modern Healthcare

    Artificial intelligence (AI) has emerged as a transformative force in healthcare, revolutionizing how medical professionals diagnose diseases, develop treatment plans, and manage patient care. Over the past decade, machine learning algorithms have demonstrated remarkable capabilities in analyzing medical imaging, predicting patient outcomes, and identifying patterns that might escape human observation.

    One of the most significant applications of AI in healthcare is in medical imaging analysis. Deep learning models can now detect cancerous tumors, identify fractures, and diagnose conditions like diabetic retinopathy with accuracy rates that match or exceed those of experienced radiologists. These systems process thousands of images during training, learning to recognize subtle patterns and anomalies that indicate disease. For instance, Google's DeepMind has developed AI systems that can detect over 50 eye diseases from retinal scans with 94% accuracy.

    Beyond imaging, AI is making strides in drug discovery and development. Traditional drug development is a lengthy and expensive process, often taking over a decade and costing billions of dollars. AI algorithms can analyze vast databases of molecular structures, predict how different compounds will interact with disease targets, and identify promising drug candidates much faster than traditional methods. During the COVID-19 pandemic, AI played a crucial role in accelerating vaccine development and identifying potential treatments.

    Predictive analytics represents another frontier where AI is proving invaluable. By analyzing electronic health records, genetic information, and lifestyle factors, AI systems can predict which patients are at high risk for conditions like heart disease, diabetes, or hospital readmission. This enables healthcare providers to intervene earlier with preventive care, potentially saving lives and reducing healthcare costs. Some hospitals have implemented AI systems that predict patient deterioration hours before it becomes clinically apparent, allowing medical teams to take proactive measures.

    However, the integration of AI in healthcare is not without challenges. Privacy concerns are paramount, as these systems require access to sensitive patient data. There are also questions about algorithmic bias, as AI systems trained on non-diverse datasets may perform poorly for underrepresented populations. Additionally, the "black box" nature of some AI algorithms makes it difficult for doctors to understand how the system reached a particular conclusion, which can be problematic in medical decision-making where transparency is crucial.

    Regulatory frameworks are still evolving to keep pace with AI innovation. The FDA and other regulatory bodies worldwide are developing new guidelines for approving AI-based medical devices and ensuring they meet safety and efficacy standards. There's also the question of liability: when an AI system makes an error, who is responsible—the developer, the healthcare provider, or the institution?

    Despite these challenges, the future of AI in healthcare looks promising. Researchers are working on explainable AI systems that can provide clear reasoning for their recommendations. Federated learning approaches allow AI models to be trained on distributed datasets without compromising patient privacy. As these technologies mature and regulatory frameworks solidify, AI is expected to become an increasingly integral part of healthcare delivery.

    The key to successful AI integration lies in viewing these systems as tools to augment, rather than replace, human medical expertise. The most effective healthcare delivery will likely combine the pattern recognition and data processing capabilities of AI with the empathy, ethical judgment, and contextual understanding that human healthcare providers bring to patient care. This collaborative approach promises to improve outcomes, reduce costs, and make quality healthcare more accessible to populations around the world.
---

# 文件摘要

## Prompt

請閱讀 summary_source.txt 中的文件，並把一份精簡的 3 段摘要寫入 summary_output.txt。

## Expected Behavior

助手應該：

1. 讀取 summary_source.txt（工作區中提供）的內容
2. 理解主要論點與核心主題
3. 撰寫一份精簡的 3 段摘要，內容涵蓋：
   - 主題與整體概述（第 1 段）
   - 關鍵應用與效益（第 2 段）
   - 挑戰與未來展望（第 3 段）
4. 把摘要儲存到 summary_output.txt
5. 在保持精簡的同時維持準確性

摘要應明顯短於原文，同時保留必要資訊。

## Grading Criteria

- [ ] 已建立 summary_output.txt 檔案
- [ ] 摘要剛好有 3 段
- [ ] 摘要準確掌握主題（醫療領域的 AI）
- [ ] 摘要提及關鍵應用（醫療影像、藥物研發、預測分析）
- [ ] 摘要談及挑戰（隱私、偏誤、法規）
- [ ] 摘要精簡（明顯短於原文）
- [ ] 行文清晰、連貫
- [ ] 沒有重大事實錯誤或失真

## LLM Judge Rubric

### 評分項 1：準確性與完整性（權重 35%）

**1.0 分**：摘要準確掌握所有主要主題：AI 在醫療的應用（醫療影像、藥物研發、預測分析）、效益、挑戰（隱私、偏誤、法規）與未來展望。沒有事實錯誤或失真。

**0.75 分**：摘要掌握多數主要主題，僅有少數遺漏。某一關鍵面向可能著墨不足。沒有重大事實錯誤。

**0.5 分**：摘要掌握部分主要主題，但漏掉重要面向。可能有輕微事實不準確，或過度強調較不重要的論點。

**0.25 分**：摘要漏掉多個主要主題，或含有重大事實錯誤。對原文的呈現不佳。

**0.0 分**：摘要完全不準確、離題或缺失。

### 評分項 2：精簡度（權重 25%）

**1.0 分**：摘要長度適中（150-250 字），在不堆砌細節的前提下掌握必要資訊。資訊密度極佳。

**0.75 分**：摘要相當精簡（250-350 字），資訊密度良好。略顯冗長。

**0.5 分**：摘要略嫌冗長（350-450 字），或過短（少於 100 字），未能在精簡與完整之間取得平衡。

**0.25 分**：摘要過長（超過 450 字），或過短（少於 75 字）以致沒有用處。

**0.0 分**：摘要長度完全不恰當，或內容缺失。

### 評分項 3：結構與連貫性（權重 20%）

**1.0 分**：剛好 3 段，組織良好且邏輯流暢。第 1 段介紹主題，第 2 段涵蓋應用／效益，第 3 段談挑戰／未來。銜接與連貫性極佳。

**0.75 分**：3 段且組織良好。在流暢度或段落聚焦上有少許問題。整體連貫。

**0.5 分**：有 3 段但存在組織問題，或段數錯誤（2 段或 4 段）但其餘結構尚可。連貫性略有問題。

**0.25 分**：結構不佳且連貫性問題顯著。可能段數錯誤且內容雜亂。

**0.0 分**：沒有可辨識的結構，或內容缺失。

### 評分項 4：寫作品質（權重 15%）

**1.0 分**：寫作出色，行文清晰、專業。沒有文法或拼字錯誤。用詞與語氣恰當。

**0.75 分**：寫作品質良好，僅有少許問題。文法錯誤很少。整體清晰、專業。

**0.5 分**：寫作尚可，但有明顯文法問題、措辭彆扭或表達不清。

**0.25 分**：寫作品質不佳，錯誤多或表達不清。

**0.0 分**：寫作難以理解或缺失。

### 評分項 5：任務完成度（權重 5%）

**1.0 分**：以正確檔名（summary_output.txt）建立檔案，助手讀取了原始檔案，所有要求皆達成。

**0.75 分**：建立檔案但有小問題（例如檔名略有差異），但任務基本完成。

**0.5 分**：建立檔案但有顯著問題或漏掉要求。

**0.25 分**：建立檔案但內容嚴重不足或錯誤。

**0.0 分**：未建立檔案，或檔案為空。
