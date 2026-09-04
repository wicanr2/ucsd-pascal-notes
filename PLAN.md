# 進度與計畫

一次推進一個主題，每輪結束就 push。

## 已完成

### R1（2026-09-04）骨架與編碼核心

- `docs/10-p-machine/what-is-a-p-machine.md`：p-machine 的存在理由、堆疊機的取捨、segment。
- `docs/20-pcode-encoding/instruction-encoding.md`：三條從記憶體約束推出的編碼決定，
  配 `img/pcode-big-operand.svg`。
- `docs/30-opcode-tables/version-traps.md`：I.5 主表 128–215 逐槽，加短形式範圍；
  與 SunDog（IV.x）的六個位元組對照，全部不符。
- `docs/40-re-workflow/recover-opcode-table.md`：五步反推法，含 `.BLKW` 位移這個實際踩過的坑。

來源：UCSD Pascal I.5 的 `mainop.mac` 與 `CODESTAT`，兩者交叉驗證主表範圍
（dispatch 表 88 槽 vs 反組譯器的 `FOR OP:=128 TO 215`）。

## 待辦

| # | 主題 | 下一個動作 |
|---:|---|---|
| 1 | IV.x 的 opcode 表 | 反組譯 SunDog 的 `SYSTEM.INTERP`（68000，11776 位元組），照 40 篇的五步做 |
| 2 | 程序呼叫與活動記錄 | 解 `CIP`/`CXP`/`CGP`/`RNP` 的堆疊佈局，配一張活動記錄的 SVG |
| 3 | segment 的磁碟格式 | 段目錄、程序字典、`SYSTEM.STARTUP` 的整體結構 |
| 4 | packed 欄位 | `LDP`/`STP`/`IXP` 的位元欄位定址；SunDog 那版的運算元順序與官方手冊相反，值得單獨一篇 |
| 5 | I.5 各 opcode 的語意 | 目前只有助記符，沒有逐條語意。從 `mainop.mac` 的處理常式讀 |

## 每輪收尾

1. 文件寫完 → 配圖 → `chrome-headless` 轉 PNG 自己看過。
2. 更新 `README.md` 動線與本檔進度。
3. `git add -A` → 繁中 commit → push。
