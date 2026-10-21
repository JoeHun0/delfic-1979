"""Proof sheets: each code card's scan line with the current transcription rendered underneath in the
same column grid, so differences show at a glance.

usage: python3 -I proof.py <workdir> <from_src_line> <count> [out.png]
Source lines are those of src/icrm.f (see src/icrm.map for page/line). Comment cards are skipped.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

deck = "icrm"
if "--deck" in sys.argv:
    k = sys.argv.index("--deck"); deck = sys.argv[k + 1]; del sys.argv[k:k + 2]
wd = Path(sys.argv[1]); a = int(sys.argv[2]); n = int(sys.argv[3])
out = sys.argv[4] if len(sys.argv) > 4 else str(wd / "review-sheets" / "proof.png")
src = (wd / "src" / f"{deck}.f").read_text().splitlines()
mp = [r.split("\t") for r in (wd / "src" / f"{deck}.map").read_text().splitlines()]
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 34)
strips, k, i, listing = [], 0, a, []
cache = {}
while k < n and i <= len(src):
    card = src[i - 1]
    if card[:1] in "C*" or not card.strip():
        i += 1; continue
    pg, ln = int(mp[i - 1][1][1:]), int(mp[i - 1][2])
    if pg not in cache:
        cache[pg] = (json.load(open(wd / "lines" / f"p{pg:03d}.json")),
                     Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L"))
    J, im = cache[pg]; m = J["meta"]
    if ln - 1 >= len(J["lines"]):
        i += 1; continue
    L = J["lines"][ln - 1]
    x0 = int(m["col1_x"] - m["pitch"] / 2); x1 = int(m["col1_x"] + 71.5 * m["pitch"])
    img = im.crop((x0, max(L["y0"] - 4, 0), x1, L["y1"] + 4)).convert("RGB")
    txt = Image.new("RGB", (img.width, 44), (235, 242, 255)); d = ImageDraw.Draw(txt)
    for c, ch in enumerate(card[:72]):
        if ch != " ":
            d.text((c * m["pitch"] + 3, 2), ch, font=font, fill=(200, 0, 0))
    lab = Image.new("RGB", (70, img.height + 44), "white")
    ImageDraw.Draw(lab).text((4, 10), str(i), fill=(0, 0, 0))
    row = Image.new("RGB", (img.width + 70, img.height + 44 + 6), "white")
    row.paste(lab, (0, 0)); row.paste(img, (70, 0)); row.paste(txt, (70, img.height))
    strips.append(row); listing.append(f"{i}\tp{pg:03d}\t{ln}\t{card}"); k += 1; i += 1
W = max(s.width for s in strips); H = sum(s.height for s in strips)
sheet = Image.new("RGB", (W, H), "white"); y = 0
for s in strips:
    sheet.paste(s, (0, y)); y += s.height
sheet.resize((int(W * 0.62), int(H * 0.62)), Image.LANCZOS).save(out)
print("\n".join(listing)); print("next", i)
