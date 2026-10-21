import re, numpy as np, sys
def grid(lines):
    cols=[[],[],[],[]]
    for l in lines:
        r=[float(x) for x in re.findall(r'\d\.\d{4}E[+-]\d\d',l.replace('?',''))]
        for c in range(len(r)//2):
            if r[2*c]>0: cols[c].append(r[2*c+1])
    return np.array(sum(cols,[]))
pr=grid([l for l in open('/home/kotnyekjm/book-ocr/books/delfic-1979-vol2/run/printed-opm-checks.txt') if '|' in l])
L=open(sys.argv[1]).read().splitlines(); i=[k for k,l in enumerate(L) if 'PSIZE          FP' in l][0]
ours=grid(L[i+1:i+9]); r=ours/pr; m=np.arange(30)!=20
print(f"K ratio {ours.sum()/pr.sum():.4f}  per-class ratio min {r.min():.4f} max {r.max():.4f} sd(no21) {np.std(r[m])/np.mean(r[m]):.5f}")
