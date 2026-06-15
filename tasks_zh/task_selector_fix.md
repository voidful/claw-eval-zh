---
id: task_selector_fix
name: 測試維護／選擇器修正
category: coding
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
source_task_id: task_selector_fix
source_benchmark: pinchbench
claw_eval_id: P036zh_selector_fix
workspace_files:
- source: dashboard_component.html
  dest: dashboard_component.html
- source: dashboard_tests.py
  dest: dashboard_tests.py
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

# 測試維護／選擇器修正

## Prompt

工作區中的 `dashboard_tests.py` 包含一個 Team Dashboard UI 元件
（`dashboard_component.html`）的 Playwright 端對端測試。在最近一次 UI 重構之後，
HTML 中所有的 class 名稱與結構性選擇器都改變了，但測試檔案卻從未更新。

目前每一個測試都使用**舊選擇器**，這些選擇器已不再與實際的標記（markup）相符。
你的工作是更新 `dashboard_tests.py` 中**所有**的選擇器，使其與
`dashboard_component.html` 中的實際元素相符。

規則：

1. 閱讀 `dashboard_component.html`，了解新的 DOM 結構與 class 名稱
2. 更新 `dashboard_tests.py` 中每一個失效的選擇器，使其符合新的標記
3. **請勿**更動測試邏輯、關於內容／數量的斷言，或測試結構——只修正選擇器
4. **請勿**修改 `dashboard_component.html`
5. 將更新後的測試檔案就地儲存為 `dashboard_tests.py`

以下是這次重構變更內容的快速對照表：

| 舊（失效） | 新（現行） |
|---|---|
| `.sidebar` | `.sidebar-nav` |
| `.menu-items` | `.nav-items` |
| `a.active` | `a[aria-current="page"]` |
| `.top-bar` | `.header-bar` |
| `.top-bar .title` | `.header-bar .page-title` |
| `.top-bar .avatar` | `.header-bar .avatar-btn` |
| `.dropdown-menu` | `.dropdown-panel` |
| `.stats-grid` / `.stat-card` | `.metrics-grid` / `.metric-card` |
| `.stat-label` / `.stat-value` / `.stat-change.positive` | `.metric-label` / `.metric-value` / `.metric-trend.trend-up` |
| `#searchBox` | `.search-input` |
| `.members-table` | `.data-section table`（或 `.data-section`） |
| `th.sortable` | `th[data-sort]` |
| `.badge` / `.badge-active` / `.badge-idle` / `.badge-offline` | `.status-badge` / `.status-active` / `.status-idle` / `.status-offline` |
| `.edit-btn` | `[data-action="edit-member"]` |
| `.notifications` / `.toast` | `.toast-container` / `.toast-message` |
| `.pager` / `.page-btn` / `.page-btn.active` | `.pagination-bar` / `.page-controls button` / `.page-controls button.is-active` |
| `.pager .info` | `.pagination-bar .page-info` |
| `.modal-backdrop` | `.modal-overlay` |
| `.modal-content` | `.modal-dialog` |
| `.cancel-btn` | `[data-action="close-modal"]` |
| `.submit-btn` | `button[type="submit"]` |

## Expected Behavior

助手應該：

1. 閱讀 `dashboard_component.html`，了解現行的 DOM 結構、class 名稱與 data 屬性
2. 閱讀 `dashboard_tests.py`，找出每一個失效的選擇器
3. 以對照表為指引，有系統地將每個選擇器更新為符合新的標記
4. 保留所有測試邏輯、斷言的值與結構性模式——只應更動選擇器
5. 將修正後的檔案儲存為 `dashboard_tests.py`

修正後的選擇器應使用 HTML 中實際存在的 class 名稱與屬性（例如 `.sidebar-nav`、
`.nav-items`、`[aria-current="page"]`、`.metric-card`、`.status-badge.status-active`、
`[data-action="edit-member"]`、`.toast-container .toast-message`、`.modal-overlay`
等）。

## Grading Criteria

- [ ] 編輯後檔案 `dashboard_tests.py` 存在
- [ ] 檔案包含有效的 Python 語法
- [ ] Sidebar 選擇器已更新（`.sidebar-nav`、`.nav-items`、`aria-current`）
- [ ] Header 選擇器已更新（`.header-bar`、`.page-title`）
- [ ] 使用者選單選擇器已更新（`.avatar-btn`、`.dropdown-panel`）
- [ ] Metric card 選擇器已更新（`.metrics-grid`、`.metric-card`、`.metric-label`、`.metric-value`、`.metric-trend`）
- [ ] 搜尋輸入框選擇器已更新（以 `.search-input` 取代 `#searchBox`）
- [ ] 表格選擇器已更新（以 `.data-section` 取代 `.members-table`）
- [ ] 排序表頭選擇器已更新（`th[data-sort]` 或 `th[aria-sort]`）
- [ ] 狀態標章選擇器已更新（`.status-badge`、`.status-active`、`.status-idle`、`.status-offline`）
- [ ] 編輯按鈕選擇器已更新（`data-action="edit-member"`）
- [ ] Toast 選擇器已更新（`.toast-container`、`.toast-message`）
- [ ] 分頁選擇器已更新（`.pagination-bar`、`.page-controls`、`.is-active`、`.page-info`）
- [ ] Modal 選擇器已更新（`.modal-overlay`、`.modal-dialog`、`data-action="close-modal"`、`button[type="submit"]`）
- [ ] 檔案中沒有殘留任何舊選擇器

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re
    import ast

    scores = {
        "file_exists": 0.0,
        "valid_python": 0.0,
        "sidebar_selectors": 0.0,
        "header_selectors": 0.0,
        "user_menu_selectors": 0.0,
        "metric_selectors": 0.0,
        "search_selector": 0.0,
        "table_selectors": 0.0,
        "sort_header_selector": 0.0,
        "status_badge_selectors": 0.0,
        "edit_button_selector": 0.0,
        "toast_selectors": 0.0,
        "pagination_selectors": 0.0,
        "modal_selectors": 0.0,
        "no_old_selectors": 0.0,
    }

    workspace = Path(workspace_path)
    test_file = workspace / "dashboard_tests.py"

    if not test_file.exists():
        return scores
    scores["file_exists"] = 1.0

    content = test_file.read_text(encoding="utf-8")

    try:
        ast.parse(content)
        scores["valid_python"] = 1.0
    except SyntaxError:
        return scores

    # --- Sidebar selectors ---
    has_sidebar_nav = "sidebar-nav" in content
    has_nav_items = "nav-items" in content
    has_aria_current = "aria-current" in content
    if has_sidebar_nav and has_nav_items and has_aria_current:
        scores["sidebar_selectors"] = 1.0
    elif has_sidebar_nav and has_nav_items:
        scores["sidebar_selectors"] = 0.75
    elif has_sidebar_nav or has_nav_items:
        scores["sidebar_selectors"] = 0.5

    # --- Header selectors ---
    has_header_bar = "header-bar" in content
    has_page_title = "page-title" in content
    if has_header_bar and has_page_title:
        scores["header_selectors"] = 1.0
    elif has_header_bar or has_page_title:
        scores["header_selectors"] = 0.5

    # --- User menu selectors ---
    has_avatar_btn = "avatar-btn" in content
    has_dropdown_panel = "dropdown-panel" in content
    if has_avatar_btn and has_dropdown_panel:
        scores["user_menu_selectors"] = 1.0
    elif has_avatar_btn or has_dropdown_panel:
        scores["user_menu_selectors"] = 0.5

    # --- Metric card selectors ---
    has_metrics_grid = "metrics-grid" in content
    has_metric_card = "metric-card" in content
    has_metric_label = "metric-label" in content
    has_metric_value = "metric-value" in content
    has_metric_trend = "metric-trend" in content
    metric_hits = sum([has_metrics_grid, has_metric_card, has_metric_label, has_metric_value, has_metric_trend])
    if metric_hits >= 4:
        scores["metric_selectors"] = 1.0
    elif metric_hits >= 2:
        scores["metric_selectors"] = 0.5
    elif metric_hits >= 1:
        scores["metric_selectors"] = 0.25

    # --- Search input selector ---
    has_search_input = "search-input" in content
    no_search_box = "#searchBox" not in content
    if has_search_input and no_search_box:
        scores["search_selector"] = 1.0
    elif has_search_input:
        scores["search_selector"] = 0.5

    # --- Table selectors ---
    has_data_section = "data-section" in content
    no_members_table = ".members-table" not in content
    if has_data_section and no_members_table:
        scores["table_selectors"] = 1.0
    elif has_data_section:
        scores["table_selectors"] = 0.5

    # --- Sort header selector ---
    has_data_sort = "data-sort" in content or "aria-sort" in content
    no_sortable_class = "th.sortable" not in content
    if has_data_sort and no_sortable_class:
        scores["sort_header_selector"] = 1.0
    elif has_data_sort:
        scores["sort_header_selector"] = 0.5

    # --- Status badge selectors ---
    has_status_badge = "status-badge" in content
    has_status_active = "status-active" in content
    has_status_idle = "status-idle" in content
    has_status_offline = "status-offline" in content
    badge_hits = sum([has_status_badge, has_status_active, has_status_idle, has_status_offline])
    no_old_badge = ".badge-active" not in content and ".badge-idle" not in content
    if badge_hits >= 3 and no_old_badge:
        scores["status_badge_selectors"] = 1.0
    elif badge_hits >= 2:
        scores["status_badge_selectors"] = 0.5

    # --- Edit button selector ---
    has_edit_action = 'data-action="edit-member"' in content or "data-action=\\'edit-member\\'" in content or "edit-member" in content
    no_edit_btn = ".edit-btn" not in content
    if has_edit_action and no_edit_btn:
        scores["edit_button_selector"] = 1.0
    elif has_edit_action:
        scores["edit_button_selector"] = 0.5

    # --- Toast selectors ---
    has_toast_container = "toast-container" in content
    has_toast_message = "toast-message" in content
    no_old_notifications = ".notifications" not in content
    if has_toast_container and has_toast_message and no_old_notifications:
        scores["toast_selectors"] = 1.0
    elif has_toast_container or has_toast_message:
        scores["toast_selectors"] = 0.5

    # --- Pagination selectors ---
    has_pagination_bar = "pagination-bar" in content
    has_page_controls = "page-controls" in content
    has_is_active = "is-active" in content
    has_page_info = "page-info" in content
    pag_hits = sum([has_pagination_bar, has_page_controls, has_is_active, has_page_info])
    no_old_pager = ".pager" not in content and ".page-btn" not in content
    if pag_hits >= 3 and no_old_pager:
        scores["pagination_selectors"] = 1.0
    elif pag_hits >= 2:
        scores["pagination_selectors"] = 0.5

    # --- Modal selectors ---
    has_modal_overlay = "modal-overlay" in content
    has_modal_dialog = "modal-dialog" in content
    has_close_modal_action = "close-modal" in content
    has_submit_type = 'type="submit"' in content or "type=\\\"submit\\\"" in content or "btn-primary" in content
    modal_hits = sum([has_modal_overlay, has_modal_dialog, has_close_modal_action, has_submit_type])
    no_old_modal = ".modal-backdrop" not in content and ".modal-content" not in content
    if modal_hits >= 3 and no_old_modal:
        scores["modal_selectors"] = 1.0
    elif modal_hits >= 2:
        scores["modal_selectors"] = 0.5

    # --- No old selectors remain ---
    old_selectors = [
        ".sidebar ",  # with trailing space to avoid matching sidebar-nav
        ".menu-items",
        "a.active",
        ".top-bar",
        ".avatar\"",  # .avatar" without -btn
        ".dropdown-menu",
        ".stats-grid",
        ".stat-card",
        ".stat-label",
        ".stat-value",
        ".stat-change",
        "#searchBox",
        ".members-table",
        "th.sortable",
        ".badge-active",
        ".badge-idle",
        ".badge-offline",
        ".edit-btn",
        ".notifications",
        ".pager",
        ".page-btn",
        ".modal-backdrop",
        ".modal-content",
        ".cancel-btn",
        ".submit-btn",
    ]
    remaining = sum(1 for sel in old_selectors if sel in content)
    if remaining == 0:
        scores["no_old_selectors"] = 1.0
    elif remaining <= 3:
        scores["no_old_selectors"] = 0.5
    elif remaining <= 6:
        scores["no_old_selectors"] = 0.25

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

### 評分項 1：選擇器正確性與專一性（權重 40%）

**1.0 分**：更新後的測試檔案中，每一個選擇器都精準對應 `dashboard_component.html`
中的元素。選擇器使用正確的 class 名稱、data 屬性與結構性關係。沒有誤判——每個
選擇器都恰好鎖定預期的元素。在 HTML 使用 data／ARIA 屬性而非樣式化 class 之處，
適當使用了 `[aria-current="page"]`、`[data-action="edit-member"]` 與 `[data-sort]`
等屬性選擇器。

**0.75 分**：幾乎所有選擇器都正確。有一兩個小瑕疵（例如稍微過度指定但仍可運作的
選擇器，或在更適合使用 data 屬性處改用了父層 class）。

**0.5 分**：多數選擇器更新正確，但有數個不精準或部分錯誤（例如鎖定父層而非特定
元素，或使用了近似的 class 名稱）。

**0.25 分**：更新了部分選擇器，但有許多不準確，或在未對照實際 HTML 結構下憑空
猜測。

**0.0 分**：選擇器大致未變、捏造，或不對應實際的標記。

### 評分項 2：選擇器風格的一致性（權重 20%）

**1.0 分**：更新後的選擇器在整個檔案中遵循一致的模式。若助手對互動元素使用 data
屬性、對樣式化元素使用 class，這項慣例就被一致地套用。選擇器專一性適中——不會
過於寬泛或不必要地深入。

**0.75 分**：大致一致，僅有一兩處風格偏差。

**0.5 分**：選擇器策略混雜——有些用 data 屬性、有些用深層巢狀路徑、有些用 class，
沒有明確的理由。

**0.25 分**：不一致且雜亂——選擇器的選擇沒有可辨識的模式。

**0.0 分**：完全沒有一致性。

### 評分項 3：測試邏輯的保留（權重 25%）

**1.0 分**：所有測試函式都保留了原本的結構、斷言值、預期數量與行為檢查。沒有移除、
更動或破壞任何測試邏輯。註解與 docstring 都被保留。只有選擇器被修改。

**0.75 分**：測試邏輯完整保留，僅有微不足道的外觀變更（例如重新排版某一行、更新
某個註解）。

**0.5 分**：多數測試邏輯被保留，但有一兩個斷言被不必要地更動（例如改變了預期數量
或文字值）。

**0.25 分**：有數個測試在選擇器修正之外，其邏輯也被修改。

**0.0 分**：測試邏輯被大幅更動——測試可能不再驗證相同的行為。

### 評分項 4：整體程式碼品質（權重 15%）

**1.0 分**：更新後的檔案是整潔、格式良好的 Python。import 維持不變。沒有語法
錯誤。選擇器字串有正確的引號，並在需要處正確跳脫（escape）。檔案能在無 import 或
語法錯誤的情況下執行。

**0.75 分**：程式碼整潔，僅有些微風格問題（例如屬性選擇器的引號不一致）。

**0.5 分**：有一些格式問題，或對非選擇器的程式碼做了不必要的更動。

**0.25 分**：有明顯的程式碼品質問題——引號不匹配、字串損壞，或不必要的重構。

**0.0 分**：檔案有語法錯誤，或無法 import。
