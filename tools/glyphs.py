"""Glyph templates from verified cards, and a nearest-template reader for numeric data cards.

usage:
  python3 -I glyphs.py <workdir> build                 # templates from final/p055-p107 AGREE/HAND cards
  python3 -I glyphs.py <workdir> read <page> [<page>]  # read numeric cards (cols 1-72) -> pam/p<page>.tsv

Each cell (one card column) is cropped at the line's band, binarised, cropped to its ink box and resized
to 16x24; templates are per-character means. Reading assigns each inked cell the character with the highest
normalised correlation and reports the margin to the runner-up.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

CHARS = "0123456789.E+-"
SZ = (16, 24)


def cell_img(a, L, meta, col):
    P, x1 = meta["pitch"], meta["col1_x"]
    xa = int(round(x1 + (col - 1) * P - P / 2)); xb = int(round(x1 + (col - 1) * P + P / 2))
    c = a[L["y0"]:L["y1"], max(xa, 0):xb]
    ys, xs = np.nonzero(c)
    if len(xs) < 5:
        return None, 0
    box = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h = ys.max() - ys.min() + 1
    top = ys.min() / max(c.shape[0], 1)
    im = Image.fromarray((box * 255).astype(np.uint8)).resize(SZ, Image.BILINEAR)
    v = np.asarray(im, float) / 255.
    return v, (h, top)


def load(wd, pg):
    J = json.load(open(wd / "lines" / f"p{pg:03d}.json"))
    a = np.asarray(Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")) < 128
    return J, a


def build(wd):
    acc = {c: [] for c in CHARS}; hs = {c: [] for c in CHARS}
    for pg in range(55, 108):
        J, a = load(wd, pg)
        for r in (wd / "final" / f"p{pg:03d}.tsv").read_text().splitlines():
            x = r.split("\t")
            if x[3] not in ("AGREE", "HAND"):
                continue
            L = J["lines"][int(x[0]) - 1]; card = x[4].ljust(72)
            if card[0] in "C*":
                continue
            for col in L["cols"]:
                if col > 72:
                    continue
                ch = card[col - 1]
                if ch in acc and len(acc[ch]) < 400:
                    v, hh = cell_img(a, L, J["meta"], col)
                    if v is not None:
                        acc[ch].append(v); hs[ch].append(hh)
    T = {c: np.mean(v, 0) for c, v in acc.items() if v}
    H = {c: (float(np.median([h[0] for h in hs[c]])), float(np.median([h[1] for h in hs[c]]))) for c in T}
    np.savez(wd / "glyphs.npz", chars="".join(T), T=np.stack([T[c] for c in T]),
             H=np.array([H[c] for c in T]))
    print({c: len(v) for c, v in acc.items()})


def read(wd, pages):
    """Constrained decoding of 5E14.6 cards: per 14-column field, either a zero ('0' at pos 3, '.' at 4)
    or '.dddddd' at pos 4-10, 'E' at 11, sign at 12, two digits at 13-14. Writes card text, the parsed
    values, and the weakest digit margin per line."""
    z = np.load(wd / "glyphs.npz"); chars = str(z["chars"]); T = z["T"]; H = z["H"]
    Tn = [(t - t.mean()) / (t.std() + 1e-9) for t in T]
    knn = knn_read(wd, pages) if "--knn" in sys.argv else None
    if knn:
        chars = CHARS
    idx = {c: k for k, c in enumerate(chars)}
    DIG = [idx[c] for c in "0123456789"]
    (wd / "pam").mkdir(exist_ok=True)
    for pg in pages:
        J, a = load(wd, pg); out = []
        for i, L in enumerate(J["lines"], 1):
            S = {}
            for col in L["cols"]:
                if col > 70:
                    continue
                v, hh = cell_img(a, L, J["meta"], col)
                if v is None:
                    continue
                if knn:
                    S[col] = knn(v); continue
                vn = (v - v.mean()) / (v.std() + 1e-9)
                sc = np.array([float((vn * t).mean()) for t in Tn])
                h = hh[0]; sc = sc * np.array([1.0 - min(abs(h - hm) / max(hm, 1), 1) * 0.6 for hm, _ in H])
                S[col] = sc
            card = [" "] * 70; vals = []; margins = []; bad = []
            def best(col, allowed):
                if col not in S:
                    return None, 0.0
                sc = S[col]; o = sorted(allowed, key=lambda k: -sc[k])
                return chars[o[0]], (sc[o[0]] - sc[o[1]]) if len(o) > 1 else 1.0
            for f in range(5):
                c0 = f * 14
                used = [c - c0 for c in S if c0 < c <= c0 + 14]
                if not used:
                    continue
                if any(p >= 5 for p in used):          # E format
                    s = ""
                    pos = {4: [idx["."]], 11: [idx["E"]], 12: [idx["+"], idx["-"]], 13: [idx["0"]]}
                    for p_ in range(4, 15):
                        ch, m = best(c0 + p_, pos.get(p_, DIG))
                        if ch is None:
                            bad.append(c0 + p_); ch = "?"
                        elif p_ not in (4, 11):
                            margins.append(m)
                        card[c0 + p_ - 1] = ch; s += ch
                    try:
                        vals.append(float("0" + s))
                    except ValueError:
                        vals.append(None)
                    extra = [p_ for p_ in used if p_ < 4]
                    if extra:
                        bad += [c0 + p_ for p_ in extra]
                else:                                    # zero
                    card[c0 + 2] = "0"; card[c0 + 3] = "."; vals.append(0.0)
                    if sorted(used) != [3, 4]:
                        bad += [c0 + p_ for p_ in used if p_ not in (3, 4)]
            out.append(f"{i}\t{L['y0']}\t{min(margins) if margins else 1:.3f}\t{','.join(map(str,bad))}\t{''.join(card).rstrip()}\t{' '.join('' if v is None else repr(v) for v in vals)}")
        (wd / "pam" / f"p{pg:03d}.tsv").write_text("\n".join(out) + "\n")
        print(f"p{pg}: {len(out)} lines")


def build_pam(wd, pages):
    """Templates from the data pages themselves: fields where the two OCR models agree on a full 5E14.6
    reading give the characters at known card columns."""
    import re
    num = re.compile(r"(\.\d{6}E[+-]\d{2}|0\.)")
    acc = {c: [] for c in CHARS}; hs = {c: [] for c in CHARS}
    for pg in pages:
        J, a = load(wd, pg)
        reads = {}
        for m in ("glm", "lighton"):
            f = wd / f"ocr-{m}" / f"p{pg:03d}.tsv"
            reads[m] = {int(r.split("\t")[0]): r.split("\t")[4].split(" || ")[0] for r in f.read_text().splitlines()}
        for i, L in enumerate(J["lines"], 1):
            vs = []
            for m in reads:
                tt = reads[m].get(i, "").replace(" ", "")
                vs.append(num.findall(tt))
            if len(vs) != 2 or len(vs[0]) != 5 or vs[0] != vs[1]:
                continue
            for f_, s in enumerate(vs[0]):
                c0 = f_ * 14
                cells = {c0 + 3: "0", c0 + 4: "."} if s == "0." else {c0 + 4 + k: ch for k, ch in enumerate(s)}
                for col, ch in cells.items():
                    if col in L["cols"] and ch in acc:
                        v, hh = cell_img(a, L, J["meta"], col)
                        if v is not None:
                            acc[ch].append(v); hs[ch].append(hh)
    T = {c: np.mean(v, 0) for c, v in acc.items() if v}
    H = {c: (float(np.median([h[0] for h in hs[c]])), float(np.median([h[1] for h in hs[c]]))) for c in T}
    np.savez(wd / "glyphs.npz", chars="".join(T), T=np.stack([T[c] for c in T]), H=np.array([H[c] for c in T]))
    print({c: len(v) for c, v in acc.items()})


def verified_cards(wd):
    """(page, line) -> card text for hand-verified PAM lines: pamfix.tsv corrections + pamok.tsv accepted readings."""
    out = {}
    f = wd / "pamok.tsv"
    if f.exists():
        for r in f.read_text().splitlines():
            if not r.strip():
                continue
            pg, spec = r.split("\t"); pg = int(pg.lstrip("p"))
            rows = {int(l.split("\t")[0]): l.split("\t")[4] for l in (wd / "pam" / f"p{pg:03d}.tsv").read_text().splitlines()}
            for part in spec.split(","):
                a, _, b = part.partition("-"); a = int(a); b = int(b or a)
                for i in range(a, b + 1):
                    out[(pg, i)] = rows[i]
    f = wd / "pamfix.tsv"
    if f.exists():
        for r in f.read_text().splitlines():
            x = r.split("\t")
            if len(x) >= 3 and not (len(x) > 3 and x[3] == "?"):
                out[(int(x[0].lstrip("p")), int(x[1]))] = x[2]
    return out


def knn_read(wd, pages, k=3):
    """Classify every cell by its k nearest verified samples (correlation), within the 5E14.6 constraints."""
    V = verified_cards(wd); X = []; Y = []
    cache = {}
    for (pg, i), card in V.items():
        if pg not in cache:
            cache[pg] = load(wd, pg)
        J, a = cache[pg]; L = J["lines"][i - 1]
        for col in L["cols"]:
            if col > 70 or col > len(card) or card[col - 1] == " ":
                continue
            v, hh = cell_img(a, L, J["meta"], col)
            if v is not None:
                vn = (v - v.mean()) / (v.std() + 1e-9); X.append(vn.ravel()); Y.append(card[col - 1])
    X = np.array(X); Y = np.array(Y)
    chars = CHARS; idx = {c: n for n, c in enumerate(chars)}
    print("training cells:", len(Y), {c: int((Y == c).sum()) for c in chars})
    import types
    def scores(v):
        vn = ((v - v.mean()) / (v.std() + 1e-9)).ravel()
        s = X @ vn / len(vn)
        out = np.full(len(chars), -1.0)
        for c in chars:
            m = s[Y == c]
            if len(m):
                out[idx[c]] = np.sort(m)[-k:].mean()
        return out
    return scores


if __name__ == "__main__":
    wd = Path(sys.argv[1])
    if sys.argv[2] == "build":
        build(wd)
    elif sys.argv[2] == "buildpam":
        build_pam(wd, [int(p) for p in sys.argv[3:]])
    else:
        read(wd, [int(p) for p in sys.argv[3:] if p.isdigit()])
