"""Apply review decisions on a tcheck.py suggestion list to tablefix.tsv.
usage: python3 -I decide.py <workdir> <sugg.txt> <offset> "1:K 2:K 3:? 4:S 5:=1.0E-1 ..."
S = first suggestion, K = keep the reading (confirmed), =v = this value, ? = unresolved (noted in JUDGEMENT-CALLS)."""
import re
import sys
from pathlib import Path

wd = Path(sys.argv[1]); rows = Path(sys.argv[2]).read_text().splitlines(); off = int(sys.argv[3])
fix = open(wd / "tablefix.tsv", "a"); jc = open(wd / "JUDGEMENT-CALLS.txt", "a")
for d in sys.argv[4].split():
    k, v = d.split(":", 1); r = rows[off + int(k) - 1]
    m = re.match(r"\s*\d+ p(\d+) L(\d+) f(\d) +(\S+)\s*(\S+)?", r)
    pg, ln, f, read, sug = m.group(1), m.group(2), m.group(3), m.group(4), (m.group(5) or "").split("(")[0]
    val = {"S": sug, "K": read, "?": read}.get(v, v.lstrip("="))
    fix.write(f"p{pg}\t{ln}\t{f}\t{val}\n")
    if v == "?":
        jc.write(f"TABLES p{pg} L{ln} f{f} DCON {read}: broken glyph, kept the reading — UNRESOLVED, check against the nuclide half-life\n")
    print(f"p{pg} L{ln} f{f} {read} -> {val}")
