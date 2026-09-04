# Codefile 組織與執行環境

出自 SofTech Microsystems《UCSD p-System and UCSD Pascal Version IV.0 Internal
Architecture Guide》（1981 年 3 月第一版）Chapter II “The P-Machine”，
印刷頁 22–41（節 II.2.1.7 尾聲、II.2.2、II.2.3，以及 II.3 開頭）。
本文所有頁碼均為印刷頁碼。

> 延伸閱讀：[本層索引](README.md)｜[Code Segment 格式](code-segment-format.md)（本篇的前半）

## Segment reference list 收尾（p.22）

- Segment reference list 以一個 **SegName 填滿空白、SegNum 為 0** 的 `SegRec` 結束
  （手冊 p.22）。
- SegName 為 `'***     '`（三個星號加空白）的 SegRec 是給作業系統執行 unit 的
  initialization / termination code 用的：執行 host program 前，作業系統掃描所有
  used units，把含有 `'***'` 參考的建成一條線性串列，在 host program 啟動前依序
  執行各 unit 的 initialization，結束後再反向執行 termination（手冊 p.22）。
- 編譯 unit 的 initialization/termination 段（即 procedure 1）時，在
  initialization 與 termination 兩部分之間發出一條
  `<CXG <***'s seg num>, 1>` 指令；`'***'` segment reference 會被保留一個本地
  segment number。作業系統把需要初始化的 unit 串成串列，串列末端是主程式的
  outer body。啟動時呼叫串列上第一個 initialization，它再呼叫下一個，一路叫到
  主程式本體；主程式結束時呼叫鏈「彈回」，termination 以相反順序執行（手冊 p.22）。

## II.2.1.7 Linker Information（p.23–26）

**Linker info 是 code segment 裡讓 Linker 解析 P-code 與 native code 之間參照的
一段資料**（手冊 p.23）。重點：

- 組譯器產生的 segment **一定有** Linker info；編譯器產生的 segment 只有在含
  `EXTERNAL` routine 時才有；只有 principal segment 可以含 `EXTERNAL` routine
  （手冊 p.23）。
- Linker info 是一串 **8 word 的記錄**，從 segment reference list 結束（高位址端）
  之後的第一個 block 邊界開始，序列末端是值為 `EOFMark` 的記錄。記錄**一律**
  8 word 長，未用的記錄與未用的欄位補零（手冊 p.23）。
- segment 有 Linker info 時，segment dictionary 的 `Seg_Misc` 裡
  `HasLinkerInfo` 為 TRUE。Linker info 起始 block（相對 codefile 開頭）的公式
  （手冊 p.23）：

  ```
  Code_Addr + ((Code_Leng + Seg_Refs + 255) DIV 256)
  ```

  `Code_Addr`、`Code_Leng`、`Seg_Refs` 都是 segment dictionary 裡的值。
- 所有 Linker info 記錄共通的兩個欄位：`Name`（8 字元的 segment 名稱）與
  `LIType`（決定記錄其餘部分的性質）（手冊 p.23）。

記錄格式（pseudo-Pascal，手冊 p.23–24）：

```pascal
PtrRecNum = {8-word pointer record 的個數，逐記錄可變};

LITypes = (EOFMark, GlobRef, PublRef, PrivRef, ConstRef, GlobDef, PublDef,
           ConstDef, ExtProc, ExtFunc, SepProc, SepFunc);

LIEntry = RECORD
            Name: PACKED ARRAY [0..7] OF CHAR;
            CASE LIType: LITypes OF
              GlobRef, PublRef, ConstRef:
                (Format: (Word, Byte, Big);
                 NRefs:  integer);
              PrivRef: (Format: (Word, Byte, Big);
                        NRefs:  integer;
                        NWords: integer);
              ExtProc, ExtFunc:
                (SrcProc: integer;
                 NParams: integer);
              SepProc, SepFunc:
                (SrcProc: integer;
                 NParams: integer;
                 KoolBit: Boolean);
              GlobDef: (HomeProc: integer;
                        ICOffSet: integer);
              PublDef: (BaseOffset: integer;
                        PubDataSeg: integer);
              ConstDef: (ConstVal: integer);
              EOFMark: ;
            PtrList: ARRAY [0..PtrRecNum] OF ARRAY [0..7] OF integer
          END;
```

各 LIType 語意（手冊 p.24–26）：

- **GlobRef / PublRef / ConstRef / PrivRef** 都是組譯器產生的。共同結構是兩個欄位
  加上一份 `PtrList`：一串指向所在 segment 的**段相對 byte 指標**。`Format` 是
  被指到欄位的大小，`NRefs` 是串列裡的指標數，`PtrList` 以 8 word 為單位、
  未用的 word 補零；`PtrRecNum = ceiling(NRefs/8)`（手冊 p.24）。
  - `GlobRef`：連結兩個以上組譯 routine 之間的識別字；`Name` 在本 segment 被參考、
    在別的組譯 routine 定義；Format 必為 Word；Linker 把被參考物件的最終段位移
    加進 PtrList 指到的所有 word（依處理器不同以 byte 或 word 為單位）。
  - `PublRef`：把組譯 routine 的識別字連到某 compilation unit 的全域變數；
    Format 必為 Word。
  - `ConstRef`：連到某 compilation unit 的全域常數；Format 可為 Byte 或 Word；
    Linker 把常數值**放進** PtrList 指到的位置。
  - `PrivRef`：在 global data segment 裡配置空間；Format 必為 Word；`NWords`
    是要配置的 word 數；Linker 把配置區起點在 global data segment 內的位移加進
    PtrList 指到的所有 word。
- **ExtProc / ExtFunc**：編譯器產生，用來參考 `EXTERNAL` routine；**沒有 PtrList**。
  `SrcProc` 是 routine 編號，`NParams` 是參數傳遞用的 word 數（手冊 p.25）。
- **SepProc / SepFunc**：組譯器為 routine 宣告產生；無 PtrList。`KoolBit` 為 TRUE
  表示 routine 可重定位。`.PROC`/`.FUNC` 產生 `KoolBit = FALSE`，
  `.RELPROC`/`.RELFUNC` 產生 `KoolBit = TRUE`（手冊 p.25）。
- **GlobDef**：宣告組譯 routine 裡的全域識別字；每個由 `.DEF`、`.PROC`、`.FUNC`、
  `.RELPROC`、`.RELFUNC` 定義的 label 各產生一筆；無 PtrList。`HomeProc` 是
  定義 `Name` 的 routine 編號，`ICOffSet` 是 `Name` 相對該 routine 起點的 byte 位移
  （手冊 p.25）。
- **PublDef**：宣告對 `EXTERNAL` routine 可見的全域變數；無 PtrList。`BaseOffset`
  是變數相對所在 data segment 起點的 **word** 位移，`PubDataSeg` 是所在 data
  segment 的本地編號（手冊 p.25）。
- **ConstDef**：宣告對 `EXTERNAL` routine 可見的全域常數；`ConstVal` 是常數值
  （手冊 p.25）。
- **EOFMark**：已用 Linker info 記錄的結尾；`Name` 應填空白（手冊 p.26）。

各 segment 型別可含哪些 Linker info 記錄（手冊 p.26；`Proc_Seg` 完全不能有
Linker info）：

| LIType   | Prog_Seg | Unit_Seg | Seprt_Seg |
|----------|----------|----------|-----------|
| GlobRef  |          |          | yes       |
| PublRef  |          |          | yes       |
| PrivRef  |          |          | yes       |
| ConstRef |          |          | yes       |
| ExtProc  | yes      | yes      |           |
| ExtFunc  | yes      | yes      |           |
| SepProc  |          |          | yes       |
| SepFunc  |          |          | yes       |
| GlobDef  |          |          | yes       |
| PublDef  | yes      | yes      |           |
| ConstDef | yes      | yes      |           |
| EOFMark  | yes      | yes      | yes       |

## II.2.2 Codefile Organization（p.27–33）

### II.2.2.1 Segment dictionary（p.27–32）

- Codefile 的第一個 block 是 segment dictionary 的第一筆記錄。IV.0 的 segment
  dictionary 是 dictionary record 的**鏈結串列**；超過一筆時，後續記錄嵌在
  codefile 內、各佔一個 block、位於 code segment 之間（手冊 p.27）。
- 一筆 dictionary record 最多描述 **16 個 segment**；同一個 segment 的資訊分散在
  **6 個陣列**裡，用同一個索引取值。dictionary 只描述 code body 收在這個
  codefile 裡的 segment（手冊 p.27）。

記錄格式（Pascal 片段，手冊 p.28–29）：

```pascal
CONST Max_Dic_Seg = 15;   {segment dictionary record 的最大項次}

TYPE  Seg_Dic_Range = 0..Max_Dic_Seg;

      Segment_Name = PACKED ARRAY [0..7] OF CHAR;

      {segment types}
      Seg_Types = (No_Seg,     {空的 dictionary 項}
                   Prog_Seg,   {program outer segment}
                   Unit_Seg,   {unit outer segment}
                   Proc_Seg,   {program/unit 內的 segment procedure}
                   Seprt_Seg); {native code segment}

      {machine types}
      M_Types = (M_Psuedo, M_6809, M_PDP_11, M_8080, M_Z_80,
                          M_GA_440, M_6502, M_6800, M_9900,
                          M_8086, M_Z8000, M_68000);

      {p-machine versions}
      Versions = (Unknown, II, II_1, III, IV, V, VI, VII);

      Seg_Dict = RECORD
        Disk_Info: ARRAY [Seg_Dic_Range] OF
                     RECORD
                       Code_Addr: integer;  {segment 起始 block}
                       Code_Leng: integer;  {segment 的 word 數}
                     END;
        Seg_Name:  ARRAY [Seg_Dic_Range] OF Segment_Name;
        Seg_Misc:  ARRAY [Seg_Dic_Range] OF
                     PACKED RECORD
                       Seg_Type: Seg_Types;
                       Filler: 0..31;          {保留}
                       Has_Link_Info: Boolean; {需要 link？}
                       Relocatable: Boolean;   {segment 可重定位？}
                     END;
        Seg_Text:  ARRAY [Seg_Dic_Range] OF integer;  {interface text 起始 block}
        Seg_Info:  ARRAY [Seg_Dic_Range] OF
                     PACKED RECORD
                       Seg_Num: 0..255;        {本地 segment number}
                       M_Type: M_Types;
                       Filler: 0..1;           {保留}
                       Major_Version: Versions;{P-machine 版本}
                     END;
        Seg_Famly: ARRAY [Seg_Dic_Range] OF
                     RECORD
                       CASE Seg_Types OF
                         Unit_Seg, Prog_Seg:
                           (Data_Size: integer;    {data size}
                            Seg_Refs: integer;     {compilation unit 的 segment 數}
                            Max_Seg_Num: integer;  {檔案內 segment 數}
                            Text_Size: integer);   {interface text 的 block 數}
                         Seprt_Seg, Proc_Seg:
                           (Prog_Name: Segment_Name); {外層 program/unit 名}
                       END;
        Next_Dict: integer;                  {下一筆 dictionary record 的 block 號}
        Filler: ARRAY [0..6] OF integer;     {保留}
        Copy_Note: string[77];               {版權宣告}
        Sex: integer;                        {machine sex（Sex = 1）}
      END;
```

各欄位說明（手冊 p.30–32）：

- **Disk_Info**：segment 在檔案內的位置。Segment code 一律從 block 邊界開始；
  `Code_Addr` 是起始 block（相對 codefile 開頭），`Code_Leng` 是 16-bit word 數，
  **含 relocation list、不含 segment reference list**；未用項補零（p.30）。
- **Seg_Name**：program/unit/segment/assembly procedure 名的前 8 字元；未用項填
  空白（p.30）。
- **Seg_Misc**：`Seg_Type` 意義如上；`Has_Link_Info` 表示該 segment 產生了 Linker
  info（Linker info 位於 segment reference list 之後的 block，從 block 邊界開始）；
  `Relocatable` 表示靜態或動態可重定位（p.30）。
  - 動態可重定位的 code segment 住在 **code pool**，執行期間記憶體位置可能多次改變；
    靜態可重定位的只載入一次、固定在 system heap 上，整個生命期 position-locked
    且 memory-locked（p.30）。
  - **純 P-code 的 segment 一律 position-independent，因此都是動態可重定位**。
    含 native code 的 segment 也可以動態重定位，前提是不依賴 segment body 的
    修改結果的生命期、也不依賴 body 在單一 p-code 執行期間的確切位址（p.30）。
  - 動態可重定位的 native code 用 `.RELPROC` / `.RELFUNC` 組譯出來；一個 link 好的
    code segment 只有當它**所有**組譯 routine 都宣告為動態可重定位時才算數。這些
    指令是程式設計師的**斷言**，系統不強制檢查：要動態重定位的 routine 不能把
    資訊存進 segment body、不能自我修改、不能把 code segment 的指標存進資料變數
    （p.30）。
  - `Relocatable` 與 relocation list 的有無無關，也與 concurrency 無關（p.30）。
- **Seg_Text**：該 segment 的 INTERFACE text section 起始 block（相對 codefile
  開頭）；INTERFACE text 可在 codefile 任何位置。搭配 `Seg_Famly` 的 `Text_Size`
  決定位址與長度。INTERFACE text 從 block 邊界開始、遵循 textfile 慣例，但最後
  一頁可為 1 或 2 個 block。**只有 `Unit_Seg` 有 INTERFACE section**，其餘補零
  （p.30–31）。
- **Seg_Info**：`Seg_Num` 是 segment 編號；`M_Type` 指出 segment 內是哪種 object
  code——含 native code 時是處理器專屬值，純 P-code 時是 `M_Psuedo`（原文拼字
  如此）；`Major_Version` 是 codefile 預定執行的 p-machine 版本（p.31）。
- **Seg_Famly**：內容依 principal/subsidiary 而定。
  - subsidiary segment（`Seprt_Seg`/`Proc_Seg`）：`Prog_Name` 存上層 compilation
    unit 名前 8 字元；生成 codefile 時不知道（如 `Seprt_Seg`）就填空白（p.31）。
  - principal segment（`Prog_Seg`/`Unit_Seg`）四個欄位（p.31）：
    - `Data_Size`：本 segment 的 base data segment 的 word 數。principal segment
      的變數從任何位置都以全域方式存取，所以 outer routine body 的 `Data_Size`
      應為 0，避免在未用的區域資料區浪費記憶體。
    - `Seg_Refs`：本 segment 的 segment reference list 的 word 數。
    - `Max_Seg_Num`：指派給本 compilation unit 的 segment number 總數，**不管
      segment body 是否收在此檔**。
    - `Text_Size`：compilation unit 內 INTERFACE text 的 block 數；只有
      `Unit_Seg` 用，其餘補零。
  - 未用項（`No_Seg`）的 `Seg_Famly` 補零（p.32）。
- **Next_Dict**：下一筆 dictionary record 的 block 號（相對 codefile 開頭）；
  最後一筆為 0（p.32）。
- **Filler**：保留，補零（p.32）。
- **Copy_Note**：版權訊息，可用 LIBRARY 工具或編譯器指令產生（p.32）。
- **Sex**：codefile 的 byte sex 標記。它是一個值為 1 的 full word，與 dictionary
  record 其他部分同 byte sex：在相同 byte sex 的機器上讀到 1，相反 byte sex 的
  機器上讀到 256。系統程式用它偵測 codefile 的 byte sex，必要時對 dictionary 的
  word 欄位做 byte-swap（p.32）。

### II.2.2.2 Assembler-Generated Codefiles（p.33）

組譯器產生的 codefile 與編譯器產生的略有不同（手冊 p.33）：

- **每個 procedure 各有一份 relocation list**（不是整個 segment 一份）；只有這種
  list 可以含 `ProcRel` relocation。每份 list 緊接在它所描述的 procedure body 之後，
  起始（高位址端）由該 procedure 的 `ExitIC` 欄位裡的段相對 word 指標指出。
- 組譯出來的 segment 在 link 時，其所有 procedure/function 的 code body 可能被
  複製進目標 compilation unit 的某個 segment；組譯時**不知道**會 link 到哪個
  segment。但透過 REF/DEF 互相通訊的組譯 routine 一律假定會 bound 進同一個
  segment。
- 組譯器為每個 routine 產生的 `DataSize` word 應為 **-1（0xFFFF）**：這是 0 的
  一補數，表示「code body 的第一道指令是 native code」。
- 因為不知道會被 link 到哪個 program/unit，segment dictionary 的 `Seg_Famly`
  陣列裡的 `Prog_Name` 應填空白，所有 `BaseRel` relocation 子串列的
  `ListHeader` 裡的 `DataSegNum` 欄位應補零。
- Link 組譯 segment 時 **Linker 的責任**：把所有 `ProcRel` relocation 子串列轉成
  `SegRel` relocation list、正確設定所有 `BaseRel` 子串列 `ListHeader` 的
  `DataSegNum`、把所有 relocation 子串列集中到 code segment 的 procedure
  dictionary 之後，並依 Linker info 更新 `Seg_Misc` 的 `Relocatable` 位元。

## II.2.3 Code Segment Environments（p.34–39）

### II.2.3.1 Segment Information Blocks（SIBs）（p.34–36）

**SIB 是描述一個「active」code segment 的記錄**——「active」指可能被正在跑的
程式用到。SIB 配置在 Heap 上，segment 活著多久它就待多久；**每個 code segment
只有一個 SIB**，不管有多少 segment 在用它。segment 不必在記憶體裡才算 active
（可以在磁碟或 Codepool 裡），但它的 SIB 一定在 Heap 上（手冊 p.34）。

SIB 格式（Pascal 片段，手冊 p.34）：

```pascal
SIB = RECORD
        Seg_Base:   Mem_Ptr;  {segment 的記憶體位址}
        Ref_Count:  integer;  {對本段 active call 的數量}
        Activity:   integer;  {記憶體 swap 活動度}
        Link_Count: integer;  {連到本 SIB 的 link 數}
        Residency:  -1..maxint; {-1 = pos lock, 0 = swap, n = mem lock}
        Seg_Name:   PACKED ARRAY [0..7] OF CHAR;
        Seg_Leng:   integer;  {segment 的 word 數}
        Seg_Addr:   integer;  {segment 的磁碟位址}
        Vol_Info:   VI_Ptr;   {指向磁碟機資訊}
        Data_Size:  integer;  {data segment 的 word 數}
        Res_SIBs:   RECORD    {code pool 管理記錄}
                      Next_SIB: SIB_P;  {串列下一個 SIB}
                      Prev_SIB: SIB_P;  {串列上一個 SIB}
                      CASE Boolean OF   {暫存區}
                        TRUE:  (Sort_SIB: SIB_P);   {排序串列下一個}
                        FALSE: (New_Loc:  Mem_Ptr); {暫時位址}
                    END;
      END;
```

欄位語意（手冊 p.34–36）：

- `Seg_Base`：segment 目前在記憶體的位址；不在記憶體時為 `NIL`。
- `Ref_Count`：未完成的跨段呼叫數。段外 routine 執行 `CXP` 呼叫段內 routine 時
  加一；段內 routine `RET` 回段外時減一。
- `Activity`：依使用次數累積的值，隨時間增加。以下情況各**加 6**：呼叫段外
  routine；段內 routine 返回段外；task switch 把正在執行的 segment 停住。
- `Link_Count`：從其他作業系統資料結構連到本 SIB 的 link 數；歸零時 SIB 從 Heap
  移除。
- `Residency`：-1 到 maxint。
  - `-1`：**Position_Locked**（segment dictionary 的 `Relocatable` 為 TRUE 時出現）。
  - `0`：**Swappable**（必要時可移出記憶體）。
  - 大於 0：**Memory_Locked**，值是已套用的 memory lock 次數。
  - 程式宣告 Memory_Locked 時加一、宣告 Swappable 時減一；歸零才真正變成
    Swappable。程式用 intrinsic `MEMLOCK` 與 `MEMSWAP` 控制 segment 的 residency。
- `Seg_Name`：segment 名前 8 字元。
- `Seg_Leng`：segment 佔的 word 數（含 relocation list，不含 segment reference
  list）。
- `Seg_Addr`：segment 在磁碟上的第一個 block 號。
- `Vol_Info`：指向 volume information record（含 segment 所在磁碟的 drive number
  與 volume name）的 `VI_Ptr`。
- `Data_Size`：segment 的 data segment word 數；只對 principal segment 有效，
  其餘為 0。
- `Res_SIBs`：維護 Code Pool 用。Code Pool 裡所有 segment 的 SIB 以 `Prev_SIB`/
  `Next_SIB` 串成雙向鏈結串列；`Sort_SIB`、`New_Loc` 是管理 Code Pool 時的暫存值。
- 作業系統管理 code segment 的資料結構全部透過指標參考 SIB。程式啟動需要一個
  尚未 active 的 segment 時，在 Heap 配置並初始化 SIB，作業系統建立指標、
  `Link_Count` 加一；不再需要時移除指標、減一，歸零即從 Heap 移除（p.35–36）。

### II.2.3.2 Environment Records（E_RECs）（p.37–39）

一個 code segment 的「environment」是「它可存取的 segment」到「本地 segment
number」的對應。Segment number 只有本地意義：segment 只能參考被指派了本地
segment number 的 segment（手冊 p.37）。每個 segment 有一筆 Environment Record
（`E_Rec`），指定一個 Environment Vector（`E_Vec`）描述本地 segment number 到
實際 code segment 的對應（p.37）。

格式（pseudo-Pascal，手冊 p.37）：

```pascal
E_Vect_P = ^E_Vect;
E_Rec_P  = ^E_Rec;

E_Vect = RECORD
           Vec_Length: integer;   {本地 segment 數}
           Map: ARRAY [1..Vec_Length] OF E_Rec_P;  {本地環境對應}
         END;

E_Rec  = RECORD
           Env_Data: Mem_Ptr;    {指向全域資料}
           Env_SIB:  SIB_P;      {指向該 segment number 的 SIB}
           Env_Vect: E_Vect_P;   {指向 environment}
           CASE Boolean OF
             TRUE: (Link_Count: integer;  {連到本 E_Rec 的 link 數}
                    Next_Rec:   E_Rec_P); {下一筆 environment record}
         END;
```

欄位語意（手冊 p.37–38）：

- `Env_Data`：指向 segment 的全域資料（data segment 在程式啟動時配置於 Heap）。
- `Env_SIB`：指向 segment 的 SIB（同樣在啟動時放 Heap）。
- `Env_Vect`：`E_Rec` 指標陣列，**以 segment number 索引**，指標指向描述某個
  code segment 的 `E_Rec`——這就是本地 segment number 到實際 segment 的對應。
  為減少索引運算，`Map` 陣列從 **1** 開始（本地 segment number 必須 ≥ 1），
  `Vec_Length` 可視為佔據 map 的第 0 格（p.38）。
- `Link_Count`：目前正在 USE 這個 segment 的 active compilation unit 數；只對
  compilation unit 的 principal `E_Rec` 有效，維護方式與 SIB 的 `Link_Count`
  相同（p.37）。
- `Next_Rec`：所有 active compilation unit 的鏈結串列 `Unit_List` 的下一筆；
  同樣只對 principal `E_Rec` 有效（p.38）。

作業系統用**遞迴** routine 建立程式 USE 的 unit、subsidiary segment 與 principal
segment（其「native segment」）的 environment，演算法大要（手冊 p.38）：

```pascal
FUNCTION Build_Env (Seg_Dict): E_Rec_P;
  BEGIN
  IF outer block segment E_Rec exists in Unit_List THEN BEGIN
    increment Link_Count;
    return existing E_Rec_P
  END ELSE BEGIN
    create E_Vect;
    create Env_Data for outer block data space;
    IF there are USEd units indicated in Seg_Dict THEN
      FOR all USEd units DO
        install Build_Env (New_Seg_Dict) into current E_Vect;
    FOR all native segments DO
    BEGIN
      create E_Rec and SIB for native segment;
      install E_Vect, SIB, and Env_Data in E_Rec;
      install E_Rec for native segments in E_Vect
    END;
    install E_Rec for outer block segment on Unit_List;
    return E_Rec_P for outer block segment
  END
  END
```

`Build_Env` 回傳被執行程式 outer block 的 `E_Rec` 指標，此指標被裝進作業系統的
`User_Program` E_Vect 項（p.38）。

程式執行完後，用遞迴 routine 把 outer block 與所有附屬 unit/segment 的
environment 解除連結，演算法大要（手冊 p.39）：

```pascal
PROCEDURE Dump_Env (E_Rec_P);
  BEGIN
  decrement Link_Count;
  IF Link_Count = 0 THEN
  BEGIN
    de-link from Unit_List;
    DISPOSE (Env_Data);
    FOR all E_Rec's on E_Vect whose Seg_Vect <> E_Rec.Seg_Vect DO
      Dump_Env (those E_Rec's);
    FOR all E_Rec's on E_Vect whose Seg_Vect = E_Rec.Seg_Vect DO
    BEGIN
      de_link E_REC^.SEG_SIB;
      DISPOSE (those E_RECs);
    END;
    DISPOSE (E_Rec.Seg_Vect);
  END
  END
```

程式終止時，作業系統把自己 E_Vect 裡對應該程式的項設為 `NIL`，對 outer block
的 `E_Rec` 呼叫 `Dump_Env`；返回後再掃一遍 `Res_SIBs` 串列，把 `Link_Count = 1`
的 segment 從 Heap 移除（p.39）。

## II.3 Task Environments 開頭（p.40–41）

- **task** 是與其他 routine 並行執行的 routine，由三個資料結構實作：body、
  Task Information Block（TIB）、task stack。Pascal 裡 task 叫 **PROCESS**
  （手冊 p.40）。
- p-System 的「main task」是從作業系統初始化、經所有系統工具或使用者程式執行、
  直到作業系統終止的那條執行線。程式可以有 subsidiary task（p.40）。
- 執行時每個 subsidiary task 用**自己的堆疊**而不用 System Stack；task 的活動記錄
  就在 task stack 裡，兩者都配置在 Heap 上，連同一塊讓堆疊成長的可用空間（p.40）。
- task body 是 p-code segment 的一部分，結構與 procedure/function body 無異（p.40）。
- task stack 的空間由 `START` intrinsic 的 `STACKSIZE` 參數決定，**預設 200 word**
  （p.40）。
- main task 用 System Stack 做 expression evaluation 與活動記錄；Heap 由 main
  task 與所有 subsidiary task 共用（p.40）。
- subsidiary task 的 TIB 在 task 啟動時配置於 Heap，記錄 task 的執行環境，在
  task 閒置後重新啟動時用來還原（p.40）。
- 任一時刻 p-machine 上可能有：一個執行中的 task、數個 ready to run 的 task、
  數個在等 semaphore 的 task。ready task 排成一條佇列，每個 semaphore 也有一條
  等待佇列（可為空）；佇列內依 priority 排序。p-machine 暫存器 **`CURTSK`**
  永遠指向當前 task 的 TIB，**`READYQ`** 指向 ready 串列第一個 task（p.40）。

TIB 格式（Pascal 片段，手冊 p.41）：

```pascal
TIB = RECORD  {Task Information Block}
        Regs: PACKED RECORD
              Wait_Q:      TIB_Ptr;
              Prior:       byte;
              Flags:       byte;
              SP_Low:      Mem_Ptr;
              SP_Upr:      Mem_Ptr;
              SP:          Mem_Ptr;
              MP:          MSCW_Ptr;
              BP:          MSCW_Ptr;
              IPC:         integer;
              Env:         ERec_Ptr;
              ProcNum:     byte;
              TIBIOResult: byte;
              Hang_Ptr:    Sem_Ptr;
              M_Depend:    integer;
        END;
        MainTask:   Boolean;
        Start_MSCW: MSCW_Ptr;
      END;
```

欄位語意（手冊 p.41）：

- `SP` 是 p-machine Stack Pointer；`SP_Low`、`SP_Upr` 是本 task 的 SP 上下限。
- `MP`、`BP` 分別指向本 task 的區域與全域活動記錄。
- `IPC` 是 p-code Instruction Counter（段相對 byte 指標）；`ProcNum` 是執行中
  routine 的編號。
- `Prior` 是 task 的 priority，0..255，**值越小越急迫**。
- `Wait_Q`：task 等待執行或等待 semaphore 時使用，是 TIB 鏈結串列的一環。
- 等待 semaphore 時 `Hang_Ptr` 指向該 semaphore；沒在等則為 `NIL`。`Hang_Ptr`
  讓 task 被終止時能從 semaphore 等待佇列中移除。
- `Flags` 保留。
- （`Env`、`TIBIOResult`、`M_Depend`、`MainTask`、`Start_MSCW` 在本頁未個別說明，
  屬下一頁範圍。）

## 與 IV.2.1 的關係

本節內容全部出自 IV.0 手冊（1981 年 3 月），而 repo 研究的 SunDog 直譯器是
IV.2.1。手冊本身沒有記載 IV.0 與 IV.2.1 之間在 codefile 格式、SIB/E_Rec/TIB
結構上的差異，以下幾點只提示「可能不同、需以 IV.2.1 實物驗證」，不臆測差異內容：

- Segment dictionary 的 `Major_Version` 欄位列舉到 `VII`（手冊 p.28），說明此
  格式設計時已預留後續版本；IV.2.1 的 codefile 是否沿用同一 `Seg_Dict` 版面，
  待查證。
- 手冊 p.34–41 的 SIB、E_Rec、TIB 是作業系統（而非直譯器）層級的結構；SunDog
  這類應用磁碟上的 `SYSTEM.INTERP` 只是直譯器，不必然包含這些結構——能否從
  直譯器映像驗證，待查證。
- 手冊 p.33 的 `DataSize = 0xFFFF` 慣例（表示 native code）與 p.23 的 Linker
  info 公式都直接涉及 codefile 解析；若日後要寫 IV.2.1 codefile 解析器，應以
  實際 `.CODE` 檔驗證這兩處是否仍成立（待查證）。
