"""Check every deck for missing or extra cards using the printed sequence numbers (columns 73-80).

usage: python3 -I seqcheck.py <workdir> <first_page> <last_page>

All lines with a sequence field are taken in page order, including dropped star-comment lines. Within a
deck the numbers must run 1, 2, 3 ...; OCR misreads single numbers, so anchors are the longest run of
readings consistent with "number = position + constant". Between consecutive anchors the number of lines
must equal the difference of their numbers; otherwise the stretch is reported.
"""
import json
import re
import sys
from pathlib import Path


def main():
    wd = Path(sys.argv[1]); p0, p1 = int(sys.argv[2]), int(sys.argv[3])
    seq = []   # (deck-prefix-guess, number or None, page, line, verdict, card)
    for pg in range(p0, p1 + 1):
        J = json.load(open(wd / "lines" / f"p{pg:03d}.json"))
        for r in (wd / "final" / f"p{pg:03d}.tsv").read_text().splitlines():
            x = r.split("\t"); i = int(x[0]); L = J["lines"][i - 1]
            if 80 not in L["cols"] and 79 not in L["cols"]:
                continue
            code = [c for c in L["cols"] if c <= 72]
            if x[3] == "NOISE" and not (code and code[0] == 1 and len(code) >= 60):
                continue          # page-edge noise, not a card
            s = x[-1] if len(x) > 7 else ""
            m = re.search(r"(\d+)$", s)
            seq.append([m.group(1) and int(m.group(1)) if m else None, pg, i, x[3], x[4].rstrip()])
    # split into decks at *DECK cards
    decks, cur = [], None
    for e in seq:
        if re.match(r"\s*\*\s*DECK", e[4]):
            cur = [e[4].split(",")[-1].strip() if "," in e[4] else e[4], []]; decks.append(cur)
        if cur is not None:
            cur[1].append(e)
    bad = 0
    for name, es in decks:
        n = len(es)
        # position k should carry number k+1
        ok = [k for k, e in enumerate(es) if e[0] == k + 1]
        problems = []
        if not ok:
            problems.append("no reading matches its position")
        else:
            # find first position where readings stop matching for a while
            off = 0; run = []
            for k, e in enumerate(es):
                if e[0] is None:
                    continue
                d = e[0] - (k + 1)
                run.append((k, d))
            # report the positions where the offset changes and stays changed for >= 3 readings
            prev = 0
            for idx in range(len(run)):
                k, d = run[idx]
                nxt = [dd for _, dd in run[idx:idx + 4]]
                if d != prev and len(nxt) >= 3 and all(dd == d for dd in nxt[:3]):
                    problems.append(f"offset {prev:+d}->{d:+d} near p{es[k][1]:03d} L{es[k][2]}")
                    prev = d
        status = "OK" if not problems else "CHECK"
        bad += status != "OK"
        print(f"{name:10s} {n:4d} lines {status} {'; '.join(problems)}")
    print(f"{bad} decks to check")


if __name__ == "__main__":
    main()
