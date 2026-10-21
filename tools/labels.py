"""Labels defined in the program unit around a source line: labels.py <workdir> <deck> <line> [<line> ...]"""
import re
import sys
from pathlib import Path

wd = Path(sys.argv[1]); src = (wd / "src" / f"{sys.argv[2]}.f").read_text().splitlines()
starts = [i for i, l in enumerate(src) if re.match(r"\s{6}\s*(SUBROUTINE|PROGRAM|FUNCTION)\b", l)] + [len(src)]
for n in map(int, sys.argv[3:]):
    a = max(s for s in starts if s <= n - 1); b = min(s for s in starts if s > n - 1)
    labs = []
    for i in range(a, b):
        l = src[i].ljust(6)
        if l[:1] not in "C*" and l[:5].strip().isdigit():
            labs.append(l[:5].strip())
    print(n, src[a].strip()[:40], "|", " ".join(labs))
