# 進度與計畫

一次推進一個主題，每輪結束就 push。

## 已完成

### R1（2026-09-04）骨架與編碼核心

- `docs/10-p-machine/what-is-a-p-machine.md`：p-machine 的存在理由、堆疊機的取捨、segment。
- `docs/20-pcode-encoding/instruction-encoding.md`：三條從記憶體約束推出的編碼決定，
  配 `img/pcode-big-operand.svg`。
- `docs/30-opcode-tables/version-traps.md`：I.5 主表 128–215 逐槽，加短形式範圍；
  與 SunDog（IV.2.1）的六個位元組對照，全部不符。
- `docs/40-re-workflow/recover-opcode-table.md`：五步反推法，含 `.BLKW` 位移這個實際踩過的坑。

來源：UCSD Pascal I.5 的 `mainop.mac` 與 `CODESTAT`，兩者交叉驗證主表範圍
（dispatch 表 88 槽 vs 反組譯器的 `FOR OP:=128 TO 215`）。

### R2（2026-09-04）解出一份 68000 直譯器的表

- `docs/30-opcode-tables/sundog-ivx-table.md`：把五步法實跑在 SunDog 的 `SYSTEM.INTERP` 上。
  主迴圈在 `0xde`、dispatch 表在 `0xec`（256 項）、107 個相異目標。
  短形式分配全部解出，與 I.5 逐項對比。
- 附帶證實兩件事：變長編碼跨版本不變；「word 編號 × 2 + 8」這條換算的出處是
  解碼器最後兩行。

### R3（2026-09-04）IV.0 官方手冊進場

取得 SofTech《Version IV.0 Internal Architecture Guide》（1981）掃描檔，收進 `refs/`，
逐節摘譯成 `docs/50-iv-internals/` 八篇，涵蓋印刷頁 1–143。

- 參考層與教學層分開：`10`–`40` 解釋為什麼，`50` 回答手冊怎麼說。
  `docs/50-iv-internals/README.md` 是該層索引。
- `version-traps.md` 加「第三個座標：IV.0 的官方表」，把 I.5／IV.0／IV.2.1 三張表的
  短形式分配並排。**R2 從直譯器解出的分配與 IV.0 官方表逐格吻合**——當時手上沒有這份手冊，
  等於一次事後的獨立驗證。
- `img/activation-record.svg`：活動記錄的欄位配置，以及動態鏈與靜態鏈指向不同框的例子，
  取代原本的 ASCII 圖。
- 建 `CLAUDE.md`（工作契約）。全 repo 標點統一為全形。

## 勘誤：已被推翻的斷言

| 原斷言 | 出處 | 被什麼推翻 | 現況 |
|---|---|---|---|
| 「`0x00`–`0x7f` 全是短常數」是跨版本通則 | R1 `version-traps.md` | IV.0 手冊 App. VI.B：`SLDC` 只佔 `0x00`–`0x1f` | 改列為「不能當起手假設」的三件事之一 |
| 「短形式放在 opcode 的高段」是跨版本通則 | R1 `version-traps.md` | 同上：IV.0 起短形式整批在低段 | 同上 |
| 「IV.x 的表尚未解出」 | R1 `README.md`、`recover-opcode-table.md` | R2 解出 IV.2.1 的表；R3 取得 IV.0 官方表 | 兩處改寫，邊界改述為「主表其餘各格尚未逐格對照」 |

## 待辦

| # | 主題 | 下一個動作 |
|---:|---|---|
| 1 | IV.0 表 × IV.2.1 dispatch 逐格對照 | 主表 128–255 目前只對過 `LDE`/`LAE`/`STE`。拿 `docs/50-iv-internals/instruction-set-details.md` 的逐條語意，對 SunDog 那 96 個專屬處理常式，一格一格判 |
| 2 | 教學篇：程序呼叫怎麼進行 | 素材已齊（活動記錄 SVG + IV.0 的 `CIP`/`CXP`/`CGP`/`RNP` 語意）。缺的是把「為什麼要分同段／跨段／全域三種呼叫」推導出來 |
| 3 | 教學篇：segment 為什麼這樣切 | 從 `code-segment-format.md` 與 `codefile-and-environments.md` 的手冊事實，回推「幾十 KB 記憶體要跑大程式」這個約束怎麼逼出 SIB／E_Rec／codepool 這組設計 |
| 4 | packed 欄位 | `LDP`/`STP`/`IXP` 的位元欄位定址。IV.0 有逐條語意；SunDog 那版的運算元順序與手冊相反，值得單獨一篇 |
| 5 | I.5 各 opcode 的語意 | 目前只有助記符。從 `mainop.mac` 的處理常式讀 |
| 6 | ASCII 圖升級 | `code-segment-format.md` 的 segment 佈局圖、`memory-and-activation.md` 的主記憶體配置圖仍是 ASCII |

不屬於這個 repo：psys21（1984 年 p-System IV.2.1 磁碟映像）的反組譯另開獨立 repo。

## 每輪收尾

1. 文件寫完 → 配圖 → 轉 PNG 自己看過。
2. 更新 `README.md` 動線、`CONTEXT.md` 術語與本檔進度。
3. 檢查這輪的結論有沒有推翻既有斷言；有就同輪改掉，並在勘誤表補一列。
4. `git add -A` → 繁中 commit → push。
