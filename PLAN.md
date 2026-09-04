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

### R4（2026-09-04）IV.0 表 × IV.2.1 dispatch 逐格對照（待辦 #1 完成）

- `docs/30-opcode-tables/iv0-vs-iv21.md`：把 IV.0 官方表與 SunDog `SYSTEM.INTERP` 的
  256 項 dispatch 表逐格比對。**IV.0 列出的 211 個指令與 IV.2.1 有處理常式的 211 個槽
  逐格重合，沒有一格例外**；兩邊「沒有指令」的 45 格也在同樣位置。
  結論：主表可以直接照 IV.0 的表讀。
- 附帶查出兩件事：
  - 16 格全部導向同一個 fault（錯誤 12），照 IV.0 的表是**全部 16 個浮點指令**，
    一個不多一個不少——這份直譯器沒有實作浮點。與 `laanwj/sundog` 的獨立結論一致。
  - `SLOD1`/`SLOD2`、`SCPI1`/`SCPI2` 各自共用一個常式，差別由 opcode 值算出來。
    IV.0 把成對指令編成相鄰號碼，實作直接利用了這個相鄰性。
- 抽驗四個運算元格式各異的常式（`LDCN`/`LDCB`/`LDCI`/`STL`），68000 碼逐行對上
  IV.0 的文字定義。其中 `LDCI` 的三行組字順序，**從位元組獨立證實了手冊 p.46 的
  「W 運算元永遠低位元組在前」**。
- 第三方比對 `laanwj/sundog` 的 `doc/notes.md`：浮點那 16 格與該文件標「error 0xc」的
  16 格完全一致；助記符拼法有 14 處不同。其中 `CPL`/`LDRD`/`NAT` 三處回查掃描原件
  （印刷頁 141、139、142）確認**摘譯忠實於手冊**——是手冊自己的拼法與它自己的說明字首
  對不起來（`CPL` 的說明是「Call **L**ocal **P**rocedure」），不是誰抄錯。
- `img/opcode-map.svg`：兩張 16×16 的 opcode 分配圖並排，灰格位置完全重疊。
- 方法可重跑：整條管線收成 `tools/dispatch-crosstab.py`。抽出來的 107 個相異目標與
  45 個錯誤槽，與 R2 用 IDA 解出的數字一致，等於換一條路徑重跑了一次。
- 建 `tools/`：另收 `normalize-punct.py`（標點正規化，已改成冪等並帶 `KEEP` 例外清單）。
  起因是同一個坑踩了兩次——手動保留的英文原文（`eX(ecute)`、`Cursor X,Y Positioning`）
  在下一輪重跑時被無聲吃掉。例外現在寫進腳本，不再靠記憶。

## 勘誤：已被推翻的斷言

| 原斷言 | 出處 | 被什麼推翻 | 現況 |
|---|---|---|---|
| 「`0x00`–`0x7f` 全是短常數」是跨版本通則 | R1 `version-traps.md` | IV.0 手冊 App. VI.B：`SLDC` 只佔 `0x00`–`0x1f` | 改列為「不能當起手假設」的三件事之一 |
| 「短形式放在 opcode 的高段」是跨版本通則 | R1 `version-traps.md` | 同上：IV.0 起短形式整批在低段 | 同上 |
| 「IV.x 的表尚未解出」 | R1 `README.md`、`recover-opcode-table.md` | R2 解出 IV.2.1 的表；R3 取得 IV.0 官方表 | 兩處改寫，邊界改述為「主表其餘各格尚未逐格對照」 |

## 待辦

| # | 主題 | 下一個動作 |
|---:|---|---|
| 1 | ~~IV.0 表 × IV.2.1 dispatch 逐格對照~~ | **R4 完成**。編號層已確立逐格相同。語意層（96 個專屬常式逐條讀）另立為 #7 |
| 2 | 教學篇：程序呼叫怎麼進行 | 素材已齊（活動記錄 SVG + IV.0 的 `CIP`/`CXP`/`CGP`/`RNP` 語意）。缺的是把「為什麼要分同段／跨段／全域三種呼叫」推導出來 |
| 3 | 教學篇：segment 為什麼這樣切 | 從 `code-segment-format.md` 與 `codefile-and-environments.md` 的手冊事實，回推「幾十 KB 記憶體要跑大程式」這個約束怎麼逼出 SIB／E_Rec／codepool 這組設計 |
| 4 | packed 欄位 | `LDP`/`STP`/`IXP` 的位元欄位定址。IV.0 有逐條語意；SunDog 那版的運算元順序與手冊相反，值得單獨一篇 |
| 5 | I.5 各 opcode 的語意 | 目前只有助記符。從 `mainop.mac` 的處理常式讀 |
| 6 | ASCII 圖升級 | `code-segment-format.md` 的 segment 佈局圖、`memory-and-activation.md` 的主記憶體配置圖仍是 ASCII |
| 7 | 96 個專屬常式的逐條語意 | 編號已確定同 IV.0，所以這步是**驗證**不是解謎：對每個常式，拿 IV.0 的定義當假設去讀 68000 碼，記錄相符或不符。R4 已驗 4 個。不符的要單獨記（`SCXG` 是已知的一例） |

不屬於這個 repo：psys21（1984 年 p-System IV.2.1 磁碟映像）的反組譯另開獨立 repo。

## 每輪收尾

1. 文件寫完 → 配圖 → 轉 PNG 自己看過。
2. 更新 `README.md` 動線、`CONTEXT.md` 術語與本檔進度。
3. 檢查這輪的結論有沒有推翻既有斷言；有就同輪改掉，並在勘誤表補一列。
4. `git add -A` → 繁中 commit → push。
