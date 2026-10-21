"""Show a line's inked cells (with ink amounts) under a reading, to find where a count mismatch is.
usage: python3 -I showcells.py <workdir> <page> <line> "<text>" """
import json, sys
from pathlib import Path
wd = Path(sys.argv[1]); pg, ln, txt = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
L = json.load(open(wd / "lines" / f"p{pg:03d}.json"))["lines"][ln - 1]
cols = [c for c in L["cols"] if c <= 72]; ink = L.get("ink", {})
chars = [c for c in txt if not c.isspace()]
for k, c in enumerate(cols):
    print(f"col {c:2d} ink {ink.get(str(c),0):4d}  {chars[k] if k < len(chars) else '?'}")
