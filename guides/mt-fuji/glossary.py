"""Glossary: the names of places, chapters and passes side by side in all 8 languages.

For the native-speaker check: one look shows whether a name is written the same way everywhere.
Usage: python3 guides/mt-fuji/glossary.py  ->  guides/mt-fuji/glossary.md
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import i18n  # noqa: E402
import magazine  # noqa: E402

CODES = [c for c, *_ in i18n.LANGS]


def row(get):
    out = []
    for code in CODES:
        try:
            out.append(str(get(code, magazine.load_text(code))).replace("|", "/").replace("\n", " "))
        except (KeyError, IndexError, TypeError):
            out.append("—")
    return out


def nav_names(code):
    if code in ("en", "ja"):
        return [nj if code == "ja" else ne for _, ne, nj, _ in magazine.PLACES]
    return i18n.PLACE_NAMES[code]


def build():
    names = {c: n for c, n, *_ in i18n.LANGS}
    head = "| | " + " | ".join(names[c] for c in CODES) + " |\n|" + "---|" * (len(CODES) + 1) + "\n"
    parts = ["# Mt. Fuji guide: glossary (8 languages)\n",
             "Made from the book's own text by glossary.py. If a name looks different in two places, fix text/*.py or i18n.py.\n"]
    parts.append("\n## The 8 places (chapter 3 list)\n\n" + head)
    for i in range(8):
        parts.append(f"| {i + 1} | " + " | ".join(row(lambda c, T: T["eight"]["names"][i])) + " |\n")
    parts.append("\n## Places on the navigation (QR) page\n\n" + head)
    for i in range(len(nav_names("en"))):
        parts.append(f"| {i + 1} | " + " | ".join(row(lambda c, T: nav_names(c)[i])) + " |\n")
    parts.append("\n## Chapters\n\n" + head)
    for key in ["ch1", "ch2", "ch4"]:
        parts.append(f"| {key} | " + " | ".join(row(lambda c, T: T[key]["title"])) + " |\n")
    parts.append(f"| finder | " + " | ".join(row(lambda c, T: T["finder"]["title"])) + " |\n")
    parts.append("\n## Cover\n\n" + head)
    for key in ["kicker", "h1", "ed"]:
        parts.append(f"| {key} | " + " | ".join(row(lambda c, T: T["cover"][key])) + " |\n")
    (HERE / "glossary.md").write_text("".join(parts), encoding="utf-8")
    print(HERE / "glossary.md")


if __name__ == "__main__":
    build()
