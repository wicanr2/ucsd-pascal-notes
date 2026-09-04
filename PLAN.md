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

### R5（2026-09-04）教學篇：程序呼叫（待辦 #2 完成）

- `docs/10-p-machine/procedure-call.md`：從「一次呼叫要留下什麼」推導出整組呼叫指令。
  九族助記符不是列舉出來的，是兩個獨立問題（非區域變數在哪、程式碼在哪）
  各自的常見情形與一般情形相乘。
- 三條推導鏈：
  - **靜態鏈必須由呼叫端填**，因為只有呼叫端知道相對層數 → 走 0／1／2／n 步與直達 `BASE`
    五種情形 → `CPL`／`SCPI1`／`SCPI2`／`CPI`／`CPG`。
  - **Codepool 會整塊移動**（手冊 p.118）→ 回返點不能存絕對位址 →
    `MSIPC`（段內相對）加 `MSPROC`（程序號）才是搬移後仍有效的座標。
  - **參數由被呼叫者清**（`RPU` 的 `B` 運算元）→ 呼叫點很多、返回點只有一個，
    把位元組數寫在返回處省的是每個呼叫點。
  三條都收束到同一條密度原則，與短形式 opcode 同源。
- 於是 Mark Stack 五個欄位每一個都有來由，一個不多——`MSENV` 是跨段呼叫存在的必然結果。
- `img/call-matrix.svg`：3×2 矩陣加位元組數，把「省的是位元組不是功能」直接畫出來。
- **解掉一個舊謎**：R2 在 SunDog 的 `SCXG` 處理常式裡發現一條 `cmpi.w #1,d0` 快速路徑，
  當時只能標成「陷阱」。手冊 p.66 寫明 segment 1 的程序可以內嵌在直譯器裡、
  位置由直譯器的表格給出——那是規格要求的分支。`sundog-ivx-table.md` 已補上指標。

### R6（2026-09-04）教學篇：segment 為什麼這樣切（待辦 #3 完成）

- `docs/10-p-machine/segment-and-environment.md`：從「1978 年的機器只有幾十 KB，
  程式比記憶體大」推導出整套 segment 機制。
- 主命題：跨段呼叫穿過的三層間接（`E_Vec` → `E_Rec` → `SIB`）**各自對應一個
  不能合併的約束**，拿掉約束該層就塌縮：
  - 分離編譯 → `E_Vec`（本地號碼；沒有中央登記處，就不能有全域編號）
  - 「同一 unit 的全域變數只有一份」→ `E_Rec`（程式碼可丟可讀回，全域資料不行）
  - 「段會被丟掉、也會整塊移動」→ `SIB`（所以它放在 Heap，不在段裡面——
    描述一個東西的資料必須活得比被描述者久）
- 附帶推出的幾件事：搬動單位必須連續 → 段內一切用相對位移；
  `Residency` 是計數不是布林（巢狀鎖定）；`Ref_Count`／`Residency`／`Activity`
  分別回答「現在能不能丟／准不准丟／該不該丟」，三者不能併。
- 反向檢查一則（柵欄原則）：`Seg_Name` 看似與 `Seg_Addr` 重複，其實服務的是
  **連結期**——號碼是本地的，名字才是跨檔案的。判欄位多餘前先確認它服務哪個階段。
- `img/segment-indirection.svg`：三層縱向流程，每層並列「回答什麼／約束是什麼／
  拿掉約束會怎樣」。

### R7（2026-09-04）逐條驗證、packed 欄位、I.5 語意（待辦 #7／#4／#5 完成）

三篇共用同一批新證據：用 IDA 把 SunDog 直譯器的 107 個處理常式全部反組譯出來，
以及把 1978 年 I.5 的 PDP-11 原始碼讀進來。

- `docs/30-opcode-tables/iv21-routine-audit.md`（#7）：98 個常式逐條對 IV.0 的定義，
  **全部相符，沒有一條不符**。副產品是這份直譯器的暫存器分工表
  （`a0`=MP、`a1`=全域基底也就是 `BASE`、`a2`=段基底、`a4`=IPC、`a5`=主迴圈…），
  補上了 R5 留的「`BASE` 是不是 `BP`」待查證項。
- `docs/20-pcode-encoding/packed-fields.md`（#4）：一個 16-bit 位址塞不下位元欄位，
  所以位址變成堆疊上三個 word。`IXP` 用 `divu` 的餘數、`LDP` 用「左移再右移」、
  `STP` 用「XOR 兩次」——三個都在避開算遮罩，因為遮罩 `(1<<n)−1` 要花指令算，
  而移位器是現成的。配 `img/packed-field.svg`。
- `docs/30-opcode-tables/i15-opcode-semantics.md`（#5）：I.5 的語意直接來自作者註解
  （80 個助記符一個不漏）。重點是三個演化：**層數從執行期搜尋搬到編譯期**
  （I.5 的 `CIP` 沿動態鏈比對 lex level，IV.0 編進運算元）、
  **MSCW 從 6 個 word 變 5 個**（`MSIPC` 從絕對位址變段內相對、`MSJTAB` 從指標變編號，
  兩者都是 Codepool 會搬移的後果）、**砍掉能組合出來的專用指令**。
- 順帶對上一件事：I.5 `macros.mac` 定義的執行期錯誤碼常數，與 IV.2.1 直譯器的
  九個錯誤入口逐項相同，七年沒動。#7 原本只能從觸發點反推語意，現在有了一手定義。
- 新工具 `tools/dump-routines.py`（IDAPython）與 `tools/routine-audit.py`。

## 勘誤：已被推翻的斷言

| 原斷言 | 出處 | 被什麼推翻 | 現況 |
|---|---|---|---|
| 「`0x00`–`0x7f` 全是短常數」是跨版本通則 | R1 `version-traps.md` | IV.0 手冊 App. VI.B：`SLDC` 只佔 `0x00`–`0x1f` | 改列為「不能當起手假設」的三件事之一 |
| 「短形式放在 opcode 的高段」是跨版本通則 | R1 `version-traps.md` | 同上：IV.0 起短形式整批在低段 | 同上 |
| 「IV.x 的表尚未解出」 | R1 `README.md`、`recover-opcode-table.md` | R2 解出 IV.2.1 的表；R3 取得 IV.0 官方表 | 兩處改寫，邊界改述為「主表其餘各格尚未逐格對照」 |
| I.5 主表有 8 格是「保留」 | R1 `version-traps.md` | `procop.mac` 用同名 `.CSECT TABLES` 把程序呼叫族填進那些 `.BLKW` 空格 | 8 格改成 `CSP`／`RNP`／`CIP`／`RBP`／`CBP`／`CXP`／`CLP`／`CGP`；`.BLKW` 的說明補上第二層 |
| 「I.5 只剩六個保留槽」 | R1 `version-traps.md` | 同上——主表 88 格全滿 | 改成「已經全滿」 |
| 「packed 欄位的運算元順序與手冊相反」 | R1 `PLAN.md` 待辦 #4 | `LDP`／`STP`／`IXP` 的堆疊次序與手冊 `Pack-ptr` 逐項相同 | 待辦刪除，說明寫進 `packed-fields.md` |
| 「`SCXG` 的運算元順序與手冊相反」 | R4 `iv0-vs-iv21.md` | 上一列的說法被誤植到 `SCXG`；實作與手冊一致 | 刪除該句 |
| `COMPAR` 用 `XFRTBL+40.` 查子表 | R1 `version-traps.md` | 子表是 `CMPTBL`；`XFRTBL+40.` 是 `BOOLCMP` 借用整數比較的手法 | 改寫成「opcode 決定運算、運算元決定型別」 |
| `0x78` 的助記符是 `SIND1` | R4 `dispatch-crosstab.py` | 手冊是 `SIND0…SIND7`；工具把範圍展開的起編寫死成 1 | 工具修正；R4 的 211 = 211 結論不受影響 |

## 待辦

| # | 主題 | 下一個動作 |
|---:|---|---|
| 1 | ~~IV.0 表 × IV.2.1 dispatch 逐格對照~~ | **R4 完成**。編號層已確立逐格相同。語意層（96 個專屬常式逐條讀）另立為 #7 |
| 2 | ~~教學篇：程序呼叫怎麼進行~~ | **R5 完成**。SunDog 端的 `CPL`／`CPI`／`CXI` 處理常式實際碼還沒讀，併入 #7 |
| 3 | ~~教學篇：segment 為什麼這樣切~~ | **R6 完成**。IV.2.1 的 SIB／E_Rec 版面還沒從 SunDog 的位元組驗過，併入 #7 |
| 4 | ~~packed 欄位~~ | **R7 完成**。順帶推翻了「運算元順序與手冊相反」這個從 R1 帶到現在的斷言 |
| 5 | ~~I.5 各 opcode 的語意~~ | **R7 完成**。順帶更正了 I.5 表裡 8 格被誤標為「保留」的程序呼叫指令 |
| 6 | ASCII 圖升級 | `code-segment-format.md` 的 segment 佈局圖、`memory-and-activation.md` 的主記憶體配置圖仍是 ASCII |
| 7 | ~~96 個專屬常式的逐條語意~~ | **R7 完成**。98 個常式全部相符 |

不屬於這個 repo：psys21（1984 年 p-System IV.2.1 磁碟映像）的反組譯另開獨立 repo。

## 每輪收尾

1. 文件寫完 → 配圖 → 轉 PNG 自己看過。
2. 更新 `README.md` 動線、`CONTEXT.md` 術語與本檔進度。
3. 檢查這輪的結論有沒有推翻既有斷言；有就同輪改掉，並在勘誤表補一列。
4. `git add -A` → 繁中 commit → push。
