#!/bin/bash
# Mac: double-click to open the Claude room (reads ~/.claude, guides by Claude). Opens the running one if it is already up.
set -eu
cd -- "$(dirname -- "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo '找不到 Python 3。請先安裝 Python 3 再開一次。'
  read -r -p '按 Enter 結束。' _ || true
  exit 1
fi
echo 'Claude 書房開著時請保留這個視窗。要停止時按 Ctrl+C。'
python3 app/codex_room.py --ai claude "$@" || {
  status=$?
  if [ -t 0 ] && [ "$status" -ne 130 ]; then
    read -r -p '按 Enter 結束。' _ || true
  fi
  exit "$status"
}
