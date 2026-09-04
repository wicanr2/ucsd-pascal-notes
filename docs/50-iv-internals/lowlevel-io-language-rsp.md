# 低階 I/O：語言層與 RSP/IO

出自《UCSD p-SYSTEM and UCSD PASCAL Version IV.0 Internal Architecture Guide》
第三章（III. LOW-LEVEL I/O），印刷頁 71–97。
涵蓋 III.1（I/O subsystem 簡介）、III.2（語言層 Device I/O Routines）、
III.3（直譯器層 RSP/IO）、III.4 前半（BIOS 開頭：設計目標、completion codes、
各裝置呼叫參數、字元碼、console 與 printer 語意）。

結論先講：**IV.0 的 I/O 分成三層——語言層的 `UNIT*` intrinsics、直譯器裡
機器無關的 RSP/IO、機器相關的 BIOS**。語言層所有 I/O 最終都變成對 RSP/IO
的呼叫；RSP/IO 管的是 special character（DLE 空白壓縮、CR→CR+LF、EOF、
ALPHALOCK），BIOS 管的是實際硬體。這一章描述的是**同步 I/O**：
I/O 請求發出後，控制權要等操作完成才回到使用者程式（手冊 p.71）。

> 延伸閱讀：[本層索引](README.md)｜[p-machine 是什麼](../10-p-machine/what-is-a-p-machine.md)｜[BIOS](lowlevel-io-bios.md)（本篇的後半）

## III.1 I/O Subsystem 簡介（手冊 p.71–72）

直譯器除了模擬 p-machine，還必須含 native code 處理 time-critical 操作與
硬體相依部分；這些「不模擬 p-code」的碼合稱 Runtime Support Package（RSP），
其中負責 I/O 的部分叫 **RSP/IO**（手冊 p.71）。RSP/IO 是機器無關的，
除了 **BIOS（Basic Input/Output Subsystem）**；BIOS 隨硬體而變，
但 RSP/IO 與 BIOS 之間的介面是標準的（手冊 p.71）。

I/O 階層：使用者的 `READLN`、`WRITELN` 由編譯器與作業系統映射成 RSP 呼叫
（`UNITREAD`、`UNITWRITE`），RSP/IO 再呼叫 BIOS 控制實際裝置（手冊 p.71）。

**歷史脈絡（手冊 p.71–72）**：

- 第一個實作在 PDP-11，周邊介面已有標準，不需要 I/O 適配。
- 移植到 8080/Z80 時直接呼叫 CP/M BIOS，凡 CP/M 支援的硬體都能跑 p-System。
- 移植到 9900、6502、6800 時需要 CP/M BIOS 的等價物，p-System BIOS
  於是誕生並標準化（即本章描述的東西）。
- SofTech 後來又做了 **Adaptable System**：BIOS 定義沒解決 bootstrap 標準化，
  而且寫 BIOS 很難（幾乎要已有一台跑得動的 p-System）。**SBIOS（Simplified
  BIOS）** 是盡量簡單的硬體介面，由一段 "interface code" 接受 BIOS 式呼叫、
  轉發成 SBIOS 呼叫；RSP/IO 基本不變。SBIOS 詳述於《Installation Guide》。
- 有直譯器與 SBIOS interface code 原始碼的使用者可以改用 BIOS 級介面，
  效率可能更好（例如磁碟介面可用 DMA）。早期移植（如 PDP-11）不一定遵守
  這些慣例。

### Diagram 1.0 — I/O Subsystem Hierarchy（手冊 p.73）

```
"Language Level"      A USER
                         v
                    THE SYSTEM
"Interpreter Level"  ----------------
                     device no., data area address,
                     byte count [, block no., control word]
                         v
                    DEVICE I/O (parameter checking)
        +------------+---------+------+-------+----------------+
        v            v         v      v       v                v
     Console      Printer    Disk   Remote  User-defined Devices
   SPECIAL CHAR  SPECIAL CHAR      SPECIAL CHAR
   HANDLING      HANDLING          HANDLING
   (DLE's,CR's,  (DLE's,CR's,      (DLE's,CR's,
   EOF & alphalock) EOF & alphalock) EOF & alphalock)
     write read   single data   drive no.,   single   device no.,
   single data   byte           data area    data     data area
   byte                         address,     byte     address,
                                byte count,  byte     byte count,
                                logical              logical
                                block no.            block no.
"BIOS Level"   --------------------------------------------------
                 PRINTER     DISK        SERIAL LINE  MISCELLANEOUS
                 PRIMITIVES  MAPPER      PRIMITIVES   DEVICE DRIVERS
                             (Map logical
                             blocks into           TYPE-AHEAD QUEUE
                             track & sector)            v
                                v                SPECIAL CHAR HANDLING
                          DISK PRIMITIVES          (start/stop, flush, break)
                                v                       v
                        SCREEN PRIMITIVES   KEYBOARD PRIMITIVES
```

注意 special character 處理出現在兩處：interpreter 層對 console/printer/remote
做 DLE/CR/EOF/alphalock；BIOS 層（keyboard 下方）做 start/stop、flush、break。

## III.2 語言層：Device I/O Routines（手冊 p.74–80）

所有語言層 I/O 請求最終由編譯器與作業系統映射成對一組 intrinsic 的呼叫，
稱為 **Device I/O Routines**。程式設計者可直接呼叫它們，也可用語言的
標準 I/O 語法。**這些常式不是 Pascal 寫的，而是組成 RSP/IO 的 native code
procedures**（手冊 p.74）。本章假設 device I/O 層（含）以下都用組語實作；
若宿主處理器的 native language 就是 p-code，則可能用 Pascal 寫（手冊 p.74）。

RSP/IO 常式是作業系統 unit **KERNEL** 的常式；KERNEL 對每個 compilation
unit 都是 **segment 1**。常式的實際碼也可能放在直譯器裡而不是 KERNEL
（手冊 p.74）。

### III.2.1 呼叫 RSP/IO（手冊 p.74–75）

對直接呼叫者來說，這些常式看起來像一般 intrinsic。若真的用 Pascal 宣告
（允許 optional 參數與可變長度陣列這些不合法寫法），形式如下：

```pascal
PROCEDURE UNITREAD( UNITNUMBER : INTEGER;
    VAR DATAAREA : PACKED ARRAY [0..BYTESTOTRANSFER-1] OF 0..255;
    BYTESTOTRANSFER : INTEGER
    [; LOGICALBLOCK : INTEGER]
    [; CONTROL : INTEGER] );

PROCEDURE UNITWRITE( <same as for UNITREAD> );

FUNCTION UNITBUSY( UNITNUMBER : INTEGER ) : BOOLEAN;

PROCEDURE UNITWAIT( UNITNUMBER : INTEGER );

PROCEDURE UNITCLEAR( UNITNUMBER : INTEGER );

PROCEDURE UNITSTATUS( UNITNUMBER : INTEGER;
    VAR STATUSWORDS : ARRAY [0..29] OF INTEGER;
    CONTROL : INTEGER );
```

手冊強調：**系統裡沒有這些宣告**，它們只是用來模型化 native code RSP/IO
常式的參數傳遞（手冊 p.75）。

### III.2.1.1 Devices and Device Numbers（Diagram 2.0，手冊 p.75）

`UNITNUMBER` 決定作用於哪台實體裝置；同一程序可處理任何實體 unit
（device-transparent）。

| Unitnumber | Volume name |
|---|---|
| 0 | （系統保留） |
| 1 | CONSOLE |
| 2 | SYSTEM |
| 3 | （系統保留） |
| 4 | disk0 |
| 5 | disk1 |
| 6 | PRINTER |
| 7 | REMIN |
| 8 | REMOUT |
| 9 | disk2 |
| 10 | disk3 |
| 11 | disk4 |
| 12 | disk5 |
| 13–127 | （保留給未來擴充） |

**大於 127 的裝置號保留給 user-defined devices**，沒有預設名稱，
但一樣可以用 `UNIT*` intrinsics 存取（手冊 p.75）。

### III.2.1.2 CONTROL 參數（手冊 p.76–77）

`UNITREAD`/`UNITWRITE`/`UNITSTATUS` 的 `CONTROL` 是一個 word，
用來把 I/O 請求的處理方式傳給 RSP/IO 與 BIOS。

Diagram 2.1 — `UNITREAD`/`UNITWRITE` 的 CONTROL word（手冊 p.76）：

| 位元 | 名稱 | 值 | 意義 |
|---|---|---|---|
| 0 | ASYNC | 1 | 1 = 非同步 I/O；0 = 同步。**手冊說此位元應恆為 0** |
| 1 | PHYSSECT | 2 | 1 = 磁碟用 Physical Sector Mode；0 = Logical Block Mode（見 III.2.3.1） |
| 2 | NOSPEC | 4 | 1 = 關掉 special character 處理；0 = 開（見 III.3.2.1、III.3.2.2） |
| 3 | NOCRLF | 8 | 1 = 非磁碟 I/O 時 CR 後不補 LF；0 = CR 後補 LF（見 III.3.2.1.2、III.3.2.1.3） |
| 4–12 | （保留） | | 未來擴充 |
| 13–15 | USER DEFINED | | 使用者自定功能 |

所有位元預設為 0。

Diagram 2.2 — `UNITSTATUS` 的 CONTROL word（手冊 p.77）：

| 位元 | 名稱 | 值 | 意義 |
|---|---|---|---|
| 0 | IODIR | 1 | 1 = 回傳 input channel 狀態；0 = output channel |
| 1–12 | （保留） | | 未來擴充 |
| 13–15 | USER DEFINED | | 使用者自定功能 |

### III.2.2 IORESULT 與 Completion Codes（手冊 p.77–78）

I/O 異常時程式可用 intrinsic `IORESULT` 查最近一次 I/O 的狀態。
每次呼叫 `UNITREAD`、`UNITWRITE`、`UNITCLEAR`、`UNITSTATUS` 都會在
**SYSCOM** 資料區（SYStem COMmunication area，慣例上是作業系統與直譯器
都能直接存取的唯一資料空間）設一個 completion code；程式用 `IORESULT` 讀它
（手冊 p.77）。

Diagram 2.3 — I/O Completion Codes（手冊 p.78）：

| Code | 意義 |
|---|---|
| 0 | No error |
| 1 | Bad block, CRC error (parity) |
| 2 | Bad device number |
| 3 | Illegal I/O request |
| 4 | Data-com timeout |
| 5 | Volume is no longer on-line |
| 6 | File is no longer in directory |
| 7 | Illegal file name |
| 8 | No room; insufficient space on disk |
| 9 | No such volume on-line |
| 10 | No such filename in directory |
| 11 | Duplicate file |
| 12 | Not closed; attempt to open an open file |
| 13 | Not open; attempt to access a closed file |
| 14 | Bad format; error reading real or integer |
| 15 | Ring Buffer Overflow |
| 16 | Write attempt to protected disk |
| 17 | Illegal block number |
| 18 | Illegal buffer address |
| 19–127 | 保留給未來擴充 |

128–255 保留給非預定義、裝置相依的錯誤。

### III.2.3 Logical Disk Structure（手冊 p.78–80）

系統把磁碟看成 **zero-based、512-byte logical blocks 的線性陣列**，不論
實體格式如何。實體配置單位是 sector，各機型差異很大；**把 logical block
映射到實體 sector 是 BIOS 的責任**（手冊 p.78）。

**III.2.3.1 Physical Sector Addressing Mode（手冊 p.79）**：CONTROL word 的
PHYSSECT bit（bit 1，值 2）設起來時，對磁碟 unit 的 `UNITREAD`/`UNITWRITE`
改用實體 sector 模式：

1. `LOGICALBLOCK` 被 BIOS 解讀為**實體 sector number（PSN）**。
   （未來可能變成 PSN 的低 15 或 16 位元。）
2. `BYTESTOTRANSFER` 必須為 0。（未來可能變成 PSN 的高 16 位元。）

**III.2.3.1.1 Physical Sector Numbers（手冊 p.79–80）**：磁碟視為 track 的
陣列、每個 track 是 sector 的陣列（track 編號 zero-based，sector 編號從 1 起）：

```pascal
type
BYTE   = 0..255;
SECTOR = array [0..(BYTESperSECTOR-1)] of BYTE;
TRACK  = array [1..SECTORSperTRACK] of SECTOR;
DISK   = array [0..(TRACKSperDISK-1)] of TRACK;

(* 換成線性表示: *)
DISK = array [0..(TRACKSperDISK*SECTORSperTRACK)-1] of SECTOR;
```

PSN 與 track/sector 的換算（手冊 p.80）：

```pascal
PSN          = (TRACKNUMBER*SECTORSperTRACK) + SECTORNUMBER-1;
TRACKNUMBER  = PSN div SECTORSperTRACK;
SECTORNUMBER = (PSN mod SECTORSperTRACK) + 1;
```

**III.2.3.1.2 Physical Sector Size（手冊 p.80）**：任何 sector 大小都可容納；
Physical Sector Mode 的 I/O 固定傳一整個 sector，程式設計者要保證 data area
至少容得下一個 sector。用 physical sector mode 寫的程式**不保證可攜**到
不同的磁碟硬體。

## III.3 直譯器層：RSP/IO（手冊 p.81–87）

RSP/IO 的設計是 processor-、hardware-independent 的，但以 native code 實現；
最終產品是 processor-specific 的，但仍與實際使用哪些周邊無關（手冊 p.81）。

### III.3.1 Calling Mechanisms（手冊 p.81–84）

本節讓 RSP 實作者知道：呼叫時怎麼從 stack 上 pop 參數、返回時 stack 應該
長什麼樣子。

#### III.3.1.1 UNITREAD / UNITWRITE（手冊 p.81–82）

參數說明：

- `UNITNUMBER`：裝置號，見上。
- `DATAAREA`：使用者緩衝區。宣告成 VAR 表示傳進來的是**指標**，而且是
  一個 **address couple:word base + byte offset**。byte addressing 的機器
  直接相加；word addressing 的機器從 base 以 byte 為單位往高位址索引。
  一般情況下 data area 起址不必在 word boundary 上；**但磁碟 unit 例外——
  必須在 word boundary**，Pascal 程式不能把奇數索引（如 `A[3]`）的實參
  拿去對磁碟傳輸。理由是避免把磁碟資料限制成逐 byte 搬運（手冊 p.81–82）。
- `BYTESTOTRANSFER`：要搬的 byte 數。
- `LOGICALBLOCK`、`CONTROL`：可省略，省略時編譯器給預設值 0。
  `LOGICALBLOCK` 只對磁碟有意義，指定要存取的 Pascal logical block
  （手冊 p.82）。

Diagram 3.0 — 進入 `UNITREAD`/`UNITWRITE` 時的堆疊狀態（每格一個 16-bit
量，堆疊往下長；手冊 p.82）：

```
++++  |////////////////|  <- (返回時 SP 指到這裡)
      |----------------|
      |  Unit Number   |
      |----------------|
      |   Word Base    |
      |----------------|
      |  Byte Offset   |
      |----------------|
      |   Byte Count   |
      |----------------|
      |  Block Number  |
      |----------------|
      |    Control     |  <- SP
----  |----------------|
```

與一般 Pascal 程序一樣，這些 RSP 常式返回前會把自己的參數 pop 掉。

#### III.3.1.2 UNITBUSY（手冊 p.83）

只在非同步環境才有意義；**本同步規格下恆回傳 FALSE（0）**。堆疊：
呼叫前頂端是 `Unit Number`，返回後頂端是 `False`（Diagram 3.1）。

#### III.3.1.3 UNITWAIT（手冊 p.83）

同樣只在非同步環境有用；同步系統裡沒有任何 unit 會有 pending 的 I/O，
所以**基本上是 no-op**。呼叫時頂端一個參數，返回前 pop 掉（Diagram 3.2）。

#### III.3.1.4 UNITCLEAR（手冊 p.84）

把指定 unit 還原到「initial」狀態。RSP 層的意思是清掉與該 unit 相關的
state flags（見 III.3.2.1.1、III.3.2.2.2）；各裝置在 BIOS 層的 initial
狀態定義在 III.4.5。堆疊格式與 `UNITWAIT` 相同。

#### III.3.1.5 UNITSTATUS（手冊 p.84）

取得裝置相依資訊。傳入 status record 的指標(長度上限 **30 個 word**)，
狀態字循序存入；**使用者自定字從 word 29 往 word 0 方向配置**，系統使用
record 前段的字。另有一個 CONTROL word。

Diagram 3.3 — 進入 `UNITSTATUS` 時的堆疊（手冊 p.84）：

```
++++  |////////////////|  <- (返回時 SP 指到這裡)
      |----------------|
      |  Unit Number   |
      |----------------|
      |  Status Record |
      |    Pointer     |
      |----------------|
      |    Control     |  <- SP
----  |----------------|
```

### III.3.2 Semantics（手冊 p.85–87）

RSP/IO 的主要工作是管理對 BIOS 的呼叫，其次是處理一些 special function。
**Appendix A 有一份 RSP/IO 的 Pascal 實現，是語意的最精確參考**（手冊 p.85）。

#### 輸出的 special character 處理（手冊 p.85）

對 printer、console、remote 的輸出必須處理 Blank Compression Code 與
Carriage Return。

**III.3.2.1.1 DLE 空白壓縮碼（手冊 p.85）**：textfile 行首可有兩位元組的
空白壓縮碼。第一位元組是 ASCII **DLE（十進位 16）**，表示下一個位元組是
「excess-32」的空白數，即 `<空白數> + 32`；RSP/IO 要把它解開、送出那麼多個
空白。減 32 後為負（顯然是錯誤）時當 0 處理。因為裝置可能切換，
blank-count byte 不一定是下一個進來的 byte，**每個裝置要維護一個
「正在處理 DLE」旗標**。DLE 與 blank-count byte 通常不送給裝置
（見 III.3.2.3）。

**III.3.2.1.2 CR/LF（手冊 p.85）**：textfile 行尾是 ASCII **CR（十進位 13）**，
定義為 "New Line" = carriage return + line feed。所以 RSP/IO 每送出一個 CR
之後要補送 ASCII **LF（十進位 10）**。

**III.3.2.1.3 NOCRLF（手冊 p.85）**：CONTROL 的 bit 3（值 8）設起來時，
關掉 CR 的特殊處理：不自動補 LF，CR 像一般字元一樣送出。

#### 輸入的 special character 處理（手冊 p.86）

從 console、printer、remote 收到的字元有幾個要特殊處理；**除了兩個以外
都由 BIOS 處理**，RSP/IO 只管 **EOF** 與 **ALPHALOCK**。

**III.3.2.2.1 EOF（手冊 p.86）**：EOF 不是固定 ASCII 碼，而是 **"soft
character"**——確切字元碼可由 Pascal 使用者在系統執行中改變（見 III.4.4）。
EOF 字元存在 **SYSCOM** 裡，RSP/IO 必須去查。在輸入流中遇到 EOF 時，
動作依裝置而異：

- **UNIT 1（CONSOLE:）**：從目前位置起，使用者 buffer 其餘部分填 null（0）。
- **UNIT 2（SYSTEM:）、printer、remote**：EOF 字元本身放進 buffer。
- 所有情況：不再傳其他字元，立即返回。

**III.3.2.2.2 ALPHALOCK（手冊 p.86）**：收到 ALPHALOCK 字元表示之後所有
小寫字母（'a'–'z'）轉成大寫；再收到一個 ALPHALOCK 則回到不轉換的預設模式。
與 DLE 一樣，**每個裝置要維護一個 ALPHALOCK 狀態旗標**；ALPHALOCK 字元
通常不放進 buffer（見 III.3.2.3）。

**III.3.2.2.3 BIOS 管的字元（手冊 p.86）**：**BREAK、START/STOP、FLUSH**
只用於 console 輸入（printer/remote 不用），由 BIOS 處理，見 III.4.5.1.4。

**III.3.2.3 NOSPEC（手冊 p.87）**：CONTROL 的 bit 2（值 4）設起來時，關掉
上述 DLE、EOF、ALPHALOCK 的偵測，這些字元照一般字元傳送。**BIOS 的功能
不受影響**。

## III.4 機器層：BIOS（開頭，手冊 p.88–97）

BIOS 負責實際的裝置存取，設計與實作都依特定處理器與 I/O 組態而定。
一般架構是 RSP/IO 經由 **vector** 呼叫 BIOS 的 read、write、initialize/
control、status 子常式；確切的 vector 方案與參數傳遞方式要逐處理器決定，
已做好的安排例示於 III.6.2（手冊 p.88）。

### III.4.1 設計目標（手冊 p.88）

BIOS 的速度跟它管的（慢速）裝置相比無關緊要；周邊常換，而且 BIOS 常駐
主記憶體、每一 byte 都是使用者少一 byte。所以主要設計目標（假設正確性
沒問題）是 **（1） 精簡 （2） 清晰**。BIOS 應該可以放進 ROM，也需要一些
RAM；它參照的位址應該用 equate 寫，方便改 I/O port 或記憶體配置時
重組譯。

### III.4.2 Completion Codes（手冊 p.88–89）

BIOS 的所有 read、write、init/control、status 呼叫都必須回傳一個 byte 的
completion code（同 III.2.2）。多數標準碼與 BIOS 無關（那是作業系統回報
檔案錯誤用的）；**BIOS 可以回報的標準錯誤**是：

| Code | 意義 |
|---|---|
| 0 | No error |
| 1 | CRC error |
| 2 | Illegal device number |
| 3 | Illegal operation on device |
| 4 | Undefined hardware error |
| 9 | Device not on line |
| 15 | Ring Buffer Overflow |
| 16 | Write protect; write attempt to protected disk |
| 17 | Illegal block number |
| 18 | Illegal buffer address |

其他錯誤都算硬體相依，BIOS 應回 128–255 範圍的碼，選碼由 BIOS 作者自訂
（手冊 p.89）。

另外兩條規則（手冊 p.89）：

- **預定義但未實作的裝置**，被初始化或使用時必須回 completion code 9
  （"Device not on line"）。
- **未實作的 user-defined 裝置**，被存取時應回 completion code 2
  （"Illegal device number"）。

### III.4.3 Calling Mechanisms（手冊 p.89–90）

每個裝置有四種 BIOS 呼叫：**READ、WRITE、CONTROL（CTRL）、STATUS**；
所有呼叫都要回 completion-code byte。呼叫需求摘要見 III.6.1。

| 裝置 | READ/WRITE 參數 | STATUS 參數 | INIT/CONTROL 參數 |
|---|---|---|---|
| Console（p.89） | 要傳的資料 byte | CONTROL word + status record 指標 | SYSCOM 基底指標 + break-handler 常式指標 |
| Printer（p.89） | 資料 byte | CONTROL word + status record 指標 | 無 |
| Disk（p.90） | （1） 起始 logical block （2） byte 數（正 16-bit，0–32K-1）（3） data area 位址 （4） drive number(0..n-1，目前假設 n=6)(5) CONTROL | CONTROL word + status record 指標 | drive number |
| Remote（p.90） | 資料 byte | CONTROL word + status record 指標 | 無 |
| User-defined（p.90） | （1） 起始 logical block （2） byte 數（0–32K-1）（3） data area 位址 （4） device number(= UNITNUMBER)(5) CONTROL | CONTROL word + device number + status record 指標 | device number |

BIOS 的 native code 可以忽略部分參數；user-defined 裝置由 device handler
自行從 device number 解出實體裝置（手冊 p.90）。

### III.4.4 Character Codes（手冊 p.91）

系統假設 printer 與 console 支援可印 ASCII 字元與少數標準控制碼
（CR、LF、SP、NUL、BEL）。其餘控制碼（游標定位、清螢幕等）是
**soft characters**，使用者可用 SETUP 公用程式修改以配合硬體。
soft characters 與 SETUP 的其他設定存在 **SYSTEM.MISCINFO** 檔，
系統開機或重新初始化時讀入全域資料區 **SYSCOM**。

把硬體相依資訊放在這麼高的層次，是因為終端機控制碼差異大、使用者常換
終端機，必須能**不重建 BIOS 就換終端機**。核心問題是「邏輯控制符號 →
硬體控制碼」的映射：例如預先宣告的 `CURSORBACK`，系統不能讓編譯器產生
固定碼再叫 BIOS 翻譯（那每換一種終端機就要一份新 BIOS）；採用的做法是
**由 BIOS 為目前線上的終端機送出正確的碼**，細節另述。

其他規定（手冊 p.91）：

- 系統對高位元不做假設，整個 byte 原樣傳送；用 7-bit ASCII 時高位元為 0。
- **BIOS 對從 console 收到的標準字元必須回高位元為 0 的 ASCII**；其他裝置
  無此要求。
- RSP 會把大小寫字元都送給 BIOS；**若裝置只能處理大寫，BIOS 要把小寫
  映射成大寫**。

### III.4.5 Semantics — Console（手冊 p.92–96）

以下假設 console 是 CRT 終端機，打字機型裝置也可當 console。

**III.4.5.1.1 輸出必要條件（手冊 p.92）**：

| 字元 | 碼 | 要求行為 |
|---|---|---|
| CR | 0x0D | 游標移到本行開頭（第 0 行） |
| LF | 0x0A | 游標下移一行、行位置不變；非末行時畫面內容不變。在末行收到 LF：游標不動、畫面上捲一行、底行清除 |
| BEL | 0x07 | 有聲音裝置就響；沒有就什麼都不做（延遲時間不拘） |
| SP | 0x20 | 在游標處寫空白（蓋掉原內容）並前進一行。已在行尾時游標位置無定義，建議保持不動；在末行末行時游標與畫面狀態都無定義（可能捲也可能不捲），建議游標不動、畫面不捲 |
| NUL | 0x00 | 延遲一個字元的輸出時間；console 狀態不變 |
| 其他可印字元 | | 同 SP，但寫出該字元 |

送上述以外的不可印字元，效果**無定義**（各終端機不同）。

**III.4.5.1.2 輸出選項（手冊 p.93）**：下列游標/螢幕功能有則佳，
沒有也不影響系統主要功能。對應的控制字元**不指定（soft characters）**；
若接的是獨立 ASCII 終端機，這些功能可由終端機本身提供，BIOS 只要轉送
控制字元：

- **Reverse Line Feed**：游標上移一行，行位置與畫面內容不變；已在頂行則
  無定義，可以的話畫面反向捲動，否則保持原狀。
- **Non-destructive Forward/Backward Space**：游標前後移動不改畫面內容；
  移出行界則無定義，建議保持不動。
- **Cursor HOME**：游標移到左上角，畫面內容不變。
- **Cursor X,Y Positioning**：游標移到絕對行列位置，畫面內容不變；移到
  不存在的位置則無定義。
- **Erase to End of Screen**：從游標清到螢幕尾，游標不動、其他內容不變。
- **Erase to End of Line**：從游標清到行尾，游標不動、其他內容不變。

**III.4.5.1.3 輸入必要條件（手冊 p.94）**：console 輸入**不要由 BIOS
echo 到螢幕**——echo 是 RSP/IO 的事。ASCII 鍵產生 0–127 的 8-bit 碼；
非 ASCII 鍵（如功能鍵）想要的話可產生 128–255 的碼。

**III.4.5.1.4 輸入選項（手冊 p.94–95）**：建議 console 輸入 BIOS 負責：

- **START/STOP**（soft character）：控制 console 輸出。收到後暫停輸出，
  直到 （a） 再收到 START/STOP、（b） 收到 FLUSH、（c） console BIOS 重新初始化、
  （d） 收到 BREAK。暫停與恢復完全在 BIOS 內做，不通知 RSP；**START/STOP
  字元絕不回給 RSP**；暫停期間鍵盤輸入的 queueing（若有）應繼續。
  用途：按住跑太快的輸出（9600 baud 捲動的文字檔、等印表機上線）。
- **FLUSH**（soft character；手冊此節編號誤植為 IV.1.4.5.1.4.2）：收到後
  console 輸出 BIOS **丟棄所有輸出字元**（不顯示），直到 （a） 再按 FLUSH、
  （b） console BIOS 被要求輸入、（c） 重新初始化、（d） 收到 BREAK。**FLUSH
  字元絕不回給 RSP**。START/STOP 暫停中收到 FLUSH：取消暫停、FLUSH 生效。
  只適用於 console 輸出。
- **BREAK**（soft character，手冊 p.95）：收到後 console 輸入 BIOS 應立即把
  控制權交給一個**特殊的直譯器常式**，其 vector 在 console 初始化時傳入；
  BREAK 常式執行完 BIOS 繼續原狀。**BREAK 常式負責通知直譯器：在解譯
  下一個 p-code 之前先執行 BREAK**。BREAK 字元絕不回給 RSP；收到 BREAK
  應終止任何 pending 的 START/STOP 或 FLUSH。
- **Type-Ahead（手冊 p.95）**：沒有 pending 讀取請求時收到的非特殊字元應
  排入佇列，下一次讀取從佇列取走最早的字元。超過佇列上限的字元丟棄，
  佇列本身保持完整。建議佇列至少約 20 字元；佇列滿後每按一鍵最好響鈴。

**III.4.5.1.5 初始化與控制（手冊 p.95–96）**：console BIOS 的 init/control
部分負責（以及 BIOS 實作者認為合適的其他事）：

- **Soft character 辨識**：系統把 START/STOP、FLUSH、BREAK 三個 soft
  character 存在 **SYSCOM**。console 初始化的參數之一是 SYSCOM 起址指標，
  三個字元相對該指標的 byte 偏移（十進位/十六進位/八進位）：

  | 字元 | 十進位 | 十六進位 | 八進位 |
  |---|---|---|---|
  | FLUSH | 83 | 0x53 | 123 |
  | BREAK | 84 | 0x54 | 124 |
  | STOP/START | 85 | 0x55 | 125 |

- **BREAK vector**：另一個初始化參數是直譯器 BREAK 處理常式的位址；
  console 初始化碼要經由自己的私有資料區建立指向該位址的 vector，
  收到 BREAK 字元時呼叫它。
- **Flags**：初始化應清掉 START/STOP 與 FLUSH 旗標（或做任何恢復正常
  所需的事）。
- **Type-ahead queue**：初始化應丟棄佇列中等待的字元。

**III.4.5.1.6 Status（手冊 p.96）**：CONTROL word 的 bit 0（值 1）決定
狀態請求的方向（見 III.2.1.2）。status record 的第一個 word 回傳該方向
目前排隊的字元數。有緩衝的話就是緩衝區內字元數；沒有緩衝時，output
status 恆回 0，input status 在有字元可讀時回 1、否則回 0。

### III.4.5.2 Printer（手冊 p.97）

printer 的設計想像是 line printer 或其他 hardcopy 裝置；實務上任何 ASCII
顯示裝置都可用。

**輸出必要條件（手冊 p.97）**：RSP/IO 不整行緩衝，**一次只送一個字元**給
printer BIOS。若印表機本身必須整行緩衝再一次印出，那是 BIOS 的事，且
BIOS 要認得行尾。EOLN 由特定字元表示：

- **CR（0x0D）**：印出該行並回車到第一行。**不應自動換行**。
- **LF（0x0A）**：正常操作下 RSP/IO 只會在 CR 之後立刻送 LF。硬體允許的話
  就做單純換行（不回車）；若機器只能做完整的 "new line"（回車+換行），
  就在 LF 時做，CR 什麼都不做。
- **FF（0x0C）**：可以的話跳頁到 top-of-form 並回車；沒此功能可用
  "new line"（回車+換行）代替。

**輸入必要條件（手冊 p.97）**：printer 輸入沒有嚴格要求。裝置若能傳資料，
printer 輸入 BIOS 應回傳全部 8 個資料位元；不能的話就不准輸入，
回 completion code 3（"Illegal operation on device"）。

**初始化與控制（手冊 p.97）**：初始化應讓印表機準備好從空行開頭印起，
可做一個 "new line"（回車+換行）。已緩衝未印的字元丟棄。初始化**不需要
每次跳頁**。

## 與 IV.2.1 的關係

本章出自 IV.0 手冊（1981），而 repo 研究的 SunDog 直譯器是 IV.2.1（1983）。
以下幾點供對照時留意，**手冊未記載 IV.2.1 是否或如何改動，實際差異待查證**：

- RSP/IO 常式在 IV.0 以 KERNEL（segment 1）的常式形式被存取，實際碼
  「可能放在直譯器裡而不是 KERNEL」（手冊 p.74）。在 SunDog 的
  `SYSTEM.INTERP` 裡找 `UNITREAD`/`UNITWRITE` 等的實作時，應預期它們是
  直譯器內的 native 常式，經某種呼叫機制進入（待查證：IV.2.1 是否以
  特定 p-code 或 CSP 之類的機制呼叫 RSP/IO，本手冊此章沒有寫呼叫端
  的 p-code 長什麼樣子）。
- completion code 表（Diagram 2.3）與 BIOS 可回報的子表（III.4.2）是
  解讀 IV.2.1 直譯器 I/O 錯誤路徑的好起點，但編號是否在 IV.2.1 沿用
  待查證。
- SYSCOM 的 soft character 偏移（FLUSH 83 / BREAK 84 / STOP/START 85）
  是 IV.0 的定值；IV.2.1 的 SYSCOM 布局待查證。
- 磁碟 logical block 固定 512 byte、PSN 換算式與 PHYSSECT 模式，
  對逆向磁碟映像的區塊定址有直接幫助；IV.2.1 是否相同待查證。
