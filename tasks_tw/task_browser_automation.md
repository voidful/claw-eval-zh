---
id: task_browser_automation
name: 瀏覽器自動化工作流程
category: coding
grading_type: hybrid
timeout_seconds: 180
language: zh
locale: zh-TW
region: TW
source_task_id: task_browser_automation
source_benchmark: pinchbench
source_locale: zh-TW
localization: taiwan
localization_strategy: language_polish
claw_eval_tw_id: T038tw_browser_automation
workspace_files:
- path: shop.html
  content: |-
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>TechMart — Gadget Shop</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, sans-serif; }
        body { background: #f5f5f5; padding: 20px; }
        h1 { text-align: center; margin-bottom: 20px; color: #333; }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; max-width: 900px; margin: 0 auto 20px; }
        .product { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
        .product h3 { margin-bottom: 8px; }
        .product .price { color: #16a34a; font-weight: bold; font-size: 1.2em; }
        .product .stock { color: #666; font-size: .85em; margin: 4px 0 12px; }
        .product button { background: #2563eb; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
        .product button:disabled { background: #9ca3af; cursor: not-allowed; }
        .product button:hover:not(:disabled) { background: #1d4ed8; }
        #cart { max-width: 900px; margin: 0 auto; background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
        #cart h2 { margin-bottom: 12px; }
        #cart-items { list-style: none; }
        #cart-items li { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
        #cart-items li .remove { color: #dc2626; cursor: pointer; text-decoration: underline; }
        #total { font-weight: bold; font-size: 1.1em; margin-top: 12px; }
        #checkout { margin-top: 12px; background: #16a34a; color: #fff; border: none; padding: 10px 24px; border-radius: 4px; cursor: pointer; font-size: 1em; }
        #checkout:hover { background: #15803d; }
        #checkout:disabled { background: #9ca3af; cursor: not-allowed; }
        #order-confirmation { display: none; max-width: 900px; margin: 20px auto; padding: 20px; background: #dcfce7; border-radius: 8px; text-align: center; }
        #order-confirmation h2 { color: #16a34a; }
        #order-id { font-family: monospace; font-size: 1.2em; }
      </style>
    </head>
    <body>
      <h1>TechMart — Gadget Shop</h1>
      <div class="products" id="product-list"></div>
      <div id="cart">
        <h2>Shopping Cart</h2>
        <ul id="cart-items"></ul>
        <div id="total">Total: $0.00</div>
        <button id="checkout" disabled>Checkout</button>
      </div>
      <div id="order-confirmation">
        <h2>Order Confirmed!</h2>
        <p>Your order <span id="order-id"></span> has been placed.</p>
        <p id="order-summary"></p>
      </div>
      <script>
        const products = [
          { id: 1, name: "Wireless Mouse", price: 29.99, stock: 15 },
          { id: 2, name: "Mechanical Keyboard", price: 89.99, stock: 8 },
          { id: 3, name: "USB-C Hub", price: 45.00, stock: 23 },
          { id: 4, name: "Webcam HD 1080p", price: 59.99, stock: 0 },
          { id: 5, name: "Monitor Stand", price: 34.50, stock: 12 },
          { id: 6, name: "Laptop Sleeve 15\"", price: 24.99, stock: 30 },
        ];
        let cart = [];
        function renderProducts() {
          const el = document.getElementById("product-list");
          el.innerHTML = products.map(p => `
            <div class="product" data-id="${p.id}">
              <h3>${p.name}</h3>
              <div class="price">$${p.price.toFixed(2)}</div>
              <div class="stock">${p.stock > 0 ? p.stock + " in stock" : "Out of stock"}</div>
              <button onclick="addToCart(${p.id})" ${p.stock === 0 ? "disabled" : ""}>Add to Cart</button>
            </div>
          `).join("");
        }
        function addToCart(id) {
          const p = products.find(x => x.id === id);
          if (!p || p.stock <= 0) return;
          const existing = cart.find(x => x.id === id);
          if (existing) { existing.qty++; } else { cart.push({ ...p, qty: 1 }); }
          p.stock--;
          renderProducts();
          renderCart();
        }
        function removeFromCart(id) {
          const idx = cart.findIndex(x => x.id === id);
          if (idx === -1) return;
          const item = cart[idx];
          const p = products.find(x => x.id === id);
          p.stock += item.qty;
          cart.splice(idx, 1);
          renderProducts();
          renderCart();
        }
        function renderCart() {
          const el = document.getElementById("cart-items");
          el.innerHTML = cart.map(item => `
            <li>
              <span>${item.name} × ${item.qty}</span>
              <span>$${(item.price * item.qty).toFixed(2)} <span class="remove" onclick="removeFromCart(${item.id})">Remove</span></span>
            </li>
          `).join("");
          const total = cart.reduce((s, i) => s + i.price * i.qty, 0);
          document.getElementById("total").textContent = "Total: $" + total.toFixed(2);
          document.getElementById("checkout").disabled = cart.length === 0;
        }
        document.getElementById("checkout").addEventListener("click", () => {
          if (cart.length === 0) return;
          const orderId = "ORD-" + Math.random().toString(36).substring(2, 8).toUpperCase();
          const total = cart.reduce((s, i) => s + i.price * i.qty, 0);
          const summary = cart.map(i => `${i.name} × ${i.qty}`).join(", ");
          document.getElementById("order-id").textContent = orderId;
          document.getElementById("order-summary").textContent = `Items: ${summary}. Total: $${total.toFixed(2)}`;
          document.getElementById("order-confirmation").style.display = "block";
          document.getElementById("cart").style.display = "none";
          document.querySelector(".products").style.display = "none";
          cart = [];
        });
        renderProducts();
        renderCart();
      </script>
    </body>
    </html>
---

# 瀏覽器自動化工作流程

## Prompt

工作區中有一個檔案 `shop.html`，它是一個自我完整（self-contained）、附帶購物車的
電子商務商品頁。你的任務：

1. 閱讀 `shop.html`，了解頁面結構、商品與購物車行為。
2. 撰寫一支 **Playwright 端對端測試腳本**，使用 `playwright.sync_api`（Python
   同步 API），並儲存為 `test_shop.py`。
3. 該腳本應自動化下列多步驟工作流程：
   - 開啟頁面
   - 確認「Webcam HD 1080p」（缺貨）的「Add to Cart」按鈕為 disabled
   - 將「Wireless Mouse」加入購物車
   - 將「Mechanical Keyboard」加入購物車
   - 再加入第二個「Wireless Mouse」（使數量變為 2）
   - 確認購物車顯示正確的總額（$149.97 = 29.99×2 + 89.99）
   - 從購物車移除「Mechanical Keyboard」
   - 確認更新後的總額（$59.98 = 29.99×2）
   - 點擊「Checkout」
   - 確認出現訂單確認，且訂單 ID 符合 `ORD-` 前綴
4. 請盡可能使用正確的 Playwright 斷言（`expect`）。
5. 測試應針對本機檔案 URL 執行：`file://{workspace}/shop.html`

## Expected Behavior

助手應該：

1. 閱讀 HTML 檔案，了解 DOM 結構與 JavaScript 行為
2. 撰寫一支涵蓋完整購物流程的 Playwright 測試
3. 使用適當的選擇器（以文字、data 屬性或 CSS 選擇器）
4. 在每個步驟加入斷言
5. 處理購物車的動態特性（品項新增／移除、總額更新）

## Grading Criteria

- [ ] 已建立檔案 `test_shop.py`
- [ ] 腳本使用 `playwright.sync_api`
- [ ] 測試缺貨時的 disabled 按鈕
- [ ] 將多個商品加入購物車
- [ ] 驗證購物車總額計算
- [ ] 從購物車移除品項
- [ ] 測試結帳（checkout）流程
- [ ] 驗證訂單確認
- [ ] 使用正確的斷言

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)
    test_file = workspace / "test_shop.py"

    if not test_file.exists():
        return {
            "file_created": 0.0,
            "uses_playwright": 0.0,
            "tests_disabled_button": 0.0,
            "tests_add_to_cart": 0.0,
            "tests_cart_total": 0.0,
            "tests_remove_item": 0.0,
            "tests_checkout": 0.0,
            "uses_assertions": 0.0,
        }

    scores["file_created"] = 1.0
    content = test_file.read_text()
    content_lower = content.lower()

    # Uses playwright sync API
    scores["uses_playwright"] = 1.0 if "playwright.sync_api" in content else 0.0

    # Tests disabled button / out of stock
    disabled_kw = ["disabled", "out of stock", "webcam", "is_disabled", "to_be_disabled"]
    scores["tests_disabled_button"] = 1.0 if sum(1 for k in disabled_kw if k in content_lower) >= 2 else 0.0

    # Tests adding to cart
    add_kw = ["add to cart", "wireless mouse", "mechanical keyboard", "addtocart", "click"]
    scores["tests_add_to_cart"] = 1.0 if sum(1 for k in add_kw if k in content_lower) >= 3 else 0.0

    # Tests cart total
    total_kw = ["149.97", "59.98", "total"]
    scores["tests_cart_total"] = 1.0 if sum(1 for k in total_kw if k in content_lower) >= 2 else 0.0

    # Tests remove from cart
    remove_kw = ["remove", "mechanical keyboard"]
    scores["tests_remove_item"] = 1.0 if all(k in content_lower for k in remove_kw) else 0.0

    # Tests checkout
    checkout_kw = ["checkout", "order", "ord-", "confirmation"]
    scores["tests_checkout"] = 1.0 if sum(1 for k in checkout_kw if k in content_lower) >= 2 else 0.0

    # Uses assertions
    assert_kw = ["expect", "assert", "to_have_text", "to_be_visible", "to_be_disabled", "to_contain_text"]
    scores["uses_assertions"] = 1.0 if sum(1 for k in assert_kw if k in content_lower) >= 2 else 0.0

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

### 評分項 1：測試覆蓋（權重 35%）

**1.0 分**：測試涵蓋所有指定的步驟：disabled 按鈕檢查、加入多個商品、數量追蹤、
總額驗證、品項移除、更新後的總額、結帳，以及訂單確認。每個步驟都有有意義的斷言。

**0.75 分**：涵蓋大多數步驟並附斷言。可能有一兩個步驟缺失或斷言薄弱。

**0.5 分**：涵蓋基本流程，但遺漏數個驗證步驟。

**0.25 分**：僅涵蓋工作流程中的少數步驟。

**0.0 分**：沒有有意義的測試覆蓋。

### 評分項 2：程式碼品質（權重 25%）

**1.0 分**：測試程式碼整潔、組織良好。正確使用 Playwright 慣用法（page fixture、
expect 斷言、適當的選擇器）。程式碼可讀，變數命名清楚，並在有助益處加上註解。

**0.75 分**：程式碼品質良好，僅有些微問題。大致為慣用的 Playwright 寫法。

**0.5 分**：可運作，但有程式碼品質問題（選擇器不佳、缺少錯誤處理、硬編碼的等待）。

**0.25 分**：程式碼有重大問題，會使其不可靠或難以維護。

**0.0 分**：程式碼無法運作，或不是有效的 Python。

### 評分項 3：選擇器策略（權重 20%）

**1.0 分**：使用穩健的選擇器——以文字為基礎的選擇器、以 role 為基礎的查詢，或
data 屬性。避免依賴版面配置的脆弱 CSS 選擇器。選擇器能在 HTML 些微變動後仍存活。

**0.75 分**：選擇器大致良好，僅有少數脆弱者。

**0.5 分**：良好與脆弱的選擇器混雜。

**0.25 分**：多數為脆弱的選擇器（nth-child、複雜的 CSS 路徑）。

**0.0 分**：沒有選擇器（程式碼未與頁面互動）。

### 評分項 4：斷言品質（權重 20%）

**1.0 分**：使用 Playwright 的 `expect` API 進行斷言。檢查具體的值（確切總額、
文字內容、可見狀態）。斷言能抓到真正的 bug。

**0.75 分**：使用 expect API 進行良好的斷言。少數本可更具體。

**0.5 分**：有斷言，但偏弱（只檢查元素是否存在，而非內容）。

**0.25 分**：斷言極少。

**0.0 分**：沒有斷言。
