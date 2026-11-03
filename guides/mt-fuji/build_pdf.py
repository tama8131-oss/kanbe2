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
SRC = [HERE / "en" / "00_know-before.md", HERE / "en" / "01-02_intro-access.md", HERE / "en" / "03-06_spots-courses-food-tips.md"]
DIST = HERE / "dist"
HTML = DIST / "mt-fuji-day-trip-guide.html"
PDF = DIST / "mt-fuji-day-trip-guide.pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

SEIGAIHA = ("data:image/svg+xml;utf8," +
    "<svg xmlns='http://www.w3.org/2000/svg' width='40' height='20' viewBox='0 0 40 20'>"
    "<g fill='none' stroke='%23ffffff' stroke-opacity='0.16' stroke-width='1.2'>"
    "<circle cx='0' cy='20' r='19'/><circle cx='0' cy='20' r='13'/><circle cx='0' cy='20' r='7'/>"
    "<circle cx='40' cy='20' r='19'/><circle cx='40' cy='20' r='13'/><circle cx='40' cy='20' r='7'/>"
    "<circle cx='20' cy='10' r='19'/><circle cx='20' cy='10' r='13'/><circle cx='20' cy='10' r='7'/></g></svg>")
SEIGAIHA_INK = SEIGAIHA.replace("%23ffffff", "%231b2a4a").replace("0.16", "0.22")

CSS = """
@page { size: A5; margin: 15mm 12mm 17mm 12mm; background: #f6efe0;
  @bottom-center { content: counter(page); font-family: "Noto Serif CJK JP", serif; font-size: 8pt; color: #8a7d68; } }
@page :first { margin: 0; background: #1b2a4a; @bottom-center { content: none; } }
:root { --ink:#2b2622; --muted:#7a6e5d; --ai:#1b2a4a; --shu:#b7382b; --gold:#a8842f; --line:#d8ccb4; --soft:#efe5d1; --paper:#f6efe0; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Noto Sans", "Noto Sans CJK JP", sans-serif; color: var(--ink); font-size: 9.3pt; line-height: 1.5; margin: 0; }
h1, h2, h3, .serif { font-family: "Noto Serif CJK JP", serif; }
.cover { width: 148mm; height: 210mm; position: relative; color: #f6efe0; text-align: center; page-break-after: always;
  background-color: #1b2a4a; background-image: url("SEIGAIHA"); background-size: 26px 13px; overflow: hidden; }
.cover .frame { position: absolute; inset: 9mm; border: 1.2px solid #a8842f; }
.cover .frame:after { content: ""; position: absolute; inset: 2mm; border: 0.6px solid rgba(168,132,47,.7); }
.cover .inner { position: absolute; top: 30mm; left: 0; right: 0; }
.cover .eyebrow { font-family: "Noto Serif CJK JP", serif; letter-spacing: .35em; font-size: 9pt; color: #d9c08a; }
.cover .art { width: 112mm; margin: 8mm auto 4mm; display: block; }
.cover h1 { font-size: 23pt; line-height: 1.2; margin: 2mm 0 3mm; color: #fffaf0; font-weight: 700; }
.cover .sub { font-size: 9.5pt; color: #e8dcc2; margin: 0 14mm 7mm; }
.cover .badge { display: inline-block; padding: 5px 14px; border: 1px solid #d9c08a; color: #f3e3b5; font-size: 8.5pt; letter-spacing: .05em; }
.cover .seal { position: absolute; right: 20mm; bottom: 22mm; width: 15mm; height: 15mm; background: #b7382b; color: #fff;
  font-family: "Noto Serif CJK JP", serif; font-size: 10pt; line-height: 1.05; display: flex; align-items: center; justify-content: center;
  text-align: center; border-radius: 2px; transform: rotate(-4deg); writing-mode: vertical-rl; letter-spacing: .05em; }
.note { page-break-after: always; }
.toc ol { padding-left: 20px; columns: 2; column-gap: 14px; font-size: 8.8pt; }
.toc li { margin: 5px 0; border-bottom: 1px dotted var(--line); padding-bottom: 3px; }
.chap { page-break-before: always; display: flex; align-items: stretch; gap: 10px; margin: 0 0 4px; }
.chap.first { page-break-before: auto; }
.chap .kanji { background: var(--shu); color: #fff; font-family: "Noto Serif CJK JP", serif; font-size: 15pt; font-weight: 700;
  writing-mode: vertical-rl; letter-spacing: .12em; padding: 8px 6px; border-radius: 2px; min-height: 22mm; display: flex; align-items: center; }
.chap .t { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; }
.chap .num { font-family: "Noto Serif CJK JP", serif; color: var(--gold); letter-spacing: .2em; font-size: 8.5pt; text-transform: uppercase; }
.chap h2 { font-size: 16pt; color: var(--ai); margin: 2px 0 0; line-height: 1.25; }
.band { height: 9px; margin: 6px 0 12px; background-color: var(--paper); background-image: url("SEIGAIHA_INK"); background-size: 18px 9px;
  border-top: 1.5px solid var(--ai); }
h3.newpage { page-break-before: always; margin-top: 0; }
h3 { font-size: 12pt; color: var(--ai); margin: 16px 0 6px; page-break-after: avoid; padding-left: 9px; border-left: 4px solid var(--shu); }
p { margin: 6px 0; }
ul, ol { margin: 6px 0; padding-left: 18px; }
li { margin: 2px 0; }
li::marker { color: var(--shu); }
strong { color: #1a1612; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 10px; font-size: 8.6pt; background: #fbf7ee; }
tr { break-inside: avoid; }
table.keep { break-inside: avoid; }
table.ess { font-size: 7.9pt; line-height: 1.35; }
table.ess td { padding: 3px 5px; }
thead { display: table-header-group; }
h3 + table, h3 + p + table { break-before: avoid; }
th { background: var(--ai); color: #f6efe0; text-align: left; padding: 4px 6px; font-family: "Noto Serif CJK JP", serif; font-weight: 600; }
td { border-bottom: 1px solid var(--line); padding: 4px 6px; vertical-align: top; }
tr:nth-child(even) td { background: var(--soft); }
hr { display: none; }
.src { color: var(--muted); font-size: 7.6pt; }
.foot { color: var(--muted); font-size: 8pt; }
""".replace("SEIGAIHA_INK", SEIGAIHA_INK).replace("SEIGAIHA", SEIGAIHA)

COVER_ART = """<svg class="art" viewBox="0 0 300 150" xmlns="http://www.w3.org/2000/svg">
<circle cx="222" cy="44" r="24" fill="#b7382b"/>
<path d="M20 140 L128 32 Q150 22 172 32 L280 140 Z" fill="#f6efe0" fill-opacity="0.12"/>
<path d="M40 140 L132 44 Q150 34 168 44 L260 140 Z" fill="#2f4a7a"/>
<path d="M107 70 L132 44 Q150 34 168 44 L193 70 Q182 64 174 74 Q165 62 158 74 Q150 63 142 74 Q134 62 126 74 Q118 64 107 70 Z" fill="#fffaf0"/>
<path d="M0 140 Q40 128 80 140 T160 140 T240 140 T320 140 V150 H0 Z" fill="#a8842f" fill-opacity="0.55"/>
</svg>"""

COVER = f"""<section class="cover"><div class="frame"></div><div class="inner">
<div class="eyebrow">TOKYO · FUJI FIVE LAKES</div>
{COVER_ART}
<h1>Mt. Fuji Day Trip Guide<br>from Tokyo</h1>
<div class="sub">Trains, buses, the 8 best places, ready-made itineraries, local food and rainy-day plans</div>
<div class="badge">Every fare and time checked on official sites and by phone · November 2026</div></div>
<div class="seal">富士</div></section>"""

NOTE = """<section class="note">
<div class="chap first"><div class="kanji">序</div><div class="t"><div class="num">Welcome</div><h2>Before you start</h2></div></div><div class="band"></div>
<p>Every fare, timetable and opening time in this guide was checked in <strong>November 2026</strong> against official websites or by phone with the operators themselves. Where we use another source, we say so.</p>
<p>Prices and times in Japan do change, often in spring (when timetables are revised) and when tax or fuel costs change. <strong>Before you travel, check the official websites</strong> mentioned in each section, especially for trains, buses and opening days.</p>
<h3>From the author</h3>
<p>I made this guide because the information on getting to Mt. Fuji is spread across dozens of Japanese websites, and quick online answers are often out of date or simply wrong. The text was written with the help of AI tools, but I checked every fare, timetable and opening time myself, on official websites and by phone with the railway and bus companies, museums, hot springs and tourist offices, in November 2026. I hope it saves you time and lets you enjoy the mountain. <strong>— Tama</strong></p>
<div class="toc"><h3>Contents</h3><ol><li>Know Before You Go</li>
<li>Before You Go</li><li>Getting There from Tokyo</li><li>The 8 Best Places</li>
<li>Ready-Made Itineraries</li><li>Local Food</li><li>Good to Know (with packing checklist)</li><li>Route Diagram</li></ol></div>
<p class="foot">This guide is an independent travel guide. It is not affiliated with any of the companies or places it mentions.</p>
</section>"""


COVER_JA = f"""<section class="cover"><div class="frame"></div><div class="inner">
<div class="eyebrow">東京 ・ 富士五湖</div>
{COVER_ART}
<h1>東京から行く<br>富士山日帰りガイド</h1>
<div class="sub">【確認用 日本語版】販売するのは英語版。中身は同じ</div>
<div class="badge">料金と時間はすべて公式サイトと電話で確認・2026年11月</div></div>
<div class="seal">富士</div></section>"""

NOTE_JA = """<section class="note">
<div class="chap first"><div class="kanji">序</div><div class="t"><div class="num">はじめに</div><h2>はじめに</h2></div></div><div class="band"></div>
<p>このガイドの料金・時刻表・営業時間はすべて、<strong>2026年11月</strong>に公式サイトか、運営している会社への電話で確かめたものです。それ以外の情報を使ったところは、そう書いています。</p>
<p>日本の料金や時刻は変わることがあります（特に時刻表が変わる春や、税金・燃料費が変わるとき）。<strong>出かける前に、各章に出てくる公式サイトを見てください。</strong>特に電車・バス・営業日。</p>
<h3>作った人より</h3>
<p>富士山への行き方の情報は、たくさんの日本語のサイトにバラバラに載っていて、ネットのかんたんな答えは古かったり、まちがっていたりすることがよくあります。それでこのガイドを作りました。文章はAIの力を借りて書きましたが、料金・時刻表・営業時間はすべて、2026年11月に私自身が公式サイトで確かめ、鉄道やバスの会社、美術館、温泉、観光案内所に電話で確認しました。みなさんの時間の節約になって、富士山を楽しんでもらえたらうれしいです。<strong>― たま</strong></p>
<div class="toc"><h3>目次</h3><ol><li>出かける前に知っておくこと</li>
<li>出かける前に</li><li>東京からの行き方</li><li>行く価値のある8か所</li>
<li>そのまま使えるモデルコース</li><li>ご当地グルメ</li><li>知っておくと便利なこと（持ち物チェックリスト付き）</li><li>乗り換え案内図</li></ol></div>
<p class="foot">このガイドは個人が作った旅行ガイドで、出てくる会社や施設とは関係ありません。</p>
</section>"""


MAP_LABELS = {
    "en": dict(
        title="Getting Around: Route Diagram", note="Diagram only. Distances and positions are not to scale. All times are from Chapters 2 and 3.",
        station="Kawaguchiko<br>Station", rail="Fujikyu Railway", red="Red Line", green="Green Line", blue="Blue Line",
        route="Route bus", direct="Direct bus", walk="on foot",
        p1="① Chureito Pagoda", p1b="Shimoyoshida Sta.<br>+ 25 min on foot", p2="② Oishi Park", p2b="about 27 min",
        p3="③ Oshino Hakkai", p3b="bus for Gotemba or Yamanakako Hirano", p4="④ Ropeway", p4b="about 11 min or 15 min on foot",
        p5="⑤ Iyashi-no-Sato Nenba", p5b="about 40 min", p6="⑥ 5th Station", p6b="about 1 hour",
        p7="⑦ Fuji-Q Highland", p7b="one stop", p8="⑧ Lake Motosu", p8b="about 1 hour + 1 hour on foot",
        tokyo="To Tokyo (Shinjuku)"),
    "ja": dict(
        title="乗り換え案内図", note="位置や距離は正確ではありません。時間は第2章・第3章の確認済みの情報です。",
        station="河口湖駅", rail="富士急行線", red="レッドライン", green="グリーンライン", blue="ブルーライン",
        route="路線バス", direct="直行バス", walk="徒歩",
        p1="① 五重塔", p1b="下吉田駅＋徒歩25分", p2="② 大石公園", p2b="約27分",
        p3="③ 忍野八海", p3b="御殿場行きか山中湖平野行き", p4="④ ロープウェイ", p4b="約11分（徒歩なら約15分）",
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
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="#1b2a4a"/>')
    lines = L["station"].split("<br>")
    for k, t in enumerate(lines):
        parts.append(f'<text x="{cx}" y="{cy + 5 + (k - (len(lines)-1)/2)*16}" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">{t}</text>')
    parts.append(f'<text x="{cx}" y="470" font-size="11" fill="#5b6770" text-anchor="middle">⇧ {L["tokyo"]}: Fuji Excursion / Highway bus (Chapter 2)</text>' if lang == "en"
                 else f'<text x="{cx}" y="470" font-size="11" fill="#5b6770" text-anchor="middle">{L["tokyo"]}：富士回遊・高速バス（第2章）</text>')
    svg = f'<svg viewBox="0 0 560 485" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">{"".join(parts)}</svg>'
    return f'<h2>{L["title"]}</h2>{svg}<p class="src">{L["note"]}</p>'


CHAPTER_KANJI = ["旅支度", "道", "名所", "行程", "味", "心得"]


def decorate_chapters(body, ja):
    def repl(m):
        title = m.group(1)
        if ja:
            mm = re.match(r"第(\d)章\s*(.*)", title)
            num, name = (f"第{mm.group(1)}章", mm.group(2)) if mm else ("", title)
            idx = int(mm.group(1)) - 1 if mm else None
        else:
            mm = re.match(r"Chapter (\d): (.*)", title)
            num, name = (f"Chapter {mm.group(1)}", mm.group(2)) if mm else ("", title)
            idx = int(mm.group(1)) - 1 if mm else None
        if idx is not None:
            kanji = CHAPTER_KANJI[idx]
        elif title in ("Know Before You Go", "出かける前に知っておくこと"):
            kanji, num = "要点", ("Essentials" if not ja else "まずはここ")
        elif title in ("Packing Checklist", "持ち物チェックリスト"):
            kanji, num = "持物", ("Extras" if not ja else "おまけ")
        else:
            kanji, num = "地図", ("Extras" if not ja else "おまけ")
        return f'<div class="chap"><div class="kanji">{kanji}</div><div class="t"><div class="num">{num}</div><h2>{name}</h2></div></div><div class="band"></div>'
    return re.sub(r"<h2>(.*?)</h2>", repl, body)


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
    md_text = re.sub(r"^# .*\n", "", md_text, count=1, flags=re.M)
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
    
    lang, cover, note = ("ja", COVER_JA, NOTE_JA) if ja else ("en", COVER, NOTE)
    body = body + route_map(lang)
    body = decorate_chapters(body, ja)
    # Short tables stay on one page; long ones may continue on the next page.
    body = re.sub(r"<table>(.*?)</table>", lambda m: ('<table class="keep">' if m.group(1).count("<tr>") <= 9 and not re.search(r"<th>(Time|時間)</th>", m.group(1)) else "<table>") + m.group(1) + "</table>",
                  body, flags=re.S)
    # The essentials table is long: use a smaller font so it fits on one page.
    for t in ("Know Before You Go</h2>", "出かける前に知っておくこと</h2>"):
        i = body.find(t)
        if i >= 0:
            j = body.find("<table", i)
            body = body[:j] + '<table class="ess"' + body[j + len("<table"):]
    # Keep the "when can you see Mt. Fuji" heading, text and table together on one page.
    for h in ("<h3>When can you actually see Mt. Fuji?</h3>", "<h3>富士山はいつ見えるの？</h3>"):
        body = body.replace(h, h.replace("<h3>", '<h3 class="newpage">'))
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
    print(out_pdf)


if __name__ == "__main__":
    build(ja="--ja" in sys.argv)
