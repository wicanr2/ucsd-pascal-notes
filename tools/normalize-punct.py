# -*- coding: utf-8 -*-
"""把 markdown 裡與中文混排的半形標點轉成全形。冪等，可重複跑。

規則
- 只處理含中文（漢字或中文標點）的行。
- 逗號／分號：後面沒有空格才轉。英文列舉一律寫成 "DB, B"（有空格），因此不受影響。
- 冒號：右邊接漢字就轉；否則左邊是 ASCII 英數就保留（"Printer:Status"、"II.1:P-machine"）。
- 括號：內容或緊鄰字元看起來像運算式就保留，其餘轉全形。
- 句點：左邊是漢字、右邊是空白或行尾才轉（避開 "p.52"、"0.5"、檔名）。

不動的區域
- fenced code block、行內程式碼、markdown 連結目標、URL、HTML 實體、千分位數字。
- KEEP 裡列的字串：引用的英文原文與手冊自己的排版慣例。**新增這類例外時要同時加進 KEEP**，
  否則下一次重跑會把它改掉——這個坑已經踩過兩次。

用法（照 CLAUDE.md 的 docker-only 規則）：
    docker run --rm --network none -u "$(id -u):$(id -g)" \
      -v "$PWD:/work" -w /work python:3.13-alpine \
      python tools/normalize-punct.py README.md docs/*/*.md
"""
import re, sys

CJKC = '[㐀-䶿一-鿿]'
CODEISH = re.compile(r'[=<>&|*\\{}$]')
ARITH = set('=<>&+-/')   # 不含 *：markdown 的 **粗體** 會誤判

# 引用的英文原文與手冊自己的排版慣例，一律原樣保留
KEEP = [
    r'eX\(ecute\)',                              # 手冊用括號標命令字母：eX(ecute)
    r'U\(ser[^)\n]*\)?',                          # 同上：U(ser restart)
    r'Cursor X,Y Positioning',                    # 手冊 III 章的節名
    r'Copr\. \(c\) 1981 Tallgrass Technologies',   # SYSTEM.INTERP 裡的版權字串原文
    r'Not implemented \(error 0xc\)',             # 引用 laanwj/sundog 的原句
]

def protect(text):
    slots = []
    def stash(m):
        slots.append(m.group(0)); return f'\x00{len(slots)-1}\x00'
    for pat in KEEP:
        text = re.sub(pat, stash, text)
    text = re.sub(r'```.*?```', stash, text, flags=re.S)
    text = re.sub(r'\]\([^)\n]*\)', stash, text)
    text = re.sub(r'https?://\S+', stash, text)
    text = re.sub(r'`[^`\n]*`', stash, text)
    text = re.sub(r'&[a-zA-Z]+;', stash, text)
    text = re.sub(r'\d,\d', stash, text)
    return text, slots

def paren(m):
    before, inner, after = m.group(1), m.group(2), m.group(3)
    if CODEISH.search(inner) or '(' in inner or ')' in inner:
        return m.group(0)
    if (before and before[-1] in ARITH) or (after and after[0] in ARITH):
        return m.group(0)
    return f'{before}（{inner}）{after}'

def colon(m):
    before, after = m.group(1), m.group(2)
    # 右邊接中文一律轉；否則左邊是 ASCII 英數就保留（Printer:Status、II.1:P-machine）
    han = lambda c: bool(c) and '\u4e00' <= c <= '\u9fff'
    if not han(after[:1]) and before and before[-1].isascii() and before[-1].isalnum():
        return m.group(0)
    return f'{before}：{after}'

def convert_line(line):
    if not re.search('[㐀-䶿一-鿿、。，；：（）「」『』《》]', line):
        return line
    line = re.sub(r'（([^（）()\n]*)\)', r'（\1）', line)
    line = re.sub(r'\(([^（）()\n]*)）', r'（\1）', line)
    line = re.sub(r'(.?)\(([^()\n]*)\)(.?)', paren, line)
    line = re.sub(r',(?!\s)', '，', line)
    line = re.sub(r';(?!\s)', '；', line)
    line = re.sub(r'(.?):(.?)', colon, line)
    line = re.sub(rf'({CJKC})!', r'\1！', line)
    line = re.sub(rf'({CJKC})\?', r'\1？', line)
    line = re.sub(rf'({CJKC})\.(\s|$)', r'\1。\2', line)
    return line

def restore(text, slots):
    # 替身可能巢狀（KEEP 的字串又被行內程式碼包住），要還原到沒有替身為止
    for _ in range(10):
        nxt = re.sub(r'\x00(\d+)\x00', lambda m: slots[int(m.group(1))], text)
        if nxt == text:
            return text
        text = nxt
    raise RuntimeError('替身還原沒有收斂')


for path in sys.argv[1:]:
    src = open(path, encoding='utf-8').read()
    body, slots = protect(src)
    out = restore('\n'.join(convert_line(l) for l in body.split('\n')), slots)
    if out != src:
        open(path, 'w', encoding='utf-8').write(out); print(f'changed: {path}')
    else:
        print(f'  same : {path}')
