"""Write hand-verified PAM cards: pamset.py <wd> <page> <line> v1 v2 v3 v4 v5  (values as printed, e.g. .549000E+00 or 0.)"""
import sys
from pathlib import Path
wd=Path(sys.argv[1]); pg=int(sys.argv[2]); ln=int(sys.argv[3]); vals=sys.argv[4:9]
assert len(vals)==5
card="".join(("  0." if v in ("0.","0") else "   "+v.rstrip("?")).ljust(14) for v in vals)
rows=[r for r in (wd/"pamfix.tsv").read_text().splitlines() if r and not r.startswith(f"p{pg:03d}\t{ln}\t")] if (wd/"pamfix.tsv").exists() else []
rows.append(f"p{pg:03d}\t{ln}\t{card.rstrip()}"+("\t?" if any(v.endswith("?") for v in vals) else ""))
(wd/"pamfix.tsv").write_text("\n".join(rows)+"\n")
