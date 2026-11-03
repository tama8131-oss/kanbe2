"""Web e-book version of the Mt. Fuji guide: choose a language, then page through ONLY that language.

A PDF always shows its full page count (241), so the language-only reading the user wants is
built as a web page instead. Each page of dist/magazine.pdf becomes a WebP picture (the design
stays exactly the same) and the PDF's links (table of contents, QR codes, booking sites) are
kept as tappable areas on top of the picture.

Usage: python3 guides/mt-fuji/webbook.py   (build dist/magazine.pdf first with magazine.py)
Output: guides/mt-fuji/dist/webbook/  (index.html + img/*.webp)
"""
import io
import json
import pathlib
import shutil
import sys

import pymupdf
from PIL import Image

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import i18n  # noqa: E402

PAGES_PER_LANG = 34
OUT = HERE / "dist" / "webbook"


def build():
    doc = pymupdf.open(HERE / "dist" / "magazine.pdf")
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "img").mkdir(parents=True)
    W, H = doc[0].rect.width, doc[0].rect.height
    credits = len(doc) - 1
    langs, start = [], 2  # page 0 = front cover, 1 = language picker, then 34 pages per language

    def picture(i):
        name = f"img/p{i:03d}.webp"
        if not (OUT / name).exists():
            pix = doc[i].get_pixmap(dpi=170)
            Image.frombytes("RGB", (pix.width, pix.height), pix.samples).save(OUT / name, "WEBP", quality=72)
        return name

    def sharp(i):  # larger picture used only when a page is zoomed in
        name = f"img/h{i:03d}.webp"
        if not (OUT / name).exists():
            pix = doc[i].get_pixmap(dpi=280)
            Image.frombytes("RGB", (pix.width, pix.height), pix.samples).save(OUT / name, "WEBP", quality=70)
        return name

    for code, name, flags, _, go in i18n.LANGS:
        own = list(range(start, start + PAGES_PER_LANG)) + [credits]
        index = {g: k for k, g in enumerate(own)}
        pages = []
        for g in own:
            links = []
            for ln in doc[g].get_links():
                r = ln["from"]
                box = [round(r.x0 / W, 4), round(r.y0 / H, 4), round(r.width / W, 4), round(r.height / H, 4)]
                if ln.get("uri"):
                    links.append({"b": box, "u": ln["uri"]})
                elif ln.get("page") in index:
                    links.append({"b": box, "p": index[ln["page"]]})
            pages.append({"i": sharp(g), "h": sharp(g), "l": links})  # one sharp picture per page (artifact file-count limit)
        langs.append({"code": code, "name": name, "flags": flags, "go": go, "pages": pages})
        start += PAGES_PER_LANG
    shutil.copy(HERE / "photos" / "cover-pagoda.jpg", OUT / "img" / "cover.jpg")
    cover = "img/cover.jpg"
    data = json.dumps({"cover": cover, "langs": langs}, ensure_ascii=False, separators=(",", ":"))
    html = (HERE / "webbook.html").read_text(encoding="utf-8").replace("/*DATA*/null", data)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(OUT, f"{len(list((OUT / 'img').glob('p*.webp')))} pages, {len(list((OUT / 'img').glob('h*.webp')))} zoom pictures, {size / 1e6:.1f} MB")


if __name__ == "__main__":
    build()
