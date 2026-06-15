---
id: task_log_nginx_user_agents
name: Nginx 存取日誌 — 使用者代理分析
category: log_analysis
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_log_nginx_user_agents
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: copy
claw_eval_tw_id: T088tw_log_nginx_user_agents
workspace_files:
- dest: nginx_access.log
  source: logs/nginx_access_json.log
---

# Nginx 存取日誌 — 使用者代理分析

## Prompt

請分析位於 `nginx_access.log` 的 Nginx JSON 存取日誌，並產生一份完整的使用者代理（user agent）分析。每一行都是一個 JSON 物件，欄位有：`time`、`remote_ip`、`remote_user`、`request`、`response`、`bytes`、`referrer`、`agent`。

你的報告應包含：

1. **不重複使用者代理（Unique User Agents）**：相異使用者代理字串的總數
2. **使用者代理排名（User Agent Ranking）**：依請求數排序列出所有使用者代理，並附計數與百分比
3. **用戶端類型分類（Client Type Classification）**：將代理分類（套件管理工具、網頁瀏覽器、機器人／爬蟲、命令列工具、未知／空白）
4. **代理對 IP 的對應（Agent-to-IP Mapping）**：對於每個使用者代理，有多少個不重複 IP 使用它？
5. **各代理的成功與錯誤率（Success vs Error Rate by Agent）**：對於每個代理，有多少百分比的請求造成錯誤（4xx/5xx）？
6. **結論（Conclusions）**：根據使用者代理的樣貌，這是何種類型的伺服器？

請把報告寫到 `user_agent_report.md`，以結構清晰的 markdown 文件呈現。

## Expected Behavior

助手應解析全部 1000 筆 JSON 日誌條目，並產生：

**不重複使用者代理：** 14 個相異代理字串（包含代表空白的「-」）

**主要使用者代理：**
- `Debian APT-HTTP/1.3 (0.9.7.9)` —— 370 次請求（37.0%）
- `Debian APT-HTTP/1.3 (0.8.16~exp12ubuntu10.16)` —— 177（17.7%）
- `Debian APT-HTTP/1.3 (0.8.16~exp12ubuntu10.22)` —— 118（11.8%）
- `Debian APT-HTTP/1.3 (1.0.1ubuntu2)` —— 116（11.6%）
- `Debian APT-HTTP/1.3 (0.8.16~exp12ubuntu10.21)` —— 64（6.4%）
- 其他 APT 變體及少數其他代理（Go 1.1 package http、urlgrabber 等）

**分類：**
- 套件管理工具（Debian APT）：絕大多數（約 95%+）
- 其他自動化工具：Go HTTP client、urlgrabber
- 空白／缺漏代理（「-」）：少量

**結論：**
- 這顯然是一台 Debian/Ubuntu 套件儲存庫或軟體下載鏡像站
- 多個 APT 版本顯示用戶端執行不同的 Ubuntu/Debian 發行版
- 幾乎沒有人為瀏覽器流量

可接受的變化：
- 精確計數由日誌決定，具確定性
- 分類類別可使用不同名稱
- 評估語言會有所不同

## Grading Criteria

- [ ] 已在工作區建立 `user_agent_report.md`
- [ ] 已列出所有使用者代理及其計數
- [ ] 代理已依類型分類（套件管理工具、機器人等）
- [ ] 已將主要代理（Debian APT）判定為首要用戶端
- [ ] 已正確推論伺服器用途（套件儲存庫／下載鏡像站）

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """Grade the Nginx user agent analysis task."""
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)
    report_file = workspace / "user_agent_report.md"

    if not report_file.exists():
        return {
            "output_created": 0.0,
            "agents_listed": 0.0,
            "agents_classified": 0.0,
            "apt_dominant": 0.0,
            "server_purpose": 0.0,
        }

    scores["output_created"] = 1.0
    content = report_file.read_text(encoding="utf-8").lower()

    # Check 1: User agents listed with counts
    has_apt = "apt-http" in content or "apt http" in content or "debian apt" in content
    has_counts = any(str(c) in content for c in ["370", "177", "118", "116"])
    scores["agents_listed"] = (
        1.0 if has_apt and has_counts else
        0.5 if has_apt else 0.0
    )

    # Check 2: Agents classified by type
    type_keywords = ["package manager", "bot", "crawler", "automated", "tool",
                     "browser", "command line", "cli", "client type", "categor"]
    scores["agents_classified"] = (
        1.0 if sum(1 for kw in type_keywords if kw in content) >= 2 else
        0.5 if sum(1 for kw in type_keywords if kw in content) >= 1 else 0.0
    )

    # Check 3: APT identified as dominant
    dominant_keywords = ["dominant", "majority", "most common", "primary",
                         "most frequent", "largest", "overwhelming"]
    has_dominant = any(kw in content for kw in dominant_keywords)
    scores["apt_dominant"] = (
        1.0 if has_apt and has_dominant else
        0.5 if has_apt else 0.0
    )

    # Check 4: Server purpose inferred
    purpose_keywords = ["repository", "mirror", "download", "package",
                        "software", "debian", "ubuntu", "apt"]
    scores["server_purpose"] = (
        1.0 if sum(1 for kw in purpose_keywords if kw in content) >= 3 else
        0.5 if sum(1 for kw in purpose_keywords if kw in content) >= 1 else 0.0
    )

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

依下列評分標準逐項評估（每項 0.0–1.0，最後取平均）：
- 已在工作區建立 `user_agent_report.md`
- 已列出所有使用者代理及其計數
- 代理已依類型分類（套件管理工具、機器人等）
- 已將主要代理（Debian APT）判定為首要用戶端
- 已正確推論伺服器用途（套件儲存庫／下載鏡像站）
