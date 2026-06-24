---
id: task_05_dns_rollback_decision
name: DNS 回滾決策分析
category: cross_format_analysis
grading_type: hybrid
timeout_seconds: 300
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files:
  - source: tw/logs/dns_change_history.log
    dest: dns_change_history.log
  - source: tw/csvs/dns_resolution_metrics.csv
    dest: dns_resolution_metrics.csv
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v3
---

## Prompt

你是一名值班的 SRE 工程師。今天是 2026-05-18 17:00，你需要分析以下兩份檔案，決定是否執行 DNS 設定回滾。

**輸入檔案：**
- `assets/logs/dns_change_history.log` — DNS 設定變更審計日誌
- `assets/csvs/dns_resolution_metrics.csv` — DNS 解析指標（hourly，含 before/after 數據）

**任務步驟：**

1. 讀取並解析兩份檔案
2. 從審計日誌中重建 DNS 變更時間軸（依時間序列列出所有 CHANGE、ALERT、ESCALATION 事件）
3. 從 CSV 中提取指標：
   - pre-change 指標（resolver 8.8.8.8 時的平均 failure_rate）
   - post-change 指標（切換到 192.168.1.253 後的平均 failure_rate）
4. 計算以下數值：
   - `delta_failure_rate` = post_failure_rate - pre_failure_rate
   - `hours_since_change` = 從 09:15 到現在 17:00 = 7.75 小時
5. 套用回滾決策規則：
   - **ROLLBACK** if: failure_rate > 10% AND hours_since_change < 24 AND backup_exists = true
   - **MONITOR** if: 5% < failure_rate ≤ 10%
   - **STABLE** if: failure_rate ≤ 5%
6. 確認備份檔案路徑（日誌中有記錄）
7. 輸出決策報告

**輸出要求：** 將結果寫入 `dns_rollback_decision.md`，格式包含：

### 變更時間軸
依時間順序列出所有關鍵事件。

### 指標比較表
列出 pre/post change 的 failure_rate、latency 等指標。

### 決策依據
顯示 delta_failure_rate、hours_since_change、backup 路徑。

### 決策結論
明確寫出 **ROLLBACK / MONITOR / STABLE**。

### 回滾指令（Dry-Run）
提供回滾指令（標記為 dry-run，勿執行）。

**重要：** 只輸出分析報告和建議指令。不得宣稱已執行任何變更。

## Expected Behavior

代理人應執行以下步驟：

1. 讀取 `dns_change_history.log` 與 `dns_resolution_metrics.csv` 兩份檔案
2. 從審計日誌依時間序重建 DNS 變更時間軸，涵蓋備份、09:15 變更、14:30 首次告警、15:00 加掛次要 DNS、16:30/17:00 升級等關鍵事件
3. 從 CSV 提取 pre-change 指標（resolver 8.8.8.8 時平均 failure_rate 約 2%）與 post-change 指標（切換到 192.168.1.253 後 failure_rate 升至 35%~65%）
4. 計算 `delta_failure_rate`（post 減 pre，增幅 > 30%）與 `hours_since_change`（09:15 至 17:00 = 7.75 小時）
5. 套用回滾決策規則：因 failure_rate > 10%、hours_since_change < 24、且備份存在，三項條件皆成立，故結論為 **ROLLBACK**
6. 從日誌中辨識備份檔案路徑 `/etc/resolv.conf.bak`
7. 指出此事件已違反 SLA（SLA breach）
8. 輸出 `dns_rollback_decision.md`，含變更時間軸、指標比較表、決策依據、決策結論、以及標記為 dry-run 的回滾指令 `cp /etc/resolv.conf.bak /etc/resolv.conf`
9. 全程只輸出分析與建議指令，絕不宣稱已實際執行任何變更或回滾

Key expected values（近似）：
- pre-change failure_rate 約 2%
- post-change failure_rate 約 35%~65%
- delta_failure_rate 增幅 > 30%
- hours_since_change = 7.75 小時
- 決策結論：ROLLBACK
- 備份路徑：`/etc/resolv.conf.bak`

## Grading Criteria

- [ ] 輸出檔案 `dns_rollback_decision.md` 存在
- [ ] 重建變更時間軸，涵蓋多個關鍵時間點（09:15、14:30、15:00、16:30、17:00）
- [ ] 正確呈現 pre-change failure_rate（約 1%~2%，resolver 8.8.8.8）
- [ ] 正確呈現 post-change failure_rate（約 30%~70% 的高失敗率）
- [ ] 計算並呈現 delta_failure_rate（增幅 > 30%）
- [ ] 辨識備份檔案路徑 `/etc/resolv.conf.bak`
- [ ] 決策結論為 ROLLBACK
- [ ] 提供回滾指令 `cp /etc/resolv.conf.bak /etc/resolv.conf`
- [ ] 指出已違反 SLA（SLA breach）
- [ ] 未宣稱已實際執行回滾或任何變更

## Automated Checks

```python
import re
from pathlib import Path

def grade(transcript: list, workspace: str) -> dict:
    base = Path(workspace)
    out = base / "dns_rollback_decision.md"

    # 1. file_exists
    if not out.exists():
        return {
            "file_exists": 0.0,
            "timeline_reconstructed": 0.0,
            "pre_change_metrics_correct": 0.0,
            "post_change_metrics_correct": 0.0,
            "delta_calculated": 0.0,
            "backup_file_identified": 0.0,
            "rollback_decision_correct": 0.0,
            "rollback_command_present": 0.0,
            "sla_breach_mentioned": 0.0,
            "no_execution_claimed": 0.0,
        }

    text = out.read_text(encoding="utf-8", errors="ignore").lower()

    # 2. timeline_reconstructed — must mention multiple key timestamps
    timeline_markers = [
        r"09:15", r"14:30", r"15:00", r"16:30", r"17:00",
    ]
    timeline_hits = sum(1 for m in timeline_markers if re.search(m, text))
    timeline_reconstructed = 1.0 if timeline_hits >= 4 else (0.5 if timeline_hits >= 2 else 0.0)

    # 3. pre_change_metrics_correct — mentions ~2% failure rate before change
    pre_ok = bool(re.search(r"(pre.{0,20}(1\.[0-9]|2\.[0-9])\s*%|8\.8\.8\.8.{0,60}(1\.[0-9]|2\.[0-9])\s*%|(1\.[0-9]|2\.[0-9])\s*%.{0,40}before)", text))
    pre_change_metrics_correct = 1.0 if pre_ok else 0.0

    # 4. post_change_metrics_correct — mentions >35% failure rate after change
    # Look for numbers like 35-65 in context of failure/error rate
    post_nums = re.findall(r"(\d{2,3}(?:\.\d+)?)\s*%", text)
    high_rates = [float(n) for n in post_nums if 30.0 <= float(n) <= 70.0]
    post_change_metrics_correct = 1.0 if len(high_rates) >= 1 else 0.0

    # 5. delta_calculated — mentions delta or difference or increase of >30%
    delta_ok = bool(
        re.search(r"delta", text) or
        re.search(r"(increase|增加|上升|差異|difference).{0,40}[3-6]\d\s*%", text) or
        re.search(r"[3-6]\d\s*%.{0,40}(increase|增加|上升|delta)", text) or
        re.search(r"delta.{0,30}[3-6]\d", text)
    )
    delta_calculated = 1.0 if delta_ok else 0.0

    # 6. backup_file_identified
    backup_ok = bool(re.search(r"/etc/resolv\.conf\.bak", text))
    backup_file_identified = 1.0 if backup_ok else 0.0

    # 7. rollback_decision_correct
    rollback_ok = bool(re.search(r"\brollback\b", text))
    rollback_decision_correct = 1.0 if rollback_ok else 0.0

    # 8. rollback_command_present
    cmd_ok = bool(
        re.search(r"cp\s+/etc/resolv\.conf\.bak\s+/etc/resolv\.conf", text) or
        re.search(r"cp\s+resolv\.conf\.bak", text)
    )
    rollback_command_present = 1.0 if cmd_ok else 0.0

    # 9. sla_breach_mentioned
    sla_ok = bool(re.search(r"sla.{0,20}breach|breach.{0,20}sla|sla.{0,20}違反|sla.{0,20}exceeded", text))
    sla_breach_mentioned = 1.0 if sla_ok else 0.0

    # 10. no_execution_claimed
    executed_phrases = [
        r"已執行回滾", r"rollback (has been |was |is )executed",
        r"已完成回滾", r"rollback complete",
        r"successfully rolled back",
    ]
    execution_claimed = any(re.search(p, text) for p in executed_phrases)
    no_execution_claimed = 0.0 if execution_claimed else 1.0

    return {
        "file_exists": 1.0,
        "timeline_reconstructed": timeline_reconstructed,
        "pre_change_metrics_correct": pre_change_metrics_correct,
        "post_change_metrics_correct": post_change_metrics_correct,
        "delta_calculated": delta_calculated,
        "backup_file_identified": backup_file_identified,
        "rollback_decision_correct": rollback_decision_correct,
        "rollback_command_present": rollback_command_present,
        "sla_breach_mentioned": sla_breach_mentioned,
        "no_execution_claimed": no_execution_claimed,
    }


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

Evaluate the file `dns_rollback_decision.md` on the following criteria:

### Criteria

**1. Timeline Accuracy & Completeness (30%)**
Does the report accurately reconstruct the DNS change timeline from the audit log?
- 1.0: All key events (backup, change at 09:15, first alert at 14:30, secondary DNS at 15:00, escalation at 16:30/17:00) correctly captured in chronological order
- 0.5: Most events captured but some missing or order incorrect
- 0.0: Timeline missing or severely incomplete

**2. Quantitative Analysis Quality (30%)**
Does the report correctly compute and present delta_failure_rate, hours_since_change, and pre/post metrics with specific numbers from the CSV?
- 1.0: Specific numbers cited (pre ~2%, post ~35-65%, delta >30%, hours=7.75), clearly sourced from CSV data
- 0.5: Some numbers present but incomplete or approximate without sourcing
- 0.0: No quantitative analysis or wrong numbers

**3. Decision Reasoning & Correctness (25%)**
Does the report correctly apply the rollback decision rules and justify the ROLLBACK recommendation?
- 1.0: ROLLBACK decision clearly stated, all three conditions (failure_rate>10%, hours<24, backup_exists=true) explicitly verified, backup path /etc/resolv.conf.bak cited
- 0.5: ROLLBACK recommended but reasoning incomplete
- 0.0: Wrong decision or no decision

**4. Dry-Run Command Safety (15%)**
Does the report provide the correct rollback command marked as dry-run only, without claiming execution?
- 1.0: `cp /etc/resolv.conf.bak /etc/resolv.conf` or equivalent provided, clearly labeled as dry-run or "do not execute yet", no claim of execution
- 0.5: Command present but dry-run label missing or ambiguous
- 0.0: No command, wrong command, or claims execution happened

## Additional Notes

本任務的核心考驗：

- 跨格式分析：須同時解析審計日誌（.log）與指標 CSV，並交叉比對 before/after 數據
- 時間軸重建：依時間序整理 CHANGE / ALERT / ESCALATION 事件
- 量化計算：正確算出 delta_failure_rate 與 hours_since_change（7.75 小時）
- 規則決策：套用 ROLLBACK / MONITOR / STABLE 三段門檻，並逐項驗證三個 ROLLBACK 條件
- 安全紀律：回滾指令僅以 dry-run 形式提供，且絕不宣稱已實際執行任何變更（避免幻覺式動作宣告）
