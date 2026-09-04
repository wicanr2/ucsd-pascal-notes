# 工具

兩支腳本，都在容器裡跑（見 [`CLAUDE.md`](../CLAUDE.md) 的執行環境）。

## `dispatch-crosstab.py`

重跑[逐格對照](../docs/30-opcode-tables/iv0-vs-iv21.md)：從 SunDog `SYSTEM.INTERP` 的
位元組抽出 256 項 dispatch 表，與 IV.0 官方表的摘譯交叉比對。

```
docker run --rm --network none -u "$(id -u):$(id -g)" \
  -v "$PWD:/work" -v /path/to/sundog:/in:ro -w /work python:3.13-alpine \
  python tools/dispatch-crosstab.py /in/SYSTEM.INTERP
```

`SYSTEM.INTERP` 不在版控裡（見 [README](../README.md) 的邊界宣告），要自備。
腳本會核對 sha256，不符只警告不中止——換一份檔案時，輸出裡的位址常數
（`0x304` 錯誤處理、`0x1b68` 浮點 fault）就不一定還成立。

## `dump-routines.py`（IDAPython）

在 IDA 裡對 dispatch 表的每個目標位址強制反組譯，輸出 JSON。這是
[逐條驗證](../docs/30-opcode-tables/iv21-routine-audit.md)的證據來源。

```
docker run --rm --network none -u "$(id -u):$(id -g)" -v "$WORK:/work" -w /work \
  ida-pro-9.4-idapython:locked-v1 \
  idat -A -p68000 -S"/work/dump-routines.py /work/routines.json" SYSTEM.INTERP
```

**exit code 不能當證據**——唯一可信的訊號是 `routines.json` 存在、`sha256` 欄位對得上。

## `routine-audit.py`

把上面的 JSON 與 IV.0 官方表配對。預設輸出 markdown 判定表，`--pairs` 輸出
「官方說明 + 反組譯」供逐條判讀。

```
docker run --rm --network none -u "$(id -u):$(id -g)" -v "$PWD:/work" -w /work \
  python:3.13-alpine python tools/routine-audit.py routines.json --pairs
```

助記符解析沿用 `dispatch-crosstab.py`，**不要再抄一份**：這份解析曾經被抄成兩份，
其中一份把範圍展開的起編寫死成 1，於是 `SIND0…SIND7` 整族的標籤錯一位。

## `check-links.py`

檢查所有 markdown 的相對連結：目標檔在不在、`#` 錨點對不對得上標題。每輪收尾跑一次。

```
docker run --rm --network none -u "$(id -u):$(id -g)" \
  -v "$PWD:/work:ro" -w /work python:3.13-alpine python tools/check-links.py
```

順帶會抓到一種容易漏的錯：markdown 把 `dir[77](一般檔案…)` 這種寫法渲染成連結。
這是真的踩過的坑。錨點規則是 GitHub 的近似——**報有問題是強訊號，報沒問題不是保證**。

## `normalize-punct.py`

把 markdown 裡與中文混排的半形標點轉成全形。冪等，可重複跑。

```
docker run --rm --network none -u "$(id -u):$(id -g)" \
  -v "$PWD:/work" -w /work python:3.13-alpine \
  python tools/normalize-punct.py README.md PLAN.md CONTEXT.md CLAUDE.md docs/*/*.md refs/*.md
```

**引用的英文原文要加進腳本裡的 `KEEP` 清單**，否則下一次重跑會把它的標點也轉掉。
目前清單裡有手冊的 `eX(ecute)`／`U(ser restart)`、節名 `Cursor X,Y Positioning`、
`SYSTEM.INTERP` 的版權字串，以及一句引用 `laanwj/sundog` 的原文。
這個坑踩過兩次：改完的例外在下一輪重跑時被無聲吃掉，而 diff 很長不容易發現。
