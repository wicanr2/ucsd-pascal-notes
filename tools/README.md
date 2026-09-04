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
