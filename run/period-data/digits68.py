"""0-9 sample table from the 1968 ERM cards (Tompkins DASA-1800-V pp. 254-257), for hand-check sheets.

usage: python3 -I digits68.py <AD0832239.pdf> <dtm_port.f> <out.png> [scale]
Only ERM value words whose PDF text-layer reading equals one of our 1979 ERMs (0.xyzE-0n = x.yzE-(n+1)) are used, so
the sampled glyphs are known; each digit's box is its share of the fixed-pitch word box. Needs pdftotext and pdftoppm.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

pdf, port, out = sys.argv[1], sys.argv[2], sys.argv[3]
SC = int(sys.argv[4]) if len(sys.argv) > 4 else 3
ROWS, DPI, PAGES = 4, 300, range(254, 258)

src = open(port).read()
erm = []
for m in re.finditer(r"DATA \(ERM\s*\(I\),I=\s*\d+,\s*\d+\s*\)/(.*?)/", src, re.S):
    erm += [x.strip() for x in re.sub(r"\n     \$", "", m.group(1)).split(",") if x.strip()]
ours = {f"{abs(float(v)):.2E}" for v in erm if float(v)}            # e.g. 1.17E-05

tmp = Path(tempfile.mkdtemp())
subprocess.run(["pdftotext", "-bbox", "-f", str(PAGES[0]), "-l", str(PAGES[-1]), pdf, str(tmp / "bb.html")], check=True)
pages = open(tmp / "bb.html").read().split("<page ")[1:]
cand = {str(d): [] for d in range(10)}
img = {}
for pn, pg in zip(PAGES, pages):
    for x0, y0, x1, y1, w in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<', pg):
        mm = re.fullmatch(r"([0-2])\.(\d)(\d)(\d)E-0(\d)", w)
        if not mm or f"{mm.group(2)}.{mm.group(3)}{mm.group(4)}E-{int(mm.group(5)) + 1:02d}" not in ours:
            continue
        x0, y0, x1, y1 = map(float, (x0, y0, x1, y1)); cw = (x1 - x0) / len(w)
        for i in (2, 3, 4, 8):                                   # the three digits and the exponent's last digit
            cand[w[i]].append((pn, x0 + i * cw, y0, x0 + (i + 1) * cw, y1))
for pn in PAGES:
    subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-f", str(pn), "-l", str(pn), "-png", pdf, str(tmp / f"p{pn}")], check=True)
    img[pn] = Image.open(sorted(tmp.glob(f"p{pn}*.png"))[0]).convert("L")
f = DPI / 72


def crop(pn, x0, y0, x1, y1):
    """the glyph's own columns: from the box centre out to the first all-white column on each side"""
    c = img[pn].crop((int((x0 - 0.8) * f), int((y0 - 1.0) * f), int((x1 + 0.8) * f), int((y1 + 1.0) * f)))
    w, h = c.size; px = c.load(); ink = [sum(px[x, y] < 128 for y in range(h)) for x in range(w)]
    l = r = w // 2
    while l > 0 and ink[l - 1]: l -= 1
    while r < w - 1 and ink[r + 1]: r += 1
    c = c.crop((max(0, l - 3), 0, min(w, r + 4), h))
    return c.resize((c.width * SC, c.height * SC), Image.LANCZOS)


pick = {d: c[::max(1, len(c) // ROWS)][:ROWS] for d, c in cand.items()}   # spread over the pages
cells = {d: [crop(*t) for t in v] for d, v in pick.items()}
cw = max(i.width for v in cells.values() for i in v); ch = max(i.height for v in cells.values() for i in v); gap = 30
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
o = Image.new("L", (10 * (cw + gap) + 20, 45 + ROWS * (ch + 12)), 255); d = ImageDraw.Draw(o)
for k in range(10):
    d.text((k * (cw + gap) + cw // 2 - 10, 0), str(k), font=F, fill=0)
    for r, c in enumerate(cells[str(k)]):
        o.paste(c, (k * (cw + gap) + (cw - c.width) // 2, 45 + r * (ch + 12)))
o.save(out)
print(out, {k: len(v) for k, v in cells.items()})
