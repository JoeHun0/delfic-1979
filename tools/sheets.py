"""Review sheets for the flagged lines: stacked line images (columns 1-72) with a number, plus a text list
of the best candidate per line.

usage: python3 -I sheets.py <workdir> <outdir> [per_sheet]
Writes <outdir>/sheet-NN.png and <outdir>/sheet-NN.txt (number, page, line, verdict, inked cells, candidate).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    wd, od = Path(sys.argv[1]), Path(sys.argv[2]); od.mkdir(parents=True, exist_ok=True)
    per = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    items = []
    for f in sorted((wd / "merged").glob("p*.tsv")):
        pg = int(f.stem[1:])
        J = json.load(open(wd / "lines" / f"p{pg:03d}.json"))
        for r in f.read_text().splitlines():
            row = r.split("\t")
            if row[3] in ("NONE", "SINGLE", "TIE"):
                i = int(row[0]); L = J["lines"][i - 1]
                cand = row[4].rstrip() if row[3] != "NONE" else ""
                if not cand:   # longest raw reading
                    raws = []
                    for d in ("ocr2-glm", "ocr-glm", "ocr2-lighton", "ocr-lighton", "ocr-dots"):
                        g = wd / d / f"p{pg:03d}.tsv"
                        if g.exists():
                            for rr in g.read_text().splitlines():
                                x = rr.split("\t")
                                if x and x[0] == str(i):
                                    raws.append(x[4].split(" || ")[0])
                    cand = "raw: " + (max(raws, key=len) if raws else "")
                items.append((pg, i, row[3], [c for c in L["cols"] if c <= 72], cand, J["meta"], L))
    for s in range(0, len(items), per):
        chunk = items[s:s + per]
        strips = []
        for k, (pg, i, v, cols, cand, meta, L) in enumerate(chunk):
            im = Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
            x0 = int(meta["col1_x"] - meta["pitch"] / 2) - 2; x1 = int(meta["col1_x"] + 71.5 * meta["pitch"]) + 2
            c = im.crop((x0, max(L["y0"] - 5, 0), x1, L["y1"] + 5)).convert("RGB")
            d = ImageDraw.Draw(c)
            for col in (6, 7, 12, 22, 32, 42, 52, 62):    # light guides at column boundaries (left edges)
                x = meta["col1_x"] + (col - 1) * meta["pitch"] - meta["pitch"] / 2 - x0
                d.line([(x, 0), (x, 4)], fill=(255, 0, 0))
            lab = Image.new("RGB", (60, c.height), "white"); ImageDraw.Draw(lab).text((5, c.height // 3), str(s + k + 1), fill=(0, 0, 0))
            row = Image.new("RGB", (c.width + 60, c.height), "white"); row.paste(lab, (0, 0)); row.paste(c, (60, 0))
            strips.append(row)
        W = max(r.width for r in strips); H = sum(r.height for r in strips)
        sheet = Image.new("RGB", (W, H), "white"); y = 0
        for r in strips:
            sheet.paste(r, (0, y)); y += r.height
        sheet = sheet.resize((int(W * 0.72), int(H * 0.72)), Image.LANCZOS)
        n = s // per + 1
        sheet.save(od / f"sheet-{n:02d}.png")
        with open(od / f"sheet-{n:02d}.txt", "w") as f:
            for k, (pg, i, v, cols, cand, meta, L) in enumerate(chunk):
                f.write(f"{s + k + 1}\tp{pg:03d}\t{i}\t{v}\t{len(cols)}\t{cols[0] if cols else ''}\t{cand}\n")
    print(len(items), "items,", (len(items) + per - 1) // per, "sheets")


if __name__ == "__main__":
    main()
