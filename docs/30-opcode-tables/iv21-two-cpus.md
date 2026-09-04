# 同一版、兩個 CPU：IV.2.1 的 68000 版與 8086 版

[README 的邊界](../../README.md#邊界)一直掛著一條沒查證的話：**同版本不同 CPU 的移植是否完全一致**。
現在有第二份 IV.2.1 直譯器可以對——1984 年 DOS 版 p-system 磁碟裡的 `SYSTEM.PME.86`。

> 延伸閱讀：[逐格對照：IV.0 官方表 × IV.2.1 dispatch 表](iv0-vs-iv21.md)｜
> [逐條驗證：98 個處理常式](iv21-routine-audit.md)｜
> [packed 欄位](../20-pcode-encoding/packed-fields.md)

結論先講：**opcode 編號完全一致——256 格裡只有一格分配不同。但實作差很多**，
而且有三處是行為上的實質差異，不只是寫法。
所以「拿一份 IV.x 的表去讀另一份 IV.x 的 p-code」在**編號**上安全，在**行為**上不安全。

## 素材

`psys21`（1984 年的 DOS hosted p-system）三個 `.VOL` 磁碟映像。
用 IV.0 手冊 p.125 的目錄版面就能解開——`tools/read-vol.py` 是那份格式的實作：

```
volume "PSYSTEM"  1000 blocks  29 files
  SYSTEM.PME.86      blk    6–38     16384 B
  SYSTEM.PASCAL      blk   68–204    69632 B
  SYSTEM.COMPILER    blk  693–803    56320 B
  ...
```

`SYSTEM.PME.86` 就是目標：**PME = P-Machine Emulator，`.86` = 8086**。16 KB。
（`SYSTEM.PASCAL` 是作業系統本體，p-code 寫的；`SYSTEM.COMPILER` 是編譯器。）

## 怎麼找到它的 dispatch 表

[五步反推法](../40-re-workflow/recover-opcode-table.md)在這裡遇到一個變化：
**8086 版沒有共同主迴圈**。68000 版每個常式結尾都是 `jmp (a5)` 回同一個地方（109 次），
8086 版是把 fetch-dispatch **內嵌在每個常式的結尾**：

```
0a88: 32e4       xor  ah, ah
0a8a: ac         lodsb                  ; 取下一個 opcode（si 是 IPC）
0a8b: 97         xchg ax, di
0a8c: d1e7       shl  di, 1             ; ×2
0a8e: 2eff25     jmp  word ptr cs:[di]  ; 查表跳走
```

所以「統計跳躍目標找主迴圈」這一招在這裡失效——沒有一個壓倒性的目標。
`lodsb` 出現 237 次，倒是與 68000 版的 `move.b (a4)+` 密度相當。

改用**已知結論當指紋**：68000 版的 `BPT`（`0x9e`）跳錯誤碼 16，
而 8086 版把錯誤碼放進 `bp` 再跳共同處理：

```
026e: bd 10 00   mov bp, 16
0271: eb 9c      jmp 0x020f
```

值 `0x026e` 在整個檔案只出現一次，在偏移 `0x1e92`。
若它是 opcode `0x9e` 的表項，表就在 `0x1e92 − 0x9e×2 = 0x1d56`。
用這個基底讀 256 項，**全部落在合理的程式碼範圍**。

再拿四個常式的內容驗證基底（下一節），確認無誤。

## 三方比對

| | IV.0 官方表 | IV.2.1 / 68000（SunDog） | IV.2.1 / 8086（PME.86） |
|---|---|---|---|
| 沒有指令的格 | 45（未列出或 `reserved`） | 45（指向錯誤 11） | **44**（指向錯誤 11） |
| 位置 | `0x40`–`0x5f`、`0xaa`、`0xaf`、`0xf5`–`0xff` | 同左 | 同左，**但少了 `0xff`** |
| 短形式分組 | `SLDC`/`SLDL`/`SLDO`/`SLLA`/`SSTL`/`SCXG`/`SIND` | 逐格相同 | 逐格相同 |
| 浮點 16 格 | 列為正常指令 | **全部導向同一個 fault** | **各有專屬常式** |
| 相異目標數 | — | 107 | 169 |

**編號層面：256 格裡只有 `0xff` 一格分配不同。** 其餘完全重合。

## 差異一：浮點

68000 版把 16 個實數指令全部導向同一個 fault（錯誤 12），
[逐格對照](iv0-vs-iv21.md)那篇的結論是「這份直譯器沒有實作浮點」。

8086 版**每一個都有專屬常式**：

| 指令 | 8086 常式 | | 指令 | 8086 常式 |
|---|---|---|---|---|
| `TNC` | `0x299c` | | `ABR` | `0x2a94` |
| `RND` | `0x29ab` | | `NGR` | `0x278c` |
| `ADR` | `0x23c2` | | `LDCRL` | `0x2a52` |
| `SBR` | `0x23bc` | | `LDRD` | `0x2a37` |
| `MPR` | `0x24e1` | | `STRL` | `0x2a19` |
| `DVR` | `0x262a` | | `EQREAL` | `0x27b5` |
| `DUPR` | `0x2a77` | | `LEREAL` | `0x27af` |
| `FLT` | `0x2770` | | `GEREAL` | `0x27ba` |

`LDCRL`（載入實數常數）的碼順帶給出這份直譯器的 realsize：

```
2a64: 83ec08     sub  sp, 8        ; 在堆疊上開 8 個位元組
2a67: 8bfc       mov  di, sp
2a6d: a5 a5 a5 a5  movsw ×4        ; 搬 4 個 word
```

**8 個位元組 = 4 個 word = 64-bit 實數**，對應手冊 p.14 的 `$R4`。

## 差異二：`0xff`

IV.0 表把 `0xfa`–`0xff` 標成 `RESERVE1`–`RESERVE6`。

- 68000 版：`0xff` 指向錯誤 11（未實作），與其他保留槽一樣。
- 8086 版：`0xff` 指向 `0x0269`，也就是 `mov bp, 14` ——**錯誤 14**，
  在 I.5 的常數表裡是 `HLTBPT`。

**8086 版把最後一個保留槽拿去用了。** 這正是[版本陷阱](version-traps.md)在講的事情，
只是這次連「同一個版本」都不保險。

## 差異三：`CXG` 內嵌程序表的上限

手冊 p.66 說 segment 號為 1 時程序碼可能內嵌在直譯器裡。兩版的實作結構**完全平行**：

```
68000（SunDog @0ee0）              8086（PME.86 @13eb）
  cmpi.w #1,d0      段號是 1 嗎      cmp  bp, 1
  bne.s  一般路徑                    jnz  一般路徑
  move.b (a4),d1    偷看程序號        mov  di, [si]
  cmpi.w #$30,d1    比上限            cmp  di, 2Fh
  bhi.s  一般路徑                    jg   一般路徑
  查表                               mov  di, cs:[di+1F56h]
                                     cmp  di, 0        ← 8086 多這一道
                                     jz   一般路徑
```

兩處不同：

- **上限差一**：68000 版是「大於 `0x30` 就退回」，8086 版是「大於 `0x2f` 就退回」。
- **8086 版多一道零檢查**：查到的表項是 0 也退回一般路徑。

兩版都用「先偷看不前進」（`move.b (a4)` / `mov di,[si]`，都不遞增指標），
因為走一般路徑時還要由那條路徑自己去讀這個位元組。

## 相同的地方也值得記

**`CPL` 與 `CPG` 的差別，在兩個 CPU 上都是「換一個基底」：**

```
68000                          8086
  CPL: move.l a0,d5              CPL: push word_2E    ← MP
  CPG: move.l a1,d5              CPG: push word_30    ← BASE
```

[程序呼叫](../10-p-machine/procedure-call.md)那篇從手冊文字推出「`CPL` 的靜態鏈是
呼叫者自己的框、`CPG` 的是 `BASE`」。兩個獨立的移植都用同一種方式實作它——
**推導的第二次獨立驗證**。

**`RPU` 順帶驗證了兩組欄位偏移：**

```
111b: mov bp, word_2E     ; 目前的框
111f: mov bp, [bp+6]      ; 讀 Mark Stack 偏移 6
1122: mov di, word_3E     ; 目前的 E_Rec
1126: cmp bp, di          ; 不同就是跨段返回
1128: jz  同段路徑
112e: call 切段
1137: mov bp, [di+4]      ; 讀 E_Rec 偏移 4
```

- Mark Stack 偏移 6 拿來與「目前的 E_Rec」比較 → 那一格是 **`MSENV`**，
  與 Figure 5 的欄位順序（`MSSTAT` 0、`MSDYN` 2、`MSIPC` 4、`MSENV` 6、`MSPROC` 8）一致。
- E_Rec 偏移 4 → **`Env_Vect`**，與手冊 p.37 的 record 宣告順序
  （`Env_Data` 0、`Env_SIB` 2、`Env_Vect` 4）一致。

手冊給的是 Pascal 宣告，沒有明寫位元組偏移；這裡是實作端的確認。

## 實作策略：同一件事，兩種做法

最能說明「編號一致不等於實作一致」的是 `LDP`（載入 packed 欄位）。

68000 版用**三次移位**把欄位以外的位元擠掉（推導見
[packed 欄位](../20-pcode-encoding/packed-fields.md)）：

```
08ce: lsr.w d0,d2      ; 右移到底
08d0: lsl.w d1,d2      ; 左移 16−n
08d2: lsr.w d1,d2      ; 再右移 16−n
```

8086 版用**一張預先算好的遮罩表**：

```
0a7d: d3ed        shr  bp, cl              ; 右移到底
0a7f: 95          xchg ax, bp
0a80: d1e5        shl  bp, 1               ; 位元數 ×2 當索引
0a82: 2e2386b61f  and  ax, cs:[bp+1FB6h]   ; 查表取遮罩
```

`0x1fb6` 那張表就是 `0x007f, 0x00ff, 0x01ff, 0x03ff, 0x07ff, 0x0fff…`——
每個欄位寬度一個遮罩。

`packed-fields.md` 說 68000 版「用移位器當遮罩產生器」，因為算遮罩比兩次移位貴。
8086 版的答案是**根本不算，查表**。兩者都在避開「執行期算遮罩」，手段不同。
那一篇的邊界原本寫「別的移植版可能用遮罩而不是移位」——現在有實證了。

## 一個沒解開的地方

`jmp word ptr cs:[di]` 沒有帶位移，字面上表示 dispatch 表在 `cs:0000`；
但表實際在檔案偏移 `0x1d56`，而且表項的值就是檔案偏移（四個常式的內容都驗過）。
這兩件事要同時成立，執行時的 `cs` 段基底就不能等於檔案載入位址。

檔案開頭那幾個 word（`0x3a04`、`0x0c9b`、`0x00e6`…）看起來像載入用的標頭或重定位資訊，
但沒有追。**這不影響本篇的結論**——所有比對都建立在「表項值 = 檔案偏移」上，
而那一點由 `LDC`、`LDP`、`IXP`、`BPT` 四個常式的內容獨立確認過。

## 邊界

- 兩份直譯器的「IV.2.1」身分來源不同：68000 版由
  [實例篇](sundog-ivx-table.md)的三個獨立來源定版；8086 版來自標為 1984 年的
  p-system 發行磁碟，**沒有從檔案本身讀到版號**。兩者同屬 IV.2.x 是強推論，不是確證。
- 8086 版只讀了 8 個常式（`LDC`、`LDCI`、`LDP`、`IXP`、`LDCRL`、`LDRD`、
  `CXG`、`RPU`、`CPL`、`CPG`）。「169 個相異目標」是表的統計，不是逐條讀過。
- 浮點那 16 格「各有專屬常式」是從表的相異值推的，沒有逐一讀碼確認它們真的在算浮點。
  `LDCRL` 的 4 個 `movsw` 是唯一實際讀過的一支。
