"""Build the Mt. Fuji guide PDF from the English Markdown chapters.

Usage: python3 guides/mt-fuji/build_pdf.py
Output: guides/mt-fuji/dist/mt-fuji-day-trip-guide.pdf
"""
import pathlib
import re
import subprocess

import markdown

HERE = pathlib.Path(__file__).parent
SRC = [HERE / "en" / "01-02_intro-access.md", HERE / "en" / "03-06_spots-courses-food-tips.md"]
DIST = HERE / "dist"
HTML = DIST / "mt-fuji-day-trip-guide.html"
PDF = DIST / "mt-fuji-day-trip-guide.pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

CSS = """
@page { size: A5; margin: 14mm 12mm 16mm 12mm; }
:root { --ink:#1f2933; --muted:#5b6770; --fuji:#1d4e89; --sun:#c8372d; --line:#d9dee3; --soft:#f2f5f8; }
* { box-sizing: border-box; }
body { font-family: "Noto Sans", "Noto Sans CJK JP", sans-serif; color: var(--ink); font-size: 9.6pt; line-height: 1.5; margin: 0; }
.cover { height: 180mm; display: flex; flex-direction: column; justify-content: center; text-align: center; page-break-after: always; }
.cover .mark { width: 120px; margin: 0 auto 18px; }
.cover h1 { font-size: 24pt; line-height: 1.15; color: var(--fuji); margin: 0 0 10px; border: 0; }
.cover .sub { font-size: 11pt; color: var(--muted); margin-bottom: 26px; }
.cover .badge { display: inline-block; margin: 0 auto; padding: 6px 14px; border: 1.5px solid var(--sun); color: var(--sun); border-radius: 20px; font-weight: 700; font-size: 9pt; }
.note { page-break-after: always; }
.note h2 { margin-top: 0; }
.toc ol { padding-left: 18px; }
.toc li { margin: 4px 0; }
h1 { font-size: 15pt; }
h2 { font-size: 15pt; color: var(--fuji); border-bottom: 2px solid var(--fuji); padding-bottom: 4px; margin: 0 0 10px; page-break-before: always; }
h2.first { page-break-before: auto; }
h3 { font-size: 11.5pt; color: var(--sun); margin: 16px 0 6px; page-break-after: avoid; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0; padding-left: 18px; }
li { margin: 3px 0; }
strong { color: #111; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 10px; font-size: 8.6pt; page-break-inside: avoid; }
th { background: var(--fuji); color: #fff; text-align: left; padding: 4px 6px; }
td { border-bottom: 1px solid var(--line); padding: 4px 6px; vertical-align: top; }
tr:nth-child(even) td { background: var(--soft); }
hr { display: none; }
.src { color: var(--muted); font-size: 7.6pt; }
.foot { color: var(--muted); font-size: 8pt; }
"""

FUJI_SVG = """<svg class="mark" viewBox="0 0 120 70" xmlns="http://www.w3.org/2000/svg">
<circle cx="92" cy="18" r="10" fill="#c8372d"/>
<polygon points="10,66 52,14 66,14 110,66" fill="#1d4e89"/>
<polygon points="40,29 52,14 66,14 78,29 70,25 63,31 56,24 48,31" fill="#ffffff"/>
</svg>"""

COVER = f"""<section class="cover">
{FUJI_SVG}
<h1>Mt. Fuji Day Trip Guide<br>from Tokyo</h1>
<div class="sub">Trains, buses, the 8 best places, ready-made itineraries,<br>local food and rainy-day plans</div>
<div><span class="badge">Information checked November 2026</span></div>
</section>"""

NOTE = """<section class="note">
<h2 class="first">Before you start</h2>
<p>Every fare, timetable and opening time in this guide was checked in <strong>November 2026</strong> against official websites or by phone with the operators themselves. Where we use another source, we say so.</p>
<p>Prices and times in Japan do change, often in spring (when timetables are revised) and when tax or fuel costs change. <strong>Before you travel, check the official websites</strong> mentioned in each section, especially for trains, buses and opening days.</p>
<div class="toc"><h3>Contents</h3><ol>
<li>Before You Go</li><li>Getting There from Tokyo</li><li>The 8 Best Places</li>
<li>Ready-Made Itineraries</li><li>Local Food</li><li>Good to Know</li><li>Packing Checklist</li></ol></div>
<p class="foot">This guide is an independent travel guide. It is not affiliated with any of the companies or places it mentions.</p>
</section>"""


def build():
    md_text = "\n\n".join(p.read_text(encoding="utf-8") for p in SRC)
    md_text = re.sub(r"^# .*\n", "", md_text, count=1)
    md_text = md_text.replace("- [ ] ", "- ☐ ")
    # Paragraphs indented under a table would otherwise swallow the list that follows.
    md_text = re.sub(r"\n\n  (?=[A-Z])", "\n\n", md_text)
    # A list right after a paragraph needs a blank line before it.
    md_text = re.sub(r"(\n(?![-\s|#])[^\n]+)\n(- )", r"\1\n\n\2", md_text)
    # Python-Markdown needs 4-space indents for nested lists.
    md_text = re.sub(r"^    - ", "        - ", md_text, flags=re.M)
    md_text = re.sub(r"^  - ", "    - ", md_text, flags=re.M)
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists"])
    # Show source notes in small grey text so the main facts stand out.
    body = re.sub(r"\((?=[^()]*(?:official|Confirmed by phone|confirmed by phone|Google Maps|Google, November))([^()]*(?:\([^()]*\)[^()]*)*)\)",
                  r'<span class="src">(\1)</span>', body)
    body = body.replace("<h2>Extras</h2>", "<h2>Packing Checklist</h2>").replace("<h3>Packing checklist</h3>", "")
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Mt. Fuji Day Trip Guide from Tokyo</title><style>{CSS}</style></head>
<body>{COVER}{NOTE}{body}</body></html>"""
    DIST.mkdir(exist_ok=True)
    HTML.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF}", HTML.as_uri()], check=True, capture_output=True)
    print(PDF)


if __name__ == "__main__":
    build()
