"""Re-key hand corrections of deskewed pages to their new line numbers (matching by line centre height).

usage: python3 -I remap.py <workdir> <page> [<page> ...]
Old geometry: <workdir>/redo/p<page>-old.json; new: <workdir>/lines/p<page>.json.
Rewrites corrections.tsv in place (a backup is kept as corrections.tsv.bak) and prints every mapping.
"""
import json
import shutil
import sys
from pathlib import Path

wd = Path(sys.argv[1]); pages = [int(p) for p in sys.argv[2:]]
shutil.copy(wd / "corrections.tsv", wd / "corrections.tsv.bak")
rows = (wd / "corrections.tsv").read_text().splitlines()
out = []
for r in rows:
    if not r.strip() or r.startswith("#"):
        out.append(r); continue
    pg, ln, txt = r.split("\t", 2); p = int(pg.lstrip("p"))
    if p not in pages:
        out.append(r); continue
    old = json.load(open(wd / "redo" / f"p{p:03d}-old.json"))["lines"][int(ln) - 1]
    new = json.load(open(wd / "lines" / f"p{p:03d}.json"))["lines"]
    yc = (old["y0"] + old["y1"]) / 2
    k, L = min(enumerate(new, 1), key=lambda kv: abs((kv[1]["y0"] + kv[1]["y1"]) / 2 - yc))
    d = abs((L["y0"] + L["y1"]) / 2 - yc)
    flag = "" if d <= 15 else "  ** CHECK"
    print(f"p{p:03d} {ln:>3s} -> {k:3d}  (dy {d:4.1f}){flag}  {txt[:60]}")
    out.append(f"p{p:03d}\t{k}\t{txt}")
(wd / "corrections.tsv").write_text("\n".join(out) + "\n")
