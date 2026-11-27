#!/bin/bash
# Mac: double-click to open the skill room locally (uses your Codex CLI if installed).
set -eu
cd -- "$(dirname -- "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo '找不到 Python 3。請先安裝 Python 3 再開一次。'
  read -r -p '按 Enter 結束。' _
  exit 1
fi
echo '書房開著時請保留這個視窗；關掉或按 Ctrl+C 就停止。'
python3 app/codex_room.py "$@"
