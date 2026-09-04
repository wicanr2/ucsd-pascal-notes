# UCSD Pascal / p-system 筆記

把 UCSD p-system 的 p-code 從第一性原理拆開：**每個編碼決定都能從「1978 年的機器只有幾十 KB」
這個約束逼出來**。寫給要讀懂一份老 p-code 的人。

起因是逆向 1985 年 Atari ST 遊戲 SunDog——它的遊戲邏輯不是 68000 機器碼，是 p-code。
過程中發現網路上找得到的 opcode 表不能直接用，而正確的做法（對著手上那份直譯器把表解出來）
沒有現成的文件在講。這個 repo 補那一塊。

## 從哪開始讀

不熟 p-system 就照順序：

1. [p-machine 是什麼](docs/10-p-machine/what-is-a-p-machine.md)
   — 為什麼要發明一台假電腦，為什麼它是堆疊機，segment 在解決什麼問題。
2. [指令編碼](docs/20-pcode-encoding/instruction-encoding.md)
   — 常數為什麼不需要 opcode、變數編號為什麼編進 opcode、變長運算元怎麼讀。
3. [opcode 表與版本陷阱](docs/30-opcode-tables/version-traps.md)
   — I.5、IV.0、IV.2.1 三張表放在一起，哪些東西跨版本不動、哪些是某一版的個別選擇。
4. [從直譯器反推 opcode 表](docs/40-re-workflow/recover-opcode-table.md)
   — 手上那份 p-code 版本不明時的正解，含機器碼直譯器怎麼處理。
5. [實例：解出一份 1985 年 68000 直譯器的 opcode 表](docs/30-opcode-tables/sundog-ivx-table.md)
   — 把第 4 篇實跑一次，從 IDA 載入到驗證，附解出來的短形式分配與兩版對比。

已經知道 p-system、只想要表：直接看 3。手上有一份讀不懂的 p-code：直接看 4，再照 5 的做法走一遍。

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
- IV.0 的表是**官方手冊印的**，不是從直譯器解出來的。SunDog 的 IV.2.1 直譯器在短形式
  分配與 `LDE`/`LAE`/`STE` 上與它吻合，主表 128–255 其餘各格尚未逐格對照。
- SunDog 直譯器裡 96 個專屬處理常式的語意，多數還沒逐條讀出來。
- 助記符來自直譯器的標籤名與官方手冊。標籤名反映實作者的命名，不一定等於官方文件用語；
  兩者不一致的地方以手冊為準並標註。

## 授權

文件與圖採 CC BY 4.0。引用的 UCSD 原始碼片段版權屬 Regents of the University of California；
`refs/` 內掃描手冊的版權屬 SofTech Microsystems 及其後續權利人，收錄為技術研究與非商業引用之用。
