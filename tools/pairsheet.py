"""One compact hand-check sheet for several DATA-table cells (pp. 174-182): per cell the field with the disputed
character boxed, and samples of just the two competing digits from the same page, at the same scale.

usage: python3 -I pairsheet.py <workdir> <out.png> <item> [<item> ...]
item = "page:line:field:char:ours:alt:title[:shift]", e.g. "176:20:1:3:9:8:Sb-129  ours 4.195670E-5, 1968/exact 4.185670E-5"
"""
import glob
import json
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

wd, out = Path(sys.argv[1]), sys.argv[2]
SC, N = 4, 6
sign_col = lambda k: 7 + 13 * (k - 1)
PG = {}


def pg(p):
    if p not in PG:
        J = json.load(open(wd / "lines" / f"p{p:03d}.json"))
        PG[p] = (J["meta"], J["lines"], Image.open(sorted(glob.glob(str(wd / "native" / f"n-{p:03d}-*.png")))[0]).convert("L"))
    return PG[p]


def crop(p, ln, c0, c1, sh=0.0):
    m, L, im = pg(p); l = L[ln - 1]; c0 += sh; c1 += sh
    x0 = int(m["col1_x"] + (c0 - 1) * m["pitch"] - m["pitch"] / 2); x1 = int(m["col1_x"] + (c1 - 1) * m["pitch"] + m["pitch"] / 2)
    c = im.crop((x0, l["y0"] - 6, x1, l["y1"] + 6))
    return c.resize((c.width * SC, c.height * SC), Image.LANCZOS)


def samples(p, digit, skip, line):
    """cells on page p whose reading is `digit` (leading digit or first three decimals of a field), nearest lines first"""
    found = []
    for row in open(wd / "tables" / f"p{p:03d}.tsv"):
        f = row.rstrip("\n").split("\t")
        if len(f) < 4 or not f[0].isdigit():
            continue
        ln = int(f[0])
        for k, v in enumerate([x for x in f[3].split() if re.match(r"-?\d", x)], 1):
            if (ln, k) == skip:
                continue
            mm = re.match(r"-?(\d)\.(\d+)E", v)
            if not mm:
                continue
            for i, ch in [(0, mm.group(1))] + [(2 + j, mm.group(2)[j]) for j in range(3)]:
                if ch == digit and not (ch == "0" and set(mm.group(2)[max(0, i - 2):]) == {"0"}):
                    found.append((abs(ln - line), ln, sign_col(k) + 1 + i))
    out = []
    for _, ln, c in sorted(found):
        if clean(p, ln, c):
            out.append(crop(p, ln, c, c))
        if len(out) == N:
            break
    return out


def clean(p, ln, col):
    """the glyph sits inside its grid cell: no ink in the outer 12% on either side, some ink in the middle"""
    m, L, im = pg(p); l = L[ln - 1]
    x0 = int(m["col1_x"] + (col - 1) * m["pitch"] - m["pitch"] / 2)
    c = im.crop((x0, l["y0"] - 6, int(x0 + m["pitch"]), l["y1"] + 6)); w, h = c.size; px = c.load(); e = max(1, int(w * 0.12))
    ink = lambda xs: sum(px[x, y] < 128 for x in xs for y in range(h))
    return ink(range(e)) == 0 and ink(range(w - e, w)) == 0 and ink(range(w // 3, 2 * w // 3)) > 5


F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
G = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
blocks = []
for n, it in enumerate(sys.argv[3:], 1):
    x = it.split(":")
    p, ln, k, ch, ours, alt, title = int(x[0]), int(x[1]), int(x[2]), int(x[3]), x[4], x[5], x[6]
    sh = float(x[7]) if len(x) > 7 else 0.0
    m = pg(p)[0]
    field = crop(p, ln, sign_col(k), sign_col(k) + 12, sh)
    sa, sb = samples(p, ours, (ln, k), ln), samples(p, alt, (ln, k), ln)
    cw = field.height // 2
    W = max(field.width, 80 + (len(sa) + len(sb) + 1) * (sa[0].width + 10)) + 60
    H = 45 + field.height + 30 + sa[0].height + 30
    b = Image.new("L", (W, H), 255); d = ImageDraw.Draw(b)
    d.text((10, 5), f"{n}. {title}   (p{p} line {ln} field {k})", font=F, fill=0)
    b.paste(field, (10, 45)); xb = 10 + (1 + ch) * m["pitch"] * SC
    d.rectangle((xb, 43, xb + m["pitch"] * SC, 47 + field.height), outline=0, width=3)
    y = 45 + field.height + 25; x0 = 10
    d.text((x0, y + 25), f"{ours}:", font=F, fill=0); x0 += 40
    for g in sa:
        b.paste(g, (x0, y)); x0 += g.width + 8
    x0 += 30; d.text((x0, y + 25), f"{alt}:", font=F, fill=0); x0 += 40
    for g in sb:
        b.paste(g, (x0, y)); x0 += g.width + 8
    blocks.append(b)
W = max(b.width for b in blocks); H = sum(b.height + 25 for b in blocks)
o = Image.new("L", (W, H), 255); y = 0
for b in blocks:
    o.paste(b, (0, y)); y += b.height + 25
    ImageDraw.Draw(o).line((0, y - 12, W, y - 12), fill=180, width=2)
o.save(out)
print(out, o.size)
