# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概覽

Snikket Web Portal 是一個 Python 3.9+ 的 Quart 非同步 Web 應用程式，用於管理 Snikket XMPP 伺服器。

## 開發設置

```bash
direnv allow                          # 載入 .envrc
cp example.env .env && $EDITOR .env   # 設定環境變數
pip install -r requirements.txt
pip install -r build-requirements.txt
make                                  # 構建 CSS + 編譯翻譯
quart run                             # 啟動開發伺服器
```

## 常用命令

```bash
# 構建
make                           # 構建 CSS + 編譯翻譯 (預設)
make build_css                 # 從 SCSS 編譯 CSS
make compile_translations      # 編譯 .po 翻譯檔案
make extract_translations      # 從代碼提取可翻譯字串

# 代碼品質
make lint                      # format + flake8
make format                    # Black 格式化 (admin.py, prosodyclient.py)
make flake8                    # Flake8 linting
make mypy                      # 型別檢查
```

## 架構

### 藍圖結構
- **main** (`main.py`): 登入、公開頁面
- **user** (`user.py`, `/user/`): 用戶自助服務
- **admin** (`admin.py`, `/admin/`): 管理面板 (需管理員權限)
- **invite** (`invite.py`, `/invite/`): 邀請管理

### 核心模組
- `prosodyclient.py` (1495 行): Prosody HTTP API 客戶端，處理所有後端通訊
- `muc_shell.py`: MUC 操作模組，直接透過 `docker exec prosodyctl shell` 執行
- `xmpputil.py`: XMPP 工具 (JID 解析等)
- `infra.py`: 基礎設施 (Babel i18n、認證客戶端)
- `colour.py`: XEP-0392 頭像顏色生成

### 認證
- Session 式認證透過 Prosody HTTP API
- 修飾器: `@client.require_admin_session()`, `@client.require_session()`
- 作用域: `prosody:restricted`, `prosody:registered`, `prosody:admin`

### 國際化
- 支援 11 種語言 (en, da, de, fr, id, it, pl, ru, sv, uk, zh_Hans_CN)
- 使用 `lazy_gettext as _l` 進行延遲翻譯
- 翻譯由 Weblate 管理

## 代碼品質標準

### 型別檢查 (mypy.ini)
嚴格模式啟用: `disallow_untyped_defs`, `disallow_untyped_calls`, `no_implicit_optional`

### 格式化
- Black 格式化: `admin.py`, `prosodyclient.py`
- 其他檔案: flake8 linting

## 環境變數

必要:
- `SNIKKET_WEB_SECRET_KEY`: Session 簽署密鑰
- `SNIKKET_WEB_PROSODY_ENDPOINT`: Prosody API URL (無尾部 /)
- `SNIKKET_WEB_DOMAIN`: 伺服器域名

選用:
- `SNIKKET_WEB_PROSODY_MUC_ENDPOINT`: MUC API Server URL (無尾部 /)，已停用

## MUC 操作

### 目前實作：muc_shell.py (Python 直接執行)

MUC 操作現在透過 `muc_shell.py` 模組直接執行 `docker exec snikket prosodyctl shell`，不需要額外的 Node.js 服務。

**前提條件**：Web Portal 必須與 Snikket Docker 容器在同一台主機上執行。

**提供的函式**：
- `muc_list_rooms(muc_domain)` - 列出 MUC 房間
- `muc_get_affiliation(room_jid, user_jid)` - 取得用戶在房間的身份
- `muc_set_affiliation(room_jid, user_jid, affiliation)` - 設定用戶身份

**prosodyclient.py 整合**：
`ProsodyClient` 類別的 MUC 方法內部呼叫 `muc_shell` 模組，保持 API 不變。

### 備用方案：snikket_muc_api_server.js (Node.js HTTP API)

若需要將 Web Portal 與 Docker host 分離部署，可使用 Node.js API Server：

```bash
node snikket_muc_api_server.js  # 監聽 127.0.0.1:5999
```

API Endpoints (POST)：
| Endpoint | 請求參數 | 說明 |
|----------|---------|------|
| `/muc/list` | `{"muc_domain": "groups.example.com"}` | 列出 MUC 房間 |
| `/muc/get-affiliation` | `{"room": "room@groups.example.com", "user": "user@example.com"}` | 取得用戶身份 |
| `/muc/set-affiliation` | `{"room": "...", "user": "...", "affiliation": "owner/admin/member/none/outcast"}` | 設定用戶身份 |

若要回退到 HTTP API，需在 `prosodyclient.py` 中取消註解原本的 HTTP 呼叫程式碼。

## CI/CD

GitHub Actions 執行: mypy → flake8 → 翻譯檢查 → Docker 構建

## 開發注意事項

### Template Macro 用法

`library.j2` 提供常用的 macro：

```jinja2
{# 標準表單按鈕 #}
{% call form_button("icon", form.action, class="primary", confirm="確認訊息?") %}{% endcall %}

{# 自訂表單按鈕 (用於內聯刪除等) #}
{% call custom_form_button("icon", name, value, class="danger", slim=True, confirm="確認?") %}
    按鈕文字
{% endcall %}
```

- `confirm` 參數：加入 JavaScript confirm() 確認對話框
- `slim=True`：只顯示圖示，文字作為 tooltip
- `class="danger"`：危險操作的視覺提示

### 表單驗證注意事項

當一個表單有多個 action（如 save、delete、add_member 等）時：
- 使用 `form.validate_on_submit()` 會驗證所有必填欄位
- 若某些 action 不需要完整驗證，需先檢查 `request.method == "POST"` 和具體的 action

範例（`edit_circle_chat` 路由）：
```python
if request.method == "POST":
    # 不需要完整驗證的 action
    if form.action_add_manager.data:
        # 處理新增管理員
        return redirect(...)

    # 需要完整驗證的 action
    elif form.validate_on_submit():
        if form.action_save.data:
            # 處理儲存
```

### Circle 與 Chat 的成員管理

- **Circle 成員**：透過 Prosody Admin API 管理
- **Chat 管理員**：透過 `muc_shell.py` 管理（owner/admin 角色）
- 聊天群組的管理員只能從該 Circle 的成員中選擇
- 新增聊天群組時會自動將建立者設為 owner

### Prosody API 回應處理

Prosody Admin API 有時回傳空內容或非 JSON：
```python
async with session.post(...) as resp:
    await self._raise_error_from_response(resp)
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return SomeClass.from_api_response(await resp.json())
    return None
```

### 除錯日誌

開發時可使用 `dev.log` 記錄除錯資訊：
```python
import logging
dev_logger = logging.getLogger("dev")
dev_logger.setLevel(logging.DEBUG)
if not dev_logger.handlers:
    fh = logging.FileHandler("dev.log")
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    dev_logger.addHandler(fh)

dev_logger.info("訊息")
```

注意：`dev.log` 不應提交到版本控制。
