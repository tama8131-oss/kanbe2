"""Build the Mt. Fuji guide PDF from the Markdown chapters.

Usage: python3 guides/mt-fuji/build_pdf.py [--ja]
Output: guides/mt-fuji/dist/mt-fuji-day-trip-guide.pdf (one book: language menu, then
        English, Simplified Chinese, Traditional Chinese and Korean sections)
        (--ja: Japanese review copy for checking, mt-fuji-day-trip-guide.ja-review.pdf)
"""
import pathlib
import re
import subprocess
import sys

import markdown
import segno

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from links import BOOKING, PLACES, maps_url  # noqa: E402
import i18n  # noqa: E402
import photos as ph  # noqa: E402
import chart  # noqa: E402

HERE = pathlib.Path(__file__).parent
SRC = [HERE / "en" / "00_know-before.md", HERE / "en" / "01-02_intro-access.md", HERE / "en" / "03-06_spots-courses-food-tips.md"]
DIST = HERE / "dist"
HTML = DIST / "mt-fuji-day-trip-guide.html"
PDF = DIST / "mt-fuji-day-trip-guide.pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

CSS = """
@page { size: A5; margin: 14mm 12mm 16mm 12mm; background: #f7f3ec;
  @bottom-left { content: "FOOTER_LABEL"; font-family: "Noto Serif CJK JP", serif; font-size: 6.5pt; letter-spacing: .22em; color: #9a8f80; }
  @bottom-right { content: counter(page, decimal-leading-zero); font-family: "Noto Serif CJK JP", serif; font-size: 7pt; color: #9a8f80; } }
@page cover { margin: 0; @bottom-left { content: none; } @bottom-right { content: none; } }
:root { --ink:#26231f; --muted:#7d7466; --red:#c0392b; --navy:#2c3e5c; --line:#e3dccf; --card:#fffdf8; --soft:#f1ebe0; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Noto Sans", "Noto Sans CJK JP", sans-serif; color: var(--ink); font-size: 8.8pt; line-height: 1.5; margin: 0; }
h1, h2, h3, .serif { font-family: "Noto Serif CJK JP", serif; }
a { color: var(--navy); text-decoration: none; border-bottom: 1px dotted var(--navy); }

/* cover */
.coverslot { page: cover; break-before: page; break-after: page; height: 20px; }
body > .coverslot:first-child, section > .coverslot:first-child { break-before: auto; }
.cmark { font-size: 3px; color: #f7f3ec; }
.cover { page: cover; width: 148mm; height: 210mm; position: relative; overflow: hidden; page-break-before: always; page-break-after: always; color: #fff; }
body > .cover:first-child { page-break-before: auto; }
.cover .langs { position: absolute; left: 10mm; right: 10mm; top: 26mm; font-size: 8pt; letter-spacing: .04em; text-shadow: 0 1px 4px rgba(0,0,0,.4); }
section.L-zh-hans { font-family: "Noto Sans CJK SC", sans-serif; }
section.L-zh-hans h1, section.L-zh-hans h2, section.L-zh-hans h3, section.L-zh-hans .serif { font-family: "Noto Serif CJK SC", serif; }
section.L-zh-hant { font-family: "Noto Sans CJK TC", sans-serif; }
section.L-zh-hant h1, section.L-zh-hant h2, section.L-zh-hant h3, section.L-zh-hant .serif { font-family: "Noto Serif CJK TC", serif; }
section.L-th { font-family: "Noto Sans Thai", "Noto Sans", sans-serif; }
section.L-th h1, section.L-th h2, section.L-th h3, section.L-th .serif { font-family: "Noto Serif Thai", "Noto Serif", serif; }
section.L-vi h1, section.L-vi h2, section.L-vi h3, section.L-vi .serif, section.L-ms h1, section.L-ms h2, section.L-ms h3 { font-family: "Noto Serif", serif; }
section.L-ms, section.L-th { font-size: 8.6pt; }
section.L-ko { font-family: "Noto Sans CJK KR", sans-serif; }
section.L-ko h1, section.L-ko h2, section.L-ko h3, section.L-ko .serif { font-family: "Noto Serif CJK KR", serif; }
.picker { page-break-before: always; page-break-after: always; }
.picker h2 { font-size: 18pt; margin: 4mm 0 1mm; }
.picker .sub { color: var(--muted); font-size: 8.5pt; margin-bottom: 6mm; }
.picker a.lang { display: flex; align-items: center; gap: 10px; border: 1.5px solid var(--line); background: var(--card); border-radius: 14px;
  padding: 8px 12px; margin: 0 0 6px; color: var(--ink); text-decoration: none; }
.picker .flag { font-size: 12.5pt; line-height: 1; font-family: "Noto Color Emoji"; width: 150px; flex: none; text-align: center; letter-spacing: 0; white-space: nowrap; }
.picker .nm { font-size: 13pt; font-weight: 700; flex: 1; }
.picker .go { color: var(--red); font-weight: 700; font-size: 9pt; }
a.change { display: inline-block; margin-top: 4px; font-size: 8pt; }
.cover svg.bg { position: absolute; inset: 0; width: 100%; height: 100%; }
.cover .top { position: absolute; top: 10mm; left: 10mm; right: 10mm; display: flex; justify-content: space-between;
  font-family: "Noto Serif CJK JP", serif; font-size: 7pt; letter-spacing: .3em; color: #fff; }
.cover .tag { position: absolute; top: 17mm; left: 10mm; background: rgba(38,35,31,.55); padding: 2px 7px; font-size: 6.5pt; letter-spacing: .05em; }
.cover .titles { position: absolute; left: 10mm; right: 10mm; bottom: 31mm; }
.cover .big { font-family: "Noto Serif CJK JP", serif; font-size: 22pt; line-height: 1; font-weight: 300; letter-spacing: .06em; text-shadow: 0 2px 8px rgba(0,0,0,.35); margin-bottom: 2mm; }
.cover .kicker { font-weight: 800; font-size: 15pt; line-height: 1.25; text-shadow: 0 1px 6px rgba(0,0,0,.55); }
.cover h1 { font-size: 20pt; line-height: 1.28; margin: 1.5mm 0 2.5mm; text-shadow: 0 1px 8px rgba(0,0,0,.55); }
.cover .ed { display: inline-block; background: var(--red); color: #fff; font-weight: 700; font-size: 10pt; padding: 3px 10px; border-radius: 2px; letter-spacing: .04em; }
.cover .stats { position: absolute; left: 10mm; right: 10mm; bottom: 10mm; display: grid; grid-template-columns: 1fr 1fr 1fr 1.6fr;
  border-top: 1px solid rgba(255,255,255,.7); padding-top: 3mm; }
.cover .stats b { display: block; font-family: "Noto Serif CJK JP", serif; font-size: 14pt; font-weight: 400; }
.cover .stats span { font-size: 6.5pt; letter-spacing: .03em; }

/* photos */
img.bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.shade { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,.30), rgba(0,0,0,0) 32%, rgba(0,0,0,.05) 55%, rgba(0,0,0,.62)); }
.place { position: relative; height: 36mm; border-radius: 10px; overflow: hidden; margin: 14px 0 8px; color: #fff; break-inside: avoid; break-after: avoid; }
.place.course { height: 25mm; }
.place.small { height: 22mm; }
.place .ph { position: absolute; inset: 0; display: flex; gap: 2px; }
.place .ph img { flex: 1; min-width: 0; height: 100%; object-fit: cover; }
.place .pn { position: absolute; left: 9px; bottom: 5px; font-family: "Noto Serif CJK JP", serif; font-size: 30pt; line-height: 1; font-weight: 300; }
.place h3 { position: absolute; left: 9px; right: 9px; bottom: 7px; margin: 0; color: #fff; font-size: 13pt; line-height: 1.25; text-shadow: 0 1px 6px rgba(0,0,0,.5); }
.place .pn + h3 { left: 52px; }
.place h3::after { background: #fff; }
.place a.nav { position: absolute; right: 7px; top: 7px; background: #fff; border-radius: 6px; padding: 3px 3px 1px; border: 0; text-align: center; line-height: 1; }
.place a.nav img { width: 15mm; height: 15mm; display: block; }
.place a.nav span { font-size: 5.5pt; font-weight: 700; letter-spacing: .15em; color: var(--red); }
.credits { page-break-before: always; }
.credits table { font-size: 7.6pt; }
.credits td { padding: 3px 6px; }

/* chapter opener */
.opener { page-break-before: always; margin: -14mm -12mm 6mm -12mm; height: 48mm; position: relative; overflow: hidden; color: #fff; }
.opener.first { page-break-before: auto; }
.opener .ph { position: absolute; inset: 0; display: flex; gap: 2px; }
.opener .ph img { flex: 1; min-width: 0; height: 100%; object-fit: cover; }
.opener .lbl { position: absolute; left: 12mm; bottom: 19mm; font-family: "Noto Serif CJK JP", serif; font-size: 7pt; letter-spacing: .35em; }
.opener .num { position: absolute; left: 11mm; bottom: 8mm; font-family: "Noto Serif CJK JP", serif; font-size: 34pt; line-height: 1; font-weight: 300; }
.opener h2 { position: absolute; left: 36mm; bottom: 8mm; right: 10mm; margin: 0; font-size: 17pt; line-height: 1.2; text-shadow: 0 1px 6px rgba(0,0,0,.35); }
.opener.nonum h2 { left: 12mm; }
.eyebrow { font-family: "Noto Serif CJK JP", serif; font-style: italic; color: var(--red); font-size: 8.5pt; margin: 0; }
h3 { font-size: 12.5pt; color: var(--ink); margin: 15px 0 6px; page-break-after: avoid; }
h3::after { content: ""; display: block; width: 18px; height: 2px; background: var(--red); margin-top: 4px; }
h3.newpage { page-break-before: always; margin-top: 0; }
.keepnext { break-inside: avoid; }
p { margin: 5px 0; }
ul, ol { margin: 5px 0; padding-left: 16px; }
li { margin: 2px 0; }
li::marker { color: var(--red); }
strong { color: #111; }
table { width: 100%; border-collapse: separate; border-spacing: 0; margin: 8px 0 10px; font-size: 8.4pt; background: var(--card);
  border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
tr { break-inside: avoid; }
table.keep { break-inside: avoid; }
table.ess { font-size: 7.7pt; line-height: 1.35; }
table.ess td { padding: 3px 6px; }
thead { display: table-header-group; }
th { background: var(--ink); color: #fff; text-align: left; padding: 5px 7px; font-weight: 600; font-size: 7.8pt; letter-spacing: .02em; }
td { border-bottom: 1px solid var(--line); padding: 5px 7px; vertical-align: top; }
tr:last-child td { border-bottom: 0; }
hr { display: none; }
.src { color: var(--muted); font-size: 7.2pt; }
.foot { color: var(--muted); font-size: 7.5pt; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 8px 10px; margin: 8px 0; }
.alert { background: #f6dcd6; border-radius: 10px; padding: 8px 10px; margin: 8px 0; font-size: 8.4pt; }
.toc ol { padding-left: 0; list-style: none; counter-reset: c; margin: 0; }
.toc ol { columns: 2; column-gap: 12px; }
.toc li { counter-increment: c; display: flex; gap: 8px; align-items: baseline; border-bottom: 1px solid var(--line); padding: 3px 0; margin: 0; font-size: 8.2pt; break-inside: avoid; }
.toc li::before { content: counter(c); font-family: "Noto Serif CJK JP", serif; color: var(--red); font-size: 13pt; width: 16px; }
.note { page-break-after: always; }

/* course finder */
.finder { font-size: 8.2pt; display: grid; grid-template-columns: 1fr 22px 1fr; gap: 0 0; align-items: stretch; margin-top: 6px; }
.q { background: var(--ink); color: #fff; border-radius: 10px; padding: 6px 9px; font-size: 8.2pt; line-height: 1.4; }
.q b { display: block; font-family: "Noto Serif CJK JP", serif; font-size: 7pt; letter-spacing: .2em; color: #e8b3aa; }
.arrow { display: flex; align-items: center; justify-content: center; color: var(--red); font-weight: 700; font-size: 7pt; writing-mode: vertical-rl; }
.res { border-radius: 10px; padding: 6px 9px; font-size: 7.9pt; line-height: 1.4; border: 1.5px solid var(--red); background: var(--card); }
.res .t { font-family: "Noto Serif CJK JP", serif; font-weight: 700; font-size: 10pt; color: var(--red); }
.down { grid-column: 1; text-align: center; color: var(--muted); font-size: 7pt; padding: 1px 0; font-weight: 700; }
.gap { grid-column: 2 / 4; }
.tips { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }
.tips .card { margin: 0; font-size: 7.6pt; padding: 5px 8px; line-height: 1.4; }

/* QR pages */
.qrgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.qr { display: flex; gap: 8px; align-items: center; background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 6px 8px; break-inside: avoid; }
.qr img { width: 17mm; height: 17mm; flex: none; }
.qr .n { font-weight: 700; font-size: 8.4pt; line-height: 1.3; }
.qr .d { font-size: 7.2pt; color: var(--muted); line-height: 1.35; }
.qr .u { font-size: 6.4pt; color: var(--navy); word-break: break-all; line-height: 1.25; margin-top: 2px; }
.check { background: #fff3c4; border: 1px solid #e0c34a; border-radius: 8px; padding: 6px 8px; font-size: 8pt; margin: 6px 0; }
""".replace("FOOTER_LABEL", "MT. FUJI GUIDE  ·  NOVEMBER 2026") + chart.CSS

PALETTES = [  # sky top, sky bottom, mountain, lake
    ("#8fb4d6", "#f2d9c4", "#4d6488", "#6f8fb3"),
    ("#e9a77a", "#f6dcc0", "#5a4e6e", "#9b7f86"),
    ("#7fb0cf", "#e4eef2", "#3e5878", "#5d86a8"),
    ("#2e4466", "#c97b5d", "#26324a", "#4a5b7a"),
    ("#a9c6b8", "#f1ead8", "#4f6a5d", "#7f9e93"),
    ("#c7b6d6", "#f5e8df", "#5b5677", "#8d88a6"),
    ("#9fc0de", "#fbefe0", "#465c80", "#7894b8"),
]


def scene(pal, pagoda=False, sun=True):
    top, bottom, mtn, lake = pal
    pg = ""
    if pagoda:
        roofs = "".join(
            f'<path d="M{455-w} {y} Q470 {y-14} {485+w} {y} L{478+w*0.7} {y+6} L{462-w*0.7} {y+6} Z" fill="#b8382c"/>'
            f'<rect x="{462-w*0.6+6}" y="{y+6}" width="{w*1.2+4}" height="18" fill="#d9462f"/>'
            for y, w in [(150, 34), (190, 30), (230, 27), (270, 24), (310, 21)])
        pg = f'<rect x="466" y="96" width="8" height="60" fill="#3b2b25"/>{roofs}'
    return f"""<svg viewBox="0 0 600 420" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0.45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.45"/></linearGradient></defs>
<rect width="600" height="420" fill="url(#sky)"/>
{'<circle cx="455" cy="95" r="34" fill="#fff4e0" fill-opacity="0.85"/>' if sun else ''}
<path d="M-20 300 L230 92 Q262 70 294 92 L560 300 Z" fill="{mtn}"/>
<path d="M186 130 L230 92 Q262 70 294 92 L338 130 Q320 120 306 138 Q290 116 278 140 Q262 118 248 140 Q234 120 220 138 Q204 120 186 130 Z" fill="#fbfbfb"/>
<path d="M0 300 Q150 284 300 300 T600 300 V420 H0 Z" fill="{lake}"/>
<path d="M0 312 Q150 300 300 312 T600 312" stroke="#fff" stroke-opacity=".35" stroke-width="2" fill="none"/>
<path d="M0 352 Q60 300 120 340 Q170 290 230 345 L230 420 H0 Z" fill="#26322b" fill-opacity=".75"/>
{pg}
<rect width="600" height="420" fill="url(#fade)"/></svg>"""


def qr_img(url):
    return segno.make(url, error="m").svg_data_uri(scale=4, border=1, dark="#26231f")


TEXT = {
    "en": dict(
        top_l="DAY TRIP FROM TOKYO", top_r="2026 EDITION", tag="",
        kicker="First time? No worries!", big="Mt. Fuji",
        h1="The Complete Yamanashi / Mt. Fuji Area Guide Map", ed="Latest Edition: November 2026",
        stats=[("8", "places worth your time"), ("3", "ready-made courses"), ("2h", "from Shinjuku"), ("11.2026", "every fare &amp; time checked by phone &amp; official sites")],
        title="First Time? No Worries! The Complete Yamanashi / Mt. Fuji Area Guide Map (Latest Edition: November 2026)",
        welcome="Welcome", before="Before you start",
        p1="Every fare, timetable and opening time in this guide was checked in <strong>November 2026</strong> against official websites or by phone with the operators themselves. Where we use another source, we say so.",
        alert="Prices and times in Japan do change, often in spring (when timetables are revised). <strong>Before you travel, check the official websites</strong> (QR codes in the Book &amp; Navigate section), especially for trains, buses and opening days.",
        author_h="From the author",
        author="I made this guide because the information on getting to Mt. Fuji is spread across dozens of Japanese websites, and quick online answers are often out of date or simply wrong. The text was written with the help of AI tools, but I checked every fare, timetable and opening time myself, on official websites and by phone with the railway and bus companies, museums, hot springs and tourist offices, in November 2026. I hope it saves you time and lets you enjoy the mountain. <strong>— Tama</strong>",
        contents="Contents",
        toc=["Know Before You Go", "Find Your Course", "Before You Go", "Getting There from Tokyo", "The 8 Best Places",
             "Ready-Made Itineraries", "Local Food", "Good to Know (with packing checklist)", "Book &amp; Navigate (QR codes)", "Route Diagram"],
        disclaimer="This guide is an independent travel guide. It is not affiliated with any of the companies or places it mentions.",
    ),
    "ja": dict(
        top_l="DAY TRIP FROM TOKYO", top_r="2026 EDITION", tag="確認用 日本語版｜販売は英語版（中身は同じ）",
        kicker="初めての人でも安心！", big="Mt. Fuji",
        h1="山梨／富士山周辺のガイドマップ完全版", ed="11月最新版（2026年）",
        stats=[("8", "行く価値のある場所"), ("3", "モデルコース"), ("2h", "新宿から"), ("11.2026", "料金・時間はすべて電話と公式サイトで確認")],
        title="初めての人でも安心！山梨/富士山周辺のガイドマップ完全版（11月最新版）",
        welcome="Welcome", before="はじめに",
        p1="このガイドの料金・時刻表・営業時間はすべて、<strong>2026年11月</strong>に公式サイトか、運営している会社への電話で確かめたものです。それ以外の情報を使ったところは、そう書いています。",
        alert="日本の料金や時刻は変わることがあります（特に時刻表が変わる春）。<strong>出かける前に公式サイトを見てください</strong>（「予約とナビ」のQRコードから開けます）。特に電車・バス・営業日。",
        author_h="作った人より",
        author="富士山への行き方の情報は、たくさんの日本語のサイトにバラバラに載っていて、ネットのかんたんな答えは古かったり、まちがっていたりすることがよくあります。それでこのガイドを作りました。文章はAIの力を借りて書きましたが、料金・時刻表・営業時間はすべて、2026年11月に私自身が公式サイトで確かめ、鉄道やバスの会社、美術館、温泉、観光案内所に電話で確認しました。みなさんの時間の節約になって、富士山を楽しんでもらえたらうれしいです。<strong>― たま</strong>",
        contents="目次",
        toc=["出かける前に知っておくこと", "あなたに合うコース診断", "出かける前に", "東京からの行き方", "行く価値のある8か所",
             "そのまま使えるモデルコース", "ご当地グルメ", "知っておくと便利なこと（持ち物チェックリスト付き）", "予約とナビ（QRコード）", "乗り換え案内図"],
        disclaimer="このガイドは個人が作った旅行ガイドで、出てくる会社や施設とは関係ありません。",
    ),
}


def cover(lang, anchor=""):
    T = TEXT[lang]
    stats = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in T["stats"])
    tag = f'<div class="tag">{T["tag"]}</div>' if T.get("tag") else ""
    ident = f' id="{anchor}"' if anchor else ""
    # Covers are printed on their own (full-bleed, no margins) and laid over these blank slot pages after printing,
    # because a 148mm-wide cover inside the normal 124mm text width makes Chrome shrink every page.
    COVERS.append((lang, cover_html(T, stats, tag)))
    return f'<section class="coverslot"{ident}><span class="cmark">COVERSLOT</span></section>'


COVERS = []


def cover_html(T, stats, tag):
    return f"""<section class="cover"><img class="bg" src="{ph.src('cover')}"><div class="shade"></div>
<div class="top"><span>DAY TRIP FROM TOKYO</span><span>2026 EDITION</span></div>{tag}
<div class="titles"><div class="big">{T["big"]}</div><div class="kicker">{T["kicker"]}</div>
<h1>{T["h1"]}</h1><div class="ed">{T["ed"]}</div></div>
<div class="stats">{stats}</div></section>"""


def note(lang):
    T = TEXT[lang]
    change = f'<p><a class="change" href="#languages">{T["change"]}</a></p>' if T.get("change") else ""
    toc = "".join(f"<li>{t}</li>" for t in T["toc"])
    return f"""<section class="note"><p class="eyebrow">{T["welcome"]}</p>
<h3 style="font-size:16pt;margin-top:2px">{T["before"]}</h3>
<p>{T["p1"]}</p><div class="alert">{T["alert"]}</div>
<h3>{T["author_h"]}</h3><p>{T["author"]}</p>
<div class="toc"><h3>{T["contents"]}</h3><ol>{toc}</ol></div>
<p class="foot">{T["disclaimer"]}</p>{change}</section>"""


FINDER = {
    "en": dict(
        title="Find Your Course", lead="Answer the questions from the top. Each answer points you to one of the three ready-made courses in Chapter 4.",
        q=["Open a live camera the night before (Chapter 1). <strong>Is Mt. Fuji visible, and will it be dry?</strong>",
           "<strong>Is the famous red pagoda photo a must</strong>, and can you take the 7:30 Fuji Excursion from Shinjuku?",
           "<strong>First visit?</strong> Want an easy day using only one sightseeing bus line?"],
        yes="YES", no="NO",
        r=[("Course C · Rainy Day", "Museums, hoto noodles and a day-trip hot spring. Works even when Mt. Fuji is hidden."),
           ("Course B · Photo Lover's Day", "Chureito Pagoda before the crowds, Oishi Park and the thatched village of Nenba. Buy the 1-Day Pass."),
           ("Course A · Relaxed Day", "Ropeway, hoto lunch and Oishi Park on the Red Line. Pay single fares; no pass needed."),
           ("Build your own", "Pick from Chapter 3: add Oshino Hakkai (bus from Kawaguchiko) or Lake Motosu (needs about 3 hours).")],
        no_note="if NO", tips=[
            ("Have a tattoo?", "For a hot spring, choose Royal Hotel Kawaguchiko (tattoos OK)."),
            ("June to August?", "Mt. Fuji is often hidden. Keep Course C ready as a backup."),
            ("Japan Rail Pass?", "It covers Shinjuku–Otsuki only. See Chapter 2."),
            ("Big suitcase?", "Leave it in a locker outside Kawaguchiko Station's ticket gates.")]),
    "ja": dict(
        title="あなたに合うコース診断", lead="上から順に答えてください。答えによって、第4章の3つのモデルコースのどれが合うかがわかります。",
        q=["前の晩にライブカメラを見る（第1章）。<strong>富士山は見えそう？雨は降らない？</strong>",
           "<strong>赤い五重塔の有名な写真は絶対に撮りたい？</strong> 新宿7:30発の富士回遊に乗れる？",
           "<strong>はじめての富士山？</strong> 周遊バス1路線だけの、のんびりした1日がいい？"],
        yes="YES", no="NO",
        r=[("コースC・雨の日", "美術館・ほうとう・日帰り温泉。富士山が隠れていても楽しめる。"),
           ("コースB・写真好きの1日", "混む前の五重塔、大石公園、かやぶきの里・根場。周遊バスは1日券を買う。"),
           ("コースA・のんびり1日", "レッドラインでロープウェイ・ほうとう・大石公園。1日券はいらない。"),
           ("自分で組み立てる", "第3章から選ぶ。忍野八海（河口湖駅からバス）や本栖湖（約3時間かかる）を足す。")],
        no_note="NOなら", tips=[
            ("タトゥーがある？", "温泉はロイヤルホテル河口湖（タトゥーOK）へ。"),
            ("6〜8月に行く？", "富士山は隠れがち。コースCも用意しておく。"),
            ("JRパスを持ってる？", "使えるのは新宿〜大月だけ。第2章へ。"),
            ("大きなスーツケース？", "河口湖駅の改札を出てすぐのロッカーへ。")]),
}


def opener(label, num, title, pal_i, first=False):
    n = f'<div class="num">{num}</div>' if num else ""
    cls = "opener" + (" first" if first else "") + ("" if num else " nonum")
    key = ph.OPENER[int(num)] if num else next(v for k, v in ph.OPENER.items() if isinstance(k, str) and k in label)
    keys = key if isinstance(key, list) else [key]
    imgs = "".join(f'<img src="{ph.src(k)}">' for k in keys)
    return (f'<div class="{cls}"><div class="ph">{imgs}</div><div class="shade"></div>'
            f'<div class="lbl">{label}</div>{n}<h2>{title}</h2></div>')


def photo_banner(keys, num, title, cls=""):
    imgs = "".join(f'<img src="{ph.src(k)}">' for k in keys)
    n = f'<div class="pn">{num:02d}</div>' if num else ""
    nav = ""
    if num:  # Google Maps directions to this place: scan the QR or tap it.
        url = maps_url(PLACES[num + 1][3])
        nav = f'<a class="nav" href="{url}"><img src="{qr_img(url)}"><span>NAVI</span></a>'
    return f'<div class="place{cls}"><div class="ph n{len(keys)}">{imgs}</div><div class="shade"></div>{n}<h3>{title}</h3>{nav}</div>'


def add_photos(body):
    """Photo headers for the 8 places (Ch3), the 3 courses (Ch4) and Yoshida udon (Ch5)."""
    parts = re.split(r'(?=<div class="opener)', body)
    for i, part in enumerate(parts):
        m = re.search(r'<div class="num">0(\d)</div>', part[:600])
        if not m or m.group(1) not in "2345":
            continue
        ch, k = int(m.group(1)), [0]

        def repl(mm):
            j = k[0]; k[0] += 1
            title = mm.group(1)
            if ch == 3 and j < 8:
                return photo_banner([ph.PLACES[j]], j + 1, re.sub(r"^(\d\.|[①-⑧])\s*", "", title))
            if ch == 4 and j < 3:
                return photo_banner(ph.COURSES[j], 0, title, " course")
            if ch == 2 and j < 2 and ph.CH2[j]:
                return photo_banner([ph.CH2[j]], 0, title, " small")
            if ch == 5 and j < 2 and ph.FOOD[j]:
                return photo_banner([ph.FOOD[j]], 0, title, " small")
            return mm.group(0)
        parts[i] = re.sub(r"<h3>([^<]*)</h3>", repl, part)
    return "".join(parts)


def credits():
    rows = "".join(f"<tr><td>{u}</td><td>{a}</td><td>{l}</td></tr>" for f, a, l, u, _ in ph.PHOTOS.values())
    return ('<section class="credits"><p class="eyebrow">Credits</p><h3 style="font-size:15pt;margin-top:2px">Photo credits</h3>'
            '<p>Photos from Wikimedia Commons, used under the licences shown (CC0 = no rights reserved; '
            'CC BY / CC BY-SA: creativecommons.org/licenses). Some photos are cropped to fit the page.</p>'
            f'<table class="keep"><thead><tr><th>Used for</th><th>Photographer</th><th>Licence</th></tr></thead><tbody>{rows}</tbody></table>'
            '<p class="foot">This is an independent travel guide. It is not connected with any company or place in it. '
            'Prices, times and opening hours were checked in November 2026. Please check the official websites before you go.</p></section>')


def finder(lang):
    F = FINDER[lang]
    rows = ""
    for i, q in enumerate(F["q"]):
        # Q1: NO -> rainy (C); YES -> next question.  Q2: YES -> B.  Q3: YES -> A, NO -> build your own.
        if i == 0:
            rows += (f'<div class="q"><b>Q1</b>{q}</div><div class="arrow">{F["no"]} →</div>'
                     f'<div class="res"><div class="t">{F["r"][0][0]}</div>{F["r"][0][1]}</div>'
                     f'<div class="down">↓ {F["yes"]}</div><div class="gap"></div>')
        elif i == 1:
            rows += (f'<div class="q"><b>Q2</b>{q}</div><div class="arrow">{F["yes"]} →</div>'
                     f'<div class="res"><div class="t">{F["r"][1][0]}</div>{F["r"][1][1]}</div>'
                     f'<div class="down">↓ {F["no"]}</div><div class="gap"></div>')
        else:
            rows += (f'<div class="q"><b>Q3</b>{q}</div><div class="arrow">{F["yes"]} →</div>'
                     f'<div class="res"><div class="t">{F["r"][2][0]}</div>{F["r"][2][1]}</div>'
                     f'<div class="down">↓ {F["no"]}</div><div class="gap"></div>'
                     f'<div class="res" style="grid-column:1 / 4;border-style:dashed"><div class="t">{F["r"][3][0]}</div>{F["r"][3][1]}</div>')
    tips = "".join(f'<div class="card"><strong>{a}</strong><br>{b}</div>' for a, b in F["tips"])
    return (opener("COURSE FINDER", "", F["title"], 4) + f'<p>{F["lead"]}</p><div class="finder">{rows}</div>'
            f'<div class="tips">{tips}</div>')


def book_and_nav(lang):
    if lang not in ("en", "ja"):
        B = i18n.BN[lang]
        names = i18n.BOOK_NAMES[lang]
        book = "".join(
            f'<div class="qr"><img src="{qr_img(url)}"><div><div class="n">{names[key][0]}</div>'
            f'<div class="d">{names[key][1]}</div><div class="u"><a href="{url}">{url.replace("https://", "")}</a></div></div></div>'
            for key, _, _, _, _, url, _ in BOOKING)
        nav = "".join(
            f'<div class="qr"><img src="{qr_img(maps_url(q))}"><div><div class="n">{m} {nm}</div>'
            f'<div class="u"><a href="{maps_url(q)}">{B["open"]}</a></div></div></div>'
            for (m, _, _, q), nm in zip(PLACES, i18n.PLACE_NAMES[lang]))
        return (opener("BOOK &amp; NAVIGATE", "", B["title"], 6) +
                f'<h3>{B["h_book"]}</h3><p>{B["lead_book"]}</p><div class="qrgrid">{book}</div><p class="src">{B["fc"]}</p>'
                f'<h3 class="newpage">{B["h_nav"]}</h3><p>{B["lead_nav"]}</p><div class="qrgrid">{nav}</div>')
    ja = lang == "ja"
    title = "予約とナビ（QRコード）" if ja else "Book &amp; Navigate"
    h_book = "チケットの予約・公式サイト" if ja else "Tickets &amp; official websites"
    h_nav = "ナビ：今いる場所から行き方を見る" if ja else "Navigation: directions from where you are"
    lead_book = ("スマホのカメラでQRコードを読むと、そのページが開きます。PDFの中の文字をタップしても開けます。"
                 if ja else "Scan a QR code with your phone camera to open the page. In the PDF you can also tap the link.")
    lead_nav = ("Googleマップが開き、今いる場所から電車・バスでの行き方が表示されます。"
                if ja else "Opens Google Maps with public-transport directions from where you are now.")
    check = ('<div class="check">【たまさんへ・確認用】リンク先はまだ確認していません。1つずつ読みこんで、正しい公式ページが開くか確かめてください。'
             '高速バスの「FUJIYAMA CONNECT」はアドレスがわからなかったので入れていません。</div>' if ja else "")
    book = "".join(
        f'<div class="qr"><img src="{qr_img(url)}"><div><div class="n">{nj if ja else ne}</div>'
        f'<div class="d">{dj if ja else de}</div><div class="u"><a href="{url}">{url.replace("https://", "")}</a></div></div></div>'
        for _, ne, nj, de, dj, url, _ in BOOKING)
    fc = ('<p class="src">高速バスの予約はFUJIYAMA CONNECTでもできます（「FUJIYAMA CONNECT」で検索）。</p>' if ja else
          '<p class="src">Highway buses can also be booked on FUJIYAMA CONNECT, Fujikyu\'s own booking site (search "FUJIYAMA CONNECT").</p>')
    nav = "".join(
        f'<div class="qr"><img src="{qr_img(maps_url(q))}"><div><div class="n">{m} {nj if ja else ne}</div>'
        f'<div class="u"><a href="{maps_url(q)}">{"Googleマップで開く" if ja else "Open in Google Maps"}</a></div></div></div>'
        for m, ne, nj, q in PLACES)
    return (opener("BOOK &amp; NAVIGATE", "", title, 6) + check +
            f'<h3>{h_book}</h3><p>{lead_book}</p><div class="qrgrid">{book}</div>{fc}'
            f'<h3 class="newpage">{h_nav}</h3><p>{lead_nav}</p><div class="qrgrid">{nav}</div>')


MAP_LABELS = {
    "en": dict(
        title="Route Diagram", note="Diagram only. Distances and positions are not to scale. All times are from Chapters 2 and 3.",
        station="Kawaguchiko<br>Station", rail="Fujikyu Railway", red="Red Line", green="Green Line", blue="Blue Line",
        route="Route bus", direct="Direct bus",
        p1="① Chureito Pagoda", p1b="Shimoyoshida Sta. + 25 min on foot", p2="② Oishi Park", p2b="about 27 min",
        p3="③ Oshino Hakkai", p3b="bus for Gotemba or Yamanakako Hirano", p4="④ Ropeway", p4b="about 11 min or 15 min on foot",
        p5="⑤ Iyashi-no-Sato Nenba", p5b="about 40 min", p6="⑥ 5th Station", p6b="about 1 hour",
        p7="⑦ Fuji-Q Highland", p7b="one stop", p8="⑧ Lake Motosu", p8b="about 1 hour + 1 hour on foot",
        tokyo="To Tokyo (Shinjuku): Fuji Excursion or highway bus (Chapter 2)"),
    "ja": dict(
        title="乗り換え案内図", note="位置や距離は正確ではありません。時間は第2章・第3章の確認済みの情報です。",
        station="河口湖駅", rail="富士急行線", red="レッドライン", green="グリーンライン", blue="ブルーライン",
        route="路線バス", direct="直行バス",
        p1="① 五重塔", p1b="下吉田駅＋徒歩25分", p2="② 大石公園", p2b="約27分",
        p3="③ 忍野八海", p3b="御殿場行きか山中湖平野行き", p4="④ ロープウェイ", p4b="約11分（徒歩なら約15分）",
        p5="⑤ いやしの里根場", p5b="約40分", p6="⑥ 五合目", p6b="約1時間",
        p7="⑦ 富士急ハイランド", p7b="1駅", p8="⑧ 本栖湖", p8b="約1時間＋徒歩約1時間",
        tokyo="東京（新宿）へ：富士回遊・高速バス（第2章）"),
}


def route_map(lang):
    L = MAP_LABELS[lang]
    spokes = [
        (20, 30, "#c0392b", L["red"], L["p4"], L["p4b"]),
        (20, 140, "#c0392b", L["red"], L["p2"], L["p2b"]),
        (20, 250, "#3f8f5b", L["green"], L["p5"], L["p5b"]),
        (20, 360, "#2f6db5", L["blue"], L["p8"], L["p8b"]),
        (340, 30, "#e08a2c", L["rail"], L["p7"], L["p7b"]),
        (340, 140, "#e08a2c", L["rail"], L["p1"], L["p1b"]),
        (340, 250, "#8c8c8c", L["route"], L["p3"], L["p3b"]),
        (340, 360, "#26231f", L["direct"], L["p6"], L["p6b"]),
    ]
    cx, cy = 280, 225
    parts = []
    for x, y, col, *_ in spokes:
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x+100}" y2="{y+32}" stroke="{col}" stroke-width="6" stroke-linecap="round"/>')
    for x, y, col, line, place, detail in spokes:
        parts.append(f'<rect x="{x}" y="{y}" width="200" height="66" rx="10" fill="#fffdf8" stroke="{col}" stroke-width="2.5"/>')
        parts.append(f'<text x="{x+10}" y="{y+17}" font-size="10" fill="{col}" font-weight="700">{line}</text>')
        parts.append(f'<text x="{x+10}" y="{y+37}" font-size="13.5" font-weight="700" fill="#26231f">{place}</text>')
        parts.append(f'<text x="{x+10}" y="{y+55}" font-size="10" fill="#7d7466">{detail}</text>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="50" fill="#26231f"/>')
    lines = L["station"].split("<br>")
    for k, t in enumerate(lines):
        parts.append(f'<text x="{cx}" y="{cy + 5 + (k - (len(lines)-1)/2)*16}" font-size="14" font-weight="700" fill="#fff" text-anchor="middle">{t}</text>')
    parts.append(f'<text x="{cx}" y="455" font-size="11" fill="#7d7466" text-anchor="middle">{L["tokyo"]}</text>')
    svg = f'<svg viewBox="0 0 560 470" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">{"".join(parts)}</svg>'
    return opener("BONUS · QUICK MAP", "", L["title"], 2) + svg + f'<p class="src">{L["note"]}</p>'


def decorate_chapters(body, ja):
    def repl(m):
        title = m.group(1)
        mm = re.match(r"(?:Chapter (\d): |第(\d)章\s*|제(\d)장\s*|บทที่ (\d) |Chương (\d): |Bab (\d): )(.*)", title)
        if mm:
            n = next(g for g in mm.groups()[:-1] if g)
            return opener("CHAPTER", f"0{n}", mm.groups()[-1], int(n))
        return opener("ESSENTIALS", "", title, 3)
    return re.sub(r"<h2>(.*?)</h2>", repl, body)


for _k in ("zh-hans", "zh-hant", "ko", "th", "vi", "ms"):
    TEXT[_k], FINDER[_k], MAP_LABELS[_k] = i18n.TEXT[_k], i18n.FINDER[_k], i18n.MAP_LABELS[_k]

NEWPAGE_H3 = {"en": ["When can you actually see Mt. Fuji?", "Useful Japanese phrases"],
              "ja": ["富士山はいつ見えるの？", "使える日本語のひとこと"], **i18n.NEWPAGE_H3}


def section(lang):
    """HTML for one language: its own cover, welcome page and all chapters."""
    if lang == "en":
        src = SRC
    elif lang == "ja":
        src = sorted((HERE / "ja-review").glob("*.ja.md"))
    else:
        src = sorted((HERE / lang).glob("*.md"))
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
    keys = {"ja": ["公式", "電話で確認", "Googleマップ", "Googleに載", "Googleのメニュー"]}.get(lang, i18n.SRC_KEYWORDS.get(lang))
    if keys:
        alt = "|".join(map(re.escape, keys))
        body = re.sub(rf"（([^（）]*(?:{alt})[^（）]*)）", r'<span class="src">（\1）</span>', body)
        body = re.sub(rf"\(([^()]*(?:{alt})[^()]*)\)", r'<span class="src">(\1)</span>', body)
    body = re.sub(r"\((?=[^()]*(?:official|Confirmed by phone|confirmed by phone|Google Maps|Google, November))([^()]*(?:\([^()]*\)[^()]*)*)\)",
                  r'<span class="src">(\1)</span>', body)
    body = decorate_chapters(body, lang == "ja")
    body = add_photos(body)
    # The course finder goes right after the essentials page, before Chapter 1.
    i = body.find('<div class="opener"><div class="ph">', body.find("ESSENTIALS") + 1)
    body = body[:i] + chart.chart(lang, FINDER[lang]["title"], FINDER[lang]["tips"], i18n.to_hant) + body[i:]
    body = body + book_and_nav(lang) + route_map(lang)
    # Short tables stay on one page; long ones (and itineraries) may continue on the next page.
    body = re.sub(r"<table>(.*?)</table>", lambda m: ('<table class="keep">' if m.group(1).count("<tr>") <= 9 and not re.search(r"<th>(Time|時間|时间|시간|เวลา|Giờ|Masa)</th>", m.group(1)) else "<table>") + m.group(1) + "</table>",
                  body, flags=re.S)
    # The essentials table is long: use a smaller font so it fits on one page.
    j = body.find("<table", body.find("ESSENTIALS"))
    body = body[:j] + re.sub(r'^<table( class="keep")?', '<table class="ess"', body[j:], count=1)
    # A heading should never sit alone at the bottom of a page: keep it with its first paragraph.
    body = re.sub(r"(<h3>[^<]*</h3>\s*<p>.*?</p>)", r'<div class="keepnext">\1</div>', body, flags=re.S)
    # Keep the "when can you see Mt. Fuji" heading, text and table together on one page.
    for h in NEWPAGE_H3[lang]:
        body = body.replace(f"<h3>{h}</h3>", f'<h3 class="newpage">{h}</h3>')
    return f'<section class="L-{lang}" lang="{lang}">{cover(lang, "lang-" + lang)}{note(lang)}{body}</section>'


def picker():
    names = " · ".join(f"{flags} {name}" for _, name, flags, _, _ in i18n.LANGS)
    front = cover("en")
    COVERS[-1] = ("en", COVERS[-1][1].replace('<div class="top">', f'<div class="langs">{names}</div><div class="top">', 1))
    rows = "".join(
        f'<a class="lang" href="#lang-{code}"><span class="flag">{flags}</span><span class="nm">{name}</span><span class="go">{go}</span></a>'
        for code, name, flags, _, go in i18n.LANGS)
    return (front + f'<div class="picker" id="languages"><p class="eyebrow">Language · 언어 · 語言 · 语言 · ภาษา · Ngôn ngữ · Bahasa</p>'
            f'<h2 class="serif">Choose your language</h2><div class="sub">언어를 선택하세요 · 選擇語言 · 选择语言 · เลือกภาษา · Chọn ngôn ngữ · Pilih bahasa — tap to jump</div>{rows}</div>')


def build(ja=False):
    if ja:
        lang, body = "ja", section("ja")
    else:
        lang = "en"
        body = picker() + "".join(section(code) for code, *_ in i18n.LANGS)
    css = CSS.replace('"Noto Sans", "Noto Sans CJK JP"', '"Noto Sans CJK JP", "Noto Sans"') if ja else CSS
    html = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<title>{TEXT[lang]["title"]}</title><style>{css}</style></head>
<body>{body}{credits()}</body></html>"""
    out_html = HTML.with_suffix(".ja-review.html") if ja else HTML
    out_pdf = PDF.with_suffix(".ja-review.pdf") if ja else PDF
    DIST.mkdir(exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", out_html.as_uri()], check=True, capture_output=True)
    # Print the covers full-bleed and lay each one over its blank slot page.
    cov_html = DIST / "covers.html"
    cov_pdf = DIST / "covers.pdf"
    cov_html.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}
@page {{ size: A5; margin: 0; @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}</style></head>
<body>{"".join(f'<section class="L-{lg}" lang="{lg}">{h}</section>' for lg, h in COVERS)}</body></html>""", encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={cov_pdf}", cov_html.as_uri()], check=True, capture_output=True)
    import pymupdf
    doc, cov = pymupdf.open(out_pdf), pymupdf.open(cov_pdf)
    slots = [i for i, pg in enumerate(doc) if "COVERSLOT" in pg.get_text()]
    assert len(slots) == len(COVERS) == len(cov), (len(slots), len(COVERS), len(cov))
    for k, i in enumerate(slots):
        doc[i].show_pdf_page(doc[i].rect, cov, k)
    tmp = out_pdf.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    tmp.replace(out_pdf)
    cov_html.unlink()
    cov_pdf.unlink()
    COVERS.clear()
    print(out_pdf)


if __name__ == "__main__":
    build(ja="--ja" in sys.argv)
