"""Magazine-style Mt. Fuji guide, laid out page by page like the photo prototype (guide_v1).

Each language gets the same 34 designed pages; the words come from text/<lang>.py
and the numbers (prices, times) are written once here or in the text files.
Usage: python3 guides/mt-fuji/magazine.py [--ja] [--only en]
"""
import importlib
import pathlib
import re
import subprocess
import sys

import segno

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import photos as ph  # noqa: E402
import i18n  # noqa: E402
from links import BOOKING, PLACES, maps_url  # noqa: E402

DIST = HERE / "dist"
FONTS = HERE / "fonts"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

RED, NAVY, GREEN, BLUE, ORANGE, GREY = "#c4473a", "#1f2a44", "#4c8c5a", "#3d6aa8", "#de8a3a", "#9b978f"


# ---------------------------------------------------------------- small helpers
def qr(url):
    return segno.make(url, error="m").svg_data_uri(scale=4, border=1, dark="#26231f")


ICON = {  # 24x24 stroke icons
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "yen": '<path d="M6 4l6 8 6-8M12 12v8M7 13h10M7 17h10"/>',
    "cal": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "ticket": '<path d="M3 8a2 2 0 0 0 0 4v0a2 2 0 0 1 0 4v2h18v-2a2 2 0 0 1 0-4 2 2 0 0 1 0-4V6H3z"/><path d="M14 6v12" stroke-dasharray="2 2"/>',
    "train": '<rect x="5" y="3" width="14" height="14" rx="3"/><path d="M5 11h14M8 21l2-4M16 21l-2-4"/><circle cx="9" cy="14" r=".6"/><circle cx="15" cy="14" r=".6"/>',
    "bus": '<rect x="4" y="3" width="16" height="15" rx="2"/><path d="M4 10h16M7 21v-3M17 21v-3"/><circle cx="8" cy="14" r=".7"/><circle cx="16" cy="14" r=".7"/>',
    "walk": '<circle cx="13" cy="4.5" r="1.8"/><path d="M10 21l2-6 3 3v3M9 12l2-5 3 2 3 1M12 15l-1-4"/>',
    "stairs": '<path d="M3 20h4v-4h4v-4h4V8h4V4"/>',
    "wc": '<circle cx="7" cy="5" r="1.6"/><circle cx="17" cy="5" r="1.6"/><path d="M5 9h4l1 6H8v6M7 15v6M15 9h4l2 7h-3v5M16 16v5"/>',
    "warn": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    "camera": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l2-3h4l2 3"/><circle cx="12" cy="13.5" r="3.5"/>',
    "home": '<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-5h4v5"/>',
    "trash": '<path d="M5 7h14M10 7V4h4v3M7 7l1 13h8l1-13"/>',
    "bag": '<rect x="5" y="7" width="14" height="13" rx="2"/><path d="M9 7V5a3 3 0 0 1 6 0v2"/>',
    "card": '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h4"/>',
    "child": '<circle cx="12" cy="5" r="2"/><path d="M9 21v-6H8l1-6h6l1 6h-1v6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/>',
    "cloud": '<path d="M7 18a4 4 0 0 1-.5-8 6 6 0 0 1 11.5 1.5A3.5 3.5 0 0 1 17.5 18z"/>',
    "umbrella": '<path d="M3 12a9 9 0 0 1 18 0zM12 12v7a2 2 0 0 0 4 0M12 3v0"/>',
    "cup": '<path d="M5 9h11v5a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5zM16 10h2a2 2 0 0 1 0 4h-2"/><path d="M8 3v3M11 3v3"/>',
    "bowl": '<path d="M3 11h18a9 7 0 0 1-18 0zM8 7l6-4M10 8l7-3"/>',
    "leaf": '<path d="M5 19C5 10 11 5 20 4c-1 9-6 15-15 15zM5 19l7-7"/>',
    "wheel": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2"/><path d="M12 4v6M12 14v6M4 12h6M14 12h6"/>',
    "dog": '<path d="M5 10l2-5 3 3h4l3-3 2 5v4a5 5 0 0 1-5 5h-4a5 5 0 0 1-5-5z"/><circle cx="10" cy="12" r=".6"/><circle cx="14" cy="12" r=".6"/>',
    "snow": '<path d="M12 3v18M4 7.5l16 9M4 16.5l16-9M9 4.5l3 2 3-2M9 19.5l3-2 3 2"/>',
    "rule": '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "quiet": '<path d="M4 9h4l5-4v14l-5-4H4zM17 9l4 6M21 9l-4 6"/>',
    "star": '<path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.5 6.7 19.4l1.2-6L3.4 9.3l6-.7z"/>',
    "map": '<path d="M9 4l-6 2v14l6-2 6 2 6-2V4l-6 2zM9 4v14M15 6v14"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
}


def icon(name, color=RED, size=11):
    return (f'<svg class="ic" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


def img(key):
    return ph.src(key)


def eyebrow(en, local=""):
    return f'<p class="eb">{en}</p>' if not local else f'<p class="eb">{en}</p>'


def head(en, title, lead=""):
    lead = f'<p class="lead">{lead}</p>' if lead else ""
    return f'<p class="eb">{en}</p><h1>{title}</h1>{lead}'


def h2(title, en=""):
    e = f'<span class="h2en">{en}</span>' if en else ""
    return f'<h2>{title}{e}</h2>'


def stats(items, cols=4, small=False):
    """items: (icon, label, value, sub)"""
    out = "".join(
        f'<div class="st">{icon(i)}<span class="sl">{l}</span><b>{v}</b>{f"<span class=ss>{s}</span>" if s else ""}</div>'
        for i, l, v, s in items)
    return f'<div class="stats c{cols}{" sm" if small else ""}">{out}</div>'


def card(ic, title, text, cls=""):
    i = icon(ic) if ic else ""
    return f'<div class="cd {cls}"><div class="ct">{i}<b>{title}</b></div><div class="cx">{text}</div></div>'


def alert(text, ic="warn"):
    return f'<div class="alert">{icon(ic)}<div>{text}</div></div>'


def note(label, text):
    return f'<div class="note"><span class="nl">{label}</span><div>{text}</div></div>'


def src(text):
    return f'<p class="src">{text}</p>'


def table(head_cells, rows, cls="", aligns=None):
    aligns = aligns or [""] * len(head_cells)
    th = "".join(f'<th class="{a}">{h}</th>' for h, a in zip(head_cells, aligns))
    labels = [re.sub(r"<[^>]+>", "", h).replace('"', "&quot;") for h in head_cells]
    tr = "".join("<tr>" + "".join(f'<td class="{a}" data-l="{l}">{c}</td>' for c, a, l in zip(r, aligns, labels)) + "</tr>" for r in rows)
    if len(head_cells) >= 4:
        cls += " wide"  # the phone version turns these rows into cards
    return f'<table class="tb {cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def chip(line, text=""):
    return f'<span class="chip {line}">{text}</span>'


def timeline(items):
    """items: (time, title, text, filled)"""
    out = ""
    for t, title, text, filled in items:
        out += (f'<div class="tl"><div class="tt">{t}</div><div class="td{" f" if filled else ""}"></div>'
                f'<div class="tc"><b>{title}</b>{f"<span>{text}</span>" if text else ""}</div></div>')
    return f'<div class="tls">{out}</div>'


# ---------------------------------------------------------------- page frame
class Book:
    def __init__(self, lang, T):
        self.lang, self.T, self.pages, self.n = lang, T, [], 0

    def page(self, body, foot, cls="", ident=""):
        self.n += 1
        i = f' id="{ident}"' if ident else ""
        f = (f'<div class="foot"><span>{foot}</span><span>{self.n:02d}</span></div>' if foot else "")
        self.pages.append(f'<section class="pg {cls}"{i}><div class="in">{body}</div>{f}</section>')


FOOT = dict(intro="INTRODUCTION", ch1="CHAPTER 1 · BEFORE YOU GO", ch2="CHAPTER 2 · GETTING THERE",
            ch3="CHAPTER 3 · EIGHT PLACES", ch4="CHAPTER 4 · MODEL COURSES", ch5="CHAPTER 5 · LOCAL FOOD",
            ch6="CHAPTER 6 · GOOD TO KNOW", bonus="BONUS · BOOK &amp; NAVIGATE", map="BONUS · QUICK MAP",
            ess="ESSENTIALS", finder="COURSE FINDER")


def opener(photo, num, title, extra="", h=112):
    keys = photo if isinstance(photo, list) else [photo]
    ims = "".join(f'<img src="{img(k)}">' for k in keys)
    return (f'<div class="op" style="height:{h}mm"><div class="opi">{ims}</div><div class="shade"></div>'
            f'<div class="opt"><span class="opl">CHAPTER</span><span class="opn">{num}</span><span class="oph">{title}</span></div></div>'
            f'<div class="opb">{extra}</div>')


def place_head(photo, num, en, title, lead, h=62, nav=None):
    n = f'<div class="pnum">{num}</div>'
    q = ""
    if nav:
        q = f'<a class="navqr" href="{nav}"><img src="{qr(nav)}"><span>NAVI</span></a>'
    return (f'<div class="ph" style="height:{h}mm"><img src="{img(photo)}">{q}</div>{n}'
            f'<div class="phb"><p class="eb">{en}</p><h1>{title}</h1><p class="lead">{lead}</p></div>')


def nav_url(i):  # i = place number 1..8
    return maps_url(PLACES[i + 1][3])


# ---------------------------------------------------------------- pages
def p_cover(B):
    T = B.T["cover"]
    st = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in T["stats"])
    body = (f'<img class="cv" src="{img("cover")}"><div class="cvs"></div>'
            f'<div class="cvtop"><span>DAY TRIP FROM TOKYO</span><span>2026 EDITION</span></div>'
            f'<div class="cvt"><div class="cvk">{T["kicker"]}</div><div class="cvbig">Fuji</div>'
            f'<div class="cvh">{T["h1"]}</div><div class="cved">{T["ed"]}</div></div><div class="cvst">{st}</div>')
    B.page(body, "", "cover", ident=f"lang-{B.lang}")


def p_welcome(B, toc_pages):
    T = B.T["welcome"]
    thumbs = ["lake", "train", "chureito", "itchiku", "hoto", "station"]
    rows = "".join(
        f'<a class="tr" href="#{B.lang}-p{toc_pages[k]}"><img src="{img(th)}"><span class="tn">{k + 1}</span>'
        f'<span class="tx"><b>{t}</b><span>{s}</span></span><span class="tp">{toc_pages[k]:02d}</span></a>'
        for k, ((t, s), th) in enumerate(zip(T["toc"], thumbs)))
    extra = "".join(f'<a href="#{B.lang}-p{toc_pages[6 + k]}">{t} <b>{toc_pages[6 + k]:02d}</b></a>' for k, t in enumerate(T["extra"]))
    # The "change language" link only makes sense in the all-languages book (it jumps to the picker page).
    change = f'<a class="chg" href="#languages">{T["change"]}</a>' if not SINGLE[0] else ""
    body = (f'<p class="eb">Welcome</p><h1>{T["h"]}</h1><p class="lead">{T["p1"]}</p>{alert(T["alert"])}'
            f'<div class="toch">{T["contents"]}<span class="h2en">Contents</span></div><div class="toc">{rows}</div>'
            f'<div class="tocx">{extra}</div><p class="src">{T["disclaimer"]} {change}</p>')
    B.page(body, FOOT["intro"])


def p_know(B, rows):
    T = B.T["know"]
    trs = "".join(f'<tr><td class="kn">{n}</td><td>{txt}</td><td class="kc">{c}</td></tr>' for n, txt, c in rows)
    body = (head("Know Before You Go", T["h"], T["lead"]) +
            f'<table class="tb know"><thead><tr><th></th><th>{T["col"]}</th><th class="r">{T["ch"]}</th></tr></thead><tbody>{trs}</tbody></table>'
            f'<div class="author"><div class="nl">{T["author_h"]}</div><div>{T["author"]}</div></div>')
    B.page(body, FOOT["ess"])


def p_finder(B, chart_html):
    B.page(chart_html, FOOT["finder"], "finder")


def p_ch1(B):
    T = B.T["ch1"]
    steps = "".join(f'<div class="step"><span class="sn">{i + 1}</span><div><b>{a}</b><span>{b}</span></div></div>'
                    for i, (a, b) in enumerate(T["steps"]))
    extra = f'<p class="lead">{T["intro"]}</p>{h2(T["hide_h"], "If Fuji is hiding")}<div class="steps">{steps}</div>'
    B.page(opener("lake", "01", T["title"], extra, h=100), FOOT["ch1"], "opener")


MONTHS = [(19, 9, 3), (22, 4, 2), (13, 7, 11), (9, 9, 12), (9, 10, 12), (2, 9, 19),
          (5, 4, 22), (3, 8, 20), (6, 11, 13), (10, 8, 13), (19, 9, 2), (19, 7, 5)]


def p_when(B):
    T = B.T["when"]
    bars = ""
    for i, (a, b, c) in enumerate(MONTHS):
        tot = a + b + c
        bars += (f'<div class="bc"><span class="bn">{a}</span><div class="bb">'
                 f'<i style="height:{c / tot * 100:.1f}%" class="b3"></i><i style="height:{b / tot * 100:.1f}%" class="b2"></i>'
                 f'<i style="height:{a / tot * 100:.1f}%" class="b1"></i></div><span class="bm">{T["months"][i]}</span></div>')
    leg = "".join(f'<span><i class="b{k + 1}"></i>{t}</span>' for k, t in enumerate(T["legend"]))
    cards = "".join(f'<div class="sc s{k}">{icon(ic)}<b>{a}</b><span>{b}</span></div>'
                    for k, ((a, b), ic) in enumerate(zip(T["seasons"], ["sun", "cloud", "umbrella"])))
    body = (head("When to Go", T["h"], T["lead"]) + f'<div class="bars">{bars}</div><div class="leg">{leg}</div>'
            + src(T["src"]) + f'<div class="seas">{cards}</div>' + note("NOTE", T["note"]))
    B.page(body, FOOT["ch1"])


def p_ch2(B):
    T = B.T["ch2"]

    def tcard(c, ic):
        li = "".join(f'<li class="{"x" if bad else "o"}">{t}</li>' for t, bad in c["pros"])
        return (f'<div class="vc"><div class="vh">{icon(ic)}<b>{c["name"]}</b></div><div class="vn"><b>{c["time"]}</b>'
                f'<small>{c["approx"]}</small><b>{c["price"]}</b></div><ul>{li}</ul><p class="vf">{c["fit"]}</p></div>')
    extra = (f'<p class="eb">Train or Bus?</p>{h2(T["tb_h"])}<div class="vs">{tcard(T["train"], "train")}<span class="vsx">vs</span>'
             f'{tcard(T["bus"], "bus")}</div>' + note("OUR PICK", T["pick"]))
    B.page(opener("train", "02", T["title"], extra, h=88), FOOT["ch2"], "opener")


def p_train(B):
    T = B.T["train"]
    st = T["stations"]
    major = {0, 3, 5, 8}
    dots = "".join(f'<div class="sd{" f" if i in major else ""}"><i></i><span>{s}</span></div>' for i, s in enumerate(st))
    cars = "".join(f'<span class="car{" on" if i < 3 else ""}">{i + 1 if i < 6 else "…"}</span>' for i in range(7))
    sides = "".join(f'<div style="flex:{w}" class="sb {c}"><b>{a}</b><span>{b}</span></div>'
                    for (a, b), w, c in zip(T["sides"], [55, 22, 18], ["blu", "red", "blu"]))
    body = (head("A — By Train", T["h"]) +
            stats([("clock", T["s1"], T["s1v"], ""), ("yen", T["s2"], T["s2v"], T["s2s"]), ("cal", T["s3"], T["s3v"], T["s3s"]),
                   ("ticket", T["s4"], T["s4v"], T["s4s"])]) +
            h2(T["stops_h"], "Stops") + f'<div class="stops">{dots}</div>' + src(T["stops_note"]) +
            f'<div class="alert big">{icon("warn")}<div><b>{T["warn_b"]}</b> {T["warn"]}<div class="cars">{cars}</div>'
            f'<div class="carl"><span>{T["car1"]}</span><span>{T["car2"]}</span></div></div></div>'
            f'<div class="g2">{card("ticket", T["c1t"], T["c1"])}{card("info", T["c2t"], T["c2"], "beige")}</div>' +
            h2(T["side_h"], "Which side?") + f'<p class="small">{T["side_lead"]}</p><div class="sides">{sides}</div>' +
            src(T["side_note"]))
    B.page(body, FOOT["ch2"])


def p_timetable(B):
    T = B.T["tt"]
    down = [("3", "7:30", "9:28"), ("7", "8:30", "10:26"), ("11", "9:30", "11:28"), ("15", "10:30", "12:24")]
    up = [("32", "14:08", "16:08"), ("36", "14:58", "16:59"), ("44", "16:48", "18:48"), ("48", "17:41", "19:48")]

    def tt(label, tag, rows, cols):
        r = "".join(f'<tr><td>{T["train"].format(n)}</td><td class="r big">{a}</td><td class="r">{b}</td></tr>' for n, a, b in rows)
        return (f'<div><div class="tth"><span class="tag {tag}">{label[0]}</span><b>{label[1]}</b></div>'
                f'<table class="tb ttb"><thead><tr><th>{cols[0]}</th><th class="r">{cols[1]}</th><th class="r">{cols[2]}</th></tr></thead><tbody>{r}</tbody></table></div>')
    body = (head("Timetable", T["h"]) + src(T["note"]) +
            f'<div class="g2 tt2">{tt(T["down"], "red", down, T["cols_down"])}{tt(T["up"], "ink", up, T["cols_up"])}</div>'
            f'<div class="photo" style="height:86mm"><img src="{img("station")}"></div>' + src(T["cap"]))
    B.page(body, FOOT["ch2"])


def p_passes(B):
    T = B.T["passes"]
    jr = table(T["jr_cols"], [[T["jr_r1"], "1,170", "600", "<b>1,770</b>"], [T["jr_r2"], "980", "600", "<b>1,580</b>"]],
               "inner", ["", "r", "r", "r big"])
    wide = "".join(f"<li>{x}</li>" for x in T["wide_li"])
    pb = "".join(f'<div class="sd{" f" if i % 2 == 0 else ""}"><i></i><span>{s}</span></div>' for i, s in enumerate(T["planb_line"]))
    rows = [[T["pb_rows"][0], "<b>400</b>", "—"], [T["pb_rows"][1], "+200", T["seat"]],
            [T["pb_rows"][2], "+900", T["special"]], [T["pb_rows"][3], "+200", T["seat"]]]
    body = (head("Rail Passes", T["h"]) +
            f'<div class="box">{icon("ticket")}<b class="bt">{T["jr_t"]}</b><p>{T["jr"]}</p>{jr}{src(T["jr_note"])}</div>'
            f'<div class="box blue">{icon("ticket")}<b class="bt">{T["wide_t"]}</b><p>{T["wide"]}</p><ul>{wide}</ul>{src(T["wide_src"])}</div>'
            + h2(T["planb_h"], "Plan B") + f'<div class="stops five">{pb}</div><p class="small">{T["planb"]}</p>'
            + table(T["pb_cols"], rows, "", ["", "r", ""]) + src(T["pb_note"]))
    B.page(body, FOOT["ch2"])


def p_bus(B):
    T = B.T["bus"]
    body = (f'<div class="ph" style="height:52mm"><img src="{img("bus")}"></div><div class="phb">'
            + head("B — By Highway Bus", T["h"]) +
            stats([("clock", T["s1"], T["s1v"], T["s1s"]), ("yen", T["s2"], T["s2v"], T["s2s"]), ("bus", T["s3"], T["s3v"], T["s3s"]),
                   ("wc", T["s4"], T["s4v"], T["s4s"])]) +
            f'<p class="small">{T["p"]}</p><div class="g2">{card("ticket", T["c1t"], T["c1"])}{card("rule", T["c2t"], T["c2"])}'
            f'{card("warn", T["c3t"], T["c3"], "beige")}{card("bag", T["c4t"], T["c4"])}</div>' + src(T["src"]) + "</div>")
    B.page(body, FOOT["ch2"], "full")


def loop_map(L):
    """Schematic of the three sightseeing bus lines."""
    def st(x, y, label, anchor="middle", dx=0, dy=-9, big=False, col=RED):
        r = 5 if not big else 9
        fill = "#fff" if not big else "#1b1b1b"
        return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{col if not big else "#1b1b1b"}" stroke-width="3"/>'
                f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{label}</text>')
    red = [(440, 120), (390, 70), (320, 70), (250, 70), (215, 70)]
    s = '<svg viewBox="0 0 520 260" class="lmap">'
    s += f'<polyline points="{" ".join(f"{x},{y}" for x, y in red)}" fill="none" stroke="{RED}" stroke-width="7" stroke-linejoin="round"/>'
    green = [(440, 120), (340, 135), (240, 140), (150, 130), (90, 110)]
    s += f'<polyline points="{" ".join(f"{x},{y}" for x, y in green)}" fill="none" stroke="{GREEN}" stroke-width="7" stroke-linejoin="round"/>'
    blue = [(440, 120), (400, 165), (330, 190), (260, 190), (180, 190), (70, 205)]
    s += f'<polyline points="{" ".join(f"{x},{y}" for x, y in blue)}" fill="none" stroke="{BLUE}" stroke-width="7" stroke-linejoin="round"/>'
    s += '<g font-size="11" fill="#2a2620" stroke="#fffdf9" stroke-width="3" paint-order="stroke">'
    s += st(390, 70, L["ropeway"], "start", 10, -8)
    s += st(320, 70, L["music"], "middle", 0, -10)
    s += st(250, 70, L["itchiku"], "middle", 18, 22)
    s += st(215, 70, L["oishi"], "middle", 0, -10)
    s += st(340, 135, L["saiko"], col=GREEN)
    s += st(240, 140, L["nenba"], col=GREEN, dy=22)
    s += st(150, 130, L["bat"], col=GREEN)
    s += st(90, 110, L["fugaku_end"], col=GREEN)
    s += st(400, 165, L["heritage"], "start", 12, 4, col=BLUE)
    s += st(330, 190, L["narusawa"], col=BLUE, dy=20)
    s += st(260, 190, L["fugaku"], col=BLUE)
    s += st(180, 190, L["shoji"], col=BLUE, dy=20)
    s += st(70, 205, L["motosu"], "start", -20, 22, col=BLUE)
    s += st(440, 120, "", big=True)
    s += f'<text x="440" y="100" font-weight="700" font-size="12" text-anchor="middle">{L["station"]}</text>'
    s += "</g></svg>"
    leg = "".join(f'<span style="color:{c}">{L[k]}</span>' for k, c in (("red", RED), ("green", GREEN), ("blue", BLUE)))
    return s + f'<div class="lmleg">{leg}</div>'


def p_around(B):
    T = B.T["around"]
    rows = [[chip("red", T["red"]), T["r1"], "②④"], [chip("green", T["green"]), T["r2"], "⑤"], [chip("blue", T["blue"]), T["r3"], "⑧"]]
    body = (head("Getting Around", T["h"], T["lead"]) + f'<div class="mapbox">{loop_map(T["map"])}</div>' + src(T["map_note"]) +
            table(T["cols"], rows, "", ["", "", "c"]) + alert(T["alert"], "info"))
    B.page(body, FOOT["ch2"])


def p_buspass(B):
    T = B.T["buspass"]
    rows = [[T["r1"], "<b>1,500</b>", "750"], [T["r2"], "<b>2,000</b>", "1,000"], [T["r3"], "<b>3,300</b>", "1,650"]]
    vals = [(T["b1"], 1220, GREY), (T["b2"], 1500, RED), (T["b3"], 1620, GREEN), (T["b4"], 2940, BLUE)]
    bars = "".join(f'<div class="hb"><span class="hl">{l}</span><div><i style="width:{v / 2940 * 100:.0f}%;background:{c}"></i></div>'
                   f'<span class="hv"{" style=color:" + RED if c == RED else ""}>{v:,}{T["yen"]}</span></div>' for l, v, c in vals)
    f = T["fares"]
    fr = [[chip("red", T["red"]), f[0], "180"], ["", f[1], "440"], ["", f[2], "570"], [chip("green", T["green"]), f[3], "810"],
          [chip("blue", T["blue"]), f[4], "740"], ["", f[5], "770"], ["", f[6], "1,470"]]
    body = (head("Bus Passes", T["h"], T["lead"]) + table(T["cols"], rows, "", ["", "r big", "r"]) + src(T["note"]) +
            h2(T["payg_h"], "Pay as you go") + f'<div class="hbars">{bars}</div>' + note("VERDICT", T["verdict"]) +
            h2(T["fares_h"], "Fares") + table(T["fcols"], fr, "compact", ["", "", "r"]) + src(T["src"]))
    B.page(body, FOOT["ch2"])


def p_passport(B):
    T = B.T["passport"]
    rows = [[T["r1"], T["r1s"], "<b>3,300</b>", "1,660"], [T["r2"], T["r2s"], "<b>4,700</b>", "2,360"]]
    body = (head("2-Day Passport", T["h"], T["lead"]) + table(T["cols"], rows, "", ["", "", "r big", "r"]) + src(T["note"]) +
            note("JR PASS HOLDERS", T["jr"]) + h2(T["good_h"], "Good to know") +
            f'<div class="g2">{card("card", T["c1t"], T["c1"])}{card("child", T["c2t"], T["c2"])}'
            f'{card("bag", T["c3t"], T["c3"], "beige")}{card("bag", T["c4t"], T["c4"] + "<div class=lock><b>700</b>" + T["s"] + " <b>1,000</b>" + T["m"] + " <b>1,200</b>" + T["l"] + "</div>")}</div>'
            + src(T["src"]))
    B.page(body, FOOT["ch2"])


def p_looptimes(B):
    T = B.T["loop"]

    def lc(col, title, rows, foot):
        r = "".join(f'<tr><td>{a}</td><td class="r">{b}</td><td class="r big">{c}</td></tr>' for a, b, c in rows)
        return (f'<div class="lc" style="border-color:{col}"><div class="lci" style="background:{col}">{icon("bus", "#fff", 13)}</div>'
                f'<b class="lct">{title}</b><table class="tb ttb"><thead><tr><th></th><th class="r">{T["first"]}</th><th class="r">{T["last"]}</th></tr></thead>'
                f'<tbody>{r}</tbody></table><p class="small">{foot}</p></div>')
    body = (head("Loop Bus Times", T["h"], T["lead"]) +
            lc(RED, T["red_t"], [(T["red_r1"], "9:00", "17:45"), (T["red_r2"], "9:27", "18:27")], T["red_f"]) +
            lc(GREEN, T["green_t"], [(T["green_r1"], "9:10", "16:40"), (T["green_r2"], "—", "17:40")], T["green_f"]) +
            lc(BLUE, T["blue_t"], [(T["blue_r1"], "9:35", "15:35"), (T["blue_r2"], "10:45", "16:45")], T["blue_f"]) + src(T["src"]))
    B.page(body, FOOT["ch2"])


def eight_map(L):
    s = '<svg viewBox="0 0 400 210" class="emap"><rect width="400" height="210" rx="14" fill="#dfe7ef"/>'
    s += '<path d="M95 210 L200 118 L305 210 Z" fill="#8d9fb8"/><path d="M200 118 L182 134 L192 131 L200 138 L208 131 L218 134 Z" fill="#fff"/>'
    lakes = [(70, 128, 22, 13, L["motosu"]), (110, 106, 12, 7, L["shoji"]), (152, 78, 27, 8, L["saiko"]),
             (230, 68, 50, 11, L["kawaguchi"]), (345, 140, 30, 13, L["yamanaka"])]
    for x, y, rx, ry, t in lakes:
        s += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#7fb0dc"/><text x="{x}" y="{y + ry + 12}" text-anchor="middle" font-size="9">{t}</text>'
    s += f'<text x="200" y="196" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">{L["fuji"]}</text>'
    s += f'<rect x="250" y="99" width="66" height="14" rx="3" fill="#222"/><text x="283" y="109" text-anchor="middle" font-size="8" fill="#fff">{L["station"]}</text>'
    pins = [(337, 72), (226, 50), (330, 120), (273, 60), (130, 65), (200, 150), (318, 85), (52, 108)]
    for i, (x, y) in enumerate(pins):
        s += f'<circle cx="{x}" cy="{y}" r="9" fill="{RED}" stroke="#fff" stroke-width="2"/><text x="{x}" y="{y + 3.5}" text-anchor="middle" font-size="9" fill="#fff" font-weight="700">{i + 1}</text>'
    return s + "</svg>"


def p_eight(B):
    T = B.T["eight"]
    acc = [T["a1"], chip("red", T["red"]) + " " + T["a2"], T["a3"], chip("red", T["red"]) + " " + T["a4"],
           chip("green", T["green"]) + " " + T["a5"], T["a6"], T["a7"], chip("blue", T["blue"]) + " " + T["a8"]]
    tm = ["1–1.5h", "1h", "1h", "1h", "1–1.5h", "1.5–2h", T["t7"], T["t8"]]
    rows = [[f'<span class="rn">{i + 1}</span>', f"<b>{n}</b>", a, t, c] for i, (n, a, t, c) in enumerate(zip(T["names"], acc, tm, T["cost"]))]
    body = (head("Chapter 03 · Eight Places", T["h"]) + eight_map(T["map"]) + src(T["map_note"]) +
            table(T["cols"], rows, "eight", ["c", "", "", "", "r"]) + src(T["note"]))
    B.page(body, FOOT["ch3"])


def month_grid(rows, labels=True, colors=None):
    """rows: (label, [(start, end, color)]) months as 0..12 floats."""
    head_ = '<div class="mg h"><span></span><div>' + "".join(f"<i>{m}</i>" for m in range(1, 13)) + "</div></div>" if labels else ""
    out = head_
    for lab, segs in rows:
        bars = "".join(f'<b style="left:{a / 12 * 100:.1f}%;width:{max(b - a, .25) / 12 * 100:.1f}%;background:{c}"></b>' for a, b, c in segs)
        out += f'<div class="mg"><span>{lab}</span><div>{bars}</div></div>'
    return f'<div class="mgs">{out}</div>'


def p_chureito(B):
    T = B.T["p1"]
    season = month_grid([(T["cherry"], [(3.4, 3.65, "#e8a0b0")]), (T["leaves"], [(10.35, 10.6, ORANGE)]),
                         (T["fuji"], [(0, 2, NAVY), (10, 12, NAVY)])])
    light = table([T["l_col1"], T["l_col2"]], [[a, b] for a, b in zip(T["l_months"], ["16:00–21:50", "17:00–21:50", "18:00–21:50", "19:00–21:50"])], "compact", ["", "r"])
    body = (place_head("chureito", "01", "The Iconic Shot — Fujiyoshida", T["title"], T["lead"], 64, nav_url(1)) +
            '<div class="pb">' + stats([("walk", T["s1"], T["s1v"], T["s1s"]), ("clock", T["s2"], "1–1.5h", ""), ("yen", T["s3"], T["s3v"], T["s3s"]),
                                       ("stairs", T["s4"], T["s4v"], "")]) +
            f'<div class="g2 top"><div>{h2(T["season_h"], "Best season")}{season}<p class="small">{T["season_note"]}</p></div>'
            f'<div>{h2(T["light_h"], "Night")}{light}<p class="small">{T["light_note"]}</p></div></div>' +
            note("INSIDER TIP", T["tip"]) + src(T["src"]) + "</div>")
    B.page(body, FOOT["ch3"], "full")


def p_oishi(B):
    T = B.T["p2"]
    fl = month_grid([(T["flowers"][0], [(3.45, 4.95, "#7a9fd6")]), (T["flowers"][1], [(4.65, 5.5, "#d9677a")]),
                     (T["flowers"][2], [(5.65, 6.5, "#9a72c4")]), (T["flowers"][3], [(6.0, 6.9, "#d4b25e")]),
                     (T["flowers"][4], [(7.0, 9.5, "#6aa35a")]), (T["flowers"][5], [(9.0, 9.9, "#c9493a")])])
    body = (place_head("lake", "02", "Lake Kawaguchiko, North Shore", T["title"], T["lead"], 64, nav_url(2)) +
            '<div class="pb">' + stats([("bus", T["s1"], T["s1v"], ""), ("clock", T["s2"], T["s2v"], ""), ("yen", T["s3"], T["s3v"], ""),
                                       ("cal", T["s4"], T["s4v"], "")]) +
            h2(T["flower_h"], "Flower calendar") + fl + src(T["flower_note"]) +
            f'<div class="g2">{card("home", T["c1t"], T["c1"])}{card("trash", T["c2t"], T["c2"], "beige")}</div></div>')
    B.page(body, FOOT["ch3"], "full")


def p_oishi2(B):
    T = B.T["p2b"]
    hours = table(["", T["nov_feb"], T["other"]], [[T["h1"], "9:00–17:15", "—"], [T["h2"], "9:15–16:15", "–16:45"], [T["h3"], "9:00–16:30", "–17:00"]],
                  "", ["", "r", "r"])
    body = (head("Oishi Park — Eat &amp; Shop", T["h"]) +
            f'<div class="g2"><div class="cd">{"<div class=ct>" + icon("cup") + "<b>" + T["cafe_t"] + "</b></div>"}<div class="cx">{T["cafe"]}</div><div class="price">550<small>{T["yen_all"]}</small></div></div>'
            f'<div class="cd"><div class="ct">{icon("cup")}<b>Mt.Fuji View Cafe</b></div><div class="cx">{T["juice"]}</div><div class="price">800<small>{T["yen"]}</small></div></div></div>'
            + card("star", T["kitchen_t"], T["kitchen"], "blue") + src(T["src"]) +
            h2(T["hours_h"], "Hours") + hours + src(T["hours_note"]) +
            f'<div class="photo" style="height:58mm"><img src="{img("spring")}"></div>' + src(T["cap"]))
    B.page(body, FOOT["ch3"])


def p_oshino(B):
    T = B.T["p3"]
    rows = [[f"<b>{a}</b>", b, c] for a, b, c in T["access"]]
    rec = "".join(f'<div class="rc"><b>{y}</b><span>{t}</span></div>' for y, t in zip(["1934", "1985", "2013"], T["rec"]))
    body = (place_head("oshino", "03", "Sacred Springs — Oshino", T["title"], T["lead"], 50, nav_url(3)) +
            f'<div class="pb"><div class="g2 top"><div>{h2(T["how_h"], "How it works")}<div class="flow"><span>{T["how"][0]}</span><i>↓</i>'
            f'<span class="m">{T["how"][1]}</span><i>↓</i><span class="b">{T["how"][2]}</span></div></div>'
            f'<div>{h2(T["rec_h"], "Recognition")}{rec}' + stats([("clock", T["s1"], T["s1v"], T["s1s"]), ("yen", T["s2"], T["s2v"], "")], 2, True) +
            "</div></div>" + h2(T["acc_h"], "Access") + table(T["cols"], rows, "compact") + src(T["src"]) + "</div>")
    B.page(body, FOOT["ch3"], "full")


def p_oshino2(B):
    T = B.T["p3b"]
    hours = "".join(f"<i>{h}</i>" for h in range(8, 18))
    crowd = (f'<div class="crowd"><div class="ch">{hours}</div><div class="cb"><b style="left:{(10.5 - 8) / 10 * 100}%;width:{4 / 10 * 100}%">'
             f'{T["busy"]}</b></div></div>')
    mus = table(T["m_cols"], [["", "<b>300</b>", "150", "100"]], "compact", ["", "r big", "r", "r"])
    body = (head("Oshino Hakkai — Good to Know", T["h"]) + crowd + src(T["crowd_note"]) +
            f'<div class="box">{icon("home")}<b class="bt">{T["m_t"]}</b><p>{T["m"]}</p>{mus}<p class="small">{T["m_note"]}</p></div>'
            f'<div class="g2">{card("child", T["c1t"], T["c1"])}{card("dog", T["c2t"], T["c2"])}'
            f'{card("snow", T["c3t"], T["c3"], "blue")}{card("rule", T["c4t"], T["c4"], "beige")}</div>' + src(T["src"]))
    B.page(body, FOOT["ch3"])


def mini_place(photo, num, en, title, lead, st, nav, cols=4, src_=""):
    return (f'<div class="mp"><div class="mpi"><img src="{img(photo)}"><a class="navqr s" href="{nav}"><img src="{qr(nav)}"><span>NAVI</span></a></div>'
            f'<div class="mpt"><span class="mpn">{num}</span><p class="eb">{en}</p><h1 class="m">{title}</h1><p class="small">{lead}</p></div></div>'
            + stats(st, cols, True) + (src(src_) if src_ else ""))


def p_rope_nenba(B):
    T = B.T["p45"]
    a = mini_place("ropeway", "04", "Mt. Tenjo", T["t4"], T["l4"],
                   [("bus", T["r_s1"], T["r_s1v"], T["r_s1s"]), ("clock", T["s_time"], T["r_s2v"], ""),
                    ("yen", T["r_s3"], "1,200／600", T["r_s3s"]), ("cal", T["r_s4"], "8:30–17:30", T["r_s4s"])], nav_url(4), src_=T["src4"])
    b = mini_place("nenba", "05", "Thatched Village", T["t5"], T["l5"],
                   [("bus", T["n_s1"], T["n_s1v"], T["n_s1s"]), ("clock", T["s_time"], "1–1.5h", ""),
                    ("yen", T["n_s3"], "500／250", T["n_s3s"]), ("cal", T["n_s4"], "9:00–17:00", T["n_s4s"])], nav_url(5), src_=T["src5"])
    B.page(a + '<hr class="sep">' + b, FOOT["ch3"])


def p_fifth_fujiq(B):
    T = B.T["p67"]
    a = mini_place("fifth", "06", "Halfway up the Mountain", T["t6"], T["l6"],
                   [("bus", T["s1"], T["s1v"], ""), ("yen", T["s2"], "2,000" + T["yen"], ""), ("clock", T["s3"], "1.5–2h", "")], nav_url(6), 3)
    rows = [[T["day"], "<b>6,000–7,900</b>", "5,500–7,400", "4,400–5,100", "2,100–2,600"],
            [T["aft"], "<b>4,100–6,000</b>", "3,800–5,700", "3,500–4,200", "1,700–2,100"]]
    b = (f'<div class="wide"><img src="{img("fujiq")}"><a class="navqr s" href="{nav_url(7)}"><img src="{qr(nav_url(7))}"><span>NAVI</span></a></div>'
         f'<div class="mpt row"><span class="mpn">07</span><div><p class="eb">Theme Park</p><h1 class="m">{T["t7"]}</h1></div></div>'
         f'<p class="small">{T["l7"]}</p>' + table(T["cols"], rows, "compact", ["", "r", "r", "r", "r"]) + src(T["note7"]))
    B.page(a + alert(T["warn6"]) + '<hr class="sep">' + b, FOOT["ch3"])


def p_motosu(B):
    T = B.T["p8"]
    tl = timeline([(T["morning"], T["i1t"], T["i1"], True), ("", T["i2t"], T["i2"], False),
                   ("15:30", f'<span class="redt">{T["i3t"]}</span>', T["i3"], True), ("16:45", T["i4t"], T["i4"], True)])
    body = (place_head("motosu", "08", "The 1,000-Yen View", T["title"], T["lead"], 62, nav_url(8)) +
            f'<div class="pb">{h2(T["plan_h"], "Plan it like this")}{tl}' + card("cal", T["fest_t"], T["fest"], "blue") + src(T["src"]) + "</div>")
    B.page(body, FOOT["ch3"], "full")


def p_ch4(B):
    T = B.T["ch4"]
    items = [(t, a, b, i in (0, 5)) for i, (t, a, b) in enumerate(T["a"])]
    extra = (src(T["note"]) + f'<div class="course"><span class="tag red">COURSE A</span><b>{T["a_t"]}</b></div>' + timeline(items))
    B.page(opener("lake", "04", T["title"], extra, h=84), FOOT["ch4"], "opener")


def p_courseB(B):
    T = B.T["cb"]
    items = [(t, a, b, i in (0, 2, 6)) for i, (t, a, b) in enumerate(T["items"])]
    body = (f'<div class="course top"><span class="tag red">COURSE B</span><span class="eb">For Photographers</span></div><h1>{T["title"]}</h1>'
            f'<div class="cbg"><div>{timeline(items)}</div><div class="cbp"><div class="photo" style="height:62mm"><img src="{img("chureito")}"></div>'
            f'<div class="photo" style="height:52mm"><img src="{img("nenba")}"></div>'
            f'<div class="cd pink"><div class="ct">{icon("star")}<b>{T["warn"]}</b></div></div>{card("ticket", T["pass_t"], T["pass"], "beige")}</div></div>')
    B.page(body, FOOT["ch4"])


def p_courseC(B):
    T = B.T["cc"]
    items = [(t, a, b, i in (0, 4)) for i, (t, a, b) in enumerate(T["items"])]
    m1 = table(["", ""], [[T["adult"], "<b>1,500</b>"], [T["hs"], "900"], [T["kid"], "400"]], "compact nohead", ["", "r big"])
    m2 = table(["", T["wd"], T["we"]], [[T["adult"], "<b>1,800</b>", "2,100"], [T["hs"], "1,300", "1,600"], [T["kid"], "1,000", "1,000"]], "compact", ["", "r big", "r"])
    body = (f'<div class="course top"><span class="tag red">COURSE C</span><span class="eb">Rainy Day</span></div><h1>{T["title"]}</h1>'
            + timeline(items) + h2(T["mus_h"], "Museums") +
            f'<div class="g2"><div class="mus"><img src="{img("itchiku")}"><b>{T["m1t"]}</b><p>{T["m1"]}</p>{m1}</div>'
            f'<div class="mus"><img src="{img("music")}"><b>{T["m2t"]}</b><p>{T["m2"]}</p>{m2}</div></div>' + src(T["src"]))
    B.page(body, FOOT["ch4"])


def p_onsen(B):
    T = B.T["onsen"]
    rows = [[f"<b>{a}</b>", b, c] for a, b, c in T["rows"]]
    rows[0] = [f"<b>{T['rows'][0][0]}</b>", f'<span class="ng">{T["rows"][0][1]}</span>', f'<span class="ok">{T["rows"][0][2]}</span>']
    body = (head("Hot Springs", T["h"], T["lead"]) + table(["", T["n1"], T["n2"]], rows, "onsen") + src(T["src"]) +
            f'<div class="photo" style="height:62mm"><img src="{img("spring")}"></div>')
    B.page(body, FOOT["ch4"])


def p_food(B):
    T = B.T["food"]
    steps = "".join(f'<div class="step sm"><span class="sn">{i + 1}</span><div><span>{s}</span></div></div>' for i, s in enumerate(T["order"]))
    body = (f'<div class="ph two" style="height:52mm"><img src="{img("hoto")}"><img src="{img("udon")}"></div><div class="phb">'
            + head("Chapter 05 · Local Food", T["h"]) +
            f'<div class="g2 top"><div>{h2(T["hoto_t"], "Hoto")}<p class="small">{T["hoto"]}</p>'
            f'<div class="cd"><div class="cx">{T["hoto_ex"]}</div><div class="price">1,815<small>{T["yen"]}</small></div>{src(T["hoto_src"])}</div>'
            f'<div class="step sm ic">{icon("bowl", "#fff", 12)}<div><b>{T["eat_t"]}</b><span>{T["eat"]}</span></div></div>'
            f'<div class="step sm ic g">{icon("leaf", "#fff", 12)}<div><b>{T["veg_t"]}</b><span>{T["veg"]}</span></div></div></div>'
            f'<div>{h2(T["udon_t"], "Yoshida Udon")}<p class="small">{T["udon"]}</p>'
            f'<div class="cd"><div class="cx">{T["udon_ex"]}</div>'
            + table(["", ""], [[T["u1"], "<b>" + T["u1p"] + "</b>"], [T["u2"], T["u2p"]]], "compact nohead", ["", "r big"]) + src(T["udon_src"]) +
            f'</div>{h2(T["order_h"], "How to order")}{steps}</div></div></div>')
    B.page(body, FOOT["ch5"], "full")


def p_good(B):
    T = B.T["good"]
    c1 = "".join(card(i, a, b) for (a, b), i in zip(T["crowd"], ["clock", "camera", "cal"]))
    c2 = "".join(card(i, a, b, "beige") for (a, b), i in zip(T["manners"], ["warn", "home", "quiet", "trash"]))
    c3 = "".join(card(i, a, b) for (a, b), i in zip(T["money"], ["card", "wc", "bag"]))
    body = (head("Chapter 06 · Good to Know", T["h"]) + h2(T["crowd_h"], "Beat the crowds") + f'<div class="g3">{c1}</div>' +
            h2(T["manners_h"], "Respect the locals") + f'<p class="small">{T["manners_lead"]}</p><div class="g2">{c2}</div>' +
            h2(T["money_h"], "Money, toilets, bags") + f'<div class="g3">{c3}</div>' + src(T["src"]))
    B.page(body, FOOT["ch6"])


PHRASES_JA = [("こんにちは", "Konnichiwa"), ("ありがとうございます", "Arigatō gozaimasu"), ("すみません", "Sumimasen"),
              ("トイレはどこですか？", "Toire wa doko desu ka?"), ("これはいくらですか？", "Kore wa ikura desu ka?"),
              ("河口湖まで1枚ください", "Kawaguchiko made ichimai kudasai"), ("カードで払えますか？", "Kādo de haraemasu ka?"),
              ("出汁に魚は入っていますか？", "Dashi ni sakana wa haitte imasu ka?")]


def p_phrases(B):
    T = B.T["phr"]
    rows = [[a, f"<b>{j}</b>", r] for a, (j, r) in zip(T["phrases"], PHRASES_JA)]
    chk = "".join(f'<div class="ck"><i></i>{x}</div>' for x in T["check"])
    body = (head("Phrases &amp; Checklist", T["h"]) + table(T["cols"], rows, "phr") +
            h2(T["check_h"], "Packing list") + f'<div class="cks">{chk}</div>'
            f'<div class="photo" style="height:50mm"><img src="{img("motosu")}"></div>')
    B.page(body, FOOT["ch6"])


def p_book(B):
    lang = B.lang
    if lang in ("en", "ja"):
        BN = B.T["bn"]
        names = {k: ((nj, dj) if lang == "ja" else (ne, de)) for k, ne, nj, de, dj, _, _ in BOOKING}
    else:
        BN, names = i18n.BN[lang], i18n.BOOK_NAMES[lang]
    cells = "".join(
        f'<a class="q" href="{url}"><img src="{qr(url)}"><div><b>{names[key][0]}</b><span>{names[key][1]}</span>'
        f'<em>{url.replace("https://", "")}</em></div></a>' for key, *_, url, _ in BOOKING)
    chk = B.T["bn"].get("check", "") if REVIEW[0] else ""  # note to Tama, only in her review copy
    chk = f'<div class="alert">{icon("warn")}<div>{chk}</div></div>' if chk else ""
    body = (head("Book &amp; Navigate", BN["h_book"], BN["lead_book"]) + chk + f'<div class="qg">{cells}</div>' + src(BN["fc"]))
    B.page(body, FOOT["bonus"])
    pn = [nj if lang == "ja" else ne for _, ne, nj, _ in PLACES] if lang in ("en", "ja") else i18n.PLACE_NAMES[lang]
    cells = "".join(
        f'<a class="q n" href="{maps_url(q_)}"><img src="{qr(maps_url(q_))}"><div><b>{m} {nm}</b><span>{BN["open"]}</span></div></a>'
        for (m, _, _, q_), nm in zip(PLACES, pn))
    B.page(head("Navigation", BN["h_nav"], BN["lead_nav"]) + f'<div class="qg">{cells}</div>', FOOT["bonus"])


def p_map(B):
    T = B.T["qmap"]
    cx, cy = 260, 268
    spokes = [  # (num, angle deg, color, dashed)
        (4, -90, RED, False), (2, -40, RED, False), (5, 5, GREEN, False), (8, 50, BLUE, False),
        (6, 90, "#1b1b1b", True), (3, 130, GREY, False), (7, 175, ORANGE, False), (1, 220, ORANGE, False)]
    import math
    s = f'<svg viewBox="0 0 520 530" class="qmap"><g font-size="12" fill="#2a2620" text-anchor="middle" stroke="#f6f2ea" stroke-width="4" paint-order="stroke">'
    for n, a, col, dash in spokes:
        r = 190
        x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        d = ' stroke-dasharray="6 6"' if dash else ""
        s += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{col}" stroke-width="8"{d}/>'
        s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="24" fill="#fff" stroke="{col}" stroke-width="4"/>'
        s += f'<text x="{x:.0f}" y="{y + 5:.0f}" font-size="14">{"①②③④⑤⑥⑦⑧"[n - 1]}</text>'
        name, how = T["spots"][n - 1]
        ty = y + 44 if a > 20 and a < 160 else y - 48 if (a < -20 and a > -160) else y + 44
        if n == 4:
            ty = y - 52
        s += f'<text x="{x:.0f}" y="{ty:.0f}" font-weight="700" font-size="13">{name}</text><text x="{x:.0f}" y="{ty + 16:.0f}" font-size="10.5" fill="#6d665c">{how}</text>'
    s += f'<circle cx="{cx}" cy="{cy}" r="50" fill="#1b1b1b"/><text x="{cx}" y="{cy}" fill="#fff" stroke="none" font-size="{17 if len(T["station"]) < 8 else 11.5}" font-weight="700">{T["station"]}</text>'
    s += f'<text x="{cx}" y="{cy + 20}" fill="#ddd" stroke="none" font-size="{10 if len(T["station_s"]) < 12 else 7.5}">{T["station_s"]}</text></g></svg>'
    leg = "".join(f'<span><i style="background:{c}"></i>{t}</span>' for t, c in zip(T["legend"], [RED, GREEN, BLUE, ORANGE, GREY, "#1b1b1b"]))
    body = (head("Bonus · Quick Map", T["h"]) + s + f'<div class="leg2">{leg}</div>' + note("TO TOKYO", T["tokyo"]) + src(T["note"]))
    B.page(body, FOOT["map"])


# ---------------------------------------------------------------- whole book
def language_book(lang, chart_html, know_rows):
    T = load_text(lang)
    B = Book(lang, T)
    toc_pages = [5, 7, 16, 25, 29, 30, 3, 4, 32, 34]  # chapters 1-6, then know, finder, book, map
    p_cover(B)
    p_welcome(B, toc_pages)
    p_know(B, know_rows)
    p_finder(B, chart_html)
    p_ch1(B); p_when(B)
    p_ch2(B); p_train(B); p_timetable(B); p_passes(B); p_bus(B); p_around(B); p_buspass(B); p_passport(B); p_looptimes(B)
    p_eight(B); p_chureito(B); p_oishi(B); p_oishi2(B); p_oshino(B); p_oshino2(B); p_rope_nenba(B); p_fifth_fujiq(B); p_motosu(B)
    p_ch4(B); p_courseB(B); p_courseC(B); p_onsen(B)
    p_food(B); p_good(B); p_phrases(B)
    p_book(B); p_map(B)
    # anchors for the table of contents
    out = []
    for i, pg in enumerate(B.pages, 1):
        out.append(pg.replace('<section class="pg', f'<section data-p="{i}" id="{lang}-p{i}" class="pg', 1)
                   if f'id="lang-{lang}"' not in pg else pg)
    return f'<div class="L L-{lang}" lang="{lang}">{"".join(out)}</div>'


def load_text(lang):
    mod = importlib.import_module("text." + lang.replace("-", "_"))
    return mod.T


FONT_FACES = "".join(
    f'@font-face {{ font-family: "{fam}"; src: url("{(FONTS / f).as_uri()}"); font-weight: {w}; font-style: {s}; }}\n'
    for fam, f, w, s in [("Shippori Mincho", "ShipporiMincho-Medium.ttf", 500, "normal"),
                         ("Shippori Mincho", "ShipporiMincho-Bold.ttf", 700, "normal"),
                         ("Shippori Mincho", "ShipporiMincho-ExtraBold.ttf", 800, "normal"),
                         ("Cormorant Garamond", "CormorantGaramond-MediumItalic.ttf", 500, "italic"),
                         ("Cormorant Garamond", "CormorantGaramond-SemiBoldItalic.ttf", 600, "italic"),
                         ("Cormorant Garamond", "CormorantGaramond-Medium.ttf", 500, "normal")])

CSS = (HERE / "magazine.css").read_text(encoding="utf-8") if (HERE / "magazine.css").exists() else ""


def picker_pages():
    rows = "".join(
        f'<a class="lang" href="#lang-{code}"><span class="flag">{flags}</span><span class="nm">{name}</span><span class="go">{go}</span></a>'
        for code, name, flags, _, go in i18n.LANGS)
    T = load_text("en")["cover"]
    names = " · ".join(f"{flags} {name}" for _, name, flags, _, _ in i18n.LANGS)
    st = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in T["stats"])
    cover = (f'<section class="pg cover"><div class="in"><img class="cv" src="{img("cover")}"><div class="cvs"></div>'
             f'<div class="cvtop"><span>DAY TRIP FROM TOKYO</span><span>2026 EDITION</span></div><div class="cvlangs">{names}</div>'
             f'<div class="cvt"><div class="cvk">{T["kicker"]}</div><div class="cvbig">Fuji</div>'
             f'<div class="cvh">{T["h1"]}</div><div class="cved">{T["ed"]}</div></div><div class="cvst">{st}</div></div></section>')
    pick = (f'<section class="pg picker" id="languages"><div class="in"><p class="eb">Language · 언어 · 語言 · 语言 · ภาษา · Ngôn ngữ · Bahasa · 言語</p>'
            f'<h1>Choose your language</h1><p class="lead">언어를 선택하세요 · 選擇語言 · 选择语言 · เลือกภาษา · Chọn ngôn ngữ · Pilih bahasa · 言語を選んでください — tap to jump</p>'
            f'{rows}</div></section>')
    return f'<div class="L L-en" lang="en">{cover}{pick}</div>'


def credits_page():
    rows = "".join(f"<tr><td>{u}</td><td>{a}</td><td>{l}</td></tr>" for f, a, l, u, _ in ph.PHOTOS.values())
    return ('<div class="L L-en" lang="en"><section class="pg"><div class="in"><p class="eb">Credits</p><h1>Photo credits</h1>'
            '<p class="small">Photos from Wikimedia Commons, used under the licences shown (CC0 = no rights reserved; CC BY / CC BY-SA: '
            'creativecommons.org/licenses). Some photos are cropped; the destination sign and number plate on the highway bus photo are blurred.</p>'
            f'<table class="tb compact"><thead><tr><th>Used for</th><th>Photographer</th><th>Licence</th></tr></thead><tbody>{rows}</tbody></table>'
            '<div class="note"><span class="nl">DISCLAIMER</span><div>This is an independent travel guide. It is not connected with any company or place in it. '
            'Prices, times and opening hours were checked in November 2026. Please check the official websites before you go.</div></div>'
            '</div><div class="foot"><span>CREDITS</span><span></span></div></section></div>')


def know_rows(lang):
    import re
    folder = {"ja": "ja-review"}.get(lang, lang)
    files = sorted((HERE / folder).glob("00_*.md"))
    if not files and lang == "zh-hant":
        files = sorted((HERE / "zh-hant").glob("00_*.md"))
    rows = []
    for line in files[0].read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|(.*)\|\s*(\d)\s*\|\s*$", line)
        if m:
            txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", m.group(2).strip())
            rows.append((m.group(1), txt, m.group(3)))
    return rows


SINGLE = [False]  # True while building a one-language book
REVIEW = [False]  # True while building Tama's Japanese review copy


def build(ja=False, only=None):
    SINGLE[0] = bool(ja or only)
    REVIEW[0] = bool(ja)
    import chart
    langs = ["ja"] if ja else [only] if only else [c for c, *_ in i18n.LANGS]
    body = "" if (ja or only) else picker_pages()
    for lang in langs:
        T = load_text(lang)
        fd = T["finder"]
        ch = chart.chart(lang, fd["title"], fd["tips"], i18n.to_hant)
        body += language_book(lang, ch, know_rows(lang))
    body += credits_page()
    css = (HERE / "magazine.css").read_text(encoding="utf-8")
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>Mt. Fuji Guide</title><style>{FONT_FACES}{css}{chart.CSS}</style></head><body>{body}</body></html>'
    DIST.mkdir(exist_ok=True)
    name = "magazine-ja-review" if ja else f"magazine-{only}" if only else "magazine"
    out_html, out_pdf = DIST / f"{name}.html", DIST / f"{name}.pdf"
    # Auto-fit: a page whose content runs past the footer gets smaller text and photos, step by step.
    import json
    level = {}
    for _ in range(6):
        fit = "".join(
            f"#{pid} {{ --fs: calc(var(--fs0) - {0.28 * k:.2f}pt); }} "
            f"#{pid} .ph, #{pid} .photo {{ max-height: {max(30, 60 - 7 * k)}mm; }} #{pid} .mpi {{ height: {max(38, 58 - 5 * k)}mm; }} "
            f"#{pid} h1 {{ font-size: {max(12, 16.5 - .8 * k)}pt; }} #{pid} .lead {{ line-height: {max(1.55, 1.9 - .1 * k)}; }}"
            for pid, k in level.items())
        out_html.write_text(html.replace("</style>", fit + "</style>", 1), encoding="utf-8")
        res = subprocess.run(["node", str(HERE / "check_overflow.js"), str(out_html)], capture_output=True, text=True)
        over = [r for r in json.loads(res.stdout or "[]") if r[0]]
        if not over:
            break
        for pid, _, px, _ in over:
            level[pid] = level.get(pid, 0) + 1
    if over:
        print("STILL OVERFLOWING:", over)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", out_html.as_uri()], check=True, capture_output=True)
    finish_pdf(out_pdf, langs, with_picker=not SINGLE[0])
    print(out_pdf)
    return out_html, out_pdf


def finish_pdf(pdf, langs, with_picker):
    """Add a bookmark list (language → chapters) for the viewer's side panel, and compress the file."""
    import pymupdf
    doc = pymupdf.open(pdf)
    toc, start = [], 1
    if with_picker:
        toc.append([1, "Choose your language · 언어 · 語言 · 语言 · ภาษา · Ngôn ngữ · Bahasa · 言語", 2])
        start = 3
    names = {c: n for c, n, *_ in i18n.LANGS}
    if REVIEW[0]:
        names["ja"] = "日本語（確認用）"
    for code in langs:
        W = load_text(code)["welcome"]
        toc.append([1, names[code], start])
        items = [(W["extra"][0], 3), (W["extra"][1], 4)] + [(t, n) for (t, _), n in zip(W["toc"], [5, 7, 16, 25, 29, 30])] + \
                [(W["extra"][2], 32), (W["extra"][3], 34)]
        toc += [[2, t.replace("&amp;", "&"), start + n - 1] for t, n in items]
        start += 34
    toc.append([1, "Photo credits", start])
    doc.set_toc(toc)
    tmp = pdf.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, use_objstms=1)
    doc.close()
    tmp.replace(pdf)


RELEASE_NAMES = {"ja": "Japanese-日本語", "ko": "Korean-한국어", "zh-hant": "TraditionalChinese-繁體中文", "zh-hans": "SimplifiedChinese-简体中文",
                 "en": "English", "th": "Thai-ภาษาไทย", "vi": "Vietnamese-TiengViet", "ms": "Malay-BahasaMelayu"}


def build_split():
    """One PDF per language: each file has only that language's pages (plus the photo credits)."""
    import shutil
    out = HERE.parent.parent / "mt-fuji-guide-by-language"
    out.mkdir(exist_ok=True)
    for code, *_ in i18n.LANGS:
        _, pdf = build(only=code)
        shutil.copy(pdf, out / f"Mt-Fuji-Guide-{RELEASE_NAMES[code]}.pdf")
    print(out)


if __name__ == "__main__":
    if "--split" in sys.argv:
        build_split()
        sys.exit()
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    build(ja="--ja" in sys.argv, only=only)
