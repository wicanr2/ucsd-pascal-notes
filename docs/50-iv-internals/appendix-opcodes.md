# 附錄：IV.0 P-Machine Opcodes 官方表

> 出自 SofTech Microsystems《UCSD p-SYSTEM and UCSD PASCAL Version IV.0
> Internal Architecture Guide》（1981 年 3 月第一版）Appendix VI.B「P-Codes」，
> 印刷頁 p.138–142（PDF 頁 144–148）。同範圍內另有 Appendix A Glossary 末頁
> （p.137）與 Appendix C ASCII 表（p.143），本文僅摘錄與 opcode 表直接相關者。

結論先講：**這是 IV.0 官方的完整 p-code 表**，按功能分組列出全部指令，
編號為**十進位**（0–255，本文括號內換算成 `0x` 十六進位）。
短形式與 repo 裡從 SunDog（IV.2.1）直譯器反推出來的分佈**完全吻合**：
`SLDC` 0–31（`0x00`–`0x1f`）、`SLDL` 32–47（`0x20`–`0x2f`）、
`SLDO` 48–63（`0x30`–`0x3f`）、`SLLA` 96–103（`0x60`–`0x67`）、
`SSTL` 104–111（`0x68`–`0x6f`）、`SCXG` 112–119（`0x70`–`0x77`）、
`SIND` 120–127（`0x78`–`0x7f`）——與
[sundog-ivx-table.md](../30-opcode-tables/sundog-ivx-table.md) 反推出的短形式切法一致。

> 延伸閱讀：[本層索引](README.md)｜[實例：解出一份 1985 年 68000 直譯器的 opcode 表](../30-opcode-tables/sundog-ivx-table.md)

## 常數載入（手冊 p.138）

| 助記符 | 編號（十進位） | 編號（0x） | 官方說明 |
|---|---|---|---|
| `SLDC` | 0..31 | `0x00`–`0x1f` | Short Load Word Constant |
| `LDCN` | 152 | `0x98` | Load Constant NIL |
| `LDCB` | 128 | `0x80` | Load Constant Byte |
| `LDCI` | 129 | `0x81` | Load Constant Word |
| `LCO` | 130 | `0x82` | Load Constant Offset（手冊原文如此拼作「Contant」） |

## 區域變數（手冊 p.138）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `SLDL1` … `SLDL16` | 32 … 47 | `0x20`–`0x2f` | Short Load Local Word |
| `LDL` | 135 | `0x87` | Load Local Word |
| `SLLA1` … `SLLA8` | 96 … 103 | `0x60`–`0x67` | Short Load Local Address |
| `LLA` | 132 | `0x84` | Load Local Address |
| `SSTL1` … `SSTL8` | 104 … 111 | `0x68`–`0x6f` | Short Store Local Word |
| `STL` | 164 | `0xa4` | Store Local Word |

## 全域變數（手冊 p.138）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `SLDO1` … `SLDO16` | 48 … 63 | `0x30`–`0x3f` | Short Load Global Word |
| `LDO` | 133 | `0x85` | Load Global Word |
| `LAO` | 134 | `0x86` | Load Global Address |
| `SRO` | 165 | `0xa5` | Store Global Word |

## 中間層（intermediate）與跨段（extended）存取（手冊 p.138–139）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `SLOD1` | 173 | `0xad` | Short Load Intermediate Word |
| `SLOD2` | 174 | `0xae` | Short Load Intermediate Word |
| `LOD` | 137 | `0x89` | Load Intermediate Word |
| `LDA` | 136 | `0x88` | Load Intermediate Address |
| `STR` | 166 | `0xa6` | Store Intermediate Word |
| `LDE` | 154 | `0x9a` | Load Extended Word |
| `LAE` | 155 | `0x9b` | Load Extended Address |
| `STE` | 217 | `0xd9` | Store Extended Word |

`LDE`／`LAE`／`STE` 分別是 `0x9a`／`0x9b`／`0xd9`，正是 SunDog 驗證步驟中
拿遊戲程式碼對過的那三個跨段全域存取指令（手冊 p.138–139；對照
sundog-ivx-table.md 第 5 步）。

## 間接存取（手冊 p.139）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `SIND0` … `SIND7` | 120 … 127 | `0x78`–`0x7f` | Short Index and Load Word |
| `IND` | 230 | `0xe6` | Index and Load Word |
| `STO` | 196 | `0xc4` | Store Indirect |

## 多 word 與實數常數（手冊 p.139）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `LDC` | 131 | `0x83` | Load Multiple Word Constant |
| `LDM` | 208 | `0xd0` | Load Multiple Words |
| `STM` | 142 | `0x8e` | Store Multiple Words |
| `LDCRL` | 242 | `0xf2` | Load Real Constant |
| `LDRD` | 243 | `0xf3` | Load Real |
| `STRL` | 244 | `0xf4` | Store Real |

## 參數複製、位元組與 packed 欄位（手冊 p.139）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `CAP` | 171 | `0xab` | Copy Array Parameter |
| `CSP` | 172 | `0xac` | Copy String Parameter |
| `LDB` | 167 | `0xa7` | Load Byte |
| `STB` | 200 | `0xc8` | Store Byte |
| `LDP` | 201 | `0xc9` | Load a Packed Field |
| `STP` | 202 | `0xca` | Store into a Packed Field |
| `MOV` | 197 | `0xc5` | Move |
| `INC` | 231 | `0xe7` | Increment Field Pointer |
| `IXA` | 215 | `0xd7` | Index Array |
| `IXP` | 216 | `0xd8` | Index Packed Array |

## 邏輯與無號比較（手冊 p.139）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `LAND` | 161 | `0xa1` | Logical And |
| `LOR` | 160 | `0xa0` | Logical Or |
| `LNOT` | 229 | `0xe5` | Logical Not |
| `BNOT` | 159 | `0x9f` | Boolean Not |
| `LEUSW` | 180 | `0xb4` | Less Than or Equal Unsigned |
| `GEUSW` | 181 | `0xb5` | Greater Than or Equal Unsigned |

## 整數運算（手冊 p.140）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `ABI` | 224 | `0xe0` | Absolute Value Integer |
| `NGI` | 225 | `0xe1` | Negate Integer |
| `INCI` | 237 | `0xed` | Increment Integer |
| `DECI` | 238 | `0xee` | Decrement Integer |
| `ADI` | 162 | `0xa2` | Add Integers |
| `SBI` | 163 | `0xa3` | Subtract Integers |
| `MPI` | 140 | `0x8c` | Multiply Integers |
| `DVI` | 141 | `0x8d` | Divide Integers |
| `MODI` | 143 | `0x8f` | Modulo Integers |
| `CHK` | 203 | `0xcb` | Check Subrange Bounds |
| `EQUI` | 176 | `0xb0` | Equal Integer |
| `NEQI` | 177 | `0xb1` | Not Equal Integer |
| `LEQI` | 178 | `0xb2` | Less Than or Equal Integer |
| `GEQI` | 179 | `0xb3` | Greater Than or Equal Integer |

## 實數運算（手冊 p.140）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `FLT` | 204 | `0xcc` | Float Top-of-Stack |
| `TNC` | 190 | `0xbe` | Truncate Real |
| `RND` | 191 | `0xbf` | Round Real |
| `ABR` | 227 | `0xe3` | Absolute Value of Real |
| `NGR` | 228 | `0xe4` | Negate Real |
| `ADR` | 192 | `0xc0` | Add Reals |
| `SBR` | 193 | `0xc1` | Subtract Reals |
| `MPR` | 194 | `0xc2` | Multiply Reals |
| `DVR` | 195 | `0xc3` | Divide Reals |
| `EQREAL` | 205 | `0xcd` | Equal Real |
| `LEREAL` | 206 | `0xce` | Less Than or Equal Real |
| `GEREAL` | 207 | `0xcf` | Greater Than or Equal Real |

## 集合運算（手冊 p.140）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `ADJ` | 199 | `0xc7` | Adjust Set |
| `SRS` | 188 | `0xbc` | Build a Subrange Set |
| `INN` | 218 | `0xda` | Set Membership |
| `UNI` | 219 | `0xdb` | Set Union |
| `INT` | 220 | `0xdc` | Set Intersection |
| `DIF` | 221 | `0xdd` | Set Difference |
| `EQPWR` | 182 | `0xb6` | Equal Set |
| `LEPWR` | 183 | `0xb7` | Less Than or Equal Set |
| `GEPWR` | 184 | `0xb8` | Greater Than or Equal Set |

## 位元組陣列比較（手冊 p.140）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `EQBYT` | 185 | `0xb9` | Equal Byte Array |
| `LEBYT` | 186 | `0xba` | Less Than or Equal Byte Array |
| `GEBYT` | 187 | `0xbb` | Greater Than or Equal Byte Array |

## 跳躍（手冊 p.141）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `UJP` | 138 | `0x8a` | Unconditional Jump |
| `FJP` | 212 | `0xd4` | False Jump |
| `TJP` | 241 | `0xf1` | True Jump |
| `EFJ` | 210 | `0xd2` | Equal False Jump |
| `NFJ` | 211 | `0xd3` | Not Equal False Jump |
| `JPL` | 139 | `0x8b` | Unconditional Long Jump |
| `FJPL` | 213 | `0xd5` | False Long Jump |
| `XJP` | 214 | `0xd6` | Case Jump |

## 程序呼叫與返回（手冊 p.141）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `CPL` | 144 | `0x90` | Call Local Procedure |
| `CPG` | 145 | `0x91` | Call Global Procedure |
| `SCPI1` | 239 | `0xef` | Short Call Intermediate Procedure |
| `SCPI2` | 240 | `0xf0` | Short Call Intermediate Procedure |
| `CPI` | 146 | `0x92` | Call Intermediate Procedure |
| `CXL` | 147 | `0x93` | Call Local External Procedure |
| `SCXG1` … `SCXG8` | 112 … 119 | `0x70`–`0x77` | Short Call External Global Procedure |
| `CXG` | 148 | `0x94` | Call Global External Procedure |
| `CXI` | 149 | `0x95` | Call Intermediate External Procedure |
| `CPF` | 151 | `0x97` | Call Formal Procedure |
| `RPU` | 150 | `0x96` | Return from Procedure |
| `LSL` | 153 | `0x99` | Load Static Link |
| `BPT` | 158 | `0x9e` | Breakpoint |

## 並行（semaphore）、字串、堆疊雜項（手冊 p.141–142）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `SIGNAL` | 222 | `0xde` | Signal |
| `WAIT` | 223 | `0xdf` | Wait |
| `EQSTR` | 232 | `0xe8` | Equal String |
| `LESTR` | 233 | `0xe9` | Less Than or Equal String |
| `GESTR` | 234 | `0xea` | Greater Than or Equal String |
| `ASTR` | 235 | `0xeb` | Assign String |
| `CSTR` | 236 | `0xec` | Check String Index |
| `LPR` | 157 | `0x9d` | Load Processor Register |
| `SPR` | 209 | `0xd1` | Store Processor Register |
| `DUP1` | 226 | `0xe2` | Duplicate One Word |
| `DUPR` | 198 | `0xc6` | Duplicate Real |
| `SWAP` | 189 | `0xbd` | Swap |
| `NOP` | 156 | `0x9c` | No Operation |
| `NAT` | 168 | `0xa8` | Native Code |
| `NAT-INFO` | 169 | `0xa9` | Native Code Information |

## 保留（手冊 p.142）

| 助記符 | 編號 | 0x | 官方說明 |
|---|---|---|---|
| `RESERVE1` … `RESERVE6` | 250 … 255 | `0xfa`–`0xff` | reserved |

## 編號空洞

把上表全部編號排開，官方表**沒有列出**的編號是（十進位／0x）：

- 64–95（`0x40`–`0x5f`）——32 個，正好是 `SLDO` 短形式群與 `SLLA` 群之間的整段留白
- 170（`0xaa`）
- 175（`0xaf`）
- 245–249（`0xf5`–`0xf9`）

對照 SunDog IV.2.1 直譯器，指向錯誤處理常式的「未實作」槽正是
`0x40`–`0x5f`、`0xaa`、`0xaf`、`0xf5`–`0xff`（sundog-ivx-table.md 第 3 步）。
IV.0 表裡 `0xf5`–`0xf9` 未列出而 `0xfa`–`0xff` 標「reserved」；IV.2.1 把整段
`0xf5`–`0xff` 都視為未使用。兩邊在「這些槽沒有指令」這點上一致。

## Appendix A / C 摘記

- Appendix A Glossary 末頁（p.137）收尾詞條：`SEG-RELATIVE`、`STATIC`、
  `SUBSIDIARY SEGMENT`（`SEG_TYPE` 為 `PROC_SEG` 或 `SEPRT_SEG` 的 segment，
  沒有 segment reference list）、`TOS`（top of stack）、`UPWARD COMPATIBILITY`、
  `WORD`（16 bits，偶位元組邊界對齊，最高位元組位置依目標機 byte sex 而定）、
  `WORD POINTER`、`ZERO-FILLED`。
- Appendix C（p.143）是標準 ASCII 對照表（十進位／八進位／十六進位／字元），
  0–127，與通用 ASCII 表相同，此處不重抄。

## 與 IV.2.1 的關係

- 本表是 **IV.0**（1981 年 3 月）的官方編號；repo 研究的 SunDog 直譯器是
  **IV.2.1**。短形式的分配（`SLDC`/`SLDL`/`SLDO`/`SLLA`/`SSTL`/`SCXG`/`SIND`
  各群範圍）在兩邊逐項吻合，`LDE`/`LAE`/`STE`（`0x9a`/`0x9b`/`0xd9`）也吻合，
  顯示 IV.0 → IV.2.1 之間這些編碼是穩定的。
- 本表只給「編號、助記符、一句英文說明」，**沒有運算元格式與堆疊效果的細節**；
  那些在手冊前面各章節（待其他篇筆記整理）。各指令吃幾個位元組的運算元，
  待查證。
- IV.2.1 是否在這張表之外新增或更動指令（例如 64–95 那段留白在 IV.2.1
  仍指向錯誤處理，代表 IV.2.1 也沒有用它），手冊沒有寫，待查證。
