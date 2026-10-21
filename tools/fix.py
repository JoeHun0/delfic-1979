"""Append card fixes by src line number: fix.py <workdir> [--deck dtm] <srcline> <fix> [<srcline> <fix> ...]
<fix> is either s|old|new|... or a full card ('|' marks column 7). --deck dtm uses src/dtm.f and dtm.map.
An s|old|new| fix is refused unless every 'old' text occurs on that source line (nothing is written then)."""
import sys
from pathlib import Path
deck = "icrm"
if "--deck" in sys.argv:
    k = sys.argv.index("--deck"); deck = sys.argv[k + 1]; del sys.argv[k:k + 2]
wd = Path(sys.argv[1]); mp = (wd / "src" / f"{deck}.map").read_text().splitlines()
src = (wd / "src" / f"{deck}.f").read_text().splitlines()
rows = []
for n, fx in zip(sys.argv[2::2], sys.argv[3::2]):
    _, pg, ln = mp[int(n) - 1].split("\t")
    if fx.startswith("s|"):
        parts = fx.split("|")
        for k in range(1, len(parts) - 1, 3):
            if parts[k] not in src[int(n) - 1]:
                sys.exit(f"REFUSED: {parts[k]!r} not on src line {n}: {src[int(n) - 1]!r}")
    rows.append(f"{pg}\t{ln}\t{fx}\n")
with open(wd / "cardfix.tsv", "a") as f:
    for r in rows:
        f.write(r); print(r.rstrip())
