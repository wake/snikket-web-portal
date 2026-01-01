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

## Fork Features

This fork adds the following features to the original Snikket Web Portal.

### Group Chat Management

- Edit group chat name and avatar
- Manage member affiliations (owner, admin, member, none)
- Block/unblock users from group chats
- View affiliation descriptions with XEP-0045 specification link

### Internationalization

- Traditional Chinese (zh_Hant_TW) translation
- Language switcher in topbar and footer (cookie-based, falls back to browser setting)

### UI Improvements

- Confirmation dialogs for destructive actions
- Administrators column in circle chat table

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

## 分支新增功能

此分支在原版 Snikket Web Portal 基礎上新增以下功能。

### 群組聊天管理

- 編輯群組聊天名稱與頭像
- 管理成員身份（擁有者、管理員、成員、預設）
- 封鎖/解除封鎖群組聊天用戶
- 查看身份說明與 XEP-0045 規範連結

### 國際化

- 繁體中文 (zh_Hant_TW) 翻譯
- 語系切換器（Cookie 儲存，預設依照瀏覽器設定）

### 介面改善

- 刪除/移除操作前的確認對話框
- Circle 聊天表格顯示管理員欄位
