# 術語表

| 詞 | 意思 |
|---|---|
| **p-code** | UCSD p-machine 的指令。編譯器的輸出，由直譯器執行，不是任何真實 CPU 的機器碼 |
| **p-machine** | 那台不存在的目標電腦。堆疊機，沒有通用暫存器 |
| **直譯器（interpreter）** | 各平台各一份，把 p-code 翻成該 CPU 的動作。UCSD 的檔名慣例是 `SYSTEM.INTERP` |
| **segment** | 程式碼的組織與換頁單位，各有自己的程序字典與全域區 |
| **dispatch 表** | 直譯器裡「opcode → 處理常式位址」的查表。反推 opcode 表就是在找它 |
| **短形式（short form）** | 把運算元編進 opcode 值本身的指令，如 `SLDC`、`SLDL`、`SLDO`、`SIND` |
| **變長運算元（big operand）** | 最高位為 0 是一個位元組，為 1 就再吃一個，值是 `((第一個 & 0x7f) << 8) \| 第二個` |
| **保留槽** | dispatch 表裡不放位址的空格（I.5 的 `.BLKW`）。抄表時漏掉會讓整張表位移 |
| **活動記錄（activation record）** | 一次程序呼叫在堆疊上的那一塊：局部變數、回傳位址、動態與靜態鏈 |
| **Mark Stack** | 活動記錄最低位址那五個 word（`MSSTAT`/`MSDYN`/`MSIPC`/`MSENV`/`MSPROC`），存呼叫的管理資訊 |
| **動態鏈 / 靜態鏈** | `MSDYN` 指呼叫者（用來 return）；`MSSTAT` 指語法父層（用來找非區域變數）。兩者常指到不同的框 |
| **SIB（Segment Information Block）** | 執行期描述一個 segment 的記錄：所在位置、是否在記憶體、參照計數 |
| **E_Rec（Environment Record）** | 一個 segment 的執行環境，含它的全域資料區與 SIB 指標 |
| **TIB（Task Information Block）** | 一個並行 task 的暫存器快照與堆疊界限。`CURTSK` 永遠指向執行中 task 的 TIB |
| **codepool** | 記憶體裡放 code segment 的區域，可整塊移動以配合 Heap 與 Stack 的成長 |
| **byte sex** | segment 的位元組序。與主機相反時，若干指令要先交換每個 word 的位元組 |
| **RSP（Runtime Support Package）** | 直譯器裡不模擬 p-code 的那部分原生碼；管 I/O 的部分叫 RSP/IO，硬體相依部分叫 BIOS |
| **lex level（語彙層級）** | 程序在原始碼裡的巢狀深度。決定呼叫時靜態鏈要沿鏈走幾步 |
| **形式程序（formal procedure）** | 當成參數傳進來的程序。目標到執行期才知道，用 `CPF` 呼叫 |
| **principal / subsidiary segment** | 一個獨立編譯的 PROGRAM 或 UNIT 產生一個 principal segment；`SEGMENT` 常式與 `EXTERNAL` 原生常式另成 subsidiary segment |
| **E_Vec（Environment Vector）** | 一段自己的對照表，把本地 segment number 映到實際的段。分離編譯的產物——本地號碼只在本段內有意義 |

## 慣例

- 助記符、識別字、檔名保留原文；說明用繁體中文。
- 位元組一律寫成 `0x` 十六進位；引用組語原文時保留該處的進位制（PDP-11 組語用八進位）。
- 每條結論標明來源檔案。沒有一手來源支持的推論寫「待查證」，不寫進表。
- 引 IV.0 手冊寫**印刷頁碼**（`手冊 p.49`）。掃描檔的 PDF 頁碼比印刷頁碼多 6，
  只在需要回查掃描檔時才並列。
- 版本一律寫明 I.5、IV.0 或 IV.2.1。「IV.x」只用在確實泛指整個 IV 系列的場合。
- 標點全形。半形只用在程式碼區塊內、行內程式碼內，以及英文列舉（`DB, B`）
  與英文原名（`Cursor X,Y Positioning`）。
