"""Review sheet for compile errors: the first error per routine (later ones are often cascades), or all.

usage: python3 -I errsheet.py <workdir> [N] [--all]
Prints n, page, line, message, current card; writes review-sheets/err.png with the line images.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

wd = Path(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 14
rows = [r.split("\t") for r in (wd / "src" / "errors.txt").read_text().splitlines() if r]
src = (wd / "src" / "icrm.f").read_text().splitlines()
# routine of each source line: last SUBROUTINE/FUNCTION before it
routine, cur = [], "MAIN"
for l in src:
    s = l[6:].strip() if len(l) > 6 and l[:1] not in "C*" else ""
    if s.startswith(("SUBROUTINE", "FUNCTION", "PROGRAM")) or "FUNCTION " in s[:20]:
        cur = s.split("(")[0]
    routine.append(cur)
pick, seen = [], set()
for r in rows:
    rt = routine[int(r[0]) - 1]
    if "--all" in sys.argv or rt not in seen:
        pick.append(r); seen.add(rt)
pick = pick[:N]; strips = []
for k, r in enumerate(pick):
    pg = int(r[1][1:]); ln = int(r[2])
    J = json.load(open(wd / "lines" / f"p{pg:03d}.json")); m = J["meta"]; L = J["lines"][ln - 1]
    im = Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
    x0 = int(m["col1_x"] - m["pitch"] / 2) - 2; x1 = int(m["col1_x"] + 71.5 * m["pitch"]) + 2
    c = im.crop((x0, max(L["y0"] - 5, 0), x1, L["y1"] + 5)).convert("RGB")
    row = Image.new("RGB", (c.width + 60, c.height), "white")
    ImageDraw.Draw(row).text((5, c.height // 3), str(k + 1), fill=(0, 0, 0)); row.paste(c, (60, 0)); strips.append(row)
    print(f"{k+1}\t{r[1]}\t{r[2]}\t{routine[int(r[0])-1]}\t{r[3][:60]}\n\t{r[4]}")
if strips:
    W = max(s.width for s in strips); H = sum(s.height for s in strips)
    sheet = Image.new("RGB", (W, H), "white"); y = 0
    for s in strips:
        sheet.paste(s, (0, y)); y += s.height
    sheet.resize((int(W * 0.72), int(H * 0.72)), Image.LANCZOS).save(wd / "review-sheets" / "err.png")
print(len(rows), "errors;", len({routine[int(r[0]) - 1] for r in rows}), "routines with errors")
