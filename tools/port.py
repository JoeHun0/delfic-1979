"""Mechanical CDC-to-gfortran port of a transcribed deck (src/<deck>.f -> run/<deck>_port.f; --deck dtm).

Only dialect changes, each logged in run/port.log; the transcription itself is not edited:
  1. CDC '*...*' string delimiters in FORMAT statements -> '...'.
  2. EQUIVALENCE with a single (linear) subscript on a 2-D array -> the equivalent 2-D subscript
     (GDPST(10,100), CX(50,10)).
"""
import re
import sys
from pathlib import Path

DIMS = {"GDPST": (10, 100), "CX": (50, 10)}


def main():
    wd = Path(sys.argv[1])
    deck = sys.argv[sys.argv.index("--deck") + 1] if "--deck" in sys.argv else "icrm"
    src = (wd / "src" / f"{deck}.f").read_text().splitlines()
    out, log = [], []
    infmt = inequiv = False
    instar = False
    holl = 0
    for n, l in enumerate(src, 1):
        if not l.strip() or l[:1] in "C*":
            out.append(l); continue
        l = l.ljust(72)[:72]
        cont = l[5] not in " 0"
        if not cont:
            body = l[6:].lstrip()
            infmt = bool(re.match(r"FORMAT\s*\(", body))
            inequiv = body.startswith("EQUIVALENCE")
            instar = False
        if infmt and "*" in l[6:] and deck == "icrm":           # CDC *...* strings occur only in ICRM
            if not cont:
                holl = 0
            b = list(l[6:]); k = 0
            changed = False
            while k < len(b):
                ch = b[k]
                if holl > 0:
                    holl -= 1; k += 1; continue
                if instar:
                    if ch == "*":
                        b[k] = "'"; instar = False; changed = True
                    k += 1; continue
                m = re.match(r"(\d+)H", "".join(b[k:k + 6])) if (k == 0 or not (b[k - 1].isdigit() or b[k - 1] == ".")) else None
                if m:
                    holl = int(m.group(1)); k += len(m.group(0)); continue
                if ch == "*":
                    b[k] = "'"; instar = True; changed = True
                k += 1
            if changed:
                log.append(f"{n}: star strings -> quotes")
                l = l[:6] + "".join(b)
        if inequiv:
            def sub(m):
                name, i = m.group(1), int(m.group(2))
                if name in DIMS:
                    r = DIMS[name][0]
                    return f"{name}({(i - 1) % r + 1},{(i - 1) // r + 1})"
                return m.group(0)
            new = l[:6] + re.sub(r"\b([A-Z]+)\(\s*(\d+)\s*\)", sub, l[6:])
            if new != l:
                log.append(f"{n}: linear EQUIVALENCE subscript -> 2-D: {new[6:].strip()}")
                l = new
        l = l.rstrip()
        if len(l) > 72:                      # only EQUIVALENCE lines grow; split at a comma
            cut = l.rfind(",", 6, 72) + 1
            out.append(l[:cut]); out.append("     $" + l[cut:])
            log.append(f"{n}: split long line")
            continue
        out.append(l)
    (wd / "run").mkdir(exist_ok=True)
    (wd / "run" / f"{deck}_port.f").write_text("\n".join(out) + "\n")
    (wd / "run" / ("port.log" if deck == "icrm" else f"port-{deck}.log")).write_text("\n".join(log) + "\n")
    print(len(log), "port changes")


if __name__ == "__main__":
    main()
