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
   — UCSD I.5 的完整表，以及為什麼它不能拿去讀別版的程式碼。
4. [從直譯器反推 opcode 表](docs/40-re-workflow/recover-opcode-table.md)
   — 手上那份 p-code 版本不明時的正解，含機器碼直譯器怎麼處理。

已經知道 p-system、只想要表：直接看 3。手上有一份讀不懂的 p-code：直接看 4。

## 資料來源

一手來源是 UCSD 於 1978 年釋出的 **UCSD Pascal I.5 原始碼**（非商業用途免費下載），
其中兩份檔案支撐了本 repo 的大部分結論：

- `mainop.mac`：PDP-11 版直譯器，含 dispatch 表 `XFRTBL`。
- `CODESTAT`：官方 p-code 反組譯器，Pascal 寫的，含 `GETBIG` 的變長解碼與 opcode 分類註解。

實測對照的樣本來自 SunDog（1985，Atari ST）的 `SYSTEM.STARTUP`。
**本 repo 不含任何原版磁碟映像、可執行檔或遊戲資料**，只保留位元組層級的編碼結論。

## 邊界

- I.5 的表是 **PDP-11 版直譯器**解出來的。同版本不同 CPU 的移植是否完全一致，未查證。
- IV.x 的表**尚未解出**。文件裡凡是提到 IV.x 的地方都只寫已由實測確認的片段。
- 助記符來自直譯器的標籤名。標籤名反映實作者的命名，不一定等於官方文件用語。

## 授權

文件與圖採 CC BY 4.0。引用的 UCSD 原始碼片段版權屬 Regents of the University of California。
