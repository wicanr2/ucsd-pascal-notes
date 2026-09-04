# UCSD Pascal / p-system 筆記

把 UCSD p-system 的 p-code 從第一性原理拆開：**每個編碼決定都能從「1978 年的機器只有幾十 KB」
這個約束逼出來**。寫給要讀懂一份老 p-code 的人。

起因是逆向 1985 年 Atari ST 遊戲 SunDog——它的遊戲邏輯不是 68000 機器碼，是 p-code。
過程中發現網路上找得到的 opcode 表不能直接用，而正確的做法（對著手上那份直譯器把表解出來）
沒有現成的文件在講。這個 repo 補那一塊。

## 從哪開始讀

不熟 p-system 就照順序讀這六篇：

1. [p-machine 是什麼](docs/10-p-machine/what-is-a-p-machine.md)
   — 為什麼要發明一台假電腦，為什麼它是堆疊機，segment 在解決什麼問題。
2. [指令編碼](docs/20-pcode-encoding/instruction-encoding.md)
   — 常數為什麼不需要 opcode、變數編號為什麼編進 opcode、變長運算元怎麼讀。
3. [程序呼叫怎麼進行](docs/10-p-machine/procedure-call.md)
   — 呼叫指令為什麼有九族。兩個獨立問題相乘出來的矩陣，以及 Mark Stack 五個欄位的來由。
4. [segment 為什麼這樣切](docs/10-p-machine/segment-and-environment.md)
   — 跨段呼叫穿過的三層間接，各自對應哪個約束；SIB 為什麼不放在段裡面。
5. [opcode 表與版本陷阱](docs/30-opcode-tables/version-traps.md)
   — I.5、IV.0、IV.2.1 三張表放在一起，哪些東西跨版本不動、哪些是某一版的個別選擇。
6. [從直譯器反推 opcode 表](docs/40-re-workflow/recover-opcode-table.md)
   — 手上那份 p-code 版本不明時的正解，含機器碼直譯器怎麼處理。

已經知道 p-system、只想要表：直接看 5。手上有一份讀不懂的 p-code：直接看 6。

## 一份直譯器，從解出表到驗完語意

同一個目標（SunDog 的 `SYSTEM.INTERP`）走完三個階段，可以當成第 6 篇的實作範例：

- [實例：解出一份 1985 年 68000 直譯器的 opcode 表](docs/30-opcode-tables/sundog-ivx-table.md)
  — 五步反推法實跑一次，從 IDA 載入到驗證。
- [逐格對照：IV.0 官方表 × IV.2.1 dispatch 表](docs/30-opcode-tables/iv0-vs-iv21.md)
  — 解出來的表拿官方表驗一次，256 格逐格比對。
- [逐條驗證：98 個處理常式](docs/30-opcode-tables/iv21-routine-audit.md)
  — 編號對上之後再驗語意，附這份直譯器的暫存器分工與執行期錯誤碼。

## 單一主題

- [packed 欄位](docs/20-pcode-encoding/packed-fields.md)
  — 一個 16-bit 位址塞不下位元欄位，於是位址變成堆疊上的三個 word。
- [I.5 各 opcode 的語意](docs/30-opcode-tables/i15-opcode-semantics.md)
  — 1978 年那版逐條在做什麼，從 PDP-11 直譯器的處理常式讀出來。

## 手冊摘譯

[`docs/50-iv-internals/`](docs/50-iv-internals/README.md) 是 IV.0 官方手冊的逐節摘譯，
八篇涵蓋 codefile 格式、記憶體佈局、指令逐條語意、三層 I/O、作業系統與官方 opcode 表。
每條結論標印刷頁碼，用來回查與對碼。

前五篇解釋「為什麼」，摘譯回答「手冊怎麼說」。兩邊衝突時以手冊加上實測位元組為準。

## 資料來源

**UCSD Pascal I.5 原始碼**（1978 年釋出，非商業用途免費下載）。其中兩份檔案支撐了
早期幾篇的結論：

- `mainop.mac`：PDP-11 版直譯器，含 dispatch 表 `XFRTBL`。
- `CODESTAT`：官方 p-code 反組譯器，Pascal 寫的，含 `GETBIG` 的變長解碼與 opcode 分類註解。

**SofTech《UCSD p-System and UCSD Pascal Version IV.0 Internal Architecture Guide》**
（1981）。掃描檔在 [`refs/`](refs/README.md)，摘譯在 `docs/50-iv-internals/`。
IV.0 是 SunDog 那版（IV.2.1）最接近的官方文件。

實測對照的樣本來自 SunDog（1985，Atari ST）的 `SYSTEM.STARTUP` 與 `SYSTEM.INTERP`。
**本 repo 不含任何原版磁碟映像、可執行檔或遊戲資料**，只保留位元組層級的編碼結論。

## 邊界

- I.5 的表是 **PDP-11 版直譯器**解出來的。同版本不同 CPU 的移植是否完全一致，未查證。
- IV.0 的表是**官方手冊印的**，不是從直譯器解出來的。它與 SunDog 的 IV.2.1 dispatch 表
  已經 256 格逐格對過，編號完全相同；但那是「編號相同」，不是「語意逐條相同」。
- SunDog 直譯器裡 96 個專屬處理常式，只讀過其中幾個。已知至少一個（`SCXG`）的
  運算元順序與手冊敘述相反。
- 助記符來自直譯器的標籤名與官方手冊。標籤名反映實作者的命名，不一定等於官方文件用語；
  兩者不一致的地方以手冊為準並標註。

## 授權

文件與圖採 CC BY 4.0。引用的 UCSD 原始碼片段版權屬 Regents of the University of California；
`refs/` 內掃描手冊的版權屬 SofTech Microsystems 及其後續權利人，收錄為技術研究與非商業引用之用。
