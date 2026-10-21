"""Check every DCON cell (PDF pp. 174-177) the way Nd-151 was settled on 21 Oct:
  1. exact: is the value exactly 0.693147/T (7 printed digits) for a round T (1-4 significant digits in s/min/h/d/y)?
  2. 1968: the Tompkins 1968 tape's half-life for the same nuclide, as a 7-digit DCON string, and where the digits differ;
  3. glyphs: a kNN vote (same printing, pp. 174-177) on every mantissa character, with the grid shift that best reproduces
     the field's other characters; characters whose vote disagrees with our reading are listed.

usage: python3 -I dconcheck.py <workdir> <bt0.txt> <exp_tran.json> <bycard68.json> <out.tsv> [--only resolved]
--only resolved: just the cells listed in tablefix.tsv's "DCON resolved from the nuclide ... half-life" section.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

wd = Path(sys.argv[1]); sys.path.insert(0, str(wd / "tools")); sys.path.insert(0, str(Path(__file__).parent))
import glyphs
from graph import load, info

bt0, expf, byf, out = sys.argv[2:6]
LN2 = 0.693147
UNITS = [("s", 1), ("min", 60), ("h", 3600), ("d", 86400), ("y", 3.15576e7), ("y", 3.1536e7), ("y", 3.1557e7)]
U68 = {1: 1, 2: 60, 3: 3600, 4: 86400, 5: 3.15576e7}
sign_col = lambda k: 7 + 13 * (k - 1)
EL = {27: "Co", 28: "Ni", 29: "Cu", 30: "Zn", 31: "Ga", 32: "Ge", 33: "As", 34: "Se", 35: "Br", 36: "Kr", 37: "Rb", 38: "Sr",
      39: "Y", 40: "Zr", 41: "Nb", 42: "Mo", 43: "Tc", 44: "Ru", 45: "Rh", 46: "Pd", 47: "Ag", 48: "Cd", 49: "In", 50: "Sn",
      51: "Sb", 52: "Te", 53: "I", 54: "Xe", 55: "Cs", 56: "Ba", 57: "La", 58: "Ce", 59: "Pr", 60: "Nd", 61: "Pm", 62: "Sm",
      63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy"}

# DCON cells in NUCLID order, with their scan position
cells = []
for pg in range(174, 178):
    for row in open(wd / "tables" / f"p{pg:03d}.tsv"):
        f = row.rstrip("\n").split("\t")
        if len(f) > 3 and f[1] == "DCON":
            for k, v in enumerate([x for x in f[3].split() if re.match(r"-?\d", x)], 1):
                cells.append((pg, int(f[0]), k, v))
N, _ = load(bt0)
only = None
if "--only" in sys.argv:
    txt = (wd / "tablefix.tsv").read_text().split("# DCON resolved from the nuclide")[1].split("\n# ")[0]
    only = set()
    for r in txt.splitlines()[1:]:
        x = r.split("\t")
        if len(x) >= 4:
            if x[2] == "*":
                only.update((x[0], int(x[1]), k) for k in range(1, 6))
            elif x[2].isdigit():
                only.add((x[0], int(x[1]), int(x[2])))


def exact(v):
    """round half-lives T with f'{LN2/T:.6E}' == v"""
    out = []
    for u, s in UNITS:
        t = LN2 / float(v) / s
        for nd in (1, 2, 3, 4):
            r = float(f"{t:.{nd}g}")
            if f"{LN2 / (r * s):.6E}" == f"{float(v):.6E}":
                out.append(f"{r:g} {u}"); break
    return out


# 1968 half-life per nuclide index k (first card of the nuclide)
exp = json.load(open(expf)); by = json.load(open(byf))
t68 = {}
for i, e in enumerate(exp, 1):
    rs = [r for r in by.get(str(i), {}).values() if r and "T" in r and r.get("u") in U68]
    if not rs or e["k"] in t68:
        continue
    vals = Counter(round(r["T"] * 10 ** r["e"] * U68[r["u"]], 6) for r in rs)
    T, n = vals.most_common(1)[0]
    t68[e["k"]] = (T, n, len(rs))

# glyph training set (same printing)
X, Y = [], []
for pg in range(174, 178):
    J, a = glyphs.load(wd, pg)
    for c in cells:
        if c[0] != pg:
            continue
        for i, ch in enumerate(c[3].lstrip("-")[:8]):
            if ch.isdigit():
                v, _ = glyphs.cell_img(a, J["lines"][c[1] - 1], J["meta"], sign_col(c[2]) + 1 + i)
                if v is not None:
                    X.append(((v - v.mean()) / (v.std() + 1e-9)).ravel()); Y.append((ch, c[:3]))
X = np.array(X); YL = np.array([y[0] for y in Y]); YC = [y[1] for y in Y]
PAGES = {pg: glyphs.load(wd, pg) for pg in range(174, 178)}


def votes(c):
    """per mantissa character: (our char, voted char, confidence) at the best grid shift"""
    pg, ln, k, v = c; J, a = PAGES[pg]; body = v.lstrip("-")
    mask = np.array([yc != (pg, ln, k) for yc in YC])
    best = None
    for sh in (0, -0.1, 0.1, -0.2, 0.2, -0.3, 0.3, -0.4, 0.4):
        meta = dict(J["meta"], col1_x=J["meta"]["col1_x"] + sh * J["meta"]["pitch"])
        res = []
        for i, ch in enumerate(body[:8]):
            if not ch.isdigit():
                continue
            g, _ = glyphs.cell_img(a, J["lines"][ln - 1], meta, sign_col(k) + 1 + i)
            if g is None:
                res.append((i, ch, "?", 0.0)); continue
            q = ((g - g.mean()) / (g.std() + 1e-9)).ravel(); s = X[mask] @ q / len(q); lab = YL[mask]
            o = np.argsort(-s)[:9]; vt = Counter(lab[o]).most_common()
            res.append((i, ch, vt[0][0], vt[0][1] / 9))
        score = sum(r[1] == r[2] for r in res)
        if best is None or score > best[0]:
            best = (score, sh, res)
    return best


rows = []
for idx, c in enumerate(cells):
    pg, ln, k, v = c
    if only is not None and (f"p{pg:03d}", ln, k) not in only:
        continue
    if idx >= len(N) or not N[idx] or float(v) == 0:
        continue
    I = info(N[idx]); name = f"{EL.get(I['Z'], I['Z'])}-{I['A']}{'m' if I['M'] else ''}"
    ex = exact(v)
    T68 = t68.get(idx)
    s68 = f"{LN2 / T68[0]:.6E}" if T68 else ""
    ours = f"{float(v):.6E}"
    diff = [i for i, (x, y) in enumerate(zip(ours, s68)) if x != y] if s68 else []
    _, sh, vt = votes(c)
    dis = [f"{i}:{o}->{g}({p:.2f})" for i, o, g, p in vt if o != g]
    if ex and s68 == ours:
        verdict = "ok (exact, = 1968)"
    elif ex and not dis:
        verdict = "ok (exact; 1968 differs)" if s68 else "ok (exact)"
    elif ex:
        verdict = "check glyphs (exact, but the vote disagrees)"
    elif s68 and len(diff) <= 3 and float(s68) and exact(s68):
        verdict = "DOUBTFUL: not exact; 1968 value is exact and close in digits"
    else:
        verdict = "DOUBTFUL: not exact"
    rows.append((pg, ln, k, name, v, LN2 / float(v), ";".join(ex), T68[0] if T68 else "", s68, "".join(map(str, diff)), sh, " ".join(dis), verdict))
with open(out, "w") as f:
    f.write("page\tline\tfield\tnuclide\tours\tT_ours_s\texact_T\tT_1968_s\tdcon_1968\tdiff_pos\tshift\tvote_disagrees\tverdict\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")
print(f"{len(rows)} cells; " + ", ".join(f"{k}: {n}" for k, n in Counter(r[-1].split(":")[0].split(" (")[0] for r in rows).items()))
for r in rows:
    if not r[-1].startswith("ok"):
        print(f"p{r[0]} L{r[1]} f{r[2]} {r[3]:9s} {r[4]:13s} T={r[5]:.6g}s exact=[{r[6]}] 1968: T={r[7]} -> {r[8]} diff@{r[9]} shift {r[10]} votes {r[11]} | {r[12]}")
