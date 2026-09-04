# IV 版指令逐條語意

> 來源：《UCSD p-SYSTEM and UCSD PASCAL Version IV.0 Internal Architecture Guide》
> （SofTech Microsystems，1981 年 3 月）第 II 章「The P-Machine」，
> 節 II.4.2.2「The Individual P-Code Instructions」，印刷頁 52–70
> （對應掃描 PDF 頁 58–76）。

結論先講：這一節是 IV.0 指令集的**權威逐條定義**。每條指令列出
助記符、十進位 opcode 值、運算元、堆疊效應（寫成 `<執行前>:<執行後>` 的形式）與語意。
手冊裡的 opcode 編號一律是**十進位**；本文照抄十進位值，換算十六進位時另加括號。

> 延伸閱讀：[本層索引](README.md)｜[opcode 表與版本陷阱](../30-opcode-tables/version-traps.md)｜[IV.0 官方 opcode 表](appendix-opcodes.md)

## 閱讀慣例（手冊全節通用）

- 堆疊效應欄 `<a,b>:<c>` 表示執行前堆疊頂依序是 a、b（TOS 在最左），執行後留下 c。
  TOS = top of stack，TOS-1 = 次頂。
- 運算元欄的代號：`UB` = 一位元組無號數、`B` = 變長運算元（big operand）、
  `SB` = 一位元組有號數、`W` = 一個 word（兩位元組）、`DB` = 靜態鏈回溯層數。
  （代號出現於各條指令行，手冊 p.52–70；各代號的正式定義在此節之前的編碼說明頁。）
- 「byte sex」：segment 的位元組序若與主機相反，若干指令在 mode 為 2 時
  會先交換每個 word 的位元組再使用（手冊 p.55、p.58、p.63–64、p.65）。
- Stack fault 與 segment fault 是兩種不同的執行期錯誤，各指令會分別註明觸發條件。

## II.4.2.2.1 Constant One-Word Loads（手冊 p.52）

| 助記符 | opcode（十進位） | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `SLDC` | 0..31（0x00–0x1F） | — | `<>:<word>` | Short Load Word Constant。把 opcode 本身推上堆疊，高位元組補零。 |
| `LDCN` | 152（0x98） | — | `<>:<NIL>` | Load Constant NIL。推 NIL；此值依處理器而異。 |
| `LDCB` | 128（0x80） | UB | `<>:<word>` | Load Constant Byte。推 UB，高位元組補零。 |
| `LDCI` | 129（0x81） | W | `<>:<word>` | Load Constant Word。推 W。 |
| `LCO` | 130（0x82） | B | `<>:<offset>` | Load Constant Offset。B 是本段常數池的 word 偏移；轉成段相對 word 偏移後推上堆疊（位元組定址機器上轉成位元組偏移）。 |

## II.4.2.2.2 Local One-Word Loads and Stores（手冊 p.52–53）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `SLDL1`–`SLDL16` | 32–47（0x20–0x2F） | — | `<>:<word>` | Short Load Local Word。取本地活動記錄偏移 x 的 word 推上堆疊。 |
| `LDL` | 135（0x87） | B | `<>:<word>` | Load Local Word。取本地活動記錄偏移 B 的 word 推上堆疊。 |
| `SLLA1`–`SLLA8` | 96–103（0x60–0x67） | — | `<>:<addr>` | Short Load Local Address。推本地活動記錄指定偏移的位址。 |
| `LLA` | 132（0x84） | B | `<>:<addr>` | Load Local Address。算本地活動記錄偏移 B 的 word 位址並推上。 |
| `SSTL1`–`SSTL8` | 104–111（0x68–0x6F） | — | `<word>:<>` | Short Store Local Word。把 TOS 存入本地活動記錄指定偏移。 |
| `STL` | 164（0xA4） | B | `<word>:<>` | Store Local Word。把 TOS 存入本地活動記錄偏移 B 的 word。 |

## II.4.2.2.3 Global One-Word Loads and Store（手冊 p.53）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `SLDO1`–`SLDO16` | 48–63（0x30–0x3F） | — | `<>:<word>` | Short Load Global Word。取本段全域資料區偏移 x 的 word 推上。 |
| `LDO` | 133（0x85） | B | `<>:<word>` | Load Global Word。取本段全域資料區偏移 B 的 word 推上。 |
| `LAO` | 134（0x86） | B | `<>:<addr>` | Load Global Address。推本段全域資料區偏移 B 的 word 位址。 |
| `SRO` | 165（0xA5） | B | `<word>:<>` | Store Global Word。把 TOS 存入本段全域資料區偏移 B 的 word。 |

## II.4.2.2.4 Intermediate One-Word Loads and Store（手冊 p.53–54）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `SLOD1` / `SLOD2` | 173 / 174（0xAD / 0xAE） | B | `<>:<word>` | Short Load Intermediate Word。推本地活動記錄的父層（SLOD1）或祖父層（SLOD2）活動記錄裡偏移 B 的 word。 |
| `LOD` | 137（0x89） | DB, B | `<>:<word>` | Load Intermediate Word。DB 是要沿靜態鏈回溯的層數；推該活動記錄偏移 B 的 word。 |
| `LDA` | 136（0x88） | DB, B | `<>:<addr>` | Load Intermediate Address。DB 同 LOD；推該活動記錄偏移 B 的位址。 |
| `STR` | 166（0xA6） | DB, B | `<word>:<>` | Store Intermediate Word。把 TOS 存入 DB 指定的活動記錄偏移 B。 |

## II.4.2.2.5 Extended One-Word Loads and Store（手冊 p.54）

跨段的全域存取：UB 是本機 segment 編號，B 是該段全域資料區的 word 偏移。

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `LDE` | 154（0x9A） | UB, B | `<>:<word>` | Load Extended Word。推 segment UB 全域資料區偏移 B 的 word。 |
| `LAE` | 155（0x9B） | UB, B | `<>:<addr>` | Load Extended Address。推該 word 的位址。 |
| `STE` | 217（0xD9） | UB, B | `<word>:<>` | Store Extended Word。把 TOS 存入該 word。 |

## II.4.2.2.6 Indirect One-Word Loads and Store（手冊 p.54）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `SIND0`–`SIND7` | 120–127（0x78–0x7F） | — | `<addr>:<word>` | Short Index and Load Word。TOS 是某記錄的位址；把它換成該記錄第 x 個 word。 |
| `IND` | 230（0xE6） | B | `<addr>:<word>` | Index and Load Word。TOS 是記錄位址；換成該記錄第 B 個 word。 |
| `STO` | 196（0xC4） | — | `<addr,word>:<>` | Store Indirect。把 TOS 存入 TOS-1 指向的 word。 |

## II.4.2.2.7 Multiple-Word Loads and Stores（手冊 p.55）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `LDC` | 131（0x83） | UB_1, B, UB_2 | `<>:<word-block>` | Load Multiple Word Constant。B 是本段常數池的 word 偏移；把從該偏移起的 UB_2 個 word 推上求值堆疊。若 mode（UB_1）為 2 且本段 byte sex 與主機相反，推入時逐 word 交換位元組。堆疊可用空間少於 B+20 個 word 時發 Stack fault。（按原文：「If less than B+20 words available」——以 UB_2 個 word 推入卻寫 B+20，可能是手冊原文如此；待查證） |
| `LDM` | 208（0xD0） | UB | `<addr>:<word-block>` | Load Multiple Words。TOS 指向 UB 個 word 的區塊開頭；把整塊推上堆疊，保持原 word 順序。可用空間少於 UB+20 個 word 時發 Stack fault。 |
| `STM` | 142（0x8E） | UB | `<addr,word-block>:<>` | Store Multiple Words。TOS 是 UB 個 word 的區塊；把區塊從堆疊搬到 TOS-1 位址起的目的地，保持順序。 |
| `LDCRL` | 242（0xF2） | B | `<>:<real>` | Load Real Constant。推本段常數池索引 B 指定的實數常數。保證是主機原生 byte sex，不需翻轉位元組。 |
| `LDRL` | 243（0xF3） | — | `<addr>:<real>` | Load Real。TOS 是實數變數位址；換成該變數的值。 |
| `STRL` | 244（0xF4） | — | `<addr,real>:<>` | Store Real。TOS 是實數值，TOS-1 是位址；把值存入該位址。 |

## II.4.2.2.8 String and Packed Array of Char Parameter Copying（手冊 p.56）

呼叫 string 或 packed array of char 型別的**傳值參數**時，呼叫方產生一個
「parameter descriptor」：一個 2-word 記錄。第一個 word（低位址）是 NIL，
或指向一個 E_Rec 的指標。若第一個 word 是 NIL，第二個 word 是參數的位址；
若指向 E_Rec，第二個 word 是相對該指定 segment 的偏移（此偏移由 LCO 指令產生）。
被呼叫方用 `CAP` 或 `CSP` 把參數複製進自己的活動記錄。

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `CAP` | 171（0xAB） | B | `<addr,addr>:<>` | Copy Array Parameter。TOS 是 packed array of characters 的參數描述符位址。若描述符指定的 segment 不在記憶體，發 segment fault；否則把來源（共 B 個 word）複製到 TOS-1 的目的位址。 |
| `CSP` | 172（0xAC） | UB | `<addr,addr>:<>` | Copy String Parameter。TOS 是 string 的參數描述符位址。segment 不在記憶體則 segment fault；否則比較指定字串的動態長度與 UB（目的形式參數的宣告大小，單位 byte），來源長於目的容量則發 string overflow fault，否則按來源長度複製到 TOS-1 位址。 |

## II.4.2.2.9 Byte Load and Store（手冊 p.57）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `LDB` | 167（0xA7） | — | `<byte-ptr>:<word>` | Load Byte。TOS 是 byte 指標；取出所指 byte，放進 word 的低位、高位元組補零後推上。 |
| `STB` | 200（0xC8） | — | `<byte-ptr,word>:<>` | Store Byte。把 byte TOS 存入 byte 指標 TOS-1 指定的位置。 |

## II.4.2.2.10 Packed Field Load and Store（手冊 p.57）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `LDP` | 201（0xC9） | — | `<pack-ptr>:<word>` | Load a Packed Field。把 TOS 的 packed field 指標換成它所指的欄位；推上前欄位靠右對齊、左側補零。 |
| `STP` | 202（0xCA） | — | `<pack-ptr,word>:<>` | Store into a Packed Field。TOS 是靠右對齊的資料，TOS-1 是 packed field 指標；把 TOS 存入該欄位。 |

## II.4.2.2.11 Record and Array Indexing and Assignment（手冊 p.58）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `MOV` | 197（0xC5） | UB, B | `<addr,addr>:<>` | Move。把 B 個 word 從 TOS 指定的來源搬到 TOS-1 指定的目的。TOS 是 word 區塊的位址（UB 為 0 時）或是本段常數 word 區塊的偏移。UB 為 2 且本段 byte sex 與主機相反時，搬運時逐 word 交換位元組。 |
| `INC` | 231（0xE7） | B | `<addr>:<addr>` | Increment Field Pointer。word 指標 TOS 往前加 B 個 word，結果指標推上。 |
| `IXA` | 215（0xD7） | B | `<addr,word>:<addr>` | Index Array。TOS 是整數索引，TOS-1 是陣列基底 word 指標，B 是元素大小（word 數）。推指向該元素的 word 指標。 |
| `IXP` | 216（0xD8） | UB_1, UB_2 | `<addr,word>:<pack-ptr>` | Index Packed Array。TOS 是整數索引，TOS-1 是陣列基底 word 指標；UB_1 是每 word 的元素數，UB_2 是欄位寬度（bit 數）。算出 packed field 指標並推上。 |

## II.4.2.2.12 Logical Operators（手冊 p.59）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `LAND` | 161（0xA1） | — | `<word,word>:<word>` | Logical And。TOS AND 進 TOS-1。 |
| `LOR` | 160（0xA0） | — | `<word,word>:<word>` | Logical Or。TOS OR 進 TOS-1。 |
| `LNOT` | 229（0xE5） | — | `<word>:<word>` | Logical Not。取 TOS 的 1 補數（逐位元反轉）。 |
| `BNOT` | 159（0x9F） | — | `<Bool>:<Bool>` | Boolean Not。反轉最低位元，其餘位元清 0。 |
| `LEUSW` | 180（0xB4） | — | `<word,word>:<Bool>` | Less Than or Equal Unsigned。推無號比較 TOS-1 <= TOS 的布林結果。 |
| `GEUSW` | 181（0xB5） | — | `<word,word>:<Bool>` | Greater Than or Equal Unsigned。推無號比較 TOS-1 >= TOS 的布林結果。 |

## II.4.2.2.13 Integer Arithmetic（手冊 p.59–60）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `ABI` | 224（0xE0） | — | `<int>:<int>` | Absolute Value Integer。取 TOS 的絕對值；TOS 為 -32768 時結果未定義。 |
| `NGI` | 225（0xE1） | — | `<int>:<int>` | Negate Integer。取 TOS 的 2 補數。 |
| `INCI` | 237（0xED） | — | `<int>:<int>` | Increment Integer。TOS 加 1。 |
| `DECI` | 238（0xEE） | — | `<int>:<int>` | Decrement Integer。TOS 減 1。 |
| `ADI` | 162（0xA2） | — | `<int,int>:<int>` | Add Integers。TOS 加進 TOS-1。 |
| `SBI` | 163（0xA3） | — | `<int,int>:<int>` | Subtract Integers。TOS-1 減 TOS。 |
| `MPI` | 140（0x8C） | — | `<int,int>:<int>` | Multiply Integers。TOS 乘進 TOS-1；結果超過 16 bit 可能 overflow。 |
| `DVI` | 141（0x8D） | — | `<int,int>:<int>` | Divide Integers。TOS-1 除以 TOS，推商；TOS 為 0 時發 execution error。 |
| `MODI` | 143（0x8F） | — | `<int,int>:<int>` | Modulo Integers。TOS-1 除以 TOS，推餘數。 |
| `CHK` | 203（0xCB） | — | `<int,int,int>:<int>` | Check Subrange Bounds。確認 TOS-1 <= TOS-2 <= TOS，把 TOS-2 留在堆疊上；條件不符則發 runtime error。 |
| `EQUI` | 176（0xB0） | — | `<int,int>:<Bool>` | Equal Integer。推整數比較 TOS-1 = TOS 的布林結果。 |
| `NEQI` | 177（0xB1） | — | `<int,int>:<Bool>` | Not Equal Integer。推 TOS-1 <> TOS 的布林結果。 |
| `LEQI` | 178（0xB2） | — | `<int,int>:<bool>` | Less than or Equal Integer。推 TOS-1 <= TOS 的布林結果。 |
| `GEQI` | 179（0xB3） | — | `<int,int>:<bool>` | Greater than or Equal Integer。推 TOS-1 >= TOS 的布林結果。 |

## II.4.2.2.14 Real Arithmetic（手冊 p.60–61）

本節開頭註明：所有 overflow 與 underflow 都發 runtime error。

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `FLT` | 204（0xCC） | — | `<int>:<real>` | Float Top-of-Stack。把整數 TOS 轉成浮點數。 |
| `TNC` | 190（0xBE） | — | `<real>:<int>` | Truncate Real。把實數 TOS 截斷成整數。 |
| `RND` | 191（0xBF） | — | `<real>:<int>` | Round Real。把實數 TOS 四捨五入成整數。 |
| `ABR` | 227（0xE3） | — | `<real>:<real>` | Absolute Value of Real。取實數 TOS 的絕對值。 |
| `NGR` | 228（0xE4） | — | `<real>:<real>` | Negate Real。實數 TOS 變號。 |
| `ADR` | 192（0xC0） | — | `<real,real>:<real>` | Add Reals。TOS 加進 TOS-1。 |
| `SBR` | 193（0xC1） | — | `<real,real>:<real>` | Subtract Reals。TOS-1 減 TOS。 |
| `MPR` | 194（0xC2） | — | `<real,real>:<real>` | Multiply Reals。TOS 乘進 TOS-1。 |
| `DVR` | 195（0xC3） | — | `<real,real>:<real>` | Divide Reals。TOS-1 除以 TOS；TOS 為 0 時發 runtime error。 |
| `EQREAL` | 205（0xCD） | — | `<real,real>:<Bool>` | Equal Real。推實數比較 TOS-1 = TOS 的布林結果。 |
| `LEREAL` | 206（0xCE） | — | `<real,real>:<Bool>` | Less than or Equal Real。推 TOS-1 <= TOS 的布林結果。 |
| `GEREAL` | 207（0xCF） | — | `<real,real>:<Bool>` | Greater than or Equal Real。推 TOS-1 >= TOS 的布林結果(手冊原文印成「TOS-1 <= TOS」，依指令名判斷應為 >=；待查證)。 |

## II.4.2.2.15 Set Operations（手冊 p.61–62）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `ADJ` | 199（0xC7） | UB | `<set>:<word-block>` | Adjust Set。把 TOS 的集合調整成佔 UB 個 word：擴張（在 TOS 與 TOS-1 之間補零）或壓縮（砍掉集合的高位 word），並丟棄其長度 word。之後若堆疊可用空間少於 20 個 word，發 Stack fault。 |
| `SRS` | 188（0xBC） | — | `<int,int>:<set>` | Build a Subrange Set。整數 TOS 與 TOS-1 必須落在 [0..4079]，否則發 runtime error；否則推該範圍的集合。TOS-1 > TOS 時推空集合。執行前若堆疊可用空間少於 20 個 word，發 Stack fault。 |
| `INN` | 218（0xDA） | — | `<int,set>:<Bool>` | Set Membership。推 TOS-1 IN TOS 的布林結果。 |
| `UNI` | 219（0xDB） | — | `<set,set>:<set>` | Set Union。推 TOS 與 TOS-1 的聯集（TOS OR TOS-1）。 |
| `INT` | 220（0xDC） | — | `<set,set>:<set>` | Set Intersection。推 TOS 與 TOS-1 的交集（TOS AND TOS-1）。 |
| `DIF` | 221（0xDD） | — | `<set,set>:<set>` | Set Difference。推 TOS 與 TOS-1 的差集（TOS-1 AND NOT TOS）。 |
| `EQPWR` | 182（0xB6） | — | `<set,set>:<bool>` | Equal Set。推集合比較 TOS-1 = TOS 的布林結果。 |
| `LEPWR` | 183（0xB7） | — | `<set,set>:<Bool>` | Less than or Equal Set。TOS-1 是 TOS 的子集則推 true，否則 false。 |
| `GEPWR` | 184（0xB8） | — | `<set,set>:<Bool>` | Greater than or Equal Set。TOS 是 TOS-1 的父集則推 true，否則 false（手冊原文「TOS is a superset of TOS」，依指令名應是 TOS-1 是 TOS 的 superset 之誤植；待查證）。 |

## II.4.2.2.16 Byte Array Comparisons（手冊 p.63–64）

三條指令結構相同：TOS 與 TOS-1 各自指向一個 byte array（對應的 UB 為 0 時）
或是本段常數 byte array 的偏移；B 是該 array 的大小（byte 數）；UB_1、UB_2
是 mode 旗標，分別對應 TOS 與 TOS-1。若段的 byte sex 與主機相反且對應 mode
為 2，比較前先交換該運算元每個 word 的位元組。

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `EQBYT` | 185（0xB9） | UB_1, UB_2, B | `<addr\|offset,addr\|offset>:<Bool>` | Equal Byte Array。推 byte array 比較 TOS-1 = TOS 的布林結果。 |
| `LEBYT` | 186（0xBA） | UB_1, UB_2, B | 同上 | Less than or Equal Byte Array。推 TOS-1 <= TOS 的布林結果。 |
| `GEBYT` | 187（0xBB） | UB_1, UB_2, B | 同上 | Greater than or Equal Byte Array。推比較結果(手冊原文比較式印成「TOS-1 <= TOS」，依指令名應為 >=；待查證)。 |

## II.4.2.2.17 Jumps（手冊 p.64–65）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `UJP` | 138（0x8A） | SB | `<>:<>` | Unconditional Jump。跳 SB 個 byte 的偏移。 |
| `FJP` | 212（0xD4） | SB | `<Bool>:<>` | False Jump。TOS 為 false 則跳 SB 個 byte。 |
| `TJP` | 241（0xF1） | SB | `<Bool>:<>` | True Jump。TOS 為 true 則跳 SB 個 byte。 |
| `EFJ` | 210（0xD2） | SB | `<int,int>:<>` | Equal False Jump。TOS <> TOS-1 時跳 SB 個 byte。 |
| `NFJ` | 211（0xD3） | SB | `<int,int>:<>` | Not Equal False Jump。TOS = TOS-1 時跳 SB 個 byte。 |
| `JPL` | 139（0x8B） | W | `<>:<>` | Unconditional Long Jump。從目前位置跳 W 個 byte。 |
| `FJPL` | 213（0xD5） | W | `<Bool>:<>` | False Long Jump。TOS 為 false 則從目前位置跳 W 個 byte。 |
| `XJP` | 214（0xD6） | B | `<int>:<>` | Case Jump。本段常數池 word 偏移 B 處的第一個 word W1（word 對齊）是 case 表的最小索引，下一個 word W2 是最大索引，再接 (W2-W1)+1 個 word 是 case 表。段 byte sex 與主機相反時這些 word 要先交換位元組。若 TOS（實際索引）在 W1..W2 內，則從目前位置跳 W3 個 word，W3 是 TOS 所指 word 的內容；否則不做任何事。 |

## II.4.2.2.18 Routine Calls and Returns（手冊 p.65–67）

全體程序呼叫指令的共同規則（手冊 p.65）：

- MSCW 與 Datasize word 推上堆疊後，檢查 Stack 與 Codepool 之間是否還有
  至少 40 個 word 可用，不足則發 Stack fault。
- 所有呼叫外部程序的指令，若目標 segment 不在記憶體，發 segment fault。

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `CPL` | 144（0x90） | UB | `<param>:<activation>` | Call Local Procedure。呼叫程序 UB——目前執行中程序的直接子程序、同段。新 MSCW 的靜態鏈設為舊 MP。 |
| `CPG` | 145（0x91） | UB | `<param>:<activation>` | Call Global Procedure。呼叫程序 UB——lex level 1、同段。新 MSCW 的靜態鏈設為 BASE。 |
| `SCPI1` / `SCPI2` | 239 / 240（0xEF / 0xF0） | UB | `<param>:<activation>` | Short Call Intermediate Procedure。靜態鏈設為指向呼叫環境的語彙父層（SCPI1）或祖父層（SCPI2），然後呼叫程序 UB。 |
| `CPI` | 146（0x92） | DB, UB | `<param>:<activation>` | Call Intermediate Procedure。呼叫程序 UB——lex level 比目前低 DB 層、同段。以該活動記錄的靜態鏈作為新 MSCW 的靜態鏈。 |
| `CXL` | 147（0x93） | UB_1, UB_2 | `<param>:<activation>` | Call Local External Procedure。呼叫程序 UB_2——目前程序的直接子程序、在 segment UB_1。 |
| `SCXG1`–`SCXG8` | 112–119（0x70–0x77） | UB | `<param>:<activation>` | Short Call External Global Procedure。segment 號由 opcode 指定（1–8），UB 是程序號。SCXG1 可能指向內嵌在直譯器裡的程序，此時由一張直譯器表格給出程序位置。 |
| `CXG` | 148（0x94） | UB_1, UB_2 | `<param>:<activation>` | Call Global External Procedure。呼叫程序 UB_2——lex level 1、在 segment UB_1。segment 號為 1 時程序碼可能內嵌在直譯器，由直譯器表格給出位置。 |
| `CXI` | 149（0x95） | UB_1, DB, UB_2 | `<param>:<activation>` | Call Intermediate External Procedure。呼叫程序 UB_2——lex level 比目前低 DB 層、在 segment UB_1。 |
| `CPF` | 151（0x96） | — | `<param,proc-ptr>:<activation>` | Call Formal Procedure。TOS 是程序號，TOS-1 是 E_Rec 指標，TOS-2 是靜態鏈。呼叫所指程序。 |
| `RPU` | 150（0x97） | B | `<activation>:<func>` | Return from Procedure。從 MSCW 回復呼叫程序的狀態並丟棄之；把 MSCW 彈出堆疊；再從堆疊削掉 B 個 word，留下函數值（若有）。若返回不同的 segment(Mark Stack 的 E_Rec <> 目前的 E_Rec)，必要時發 segment fault。若 MSCW 裡的程序號 < 0，返回該程序的 EXITIC 而不是 MSCW 的 IPC。 |
| `LSL` | 153（0x99） | DB | `<>:<addr>` | Load Static Link onto Stack。DB 是要回溯的靜態鏈數；推該靜態鏈。 |
| `BPT` | 158（0x9E） | — | `<>:<activation>` | Breakpoint。無條件呼叫 execution error 程序。 |

## II.4.2.2.19 Concurrency Support（手冊 p.68）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `SIGNAL` | 222（0xDE） | — | `<addr>:<>` | Signal。TOS 是 semaphore 位址；對它發 signal。 |
| `WAIT` | 223（0xDF） | — | `<addr>:<>` | Wait。TOS 是 semaphore 位址；在它上面等待。 |

## II.4.2.2.20 String Instructions（手冊 p.68–69）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `EQSTR` | 232（0xE8） | UB_1, UB_2 | `<addr\|offset,addr\|offset>:<Bool>` | Equal String。TOS 與 TOS-1 各指向一個 string 變數（對應 UB 為 0 時）或本段常數字串的偏移；UB_1、UB_2 分別對應 TOS、TOS-1。推字串比較 TOS-1 = TOS 的布林結果。 |
| `LESTR` | 233（0xE9） | UB_1, UB_2 | 同上 | Less or Equal String。推 TOS-1 <= TOS 的布林結果。 |
| `GESTR` | 234（0xEA） | UB_1, UB_2 | 同上 | Greater or Equal String。推 TOS-1 >= TOS 的布林結果。 |
| `ASTR` | 235（0xEB） | UB_1, UB_2 | `<addr,addr\|offset>:<>` | Assign String。TOS-1 是目的 string 變數位址，UB_2 是該字串的宣告大小。TOS 是賦值來源：mode（UB_1）為 0 時是 string 變數位址，否則是本段字串常數的偏移。來源動態長度超過目的宣告大小則發 string overflow fault；否則複製過去。 |
| `CSTR` | 236（0xEC） | — | `<>:<>` | Check String Index。TOS-1 是 string 變數位址，TOS 是索引。檢查索引在 1 與該變數目前動態長度之間，否則發 range-check execution error。 |

## II.4.2.2.21 Miscellaneous Instructions（手冊 p.69–70）

| 助記符 | opcode | 運算元 | 堆疊 | 語意 |
|---|---|---|---|---|
| `LPR` | 157（0x9D） | — | `<int>:<word>` | Load Processor Register。TOS 是暫存器號；推所指暫存器內容（SPR 亦同此編號）：a) 暫存器號為正：它是目前 TIB 的 word 索引；b) 為負：-1 = 指向目前執行中 task 的 TIB 的指標，-2 = 目前的 E_Vec_P，-3 = 指向 ready queue 開頭 TIB 的指標。 |
| `SPR` | 209（0xD1） | — | `<int,word>:<>` | Store Processor Register。TOS-1 是暫存器號（定義同 LPR）；把 TOS 存入所指暫存器。 |
| `DUP1` | 226（0xE2） | — | `<word>:<word,word>` | Duplicate One Word。複製 TOS 上的一個 word。 |
| `DUPR` | 198（0xC6） | — | `<word-block>:<word-block>` | Duplicate Real。複製 TOS 上的實數。 |
| `SWAP` | 189（0xBD） | — | `<word,word>:<word,word>` | Swap。交換 TOS 與 TOS-1。 |
| `NOP` | 156（0x9C） | — | `<>:<>` | No Operation。繼續執行。 |
| `NAT` | 168（0xA8） | — | `<>:<>` | Native Code。把控制權交給緊接此指令之後的原生碼；細節依機器而定。 |
| `NAT-INFO` | 169（0xA9） | B | `<>:<>` | Native Code Information。忽略 p-code 流接下來 B 個 byte。這些資訊供原生碼生成使用；把它當成長形式的 NOP。 |
| `RESERVE1`–`RESERVE6` | 250–255（0xFA–0xFF） | — | — | 保留給編譯器用來標識內嵌的編譯器指令；程式不得自行產生這些碼。 |

## 與 IV.2.1 的關係

本節是 IV.0（1981）的定義；本 repo 研究的 SunDog 直譯器是 IV.2.1。
就短形式而言，兩版已能直接對照：IV.0 的 `SLDC` 0..31、`SLDL` 32–47、
`SLDO` 48–63、`SLLA` 96–103、`SSTL` 104–111、`SCXG` 112–119、
`SIND` 120–127（手冊 p.52–54、p.66），與
[sundog-ivx-table.md](../30-opcode-tables/sundog-ivx-table.md)從 IV.2.1
`SYSTEM.INTERP` 反推出的編碼區段逐格吻合——短形式的切法在 IV.0→IV.2.1
之間沒有變動。`LDE`/`LAE`/`STE` = 154/155/217（手冊 p.54）也與 IV.2.1 直譯器裡
`0x9a`/`0x9b`/`0xd9` 三兄弟的語意一致。至於其餘 opcode 是否有 IV.0 與
IV.2.1 之間的增刪改號，手冊未提及，需逐條與 IV.2.1 的表對照才能確認（待查證）。

## 待查證清單

- `LDC` 的 Stack fault 條件原文寫「B+20 words」，但推入量是 UB_2 個 word，
  疑為 UB_2+20 之誤植（手冊 p.55）。
- `GEREAL` 與 `GEBYT` 手冊原文的比較式皆印成 `TOS-1 <= TOS`，依指令名
  應為 `>=`（手冊 p.61、p.64）。
- `GEPWR` 手冊原文寫「push true if TOS is a superset of TOS」，顯然是
  排版錯誤；正確形式待查證（手冊 p.62）。
- `LEQI`/`GEQI`/`EQPWR` 的堆疊結果手冊印成小寫 `<bool>`，與他處 `<Bool>` 不一致，
  屬排版層面的差異（手冊 p.60、p.62）。
- 本節未出現 opcode 245–249（0xF5–0xF9）與 170（0xAA）、175（0xAF）等號碼的定義；
  它們在 IV.0 是否保留、或定義在本節範圍外（如作業系統介面指令），待查證。
