# 規範書房 · Skill Room

把你的 AI Skill（`SKILL.md`、`AGENTS.md`）讀懂、整理，然後讓整理真的生效。
Read, sort and actually clean up your AI agent skills (`SKILL.md`, `AGENTS.md`) — in a cozy library instead of a file tree.

## 最簡單：叫你的 AI 幫你開 · Easiest: ask your Codex or Claude Code

不用會 GitHub。打開 Codex 或 Claude Code（app 或終端都可以），整段貼上：

```
請幫我安裝並打開「規範書房」：
1. 把 https://github.com/Erica-vegaos/skill-management 下載到 ~/skill-room（已經有就更新到最新版）
2. 把 ~/.claude/skills/*/SKILL.md、~/.codex/skills/*/SKILL.md、~/.codex/AGENTS.md（存在的才收）
   打包成桌面上的 my-skills.zip，zip 裡保留「資料夾名/SKILL.md」的結構，不要修改任何原始檔案
3. Mac：執行 open ~/skill-room/開啟書房.command
   Windows：另開一個終端執行 py ~/skill-room/app/codex_room.py，不要讓它卡住這個對話
4. 告訴我：書房網址、zip 位置、收了幾份 Skill
```

書房打開後：按「開始」→ 選你用的 AI（「Codex 本機」或「Claude 桌面 app／Claude Code」）→ 上傳桌面的 `my-skills.zip`。
電腦上有 Codex 就由 Codex 寫中文導讀，沒有就用 Claude Code，用的都是你自己的帳號額度。
之後要再開，雙擊 `~/skill-room/開啟書房.command` 就好。

## 怎麼開 · Run it

| 方式 | 做法 |
|---|---|
| 自己電腦 | 下載這個 repo。Mac 雙擊 `開啟書房.command`；其他系統執行 `python3 app/codex_room.py`，打開終端顯示的 `127.0.0.1` 網址 |
| 誰寫導讀 | 自動找電腦上的 Codex CLI，沒有就找 Claude Code（`claude`）；兩個都沒有也能用，改成複製提問到 ChatGPT。要指定：`--ai claude` |
| Claude 雲端 | 把 `app/index.html` 發布成 Claude Artifact（宣告 `db`、`user`、`sample`），導讀由看的人自己的 Claude 寫 |

Only Python 3 is needed. No build step, no dependencies, nothing leaves your machine except what you send to your own AI.

## 三步 · How it works

1. **搬進來 Import** — 選你用的 AI，複製畫面上的指令給它，把它給的 zip 或全文交給書房。上傳前自動遮蔽金鑰、密碼、Email、電腦路徑。
2. **整理 Sort** — 在咖啡廳翻卡片：保留、待修、封存、必備。看不懂按「?」請 AI 解釋。
3. **讓它生效 Apply** — 按「讓整理生效」，複製指令貼給你的 AI：封存的 Skill 會被移到 `skills-archive/`（不刪除），待修的先給修改建議，等你確認才改。

## 資料 · Privacy

- 本機版：資料存在你的瀏覽器。Local: data stays in your browser's storage.
- Claude 雲端版：每個人的書房在 `data/users/<id>/`，連發布者都看不到。Cloud: each viewer's library is private, even from the publisher.
- 本機服務只聽 `127.0.0.1`，並檢查來源。呼叫 Codex 時關閉 shell、網路搜尋並用唯讀沙箱；呼叫 Claude Code 時不給任何工具、不存對話。

## License

MIT
