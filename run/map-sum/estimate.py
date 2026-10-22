"""Estimate the book's true sum of map ordinates from (1) the prediction with the book FP table and (2) the book's printed
cells: ORNL's typing for exponent <= 1 (two gross misreads corrected) and our scan verdicts for exponent 2-3.
usage: python3 -I estimate.py   (run from anywhere)"""
import re
from pathlib import Path
M = Path(__file__).resolve().parent
def load_out(fn):
    L = fn.read_text().split('\n'); U = {}
    for i, l in enumerate(L):
        m = re.match(r'^\s+(-?\d+)\.\s+((?:\d\.\d{3}\s*)+)$', l)
        if m:
            ex = [int(x) for x in L[i - 1].split()]; ms = [float(x) for x in m.group(2).split()]
            if len(ex) == 13 and len(ms) == 13: U[m.group(1)] = list(zip(ms, ex))
    fsum = float(re.search(r'SUM OF MAP ORDINATES =\s*([\d.E+]+)', fn.read_text()).group(1))
    return U, fsum
P, pF = load_out(M / 'opm-bookfp.out')
B = {}
for l in (M / 'ornl-book-map.tsv').read_text().split('\n'):
    if l and not l.startswith('#'):
        f = l.split('\t'); B[f[0]] = [(float(c.split('e')[0]), int(c.split('e')[1])) for c in f[1:]]
B['36000'][2] = (9.043, 1); B['27000'][2] = (9.957, 1)
v = lambda c: c[0] * 10 ** c[1]
pcells = sum(v(c) for r in P.values() for c in r)
small = sum(v(B[y][k]) - v(P[y][k]) for y in B for k in range(13) if B[y][k][1] <= 1)
clear = 0.0; amb = 0.0
for l in (M / 'scan-verdicts.tsv').read_text().split('\n'):
    f = l.split('\t')
    if len(f) < 3 or l.startswith('#') or not f[1].isdigit() or B[f[0]][int(f[1])][1] < 2: continue
    y, k, s = f[0], int(f[1]), f[2].split()[0]
    lsd = 10 ** (B[y][k][1] - 3)
    if s == '?': amb += v(B[y][k]) - v(P[y][k])
    elif s != '=': clear += int(s) * lsd
off = pF - pcells
print(f'prediction from the book FP table: FSUM {pF:.1f} (printed cells {pcells:.2f})')
print(f'book - prediction: exponent<=1 cells {small:+.2f}, large cells read clearly {clear:+.2f}, unreadable large cells 0 .. {amb:+.2f}')
lo = pcells + small + clear + min(0, amb) + off; hi = pcells + small + clear + max(0, amb) + off
print(f'estimated book FSUM {lo:.1f} .. {hi:.1f} (+-0.5 rounding); candidates 28553.8 (5th digit 3), 28550.8 (0), 28551.8 (1)')
