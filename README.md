# 規範書房 · Skill Room

在書房閱讀、標記和整理你的 AI 規範（`SKILL.md`、`AGENTS.md`）。
Read and organize your AI agent skills in a cozy library.

## 貼給本機 Codex，一次安裝並開啟

在能操作你電腦檔案和終端的 Codex app 或 CLI 裡，整段貼上：

```text
請在我的電腦安裝並開啟「規範書房」。
1. 將 https://github.com/Erica-vegaos/skill-management.git clone 到 ~/skill-room。若已有這個 repo，確認沒有未提交的修改，再用 git pull --ff-only 更新。若目錄不是這個 repo 或有本機修改，保留現況並告訴我。
2. 確認 Python 3 可用。Mac 執行 open "$HOME/skill-room/開啟書房.command"。Windows 或 Linux 在獨立終端啟動 app/codex_room.py（Windows 用 py，Linux 用 python3），讓服務保持執行。
3. 開啟 http://127.0.0.1:8765/。從書房畫面或啟動日誌核對載入份數與錯誤，回報網址和結果。不用打包 ZIP、上傳 Skill、選 AI 或產生導讀，也不要變更任何 Skill 原始檔案。
```

書房開啟時會自動載入 `~/.codex/skills/*/SKILL.md`、`~/.codex/skills/.system/*/SKILL.md` 和 `~/.codex/AGENTS.md`。空白檔會略過。來源以相對路徑顯示，同名的個人與系統 Skill 各自保留。畫面會顯示載入數量，讀取失敗的原因可在「我的書房」查看。

## 怎麼開 · Run it

| 方式 | 做法 |
|---|---|
| Mac | 雙擊 `開啟書房.command`。保留第一次啟動的終端視窗。再雙擊會開啟同一個服務。 |
| Linux／Windows | 在專案目錄執行 `python3 app/codex_room.py`（Windows 用 `py app/codex_room.py`），開啟終端顯示的網址。 |
| 純 HTML | 開啟 `app/index.html`，依畫面指示手動匯入 Skill。 |
| Claude 雲端 | 把 `app/index.html` 發布成 Claude Artifact（宣告 `db`、`user`、`sample`），由看的人手動匯入。 |

只需要 Python 3，無須安裝 Python 套件。若 8765 已被其他程式占用，關閉該程式後再試，或在專案目錄執行 `python3 app/codex_room.py --port 8766`，再使用終端顯示的網址。更新程式後，請先在原本的終端按 Ctrl+C 停止舊服務，再重新啟動。

## 整理與更新

- 從「書架」打開文件，或按「決定去留」標記保留、待修、封存或必備。本機版的標記只記錄在書房。
- 啟動時會掃描來源，也可以在「我的書房」按「重新掃描本機 Skill」。原文更新時會保留原有決定和導讀資料，書房會提示重新確認新版。來源移除後，既有書籍與整理紀錄仍可查閱。
- 需要導讀時再按畫面上的導讀或解釋按鈕。服務優先找 Codex CLI，再找 Claude Code，也可用 `--ai claude` 指定。兩者都沒有時可以複製提問到 ChatGPT。啟動和掃描均不會呼叫 AI。

## 遷移舊書房

- 在以前用來匯入的瀏覽器，以原本的網址開啟新版書房。在「我的書房」按「遷移這個瀏覽器的舊資料」。不同瀏覽器的舊資料可以各自遷移。
- 如果舊資料存在不同網址，例如另一個連接埠或純 HTML 頁面，請先在原網址用更新後的頁面按「下載這個瀏覽器的舊資料備份」，再到本機版的「我的書房」按「匯入舊書房備份」。備份可能含有原先選擇不遮蔽的內容，請留在自己的電腦。
- 遷移會保留舊書副本、整理標記與導讀，並保留同名的現有書籍。重複匯入相同備份不會新增副本。舊瀏覽器內的原始資料會留著。

## 資料 · Privacy

- 本機版的書籍與整理資料保存在 `~/.skill-room/library-v1.sqlite3`。所有連到同一台電腦上同一服務的瀏覽器共用書房資料。燈光和音效是各瀏覽器自己的設定。
- 本機匯入會在儲存前遮蔽可辨識的金鑰、密碼、Email、電話和家目錄路徑。服務只監聽 `127.0.0.1`，並檢查請求來源。
- 純 HTML 的資料留在該瀏覽器。Claude 雲端的書房資料依使用者隔離。選擇請 AI 寫導讀或解釋時，才會用你的 AI 帳號處理送出的內容。

## License

MIT
