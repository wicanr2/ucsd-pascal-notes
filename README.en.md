# UCSD Pascal / p-system notes

**English** ｜ [日本語](README.ja.md) ｜ [繁體中文](README.md)

Taking UCSD p-system's p-code apart from first principles: **every encoding
decision can be forced out of one constraint — a 1978 machine had only tens of
kilobytes.** Written for someone holding a piece of old p-code they cannot read.

It started with reverse-engineering SunDog, a 1985 Atari ST game whose logic is
p-code rather than 68000 machine code. Along the way it became clear that the
opcode tables floating around the web cannot be used as-is, and that nobody had
written down the correct approach — recovering the table from the interpreter in
front of you. This repo fills that gap.

## Where to start

New to the p-system? Read these six in order:

1. [What a p-machine is](docs/10-p-machine/what-is-a-p-machine.md)
   — why invent a fake computer, why it is a stack machine, what problem
   segments solve.
2. [Instruction encoding](docs/20-pcode-encoding/instruction-encoding.md)
   — why constants need no opcode, why variable numbers are encoded into the
   opcode, how variable-length operands are read.
3. [How a procedure call works](docs/10-p-machine/procedure-call.md)
   — why there are nine families of call instruction: a matrix produced by two
   independent questions, and where the Mark Stack's five fields come from.
4. [Why segments are cut this way](docs/10-p-machine/segment-and-environment.md)
   — the three levels of indirection a cross-segment call goes through, the
   constraint behind each, and why the SIB is not stored inside the segment.
5. [Opcode tables and version traps](docs/30-opcode-tables/version-traps.md)
   — I.5, IV.0 and IV.2.1 side by side: what holds across versions and what was
   one version's private choice.
6. [Recovering an opcode table from an interpreter](docs/40-re-workflow/recover-opcode-table.md)
   — what to do when you do not know which version your p-code is, including
   machine-code interpreters.

Already know the p-system and just want the table? Go to 5. Holding p-code you
cannot read? Go to 6.

## One interpreter, from recovering the table to verifying the semantics

The same target (SunDog's `SYSTEM.INTERP`) taken through three stages — a worked
example for chapter 6:

- [Worked example: recovering the opcode table of a 1985 68000 interpreter](docs/30-opcode-tables/sundog-ivx-table.md)
  — the five-step method run for real, from loading it into IDA to verification.
- [Cell by cell: the official IV.0 table against the IV.2.1 dispatch table](docs/30-opcode-tables/iv0-vs-iv21.md)
  — the recovered table checked against the official one, all 256 cells.
- [Instruction by instruction: 98 handlers](docs/30-opcode-tables/iv21-routine-audit.md)
  — once the numbering matches, verify the semantics; includes this
  interpreter's register assignments and runtime error codes.
- [One version, two CPUs](docs/30-opcode-tables/iv21-two-cpus.md)
  — the 1984 DOS 8086 interpreter for comparison. One cell differs in
  numbering; the implementations differ a great deal.

## Single topics

- [Packed fields](docs/20-pcode-encoding/packed-fields.md)
  — a 16-bit address cannot hold a bit field, so the address becomes three
  words on the stack.
- [What each I.5 opcode does](docs/30-opcode-tables/i15-opcode-semantics.md)
  — the 1978 version instruction by instruction, read out of the PDP-11
  interpreter's handlers.

## Manual digest

[`docs/50-iv-internals/`](docs/50-iv-internals/README.md) is a section-by-section
digest of the official IV.0 manual: eight chapters covering the codefile format,
memory layout, per-instruction semantics, the three I/O layers, the operating
system and the official opcode table. Every conclusion carries a printed page
number so it can be traced back.

The first five chapters explain *why*; the digest answers *what the manual
says*. Where they conflict, the manual plus measured bytes wins.

## Sister repo

**Parhelion PME** ([`Parhelion-PME86`](https://github.com/wicanr2/Parhelion-PME86))
takes the 1984 DOS 8086 interpreter (`SYSTEM.PME.86`) apart routine by routine —
all 169 handlers disassembled, covering dispatch, the state model, addressing,
segment switching, segment 1's embedded native procedures, concurrency and task
switching, plus a 256-cell map — and remakes a p-machine in Go in the same repo.

**That remake boots.** Feed it a 1984 `.VOL` disk image and the p-System boots
itself to the command line, responds to keystrokes and the Filer lists a
directory; all 226,623 p-code instructions of the boot match the original one
by one.

**General principles, encoding and the manual digest live here; the details of
that 8086 implementation and the remake live there.**

## Sources

**UCSD Pascal I.5 source** (released 1978, free for non-commercial download).
Two files support the conclusions in the early chapters:

- `mainop.mac`: the PDP-11 interpreter, including the `XFRTBL` dispatch table.
- `CODESTAT`: the official p-code disassembler, written in Pascal, including
  `GETBIG`'s variable-length decoding and opcode classification comments.

**SofTech, *UCSD p-System and UCSD Pascal Version IV.0 Internal Architecture
Guide*** (1981). The scan is in [`refs/`](refs/README.md); the digest is in
`docs/50-iv-internals/`. IV.0 is the closest official document to SunDog's
version (IV.2.1).

Measurements come from SunDog's (1985, Atari ST) `SYSTEM.STARTUP` and
`SYSTEM.INTERP`. **This repo contains no original disk image, executable or game
data** — only byte-level conclusions about the encoding.

## Limits

- The I.5 table was recovered from the **PDP-11 interpreter**. Whether the
  8080/Z80 ports of the same version agree has not been checked — and optimism
  is not warranted: the two CPU versions of IV.2.1 have been compared, and
  **the numbering matches while the behaviour differs in substance**
  (see [one version, two CPUs](docs/30-opcode-tables/iv21-two-cpus.md)).
- The IV.0 table is **printed in the official manual**, not recovered from an
  interpreter. It has been checked cell by cell against SunDog's IV.2.1 dispatch
  table and the numbering is identical — but that is "same numbers", not "same
  semantics per instruction".
- All 98 routines in SunDog's 68000 interpreter have been verified one by one
  and all agree with IV.0's definitions. The per-routine conclusions for the
  8086 one are not in this repo; see the sister repo above.
- Mnemonics come from the interpreter's own labels and the official manual.
  Label names reflect the implementer's naming and do not necessarily match
  official terminology; where they disagree the manual wins and it is noted.

## Licence

Documents and figures are CC BY 4.0. The quoted UCSD source fragments are
copyright the Regents of the University of California; the manual scan in
`refs/` is copyright SofTech Microsystems and its successors, included for
technical research and non-commercial citation.
