---
id: task_web_search_market_research
name: 網路搜尋：臺灣行動支付市場競爭格局研究
category: web_search_analysis
grading_type: hybrid
timeout_seconds: 600
grading_weights:
  automated: 0.5
  llm_judge: 0.5
workspace_files: []
language: zh
locale: zh-TW
region: TW
localization: taiwan
localization_strategy: native
source_benchmark: benchmark_v2
---
## Prompt

使用網路搜尋工具（web search skill）研究「2024 年臺灣行動支付市場競爭格局」，輸出 `mobile_payment_market_report.md`。**所有數據都必須標注來源 URL 和日期**。

本任務無預置檔案，所有資料皆透過網路搜尋取得。

研究範圍：

1. **市場規模**：2024 年臺灣電子支付／行動支付總交易額（搜尋金管會或財政部統計數據）
2. **主要競爭者市佔**：LINE Pay、街口支付（JKOPAY）、Apple Pay、Google Pay、台灣 Pay（全支付／一卡通）的用戶數或市佔率
3. **2024 年重大事件**：各服務商在 2024 年的重要動態（新功能、合作案、政策調整）
4. **競爭格局矩陣**：依「用戶規模」和「功能廣度」建立 2×2 矩陣
5. **趨勢分析**：BNPL（先買後付）、加密貨幣支付在臺灣的進展

**特別要求**：

- 每個數據點**必須**有 `[來源: URL]` 或 `[Source: URL]` 格式的引用
- 搜尋時使用多個查詢詞（如「臺灣行動支付市佔率 2024」「LINE Pay 用戶數 2024」等）
- 若搜尋結果相互矛盾，需標注並說明差異

### 輸出格式

輸出檔案：`mobile_payment_market_report.md`

結構如下：

```markdown
# 2024 年臺灣行動支付市場競爭格局研究報告
### 一、市場規模
### 二、主要競爭者分析
### 三、2024 年重大事件
### 四、競爭格局矩陣（2×2）
### 五、趨勢分析：BNPL 與加密貨幣支付
### 六、總結與展望
### 參考來源
```

---

## Expected Behavior

代理人應執行以下步驟：

1. 使用網路搜尋工具發出多組查詢（繁體中文與英文關鍵詞組合），蒐集臺灣行動支付市場資料
2. 搜尋金管會／財政部統計，找出 2024 年電子支付／行動支付總交易額（億／兆等大數量級）
3. 蒐集各主要競爭者（LINE Pay、街口／JKOPAY、Apple Pay、Google Pay、台灣 Pay、全支付、一卡通等）的用戶數或市佔率
4. 整理 2024 年各服務商重大動態（新功能、合作案、政策調整）
5. 依「用戶規模」與「功能廣度」建立 2×2 競爭格局矩陣並說明各象限定位
6. 評估 BNPL（先買後付）與加密貨幣支付在臺灣的進展趨勢
7. 為每個數據點標注 `[來源: URL]` 與日期；若來源相互矛盾，明確標注並說明差異
8. 依規定結構輸出完整的 `mobile_payment_market_report.md`

關鍵預期值（近似）：

- 報告中至少出現 4 個不同的支付服務名稱
- 至少 2 個 http/https 來源 URL
- 含 2024 年份引用、市場規模大數字、2×2 矩陣與趨勢分析段落

---

## Grading Criteria

- [ ] 輸出檔案 `mobile_payment_market_report.md` 存在
- [ ] 報告含市場規模大數字（億／兆／百萬等量級或交易額數值）
- [ ] 提到 LINE Pay
- [ ] 提到街口／JKOPAY
- [ ] 提到 Apple Pay 或 Google Pay
- [ ] 至少 2 個來源 URL（http/https）
- [ ] 含 2024 年份引用
- [ ] 含競爭格局矩陣（矩陣／象限／matrix／2×2 等）
- [ ] 含趨勢分析（趨勢／BNPL／先買後付等）
- [ ] 至少提及 4 個不同的支付服務名稱

---

## Automated Checks

```python
import re
from pathlib import Path

def grade(transcript: list, submission_dir: str) -> dict:
    report_path = Path(submission_dir) / "mobile_payment_market_report.md"
    if not report_path.exists():
        return {"score": 0, "max_score": 10, "details": "未找到 mobile_payment_market_report.md", "passed": False}

    text = report_path.read_text(encoding="utf-8")
    checks = {}

    # 1. report_created
    checks["report_created"] = True

    # 2. market_size_number: 有交易額或金額的大數字（億、兆、百萬以上）
    checks["market_size_number"] = bool(
        re.search(r"\d+[\.,]?\d*\s*(億|兆|trillion|billion|million|百萬|千億)", text, re.IGNORECASE) or
        re.search(r"(交易額|transaction).{0,60}\d{4,}", text, re.IGNORECASE) or
        re.search(r"\d{4,}\s*(億|兆|萬)", text)
    )

    # 3. line_pay_mentioned: LINE Pay 出現
    checks["line_pay_mentioned"] = bool(re.search(r"LINE\s*Pay", text, re.IGNORECASE))

    # 4. jkopay_mentioned: 街口 或 JKOPAY 出現
    checks["jkopay_mentioned"] = bool(re.search(r"(街口|JKOPAY|JKO)", text, re.IGNORECASE))

    # 5. apple_google_pay: Apple Pay 或 Google Pay 出現
    checks["apple_google_pay"] = bool(
        re.search(r"Apple\s*Pay", text, re.IGNORECASE) or
        re.search(r"Google\s*Pay", text, re.IGNORECASE)
    )

    # 6. source_urls: 有 http 或 https URL >= 2 個
    urls = re.findall(r"https?://[^\s\)\]\"']+", text)
    checks["source_urls"] = len(urls) >= 2

    # 7. date_cited: 有年份引用 2024
    checks["date_cited"] = bool(re.search(r"2024", text))

    # 8. competition_matrix: 有矩陣或象限相關詞
    checks["competition_matrix"] = bool(
        re.search(r"(矩陣|象限|matrix|quadrant|2×2|2x2)", text, re.IGNORECASE)
    )

    # 9. trend_analysis: 有趨勢或 BNPL 相關詞
    checks["trend_analysis"] = bool(
        re.search(r"(趨勢|trend|BNPL|先買後付|buy now pay later)", text, re.IGNORECASE)
    )

    # 10. multiple_competitors: 有 >= 4 個不同支付服務名稱
    payment_services = [
        r"LINE\s*Pay",
        r"街口|JKOPAY|JKO",
        r"Apple\s*Pay",
        r"Google\s*Pay",
        r"台灣\s*Pay|TaiwanPay",
        r"全支付",
        r"一卡通|iPass",
        r"Pi\s*錢包|PiPay",
        r"悠遊付|EasyPay",
        r"Samsung\s*Pay",
        r"支付寶|Alipay",
        r"WeChat\s*Pay|微信支付",
    ]
    found_services = sum(
        1 for pattern in payment_services
        if re.search(pattern, text, re.IGNORECASE)
    )
    checks["multiple_competitors"] = found_services >= 4

    passed_count = sum(1 for v in checks.values() if v)
    score = passed_count

    details_lines = []
    for key, val in checks.items():
        icon = "✅" if val else "❌"
        details_lines.append(f"{icon} {key}")

    if checks["source_urls"]:
        details_lines.append(f"   → found {len(urls)} URLs")
    if checks["multiple_competitors"]:
        details_lines.append(f"   → found {found_services} payment service(s) mentioned")

    return {
        "score": score,
        "max_score": 10,
        "passed": passed_count >= 7,
        "checks": checks,
        "details": "\n".join(details_lines),
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

---

## LLM Judge Rubric

| 維度 | 權重 | 評分說明 |
|------|------|----------|
| **Source Quality & Citation** | 30% | 是否引用了可信來源（新聞媒體、官方機構、研究報告）並正確標注 URL 與日期；來源是否多元（≥3 個不同網域） |
| **Data Accuracy** | 25% | 市場數據是否真實合理（數量級是否符合已知事實；如有矛盾數據是否說明差異） |
| **Coverage Completeness** | 25% | 是否涵蓋了主要競爭者（LINE Pay、街口、Apple/Google Pay、台灣 Pay）和 2024 年關鍵市場動態 |
| **Analysis Depth** | 20% | 是否超越數字呈現，提供競爭格局洞察（如 2×2 矩陣定位說明、BNPL 趨勢評估） |

> LLM Judge 總權重加總：30 + 25 + 25 + 20 = 100%

---

## Additional Notes

核心考驗：

- **網路搜尋工具整合**：需發出多個有效查詢（繁體中文與英文關鍵詞組合）
- **來源引用規範**：每個數據點均需標注 URL，不能使用未標注來源的數字
- **矛盾數據處理**：不同來源數據相互矛盾時需明確標注並說明
- **結構化輸出**：從散落的搜尋結果組合出完整市場報告（含 2×2 矩陣）
- **趨勢辨識**：需搜尋並評估 BNPL 及加密貨幣支付的臺灣在地進展
