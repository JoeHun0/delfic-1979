"""Count cloud-history cells of an ICRM output that equal the printed table at 4 significant digits."""
import re, sys
pr={}
for l in open(sys.argv[1]):
    if l[0] in "#r": continue
    f=l.rstrip("\n").split("\t"); pr[int(f[0])]=f[1:]
def sig4(x): return f"{float(x):.4g}"
ok=tot=0
for l in open(sys.argv[2]):
    m=re.match(r"\s+(\d+)\)\s+(.*)", l)
    if not m or int(m.group(1)) not in pr: continue
    row=int(m.group(1)); ours=re.findall(r"-?\d\.\d+E[+-]\d+", m.group(2))
    for p,o in zip(pr[row], ours):
        if "?" in p or not p: continue
        tot+=1; ok+= sig4(p)==sig4(o)
    pr.pop(row)
print(f"{ok}/{tot} legible printed cells identical")
