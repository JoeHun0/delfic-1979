"""Compare the glyph-classifier reading of the PAM data cards with the OCR models, field by field, and
write a review list. usage: python3 -I pamcheck.py <workdir> <page> ...
A field is accepted when the classifier agrees with every OCR model that parsed the line into 5 fields
(and at least one did), or when no model parsed it but the classifier's weakest digit margin is high."""
import re
import sys
from pathlib import Path

num = re.compile(r"(\d?\.\d{6}E[+-]\d{2}|0\.)")


def fix(t):
    t = t.replace(" ", "")
    return t


def main():
    wd = Path(sys.argv[1]); pages = [int(p) for p in sys.argv[2:]]
    tot = ok = 0; review = []
    for pg in pages:
        cl = [l.split("\t") for l in (wd / "pam" / f"p{pg:03d}.tsv").read_text().splitlines()]
        reads = {}
        for m in ("glm", "lighton", "dots"):
            f = wd / f"ocr-{m}" / f"p{pg:03d}.tsv"
            if f.exists():
                reads[m] = {int(r.split("\t")[0]): r.split("\t")[4].split(" || ")[0] for r in f.read_text().splitlines()}
        for x in cl:
            i = int(x[0]); vals = x[5].split() if len(x) > 5 else []
            if len(vals) != 5:
                continue
            ocr = []
            for m, R in reads.items():
                v = num.findall(fix(R.get(i, "")))
                if len(v) == 5:
                    ocr.append([float(("0" + a) if a.startswith(".") else a) for a in v])
            for k, v in enumerate(vals):
                tot += 1
                ov = [o[k] for o in ocr]
                if ov and all(abs(float(v) - o) <= 1e-9 * max(1, abs(o)) for o in ov):
                    ok += 1
                else:
                    review.append((pg, i, k + 1, v, ov))
    (wd / "pam" / "review.tsv").write_text("".join(f"{a}\t{b}\t{c}\t{d}\t{e}\n" for a, b, c, d, e in review))
    print(f"{tot} fields, {ok} agreed, {len(review)} to review")


if __name__ == "__main__":
    main()
