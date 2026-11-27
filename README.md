# 規範書房 · Skill Room

在書房閱讀、標記和整理你的 AI 規範（`SKILL.md`、`AGENTS.md`、`CLAUDE.md`）。Codex 和 Claude 各有一間獨立的書房。
Read and organize your AI agent skills in a cozy library.

## 貼給你的 AI，一次安裝並開啟

不用會 GitHub。Codex 和 Claude 各有一間**獨立的書房**：各讀各的 Skill、各自寫導讀、資料分開存。兩個都裝的人，兩間可以同時開。

### 用 Codex 的人

打開 Codex（app 或 CLI），整段貼上：

```text
請在我的電腦安裝並開啟「Codex 書房」。
1. 將 https://github.com/Erica-vegaos/skill-management.git clone 到 ~/skill-room。若已有這個 repo，確認沒有未提交的修改，再用 git pull --ff-only 更新。若目錄不是這個 repo 或有本機修改，保留現況並告訴我。
2. 確認 Python 3 可用。Mac 執行 open "$HOME/skill-room/開啟 Codex 書房.command"。Windows 或 Linux 在獨立終端執行 app/codex_room.py --ai codex（Windows 用 py，Linux 用 python3），讓服務保持執行。
3. 開啟 http://127.0.0.1:8765/，回報匯入的份數。中文導讀由服務在背景生成，頁面會顯示進度和預估剩餘時間。不要變更任何 Skill 原始檔案。
```

會讀：`~/.codex/skills/*/SKILL.md`、`~/.codex/skills/.system/*/SKILL.md`、`~/.codex/AGENTS.md`。導讀由 Codex 寫。

Mac 上只安裝桌面版的同事，可以直接用位於「應用程式」資料夾的 ChatGPT 或 Codex 桌面版所附的 Codex，無須另外安裝 CLI。

### 用 Claude 的人

打開 Claude 桌面 app 的「Code」分頁（或終端裡的 Claude Code），整段貼上。一般聊天分頁碰不到你電腦的檔案，不能用。

```text
請在我的電腦安裝並開啟「Claude 書房」。
1. 將 https://github.com/Erica-vegaos/skill-management.git clone 到 ~/skill-room。若已有這個 repo，確認沒有未提交的修改，再用 git pull --ff-only 更新。若目錄不是這個 repo 或有本機修改，保留現況並告訴我。
2. 確認 Python 3 可用。Mac 執行 open "$HOME/skill-room/開啟 Claude 書房.command"。Windows 或 Linux 在獨立終端執行 app/codex_room.py --ai claude（Windows 用 py，Linux 用 python3），讓服務保持執行。
3. 開啟 http://127.0.0.1:8766/，回報載入了幾份文件。不要變更任何 Skill 原始檔案。
```

會讀：`~/.claude/skills/*/SKILL.md`、`~/.claude/CLAUDE.md`。導讀由 Claude Code 寫。

兩間本機書房啟動或重新掃描後會在背景補寫缺少或過期的導讀，每份完成即儲存並顯示。關閉或重新整理網頁不影響生成。重啟服務後會從尚未完成的導讀接續。若暫停，可在底部按「接續生成」。空白檔會略過，讀取失敗的原因在「我的書房」查看。

## 怎麼開 · Run it

| | Codex 書房 | Claude 書房 |
|---|---|---|
| Mac | 雙擊 `開啟 Codex 書房.command` | 雙擊 `開啟 Claude 書房.command` |
| Linux／Windows | `python3 app/codex_room.py --ai codex` | `python3 app/codex_room.py --ai claude` |
| 網址 | http://127.0.0.1:8765/ | http://127.0.0.1:8766/ |
| 資料 | `~/.skill-room/library-v1.sqlite3` | `~/.skill-room/library-claude-v1.sqlite3` |

只需要 Python 3，無須安裝套件。連接埠被占用時可加 `--port 其他號碼`。程式更新後重新開一次，舊版書房會自動被換掉。

另外也可以直接開 `app/index.html` 手動匯入，或把它發布成 Claude Artifact（宣告 `db`、`user`、`sample`）給只用 claude.ai 網頁的人。

## 整理與更新

- 從「書架」打開文件，或按「快速整理」標記保留、待修、封存或必備。標為「看不懂」的 Skill 可以從首頁的「待解釋」找到。
- 本機書房可從「我的書房」或整理結果按「讓整理生效」。把指令貼回同一個 AI，就能將勾選的個人 Skill 搬到 `skills-archive`，或請它就待修的 Skill 提出建議。封存後重新掃描會更新可處理清單，封存記錄仍可在書架的「封存」篩選查看。
- Codex 本機書房也可按「開始生效」。預覽會顯示要封存的路徑與待修草稿的差異。按「確認套用」才會備份至 `~/.skill-room/skill-backups/` 並寫回或搬移所選的個人 Skill。完成後頁面會列出結果及復原方式。Codex 僅負責草擬，檔案由書房服務依確認的清單處理。
- 首頁底部的「冷板凳 Skill」會盤點本機可辨識的成功讀取紀錄，優先列出紀錄未見使用及最後記錄距今至少 180 天的 Skill。未留下紀錄的使用方式無法判斷。先勾選，再標為封存並預覽指令。系統 Skill、全域規範、符號連結、必備及保留的 Skill 不會列入批次清理。
- Skill 宇宙會同時顯示中文導讀名稱與原始名稱。點開星星即可查看完整名稱，尚未產生導讀的 Skill 會顯示原始名稱。
- 啟動時會掃描來源，也可以在「我的書房」按「重新掃描本機 Skill」。原文更新時會保留原有決定和導讀資料，書房會提示重新確認新版。來源移除後，既有書籍與整理紀錄仍可查閱。
- 導讀和解釋由這間書房的 AI 寫（Codex 書房用 Codex、Claude 書房用 Claude Code），用的是你自己的帳號額度。已有的同版導讀會沿用。找不到該 AI 時可以複製提問到 ChatGPT。

## 遷移舊書房

- 在以前用來匯入的瀏覽器，以原本的網址開啟新版書房。在「我的書房」按「遷移這個瀏覽器的舊資料」。不同瀏覽器的舊資料可以各自遷移。
- 如果舊資料存在不同網址，例如另一個連接埠或純 HTML 頁面，請先在原網址用更新後的頁面按「下載這個瀏覽器的舊資料備份」，再到本機版的「我的書房」按「匯入舊書房備份」。備份可能含有原先選擇不遮蔽的內容，請留在自己的電腦。
- 遷移會保留舊書副本、整理標記與導讀，並保留同名的現有書籍。重複匯入相同備份不會新增副本。舊瀏覽器內的原始資料會留著。

## 資料 · Privacy

- 本機版的書籍與整理資料保存在 `~/.skill-room/`，Codex 書房和 Claude 書房各一份。同一台電腦上的瀏覽器共用同一間書房的資料。燈光和音效是各瀏覽器自己的設定。
- 本機匯入會在儲存前遮蔽可辨識的金鑰、密碼、Email、電話和家目錄路徑。服務只監聽 `127.0.0.1`，並檢查請求來源。
- 純 HTML 的資料留在該瀏覽器。Claude 雲端的書房資料依使用者隔離。選擇請 AI 寫導讀或解釋時，才會用你的 AI 帳號處理送出的內容。

## License

MIT
