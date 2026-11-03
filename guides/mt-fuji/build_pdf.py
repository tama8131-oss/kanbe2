"""Build the Mt. Fuji guide PDF from the English Markdown chapters.

Usage: python3 guides/mt-fuji/build_pdf.py [--ja]
Output: guides/mt-fuji/dist/mt-fuji-day-trip-guide.pdf
        (--ja: Japanese review copy for checking, mt-fuji-day-trip-guide.ja-review.pdf)
"""
import pathlib
import re
import subprocess
import sys

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
<li>Ready-Made Itineraries</li><li>Local Food</li><li>Good to Know</li><li>Route Diagram</li><li>Packing Checklist</li></ol></div>
<p class="foot">This guide is an independent travel guide. It is not affiliated with any of the companies or places it mentions.</p>
</section>"""


COVER_JA = f"""<section class="cover">
{FUJI_SVG}
<h1>東京から行く<br>富士山日帰りガイド</h1>
<div class="sub">【確認用 日本語版】<br>販売するのは英語版。中身は同じ</div>
<div><span class="badge">2026年11月に確認した情報</span></div>
</section>"""

NOTE_JA = """<section class="note">
<h2 class="first">はじめに</h2>
<p>このガイドの料金・時刻表・営業時間はすべて、<strong>2026年11月</strong>に公式サイトか、運営している会社への電話で確かめたものです。それ以外の情報を使ったところは、そう書いています。</p>
<p>日本の料金や時刻は変わることがあります（特に時刻表が変わる春や、税金・燃料費が変わるとき）。<strong>出かける前に、各章に出てくる公式サイトを見てください。</strong>特に電車・バス・営業日。</p>
<div class="toc"><h3>目次</h3><ol>
<li>出かける前に</li><li>東京からの行き方</li><li>行く価値のある8か所</li>
<li>そのまま使えるモデルコース</li><li>ご当地グルメ</li><li>知っておくと便利なこと</li><li>乗り換え案内図</li><li>持ち物チェックリスト</li></ol></div>
<p class="foot">このガイドは個人が作った旅行ガイドで、出てくる会社や施設とは関係ありません。</p>
</section>"""


MAP_LABELS = {
    "en": dict(
        title="Getting Around: Route Diagram", note="Diagram only. Distances and positions are not to scale. All times are from Chapters 2 and 3.",
        station="Kawaguchiko<br>Station", rail="Fujikyu Railway", red="Red Line", green="Green Line", blue="Blue Line",
        route="Route bus", direct="Direct bus", walk="on foot",
        p1="① Chureito Pagoda", p1b="Shimoyoshida Sta.<br>+ 25 min on foot", p2="② Oishi Park", p2b="about 27 min",
        p3="③ Oshino Hakkai", p3b="A1/A2 or F1/F2", p4="④ Ropeway", p4b="about 11 min or 15 min on foot",
        p5="⑤ Iyashi-no-Sato Nenba", p5b="about 40 min", p6="⑥ 5th Station", p6b="about 1 hour",
        p7="⑦ Fuji-Q Highland", p7b="one stop", p8="⑧ Lake Motosu", p8b="about 1 hour + 1 hour on foot",
        tokyo="To Tokyo (Shinjuku)"),
    "ja": dict(
        title="乗り換え案内図", note="位置や距離は正確ではありません。時間は第2章・第3章の確認済みの情報です。",
        station="河口湖駅", rail="富士急行線", red="レッドライン", green="グリーンライン", blue="ブルーライン",
        route="路線バス", direct="直行バス", walk="徒歩",
        p1="① 五重塔", p1b="下吉田駅＋徒歩25分", p2="② 大石公園", p2b="約27分",
        p3="③ 忍野八海", p3b="A1/A2かF1/F2", p4="④ ロープウェイ", p4b="約11分（徒歩なら約15分）",
        p5="⑤ いやしの里根場", p5b="約40分", p6="⑥ 五合目", p6b="約1時間",
        p7="⑦ 富士急ハイランド", p7b="1駅", p8="⑧ 本栖湖", p8b="約1時間＋徒歩約1時間",
        tokyo="東京（新宿）へ"),
}


def route_map(lang):
    L = MAP_LABELS[lang]
    spokes = [  # (x, y, colour, line label, place, detail)
        (40, 40, "#c8372d", L["red"], L["p4"], L["p4b"]),
        (40, 150, "#c8372d", L["red"], L["p2"], L["p2b"]),
        (40, 260, "#2e8b57", L["green"], L["p5"], L["p5b"]),
        (40, 370, "#1d6fd1", L["blue"], L["p8"], L["p8b"]),
        (330, 40, "#555555", L["rail"], L["p7"], L["p7b"]),
        (330, 150, "#555555", L["rail"], L["p1"], L["p1b"]),
        (330, 260, "#8a5a00", L["route"], L["p3"], L["p3b"]),
        (330, 370, "#8a5a00", L["direct"], L["p6"], L["p6b"]),
    ]
    cx, cy = 260, 230
    parts = []
    for x, y, col, line, place, detail in spokes:
        bx = x + 95
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{bx}" y2="{y+30}" stroke="{col}" stroke-width="5" stroke-linecap="round"/>')
    for x, y, col, line, place, detail in spokes:
        parts.append(f'<rect x="{x}" y="{y}" width="190" height="64" rx="8" fill="#fff" stroke="{col}" stroke-width="2"/>')
        parts.append(f'<rect x="{x}" y="{y}" width="190" height="18" rx="8" fill="{col}"/>')
        parts.append(f'<text x="{x+8}" y="{y+13}" font-size="10" fill="#fff" font-weight="700">{line}</text>')
        parts.append(f'<text x="{x+8}" y="{y+36}" font-size="13" font-weight="700" fill="#1f2933">{place}</text>')
        parts.append(f'<text x="{x+8}" y="{y+54}" font-size="10.5" fill="#5b6770">{detail.replace("<br>", " ")}</text>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="#1d4e89"/>')
    lines = L["station"].split("<br>")
    for k, t in enumerate(lines):
        parts.append(f'<text x="{cx}" y="{cy + 5 + (k - (len(lines)-1)/2)*16}" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">{t}</text>')
    parts.append(f'<text x="{cx}" y="470" font-size="11" fill="#5b6770" text-anchor="middle">⇧ {L["tokyo"]}: Fuji Excursion / Highway bus (Chapter 2)</text>' if lang == "en"
                 else f'<text x="{cx}" y="470" font-size="11" fill="#5b6770" text-anchor="middle">{L["tokyo"]}：富士回遊・高速バス（第2章）</text>')
    svg = f'<svg viewBox="0 0 560 485" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">{"".join(parts)}</svg>'
    return f'<h2>{L["title"]}</h2>{svg}<p class="src">{L["note"]}</p>'


def add_page_numbers(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        if i == 0:
            continue
        r = page.rect
        page.insert_text((r.width / 2 - 6, r.height - 22), str(i + 1), fontsize=8, color=(0.36, 0.4, 0.44))
    tmp = pdf_path.with_suffix(".tmp.pdf")
    doc.save(tmp)
    doc.close()
    tmp.replace(pdf_path)


def build(ja=False):
    src = sorted((HERE / "ja-review").glob("*.ja.md")) if ja else SRC
    md_text = "\n\n".join(p.read_text(encoding="utf-8") for p in src)
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
    if ja:
        body = re.sub(r"（([^（）]*(?:公式|電話で確認|Googleマップ|Googleに載|Googleのメニュー)[^（）]*)）", r'<span class="src">（\1）</span>', body)
    body = re.sub(r"\((?=[^()]*(?:official|Confirmed by phone|confirmed by phone|Google Maps|Google, November))([^()]*(?:\([^()]*\)[^()]*)*)\)",
                  r'<span class="src">(\1)</span>', body)
    body = body.replace("<h2>Extras</h2>", "<h2>Packing Checklist</h2>").replace("<h3>Packing checklist</h3>", "")
    lang, cover, note = ("ja", COVER_JA, NOTE_JA) if ja else ("en", COVER, NOTE)
    checklist = "<h2>持ち物チェックリスト</h2>" if ja else "<h2>Packing Checklist</h2>"
    body = body.replace(checklist, route_map(lang) + checklist)
    css = CSS.replace('"Noto Sans", "Noto Sans CJK JP"', '"Noto Sans CJK JP", "Noto Sans"') if ja else CSS
    html = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<title>Mt. Fuji Day Trip Guide from Tokyo</title><style>{css}</style></head>
<body>{cover}{note}{body}</body></html>"""
    out_html = HTML.with_suffix(".ja-review.html") if ja else HTML
    out_pdf = PDF.with_suffix(".ja-review.pdf") if ja else PDF
    DIST.mkdir(exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", out_html.as_uri()], check=True, capture_output=True)
    add_page_numbers(out_pdf)
    print(out_pdf)


if __name__ == "__main__":
    build(ja="--ja" in sys.argv)
