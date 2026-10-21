"""Find printed lines and the 80-column card grid on a line-printer listing page (1-bit scan, 300 dpi).

usage: python3 -I lines.py <native.png> <out.json> [debug.png]

The listing is monospaced. The character pitch and phase are fitted to the x-centres of letter-sized ink
blobs. Card columns 73-80 hold the sequence IDs: the rightmost run of 8 densely used cells. Every blob is
assigned to the cell of its centre, so a line's inked cells are exact even for broken glyphs. Lines are
found only between card columns 0 and 81, so page-edge shadows cannot join them.
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def main():
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("L")
    a = np.asarray(im) < 128
    h, w = a.shape
    lab, n = ndimage.label(a)
    objs = ndimage.find_objects(lab)
    blobs = []
    for i, sl in enumerate(objs, 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 2 <= hh <= 45 and ww <= 40:
            npx = int((lab[sl] == i).sum())
            if npx >= 5:
                blobs.append((sl[0].start, sl[0].stop, sl[1].start, sl[1].stop, npx))
        elif 12 <= hh <= 45 and 40 < ww <= 140:      # touching characters: split into pitch-wide pieces
            npx = int((lab[sl] == i).sum())
            k = max(2, int(round(ww / 25.9)))
            for j in range(k):
                xa = sl[1].start + j * ww / k; xb = sl[1].start + (j + 1) * ww / k
                blobs.append((sl[0].start, sl[0].stop, xa, xb, npx // k))
    B = np.array(blobs, float)
    yc, xc = (B[:, 0] + B[:, 1]) / 2, (B[:, 2] + B[:, 3]) / 2
    big = ((B[:, 1] - B[:, 0]) >= 15) & ((B[:, 3] - B[:, 2]) >= 4) & ((B[:, 3] - B[:, 2]) <= 30)
    best = None
    for pitch in np.arange(23.0, 29.0, 0.005):
        z = np.exp(2j * np.pi * xc[big] / pitch).mean()
        if best is None or abs(z) > best[0]:
            best = (abs(z), pitch, (np.angle(z) % (2 * np.pi)) / (2 * np.pi) * pitch)
    _, pitch, phase = best
    cell = np.floor((xc - phase) / pitch + 0.5).astype(int)
    # column 80 (last digit of the sequence number) is inked on every card: the rightmost cell whose
    # letter-sized-blob count is at least 60 % of the busiest cell; column 73 = that - 7
    cnt = np.bincount(cell[big] - cell.min(), minlength=cell.max() - cell.min() + 1)
    strong = np.nonzero(cnt >= 0.6 * cnt.max())[0]
    c80 = strong.max() + cell.min()
    c73 = c80 - 7
    col = cell - c73 + 73
    inside = (col >= 0) & (col <= 81)
    # lines from blobs inside the card area
    prof = np.zeros(h)
    codeonly = "--codeonly" in sys.argv
    for (y0, y1, x0, x1, npx), ok, cc in zip(blobs, inside, col):
        if ok and (not codeonly or cc <= 72):
            prof[int(y0):int(y1)] += 1
    on = prof > 0
    rows, start = [], None
    for y in range(h + 1):
        v = on[y] if y < h else False
        if v and start is None:
            start = y
        if not v and start is not None:
            rows.append([start, y]); start = None
    # merge pieces closer than 8 px (dots/commas below letters), drop slivers
    merged = []
    for r in rows:
        if merged and r[0] - merged[-1][1] < 8:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    # split bands that hold several lines: cut at the profile minima nearest to multiples of the line pitch
    hts = [r[1] - r[0] for r in merged if 18 <= r[1] - r[0] <= 40]
    hmed = float(np.median(hts)) if hts else 30.0
    starts = [r[0] for r in merged if 18 <= r[1] - r[0] <= 40]
    dif = [b - a for a, b in zip(starts, starts[1:]) if 30 < b - a < 60]
    ypitch = float(np.median(dif)) if dif else 43.0
    split = []
    for y0, y1 in merged:
        k = int(round((y1 - y0 + (ypitch - hmed)) / ypitch))
        if y1 - y0 > hmed + 0.45 * ypitch and k >= 2:
            cuts = [y0]
            for j in range(1, k):
                guess = y0 + j * (y1 - y0 + (ypitch - hmed)) / k - (ypitch - hmed) / 2
                lo, hi = int(guess - 10), int(guess + 10)
                seg = prof[lo:hi]
                cuts.append(lo + int(np.argmin(seg)) if len(seg) else int(guess))
            cuts.append(y1)
            split += [[a, b] for a, b in zip(cuts, cuts[1:])]
        else:
            split.append([y0, y1])
    lines = []
    for y0, y1 in split:
        if y1 - y0 < 10:
            continue
        sel = inside & (yc >= y0) & (yc < y1)
        ink = {}
        for c, npx in zip(col[sel], B[sel, 4]):
            if 1 <= c <= 80:
                ink[int(c)] = ink.get(int(c), 0) + int(npx)
        cols = sorted(ink)
        if cols:
            lines.append({"y0": int(y0), "y1": int(y1), "cols": cols, "ink": {str(k): v for k, v in ink.items()}})
    col1_x = phase + (c73 - 72) * pitch
    meta = {"pitch": float(pitch), "col1_x": float(col1_x), "width": w, "height": h, "n_lines": len(lines)}
    json.dump({"meta": meta, "lines": lines}, open(dst, "w"))
    tall = [L for L in lines if L["y1"] - L["y0"] > 48]
    print(f"{src.split('/')[-1]}: {len(lines)} lines, pitch {pitch:.3f}px, col1 x={col1_x:.1f}, tall {len(tall)}")
    if len(sys.argv) > 3 and not sys.argv[3].startswith("--"):
        dbg = im.convert("RGB"); d = ImageDraw.Draw(dbg)
        for k in range(0, 82):
            x = col1_x + (k - 1) * pitch - pitch / 2
            d.line([(x, 0), (x, h)], fill=(255, 0, 0) if k in (1, 6, 7, 73, 81) else (255, 210, 210))
        for L in lines:
            d.rectangle([col1_x - 2 * pitch, L["y0"], col1_x - pitch, L["y1"]], outline=(0, 0, 255))
        dbg.save(sys.argv[3])


if __name__ == "__main__":
    main()
