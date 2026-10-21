"""Hand-check sheet for one disputed digit in a PAM DATA-table field (pp. 174-182): the whole field, the disputed glyph
boxed, and a 0-9 sample grid taken from other fields of the same page at the same scale (nearest lines first).

A disputed sign (+/-) gets + and - samples instead of digits.

usage: python3 -I digitsheet.py <workdir> <page> <line> <field 1-5> <char> <out.png> [--note "text"] [--extra img.png "caption"] [--shift cols]
<char>[,<char>...] = position(s) in the printed value without its sign: 0 = digit before the point, 2 = first digit after it, ...
Samples come from tables/p<page>.tsv (the current reading): leading digits, the first two digits after the point and the
exponent digit; trailing zeros are skipped (they are often broken on this scan). --extra appends e.g. a 1968 card crop.
"""
import glob
import json
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

a = sys.argv
wd, page, line, field, out = Path(a[1]), int(a[2]), int(a[3]), int(a[4]), a[6]
chars = [int(c) for c in a[5].split(",")]; char = chars[0]
note = a[a.index("--note") + 1] if "--note" in a else ""
extra = (a[a.index("--extra") + 1], a[a.index("--extra") + 2]) if "--extra" in a else None
shift = float(a[a.index("--shift") + 1]) if "--shift" in a else 0.0   # columns; for lines whose glyphs sit off the fitted grid
SC, ROWS = 4, 4

J = json.load(open(wd / "lines" / f"p{page:03d}.json")); m = J["meta"]; L = J["lines"]
im = Image.open(sorted(glob.glob(str(wd / "native" / f"n-{page:03d}-*.png")))[0]).convert("L")


def crop(ln, c0, c1, sh=0.0):
    l = L[ln - 1]; c0 += sh; c1 += sh
    x0 = int(m["col1_x"] + (c0 - 1) * m["pitch"] - m["pitch"] / 2); x1 = int(m["col1_x"] + (c1 - 1) * m["pitch"] + m["pitch"] / 2)
    c = im.crop((x0, l["y0"] - 6, x1, l["y1"] + 6))
    return c.resize((c.width * SC, c.height * SC), Image.LANCZOS)


sign_col = lambda k: 7 + 13 * (k - 1)          # field k: sign, digit, point, mantissa, E, sign, exponent, comma
reading, cand = None, {c: [] for c in "0123456789+-"}
for row in open(wd / "tables" / f"p{page:03d}.tsv"):
    f = row.rstrip("\n").split("\t")
    if len(f) < 4 or not f[0].isdigit():
        continue
    ln = int(f[0])
    vals = [v for v in f[3].split() if re.match(r"-?\d", v)]
    for k, v in enumerate(vals, 1):
        if (ln, k) == (line, field):
            reading = v; continue
        mm = re.match(r"(-?)(\d)\.(\d+)E([-+])(\d+)$", v)
        if not mm:
            continue
        base = sign_col(k)
        man, ecol = mm.group(3), base + 3 + len(mm.group(3))          # ecol = column of the 'E'
        digs = [(mm.group(2), base + 1)] + [(man[i], base + 3 + i) for i in range(2)]
        digs.append((mm.group(5)[-1], ecol + 1 + len(mm.group(5))))
        for i, (d, col) in enumerate(digs):
            if i in (1, 2) and set(man[i - 1:]) == {"0"}:
                continue                         # a trailing zero
            cand[d].append((abs(ln - line) + (3 if i == 3 else 0), ln, col))
        cand[mm.group(4)].append((abs(ln - line), ln, ecol + 1))        # exponent sign
        if mm.group(1):
            cand["-"].append((abs(ln - line) + 1, ln, base))            # leading minus
body = (reading or "").lstrip("-")
keys = "+-" if char < len(body) and body[char] in "+-" else "0123456789"
pick = {d: sorted(cand[d])[:ROWS] for d in keys}

font = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s)
F, G = font(30), font(24)
cell = crop(line, sign_col(field), sign_col(field) + 12, shift)
tgts = [crop(line, sign_col(field) + 1 + c, sign_col(field) + 1 + c, shift) for c in chars]; tgt = tgts[0]
cw, gap = tgt.width, 18
xtra = Image.open(extra[0]).convert("L") if extra else None
W = max(cell.width, len(keys) * (cw + gap), xtra.width if xtra else 0) + 80
o = Image.new("L", (W, 4000), 255); d = ImageDraw.Draw(o); y = 20
d.text((40, y), f"p{page} line {line}, field {field}: our reading {reading}" + (f"   {note}" if note else ""), font=F, fill=0); y += 50
o.paste(cell, (40, y)); y += cell.height + 15
for c in chars:                                           # mark the disputed characters on the field crop
    x = 40 + (1 + c) * m["pitch"] * SC
    d.rectangle((x, y - cell.height - 13, x + m["pitch"] * SC, y - 13), outline=0, width=3)
d.text((40, y), f"the disputed character(s) (position {', '.join(map(str, chars))} of the value), same scale as the samples:", font=G, fill=80); y += 40
for k, t in enumerate(tgts):
    x = 40 + k * (cw + gap); o.paste(t, (x, y)); d.rectangle((x - 2, y - 2, x + t.width + 2, y + t.height + 2), outline=0, width=2)
y += tgt.height + 30
what = "signs" if keys == "+-" else "digits"
d.text((40, y), f"the same {what} elsewhere on p{page} (nearest lines first; zeros are often broken on this scan):", font=G, fill=80); y += 40
for k, key in enumerate(keys):
    d.text((40 + k * (cw + gap) + cw // 2 - 10, y), key, font=F, fill=0)
y += 45
for r in range(ROWS):
    h = 0
    for k, key in enumerate(keys):
        if r < len(pick[key]):
            _, ln, col = pick[key][r]; g = crop(ln, col, col); o.paste(g, (40 + k * (cw + gap), y)); h = max(h, g.height)
    y += h + 12
if xtra:
    y += 20; d.text((40, y), extra[1], font=G, fill=80); y += 35; o.paste(xtra, (40, y)); y += xtra.height + 20
o.crop((0, 0, W, y)).save(out)
print(out, "reading", reading, {k: len(v) for k, v in pick.items()})
