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
- `SNIKKET_PROSODY_MUC_ENDPOINT`: MUC API Server URL (無尾部 /)，預設為空

## MUC API Server

`snikket_muc_api_server.js` 是一個 Node.js 常駐服務，透過 `prosodyctl shell` 執行 MUC 相關操作。

### 啟動方式
```bash
node snikket_muc_api_server.js  # 監聽 127.0.0.1:5999
```

### API Endpoints (POST)

| Endpoint | 請求參數 | 說明 |
|----------|---------|------|
| `/muc/list` | `{"muc_domain": "groups.example.com"}` | 列出 MUC 房間 |
| `/muc/get-affiliation` | `{"room": "room@groups.example.com", "user": "user@example.com"}` | 取得用戶身份 |
| `/muc/set-affiliation` | `{"room": "...", "user": "...", "affiliation": "owner/admin/member/none/outcast"}` | 設定用戶身份 |

### Python 客戶端方法 (prosodyclient.py)

- `muc_list_rooms(muc_domain)` - 列出 MUC 房間
- `muc_get_affiliation(room_jid, user_jid)` - 取得用戶在房間的身份
- `muc_set_affiliation(room_jid, user_jid, affiliation)` - 設定用戶身份

## CI/CD

GitHub Actions 執行: mypy → flake8 → 翻譯檢查 → Docker 構建
