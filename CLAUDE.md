# 這個 repo 怎麼寫

UCSD p-system 的 p-code 知識庫。目標讀者是「手上有一份讀不懂的 p-code，想把它解出來」的人。

繼承 `~/.claude/rules/`（身分、文風、執行邊界）與 `~/.claude/rules/00-rules-index.md` 的
按需索引；本檔只寫這個 repo 特有的部分。

## 兩層結構

| 層 | 位置 | 性質 | 判準 |
|---|---|---|---|
| 教學層 | `docs/10`–`docs/40` | 第一性原理敘事，從「1978 年的機器只有幾十 KB」這個約束推導 | 讀者從零開始能一路讀下去 |
| 參考層 | `docs/50-iv-internals` | IV.0 官方手冊的逐節摘譯，每條結論標印刷頁碼 | 查得到、對得回原文 |

參考層是教學層的證據來源，不是它的替代品。新解出的東西先落進參考層（帶頁碼），
確認站得住再決定要不要寫成教學篇。

## 文件職責

| 檔 | 放什麼 | 不放什麼 |
|---|---|---|
| `README.md` | 用途、閱讀動線、資料來源、邊界宣告 | 日期、逐輪進度、失敗嘗試 |
| `PLAN.md` | 分輪進度與待辦表、每輪收尾流程 | 結論本身 |
| `CONTEXT.md` | 術語表與書寫慣例 | 教學內容 |
| `CLAUDE.md` | 本檔：工作契約 | 領域知識 |
| `docs/NN-主題/` | 一檔一主題，數字前綴決定閱讀順序 | — |
| `img/` | 所有 SVG | PNG（驗證用的 PNG 走 scratchpad，不入版控） |
| `refs/` | 一手來源掃描檔 | 遊戲原版磁碟映像、可執行檔、遊戲資料 |

新結論要寫進既有文件時，正文只寫現況，不敘述「當初怎麼錯的」；被推翻的舊斷言集中記在
`PLAN.md` 的勘誤段，正文最多留一個指標。教訓寫成規則，不寫成會過期的事件敘述
（見 `~/.claude/rulebook/63`）。

## 書寫規範

- 繁體中文。程式碼、助記符、識別字、檔名保留原文。
- 標點全形（`，。：；（）`）。半形只用在三處：程式碼區塊內、行內程式碼內、
  英文列舉（`DB, B`）與英文原名（`Cursor X,Y Positioning`）。
- 術語首次出現當場一句話翻譯：`活動記錄（activation record）`。
- 結論先行。長篇開頭寫「結論先講：⋯」，接著才是推導。
- 不貼導引式 meta 標籤（「先看這段」「白話：」「本文適合⋯」）。章節用中性標題。
- 位元組寫 `0x` 十六進位；引用組語原文時保留該處進位制（PDP-11 組語是八進位）。

## 證據紀律

- **每條結論標來源。** 手冊出處寫**印刷頁碼**（`手冊 p.49`），不寫 PDF 頁碼。
  兩者差 6（印刷頁 = PDF 頁 − 6），只在需要回查掃描檔時才並列。
- **一手贏二手。** 原始位元組與官方手冊 > 反組譯推論 > 網路上流傳的 opcode 表。
  網路表在本 repo 只能當「待驗證的線索」，不能當結論。
- **推論等級。** 沒有一手來源支持的推論寫「待查證」，不寫進表。反組譯得到的語意標明
  是已證實還是強推論，並附證據出處（函式位址、位元組）。
- **版本不可混用。** I.5（1978, PDP-11）、IV.0（1981, 手冊）、IV.2.1（1985, SunDog）
  是三份不同的東西。opcode 數值分配跨版本會變，指令編碼慣例不會。
  任何一張表都要標它屬於哪一版、由哪份直譯器解出。
- **查詢落空不等於不存在。** grep 沒中先換大小寫、換編碼、拆字再搜，並做一次正對照
  （拿已知會中的樣本驗證搜尋本身沒壞）。

## 配圖

- 概念圖、格式圖、記憶體佈局一律手繪 SVG 放 `img/`，不用 ASCII 圖。
  既有的 ASCII 圖視為待升級項。
- 白底、克制配色（可帶橘色點綴）、圓角框，
  `font-family="'Noto Sans CJK TC','PingFang TC','Microsoft JhengHei',sans-serif"`。
- 畫完一定轉 PNG 自己看過再收，檢查 CJK 缺字、標籤重疊、溢出：

  ```
  docker run --rm --network none -u "$(id -u):$(id -g)" \
    -v "$PWD:/w" -w /w zenika/alpine-chrome \
    --headless --no-sandbox --disable-gpu --screenshot=/w/out.png \
    --window-size=W,H --force-device-scale-factor=2 file:///w/img/x.svg
  ```

- 文件引用相對路徑（`docs/NN-主題/` 深度 2 → `../../img/`），
  用 `<p align="center"><img src=... width=... alt=...></p>` 置中。

## 每輪流程

1. 一次推進一個主題。
2. 寫文件 → 配圖 → 轉 PNG 自檢。
3. 更新 `README.md` 動線、`CONTEXT.md` 術語、`PLAN.md` 進度與待辦。
4. 檢查有沒有舊斷言被這輪的結論推翻；有就同輪改掉，別留到下一輪。
5. `git add -A` → 繁中 commit → push。

## 執行環境

- 批次文字處理、轉檔、反組譯、抓圖一律在 Docker 容器內跑；主機只做 git、檔案編輯與
  容器控制。一次性工作用 `docker run --rm --network none -u "$(id -u):$(id -g)"`
  並設 `--memory` / `--cpus` / `--pids-limit`。
- **不碰共用的 docker 資源**：禁止任何 `prune`、`rmi`、刪除不是自己這次建立的容器。
  這台機器同時放著多個客戶專案的 image。
- 反組譯用 `ida-pro-9.4-idapython:locked-v1`；作法見
  `~/.claude/knowledge-base/retro/ida-pro-9.4.md`。
- 中間產物寫 scratchpad，不寫進 repo。

## git

- 作者信箱一律 `wicanr2@gmail.com`。進 repo 動工時先跑
  `git config user.email` 與 `git log --format=%ae | sort -u` 各一次
  （前者管下一個 commit，後者才看得到歷史）。
- commit message 用繁體中文，結尾帶 `Co-Authored-By:`。
  **不放 `Claude-Session:` 連結**——那個 URL 只有當事人打得開。
- push 前確認 `README.md` 的邊界宣告與 repo 實際內容一致（這是 public repo）。

## 素材位置

| 東西 | 位置 |
|---|---|
| IV.0 Internal Architecture Guide（1981） | `refs/Softech_Pascal_IV_intArch_1981.pdf` |
| p-System IV.2.1 磁碟映像（1984） | `~/cht/p-code/psys21/`，不入版控 |
| SunDog（1985, Atari ST）樣本 | 本機，不入版控。repo 只留位元組層級的編碼結論 |
| UCSD Pascal I.5 原始碼（`mainop.mac`、`CODESTAT`） | 引用片段見 `docs/30-opcode-tables/version-traps.md` |
