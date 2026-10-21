"""OCR a line-printer listing line by line and place the characters into card columns.

usage: python3 -I ocrlines.py <workdir> <model> <first_page> <last_page> [--port 8095]

For each page: <workdir>/native/n-<page>-*.png and <workdir>/lines/p<page>.json (from lines.py).
Each line is cropped (columns 1-72 and 73-80 separately), read by the model, and the non-blank
characters are put, in order, into the line's inked columns. Result per page:
<workdir>/ocr-<model>/p<page>.tsv  with  line_no, y0, status, card(80 chars), raw text.
status OK = number of characters read equals number of inked cells; otherwise COUNT a/b (needs a look).
"""
import base64
import io
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path.home() / ".claude/skills/book-ocr/scripts"))
from common import MODELS, MODELS_DIR, SERVER  # noqa: E402

LINE_PROMPT = "Transcribe this single line of a computer program listing exactly, character by character."


def ask(port, img, prompt):
    buf = io.BytesIO(); img.save(buf, "PNG")
    url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    content = [{"type": "image_url", "image_url": {"url": url}}]
    if prompt:
        content.append({"type": "text", "text": prompt})
    body = {"messages": [{"role": "user", "content": content}], "temperature": 0.0, "max_tokens": 200}
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def clean(text):
    t = text.strip().splitlines()[0] if text.strip() else ""
    for a, b in (("```", ""), ("`", ""), ("$", ""), ("\\(", "("), ("\\)", ")")):
        t = t.replace(a, b)
    return t.strip()


def place(text, cols):
    chars = [c for c in text if not c.isspace()]
    card = [" "] * 80
    if len(chars) == len(cols):
        for c, k in zip(chars, cols):
            card[k - 1] = c
        return "".join(card), "OK"
    return "".join(card), f"COUNT {len(chars)}/{len(cols)}"


def main():
    wd, model = Path(sys.argv[1]), sys.argv[2]
    p0, p1 = int(sys.argv[3]), int(sys.argv[4])
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8095
    mfile, mmproj, mprompt = MODELS[model]
    prompt = mprompt if model != "lighton" else None
    out = wd / f"ocr-{model}"; out.mkdir(exist_ok=True)
    log = open(wd / f"server-lines-{model}.log", "w")
    proc = subprocess.Popen([str(SERVER), "-m", str(MODELS_DIR / mfile), "--mmproj", str(MODELS_DIR / mmproj),
                             "-ngl", "99", "-c", "4096", "--port", str(port), "--no-webui"], stdout=log, stderr=log)
    try:
        for _ in range(300):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2); break
            except Exception:
                time.sleep(1)
        for pg in range(p0, p1 + 1):
            dst = out / f"p{pg:03d}.tsv"
            if dst.exists():
                continue
            nat = sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]
            meta_lines = json.load(open(wd / "lines" / f"p{pg:03d}.json"))
            meta, lines = meta_lines["meta"], meta_lines["lines"]
            im = Image.open(nat).convert("L")
            P, x1 = meta["pitch"], meta["col1_x"]
            rows = []
            t0 = time.time()
            for i, L in enumerate(lines, 1):
                y0, y1 = max(L["y0"] - 8, 0), min(L["y1"] + 8, im.height)
                code_cols = [c for c in L["cols"] if c <= 72]
                seq_cols = [c for c in L["cols"] if c >= 73]
                card = [" "] * 80; status = []; raw = []
                for cols, c_lo, c_hi in ((code_cols, 1, 72), (seq_cols, 73, 80)):
                    if not cols:
                        continue
                    xa = int(x1 + (min(cols) - 1) * P - P / 2) - 4
                    xb = int(x1 + (max(cols) - 1) * P + P / 2) + 4
                    crop = im.crop((max(xa, 0), y0, min(xb, im.width), y1))
                    if cols == [1]:            # a lone mark in column 1 is a comment line's C
                        card[0] = "C"; status.append("OK"); raw.append("C"); continue
                    crop = crop.resize((int(crop.width * 2), int(crop.height * 2)), Image.LANCZOS)
                    W = max(crop.width + 80, 900)
                    pad = Image.new("L", (W, crop.height + 40), 255); pad.paste(crop, (40, 20))
                    text = clean(ask(port, pad, prompt or LINE_PROMPT))
                    part, st = place(text, cols)
                    for k in range(c_lo - 1, c_hi):
                        if part[k] != " ":
                            card[k] = part[k]
                    status.append(st if st != "OK" else ("OK" if c_lo == 1 else "OKs"))
                    raw.append(text.replace("\t", " "))
                stat = "OK" if all(s.startswith("OK") for s in status) else ";".join(s for s in status if not s.startswith("OK"))
                rows.append(f"{i}\t{L['y0']}\t{stat}\t{''.join(card)}\t{' || '.join(raw)}")
            dst.write_text("\n".join(rows) + "\n")
            nok = sum(r.split("\t")[2] == "OK" for r in rows)
            print(f"p{pg:03d}: {len(rows)} lines, {nok} OK, {time.time() - t0:.0f}s", flush=True)
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
