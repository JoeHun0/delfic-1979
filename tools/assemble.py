"""Assemble the transcribed DELFIC listing (final/p*.tsv) into Fortran source decks.

usage: python3 -I assemble.py <workdir> <first_page> <last_page>

Writes <workdir>/src/<deck>.f (one per *DECK) and <workdir>/src/listing.txt (all cards with their
sequence IDs), and checks each deck's sequence numbers for gaps and repeats (a gap = a line missed by the
segmentation, a repeat = a line read twice).
"""
import re
import sys
from collections import OrderedDict
from pathlib import Path


def main():
    wd = Path(sys.argv[1]); p0, p1 = int(sys.argv[2]), int(sys.argv[3])
    src = wd / "src"; src.mkdir(exist_ok=True)
    decks = OrderedDict(); cur = None; listing = []
    inserts = {}
    for r in (wd / "inserts.tsv").read_text().splitlines():
        if r.strip() and not r.startswith("#"):
            pg_, ln_, card_, note_ = r.split("\t")
            inserts.setdefault((int(pg_.lstrip("p")), int(ln_)), []).append(card_)
    for pg in range(p0, p1 + 1):
        f = wd / "final" / f"p{pg:03d}.tsv"
        for r in f.read_text().splitlines():
            row = r.split("\t")
            verdict, card = row[3], row[4]
            seq = row[-1] if len(row) > 7 else ""
            if verdict in ("NOISE", "SEQONLY"):
                continue
            m = re.match(r"\s*\*\s*D\s*E\s*C\s*K\s*,?\s*([A-Z0-9]+)", card)
            if m:
                cur = m.group(1); decks[cur] = []
                listing.append(f"{'':72s}  p{pg:03d} {row[0]:>2s} *DECK {cur}")
                continue
            if cur is None:
                cur = "PRELUDE"; decks[cur] = []
            decks[cur].append((pg, int(row[0]), card.rstrip(), seq, verdict))
            listing.append(f"{card:72s}  p{pg:03d} {row[0]:>2s} {seq:10s} {verdict}")
            for extra in inserts.get((pg, int(row[0])), []):
                decks[cur].append((pg, int(row[0]), extra.rstrip(), "", "INSERT"))
                listing.append(f"{extra:72s}  p{pg:03d} {row[0]:>2s} {'':10s} INSERT")
    (src / "listing.txt").write_text("\n".join(listing) + "\n")
    for name, cards in decks.items():
        (src / f"{name.lower()}.f").write_text("".join(c[2] + "\n" for c in cards))
        nums = []
        for pg, ln, card, seq, v in cards:
            m = re.search(r"(\d+)$", seq)
            nums.append(int(m.group(1)) if m else None)
        known = [n for n in nums if n is not None]
        gaps = []
        for a, b in zip(known, known[1:]):
            if b != a + 1:
                gaps.append(f"{a}->{b}")
        print(f"{name:8s} {len(cards):4d} cards, seq {known[0] if known else '-'}..{known[-1] if known else '-'}, "
              f"unread seq {nums.count(None)}, jumps {len(gaps)}: {' '.join(gaps[:12])}")


if __name__ == "__main__":
    main()
