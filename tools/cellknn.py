"""Score one disputed character of a PAM DATA-table field against every digit, with a nearest-neighbour vote over
the glyphs of the same printing (DATA tables pp. 174-177, read via tables/p<page>.tsv), the disputed field left out.

usage: python3 -I cellknn.py <workdir> <page> <line> <field 1-5> <char> [k] [--shift cols]
<char> as in digitsheet.py (position in the value without its sign). Prints the ink amount against typical cells, the
k nearest neighbours' labels, and the best correlation per digit. Trailing zeros count as zeros (every ERM/DCON on
these pages is x.xx0000 or a full 7-digit value), so broken zeros are in the 0 class, as they should be.
"""
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import glyphs

wd, page, line, field, char = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
args = [x for x in sys.argv[6:] if not x.startswith("--")]
K = int(args[0]) if args and args[0].lstrip("-").isdigit() else 7
SHIFT = float(sys.argv[sys.argv.index("--shift") + 1]) if "--shift" in sys.argv else 0.0
sign_col = lambda k: 7 + 13 * (k - 1)


def cells(pg):
    for row in open(wd / "tables" / f"p{pg:03d}.tsv"):
        f = row.rstrip("\n").split("\t")
        if len(f) < 4 or not f[0].isdigit():
            continue
        vals = [v for v in f[3].split() if re.match(r"-?\d", v)]
        for k, v in enumerate(vals, 1):
            body = v.lstrip("-")
            for i, ch in enumerate(body[:8]):           # digits and point of the mantissa
                if ch.isdigit():
                    yield int(f[0]), k, i, sign_col(k) + 1 + i, ch


X, Y, ink = [], [], []
for pg in range(174, 178):
    J, a = glyphs.load(wd, pg)
    for ln, k, i, col, ch in cells(pg):
        if pg == page and ln == line and k == field:
            continue
        v, hh = glyphs.cell_img(a, J["lines"][ln - 1], J["meta"], col)
        if v is None:
            continue
        X.append(((v - v.mean()) / (v.std() + 1e-9)).ravel()); Y.append(ch); ink.append(v.sum())
X, Y = np.array(X), np.array(Y)
J, a = glyphs.load(wd, page)
J["meta"] = dict(J["meta"], col1_x=J["meta"]["col1_x"] + SHIFT * J["meta"]["pitch"])   # query line only
L = J["lines"][line - 1]; col = sign_col(field) + 1 + char
P, x1 = J["meta"]["pitch"], J["meta"]["col1_x"]
raw = a[L["y0"]:L["y1"], int(x1 + (col - 1) * P - P / 2):int(x1 + (col - 1) * P + P / 2)]
v, hh = glyphs.cell_img(a, L, J["meta"], col)
print(f"p{page} L{line} f{field} char {char} (column {col}): {raw.sum()} ink pixels; "
      f"typical digit cell on these pages: median {int(np.median([0]))}" if v is None else
      f"p{page} L{line} f{field} char {char} (column {col}): {raw.sum()} ink pixels in the cell")
if v is None:
    sys.exit("too little ink to classify")
q = ((v - v.mean()) / (v.std() + 1e-9)).ravel()
sim = X @ q / len(q)
order = np.argsort(-sim)[:K]
print(f"{len(Y)} training glyphs; {K} nearest:", " ".join(f"{Y[j]}({sim[j]:.2f})" for j in order))
print("vote:", dict(Counter(Y[order]).most_common()))
best = {d: float(sim[Y == d].max()) for d in "0123456789" if (Y == d).any()}
mean5 = {d: float(np.sort(sim[Y == d])[-5:].mean()) for d in best}
for d in sorted(best, key=lambda d: -mean5[d]):
    print(f"  {d}: best {best[d]:.3f}  mean of top 5 {mean5[d]:.3f}  ({(Y == d).sum()} samples)")
