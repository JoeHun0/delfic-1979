"""Proof sheets for the PAM data cards: scan line + classifier reading rendered on the same column grid.
usage: python3 -I pamproof.py <workdir> <page> <first_line> <count> [out.png]
Prints line number and reading; corrections go to pamfix.tsv (page<TAB>line<TAB>full card text, cols 1-70)."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

wd = Path(sys.argv[1]); pg = int(sys.argv[2]); a = int(sys.argv[3]); n = int(sys.argv[4])
out = sys.argv[5] if len(sys.argv) > 5 else str(wd / "review-sheets" / "pamproof.png")
J = json.load(open(wd / "lines" / f"p{pg:03d}.json")); m = J["meta"]
im = Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
rows = {int(l.split("\t")[0]): l.split("\t") for l in (wd / "pam" / f"p{pg:03d}.tsv").read_text().splitlines()}
fix = {}
f = wd / "pamfix.tsv"
if f.exists():
    for r in f.read_text().splitlines():
        if r.strip() and not r.startswith("#"):
            p_, l_, t_ = r.split("\t", 2)
            if int(p_.lstrip("p")) == pg:
                fix[int(l_)] = t_
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 34)
strips = []
for i in range(a, min(a + n, len(J["lines"]) + 1)):
    L = J["lines"][i - 1]
    card = fix.get(i, rows.get(i, ["", "", "", "", ""])[4] if len(rows.get(i, [])) > 4 else "")
    x0 = int(m["col1_x"] - m["pitch"] / 2); x1 = int(m["col1_x"] + 70.5 * m["pitch"])
    img = im.crop((x0, max(L["y0"] - 4, 0), x1, L["y1"] + 4)).convert("RGB")
    txt = Image.new("RGB", (img.width, 44), (235, 242, 255)); d = ImageDraw.Draw(txt)
    for c, ch in enumerate(card[:70]):
        if ch != " ":
            d.text((c * m["pitch"] + 3, 2), ch, font=font, fill=(200, 0, 0) if i not in fix else (0, 120, 0))
    row = Image.new("RGB", (img.width + 70, img.height + 50), "white")
    ImageDraw.Draw(row).text((4, 10), str(i), fill=(0, 0, 0)); row.paste(img, (70, 0)); row.paste(txt, (70, img.height))
    strips.append(row); print(f"{i}\t{card}")
W = max(s.width for s in strips); H = sum(s.height for s in strips)
sheet = Image.new("RGB", (W, H), "white"); y = 0
for s in strips:
    sheet.paste(s, (0, y)); y += s.height
sheet.resize((int(W * 0.62), int(H * 0.62)), Image.LANCZOS).save(out)
