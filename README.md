# 規範書房 · Skill Room

把你的 AI Skill（`SKILL.md`、`AGENTS.md`）讀懂、整理，然後讓整理真的生效。
Read, sort and actually clean up your AI agent skills (`SKILL.md`, `AGENTS.md`) — in a cozy library instead of a file tree.

## 怎麼開 · Run it

| 方式 | 做法 |
|---|---|
| 自己電腦 | 下載這個 repo。Mac 雙擊 `開啟書房.command`；其他系統執行 `python3 app/codex_room.py`，打開終端顯示的 `127.0.0.1` 網址 |
| Codex 寫導讀 | 先裝 Codex CLI 並 `codex login`，書房會自動用它寫中文導讀和解釋；沒裝也能用，改成複製提問到 ChatGPT |
| Claude 雲端 | 把 `app/index.html` 發布成 Claude Artifact（宣告 `db`、`user`、`sample`），導讀由看的人自己的 Claude 寫 |

Only Python 3 is needed. No build step, no dependencies, nothing leaves your machine except what you send to your own AI.

## 三步 · How it works

1. **搬進來 Import** — 選你用的 AI，複製畫面上的指令給它，把它給的 zip 或全文交給書房。上傳前自動遮蔽金鑰、密碼、Email、電腦路徑。
2. **整理 Sort** — 在咖啡廳翻卡片：保留、待修、封存、必備。看不懂按「?」請 AI 解釋。
3. **讓它生效 Apply** — 按「讓整理生效」，複製指令貼給你的 AI：封存的 Skill 會被移到 `skills-archive/`（不刪除），待修的先給修改建議，等你確認才改。

## 資料 · Privacy

- 本機版：資料存在你的瀏覽器。Local: data stays in your browser's storage.
- Claude 雲端版：每個人的書房在 `data/users/<id>/`，連發布者都看不到。Cloud: each viewer's library is private, even from the publisher.
- 本機服務只聽 `127.0.0.1`，並檢查來源；呼叫 Codex 時關閉 shell、網路搜尋，用唯讀沙箱。

## License

MIT
