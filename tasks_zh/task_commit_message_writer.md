---
id: task_commit_message_writer
name: Commit 訊息撰寫
category: writing
grading_type: llm_judge
timeout_seconds: 120
language: zh
locale: zh-TW
source_task_id: task_commit_message_writer
source_benchmark: pinchbench
claw_eval_id: P025zh_commit_message_writer
workspace_files:
- path: change.diff
  content: "diff --git a/src/auth/session.ts b/src/auth/session.ts\nindex 3a1c4e8..b7f2d91 100644\n---\
    \ a/src/auth/session.ts\n+++ b/src/auth/session.ts\n@@ -12,8 +12,10 @@ import { Redis } from 'ioredis';\n\
    \ \n const SESSION_TTL = 3600; // 1 hour\n \n-export async function createSession(userId: string):\
    \ Promise<string> {\n+export async function createSession(userId: string, rememberMe: boolean = false):\
    \ Promise<string> {\n   const token = crypto.randomUUID();\n+  const ttl = rememberMe ? SESSION_TTL\
    \ * 24 * 30 : SESSION_TTL;\n+\n   const session: Session = {\n     userId,\n     token,\n@@ -21,7\
    \ +23,7 @@ export async function createSession(userId: string): Promise<string> {\n     isActive:\
    \ true,\n   };\n \n-  await redis.set(`session:${token}`, JSON.stringify(session), 'EX', SESSION_TTL);\n\
    +  await redis.set(`session:${token}`, JSON.stringify(session), 'EX', ttl);\n   await redis.sAdd(`user_sessions:${userId}`,\
    \ token);\n \n   return token;\n@@ -45,3 +47,15 @@ export async function destroySession(token: string):\
    \ Promise<void> {\n   await redis.sRem(`user_sessions:${session.userId}`, token);\n   await redis.del(`session:${token}`);\n\
    \ }\n+\n+export async function refreshSession(token: string): Promise<boolean> {\n+  const raw = await\
    \ redis.get(`session:${token}`);\n+  if (!raw) return false;\n+\n+  const session: Session = JSON.parse(raw);\n\
    +  const remaining = await redis.ttl(`session:${token}`);\n+  const originalTtl = remaining > SESSION_TTL\
    \ ? SESSION_TTL * 24 * 30 : SESSION_TTL;\n+\n+  await redis.expire(`session:${token}`, originalTtl);\n\
    +  return true;\n+}\ndiff --git a/src/auth/session.test.ts b/src/auth/session.test.ts\nindex 8e21f3a..c4d9b72\
    \ 100644\n--- a/src/auth/session.test.ts\n+++ b/src/auth/session.test.ts\n@@ -22,6 +22,28 @@ describe('createSession',\
    \ () => {\n     expect(parsed.isActive).toBe(true);\n   });\n \n+  it('should create a session with\
    \ extended TTL when rememberMe is true', async () => {\n+    const token = await createSession('user-1',\
    \ true);\n+    const ttl = await redis.ttl(`session:${token}`);\n+    expect(ttl).toBeGreaterThan(SESSION_TTL);\n\
    +  });\n+});\n+\n+describe('refreshSession', () => {\n+  it('should reset TTL for an active session',\
    \ async () => {\n+    const token = await createSession('user-1');\n+    // wait a tick so TTL decreases\n\
    +    await new Promise(r => setTimeout(r, 50));\n+    const result = await refreshSession(token);\n\
    +    expect(result).toBe(true);\n+    const ttl = await redis.ttl(`session:${token}`);\n+    expect(ttl).toBeGreaterThan(SESSION_TTL\
    \ - 5);\n+  });\n+\n+  it('should return false for a nonexistent session', async () => {\n+    const\
    \ result = await refreshSession('nonexistent-token');\n+    expect(result).toBe(false);\n+  });\n\
    \ });\n \n describe('destroySession', () => {"
---

# Commit 訊息撰寫

## Prompt

請閱讀 `change.diff` 中的 unified diff。為這些變更撰寫一則妥善、符合慣例的
commit 訊息，並儲存到 `commit_message.txt`。

注意：commit 訊息屬慣例性的英文格式，請以英文撰寫；以下需求說明僅以中文呈現。

需求：

1. 遵循 Conventional Commits 格式：`type(scope): description`
2. 第一行（主旨）必須在 72 個字元以內。
3. 包含一段內文（與主旨以空行隔開），說明這項變更**為何**進行，而不只是變更了
   什麼。
4. 不要在 commit 訊息中放入原始的 diff。
5. 訊息僅能為純文字，不可使用 markdown 排版。

## Expected Behavior

助手應該閱讀 diff 並辨識出：

- 在 session 建立流程中新增了 `rememberMe` 選項，並搭配延長的 TTL。
- 新增了一個 `refreshSession` 函式，用於重設 session 的 TTL。
- 為這兩項變更新增了對應的測試。

優秀的 commit 訊息會：

- 使用恰當的 type（例如 `feat`）搭配 scope（例如 `auth` 或 `session`）。
- 主旨簡潔，概括此功能（例如「add remember-me and session refresh support」）。
- 內文說明動機：為選擇啟用的使用者提供持久性 session，以及延長進行中 session 的
  能力。
- 在內文中提及測試涵蓋，但不過度著墨細節。

## Grading Criteria

- [ ] 已建立檔案 `commit_message.txt`
- [ ] 使用 Conventional Commits 格式（`type(scope): description`）
- [ ] 主旨行在 72 個字元以內
- [ ] 包含一段以空行隔開的內文
- [ ] 內文說明動機／為何，而不只是覆述 diff
- [ ] 正確概括 diff 中的所有變更
- [ ] 輸出中沒有原始 diff 內容或 markdown 排版

## LLM Judge Rubric

### 評分項 1：格式符合度（權重 25%）

**1.0 分**：精確遵循 Conventional Commits — type 正確、scope 可選、主旨為祈使
語氣且在 72 字元以內、內文前有空行。

**0.75 分**：格式大致正確，僅有一處小問題（例如略超過 72 字元，或缺少 scope）。

**0.5 分**：是可辨識的 commit 訊息格式，但在明顯之處偏離 Conventional Commits。

**0.25 分**：有主旨與內文，但無慣例性結構。

**0.0 分**：並非可辨識的 commit 訊息格式。

### 評分項 2：主旨行品質（權重 25%）

**1.0 分**：簡潔、祈使語氣，準確抓住主要變更（remember-me session 與／或
session refresh）。不堆砌不必要的細節。

**0.75 分**：概括良好，僅有小幅措辭問題，或範圍略嫌過寬／過窄。

**0.5 分**：可理解，但概括含糊或部分不準確。

**0.25 分**：具誤導性或過於空泛（例如「update session code」）。

**0.0 分**：主旨缺漏或完全不準確。

### 評分項 3：內文品質 — 動機與脈絡（權重 30%）

**1.0 分**：內文清楚說明變更的原因（例如使用者需要持久性 session、session 應可
刷新），涵蓋兩項功能，並提及新增測試而不過度著墨細節。

**0.75 分**：內文提供良好脈絡，僅有小幅缺漏（例如漏掉兩項功能之一，或未提及
測試）。

**0.5 分**：有內文，但多半是覆述 diff 做了什麼，而非為何。

**0.25 分**：內文極少，對主旨行幾乎沒有補充。

**0.0 分**：沒有內文，或內文含有原始 diff／無關內容。

### 評分項 4：正確性與完整性（權重 20%）

**1.0 分**：訊息準確反映所有變更：`rememberMe` 參數、延長的 TTL、新的
`refreshSession` 函式，以及相關測試。無捏造細節。

**0.75 分**：準確抓住大部分變更，僅有一處小幅遺漏。

**0.5 分**：抓住大致概念，但漏掉重大變更或含有不準確之處。

**0.25 分**：有重大不準確之處，或漏掉大部分變更。

**0.0 分**：未反映實際的 diff 內容。
