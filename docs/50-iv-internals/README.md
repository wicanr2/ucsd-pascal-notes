# IV.0 Internal Architecture Guide 摘譯

SofTech Microsystems《UCSD p-SYSTEM and UCSD PASCAL Version IV.0 Internal Architecture Guide》
（1981 年 3 月第一版）的逐節摘譯。掃描檔在 [`refs/`](../../refs/)。

這是 repo 的參考層：每條結論標印刷頁碼，用來回查、對碼、驗證教學層的說法。
從零開始學 p-machine 請走 [教學動線](../../README.md#從哪開始讀)。

手冊本身的定位是「進階使用者的指南與參考」，不是實作規格書；SofTech 在 p.1 聲明它承諾維護的
是《Users' Manual》描述的使用者層功能，「利用 internal tricks 的程式設計師風險自負」。
也就是說，這裡的每一條都描述 IV.0 的**實作**，不是跨版本保證。

| 篇 | 手冊範圍 | 內容 |
|---|---|---|
| [Code Segment 格式](code-segment-format.md) | Ch. I、II.1–II.2.2.1（p.1–27） | 系統沿革、interpretive execution、segment 格式、byte sex、routine dictionary、常數池、relocation list |
| [Codefile 組織與執行環境](codefile-and-environments.md) | II.2.1.7–II.3（p.22–41） | segment reference list、linker information、segment dictionary、SIB 與 E_Rec |
| [記憶體佈局、Task 環境與活動記錄](memory-and-activation.md) | II.3–II.4.2.1（p.40–53） | TIB 與並行 task、主記憶體配置、五種運算元格式、活動記錄與兩條鏈 |
| [IV 版指令逐條語意](instruction-set-details.md) | II.4.2.2（p.52–70） | 每條指令的 opcode 值、運算元、堆疊效應、語意 |
| [低階 I/O：語言層與 RSP/IO](lowlevel-io-language-rsp.md) | III.1–III.4 前半（p.71–97） | I/O 三層架構、`UNIT*` intrinsics、IORESULT、邏輯磁碟結構、RSP/IO 語意 |
| [低階 I/O：BIOS](lowlevel-io-bios.md) | III.4–III.5（p.98–109） | 邏輯區塊到實體磁區的對映、bootstrap 位置、各處理器的 BIOS 呼叫序列 |
| [作業系統層](operating-system.md) | Ch. IV–V（p.111–133） | UNIT 組成、Heap 與 Codepool、fault handling、目錄格式、程式啟動流程 |
| [附錄：IV.0 官方 opcode 表](appendix-opcodes.md) | App. VI.B（p.137–143） | 官方完整 p-code 表，按功能分組 |

## 版本

手冊描述 IV.0；repo 逆向的 SunDog 直譯器是 IV.2.1。已對上的穩定點與已知差異記在
[opcode 表與版本陷阱](../30-opcode-tables/version-traps.md)。

跨版本穩定的是**編碼慣例**（變長運算元的讀法、短形式把運算元編進 opcode 值的作法）；
不穩定的是**數值分配**。拿這裡的表去讀 I.5 的程式碼會全錯。
