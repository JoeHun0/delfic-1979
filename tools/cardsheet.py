"""Hand-check sheet for disputed characters on a code card: the card's statement field, the disputed glyphs boxed,
and a 0-9 sample grid from other cards on the same page whose reading all OCR models agreed on (AGREE) or that were
read by hand (HAND), nearest lines first, at the same scale.

usage: python3 -I cardsheet.py <workdir> <page> <line> <col>[,<col>...] <out.png> [--note "text"] [--from C0 --to C1] [--chars T1]
<col> = card column (1-80) of each disputed character; --from/--to = columns of the crop (default 7-72);
--chars = the sample characters (default the digits 0-9; e.g. T1 or B3 for a disputed letter).
"""
import glob
import json
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

a = sys.argv
wd, page, line, out = Path(a[1]), int(a[2]), int(a[3]), a[5]
cols = [int(c) for c in a[4].split(",")]
note = a[a.index("--note") + 1] if "--note" in a else ""
c0 = int(a[a.index("--from") + 1]) if "--from" in a else 7
c1 = int(a[a.index("--to") + 1]) if "--to" in a else 72
CH = a[a.index("--chars") + 1] if "--chars" in a else "0123456789"
SC, ROWS = 4, 4

PG = {}


def pg(p):
    if p not in PG:
        J = json.load(open(wd / "lines" / f"p{p:03d}.json"))
        PG[p] = (J["meta"], J["lines"], Image.open(sorted(glob.glob(str(wd / "native" / f"n-{p:03d}-*.png")))[0]).convert("L"))
    return PG[p]


def raw(p, ln, x0c, x1c):
    m, L, im = pg(p); l = L[ln - 1]
    x0 = int(m["col1_x"] + (x0c - 1) * m["pitch"] - m["pitch"] / 2); x1 = int(m["col1_x"] + (x1c - 1) * m["pitch"] + m["pitch"] / 2)
    return im.crop((x0, l["y0"] - 6, x1, l["y1"] + 6))


def crop(ln, x0c, x1c, p=None):
    c = raw(p or page, ln, x0c, x1c)
    return c.resize((c.width * SC, c.height * SC), Image.LANCZOS)


def clean(p, ln, col):
    """the glyph sits inside its cell: no ink in the outer 12% on either side, and some ink in the middle"""
    c = raw(p, ln, col, col); w, h = c.size; px = c.load(); e = max(1, int(w * 0.12))
    ink = lambda xs: sum(px[x, y] < 128 for x in xs for y in range(h))
    return ink(range(e)) == 0 and ink(range(w - e, w)) == 0 and ink(range(w // 3, 2 * w // 3)) > 5
m = pg(page)[0]


cand = {ch: [] for ch in CH}
reading = ""
for p in (page, page - 1, page + 1, page - 2, page + 2):  # neighbouring pages only fill digits this page lacks
    fn = wd / "final" / f"p{p:03d}.tsv"
    if not fn.exists() or not glob.glob(str(wd / "native" / f"n-{p:03d}-*.png")):
        continue
    for row in open(fn):
        f = row.rstrip("\n").split("\t")
        if len(f) < 5 or not f[0].isdigit():
            continue
        ln, status, text = int(f[0]), f[3], f[4]
        if p == page and ln == line:
            reading = text; continue
        if status not in ("AGREE", "HAND"):
            continue
        for i, ch in enumerate(text[:72]):
            if ch in cand and i >= 6:                  # statement field only (labels are often damaged)
                cand[ch].append((abs(ln - line) + 1000 * abs(p - page), p, ln, i + 1))
pick = {}
for d, c in cand.items():
    pick[d] = []
    for t in sorted(c):
        if clean(t[1], t[2], t[3]):
            pick[d].append(t)
        if len(pick[d]) == ROWS:
            break

font = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s)
F, G = font(30), font(24)
card = crop(line, c0, c1)
tg = [crop(line, c, c) for c in cols]
cw, gap = tg[0].width, 18
title = f"p{page} line {line}: transcription '{reading[c0 - 1:c1].rstrip()}'" + (f"   {note}" if note else "")
W = max(card.width, len(CH) * (cw + gap), int(F.getlength(title))) + 80
o = Image.new("L", (W, 4000), 255); d = ImageDraw.Draw(o); y = 20
d.text((40, y), title, font=F, fill=0); y += 50
o.paste(card, (40, y))
for c in cols:                                            # mark the disputed columns on the card crop
    x = 40 + (c - c0) * m["pitch"] * SC
    d.rectangle((x, y - 2, x + m["pitch"] * SC, y + card.height + 2), outline=0, width=3)
y += card.height + 15
d.text((40, y), "the disputed characters (columns " + ", ".join(map(str, cols)) + "), same scale as the samples below:", font=G, fill=80); y += 40
for k, t in enumerate(tg):
    x = 40 + k * (cw + gap); o.paste(t, (x, y)); d.rectangle((x - 2, y - 2, x + t.width + 2, y + t.height + 2), outline=0, width=2)
y += max(t.height for t in tg) + 30
d.text((40, y), f"{'digits' if CH == '0123456789' else 'samples'} elsewhere on p{page} (or the next pages if too few; cards all OCR models agreed on):", font=G, fill=80); y += 40
for k, ch in enumerate(CH):
    d.text((40 + k * (cw + gap) + cw // 2 - 10, y), ch, font=F, fill=0)
y += 45
for r in range(ROWS):
    h = 0
    for k, ch in enumerate(CH):
        if r < len(pick[ch]):
            _, p, ln, col = pick[ch][r]; g = crop(ln, col, col, p); o.paste(g, (40 + k * (cw + gap), y)); h = max(h, g.height)
    y += h + 12
o.crop((0, 0, W, y)).save(out)
print(out, {k: [f"p{t[1]}" for t in v] for k, v in pick.items()})
