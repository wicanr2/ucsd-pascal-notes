# -*- coding: utf-8 -*-
"""把 IDA 產出的處理常式反組譯，與 IV.0 官方表配對，輸出逐條驗證用的材料。

輸入是 `dump-routines.py` 在 IDA 裡產生的 JSON。助記符解析直接沿用
`dispatch-crosstab.py` 的 `read_official`——**不要再抄一份**：這份解析曾經因為
被抄成兩份，其中一份把範圍展開的起編寫死成 1，於是整族 `SIND0…SIND7` 的標籤
錯一位（手冊從 0 起編，`SLDL1…SLDL16` 卻從 1）。

用法：
    docker run --rm --network none -u "$(id -u):$(id -g)" \
      -v "$PWD:/work" -w /work python:3.13-alpine \
      python tools/routine-audit.py routines.json [--pairs]

預設輸出 markdown 判定表；`--pairs` 改輸出「官方說明 + 反組譯」對照，供逐條判讀。
"""
import collections
import importlib.util
import json
import os
import sys

ERR = 0x304      # moveq #11 → 未實作指令
FP = 0x1b68      # jmp (0x308,a3) → moveq #12，浮點


def _load_sibling(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(routines_path, mode):
    here = os.path.dirname(os.path.abspath(__file__))
    xtab = _load_sibling('xtab', os.path.join(here, 'dispatch-crosstab.py'))
    iv0_names = xtab.read_official()

    d = json.load(open(routines_path, encoding='utf-8'))
    tbl = [int(x, 16) for x in d['dispatch']]
    cnt = collections.Counter(tbl)

    # 短形式群常式（整群都落在 0x00–0x7f）在 sundog-ivx-table.md 已經解過，這裡不重列
    short = {a for a, n in cnt.items()
             if n > 1 and a not in (ERR, FP)
             and all(o < 0x80 for o in range(256) if tbl[o] == a)}

    # 官方說明（第 4 欄），與助記符分開取
    desc = {}
    import re
    for line in open(os.path.join(here, '..', 'docs', '50-iv-internals',
                                  'appendix-opcodes.md'), encoding='utf-8'):
        if not line.startswith('| `'):
            continue
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) < 4:
            continue
        for h in re.findall(r'`0x([0-9a-fA-F]{2})`', c[2]):
            desc[int(h, 16)] = c[3]
        if '–' in c[2]:
            hs = re.findall(r'`0x([0-9a-fA-F]{2})`', c[2])
            if len(hs) == 2:
                for op in range(int(hs[0], 16), int(hs[1], 16) + 1):
                    desc[op] = c[3]

    seen, out = set(), []
    if mode == 'table':
        out.append('| opcode | IV.0 助記符 | 常式 | 指令數 | 判定 |')
        out.append('|---|---|---|---|---|')
    for op in range(256):
        t = tbl[op]
        if t in (ERR, FP) or t in short or t in seen:
            continue
        seen.add(t)
        mates = [o for o in range(256) if tbl[o] == t]
        ops = '、'.join(f'`0x{o:02x}`' for o in mates)
        names = ' / '.join(f'`{iv0_names.get(o, "?")}`' for o in mates)
        code = d['routines'][f'{t:04x}']
        if mode == 'table':
            out.append(f'| {ops} | {names} | `0x{t:04x}` | {len(code)} | ✓ |')
        else:
            out.append(f'### {names}  [{ops}]  @{t:04x}')
            out.append(f'官方：{desc.get(op, "?")}')
            for l in code:
                out.append(f"  {l['ea']:04x}: {l['bytes']:<12} {l['text']}")
            out.append('')
    print('\n'.join(out))
    print(f'\n<!-- {len(seen)} 個常式 -->', file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], 'pairs' if '--pairs' in sys.argv else 'table')
