"""Consistency checks on the PAMI DATA tables read by tables.py.

usage: python3 -I tcheck.py <workdir> dcon [page]      half-life of each DCON value; '*' = not a round half-life
       python3 -I tcheck.py <workdir> branch           BRANCH fractions grouped into sets summing to 1
       python3 -I tcheck.py <workdir> values ARRAY     the array's values in DATA order with their page/line

DCON values are decay constants lambda = 0.693147/T (seconds); a value read with a wrong digit almost never gives
a half-life that is a round number of seconds, minutes, hours, days or years, so the round ones are confirmed.
"""
import sys
from pathlib import Path

LN2 = 0.693147
UNITS = (("s", 1.0), ("m", 60.0), ("h", 3600.0), ("d", 86400.0), ("y", 3.15576e7), ("y5", 3.1536e7))
NICE = {"s": (1e-3, 1e5), "m": (1, 1e4), "h": (1, 1e4), "d": (1, 1e4), "y": (0.1, 1e9), "y5": (0.1, 1e9)}


def arrays(wd):
    """array -> [(page, line, field, value-string)] in DATA order."""
    out = {}
    for pg in range(174, 183):
        f = wd / "tables" / f"p{pg:03d}.tsv"
        for r in f.read_text().splitlines():
            x = r.split("\t")
            toks = [t for t in x[3].split() if t != "/"]
            for k, t in enumerate(toks):
                out.setdefault(x[1], []).append((pg, int(x[0]), k + 1, t))
    return out


def round_t(v, t=None):
    """'2.5h' when the printed decay constant is exactly 0.693147/T (to the printed 7 digits) for a half-life T
    that is a round number (<= 4 significant digits) of seconds, minutes, hours, days or years."""
    if v <= 0:
        return "-"
    txt = f"{v:.6E}"
    T = LN2 / v
    for u, f in UNITS:
        for nd in (1, 2, 3, 4):
            r = float(f"{T / f:.{nd}g}")
            if r and f"{LN2 / (r * f):.6E}" == txt:
                return f"{r:g}{u}"
    return None


def main():
    wd = Path(sys.argv[1]); cmd = sys.argv[2]; A = arrays(wd)
    if cmd == "dcon":
        pg = int(sys.argv[3]) if len(sys.argv) > 3 else None
        n = 0
        for k, (p, l, f, t) in enumerate(A.get("DCON", [])):
            if pg and p != pg:
                continue
            try:
                v = float(t)
            except ValueError:
                print(f"{k+1:4d} p{p} L{l} f{f} {t:>13s}  ?"); continue
            rt = round_t(v) if v else "zero"
            T = LN2 / v if v else 0
            if not rt:
                n += 1
            print(f"{k+1:4d} p{p} L{l} f{f} {t:>13s}  T={T:.6g}s {rt or '*'}")
        print("not round:", n)
    elif cmd == "branch":
        vals = A.get("BRANCH", []); s = 0.0; grp = []
        for p, l, f, t in vals:
            v = float(t); s += v; grp.append(t)
            if abs(s - 1) < 1e-6:
                print("ok ", " + ".join(grp)); s = 0.0; grp = []
            elif s > 1 + 1e-6:
                print(f"BAD p{p} L{l} f{f}:", " + ".join(grp), "=", s); s = 0.0; grp = []
        if grp:
            print("rest:", " + ".join(grp), "=", s)
    elif cmd == "values":
        for k, (p, l, f, t) in enumerate(A.get(sys.argv[3], [])):
            print(f"{k+1:4d} p{p} L{l} f{f} {t}")


if __name__ == "__main__":
    main()


def suggest(v, txt):
    """round-half-life decay constants whose printed form differs from txt in one or two characters."""
    out = []
    T = LN2 / v if v > 0 else 0
    seen = set()
    for u, f in UNITS:
        for nd in (1, 2, 3, 4):
            for scale in (1, 10, 0.1):
                if not T:
                    continue
                r = float(f"{T * scale / f:.{nd}g}")
                if not r or not NICE[u][0] <= r <= NICE[u][1]:
                    continue
                c = f"{LN2 / (r * f):.6E}".replace("E+0", "E+").replace("E-0", "E-")
                if len(c) == len(txt) and c not in seen:
                    d = sum(a != b for a, b in zip(c, txt))
                    if 0 < d <= 2:
                        seen.add(c); out.append((d, c, f"{r:g}{u}"))
    return sorted(out)


def sheet(wd, out_png, items):
    """items: (page, line, field, read, note) -> contact sheet of the field crops."""
    import json
    from PIL import Image, ImageDraw
    sys.path.insert(0, str(Path(__file__).parent))
    from tables import render
    strips = []
    for pg, l, f, read, note in items:
        J = json.load(open(wd / "lines" / f"p{pg:03d}.json")); m = J["meta"]; L = J["lines"][l - 1]
        im = Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
        row = [r.split("\t") for r in (wd / "tables" / f"p{pg:03d}.tsv").read_text().splitlines() if r.split("\t")[0] == str(l)][0]
        toks = [t for t in row[3].split() if t != "/"]
        card = render(toks, False); c0 = 7
        for k in range(f - 1):
            c0 = card.index(",", c0) + 2 if k < f - 1 else c0
        c0 -= 0
        x0 = int(m["col1_x"] + (c0 - 2) * m["pitch"]); x1 = int(m["col1_x"] + (c0 + 13) * m["pitch"])
        crop = im.crop((x0, L["y0"] - 4, x1, L["y1"] + 4)); crop = crop.resize((crop.width * 2, crop.height * 2))
        r = Image.new("L", (crop.width + 620, crop.height + 6), 255); r.paste(crop, (0, 3))
        ImageDraw.Draw(r).text((crop.width + 10, 8), f"{len(strips)+1}. p{pg} L{l} f{f}  {read}  {note}", fill=0)
        strips.append(r)
    W = max(s.width for s in strips); H = sum(s.height for s in strips)
    sh = Image.new("L", (W, H), 255); y = 0
    for s in strips:
        sh.paste(s, (0, y)); y += s.height
    sh.save(out_png)


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "suggest":
    wd = Path(sys.argv[1]); A = arrays(wd); items = []
    for k, (p, l, f, t) in enumerate(A.get("DCON", [])):
        try:
            v = float(t)
        except ValueError:
            continue
        if v == 0 or round_t(v):
            continue
        s = suggest(v, t)
        print(f"{k+1:4d} p{p} L{l} f{f} {t:>13s}  " + "  ".join(f"{c}({T},{d})" for d, c, T in s[:3]))
        items.append((p, l, f, t, "  ".join(f"{c} ({T})" for d, c, T in s[:2])))
    a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    sheet(wd, str(wd / "review-sheets" / "dcon.png"), items[a:a + 22])


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "blocks":
    sys.path.insert(0, str(Path(__file__).parent))
    import tables
    wd = Path(sys.argv[1]); D = tables.data_lines(wd, list(range(174, 183))); cur = None
    rows = {}
    for pg in range(174, 183):
        for r in (wd / "tables" / f"p{pg:03d}.tsv").read_text().splitlines():
            x = r.split("\t"); rows[(pg, int(x[0]))] = len([t for t in x[3].split() if t != "/"])
    for pg in range(174, 183):
        for i, arr, last in D[pg]:
            if cur is None:
                cur = [arr, pg, i, 0, 0, []]
            cur[3] += 1; cur[4] += rows[(pg, i)]
            if rows[(pg, i)] != 5:
                cur[5].append(f"p{pg}L{i}:{rows[(pg, i)]}")
            if last:
                print(*cur[:5], " ".join(cur[5])); cur = None


SYM = ("n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr "
       "Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf").split()


def nuclide(v):
    """packed NUCLID value -> (head, A, Z, M, low): octal AAA ZZZ M LLLLL."""
    head = v < 0; v = abs(v)
    return head, v // 8 ** 9, (v // 8 ** 6) % 512, (v // 8 ** 5) % 8, v % 8 ** 5


def nuclides(wd):
    return arrays(wd)["NUCLID"]


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "nuclid":
    wd = Path(sys.argv[1]); seq = nuclides(wd); dcon = arrays(wd); dc = []
    for k in ("DCON", "OCON"):
        pass
    D = dcon["DCON"]
    from collections import Counter
    lows = Counter()
    dec = []
    for p, l, f, t in seq:
        try:
            dec.append(nuclide(int(t)))
        except ValueError:
            dec.append(None)
    for d in dec:
        if d:
            lows[d[4]] += 1
    prev = None; bad = 0
    for n, ((p, l, f, t), d) in enumerate(zip(seq, dec)):
        why = []
        if d is None:
            why.append("unreadable")
        else:
            head, a, z, m, low = d
            if not (66 <= a <= 172) or not (20 <= z <= 72) or m > 1:
                why.append("range")
            if lows[low] < 3:
                why.append(f"low {low:05o} rare")
            if prev:
                ph, pa, pz, pm, _ = prev
                if a < pa or (a == pa and (z < pz or (z == pz and m >= pm))):
                    why.append("order")
                if a == pa and head:
                    why.append("head mid-chain")
                if a != pa and not head:
                    why.append("chain without head")
            prev = d
        dv = D[n][3] if n < len(D) else "?"
        try:
            rt = round_t(float(dv)) if float(dv) else "zero"
        except ValueError:
            rt = "?"
        nm = f"{SYM[d[2]] if d and d[2] < len(SYM) else '?'}-{d[1]}{'m' if d and d[3] else ''}" if d else "?"
        if why:
            bad += 1
        if why or "-v" in sys.argv:
            print(f"{n+1:4d} p{p} L{l} f{f} {t:>13s} {(('-' if d[0] else ' ') + f'{d[1]:03o} {d[2]:03o} {d[3]} {d[4]:05o}') if d else '':18s} {nm:8s} DCON {dv} {rt or '*'}  {' '.join(why)}")
    print("values", len(seq), "flagged", bad, "low codes", {f"{k:05o}": v for k, v in lows.most_common(12)})


COMMON_LOW = {0o10004, 0o00004, 0o12002, 0o20004, 0o00000, 0o10002, 0o30004, 0o40004}


def nvalid(d, prev, nxt):
    if d is None:
        return False
    head, a, z, m, low = d
    if not (66 <= a <= 172 and 20 <= z <= 72 and m <= 1 and low in COMMON_LOW):
        return False
    for o, sgn in ((prev, 1), (nxt, -1)):
        if not o:
            continue
        oh, oa, oz, om, _ = o
        if abs(a - oa) > 1:
            return False
        if sgn == 1 and (a < oa or (a == oa and (z < oz or (z == oz and m >= om)))):
            return False
        if sgn == -1 and (a > oa or (a == oa and (z > oz or (z == oz and m <= om)))):
            return False
    if prev and a != prev[1] and not head:
        return False
    return True


def ncands(t, prev, nxt):
    """structurally valid values within two digit changes of the reading ('-' and '?' inside are wildcards)."""
    import itertools
    neg = t.startswith("-"); b = t.lstrip("-")
    if len(b) != 11:
        b = b.rjust(11, "?")
    wild = [i for i, c in enumerate(b) if not c.isdigit()]
    if len(wild) > 3:
        return []
    out = []
    pos = [i for i in range(11) if i not in wild]
    for k in range(0, 3 - len(wild) if len(wild) < 3 else 1):
        for ch in itertools.combinations(pos, k):
            idx = wild + list(ch)
            for digs in itertools.product("0123456789", repeat=len(idx)):
                s = list(b)
                if any(s[i] == d for i, d in zip(ch, digs[len(wild):])):
                    continue
                for i, d in zip(idx, digs):
                    s[i] = d
                for sg in ((True, False) if wild or k else (neg,)):
                    v = int("".join(s)) * (-1 if sg else 1)
                    if nvalid(nuclide(v), prev, nxt):
                        out.append((len(idx), str(v)))
        if out:
            break
    return sorted(set(out))


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "nsuggest":
    wd = Path(sys.argv[1]); seq = nuclides(wd)[:692]
    dec = []
    for p, l, f, t in seq:
        try:
            dec.append(nuclide(int(t)))
        except ValueError:
            dec.append(None)
    ok = [False] * len(seq)
    for n in range(len(seq)):
        ok[n] = nvalid(dec[n], dec[n - 1] if n and dec[n - 1] else None, None)
    items = []
    for n, (p, l, f, t) in enumerate(seq):
        prev = next((dec[j] for j in range(n - 1, -1, -1) if ok[j]), None)
        nxt = next((dec[j] for j in range(n + 1, len(seq)) if ok[j]), None)
        if dec[n] and nvalid(dec[n], prev, nxt):
            continue
        c = ncands(t, prev, nxt)
        def nm(v):
            h, a, z, m, low = nuclide(int(v)); return f"{SYM[z]}-{a}{'m' if m else ''}/{low:05o}"
        print(f"{n+1:4d} p{p} L{l} f{f} {t:>13s}  " + "  ".join(f"{v}({nm(v)})" for d, v in c[:4]) + ("" if c else "  NONE"))
        items.append((p, l, f, t, "  ".join(f"{v} {nm(v)}" for d, v in c[:2]) or "none"))
    a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    sheet(wd, str(wd / "review-sheets" / "nuclid.png"), items[a:a + 22])


if __name__ == "__main__" and len(sys.argv) > 3 and sys.argv[2] == "freeze":
    # write every value of the named arrays into tablefix.tsv as a hand reading, so a later re-read cannot move it
    wd = Path(sys.argv[1]); A = arrays(wd); n = 0
    with open(wd / "tablefix.tsv", "a") as f:
        f.write(f"# frozen after review: {' '.join(sys.argv[3:])}\n")
        for name in sys.argv[3:]:
            for p, l, k, t in A[name]:
                f.write(f"p{p}\t{l}\t{k}\t{t}\n"); n += 1
    print("frozen", n)


def ncands2(t, prev, nxt, stable, lows, adj=(True, True)):
    """model-based candidates: A, Z, M near the neighbours, a low code seen at least twice (00004 iff the DCON
    of the same index is zero), the printed sign; ranked by decimal digit distance to the reading."""
    neg = t.startswith("-"); b = t.lstrip("-")
    out = []
    refs = [o for o in (prev, nxt) if o]
    if not refs:
        return out
    As = {o[1] for o in refs} | {refs[0][1] + 1}
    zs = range(min(o[2] for o in refs) - 14, max(o[2] for o in refs) + 3)
    for a in As:
        for z in zs:
            for m in (0, 1, 2):
                for low in lows:
                    if (low == 0o00004) != stable:
                        continue
                    for head in ((True, False) if "-" in b or "?" in b else (neg,)):
                        d = (head, a, z, m, low)
                        if not nvalid2(d, prev, nxt, adj):
                            continue
                        v = a * 8 ** 9 + z * 8 ** 6 + m * 8 ** 5 + low
                        s = str(v)
                        if len(s) != len(b):
                            continue
                        dist = sum(1 for x, y in zip(s, b) if x != y and y.isdigit())
                        if dist <= 3:
                            out.append((dist, ("-" if head else "") + s))
    return sorted(set(out))


def nvalid2(d, prev, nxt, adj=(True, True)):
    head, a, z, m, low = d
    for o, sgn in ((prev, 1), (nxt, -1)):
        if not o:
            continue
        oh, oa, oz, om, _ = o
        if abs(a - oa) > 1:
            return False
        if sgn == 1 and (a < oa or (a == oa and (z < oz or (z == oz and m >= om)))):
            return False
        if sgn == -1 and (a > oa or (a == oa and (z > oz or (z == oz and m <= om)))):
            return False
    if adj[0] and prev and a != prev[1] and not head:
        return False
    if adj[0] and prev and a == prev[1] and z > prev[2] + 1 and not head:     # a chain steps one Z at a time
        return False
    if adj[1] and nxt and nxt[1] != a and not nxt[0]:
        return False
    return True


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "nsuggest2":
    from collections import Counter
    wd = Path(sys.argv[1]); A = arrays(wd); seq = A["NUCLID"][:692]; D = A["DCON"]
    dec = []
    for p, l, f, t in seq:
        try:
            dec.append(nuclide(int(t)))
        except ValueError:
            dec.append(None)
    cnt = Counter(d[4] for d in dec if d)
    lows = [k for k, v in cnt.items() if v >= 2]
    stable = [float(x[3]) == 0 for x in D[:692]]
    ok = []
    for n, d in enumerate(dec):
        good = d is not None and 66 <= d[1] <= 172 and 20 <= d[2] <= 72 and d[3] <= 2 and ((d[4] == 0o00004) == stable[n])
        ok.append(good)
    def near(n):
        pj = next((j for j in range(n - 1, -1, -1) if ok[j]), None)
        nj = next((j for j in range(n + 1, len(seq)) if ok[j]), None)
        return (dec[pj] if pj is not None else None, dec[nj] if nj is not None else None,
                (pj == n - 1, nj == n + 1))
    for n in range(len(seq)):                       # order against the nearest good neighbours
        if ok[n]:
            pv, nx, adj = near(n)
            ok[n] = nvalid2(dec[n], pv, nx, adj)
    items = []
    for n, (p, l, f, t) in enumerate(seq):
        if ok[n]:
            continue
        pv, nx, adj = near(n)
        c = ncands2(t, pv, nx, stable[n], lows, adj)
        def nm(v):
            h, a, z, m, low = nuclide(int(v)); return f"{SYM[z]}-{a}{'m' * m}/{low:05o}"
        print(f"{n+1:4d} p{p} L{l} f{f} {t:>13s}  " + "  ".join(f"{v}({nm(v)},{d})" for d, v in c[:3]) + ("" if c else "  NONE") + f"   [DCON {D[n][3]}]")
        items.append((p, l, f, t, "  ".join(f"{v} {nm(v)}" for d, v in c[:2]) or "none"))
    a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    sheet(wd, str(wd / "review-sheets" / "nuclid.png"), items[a:a + 22])
