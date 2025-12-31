# Snikket Web Portal

![Screenshot of the app](docs/readme-screenshot.png)

## Development quickstart

```console
$ direnv allow
$ cp example.env .env
$ $EDITOR .env  # to adapt the configuration to your needs
$ pip install -r requirements.txt
$ pip install -r build-requirements.txt
$ make
$ quart run
```

## Configuring

### Purely via environment variables

For a list of required and understood environment variables as well as their
semantics, please refer to [`example.env`](example.env).

### Via python code

In addition to statically setting environment variables, it is possible to
initialise the environment variables in a python file. To do that, pass the
path to the python file as `SNIKKET_WEB_PYENV` environment variable.

The python file is evaluated before further environment variable processing
takes place. Every name defined in that file which begins with an upper case
ASCII letter is included in the processing of environment variables for
configuration purposes.

For a (non-productive) example of such a file, see `example.env.py`.

---

# Snikket Web Portal（中文版）

![應用程式截圖](docs/readme-screenshot.png)

## 開發快速入門

```console
$ direnv allow
$ cp example.env .env
$ $EDITOR .env  # 根據需求調整設定
$ pip install -r requirements.txt
$ pip install -r build-requirements.txt
$ make
$ quart run
```

## 設定方式

### 純環境變數設定

必要與可用的環境變數及其說明，請參閱 [`example.env`](example.env)。

### 透過 Python 程式碼設定

除了靜態設定環境變數外，也可以在 Python 檔案中初始化環境變數。只需將 Python 檔案路徑設定為 `SNIKKET_WEB_PYENV` 環境變數即可。

該 Python 檔案會在其他環境變數處理之前執行。檔案中以大寫 ASCII 字母開頭的變數名稱，都會被納入設定處理。

範例檔案（非正式環境用）請參閱 `example.env.py`。

---

# Changelog / 更新日誌

## Changes since Nov 22, 2025 / 2025年11月22日以來的變更

### New Features / 新功能

#### MUC (Multi-User Chat) Management / MUC 群組聊天管理

- **Group chat editing** - Add ability to edit MUC group chat name and avatar (XEP-0045, XEP-0486)

  **群組聊天編輯** - 新增編輯 MUC 群組聊天名稱和頭像的功能（XEP-0045、XEP-0486）

- **Chat managers management** - Add/remove managers from circle members, change manager roles (owner/admin)

  **聊天管理員管理** - 從 Circle 成員中新增/移除管理員，變更管理員角色（owner/admin）

- **Administrators column** - Display administrators in circle edit page chat table

  **管理員欄位** - 在 Circle 編輯頁面的聊天表格中顯示管理員

- **muc_shell.py module** - Execute MUC operations directly via `docker exec prosodyctl shell`, eliminating the need for Node.js MUC API server

  **muc_shell.py 模組** - 透過 `docker exec prosodyctl shell` 直接執行 MUC 操作，不再需要 Node.js MUC API 伺服器

#### Internationalization / 國際化

- **Traditional Chinese (zh_Hant_TW)** - Add complete Traditional Chinese translation

  **繁體中文 (zh_Hant_TW)** - 新增完整繁體中文翻譯

#### UI/UX Improvements / 介面改善

- **Confirm dialogs** - Add confirmation dialogs to all delete/remove actions (delete group chat, remove circle member, remove chat manager, delete avatar, delete/revoke invitation, destroy password reset link)

  **確認對話框** - 為所有刪除/移除操作新增確認對話框

- **Styling improvements** - Adjust topbar, login page, and avatar image styling

  **樣式改善** - 調整頂部導覽列、登入頁面和頭像圖片樣式

#### Developer Experience / 開發者體驗

- **start.sh script** - Add startup script with auto-detection of script directory and virtual environment activation

  **start.sh 腳本** - 新增啟動腳本，支援自動偵測目錄和虛擬環境啟動

- **CLAUDE.md** - Add development guidance for Claude Code instances

  **CLAUDE.md** - 新增 Claude Code 開發指引文件

### Bug Fixes / 錯誤修正

- **MUC forbidden error** - Show user-friendly message when admin lacks MUC owner permissions

  **MUC 權限錯誤** - 當管理員缺少 MUC owner 權限時顯示友善訊息

- **MUC API integration** - Fix environment variable handling and non-JSON response handling

  **MUC API 整合** - 修正環境變數處理和非 JSON 回應處理

- **Template fixes** - Fix b64encode syntax and standard_button macro call

  **模板修正** - 修正 b64encode 語法和 standard_button 巨集呼叫

### Removed / 移除

- **snikket_muc_api_server.js** - Deprecated Node.js MUC API server removed (replaced by muc_shell.py)

  **snikket_muc_api_server.js** - 移除已棄用的 Node.js MUC API 伺服器（由 muc_shell.py 取代）
