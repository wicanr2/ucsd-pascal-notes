# -*- coding: utf-8 -*-
"""重跑 docs/30-opcode-tables/iv0-vs-iv21.md 的逐格對照。

輸入
  1. SunDog 的 `SYSTEM.INTERP`（68000 raw binary，11776 bytes，
     sha256 a344edfb07d27cafa3dfda68f1854a76f63a0e89cf2e8229dacf5aa64d603c38）
     dispatch 表在檔內位移 0xec，256 項，每項兩位元組 big-endian，
     值即處理常式的檔內位移。推導見 docs/30-opcode-tables/sundog-ivx-table.md 第 1–2 步。
  2. docs/50-iv-internals/appendix-opcodes.md —— IV.0 官方表的摘譯。

輸出：兩張表的槽位交叉比對，以及 107 個相異目標的組成。

`SYSTEM.INTERP` 不在版控裡（見 README 的邊界宣告），要自備。

用法：
    docker run --rm --network none -u "$(id -u):$(id -g)" \
      -v "$PWD:/work" -v /path/to/sundog:/in:ro -w /work python:3.13-alpine \
      python tools/dispatch-crosstab.py /in/SYSTEM.INTERP
"""
import collections
import hashlib
import re
import struct
import sys

TABLE_OFF = 0xec          # dispatch 表的檔內位移
ERR = 0x304               # moveq #11,d0 → 錯誤處理（未實作指令）
FP = 0x1b68               # jmp (0x308,a3) → moveq #12,d0（浮點）
EXPECT_SHA = 'a344edfb07d27cafa3dfda68f1854a76f63a0e89cf2e8229dacf5aa64d603c38'
APPENDIX = 'docs/50-iv-internals/appendix-opcodes.md'


def read_dispatch(path):
    data = open(path, 'rb').read()
    got = hashlib.sha256(data).hexdigest()
    if got != EXPECT_SHA:
        print(f'警告：sha256 是 {got}，與記錄的 {EXPECT_SHA} 不同。'
              f'以下結論只對記錄的那一份成立。', file=sys.stderr)
    return [struct.unpack_from('>H', data, TABLE_OFF + 2 * i)[0] for i in range(256)]


def read_official(path=APPENDIX):
    """把摘譯的表格列解析成 opcode → 助記符。範圍寫法（SLDL1 … SLDL16）會展開。"""
    tbl = {}
    for line in open(path, encoding='utf-8'):
        if not line.startswith('| `'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 4:
            continue
        mn = [m.strip('`') for m in re.findall(r'`[^`]+`', cells[0])]
        hx = re.findall(r'`0x([0-9a-fA-F]{2})`', cells[2])
        if not hx:
            continue
        if '–' in cells[2] and len(hx) == 2:
            stem = re.match(r'([A-Z_]+)', mn[0]).group(1)
            for i, op in enumerate(range(int(hx[0], 16), int(hx[1], 16) + 1)):
                tbl[op] = f'{stem}{i + 1}' if mn[0] != stem else stem
        else:
            pairs = zip(mn, hx) if len(mn) == len(hx) else [(mn[0], hx[0])]
            for m, h in pairs:
                tbl[int(h, 16)] = m
    return tbl


def fmt(ops):
    """把 opcode 集合寫成連續區間"""
    xs = sorted(ops)
    if not xs:
        return '—'
    out, s, p = [], xs[0], xs[0]
    for x in xs[1:]:
        if x == p + 1:
            p = x
        else:
            out.append((s, p))
            s = p = x
    out.append((s, p))
    return '、'.join(f'0x{a:02x}' if a == z else f'0x{a:02x}–0x{z:02x}' for a, z in out)


def main(interp_path):
    tbl = read_dispatch(interp_path)
    iv0 = read_official()

    reserved = {o for o, m in iv0.items() if m.startswith('RESERVE')}
    listed = set(iv0) - reserved
    unlisted = set(range(256)) - set(iv0)
    err_ops = {i for i in range(256) if tbl[i] == ERR}
    impl = set(range(256)) - err_ops
    fp_ops = {i for i in range(256) if tbl[i] == FP}

    print('== 結果一：沒有指令的槽 ==')
    print(f'IV.0 未列出          {len(unlisted):3d} 格  {fmt(unlisted)}')
    print(f'IV.0 標 reserved     {len(reserved):3d} 格  {fmt(reserved)}')
    print(f'IV.2.1 指向錯誤 11   {len(err_ops):3d} 格  {fmt(err_ops)}')
    same = (unlisted | reserved) == err_ops
    print(f'兩集合相同：{same}')
    if not same:
        print(f'  只有 IV.2.1 當未使用：{fmt(err_ops - unlisted - reserved)}')
        print(f'  只有 IV.0 當未使用：{fmt(unlisted | reserved - err_ops)}')

    print()
    print('== 結果二：107 個目標的組成 ==')
    cnt = collections.Counter(tbl)
    short = [a for a, n in cnt.items() if n > 1 and a not in (ERR, FP)
             and all(o < 0x80 for o in range(256) if tbl[o] == a)]
    pair = [a for a, n in cnt.items() if n > 1 and a not in (ERR, FP) and a not in short]
    solo = [a for a, n in cnt.items() if n == 1]
    span = lambda xs: sum(cnt[a] for a in xs)
    for name, tg, sl in (('錯誤 11', 1, cnt[ERR]), ('浮點 fault', 1, cnt[FP]),
                         ('短形式群常式', len(short), span(short)),
                         ('兩格共用', len(pair), span(pair)),
                         ('專屬常式', len(solo), span(solo))):
        print(f'  {name:12s} 目標 {tg:3d}   涵蓋 {sl:3d} 格')
    print(f'  合計         目標 {2 + len(short) + len(pair) + len(solo)}   涵蓋 '
          f'{cnt[ERR] + cnt[FP] + span(short) + span(pair) + span(solo)} 格')
    for a in pair:
        print(f'    共用 0x{a:04x}：{" ".join(iv0.get(o, "?") for o in range(256) if tbl[o] == a)}')

    print()
    print(f'== 結果三：走浮點 fault 的 {len(fp_ops)} 格 ==')
    print('  ' + ' '.join(iv0.get(o, '?') for o in sorted(fp_ops)))

    print()
    print('== 逐格結論 ==')
    print(f'IV.0 列出的實際指令 {len(listed)} 格；IV.2.1 有處理常式 {len(impl)} 格；'
          f'兩者相同：{listed == impl}')
    if listed != impl:
        print(f'  IV.0 有列但 IV.2.1 沒實作：{fmt(listed - impl)}')
        print(f'  IV.2.1 有實作但 IV.0 沒列：{fmt(impl - listed)}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
