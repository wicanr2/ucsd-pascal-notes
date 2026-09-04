# Code Segment 格式

> 來源：SofTech Microsystems《UCSD p-SYSTEM and UCSD PASCAL Version IV.0
> INTERNAL ARCHITECTURE GUIDE》（1981 年 3 月第一版），出自 Chapter I
> （Introduction）與 Chapter II「The P-Machine」的 II.1～II.2.2.1 開頭，
> 涵蓋印刷頁 1–27（掃描 PDF 頁 pg-007～pg-033；實測印刷頁碼 = PDF 頁碼 − 6）。

> 延伸閱讀：[本層索引](README.md)｜[p-machine 是什麼](../10-p-machine/what-is-a-p-machine.md)（segment 在解決什麼問題）

## Chapter I：簡介（手冊 p.1–3）

這本指南描述 UCSD p-System 的內部設計：P-machine、作業系統、基本 I/O，
以及這些元素如何組織起來執行 UCSD Pascal（或 BASIC、FORTRAN）寫的程式。
定位是「進階使用者的指南與參考」，**不是**給實作者的獨立規格書（手冊 p.1）。
SofTech 聲明它承諾維護的是《Users' Manual》描述的使用者層功能，而不是本書
描述的實作策略；「利用 internal tricks 的程式設計師風險自負」（手冊 p.1）。

系統沿革（手冊 p.2–3）：1974 年底 Kenneth Bowles 在 UCSD 帶學生為微電腦
實作 Pascal；最早跑在 PDP-11/10 配軟碟與 VT-50 終端機上。直譯式執行從一開始
就存在；p-code 改編自 Urs Ammann（ETH Zürich）的原始設計，目標是緊湊、
容易由編譯器產生，並讓編譯器與 codefile 盡量小。最早的實作都在
PDP-11/LSI-11 上，之後才移植到 8080、Z80 與其他處理器。後來由 SofTech
Microsystems 接手維護與授權。

## Chapter II.1：P-machine 概觀（手冊 p.5–7）

### II.1 與 II.1.1 Interpretive Execution（手冊 p.5）

- P-machine 是一台理想化的機器；作業系統本身、Filer 等系統程式、編譯出來的
  使用者程式全都跑在 P-machine 上。系統裡的 codefile 不是 p-code 就是
  native code（特定實體處理器的碼）（手冊 p.5）。
- p-code 設計目標是**緊湊**（比等價 native code 短很多）且**容易被編譯器
  產生**；因為緊湊又簡單，把 P-machine 實作到各種真實處理器上相對容易，
  這是 p-System 可移植性的關鍵（手冊 p.5）。
- 「P」代表 “pseudo”。P-machine 可以是實體處理器，也可以由直譯器模擬；
  直譯器是以某特定處理器的 native code 寫成的程式，負責逐條執行 p-code
  指令並控制機器相關的 I/O。開機（bootstrap）= 載入直譯器（若需要）並啟動它，
  下一步是呼叫作業系統（手冊 p.5）。

### II.1.2 Stack 與 Heap（手冊 p.5–6）

- 系統把常駐記憶體的資料放在兩個動態結構：**Stack** 放靜態變數、程序/函式
  呼叫的簿記資訊、運算式求值；**Heap** 放動態變數，包括描述程式環境的結構
  （手冊 p.5）。
- Stack 可視為 P-machine 的一部分（大多數 p-code 指令都會動到它）；Heap
  是系統的一部分，但主要由作業系統而非 P-machine 支援（手冊 p.6）。
- Stack 與 Heap 都在主記憶體、彼此相向成長，「（大致上）First-In-First-Out」。
  兩者之間是一塊部分未使用、但包含 **Codepool** 的區域（手冊 p.6）。

### II.1.3 Code Segments（手冊 p.6）

- 程式碼存在一或多個 segment 裡；一個 segment 可含 p-code、native code 或
  兩者混合。除了碼本身，每個 segment 還有給系統用的簿記資訊，以及（通常）
  一個常數池（手冊 p.6）。
- 每個「編譯單元」（獨立編譯的 Pascal PROGRAM 或 UNIT）產生一個
  **principal segment**；若程式含 `SEGMENT` 常式或 `EXTERNAL` native 常式，
  還會有 **subsidiary segments**（手冊 p.6）。
- 執行（eX(ecute)）程式時，作業系統讀取 codefile 內嵌的參考資訊，找出所有
  需要的編譯單元（含 subsidiary segments 與 UNIT 引用 UNIT 這種間接參考），
  建立執行期跨段參考（如程序呼叫）用的表（手冊 p.6）。
- 執行中的各 segment 與 Stack、Heap 競爭主記憶體；跨段呼叫成功的前提条件是
  **呼叫方與被呼叫方的 segment 都必須在主記憶體中**（手冊 p.6）。
- 主記憶體中的 segment 全部連續存放在 Stack 與 Heap 之間的 **Codepool**，
  Codepool 可被搬動以騰出空間；Codepool 的管理在 Chapter IV（手冊 p.6）。

### II.1.4 Device I/O（手冊 p.7）

- 裝置 I/O 由語言層呼叫直譯器內的常式完成；直譯器的 I/O 常式再呼叫
  直譯器的 **BIOS**（Basic I/O Subsystem），BIOS 直接控制周邊硬體。
  I/O 環境相依性被隔離在 BIOS 裡，移植到新硬體只需改 BIOS，不必動整個
  直譯器（手冊 p.7）。
- 在 Adaptable Systems 上，BIOS 本身對 **SBIOS**（Simplified BIOS）有標準
  介面；SBIOS 是一組簡單 I/O 常式，讓使用者能快速把系統移植到新的 I/O 環境。
  BIOS 在 Chapter III 說明，SBIOS 在《Installation Guide》（手冊 p.7）。

## II.2.1 Code Segments（手冊 p.8–20）

### 段的基本屬性與段頭（手冊 p.8）

- 一個 code segment 是一群常式（routine）加上描述資訊；段內的碼與資訊是
  連續的，因為 segment 是碼的「搬動單位」——一次載入一整段（手冊 p.8）。
- 一段最多 255 個常式，編號 1..255（手冊 p.8）。
- 編譯時每段被指定一個**名稱**（8 字元）與一個**號碼**。名稱給作業系統在
  associate time 處理跨段參考、以及 LIBRARY 維護 codefile 時用；號碼是執行期
  參考該段用的（手冊 p.8）。
- 段的開頭（低位址）是一筆記錄，依序包含：routine dictionary 指標、
  relocation list 指標、8 字元段名（4 個 word）、byte sex 指示字、
  constant pool 指標、realsize 字、保留 2 個 word（手冊 p.8）。

### Figure 1:Executable Code Segment Format（手冊 p.9）

段的記憶體配置（低位址在下，高位址在上；圖頂標了 odd/even 表示 word 的
兩個位元組序）：

```
高位址(high)             ┌ odd | even
        ┌──────────────────────────┐
        │      relocation list     │ ←┐
        ├──────────────────────────┤  │
        │    number of procedures  │ ←┼┐
        ├──────────────────────────┤  ││
        │   pointer to procedure 1 │  ││
        ├──────────────────────────┤  ││
        │   pointer to procedure 2 │ ─┘│
        ├──────────────────────────┤   │  procedure
        │           ...            │   │  dictionary
        ├──────────────────────────┤   │
        │   pointer to procedure N │   │
        ├──────────────────────────┤   │
        │       Constant Pool      │ ←┼─┐
        ├──────────────────────────┤   │
        │      procedure code      │   │
        ├──────────────────────────┤   │
        │     procedure#2          │ ←┐│
        │       object code        │  ││  procedure code
        ├──────────────────────────┤  ││  for procedure #2
        │         datasize         │ ←┼┼┐
        ├──────────────────────────┤  │││
        │          exitic          │  │││
        ├──────────────────────────┤  │││
        │      procedure code      │  │││
        ├──────────────────────────┤  │││
        │   reserved for future use│  │││
        │   reserved for future use│  │││
        │          realsize        │  │││
        │    constant pool pointer │ ─┘││
        │  byte sex indicator word │  ││   (恆為 1)
        │      (= 1)               │  ││
        │   8 character symbolic   │  ││
        │      name of segment     │  ││
        ├──────────────────────────┤  ││
        │  relocation list pointer │ ─┘│
        │   proc dictionary pointer│ ──┘
低位址(low)└──────────────────────────┘
```

（數值照抄 Figure 1；箭頭表示各指標欄位指向的位置。）（手冊 p.9）
probe
