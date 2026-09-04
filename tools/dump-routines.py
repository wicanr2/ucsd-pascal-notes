# 對 SunDog SYSTEM.INTERP 的 dispatch 表逐個目標強制反組譯，輸出 JSON。
# 結束判準：jmp (a5)（4ED5，回主迴圈）或 rts（4E75），或達到指令上限。
import json, sys
import ida_auto, ida_bytes, ida_ua, ida_pro, ida_segment, ida_nalt, idc

ida_auto.auto_wait()

seg = ida_segment.getnseg(0)
BASE = seg.start_ea
TABLE = BASE + 0xec
LIMIT = 48                      # 單一常式的指令數上限

def w(ea):
    return ida_bytes.get_word(ea)

# 1. 讀 dispatch 表
tbl = [w(TABLE + 2 * i) for i in range(256)]

# 2. 對每個相異目標線性反組譯
def disasm_from(off):
    ea = BASE + off
    lines, n = [], 0
    while n < LIMIT:
        ida_bytes.del_items(ea, ida_bytes.DELIT_SIMPLE, 8)
        ln = ida_ua.create_insn(ea)
        if ln <= 0:
            lines.append({"ea": ea - BASE, "bytes": ida_bytes.get_bytes(ea, 2).hex(),
                          "text": "<無法反組譯>"})
            break
        raw = ida_bytes.get_bytes(ea, ln).hex()
        txt = idc.generate_disasm_line(ea, 1) or ""
        txt = txt.split(";")[0].rstrip()
        lines.append({"ea": ea - BASE, "bytes": raw, "text": txt})
        first = int(raw[:4], 16)
        # 回主迴圈或返回 → 常式結束
        if first in (0x4ed5, 0x4e75):
            break
        # 無條件跳躍離開（bra / jmp）也視為結束，但記下目標
        if (first & 0xff00) == 0x6000 or (first & 0xffc0) == 0x4ec0:
            break
        ea += ln
        n += 1
    return lines

targets = {}
for t in sorted(set(tbl)):
    targets[f"{t:04x}"] = disasm_from(t)

out = {
    "input": ida_nalt.get_root_filename(),
    "sha256": ida_nalt.retrieve_input_file_sha256().hex(),
    "base": BASE,
    "table_off": 0xec,
    "dispatch": [f"{v:04x}" for v in tbl],
    "routines": targets,
}
with open(sys.argv[1], "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
ida_pro.qexit(0)
