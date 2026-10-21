import sys
from pathlib import Path
B=Path(sys.argv[1]); n=sys.argv[2]
done={tuple(l.split("\t")[:2]) for l in (B/"corrections.tsv").read_text().splitlines() if l and not l.startswith("#")}
for l in (B/"review-sheets"/f"sheet-{int(n):02d}.txt").read_text().splitlines():
    x=l.split("\t"); print(("DONE " if (x[1],x[2]) in done else "     ")+"\t".join(x[:6])+"\t"+x[6][:110])
