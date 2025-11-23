#!/bin/bash
set -e

# 取得目前這個腳本所在目錄（也就是 repo 根目錄）
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

# 可以讓外部指定 VENV_DIR，沒給就用預設 ./venv
VENV_DIR="${VENV_DIR:-$BASE_DIR/venv}"

# 啟動 venv
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
else
  echo "Virtualenv not found at $VENV_DIR"
  exit 1
fi

# ====== 環境變數，沒指定就用預設值 ======
: "${QUART_APP:=snikket_web:create_app}"
: "${QUART_ENV:=production}"
: "${QUART_DEBUG:=0}"
: "${QUART_PORT:=5444}"
: "${QUART_HOST:=127.0.0.1}"

export QUART_APP QUART_ENV QUART_DEBUG

# ====== 啟動 Quart ======
exec quart run --port "$QUART_PORT" --host "$QUART_HOST"
