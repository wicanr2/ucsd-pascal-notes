# 作業系統層：The Operating System 與 Program Execution

> 出自《UCSD p-SYSTEM and UCSD PASCAL Version IV.0 Internal Architecture Guide》
> （SofTech Microsystems，1981 年 3 月）第四章（pp. 111–131）與第五章（p. 133），
> 對應掃描檔 pg-117.png – pg-140.png。
> 注意：這份掃描的**印刷頁碼 = PDF 頁碼 − 6**（例如印刷頁 111 是 pg-117.png）。

本章講的是 p-System 作業系統本身的內部結構：它是一群 Pascal UNIT 的集合，
管 Heap、Codepool、fault、concurrency、檔案 I/O 與螢幕。
第五章則講一個程式從命令列到執行的過程（GETCMD → ASSOCIATE → BUILDENV）。

> 延伸閱讀：[本層索引](README.md)｜[Codefile 組織與執行環境](codefile-and-environments.md)（SIB 與 E_Rec）

## IV.1 Organization（手冊 p. 111–112）

IV.0 作業系統是一群 Pascal UNIT 的集合；分 UNIT 的考量是功能分組、空間與
語言限制、以及與系統其他部分的程式碼共享（手冊 p. 111）。部分 UNIT（如
SCREENOPS）也開放給使用者程式用。

作業系統 UNIT 全表（手冊 p. 111–112）：

| Unit 名稱 | 功能 |
|---|---|
| HEAPOPS / EXTRAHEAP / PERMHEAP | Heap operators |
| SCREENOPS | Screen control |
| FILEOPS | File and Directory operations |
| PASCALIO / EXTRAIO / SOFTOPS | File-level I/O |
| SMALLCOMMAND / COMMANDIO | I/O redirection and chaining |
| STRINGOPS | String intrinsics |
| OSUTIL | Conversion utilities |
| CONCURRENCY | Concurrency |
| REALOPS | Floating Point Functions and Real Number I/O |
| LONGOPS | Long Integer operations |
| GOTOXY | Screen cursor control（可由使用者提供） |
| KERNEL | 作業系統不可 swap 的核心設施（永遠常駐主記憶體） |
| GETCMD / USERPROG / INITIALIZE / PRINTERROR | KERNEL 的附屬 segment（可 swap） |

KERNEL 含維護 codepool、處理 fault、讀取 segment 所需的常駐碼，另有四個可
swap 的附屬 segment（手冊 p. 112）：

- **GETCMD**：處理主命令層的使用者輸入，建立使用者程式的 runtime environment。
- **USERPROG**：使用者程式的保留 segment 槽；bootstrap 時裡面是建立作業系統
  初始 runtime environment 的 Pascal 層程式碼。
- **INITIALIZE**：系統開機或重新初始化時被呼叫；讀 `SYSTEM.MISCINFO`、
  定位系統 codefile、建立裝置表。
- **PRINTERROR**：印 runtime 錯誤訊息。

作業系統各 UNIT 分開編譯，再用工具 LIBRARY 綁成單一 codefile
`SYSTEM.PASCAL`。因 bootstrap 限制，**KERNEL 必須在 segment-slot 0、
USERPROG 必須在 slot 15**，其餘 UNIT 在 `SYSTEM.PASCAL` 內的位置無限制
（手冊 p. 112）。

## IV.2 P-Machine Support

### IV.2.1 The Heap（手冊 p. 113–117）

Heap 是低記憶體的一塊區域，用來配置動態變數；其上界取決於 Stack 與
Codepool 的大小。Heap 與 Codepool 之間的區域暫時可用——Stack fault 與
segment fault 可能改變這塊區域的大小；Heap fault 則是 Heap 運算子用來
要求更多空間的機制（手冊 p. 113）。

**MARK / RELEASE**（p. 113）：`MARK` 記下 Heap 目前頂端位置；`RELEASE` 把
Heap 砍回對應的 mark。MARK 與 RELEASE 之間配置的變數都會被移除，但
PERMNEW 配置的例外。兩者可巢狀，但必須正確配對。

**NEW / VARNEW**（p. 113）：在「最頂端」mark 之上配置變數。`NEW(P)` 依 P
所指型別 T 的字數配置；若 T 是含 variant 的 record，配最大 variant 的空間
（Pascal 呼叫可指定 variant）。`VARNEW(P,NWords)` 配 NWords 個字（典型是
陣列）；它是函式，回傳實際配到的字數——應等於 NWords；是 0 表示空間不足；
其他數字表示出錯。

**DISPOSE / VARDISPOSE**（p. 114）：分別釋放 NEW 與 VARNEW 配的空間，之後
P 被設為 NIL。這些 intrinsic 幾乎不做錯誤檢查，誤用「最不神秘的症狀」是
系統當掉。VARNEW 配的空間只能用相同 NWords 的 VARDISPOSE 釋放；指定
variant 的 NEW 要用同一 variant 的 DISPOSE。

**PERMNEW / PERMDISPOSE**（p. 114）：PERMNEW 配的變數連 RELEASE 都移不掉，
只能用 PERMDISPOSE 釋放。屬系統內部用，非使用者常式。作業系統用它讓變數
跨 MARK/RELEASE 存活——例如 CHAIN 命令的程式用 PERMNEW 存在 Heap 上，
chaining 程式結束、Heap 釋放後命令仍可供系統判斷下一步。

#### Heap 實作（手冊 p. 114–116）

程式碼分在三個 UNIT（p. 114）：HEAPOPS 含 MARK、RELEASE、NEW；
EXTRAHEAP 含 DISPOSE、VARNEW、VARAVAIL、MEMLOCK、MEMSWAP；
PERMHEAP 含 PERMNEW、PERMDISPOSE、PERMRELEASE。
（VARAVAIL、MEMLOCK、MEMSWAP 屬 segment 管理，另章說明。）

Heap 用一條 MARK 鏈結串列維護，最頂端 MARK 由 `HeapInfo.TopMark` 指出。
MARK（又稱 HMR，Heap Mark Record）結構（p. 115）：

```pascal
TYPE
  MemLink = RECORD
              Avail_list: MemPtr;
              NWords: integer;
              CASE Boolean OF
                true: (Last_Avail,
                       Prev_Mark: MemPtr);
            END;
```

MARK 裡 NWords 恆為 0、variant 恆為 TRUE（MARK 只標位置不佔空間）。
每個 MARK 指向一條 Avail_List，串的是 MemLink 的 FALSE variant，NWords 是
可用空間的字數（含 record 本身兩個字）；Avail_List 鏈以 NIL 結束。Heap 上
第一個 MARK 的 Prev_Mark 是 NIL，之後每個 MARK 指回前一個，可沿鏈走訪。
對每個 MARK，第一個 Avail_List record 是 MARK 上方最低的未配置空間，
`Last_Avail` 指向可用空間的末端（通常以已配置 Heap 空間或另一個 MARK 為
界；若該 MARK 是 TopMark，則以 Codepool 為界）（p. 115）。

Heap 維護用全域變數（p. 115–116）：

```pascal
VAR
  HeapInfo: RECORD
              Lock: semaphore;
              TopMark,
              HeapTop: MemPtr;
            END;
  PoolBase: MemPtr;
  PermList: MemPtr;
```

- `Lock` semaphore 保證同一時間只有一個 process 修改 Heap。
- `TopMark` 指向最高的 MARK；`HeapTop` 指向 Heap 上最高的已配置空間，
  fault handler 用它判斷 Codepool 可往 Heap 方向移多近。
- `PoolBase` 指向 Codepool 底部。
- `PermList` 指向 PERMNEW 變數的鏈結串列（結構同 Avail_List，各 NWords 是
  一次 PERMNEW 配的字數）；NIL 表示沒有 PERMNEW 過的變數。

**Tactics**（p. 116）：MARK、NEW、VARNEW、PERMNEW 都會把 HeapTop 設到新的
Heap 頂；fault handler 總是把 Codepool（在 PoolBase）放在 HeapTop 之上，所以
Heap 運算子一要求空間就立刻保留。作業系統用全域變數 `SysCom^.GDirP` 在
Heap 上配置磁碟目錄，且要對使用者隱形——因此任何 Heap 操作（DISPOSE 除外）
之前，會先 DISPOSE `SysCom^.GDirP` 把目錄佔的空間釋出。

**Runtime environment**（p. 116–117）：使用者程式執行前，作業系統呼叫
`MARK(EMPTYHEAP)`；程式結束後呼叫 `RELEASE(EMPTYHEAP)`。使用者空間
因此全部釋放（PERMNEW 配的除外）。MARK（EMPTYHEAP） 發生在使用者程式
runtime environment 建好之後：SIBs、E_Rec's、E_Vec's 等系統結構、程式
全域資料與其 USES 的 unit 的資料都配置在 EMPTYHEAP 之前；EMPTYHEAP 之後
的 Heap 空間才給使用者程式局部使用。**Heap 由系統中所有 task 共享**
（p. 117）。

### IV.2.2 The Codepool（手冊 p. 118–119）

Codepool 位於 Stack 與 Heap 之間，放可執行的 segment，這些 segment 可能被
丟棄或從磁碟再 swap 進來，所以 Codepool 的內容、大小、位置在程式執行中
會變動（p. 118）。

Codepool 中的 segment 必須是 **p-code 或可重定位（relocatable）的 native
code**；不可重定位的 native code segment 放在 Heap 上（associate 時放）。
Codepool 是連續的一塊：丟棄一個 segment 時周圍的 segment 會靠攏；swap 進來
的 segment 放在 Codepool 任一端。Codepool 中的 segment 由各 segment SIB 裡
的指標組成雙向鏈結串列。

管理常式在 KERNEL，用到 SIB 指標與以下全域值（p. 118）：

| 變數 | 型別 | 意思 |
|---|---|---|
| PoolHead | SIB_Ptr | Codepool 底部（靠 Heap 側）那個 segment 的 SIB |
| PermSIB | SIB_Ptr | 永遠常駐 Codepool 的 segment 的 SIB（目前是 GOTOXY） |
| PoolBase | Mem_Ptr | Codepool 底部的記憶體位址 |
| SP_Low | Mem_Ptr | Stack 的最低可能界；指向 Codepool 頂端之上一個字 |
| HeapTop | Mem_Ptr | Heap 頂端 |

Heap 或 Stack 要空間時，Codepool 管理常式先嘗試不 swap 任何 segment、只
重新擺放 Codepool。Codepool 的界是 PoolBase（低端）與 SP_Low（頂端上一字）；
它可以整塊移動，Heap 側可到 HeapTop，Stack 側可到 SP 減 40 個字的邊界
（p. 118）。

Codepool 被修改的五種情況（p. 119）：

1. Heap fault:Codepool 往 Stack 方向上移，騰字給 Heap。
2. Stack fault:Codepool 往 Heap 方向下移，騰字給 Stack。
3. Heap/Stack fault 且移動也騰不出空間：swap 出一或多個 segment，其餘靠攏，
   再擺 Codepool。
4. 連 swap 出所有可 swap 的 segment 後仍不夠：回報 STACK OVERFLOW，系統
   重新初始化。
5. Segment fault：先試著不動 Codepool、從任一端讀進該 segment；不行就移動
   Codepool 騰空間；再不行 swap 出 segment 騰空間再讀；都失敗就 STACK
   OVERFLOW 並重新初始化。

Codepool 管理常式只被 Faulthandler 呼叫；Faulthandler 是附屬 task，自己的
stack 是靜態配置的，所以可以自由操作 Codepool 而不怕造成 Stack fault
（p. 119）。

### IV.2.3 Fault Handling（手冊 p. 120–121）

Stack 或 Heap 需要記憶體、或試圖進入不在記憶體的 segment 時，發出 fault，
啟動 Faulthandler process，用 Codepool 管理常式重排主記憶體（p. 120）。

Faulthandler 在 bootstrap 時被 START，平時閒置、WAIT 在一個 semaphore 上；
SIGNAL 時醒來做記憶體管理。fault 可由直譯器 SIGNAL（Stack 與 segment
fault）或由作業系統的 EXECERROR 程序 SIGNAL（Heap fault 與一種 segment
fault）。semaphore record 放在 SYSCOM（p. 120）：

```pascal
Fault_Message = RECORD
                  Fault_TIB: TIB_Ptr;
                  Fault_E_Rec: E_Rec_Ptr;
                  Fault_Words: integer;
                  Fault_Type: Seg_Fault .. Heap_Fault;
                END;

Fault_Sem: RECORD
             Real_Sem, Message_Sem: semaphore;
             Message: Fault_Message;
           END;
```

直譯器只偵測 Stack 與 segment fault：把資訊放進 `Fault_Sem.Message` 後
SIGNAL `Fault_Sem.Message_Sem`，造成切換到 Faulthandler；處理完 Codepool
後 Faulthandler 再 WAIT，切回原 process，**造成 fault 的指令會被重新執行**。

作業系統發 Heap fault（MARK、NEW、VARNEW、PERMNEW 要空間時由 Heap
運算子偵測），以及唯一一種 segment fault:MEMLOCK 要把某 segment 鎖在
Codepool 而該 segment 不在記憶體時（p. 120）。

作業系統發 fault 的方式是呼叫 EXECERROR 並傳入所需資訊，由 EXECERROR 對
Message_Sem 做 SIGNAL。Faulthandler 先確保目前執行的 segment 不會被 swap
出去，再用 Codepool 管理常式調整記憶體配置。若 Stack fault 是由跨 segment
呼叫引起的，Faulthandler 必須把呼叫方與被呼叫方兩個 segment 都鎖在記憶體
（p. 121）。

### IV.2.4 Concurrency（手冊 p. 122）

作業系統只透過 process 的啟動與停止來支援並行；真正的 task 切換由
p-machine 指令 SIGNAL 與 WAIT 完成。IV.0 的並行支援以低階 task 為對象；
多數系統層設施（尤其 I/O）是同步的——例如對 console 的 READ 或 UNITREAD
在拿到字元前不會返回，等待期間不會發生 task 切換。

全域變數 `Task_Info` 追蹤附屬 process 的部分資料：

```pascal
Task_Info: RECORD
             Lock,
             Task_Done: semaphore;
             N_Tasks: integer;
           END {of Task_Info};
```

`Lock` 用於修改其他欄位時的互斥；`Task_Done` 用來 WAIT 任一附屬 process 的
結束；`N_Tasks` 是已 START 的附屬 task 數。

UNIT **CONCURRENCY** 有三個常式：START、STOP、BLK_EXIT。每次啟動
process，編譯器會產生初始化碼對傳給 START 的 semaphore 做 signal；也在每個
process 的結尾碼產生 STOP 呼叫；主 process 的結尾碼含 BLK_EXIT 呼叫。

- **START**：建立新 task 的資料結構並啟動。task 的 TIB、活動記錄、stack
  空間都配置在 Heap 上；作業系統用 WAIT 強制 task 切換。START 做 WAIT 時，
  實際開始執行的是優先權最高的 process。
- **STOP**：記錄 process 結束。遞減 `Task_Info.N_Tasks`、SIGNAL
  `Task_Info.Task_Done`，再初始化並 WAIT 一個 dummy semaphore，強制從終止中
  的 process 永久切走。
- **BLK_EXIT**：由主 task 呼叫，WAIT 在 Task_Done 上等所有附屬 task 結束；
  當 N_Tasks 為 0 時終止主 task。

## IV.3 I/O Support

### IV.3.1 FIBs（手冊 p. 123–124）

檔案 I/O 由 FIB（File Information Block）控制；使用者宣告一個檔案時，編譯器
產生初始化該檔 FIB 的碼（p. 123）：

```pascal
FIB = RECORD
        FWindow: Window_P;
        FEOF, FEOLN: Boolean;
        FState: (FJandW, FNeedChar, FGotChar);
        FRecSize: integer;
        FLock: semaphore;
        CASE FIsOpen: Boolean OF
          true: (FIsBlkd: Boolean;
                 FDev: DevNum;
                 FVolID: VolID;
                 FReptCnt,
                 FNxtBlk,
                 FMaxBlk: integer;
                 FModified: Boolean;
                 FHeader: DirEntry;
                 CASE FSoftBuf: Boolean OF
                   true: (FNxtByte, FMaxByte: integer;
                          FBufChngd: Boolean;
                          FBuffer: PACKED ARRAY [0..FBlkSize]
                                     OF CHAR))
      END {of FIB}
```

欄位語意（p. 123–124）：

- `FWindow`：指向檔案緩衝區中目前的字元。`FEOF`、`FEOLN` 是 EOF 與 EOLN
  旗標。
- `FState`：檔案是標準(Jensen & Wirth)檔案、等待字元的 INTERACTIVE 檔案、
  或已拿到字元的 INTERACTIVE 檔案。
- `FRecSize`：untyped 檔為 0，INTERACTIVE 檔與 textfile 為 1；大於零則是
  record 的大小（位元組）。
- `FLock`：semaphore，保證一次只有一個 process 修改該檔。
- `FIsOpen` 為 TRUE（檔案開著）時：`FIsBlkd` 表示在 block-structured 裝置上；
  `FDev` 是裝置號、`FVolID` 是 volume 名；`FReptCnt` 記 window 值還有效幾次
  （才需要再一次 GET）；`FNxtBlk` 是下一個要存取的（相對）block，`FMaxBlk`
  是可存取的最大（相對）block；`FModified` 為 TRUE 時會在目錄設新日期；
  `FHeader` 是該檔目錄項目的副本。
- `FSoftBuf` 為 TRUE 表示用 soft-buffered I/O——block-structured volume 上
  除 untyped 檔外都如此；此時 `FNxtByte`、`FMaxByte` 做緩衝管理，
  `FBufChngd` 表示緩衝內容改過，`FBuffer` 是緩衝區本身。

### IV.3.2 Directories（手冊 p. 124–125，Figure 6）

Figure 6（p. 125）是磁碟等 block-structured volume 的目錄結構。目錄是
`array [0..77] of direntry`（共 78 項，編號 0 到 77）。

**dir[0]（dfkind=securedir，untyped file 的 DIRENTRY RECORD）**：

| 欄位 | 說明 |
|---|---|
| dfirstblk | 第一個 block |
| dlastblk | 最後一個 block |
| filler_1 / dfkind | filler 與檔案種類 |
| dvid | volume 名：length（7）加上字元 1–7（兩欄各 4 列：1/2/4/6 與 3/5/7） |
| deovblk | (end-of-volume block) |
| dnumfiles | 檔案數 |
| dloadtime | 載入時間 |
| dlastboot | 最後開機日期，一個字內分 (year)/(month)/（day） |

**dir[1]–dir[77]（一般檔案的 DIRENTRY RECORD）**：

| 欄位 | 說明 |
|---|---|
| dfirstblk | 第一個 block |
| dlastblk | 最後一個 block |
| status bit / filler_2 / dfkind | 狀態位元、filler、檔案種類 |
| dtid | 檔名：length（15）加字元 1–15（兩欄：1/2/4/6/8/10/12/14 與 1/3/5/7/9/11/13/15） |
| dlastbyte | 最後位元組 |
| daccess | 存取日期，一個字內分 (year)/(month)/（day） |

### IV.3.3 Varieties of I/O（手冊 p. 126）

- **Record I/O**：typed Pascal 檔，用 GET 與 PUT。
- **Screen I/O**：由 UNIT SCREENOPS 處理。螢幕輸入用 CHAR_DEV_GET（內部用
  SCREENOPS 的 SC_CHECK_CHAR 與 `SYSCOM^.MISCINFO` 判斷是否要特殊處理）；
  螢幕輸出就是單純的 UNITWRITE。
- **Block I/O**：untyped 檔，用 BLOCKREAD / BLOCKWRITE，屬 EXTRAIO 的系統
  常式 FBLOCKIO。檔案以 untyped 存取時，其他檔案格式全部停用。
- **Text I/O**：textfile 是 ASCII 字元檔，開頭有 **2 個 block 的 header**，給
  Screen Oriented Editor 放格式資訊；Editor 以外的系統程式忽略它。新建
  textfile 時作業系統寫入填滿 NUL 的 2-block header。textfile 的 block 數恆為
  偶數，所以最小的 textfile 是 4 個 block，多餘空間補 NUL。每筆 record 是一行，
  以 `<return>` 結束；若 record 第一個字元是 DLE（十進位 16），視為空白壓縮碼：
  下一個位元組是 （32+n），n 是行首空白數（由 Editor 產生，主要用來省縮排
  原始碼的空間）。使用者程式一般用 READ、READLN、WRITE、WRITELN；也可用
  GET/PUT，遵循 Jensen & Wirth 的 TEXT 標準。

## IV.4 Using the Screen Control Unit（手冊 p. 127–131）

要用 Screen Control Unit，程式需有 `SCREENOPS.CODE` 及其 INTERFACE 段，並
宣告（p. 127）：

```pascal
USES {$U SCREENOPS.CODE} SCREENOPS;
```

本節常式都可由程式呼叫。「text port」是螢幕上可定義成與實際螢幕不同大小的
矩形區域；此功能在當時未被整個系統充分利用，提到 text port 時預設就是整個
螢幕（p. 127）。

常式列表（p. 127–131）：

| 常式 | 功能 |
|---|---|
| `SC_Init` | 初始化所有 Screen Control 表格與變數（通常只有作業系統呼叫） |
| `SC_Clr_Cur_Line` | 清除目前行 |
| `SC_Clr_Line(Y)` | 清除目前 text port 第 Y 行 |
| `SC_Clr_Screen` | 清除螢幕 |
| `SC_Erase_to_EOL(X, Line)` | 從 （X, Line） 清到行尾 |
| `SC_Eras_EOS(X, Line)` | 從 （X, Line） 清到螢幕尾 |
| `SC_Left` / `SC_Right` | 游標左 / 右移一字元 |
| `SC_Up` / `SC_Down` | 游標上 / 下移一行 |
| `SC_Home` | 游標移到目前 text port 的 0,0 |
| `SC_GOTO_XY(X, Line)` | 游標移到 （X, Line） |
| `SC_Find_X` / `SC_Find_Y` | 回傳游標行 / 列（相對目前 text port） |
| `SC_GetC_CH(VAR CH: char; Return_on_Match: SC_ChSet)` | 反覆讀鍵盤直到 CH ∈ Return_on_Match（SC_ChSet 是 SET OF CHAR）；字母應傳大寫，小寫會先轉大寫再比 |
| `SC_Space_Wait(Flush: Boolean): Boolean` | 反覆讀鍵盤直到 `<space>` 或 ALTMODE；Flush 為 TRUE 時先做 UNITCLEAR（1） 並印「Type \<space\> to continue」；讀到的不是 `<space>` 時回傳 TRUE |
| `SC_Prompt(Line: SC_Long_String; X_Cursor, Y_Cursor, X_Pos, Where: integer; Return_on_Match: SC_ChSet; No_Char_Back: Boolean; Break_Char: char): char` | 在 （X_Pos, Where） 印提示列(SC_Long_String = STRING[255])，游標放 （X_Cursor, Y_Cursor），X_Cursor<0 時放提示尾；提示太長時在 Break_Char 處切段，可用 ‘?’ 循環看各段；反覆讀鍵盤直到字元 ∈ Return_on_Match |
| `SC_Check_Char(VAR Buf: SC_Window; VAR Buf_Index, Bytes_Left: integer): Boolean` | 讀字串時檢查是否讀到 `<backspace>` 或 `<rubout>`（DEL），有則修改輸入緩衝並回 TRUE |
| `SC_Map_CRT_Command(VAR K_CH: char): SC_Key_Command` | 把字元映射成 SC_Key_Command:（SC_Backspace_Key, SC_DC1_Key, SC_EOF_Key, SC_ETX_Key, SC_Escape_Key, SC_DEL_Key, SC_Up_Key, SC_Down_Key, SC_Left_Key, SC_Right_Key, SC_Not_Legal） |
| `SC_Scrn_Has(What: SC_Scrn_Command): Boolean` | CRT 是否有所傳的控制字元；SC_Scrn_Command:（SC_Home, SC_Eras_S, SC_Eras_EOL, SC_Clear_Lne, SC_Clear_Scn, SC_Up_Cursor, SC_Down_Cursor, SC_Left_Cursor, SC_Right_Cursor） |
| `SC_Has_Key(What: SC_Key_Command): Boolean` | CRT 是否會產生所傳的鍵盤字元 |
| `SC_Use_Info(Do_What: SC_Choice; VAR T_Info: SC_Info_Type)` | 程式與 Screen Control Unit 雙向傳資訊；Do_What 是 SC_Get 或 SC_Give |
| `SC_Use_Port(Do_What: SC_Choice; VAR T_Port: SC_TX_Port)` | 同 SC_Use_Info，傳 text port 資訊 |

`T_Info` 內容（p. 130）：

```pascal
SC_Version: string;
SC_Date: PACKED RECORD
           Month: 0..12;
           Day: 0..31;
           Year: 0..99;
         END;
Spec_Char: SET OF char;   (* 不回顯的字元 *)
Misc_Info: PACKED RECORD
             Height, Width: 0..255;
             Can_Break, Slow, XY_CRT, LC_CRT,
             Can_UpScroll, Can_DownScroll: Boolean;
           END;
```

`T_Port` 內容（p. 131）：`Row, Col, Height, Width, Cur_X, Cur_Y: integer;`

## V. Program Execution（手冊 p. 133–134）

使用者程式的 runtime environment 由 GETCMD 建立。GETCMD 啟動系統程式
（Compiler、Linker、Filer 等）與 eX(ecute 命令指定的使用者程式；兩種情況都
呼叫 ASSOCIATE 找到 codefile，再呼叫 BUILDENV 依第二章的方式建立 runtime
environment（p. 133）。

BUILDENV 遞迴走訪程式用到的 segment，為每個 segment 初始化 E_Vec、E_Rec、
SIB；每建好一個 E_Rec 就鏈到已啟用 segment 的鏈上，作業系統藉此追蹤所有
active segment。初始化前若發現該 segment 已 active，只設好指標；否則從
codefile 的資訊建立 E_Vec、E_Rec、SIB。

SEGREF 是編譯器產生的 segment reference 指派。**segment 編號是 code
segment 局部的：主程式是 segment 2，附屬 segment 從 3 起編，segment 1 永遠
是作業系統的 KERNEL unit。** 編譯用到的 principal segment（如 USES 的
unit）都會有 SEGREF；associate 時 BUILDENV 用 SEGREF 清單找程式用到的
segment（p. 133）。

系統偵測到的所有 runtime 錯誤都使目前程式中止：顯示錯誤訊息，使用者按
`<space>` 後系統重新初始化，程式的 runtime environment 遺失。程式正常結束
時控制權回到 GETCMD 等下一個命令；正常結束的程式 environment 不會遺失，
可用 U(ser restart 命令重新啟動——系統可能需要、也可能不需要再呼叫
BUILDENV（p. 133）。

## 與 IV.2.1 的關係

本章是 IV.0（1981）的作業系統描述，而本 repo 研究的 SunDog 直譯器是
IV.2.1（1983 手冊所記）。讀者對照時應留意：

- 手冊明說 IV.0 的 Codepool 彈性配置「能提供比以往版本更多的可用記憶體」
  （p. 118），表示換頁策略在 IV 系列內仍在演進；IV.2.1 的作法需以 IV.2.1
  的來源為準（待查證）。
- `KERNEL 在 slot 0、USERPROG 在 slot 15`、`segment 1 永遠是 KERNEL` 這類
  編號約定是否沿用到 IV.2.1，本手冊無從得知（待查證）。
- SCREENOPS 介面、FIB 欄位、目錄格式（Figure 6）在 IV.2.1 是否相同，
  同樣需要 IV.2.1 的一手來源核對（待查證）。

## 掃描不清與待查證

- Figure 6（p. 125）中 dvid/dtid 的字元編號以兩欄排版（1/2/4/6 對 3/5/7 等），
  照抄如上；欄位在 word 內的確切位元配置圖中沒有標，無法從本頁推出。
- p. 115 的 `MemLink` variant record 只印出 TRUE 分支的欄位，但內文說
  Avail_List 的 record 是 FALSE variant；FALSE 分支的欄位清單掃描頁面上沒有
  顯示（可能在本書其他章節，待查證）。
- 本掃描實際頁碼對應是「印刷頁 = PDF 頁 − 6」，與任務簡報的「−8」不同；
  本文已依掃描頁腳的印刷頁碼標註。
