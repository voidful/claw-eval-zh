---
id: task_email_triage
name: 電子郵件收件匣分類
category: productivity
grading_type: hybrid
timeout_seconds: 240
language: zh
locale: zh-TW
source_task_id: task_email_triage
source_benchmark: pinchbench
claw_eval_id: P006zh_email_triage
workspace_files:
- path: inbox/email_01.txt
  content: |
    From: cto@mycompany.com (David Park, CTO)
    To: me@mycompany.com
    Date: Mon, 17 Feb 2026 08:02:00 -0500
    Subject: URGENT: Production database outage - all hands needed

    Our primary production database cluster went down at 7:45am EST. Customer-facing
    services are returning 500 errors. SRE team is engaged but we need all backend
    engineers on the war room bridge call immediately.

    War room link: https://meet.mycompany.com/war-room-prod
    Incident channel: #incident-db-20260217

    This is a P0 incident. Drop everything else until this is resolved.

    -David
- path: inbox/email_02.txt
  content: |
    From: sarah.marketing@mycompany.com (Sarah Liu, Marketing Director)
    To: me@mycompany.com
    Date: Mon, 17 Feb 2026 09:15:00 -0500
    Subject: Blog post review needed by EOD Wednesday

    Hi,

    We have a new blog post about our Q4 product updates that needs a technical
    accuracy review. It's about 1,200 words. Could you take a look and flag anything
    that's incorrect or misleading? No rush - end of day Wednesday works.

    Draft link: https://docs.mycompany.com/blog-q4-review

    Thanks!
    Sarah
- path: inbox/email_03.txt
  content: |
    From: noreply@github.com
    To: me@mycompany.com
    Date: Mon, 17 Feb 2026 07:30:00 -0500
    Subject: [mycompany/api-gateway] Pull request #482: Dependency updates (Dependabot)

    Dependabot has opened a pull request to update the following dependencies:

    - express: 4.18.2 → 4.19.0 (minor)
    - lodash: 4.17.21 → 4.17.22 (patch)
    - @types/node: 20.10.0 → 20.11.0 (minor)

    All CI checks are passing. No breaking changes detected.

    View pull request: https://github.com/mycompany/api-gateway/pull/482
- path: inbox/email_04.txt
  content: |
    From: jenna.hr@mycompany.com (Jenna Walsh, HR)
    To: all-staff@mycompany.com
    Date: Fri, 14 Feb 2026 16:00:00 -0500
    Subject: Reminder: Benefits enrollment deadline is Feb 28

    Hi everyone,

    Just a friendly reminder that the annual benefits enrollment window closes on
    February 28, 2026. If you haven't reviewed your selections, please log into
    the HR portal and make any changes before the deadline.

    Key items:
    - Health insurance plan selection
    - 401(k) contribution changes
    - FSA/HSA elections
    - Life insurance beneficiary updates

    Portal link: https://hr.mycompany.com/benefits

    If you have questions, reach out to the HR team.

    Thanks,
    Jenna
- path: inbox/email_05.txt
  content: |
    From: mike.chen@bigclient.com (Mike Chen, VP Engineering)
    To: me@mycompany.com
    Date: Mon, 17 Feb 2026 08:45:00 -0500
    Subject: Re: API integration timeline

    Hi,

    Following up on our call last week. Our board approved the integration project
    and we'd like to move forward. We need to finalize the API contract and get
    staging credentials set up ASAP so our team can start development.

    Can we schedule a 30-minute call this week? Tuesday or Thursday afternoon works
    best for us. This is a $2M annual contract so we want to keep momentum.

    Also, our security team will need to complete a vendor assessment. Could you
    send over your SOC 2 report and data processing agreement?

    Best,
    Mike Chen
    VP Engineering, BigClient Inc.
- path: inbox/email_06.txt
  content: |
    From: noreply@linkedin.com
    To: me@mycompany.com
    Date: Sun, 16 Feb 2026 14:22:00 -0500
    Subject: You have 3 new connection requests

    You have new connection requests from:
    - Alex Turner, Software Engineer at TechCorp
    - Maria Santos, Product Manager at StartupXYZ
    - Kevin Park, Recruiter at TopTalent Agency

    View and respond to your invitations:
    https://linkedin.com/notifications
- path: inbox/email_07.txt
  content: |
    From: team-lead@mycompany.com (Rachel Green, Engineering Manager)
    To: me@mycompany.com
    Date: Mon, 17 Feb 2026 09:30:00 -0500
    Subject: Performance review self-assessment due Friday

    Hi,

    Quick reminder that your annual performance review self-assessment is due this
    Friday, Feb 21. Please fill out the form I shared last week covering:

    1. Key accomplishments from the past year
    2. Areas for growth
    3. Goals for the next review period
    4. Any feedback on team processes

    Form link: https://hr.mycompany.com/perf-review/2026

    Let me know if you have any questions. I'll be scheduling our 1:1 review
    meeting for the following week.

    Rachel
- path: inbox/email_08.txt
  content: |
    From: security@mycompany.com (Security Team)
    To: engineering@mycompany.com
    Date: Mon, 17 Feb 2026 07:00:00 -0500
    Subject: IMPORTANT: Mandatory password rotation by Feb 19

    As part of our quarterly security compliance, all engineering team members
    must rotate their passwords and SSH keys by Wednesday, February 19, 2026.

    Required actions:
    1. Change your SSO password via https://sso.mycompany.com/reset
    2. Rotate your SSH keys on all company repositories
    3. Update any personal access tokens older than 90 days
    4. Confirm completion by replying to this email

    Failure to comply by the deadline may result in temporary account lockout.

    Security Team
- path: inbox/email_09.txt
  content: |
    From: newsletter@techdigest.io
    To: me@mycompany.com
    Date: Mon, 17 Feb 2026 06:00:00 -0500
    Subject: TechDigest Weekly: AI agents are reshaping software development

    This week in tech:

    → AI coding agents now write 40% of code at top tech companies
    → New study shows remote engineers are 15% more productive
    → Rust adoption surges in cloud-native development
    → OpenAI announces GPT-5 release date
    → Kubernetes 1.32 brings major networking improvements

    Read the full digest: https://techdigest.io/weekly/2026-02-17

    Unsubscribe: https://techdigest.io/unsubscribe
- path: inbox/email_10.txt
  content: |
    From: alice.wong@mycompany.com (Alice Wong, Senior Engineer)
    To: me@mycompany.com
    Date: Mon, 17 Feb 2026 09:50:00 -0500
    Subject: Code review request - auth service refactor

    Hey,

    I just pushed a pretty significant refactor of the auth service to handle
    the new OAuth2 PKCE flow. It's about 800 lines changed across 12 files.
    I'd really appreciate your review since you wrote the original auth module.

    PR link: https://github.com/mycompany/auth-service/pull/156

    The key changes:
    - Replaced implicit flow with PKCE
    - Added token rotation logic
    - New middleware for session validation
    - Updated all integration tests

    I'd like to merge by Thursday if possible since it blocks the mobile app release.
    Let me know if you need more context on any of the changes.

    Thanks,
    Alice
- path: inbox/email_11.txt
  content: |
    From: deals@saastools.com
    To: me@mycompany.com
    Date: Sat, 15 Feb 2026 10:00:00 -0500
    Subject: 🔥 Flash Sale: 60% off all annual plans - 48 hours only!

    LIMITED TIME OFFER!

    Upgrade your development workflow with SaaSTools Pro:
    ✅ Advanced CI/CD pipelines
    ✅ Real-time monitoring
    ✅ Unlimited team members

    Regular price: $299/year
    FLASH SALE: $119/year

    Use code FLASH60 at checkout.

    This offer expires Monday at midnight!

    Shop now: https://saastools.com/pricing
- path: inbox/email_12.txt
  content: |
    From: cfo@mycompany.com (Linda Zhao, CFO)
    To: engineering-leads@mycompany.com
    Date: Mon, 17 Feb 2026 08:30:00 -0500
    Subject: Q1 budget reconciliation - action needed by Thursday

    Hi team leads,

    Finance is closing out Q1 budget projections and we need each team to review
    and confirm their spending against allocated budgets. Specifically:

    1. Verify cloud infrastructure costs (AWS/GCP) for Jan-Feb
    2. Flag any anticipated overruns for March
    3. Submit any pending purchase requests before the March 1 cutoff

    Please fill out the budget tracker: https://docs.mycompany.com/q1-budget

    Need responses by end of day Thursday, Feb 20. If your team is trending
    over budget, let's schedule a quick sync to discuss.

    Thanks,
    Linda
- path: inbox/email_13.txt
  content: |-
    From: automated-alerts@monitoring.mycompany.com
    To: oncall@mycompany.com, me@mycompany.com
    Date: Mon, 17 Feb 2026 07:48:00 -0500
    Subject: [ALERT] API latency exceeding threshold - p99 > 2000ms

    MONITORING ALERT

    Service: api-gateway
    Metric: p99 latency
    Current value: 3,247ms (threshold: 2,000ms)
    Duration: 3 minutes
    Status: FIRING

    Affected endpoints:
    - POST /api/v1/transactions (p99: 4,102ms)
    - GET /api/v1/accounts (p99: 2,891ms)
    - POST /api/v1/auth/token (p99: 3,415ms)

    Dashboard: https://grafana.mycompany.com/d/api-latency
    Runbook: https://wiki.mycompany.com/runbooks/api-latency

    This alert correlates with the ongoing database incident (INC-20260217-001).
grading_weights:
  automated: 0.4
  llm_judge: 0.6
---

# 電子郵件收件匣分類

## Prompt

你正在協助分類整理一個爆滿的電子郵件收件匣。這些郵件已放在你工作區的 `inbox/`
資料夾中（檔名為 `email_01.txt` 至 `email_13.txt`）。請讀取全部 13 封郵件，
並建立一份分類報告，儲存到 `triage_report.md`。針對每一封郵件，請指派：

1. **優先順序（Priority）**：P0（放下一切、立即處理）、P1（今天）、
   P2（本週）、P3（有空再處理）、P4（無需行動／歸檔）
2. **分類（Category）**：擇一指派為下列其中之一——"incident"、"client"、
   "internal-request"、"administrative"、"code-review"、"automated"、
   "newsletter"、"spam"
3. **建議行動（Recommended action）**：一段簡短（1 至 2 句）說明該如何處理

請依優先順序整理報告（最緊急者排在最前）。並在最上方加入一段簡短的摘要區段，
凸顯最關鍵的項目，並為當天提出一份行動計畫。

## Expected Behavior

助手應該：

1. 探索並讀取 `inbox/` 目錄中全部 13 個郵件檔案
2. 針對每封郵件分析其急迫性、寄件者重要性、期限與內容
3. 指派適當的優先順序，並考量下列原則：
   - 線上服務事故（production incident）為 P0
   - 高價值客戶往來郵件為 P1
   - 資安合規期限為 P1 至 P2
   - 有期限的同事程式碼審查為 P2
   - 有期限的行政事務為 P2
   - 電子報與社群通知為 P3 至 P4
   - 垃圾／促銷郵件為 P4
4. 為每封郵件正確分類
5. 為每封郵件提供可執行、具體的建議
6. 製作一份結構化、易於快速瀏覽、且依優先順序排序的報告
7. 在最上方加入一段總結，並附上建議的當日行動計畫
8. 將報告儲存到 `triage_report.md`

這項任務測試助手是否能夠：

- 處理一批異質的輸入
- 運用判斷力來分類並排定資訊的優先順序
- 辨識情境線索（例如監控警報與資料庫服務中斷有關）
- 區分緊急、重要與低價值項目
- 產出結構化、可執行的輸出

## Grading Criteria

- [ ] 助手探索並讀取了 inbox/ 中全部 13 封郵件
- [ ] 已建立檔案 `triage_report.md`
- [ ] 報告中包含全部 13 封郵件
- [ ] 每封郵件都已指派優先順序（P0-P4）
- [ ] 每封郵件都已指派分類
- [ ] 每封郵件都附有建議行動
- [ ] 線上服務中斷郵件（01）被歸類為 P0
- [ ] 監控警報（13）與服務中斷事件相連結或歸為一組
- [ ] 客戶郵件（05）被歸類為高優先（P0 或 P1）
- [ ] 垃圾／促銷郵件（11）被歸類為 P4
- [ ] 報告依優先順序排序（最緊急者在最前）
- [ ] 報告最上方有摘要區段

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the email triage task based on structural correctness and key priority assignments.

    Args:
        transcript: Parsed JSONL transcript as list of dicts
        workspace_path: Path to the task's isolated workspace directory

    Returns:
        Dict mapping criterion names to scores (0.0 to 1.0)
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check if triage_report.md exists
    report_file = workspace / "triage_report.md"

    if not report_file.exists():
        return {
            "file_created": 0.0,
            "all_emails_covered": 0.0,
            "priorities_assigned": 0.0,
            "categories_assigned": 0.0,
            "actions_assigned": 0.0,
            "outage_is_p0": 0.0,
            "alert_linked_to_outage": 0.0,
            "client_is_high_priority": 0.0,
            "spam_is_low_priority": 0.0,
            "sorted_by_priority": 0.0,
            "has_summary_section": 0.0,
        }

    scores["file_created"] = 1.0
    content = report_file.read_text()
    content_lower = content.lower()

    # Check all 13 emails are covered.
    # Look for references to email subjects or senders as indicators.
    email_indicators = [
        r"(production database outage|war room|p0 incident|david park)",
        r"(blog post review|sarah.?liu|marketing|q4 product)",
        r"(dependabot|pull request #?482|dependency update)",
        r"(benefits enrollment|jenna walsh|feb(ruary)?\s*28)",
        r"(bigclient|mike chen|\$2m|api integration timeline)",
        r"(linkedin|connection request)",
        r"(performance review|self.?assessment|rachel green)",
        r"(password rotation|ssh key|security compliance|feb(ruary)?\s*19)",
        r"(techdigest|newsletter|weekly.*ai agent)",
        r"(auth service refactor|alice wong|oauth2?\s*pkce|pr.*#?156)",
        r"(flash sale|saastools|60%\s*off|spam)",
        r"(budget reconciliation|linda zhao|cfo|q1 budget)",
        r"(api latency|monitoring alert|\[alert\]|p99.*2000)",
    ]

    found_emails = 0
    for pattern in email_indicators:
        if re.search(pattern, content_lower):
            found_emails += 1

    scores["all_emails_covered"] = found_emails / 13.0

    # Check priorities are assigned (look for P0-P4 labels)
    priority_matches = re.findall(r'\bP[0-4]\b', content, re.IGNORECASE)
    if len(priority_matches) >= 13:
        scores["priorities_assigned"] = 1.0
    elif len(priority_matches) >= 10:
        scores["priorities_assigned"] = 0.75
    elif len(priority_matches) >= 6:
        scores["priorities_assigned"] = 0.5
    elif len(priority_matches) >= 1:
        scores["priorities_assigned"] = 0.25
    else:
        scores["priorities_assigned"] = 0.0

    # Check categories are assigned
    category_keywords = [
        "incident", "client", "internal", "administrative", "admin",
        "code.?review", "automated", "newsletter", "spam", "promotional",
    ]
    categories_found = sum(
        1 for kw in category_keywords
        if re.search(kw, content_lower)
    )
    if categories_found >= 6:
        scores["categories_assigned"] = 1.0
    elif categories_found >= 4:
        scores["categories_assigned"] = 0.75
    elif categories_found >= 2:
        scores["categories_assigned"] = 0.5
    else:
        scores["categories_assigned"] = 0.0

    # Check recommended actions exist (look for action-oriented language near each email)
    action_patterns = [
        r"(action|respond|reply|review|schedule|join|ignore|archive|complete|submit|fill|approve|merge|delete|unsubscribe|forward|delegate|attend|read|dismiss)",
    ]
    action_count = len(re.findall(action_patterns[0], content_lower))
    if action_count >= 13:
        scores["actions_assigned"] = 1.0
    elif action_count >= 8:
        scores["actions_assigned"] = 0.75
    elif action_count >= 4:
        scores["actions_assigned"] = 0.5
    else:
        scores["actions_assigned"] = 0.25

    # Check production outage (email 01) is P0
    # Look for P0 near the outage-related content
    outage_section = ""
    # Try to find the section about the outage
    outage_matches = list(re.finditer(
        r'(production database outage|david park|war room|cto)',
        content_lower
    ))
    if outage_matches:
        # Get surrounding context (500 chars around first match)
        start = max(0, outage_matches[0].start() - 200)
        end = min(len(content_lower), outage_matches[0].end() + 300)
        outage_section = content_lower[start:end]

    if re.search(r'\bp0\b', outage_section, re.IGNORECASE):
        scores["outage_is_p0"] = 1.0
    elif re.search(r'\bp1\b', outage_section, re.IGNORECASE):
        scores["outage_is_p0"] = 0.5
    else:
        scores["outage_is_p0"] = 0.0

    # Check monitoring alert (email 13) is linked to the outage
    alert_section = ""
    alert_matches = list(re.finditer(
        r'(api latency|monitoring alert|\balert\b.*threshold|p99)',
        content_lower
    ))
    if alert_matches:
        start = max(0, alert_matches[0].start() - 200)
        end = min(len(content_lower), alert_matches[0].end() + 500)
        alert_section = content_lower[start:end]

    if re.search(r'(relat|correlat|connect|linked|same.*incident|outage|database|incident)', alert_section):
        scores["alert_linked_to_outage"] = 1.0
    elif re.search(r'\bp0\b', alert_section, re.IGNORECASE):
        scores["alert_linked_to_outage"] = 0.75
    else:
        scores["alert_linked_to_outage"] = 0.0

    # Check client email (email 05, BigClient) is high priority
    client_section = ""
    client_matches = list(re.finditer(
        r'(bigclient|mike chen|\$2m|api integration)',
        content_lower
    ))
    if client_matches:
        start = max(0, client_matches[0].start() - 200)
        end = min(len(content_lower), client_matches[0].end() + 300)
        client_section = content_lower[start:end]

    if re.search(r'\bp[01]\b', client_section, re.IGNORECASE):
        scores["client_is_high_priority"] = 1.0
    elif re.search(r'\bp2\b', client_section, re.IGNORECASE):
        scores["client_is_high_priority"] = 0.5
    else:
        scores["client_is_high_priority"] = 0.0

    # Check spam/promotional email (email 11) is P4
    spam_section = ""
    spam_matches = list(re.finditer(
        r'(flash sale|saastools|60%.*off)',
        content_lower
    ))
    if spam_matches:
        start = max(0, spam_matches[0].start() - 200)
        end = min(len(content_lower), spam_matches[0].end() + 300)
        spam_section = content_lower[start:end]

    if re.search(r'\bp4\b', spam_section, re.IGNORECASE):
        scores["spam_is_low_priority"] = 1.0
    elif re.search(r'\bp3\b', spam_section, re.IGNORECASE):
        scores["spam_is_low_priority"] = 0.75
    else:
        scores["spam_is_low_priority"] = 0.0

    # Check report is sorted by priority (P0 items should appear before P4 items)
    p0_positions = [m.start() for m in re.finditer(r'\bP0\b', content, re.IGNORECASE)]
    p4_positions = [m.start() for m in re.finditer(r'\bP4\b', content, re.IGNORECASE)]

    if p0_positions and p4_positions:
        if max(p0_positions) < min(p4_positions):
            scores["sorted_by_priority"] = 1.0
        elif min(p0_positions) < min(p4_positions):
            scores["sorted_by_priority"] = 0.5
        else:
            scores["sorted_by_priority"] = 0.0
    elif p0_positions or p4_positions:
        scores["sorted_by_priority"] = 0.25
    else:
        scores["sorted_by_priority"] = 0.0

    # Check for summary section at top
    # Summary should appear in the first 20% of the document
    first_chunk = content_lower[:max(len(content_lower) // 5, 200)]
    if re.search(r'(summary|overview|highlights|critical items|day plan|top priorities)', first_chunk):
        scores["has_summary_section"] = 1.0
    elif re.search(r'(summary|overview|highlights)', content_lower):
        scores["has_summary_section"] = 0.5
    else:
        scores["has_summary_section"] = 0.0

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

### 評分項 1：優先順序指派準確度（權重 30%）

**1.0 分**：所有優先順序皆正確指派。線上服務中斷（郵件 01）與相關連的監控警報
（郵件 13）為 P0。BigClient 後續追蹤（郵件 05）為 P0 或 P1。資安密碼更換
（郵件 08）因有 2 天期限，為 P1 或 P2。Auth service 程式碼審查（郵件 10）因
會阻擋發布，為 P2。預算對帳（郵件 12）為 P2。績效考核（郵件 07）與部落格審查
（郵件 02）為 P2 至 P3。福利提醒（郵件 04）為 P2 至 P3。Dependabot PR
（郵件 03）為 P3。LinkedIn（郵件 06）、電子報（郵件 09）與促銷垃圾郵件
（郵件 11）為 P3 至 P4。無重大排序錯誤。

**0.75 分**：多數優先順序合理，僅有 1 至 2 處輕微排序失準（例如程式碼審查評得
太低或太高）。所有關鍵項目（服務中斷、客戶、資安）皆正確辨識為高優先。

**0.5 分**：有數處優先順序指派值得商榷。可能未察覺客戶郵件或資安期限的急迫性。
明顯的項目能答對（服務中斷＝P0、垃圾郵件＝P4），但在中間優先級上力有未逮。

**0.25 分**：排序明顯失準。可能未能辨識線上服務中斷為最高優先，或把低價值項目
排得太高。優先順序的安排顯得隨意。

**0.0 分**：未指派優先順序，或優先順序完全錯誤（例如把垃圾郵件排得比線上服務
事故還高）。

### 評分項 2：分類品質（權重 15%）

**1.0 分**：所有郵件分類正確。能辨識：incident（郵件 01、13）、client
（郵件 05）、internal-request（郵件 02、07、08、10、12）、automated
（郵件 03）、newsletter（郵件 09）、spam（郵件 11）、administrative
（郵件 04、07）。分類一致且具意義。

**0.75 分**：多數分類正確，僅有 1 至 2 處輕微誤分類。分類取自合理的分類體系。

**0.5 分**：部分分類正確，但有數封郵件被誤分類。可能使用不一致或過於籠統的分類。

**0.25 分**：分類不佳。許多郵件被誤分類，或分類缺乏意義。

**0.0 分**：未指派分類，或完全錯誤。

### 評分項 3：行動建議（權重 25%）

**1.0 分**：建議具體、可執行且得宜。例如：對服務中斷建議「立即加入 war room
通話」；對客戶郵件建議「回覆 Mike Chen 提議週二／週四的時段、把客戶經理拉進
來、備妥 SOC 2 文件」；對垃圾郵件建議「歸檔／刪除」；對程式碼審查建議「在週三前
審查 PR #156，重點放在 PKCE flow 的變更」。建議顯示出對情境的理解（例如警報與
服務中斷相關連、程式碼審查會阻擋行動版發布）。

**0.75 分**：多數建議良好且可執行。僅有少量瑕疵，例如 1 至 2 項過於含糊，或漏掉
情境上的關聯。

**0.5 分**：有提出建議，但偏向通用（「回覆這封郵件」）而非具體。漏掉關鍵情境，
例如 2M 美元合約價值，或程式碼審查會阻擋發布的特性。

**0.25 分**：建議過於含糊而無實用價值，或對數封郵件的建議並不得宜。

**0.0 分**：未提供建議，或完全無用。

### 評分項 4：情境意識與關聯（權重 15%）

**1.0 分**：展現強大的情境推理能力。明確將監控警報（郵件 13）與線上服務中斷
（郵件 01）相連結。辨識出 BigClient 關係的 2M 美元價值。指出 auth 程式碼審查
會阻擋行動版發布。理解資安期限只剩 2 天。亦可能指出服務中斷可能影響 BigClient
的關係。

**0.75 分**：做出多數關鍵關聯。將警報連結到服務中斷。辨識多數具時效性的項目及其
影響。

**0.5 分**：做出 1 至 2 項關聯，但漏掉其他。多半孤立看待每封郵件，未看出彼此關係。

**0.25 分**：情境意識極少。各封郵件獨立處理，毫無交叉參照。

**0.0 分**：未做出任何情境關聯。

### 評分項 5：報告結構與可用性（權重 15%）

**1.0 分**：報告結構良好且可立即據以行動。最上方有清楚的摘要／當日計畫。郵件依
優先順序組織。格式一致（標題、條列、表格）。易於快速瀏覽。忙碌的人掃一眼就知道
該先做什麼。

**0.75 分**：結構良好，僅有少量格式問題。有摘要。大致易於瀏覽。

**0.5 分**：具備基本結構，但組織仍可改善。可能缺少摘要或格式不一致。要擷取關鍵
資訊較費力。

**0.25 分**：結構不佳，難以瀏覽。沒有清楚的組織或摘要。

**0.0 分**：輸出毫無結構或無法理解。
