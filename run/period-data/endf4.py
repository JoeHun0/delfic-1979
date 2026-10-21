"""Compare DELFIC's 1979 decay constants with the ENDF/B-IV (1974) fission-product file, as an era reference.

usage: python3 -I endf4.py <EN4_FP.DAT | en4-halflives.txt> <bt0.txt> <out.tsv> [dcon-check.tsv]
Reads every MF8/MT457 section (decay data): HEAD = ZA, AWR, LIS (isomer state), ...; the next record starts with T1/2 (s).
For each DELFIC nuclide (NUCLID: A, Z, isomer) prints DELFIC's T and the ENDF/B-IV T, and whether DELFIC's DCON is the
exact 0.693147/T of the ENDF/B-IV value. With dcon-check.tsv (from dconcheck.py) the still-open cells are marked.
Also lists the MF8 MT454/459 fission-yield sections it finds (fissioning material, number of entries), for a later check.
The input file is treated as plain data: fixed 80-column ENDF records, nothing else is interpreted.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from graph import load, info

LN2 = 0.693147


def num(s):
    """ENDF float: ' 1.234567+5', '-1.2345-12', ' 1.0E+00', or blank"""
    s = s.strip()
    if not s:
        return 0.0
    s = s.replace(" ", "")
    s = re.sub(r"(?<=[0-9.])([+-])(\d+)$", r"E\1\2", s) if "E" not in s.upper() else s
    return float(s)


def records(path):
    for line in open(path, errors="replace"):
        line = line.rstrip("\n").ljust(80)
        try:
            mat, mf, mt = int(line[66:70]), int(line[70:72]), int(line[72:75])
        except ValueError:
            continue
        yield mat, mf, mt, line


def sections(path):
    cur, key = [], None
    for mat, mf, mt, line in records(path):
        k = (mat, mf, mt)
        if mt == 0 or mf == 0:
            if cur:
                yield key, cur
            cur, key = [], None
            continue
        if k != key and cur:
            yield key, cur; cur = []
        key = k; cur.append(line)
    if cur:
        yield key, cur


endf, bt0, out = sys.argv[1:4]
dec, yields = {}, []
if endf.endswith(".txt"):           # the extract en4-halflives.txt: "ZA LIS T1/2_s" per line
    for line in open(endf):
        if line.startswith("#") or not line.strip():
            continue
        za, lis, t = line.split(); za = int(za)
        dec.setdefault((za % 1000, za // 1000, int(lis)), (float(t), 0.0, 0))
for (mat, mf, mt), lines in ([] if endf.endswith(".txt") else sections(endf)):
    if mf in (1, 8) and mt == 457 and len(lines) >= 2:      # ENDF/B-IV keeps decay data in MF1, later versions in MF8
        za, awr = num(lines[0][0:11]), num(lines[0][11:22])
        lis = int(num(lines[0][22:33]))
        t = num(lines[1][0:11]); dt = num(lines[1][11:22])
        z, a = int(za) // 1000, int(za) % 1000
        dec.setdefault((a, z, lis), (t, dt, mat))
    elif mf == 8 and mt in (454, 459):
        yields.append((mat, mt, num(lines[0][0:11]), len(lines)))

open_cells = {}
if len(sys.argv) > 4:
    for row in open(sys.argv[4]):
        f = row.rstrip("\n").split("\t")
        if len(f) > 12 and f[0] != "page" and not f[12].startswith("ok"):
            open_cells[f[3]] = f[12]

N, _ = load(bt0)
dcon = [l.split()[4] for l in open(bt0)]
rows = []
for k, v in enumerate(N):
    if not v:
        continue
    I = info(v); key = (I["A"], I["Z"], I["M"])
    lam = float(dcon[k]); T = LN2 / lam if lam > 0 else 0.0
    e = dec.get(key)
    if not e:
        rows.append((k + 1, *key, T, "", "", "", "", "not in ENDF/B-IV")); continue
    t4, dt4, mat = e
    ours = f"{lam:.6E}"
    ex = t4 > 0 and f"{LN2 / t4:.6E}" == ours
    rel = (T / t4 - 1) if t4 > 0 and T > 0 else float("nan")
    # the ENDF/B-IV half-life as DELFIC would have used it: as is, or rounded to 2-4 significant digits in a natural unit;
    # keep the candidate whose 7-digit DCON string is closest to ours (number of differing characters, and where)
    best = None
    if t4 > 0 and lam > 0:
        for u, sc in (("s", 1), ("min", 60), ("h", 3600), ("d", 86400), ("y", 3.15576e7)):
            for nd in (None, 2, 3, 4):
                tt = t4 / sc if nd is None else float(f"{t4 / sc:.{nd}g}")
                if tt <= 0:
                    continue
                cand = f"{LN2 / (tt * sc):.6E}"
                d = [i for i, (x, y) in enumerate(zip(ours, cand)) if x != y]
                lab = f"{tt:g} {u}"
                if best is None or len(d) < len(best[0]):
                    best = (d, cand, lab)
    nd_ = len(best[0]) if best else ""
    note = "exact" if ex else ("only char(s) " + ",".join(map(str, best[0])) + f" differ: {best[1]} = ln2/{best[2]}"
                               if best and 0 < len(best[0]) <= 2 else ("same digits as ln2/" + best[2] if best and not best[0] else ""))
    rows.append((k + 1, *key, T, t4, dt4, f"{rel:+.4f}", nd_, note))
with open(out, "w") as f:
    f.write("index\tA\tZ\tM\tT_delfic_s\tT_endfb4_s\tdT_endfb4_s\trel_diff\tn_chars_differ\tnote\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")
found = [r for r in rows if r[5] != ""]
print(f"ENDF/B-IV: {len(dec)} decay sections, {len(yields)} yield sections; DELFIC nuclides {len(rows)}, matched {len(found)}")
from collections import Counter
print("  characters differing from the closest ENDF/B-IV-based DCON:", dict(sorted(Counter(r[8] for r in found if isinstance(r[8], int)).items())))
SYM0 = "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy".split()
print("  one or two characters away (candidate misreads, or DELFIC typed a near value):")
for r in found:
    if r[8] in (1, 2):
        print(f"    #{r[0]} {SYM0[r[2] - 1]}-{r[1]}{'m' if r[3] else ''}: ours {float(LN2 / r[4]) if r[4] else 0:.6E}  {r[9]}")
if yields:
    print("  yield sections (MAT, MT, ZA, lines):", yields[:12], "..." if len(yields) > 12 else "")
SYM = "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru " \
      "Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy".split()
for r in rows:
    name = f"{SYM[r[2] - 1]}-{r[1]}{'m' if r[3] else ''}"
    if name in open_cells and r[5] != "":
        print(f"  open cell {name}: DELFIC T={r[4]:.6g} s, ENDF/B-IV T={r[5]:.6g} s ({r[7]}); {r[8]} chars differ; {r[9]}")
