"""Variables that a routine reads but never sets: the usual signature of a misread identifier that still
compiles (AFEAN for AREAN, MC(1).EQ.J for MC(1).EQ.0).

usage: python3 -I unset.py <workdir> [--deck dtm] [--setonly]
--setonly lists the reverse: local names assigned but never read (Z0=ZP for ZO=ZP), excluding dummies and COMMON.
A name counts as set when it is a dummy argument, a COMMON member, DATA-initialised, assigned (X= or X(..)=),
a DO or implied-DO variable, in a READ list, an argument of a CALL (may be set by the callee), an ASSIGN
target, or a statement-function name/argument. Intrinsics and called functions are skipped.
"""
import re
import sys
from pathlib import Path

INTRINSIC = {"SQRT", "EXP", "ALOG", "ALOG10", "LOG", "SIN", "COS", "TAN", "ATAN", "ATAN2", "ABS", "IABS", "AMAX1",
             "AMIN1", "MAX0", "MIN0", "MAX", "MIN", "MOD", "AMOD", "FLOAT", "IFIX", "INT", "SIGN", "ISIGN", "REAL",
             "DBLE", "EOF", "AINT", "MAX1", "MIN1", "ACOS", "ASIN", "SINH", "COSH", "TANH", "DIM", "IDIM"}
KEY = {"IF", "GO", "TO", "GOTO", "DO", "CALL", "RETURN", "END", "CONTINUE", "SUBROUTINE", "FUNCTION", "COMMON",
       "DIMENSION", "DATA", "EQUIVALENCE", "FORMAT", "READ", "WRITE", "REWIND", "STOP", "REAL", "INTEGER",
       "LOGICAL", "EXTERNAL", "AND", "OR", "NOT", "EQ", "NE", "LT", "LE", "GT", "GE", "ENDFILE", "BACKSPACE",
       "PRINT", "ASSIGN", "TRUE", "FALSE", "PROGRAM", "ENTRY", "PAUSE"}


def strip_holl(s):
    out, i = [], 0
    while i < len(s):
        m = re.match(r"(\d+)H", s[i:]) if (i == 0 or not s[i - 1].isalnum()) else None
        if m:
            i += len(m.group(0)) + int(m.group(1)); out.append(" "); continue
        out.append(s[i]); i += 1
    return "".join(out)


def split_kw(t):
    """separate the keywords that blank removal glued to their operands."""
    t = re.sub(r"GOTO(?=[\d(A-Z])", " GOTO ", t)
    t = re.sub(r"^(\d*)DO(\d+)", r"DO \2 ", t)
    t = re.sub(r"(^|\))DO(\d+)", r"\1DO \2 ", t)
    t = re.sub(r"(^|\))CALL(?=[A-Z])", r"\1CALL ", t)
    t = re.sub(r"^ASSIGN(\d+)TO", r"ASSIGN \1 TO ", t)
    t = re.sub(r"(^|\))(RETURN|CONTINUE|STOP)$", r"\1 \2", t)
    return t


def names(s):
    s = split_kw(s)
    return [m.group(0) for m in re.finditer(r"(?<![0-9A-Z])(?<![0-9]\.)[A-Z][A-Z0-9]*", s)
            if m.group(0) not in KEY and not re.fullmatch(r"E\d+", m.group(0))]


def main():
    wd = Path(sys.argv[1]); deck = sys.argv[sys.argv.index("--deck") + 1] if "--deck" in sys.argv else "icrm"
    src = (wd / "src" / f"{deck}.f").read_text().splitlines()
    mp = (wd / "src" / f"{deck}.map").read_text().splitlines()
    st = []; cur = None                      # statements: (first line, label, text)
    for n, l in enumerate(src, 1):
        if not l.strip() or l[:1] in "C*":
            continue
        l = l.ljust(72)
        if l[5] not in " 0" and cur:
            cur[2] += l[6:72]; continue
        if cur:
            st.append(cur)
        cur = [n, l[:5].strip(), l[6:72]]
    st.append(cur)
    units = []
    for s in st:
        t = strip_holl(s[2].replace(" ", "")).upper()
        if re.match(r"(SUBROUTINE|PROGRAM|(REAL|INTEGER|LOGICAL)?FUNCTION)", t):
            units.append([s, []])
        elif units:
            units[-1][1].append((s[0], t))
    for head, body in units:
        h = strip_holl(head[2].replace(" ", ""))
        m = re.match(r"(?:SUBROUTINE|(?:REAL|INTEGER|LOGICAL)?FUNCTION|PROGRAM)([A-Z0-9]+)\(?([^)]*)\)?", h)
        uname = m.group(1); setn = set(a for a in m.group(2).split(",") if a) | {uname}
        arrays = set(); called = set(); uses = {}; dummies = set(setn); common = set(); lhs = {}; reads = set()
        for n, t in body:
            if t.startswith("FORMAT("):
                continue
            if re.match(r"(COMMON|DIMENSION|REAL|INTEGER|LOGICAL|EXTERNAL|EQUIVALENCE)", t):
                body_t = re.sub(r"^(COMMON(/[A-Z0-9]*/)?|DIMENSION|REAL|INTEGER|LOGICAL|EXTERNAL|EQUIVALENCE)", "", t)
                for a in re.finditer(r"([A-Z][A-Z0-9]*)(\()?", re.sub(r"/[A-Z0-9]+/", ",", body_t)):
                    if a.group(2):
                        arrays.add(a.group(1))
                    if t.startswith("COMMON") or t.startswith("EQUIVALENCE"):
                        setn.add(a.group(1)); common.add(a.group(1))
                continue
            if t.startswith("DATA"):
                for part in re.findall(r"([^/]*)/[^/]*/", t[4:]):
                    setn.update(names(part))
                continue
            for a in re.finditer(r"CALL([A-Z][A-Z0-9]*)\((.*)\)\s*$", t):
                called.add(a.group(1)); setn.update(names(a.group(2)))
            mm = re.match(r"(?:IF\(.*\))?CALL([A-Z][A-Z0-9]*)", t)
            if mm:
                called.add(mm.group(1))
            mcall = re.search(r"CALL([A-Z][A-Z0-9]*)\((.*)\)", t)
            if mcall:
                called.add(mcall.group(1)); setn.update(names(mcall.group(2)))
            a = re.match(r"DO\d+([A-Z][A-Z0-9]*)=", t)
            if a:
                setn.add(a.group(1))
            for a in re.finditer(r",([A-Z][A-Z0-9]*)=", t):          # implied DO
                setn.add(a.group(1))
            if re.match(r"READ", t):
                setn.update(names(re.sub(r"^READ\([^)]*\)", "", t)))
            a = re.match(r"ASSIGN\d+TO([A-Z][A-Z0-9]*)", t)
            if a:
                setn.add(a.group(1))
            # assignment, possibly after a logical IF
            rest = t
            while True:
                mi = re.match(r"IF\(", rest)
                if not mi:
                    break
                d = 0
                for k, ch in enumerate(rest[2:], 2):
                    d += ch == "("; d -= ch == ")"
                    if d == 0:
                        break
                rest = rest[k + 1:]
            a = re.match(r"([A-Z][A-Z0-9]*)(\([^=]*\))?=", rest)
            if a and not re.match(r"DO\d", rest):
                if a.group(2) and a.group(1) not in arrays:            # statement function
                    setn.add(a.group(1)); setn.update(names(a.group(2)))
                setn.add(a.group(1)); lhs.setdefault(a.group(1), n)
                reads.update(names(rest[a.end():])); reads.update(names(t[:len(t) - len(rest)]))
                if a.group(2):
                    reads.update(names(a.group(2)))
            else:
                reads.update(names(t))
            for w in names(t):
                uses.setdefault(w, n)
        if "--setonly" in sys.argv:
            for w, n in sorted(lhs.items(), key=lambda x: x[1]):
                if w not in reads and w not in dummies and w not in common and w != uname:
                    print(f"{uname:8s} {w:8s} line {n:5d} {mp[n - 1].split(chr(9))[1]}:{mp[n - 1].split(chr(9))[2]}  {src[n - 1].strip()[:70]}")
            continue
        bad = sorted((uses[w], w) for w in uses
                     if w not in setn and w not in INTRINSIC and w not in called and not w.startswith("ERROR"))
        for n, w in bad:
            print(f"{uname:8s} {w:8s} line {n:5d} {mp[n - 1].split(chr(9))[1]}:{mp[n - 1].split(chr(9))[2]}  {src[n - 1].strip()[:70]}")


if __name__ == "__main__":
    main()
