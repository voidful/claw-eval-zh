# 用一個 HuggingFace model id 跑 claw-eval-zh

目標：**只給一個 HuggingFace model id,整套任務就能跑起來**(含原本會失敗的
skills / integrations 類)。本文說明背後機制與一鍵指令。

---

## 0. TL;DR

```bash
# 1) 必裝:OpenClaw（agent 執行器）— 沒它所有任務都不能跑
which openclaw

# 2) HF token（router 模式用,免 GPU）
export HF_TOKEN=hf_xxx

# 3) 一鍵跑（台灣在地版,自動安裝 fws mock、跳過環境未就緒的任務）
python scripts/run_hf_benchmark.py --hf-model Qwen/Qwen2.5-7B-Instruct --auto-install
```

就這樣。其餘前置(fws / gws / gh / 影像金鑰)會被 **preflight** 自動偵測:能裝的自動裝,
裝不了的會清楚告訴你補法,並把「環境未就緒」的任務**跳過(不計入分數)**,不會出現先前
那種「整類 0% 失敗」的假象。

---

## 1. 為什麼可以「只給 model id」

執行器是 **OpenClaw**;它的模型設定支援任何 **OpenAI 相容端點**
([scripts/lib_agent.py](../scripts/lib_agent.py) 的 `custom` provider)。HuggingFace 模型
正好能透過 OpenAI 相容端點存取,所以我們把「HF model id → 端點 → benchmark」串起來。

[scripts/run_hf_benchmark.py](../scripts/run_hf_benchmark.py) 提供三種服務方式 `--serve`:

| 模式 | 端點 | 需求 | 適用 |
|---|---|---|---|
| `router`（預設） | `https://router.huggingface.co/v1` | **HF token**,免 GPU | 最省事,「只給 model id」 |
| `local` | 本機 `vLLM`（`http://127.0.0.1:8000/v1`） | GPU + `pip install vllm` | 自架、離線推論 |
| `endpoint` | 你自己的 `--base-url` | 視端點而定 | TGI / HF 專用 Inference Endpoint |

範例:

```bash
# router（預設）
python scripts/run_hf_benchmark.py --hf-model meta-llama/Llama-3.3-70B-Instruct

# 本機 vLLM
python scripts/run_hf_benchmark.py --hf-model my/model --serve local

# 自訂端點
python scripts/run_hf_benchmark.py --hf-model my/model --serve endpoint \
       --base-url http://localhost:8080/v1 --api-key EMPTY
```

`--dry-run` 會印出將執行的 `benchmark.py` 指令與要跑的任務數,**不啟動模型、不連網**,可先預覽。

---

## 2. 任務就緒矩陣（147 題）

裝好 OpenClaw 後,**142/147 題只需要模型**就能跑。其餘 5 題需要額外前置:

| 任務 | 需要 | 能自動裝? | 說明 |
|---|---|:---:|---|
| `task_gws_email_triage`、`task_gws_cross_service`、`task_gws_task_management` | `fws` + `gws` CLI | fws ✅ / gws ✋ | GWS 任務 |
| `task_gh_issue_triage` | `fws` + `gh` CLI | fws ✅ / gh 多半已裝 | GitHub 任務 |
| `task_image_gen` | `OPENROUTER_API_KEY` | ✋ | 影像生成工具 |

隨時可查就緒狀況:

```bash
python scripts/preflight_env.py --language tw --suite all          # 全部
python scripts/preflight_env.py --language tw --suite integrations # 只看某類
python scripts/preflight_env.py --language tw --install            # 順便自動裝 fws
```

---

## 3. 重要:不需要真實 Google / GitHub 憑證

GWS / GitHub 類任務用的是 **`fws`(Fake Web Services)本地 mock 伺服器**(`@juppytt/fws`),
內建固定 seed 資料,**完全不需要真實帳號或憑證**。執行時 runner 會自動
`fws server start`/`stop`(見 [scripts/lib_fws.py](../scripts/lib_fws.py)),把 `gws`/`gh`
的 API 呼叫導向本地 mock。這對**可重現性**是好事:答案來自固定 mock,不隨真實信箱變動。

- `fws`:`npm install -g @juppytt/fws`(本工具的 `--auto-install` 會幫你裝)
- `gws`:Google Workspace CLI 用戶端,需另行安裝(見 `@juppytt/fws` README 的 gws 章節)
- `gh`:`brew install gh`(多數環境已有)

---

## 4. 環境未就緒時的行為（避免污染分數）

預設 `run_hf_benchmark.py` 會**只跑環境就緒的任務**,並列出被跳過的任務與原因
(跳過的不計入分母,所以不會像先前那樣顯示「整類 0% 失敗」)。

- 想強制連未就緒的任務一起跑:加 `--include-unready`。
- 直接用 `benchmark.py` 而未裝前置時,缺 `fws` 的任務只會記為失敗(0 分)——這正是本包裝
  工具與 preflight 存在的原因。

---

## 5. 常用參數

| 參數 | 預設 | 說明 |
|---|---|---|
| `--hf-model` | （必填） | HuggingFace model id |
| `--hf-token` | `$HF_TOKEN` 等 | router 模式必需 |
| `--serve` | `router` | `router` / `local` / `endpoint` |
| `--language` | `tw` | `en` / `zh` / `tw` |
| `--suite` | `all` | 類別名稱或逗號分隔 task id |
| `--runs` | `1` | 每題次數(pass@k / pass^k) |
| `--pass-threshold` | `0.8` | pass 門檻 |
| `--auto-install` | 關 | 自動安裝 fws |
| `--include-unready` | 關 | 不跳過未就緒任務 |
| `--dry-run` | 關 | 只預覽,不執行 |

---

## 6. 注意

- 本工具**不會偽造跑分**;沒有模型/token/OpenClaw 時不會產生任何結果。
- `local` 模式需要 GPU 與 `vllm`,屬選配。
- 真正的端到端跑分仍需你提供 HF token(或自架端點)與 OpenClaw 執行器。
