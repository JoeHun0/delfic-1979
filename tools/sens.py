"""Perturb each numeric literal in a line range of run/icrm_port.f by +1% and report row-1/row-17 effects.
usage: python3 -I sens.py <rundir> <from> <to>"""
import re, subprocess, sys
from pathlib import Path
rd = Path(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3])
src = (rd / "icrm_port.f").read_text().splitlines()
deck = (rd / "icrm-test-deck.txt").read_text()
def run(lines):
    (rd / "s.f").write_text("\n".join(lines) + "\n")
    r = subprocess.run(["gfortran", "-std=legacy", "-ffixed-form", "-fdefault-real-8", "-fdefault-integer-8",
                        "-fno-automatic", "-finit-local-zero", "-o", "s", "driver.f", "s.f"], cwd=rd, capture_output=True)
    if r.returncode: return None
    o = subprocess.run(["./s"], cwd=rd, input=deck, capture_output=True, text=True, timeout=60).stdout
    rows = {}
    for l in o.splitlines():
        m = re.match(r"\s*(\d+)\)\s+(.*)", l)
        if m and m.group(1) in ("1", "17") and m.group(1) not in rows:
            v = re.findall(r"-?\d\.\d+E[+-]\d+", m.group(2)); rows[m.group(1)] = [float(x) for x in v]
    return rows
base = run(src)
print("base r1 base/top/rad", base["1"][2:5], "r17", base["17"][2:5])
num = re.compile(r"(?<![A-Z0-9.])(\d+\.\d*(?:E[+-]?\d+)?|\d*\.\d+(?:E[+-]?\d+)?)")
for n in range(a, b + 1):
    l = src[n - 1]
    if not l.strip() or l[0] in "C*" or "FORMAT" in l: continue
    for m in num.finditer(l[6:]):
        tok = m.group(1); val = float(tok)
        if val == 0: continue
        new = l[:6] + l[6:][:m.start()] + repr(val * 1.01) + l[6:][m.end():]
        if len(new) > 72: new = new[:72]
        s2 = list(src); s2[n - 1] = new
        r = run(s2)
        if not r: continue
        d1 = [(x / y - 1) * 100 if y else 0 for x, y in zip(r["1"][2:5], base["1"][2:5])]
        d17 = [(x / y - 1) * 100 if y else 0 for x, y in zip(r["17"][2:5], base["17"][2:5])]
        if max(map(abs, d1 + d17)) > 0.01:
            print(f"{n:5d} {tok:>14s}  r1 base/top/rad % {d1[0]:+.3f} {d1[1]:+.3f} {d1[2]:+.3f}   r17 {d17[0]:+.3f} {d17[1]:+.3f} {d17[2]:+.3f}")
