#!/bin/bash
# Mac: double-click to start the local Skill Room or open the running instance.
set -eu
cd -- "$(dirname -- "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo '找不到 Python 3。請先安裝 Python 3 再開一次。'
  read -r -p '按 Enter 結束。' _ || true
  exit 1
fi
echo '第一次啟動後請保留這個視窗。要停止服務時按 Ctrl+C。'
python3 app/codex_room.py "$@" || {
  status=$?
  if [ -t 0 ] && [ "$status" -ne 130 ]; then
    read -r -p '按 Enter 結束。' _ || true
  fi
  exit "$status"
}
