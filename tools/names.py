"""Find misread identifiers: names used rarely that differ from a frequent name only by OCR-confusable
characters (O/D/0/C/U/Q, I/L/1/J, S/5, B/8, Z/2, G/6, P/F/R, H/M/W/N, E/F, K/R, V/Y).

usage: python3 -I names.py <workdir> [--apply]
Hollerith strings (nH...) and comments are ignored. Prints suspect -> candidate with counts.
With --apply, writes the unambiguous replacements (candidate used >= 3 times, suspect <= 2 times,
only one candidate) to namefix.tsv, which build.py applies to code text outside Hollerith fields.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

GROUPS = ["OD0CUQ", "IL1J", "S5", "B8", "Z2", "G6C", "PFR", "HMWN", "EF", "KR", "VY", "T7", "A4"]
CANON = {}
for g in GROUPS:
    for ch in g:
        CANON.setdefault(ch, set()).update(g)
KEYWORDS = {"IF", "GO", "TO", "GOTO", "DO", "CALL", "RETURN", "END", "CONTINUE", "SUBROUTINE", "FUNCTION",
            "COMMON", "DIMENSION", "DATA", "EQUIVALENCE", "FORMAT", "READ", "WRITE", "REWIND", "STOP",
            "REAL", "INTEGER", "LOGICAL", "EXTERNAL", "AND", "OR", "NOT", "EQ", "NE", "LT", "LE", "GT", "GE",
            "FILE", "ENDFILE", "BACKSPACE", "PRINT", "PAUSE", "ASSIGN", "TRUE", "FALSE"}


def strip_holl(s):
    out, i = [], 0
    while i < len(s):
        m = re.match(r"(?<![A-Z0-9])(\d+)H", s[i:]) if (i == 0 or not s[i - 1].isalnum()) else None
        if m:
            n = int(m.group(1)); i += len(m.group(0)) + n; out.append(" "); continue
        out.append(s[i]); i += 1
    return "".join(out)


def statements(src):
    st, cur = [], None
    for ln, l in enumerate(src, 1):
        if not l.strip() or l[:1] in "C*":
            continue
        l = l.ljust(72)
        if l[5] not in " 0" and cur is not None:
            cur[1] += l[6:72]; continue
        if cur:
            st.append(cur)
        cur = [ln, l[6:72]]
    if cur:
        st.append(cur)
    return st


def close(a, b):
    if len(a) != len(b) or a == b:
        return False
    return all(x == y or y in CANON.get(x, ()) for x, y in zip(a, b))


def main():
    deck = sys.argv[sys.argv.index("--deck") + 1] if "--deck" in sys.argv else "icrm"
    wd = Path(sys.argv[1]); src = (wd / "src" / f"{deck}.f").read_text().splitlines()
    cnt = Counter(); where = defaultdict(list)
    for ln, s in statements(src):
        s = strip_holl(s.upper())
        s = re.sub(r"'[^']*'", " ", s)
        for m in re.finditer(r"(?<![0-9])(?<![0-9]\.)[A-Z][A-Z0-9]*", s.replace(" ", " ")):
            w = m.group(0)
            if w in KEYWORDS or re.fullmatch(r"(E|D)\d+", w):
                continue
            cnt[w] += 1; where[w].append(ln)
    names = sorted(cnt, key=lambda w: -cnt[w])
    fixes = []
    for w in sorted(cnt, key=lambda w: cnt[w]):
        if cnt[w] > 3:
            continue
        cands = [v for v in names if cnt[v] >= max(3, 2 * cnt[w]) and close(w, v)]
        if cands:
            print(f"{w:10s} x{cnt[w]}  ->  {', '.join(f'{v} x{cnt[v]}' for v in cands[:4])}   lines {where[w][:6]}")
            if len(cands) == 1:
                fixes.append((w, cands[0]))
    if "--apply" in sys.argv:
        (wd / "namefix.tsv").write_text("".join(f"{a}\t{b}\n" for a, b in fixes))
        print(len(fixes), "written to namefix.tsv")


if __name__ == "__main__":
    main()
