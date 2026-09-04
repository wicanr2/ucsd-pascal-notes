# 低階 I/O：BIOS

出自《UCSD p-SYSTEM and UCSD PASCAL Version IV.0 Internal Architecture Guide》（SofTech Microsystems，1981 年 3 月）第 III.4-5 章，印刷頁 98–109。

> 延伸閱讀：[本層索引](README.md)｜[語言層與 RSP/IO](lowlevel-io-language-rsp.md)（本篇的前半）

## 裝置語意（續前篇）

### III.4.5.2.4 Printer:Status（手冊 p.98）

CONTROL word 指定方向的目前緩衝位元組數應放在第一個 status word 回傳。若印表機沒有任何自我檢查能力，回傳 0。

### III.4.5.3 Disk（手冊 p.98–100）

**邏輯區塊到實體磁區的對映**（III.4.5.3.1，手冊 p.98）：磁碟裝置可以是任何類型的磁碟機（軟碟或硬碟），實際的磁區配置無關緊要。系統一律以連續的 512 位元組邏輯區塊定址磁碟；磁碟 BIOS 的主要功能就是把邏輯區塊對映到實體磁區。磁區交錯（interleaving）演算法應針對硬體最佳化，系統對 BIOS 用什麼交錯方法不做任何假設——原文附註「（except that it works!）」。

**Bootstrap 位置**（III.4.5.3.1.1，手冊 p.98–99）：典型開機流程是硬體（通常是 ROM）bootstrap 載入並執行第一級軟體 bootstrap，後者再載入第二級軟體 bootstrap；第二級 bootstrap 載入直譯器與作業系統、做完必要的初始化後啟動系統。第一級軟體 bootstrap 必須放在硬體廠商預先決定的磁碟位置，因此系統對實體磁碟格式的要求必須在此保持彈性。第一級 bootstrap 區不得與系統維護的磁碟資料結構（主要是目錄與 bootstrap 本身）重疊。

- 慣例：每片磁碟的邏輯區塊 0 與 1（共 1024 位元組）保留給 bootstrap 碼——這是最方便的做法（手冊 p.98）。
- 若 1024 位元組不夠、或交錯格式不被硬體 bootstrap 接受，第一級 bootstrap 區必須放在「Pascal disk」之外，且邏輯區塊的對映方式要讓硬體定義的 bootstrap 區對 Pascal 系統而言不是可定址的邏輯區塊。該區仍可用 Physical Sector Mode 存取（見 III.2.3.1 節）（手冊 p.99）。
- Adaptable Systems 的 bootstrap 位置與開機機制細節在《Installation Guide》（手冊 p.99）。

**Physical Sector Mode**（III.4.5.3.1.2，手冊 p.99）：CONTROL word 的 bit 1（值 2）設定時，磁碟存取以 Physical Sector Mode 進行（III.2.3.1 節所述）。

**輸出要求**（III.4.5.3.2，手冊 p.99）：磁碟 BIOS 必須傳輸足以容納資料的實體磁區數。為簡化 `BYTESTOTRANSFER mod 512 ≠ 0`（區塊只寫一部分）的寫入，最後一個區塊的剩餘內容是 **undefined**——BIOS 可以把緩衝區裡殘留的垃圾順便寫滿整個磁區。追蹤有效資料位置（以邏輯區塊號與位元組數計）是語言層的責任。

手冊的例子（Diagram 4.0，手冊 p.99）：寫入 1174 位元組、起始邏輯區塊 72、資料位址 DATAAREA:

```
|               |               |     :          |
|   Block 72    |   Block 73    |   Block 74     |
|  (512 bytes)  |  (512 bytes)  | 150 : (362     |
|               |               | bytes: bytes)  |
|<----------------data----------->:<undefined>   |
|               |               |     :          |
 start of data area          end of data area   |
                                       end of last block
```

(1174 = 512 + 512 + 150；Block 74 寫了 150 位元組有效資料，其餘 362 位元組內容未定。)

**輸入要求**（III.4.5.3.3，手冊 p.100）：讀取時**不允許**覆寫指定資料區的末端，BIOS 有責任不多傳任何一個位元組。做法之一是把最後一個磁區先讀進緩衝區，再只搬要求的部分。

**初始化與控制**（III.4.5.3.4，手冊 p.100）：初始化應把磁碟裝置帶到可從任意磁軌或磁區讀寫的狀態。某些配簡單控制器的磁碟機可能需要把磁頭步進到 track 0，以便 BIOS 磁碟驅動程式記住目前磁軌。任何已緩衝的資料都會遺失。

**Status**（III.4.5.3.5，手冊 p.100）：磁碟的 status record 回傳：

| word | 內容 |
|---|---|
| 1 | CONTROL word 指定方向目前緩衝的位元組數（無檢查能力時設 0） |
| 2 | 每磁區位元組數 |
| 3 | 每磁軌磁區數 |
| 4 | 每片磁碟磁軌數 |

### III.4.5.4 Remote（手冊 p.100–101）

RS-232 串列線，供各種通訊用途。必須原樣傳輸 raw data，不得做任何更動；**傳輸位元組的全部 8 個位元都視為有效**。傳輸率通常是 9600 baud（手冊 p.100）。

- 輸出（III.4.5.4.1）：一次送一個位元組給 remote BIOS driver，8 位元全送（手冊 p.101）。
- 輸入（III.4.5.4.2）：可能時按 III.4.5.1.4.4 節建議的方式緩衝；8 個資料位元全部要回傳（手冊 p.101）。
- 初始化與控制（III.4.5.4.3）：帶到可讀寫的狀態（手冊 p.101）。
- Status（III.4.5.4.4）：第一個 status word 回傳 CONTROL word 指定方向的緩衝位元組數；無檢查能力時回傳 0（手冊 p.101）。

### III.4.5.5 User-Defined Devices（手冊 p.101）

讓使用者自行實作本文件未定義的裝置，實作完全留給使用者。唯一要求：結束時回傳 completion code；若 UNITNUMBER 未定義，回傳 code 2（「Illegal unit number」）。使用者裝置號碼應從 128 起編（見 III.2.1.1.1 節）。

## III.4.6 Special BIOS Calls（手冊 p.101–102）

這些功能與輸出入無關，但因為是機器配置相關的程式碼，統一放在 BIOS 裡供直譯器使用。與 BIOS 其他常式一樣，每個都要回傳 completion code（手冊 p.101）。

- **System Output**（III.4.6.1）：保留給未來擴充，目前應使系統 **HALT**。（注意：HALT 在少數實作上實際會造成 reboot。）（手冊 p.102）
- **System Input**（III.4.6.2）：同樣保留，應造成 HALT（手冊 p.102）。
- **System Initialization and Control**（III.4.6.3）：初始化時鐘（歸零）與中斷系統——如果要用到它們的話（手冊 p.102）。
- **System Status**（III.4.6.4）：status record 應回傳（手冊 p.102）：

| word | 內容 |
|---|---|
| 1 | 可存取連續 RAM 最後一個 **word** 的位址。例：8080 系統 64K 位元組 RAM，最後位元組位址是 `0xFFFF`，但最後 word 位址是 `0xFFFE` |
| 2 | 系統時鐘 32-bit word 的低位部分；無時鐘時必須為 0 |
| 3 | 系統時鐘 32-bit word 的高位部分；無時鐘時必須為 0 |

若使用時鐘，系統假設回傳的兩個 word 代表以 **1/60 秒**為單位的時間；時鐘驅動程式有責任維持最接近此時間的值。時鐘初始化時時間定義為 0。目前 CONTROL word 被忽略（手冊 p.102）。

## III.5.1 Appendix A:BIOS 呼叫序列摘要（手冊 p.103–104）

III.4.3 節呼叫慣例的總表。**所有 BIOS 呼叫都回傳 completion code。**處理器專屬協定見下一節。

| Entry Point | 參數 |
|---|---|
| CONSOLEREAD | 回傳單一資料位元組 |
| CONSOLEWRITE | 單一資料位元組 |
| CONSOLECTRL | BREAK vector、SYSCOM pointer |
| CONSOLESTAT | STATREC pointer、CONTROL word |
| PRINTERREAD | 回傳單一資料位元組 |
| PRINTERWRITE | 單一資料位元組 |
| PRINTERCTRL | （無） |
| PRINTERSTAT | STATREC pointer、CONTROL word |
| DISKREAD | block number、byte count、data area address、drive number、CONTROL word |
| DISKWRITE | （同 DISKREAD） |
| DISKCTRL | drive number |
| DISKSTAT | drive number、STATREC pointer、CONTROL word |
| REMOTEREAD | 回傳單一資料位元組 |
| REMOTEWRITE | 單一資料位元組 |
| REMOTECTRL | （無） |
| REMOTESTAT | STATREC pointer、CONTROL word |
| USERREAD | block number、byte count、data area address、device number、CONTROL word |
| USERWRITE | （同 USERREAD） |
| USERCTRL | device number |
| USERSTAT | device number、STATREC pointer、CONTROL word |
| SYSREAD | block number、byte count、data area address、device number、CONTROL word |
| SYSWRITE | （同 SYSREAD） |
| SYSCTRL | device number |
| SYSSTAT | STATREC pointer、CONTROL word |

(手冊 p.103–104；USER* 與 SYS* 在 p.104。)

## III.5.2 Appendix B：處理器專屬 BIOS 呼叫（手冊 p.105–109）

### III.5.2.1 8080/Z-80（手冊 p.105–106）

- **Entry points**：BIOS 各進入點是從 BIOS 碼空間起點算起的正偏移；這些位置應放一個 `JMP` 跳到 BIOS 內對應位址。
- **參數**：未指定用暫存器傳的參數一律推上堆疊；表中給的是距離 stack top 的偏移（堆疊向下長）。
- **Completion code**：回傳在暫存器 A。
- **呼叫序列**：RSP 用 `CALL` 呼叫 BIOS，所以回返位址在 `(SP),(SP)+1`。所有暫存器都可供 BIOS 使用；BIOS 返回 RSP 前應把堆疊清乾淨。

| Entry Point | 偏移 | 參數 |
|---|---|---|
| CONSOLEREAD | 0x00 | 資料位元組回傳在 Reg C |
| CONSOLEWRITE | 0x03 | 寫出位元組在 Reg C |
| CONSOLECTRL | 0x06 | BREAK vector at (SP)+2,(SP)+3;SYSCOM pointer at (SP)+4,(SP)+5 |
| CONSOLESTAT | 0x09 | STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| PRINTERREAD | 0x0C | 資料位元組回傳在 Reg C |
| PRINTERWRITE | 0x0F | 寫出位元組在 Reg C |
| PRINTERCTRL | 0x12 | （無） |
| PRINTERSTAT | 0x15 | STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| DISKREAD | 0x18 | block number at (SP)+2,(SP)+3;byte count at (SP)+4,(SP)+5;data area address at (SP)+6,(SP)+7;drive number at (SP)+8,(SP)+9;CONTROL word at (SP)+0xA,(SP)+0xB |
| DISKWRITE | 0x1B | （同 DISKREAD） |
| DISKCTRL | 0x1E | drive number in Reg C |
| DISKSTAT | 0x21 | drive number in Reg C;STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| REMOTEREAD | 0x24 | 資料位元組回傳在 Reg C |
| REMOTEWRITE | 0x27 | 寫出位元組在 Reg C |
| REMOTECTRL | 0x2A | （無） |
| REMOTESTAT | 0x2D | STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| USERREAD | 0x30 | block number at (SP)+2,(SP)+3;byte count at (SP)+4,(SP)+5;data area address at (SP)+6,(SP)+7;device number at (SP)+8,(SP)+9;CONTROL word at (SP)+0xA,(SP)+0xB |
| USERWRITE | 0x33 | （同 USERREAD） |
| USERCTRL | 0x36 | device number in Reg C |
| USERSTAT | 0x39 | device number in Reg C;STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| SYSREAD | 0x3C | block number at (SP)+2,(SP)+3;byte count at (SP)+4,(SP)+5;data area address at (SP)+6,(SP)+7;device number at (SP)+8,(SP)+9;CONTROL word at (SP)+0xA,(SP)+0xB |
| SYSWRITE | 0x3F | （同 SYSREAD） |
| SYSCTRL | 0x42 | device number in Reg C |
| SYSSTAT | 0x45 | device number in Reg C;STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |

### III.5.2.2 6500 系列（手冊 p.106–108）

- **Entry points**：同上，BIOS 碼空間起點算起的正偏移，放 `JMP`。
- **參數**：推上堆疊；表中偏移以 S 指到的位址為準（記作 `(S)`）。堆疊向下長，且 S 通常指向有效資料下方第一個可用位址。
- **Completion code**：回傳在暫存器 X。
- **呼叫序列**：RSP 用 `JSR` 呼叫，回返位址在 `(S)+1,(S)+2`。所有暫存器可用；BIOS 返回前清堆疊。

| Entry Point | 偏移 | 參數 |
|---|---|---|
| CONSOLEREAD | 0x00 | 資料位元組回傳在 Reg A |
| CONSOLEWRITE | 0x03 | 寫出位元組在 Reg A |
| CONSOLECTRL | 0x06 | BREAK vector at (S)+3,(S)+4;SYSCOM pointer at (S)+5,(S)+6 |
| CONSOLESTAT | 0x09 | STATREC pointer at (S)+3,(S)+4;CONTROL word at (S)+5,(S)+6 |
| PRINTERREAD | 0x0C | 資料位元組回傳在 Reg A |
| PRINTERWRITE | 0x0F | 寫出位元組在 Reg A |
| PRINTERCTRL | 0x12 | （無） |
| PRINTERSTAT | 0x15 | STATREC pointer at (S)+3,(S)+4;CONTROL word at (S)+5,(S)+6 |
| DISKREAD | 0x18 | block number at (S)+3,(S)+4;byte count at (S)+5,(S)+6;data area address at (S)+7,(S)+8;drive number at (S)+9,(S)+0xA;CONTROL word at (S)+0xB,(S)+0xC |
| DISKWRITE | 0x1B | （同 DISKREAD） |
| DISKCTRL | 0x1E | drive number in Reg A |
| DISKSTAT | 0x21 | drive number in Reg A;STATREC pointer at (S)+3,(S)+4;CONTROL word at (S)+5,(S)+6 |
| REMOTEREAD | 0x24 | 資料位元組回傳在 Reg A |
| REMOTEWRITE | 0x27 | 寫出位元組在 Reg A |
| REMOTECTRL | 0x2A | （無） |
| REMOTESTAT | 0x2D | STATREC pointer at (S)+3,(S)+4;CONTROL word at (S)+5,(S)+6 |
| USERREAD | 0x30 | block number at (S)+3,(S)+4;byte count at (S)+5,(S)+6;data area address at (S)+7,(S)+8;device number at (S)+9,(S)+0xA;CONTROL word at (S)+0xB,(S)+0xC |
| USERWRITE | 0x33 | （同 USERREAD） |
| USERCTRL | 0x36 | device number in Reg A |
| USERSTAT | 0x39 | device number in Reg A;STATREC pointer at (S)+3,(S)+4;CONTROL word at (S)+5,(S)+6 |
| SYSREAD | 0x3C | block number at (S)+3,(S)+4;byte count at (S)+5,(S)+6 |
| SYSWRITE | 0x3F | （同 SYSREAD） |
| SYSCTRL | 0x42 | device number in Reg A |
| SYSSTAT | 0x45 | device number in Reg A;STATREC pointer at (S)+3,(S)+4;CONTROL word at (S)+5,(S)+6 |

注意：6500 的進入點偏移與 8080/Z-80 完全相同，但堆疊參數的位移全部 +1(因為 S 指向有效資料下方一格，且回返位址佔 (S)+1，(S)+2)。另外 SYSREAD 的參數列在手冊 p.107 只印出 block number 與 byte count 兩行，data area address / device number / CONTROL word 印到 p.108 開頭（接續同 USERREAD 格式）。

### III.5.2.3 6809（手冊 p.108–109）

- **Entry points**：同上的正偏移，但手冊此處寫的是放一個「vector」到 BIOS 內對應位址。
- **參數**：推上堆疊，偏移以 SP 為準；堆疊向下長，SP 通常指向有效資料下方第一個可用位址。
- **Completion code**：回傳在暫存器 B。
- **呼叫序列**：RSP 用 `JSR` 呼叫，回返位址在 `(SP)+0,(SP)+1`。**U 與 Y 暫存器存有直譯器資訊，BIOS 返回 RSP 前必須保存/恢復**；其他暫存器可自由使用；BIOS 返回前清堆疊。

6809 的進入點偏移比 8080/6500 密（每格 2 位元組而非 3，因為放的是 vector 而非 `JMP`）：

| Entry Point | 偏移 | 參數 |
|---|---|---|
| CONSOLEREAD | 0x00 | 資料位元組回傳在 Reg A |
| CONSOLEWRITE | 0x02 | 寫出位元組在 Reg A |
| CONSOLECTRL | 0x04 | BREAK vector at (SP)+2,(SP)+3;SYSCOM pointer at (SP)+4,(SP)+5 |
| CONSOLESTAT | 0x06 | STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| PRINTERREAD | 0x08 | 資料位元組回傳在 Reg A |
| PRINTERWRITE | 0x0A | 寫出位元組在 Reg A |
| PRINTERCTRL | 0x0C | （無） |
| PRINTERSTAT | 0x0E | STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| DISKREAD | 0x10 | block number at (SP)+2,(SP)+3;byte count at (SP)+4,(SP)+5;data area address at (SP)+6,(SP)+7;drive number at (SP)+8,(SP)+9;CONTROL word at (SP)+0xA,(SP)+0xB |
| DISKWRITE | 0x12 | （同 DISKREAD） |
| DISKCTRL | 0x14 | drive number in Reg A |
| DISKSTAT | 0x16 | drive number in Reg A;STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| REMOTEREAD | 0x18 | 資料位元組回傳在 Reg A |
| REMOTEWRITE | 0x1A | 寫出位元組在 Reg A |
| REMOTECTRL | 0x1C | （無） |
| REMOTESTAT | 0x1E | STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| USERREAD | 0x20 | block number at (SP)+2,(SP)+3;byte count at (SP)+4,(SP)+5;data area address at (SP)+6,(SP)+7;device number at (SP)+8,(SP)+9;CONTROL word at (SP)+0xA,(SP)+0xB |
| USERWRITE | 0x22 | （同 USERREAD） |
| USERCTRL | 0x24 | device number in Reg A |
| USERSTAT | 0x26 | device number in Reg A;STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |
| SYSREAD | 0x28 | block number at (SP)+2,(SP)+3;byte count at (SP)+4,(SP)+5;data area address at (SP)+6,(SP)+7;device number at (SP)+8,(SP)+9;CONTROL word at (SP)+0xA,(SP)+0xB |
| SYSWRITE | 0x2A | （同 SYSREAD） |
| SYSCTRL | 0x2C | device number in Reg A |
| SYSSTAT | 0x2E | device number in Reg A;STATREC pointer at (SP)+2,(SP)+3;CONTROL word at (SP)+4,(SP)+5 |

## 與 IV.2.1 的關係

本篇內容出自 IV.0 手冊（1981 年 3 月版）。repo 研究的 SunDog 直譯器是 IV.2.1（68000）。以下幾點對逆向 IV.2.1 時要特別留意：

- **Appendix B 沒有 68000**。IV.0 手冊只列出 8080/Z-80、6500、6809 三個平台的 BIOS 呼叫協定。SunDog 的 Atari ST（68000）BIOS 介面——進入點表的形式、參數放哪裡、completion code 放哪個暫存器——在這份手冊裡沒有記載，要從 `SYSTEM.INTERP` 與其 BIOS 本體反推。手冊沒寫的差異一律標待查證，不能拿 6809 的表直接套。
- **概念層面的穩定度待查證**：completion code 制度、CONSOLE/DISK 等裝置的 entry point 名稱、STATREC/CONTROL word 結構在 IV.2.1 是否沿用，需以 IV.2.1 時代的文件（如 1983 年《Internal Architecture》，bitsavers 文件編號 1-140.41.A）或直譯器二進位驗證。
- 手冊 p.102 記載 System Status 回傳「最後一個 RAM word 的位址」與 32-bit 時鐘（1/60 秒為單位），這是直譯器取得記憶體上限與時間的標準管道；在 ST 上對應的機制為何，待查證。
