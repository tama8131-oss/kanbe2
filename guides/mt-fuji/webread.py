"""Phone reading version of the Mt. Fuji guide (used by the e-book, webbook.py).

The same designed pages as the PDF (magazine.py), but as real web pages: the reader's
screen sets the width, everything is drawn larger (web.css scales the print sizes up with
`zoom`), wide blocks stack into one column, and the course finder becomes a tap-through quiz.

Output: dist/webbook/read/{lang}.html (one fragment per language), read/style.css, read/photos/
"""
import pathlib
import re
import sys

from PIL import Image

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import chart  # noqa: E402
import i18n  # noqa: E402
import magazine  # noqa: E402
import photos as ph  # noqa: E402

OUT = HERE / "dist" / "webbook" / "read"


def scope(css):
    """Put `.read ` in front of every rule, so the book's styles never touch the reader's own buttons."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            out.append(css[i:])
            break
        head = css[i:j]
        depth, k = 1, j + 1
        while depth and k < n:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        body = css[j + 1:k - 1]
        sel = head.strip()
        if sel.startswith("@media") or sel.startswith("@supports"):
            out.append(head + "{" + scope(body) + "}")
        elif sel.startswith("@"):
            out.append(head + "{" + body + "}")
        else:
            lead = head[:len(head) - len(head.lstrip())]
            parts = []
            for part in sel.split(","):
                part = part.strip()
                parts.append(part if part.startswith(".read") else ".read " + part)
            out.append(lead + ", ".join(parts) + " {" + body + "}")
        i = k
    return "".join(out)


def build():
    (OUT / "photos").mkdir(parents=True, exist_ok=True)
    for key, (name, *_rest) in ph.PHOTOS.items():
        im = Image.open(ph.DIR / name).convert("RGB")
        im.thumbnail((1200, 1200))
        im.save(OUT / "photos" / name, "JPEG", quality=78, optimize=True)
    ph.WEB[0] = True
    magazine.SINGLE[0] = True   # no "change language" link inside a page: the reader's top bar does that
    magazine.REVIEW[0] = False
    try:
        for code, *_ in i18n.LANGS:
            T = magazine.load_text(code)
            quiz = chart.quiz(code, T["finder"]["title"], T["finder"]["tips"], i18n.to_hant)
            html = magazine.language_book(code, quiz, magazine.know_rows(code))
            (OUT / f"{code}.html").write_text(html, encoding="utf-8")
    finally:
        ph.WEB[0] = False
    css = (HERE / "magazine.css").read_text(encoding="utf-8")
    css = css.replace(":root {", ".read {", 1)
    css = css.replace("html, body { margin: 0; padding: 0; background: var(--paper); }", "")
    css = css.replace("body { font-family: var(--sans); color: var(--ink); }", ".read { font-family: var(--sans); color: var(--ink); background: var(--paper); }")
    css = css.replace("@page { size: 148mm 210mm; margin: 0; }", "")
    css = scope(css + chart.CSS) + (HERE / "web.css").read_text(encoding="utf-8")
    (OUT / "style.css").write_text(css, encoding="utf-8")
    print(OUT, len(list(OUT.glob("*.html"))), "languages")


if __name__ == "__main__":
    build()
