import argparse
import re

OPCODES = {
    "NOP": (0x00, "none"), "HLT": (0x01, "none"),
    "ADD": (0x10, "r"), "SUB": (0x11, "r"), "AND": (0x12, "r"), "OR": (0x13, "r"), "XOR": (0x14, "r"), "SHL": (0x15, "r"), "SHR": (0x16, "r"), "SAR": (0x17, "r"),
    "ADDI": (0x18, "i"), "ANDI": (0x19, "i"), "ORI": (0x1A, "i"), "XORI": (0x1B, "i"), "SHLI": (0x1C, "i"), "SHRI": (0x1D, "i"), "SARI": (0x1E, "i"), 
    "LUI": (0x1F, "lui"),
    "CMP": (0x20, "c"), "CMPI": (0x21, "ci"),
    "LB": (0x30, "l"), "LBU": (0x31, "l"), "LH": (0x32, "l"), "LHU": (0x33, "l"), "LW": (0x34, "l"), "LWU": (0x35, "l"), "LD": (0x36, "l"),
    "SB": (0x38, "s"), "SH": (0x39, "s"), "SW": (0x3A, "s"), "SD": (0x3B, "s"),
    "JMP": (0x40, "b"), "BEQ": (0x41, "b"), "BNE": (0x42, "b"), "BLT": (0x43, "b"), "BGE": (0x44, "b"), "BLTU": (0x45, "b"), "BGEU": (0x46, "b"), "CALL": (0x48, "b"), 
    "JR": (0x49, "jr"), "CALLR": (0x4A, "jr"),
}

REGISTERS = {f"R{i}": i for i in range(16)}

REGISTERS |= {
    "ZERO": REGISTERS["R0"],
    "LR"  : REGISTERS["R14"], # link register
    "SP"  : REGISTERS["R15"],  # stack pointer
}

def mem(tokens, labels):
    """['[R1+8]'] -> (1, 8).  Also handles '[R1 + 8]' split across tokens."""
    text = "".join(tokens)
    m = re.fullmatch(r"\[\s*([A-Za-z0-9]+)\s*([+-]\s*[^\]]+)?\s*\]", text)
    if not m:
        raise AsmError(f"bad memory operand {text!r}")
    base = reg(m.group(1))
    off  = value(m.group(2).replace(" ", ""), labels) if m.group(2) else 0
    return base, off

def parse_line(text):
    """Split one cleaned line into (labels, mnemonic, operands).

    labels   -- label names defined on this line, usually none or one
    mnemonic -- uppercased, or None if the line holds no instruction
    operands -- operand tokens, commas already removed
    """
    names = []
    while ":" in text:
        name, _, text = text.partition(":")
        names.append(name.strip())
        text = text.strip()
    if not text:
        return names, None, []
    mnemonic, *operands = text.replace(",", " ").split()
    return names, mnemonic.upper(), operands

def value(tok, labels):
    """'0x10' -> 16, '-8' -> -8, 'done' -> its address"""
    t = tok.strip()
    if t in labels:
        return labels[t]
    try:
        return int(t, 0)
    except:
        raise AsmError(f"unkown label or bad number {tok!r}") from None

class AsmError(Exception):
    """A problem in the source file, not a bug in the assembler."""

def expand(mnemonic, operands):
    rd = operands[0] if operands else None
    if mnemonic == "LI":  return [("ADDI", [rd, "R0", operands[1]])]
    if mnemonic == "MOV": return [("ADD",  [rd, operands[1], "R0"])]
    if mnemonic == "NEG": return [("SUB",  [rd, "R0", operands[1]])]
    if mnemonic == "RET": return [("JR",   ["LR"])]
    if mnemonic == "NOT": return [("ADDI", ["R13", "R0", "-1"]),
                                  ("XOR",  [rd, operands[1], "R13"])]
    
    return [(mnemonic, operands)]

def reg(tok): 
    """Resolve a register name or alias to its 4-bit field value."""
    try:
        return REGISTERS[tok.strip().upper()]
    except KeyError:
        raise AsmError(f"unknown register {tok!r}") from None
    
def clean_source(source):
    """Strip comments and surrounding whitespace, keeping source line numbers.

    Returns a list of (lineno, text) pairs. Blank and comment-only lines are
    kept as empty text so the line numbers stay true to the file.
    """
    out = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        code, _, _ = line.partition(";")
        out.append((lineno, code.strip()))
    return out
        
def pass1(lines, origin=0):
    """Assign an address to every label.  Returns {name: address}."""
    labels, addr = {}, origin
    for lineno, text in lines:
        names, mnemonic, operands = parse_line(text)
        for name in names:
            if name in labels:
                raise AsmError(f"line {lineno}: label {name!r} already "
                               f"defined at 0x{labels[name]:08X}")
            labels[name] = addr
        if mnemonic:
            addr += 8 * len(expand(mnemonic, operands))
    return labels

def pass2(lines, labels, origin=0):
    """Encode every instruction.

    Returns a list of (addr, word, lineno, source, real) rows -- one per
    emitted word, so a pseudo-instruction that expands to two words produces
    two rows.  `source` is the original line text on the first row of an
    expansion and None on the rest; `real` is the actual instruction encoded.
    """
    rows, addr = [], origin
    for lineno, text in lines:
        _, mnemonic, operands = parse_line(text)
        if mnemonic is None:
            continue
        for i, (real_m, real_ops) in enumerate(expand(mnemonic, operands)):
            word = encode(real_m, real_ops, labels, lineno)
            real = f"{real_m} {', '.join(real_ops)}".strip()
            rows.append((addr, word, lineno, text if i == 0 else None, real))
            addr += 8
    return rows


def format_listing(rows, labels=None):
    """Render pass2 rows as an address / word / label / source table."""
    at = {}
    for name, addr in (labels or {}).items():
        at.setdefault(addr, []).append(name)

    out = [f"{'ADDR':<13}{'WORD':<19}{'LABEL':<10}{'LINE':>4}  SOURCE",
           f"{'-' * 12} {'-' * 18} {'-' * 9} {'-' * 4}  {'-' * 32}"]
    for addr, word, lineno, source, real in rows:
        label = ",".join(at.get(addr, []))
        line = "" if source is None else str(lineno)
        text = f"\u21b3 {real}" if source is None else source
        out.append(f"0x{addr:08X}   0x{word:016X} {label:<9} {line:>4}  {text}")
    return "\n".join(out)

def encode(mnemonic, operands, labels, lineno):
    if mnemonic not in OPCODES:
        raise AsmError(f"line {lineno}: unknown instruction {mnemonic!r}")
    opcode, fmt = OPCODES[mnemonic]
    rd = rs1 = rs2 = imm = 0
    
    if fmt == "none": pass
    elif fmt == "r":    rd, rs1, rs2 = (reg(o) for o in operands)
    elif fmt == "i":    rd, rs1, imm = reg(operands[0]), reg(operands[1]), value(operands[2], labels)
    elif fmt == "lui":  rd,      imm = reg(operands[0]), value(operands[1], labels)
    elif fmt == "c":    rs1, rs2     = reg(operands[0]), reg(operands[1])
    elif fmt == "ci":   rs1,     imm = reg(operands[0]), value(operands[1], labels)
    elif fmt == "l":    rd = reg(operands[0]); rs1, imm = mem(operands[1:], labels)
    elif fmt == "s":    rs2 = reg(operands[0]); rs1, imm = mem(operands[1:], labels)
    elif fmt == "b":    imm = value(operands[0], labels)
    elif fmt == "jr":   rs1 = reg(operands[0])
    
    return ((opcode << 56) | (rd << 52) | (rs1 << 48)
            | (rs2 << 44) | (imm & 0xFFFFFFFF))
    
def main():
    p = argparse.ArgumentParser(description="Assembler for the CPU")
    p.add_argument("input", help="source .asm file")
    p.add_argument("-o", "--output", default="out.bin", help="output file")
    p.add_argument("-v", "--verbose", action="store_true", help="dump symbol table")
    p.add_argument("--origin", type=lambda s: int(s, 0), default=0,
               help="address the program is loaded at (default 0)")
    p.add_argument("-l", "--listing", action="store_true",
               help="print an address/word/source listing")
    
    args = p.parse_args()
    
    with open(args.input) as f:
        source = f.read()
        
    if args.origin % 8:
        p.error(f"origin 0x{args.origin:X} is not a multiple of 8")

    lines = clean_source(source)
    labels = pass1(lines, args.origin)
    rows = pass2(lines, labels, args.origin)

    if args.verbose:
        for name, addr in sorted(labels.items(), key=lambda kv: kv[1]):
            print(f"0x{addr:08X}  {name}")

    if args.listing:
        print(format_listing(rows, labels))

    with open(args.output, "wb") as out:
        for _, word, _, _, _ in rows:
            out.write(word.to_bytes(8, "big"))
    
if __name__ == '__main__':
    main()