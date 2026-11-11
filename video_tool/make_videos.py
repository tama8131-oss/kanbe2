#!/usr/bin/env python3
"""
Amazon配送ドライバー募集用ショート動画（1080x1920 / mp4）の自動生成ツール

使い方:
    python3 make_videos.py              # scripts/ の YAML を全部動画にする
    python3 make_videos.py scripts/xx.yaml   # 1本だけ作る
    python3 make_videos.py --preview    # 音声なしで画面の見た目（PNG）だけ確認

使うもの: Python / Pillow / PyYAML / ffmpeg / VOICEVOX Engine（すべて無料）
"""
import argparse
import datetime
import io
import json
import re
import math
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFont

import audio_fx

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

W, H = 1080, 1920
FPS = 30
BG = (220, 235, 245)
FG = (35, 57, 91)
WHITE = (255, 255, 255)

# 動画ごとに背景の色を変える（毎回同じ見た目で飛ばされるのを防ぐ）
# YAML に theme: 0〜4 を書けばその色、書かなければ作る順番で自動で回す
THEMES = [
    (220, 235, 245),  # 水色
    (252, 241, 214),  # クリーム
    (222, 242, 226),  # ミント
    (250, 228, 226),  # ピンク
    (232, 228, 248),  # ラベンダー
]
LINE_COLOR = (190, 205, 220)

HEADLINE = "Amazon配送ドライバーのリアル"
AI_LABEL = "AI生成"
SAIGEN_LABEL = "再現"
CHARA_LABEL = "配送ドライバー"
END_TEXT = "条件は\nプロフィールの\n固定投稿へ"
END_SECONDS = 2.0

VOICEVOX_URL = "http://127.0.0.1:50021"
SPEAKER_NAME = "玄野武宏"
STYLE_NAME = "ノーマル"
SPEED_SCALE = 1.1

LEAD_SILENCE = 0.15   # セリフの前の無音（秒）
TAIL_SILENCE = 0.35   # セリフの後の無音（秒）

DISCLAIMER = [
    "※記載の金額は、実際に働いているドライバーの実績をもとにした目安です。",
    "※収入は働く日数・時間・配達件数などによって、人によって大きく変わります。平均より多く稼ぐ人もいれば、少ない人もいます。",
    "※記載の金額を保証するものではありません。",
]
# 声のクレジット（VOICEVOXの決まりで表記が必要）。投稿文には書かず、動画の画面に出す（たまさんの希望）
VOICE_CREDIT = "VOICEVOX:玄野武宏"
POST_FOOTER = ["この動画はAIで作っています"]
MAX_HASHTAGS = 5  # インスタのハッシュタグは5個まで

# 「1日の流れ」の型では画面に「再現」と出す
SAIGEN_TYPES = {"1日の流れ"}

FONT_CANDIDATES = [
    BASE_DIR / "fonts" / "NotoSansCJKjp-Bold.otf",
    BASE_DIR / "fonts" / "NotoSansCJK-Bold.ttc",
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc"),
    Path("/System/Library/Fonts/NotoSansCJK-Bold.ttc"),
    Path("/Library/Fonts/NotoSansCJKjp-Bold.otf"),
    Path.home() / "Library/Fonts/NotoSansCJKjp-Bold.otf",
    Path("C:/Windows/Fonts/NotoSansCJKjp-Bold.otf"),
    Path.home() / "AppData/Local/Microsoft/Windows/Fonts/NotoSansCJKjp-Bold.otf",
]


class UserError(Exception):
    """たまさん向けの分かりやすいエラー"""


# ---------------------------------------------------------------------------
# フォント
# ---------------------------------------------------------------------------
_font_path = None
_font_cache = {}


def font(size):
    global _font_path
    if _font_path is None:
        for p in FONT_CANDIDATES:
            if p.exists():
                _font_path = p
                break
        else:
            raise UserError(
                "フォント「Noto Sans CJK Bold」が見つかりません。\n"
                "README の「フォントを入れる」の手順を見てください。"
            )
    if size not in _font_cache:
        # .ttc の 0 番目は日本語(JP)
        _font_cache[size] = ImageFont.truetype(str(_font_path), size, index=0)
    return _font_cache[size]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


# 行頭に来てほしくない文字
NO_LINE_START = set("、。，．・：；？！ー）」』】〉》〕｝’”ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ%％,.)]!?")


def wrap(draw, s, f, max_w):
    """日本語の折り返し（1文字ずつ詰めて、行頭禁則を少しだけ守る）"""
    lines = []
    for para in s.split("\n"):
        cur = ""
        for ch in para:
            if text_w(draw, cur + ch, f) <= max_w or not cur:
                cur += ch
            elif ch in NO_LINE_START:
                # 句読点などは前の行にぶら下げる
                cur += ch
            else:
                lines.append(cur)
                cur = ch
        lines.append(cur)
    return lines


def wrap_balanced(draw, s, f, max_w):
    """行数は変えずに、各行の長さをなるべくそろえる（最後に1〜2文字だけ残るのを防ぐ）"""
    lines = wrap(draw, s, f, max_w)
    if len(lines) <= 1:
        return lines
    lo, hi = 1, int(max_w)
    while lo < hi:
        mid = (lo + hi) // 2
        if len(wrap(draw, s, f, mid)) <= len(lines):
            hi = mid
        else:
            lo = mid + 1
    return wrap(draw, s, f, lo)


def draw_centered_lines(draw, lines, f, cx, top, line_h, fill):
    for i, ln in enumerate(lines):
        w = text_w(draw, ln, f)
        draw.text((cx - w / 2, top + i * line_h), ln, font=f, fill=fill)


# ---------------------------------------------------------------------------
# キャラ「はこぶ」
# ---------------------------------------------------------------------------
_chara = None


def chara_image():
    """SVGから作ったPNGに、Pillowで「配送ドライバー」のラベルを描く"""
    global _chara
    if _chara is not None:
        return _chara
    base_png = ASSETS_DIR / "hakobu_base.png"
    if not base_png.exists():
        svg_to_png(ASSETS_DIR / "hakobu.svg", base_png)
    im = Image.open(base_png).convert("RGBA")
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 385, 712, 695, 796
    d.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=WHITE,
                        outline=(0x3A, 0x2A, 0x1C), width=6)
    f = font(42)
    bbox = d.textbbox((0, 0), CHARA_LABEL, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((x0 + x1) / 2 - tw / 2 - bbox[0], (y0 + y1) / 2 - th / 2 - bbox[1]),
           CHARA_LABEL, font=f, fill=FG)
    _chara = im
    return im


FACE = (0xC8, 0x95, 0x5A)
LINE = (0x3A, 0x2A, 0x1C)
_variants = {}


def chara_variants():
    """はこぶの表情4種類（ふつう／口あけ／まばたき／まばたき＋口あけ）を、動画用の大きさで返す"""
    if _variants:
        return _variants
    base = chara_image()

    def mouth_open(im):
        d = ImageDraw.Draw(im)
        d.rectangle((488, 643, 592, 692), fill=FACE)
        d.ellipse((514, 650, 566, 702), fill=LINE)
        d.ellipse((524, 676, 556, 698), fill=(0xE9, 0x8A, 0x7A))

    def blink(im):
        d = ImageDraw.Draw(im)
        for cx in (465, 615):
            d.rectangle((cx - 28, 572, cx + 28, 628), fill=FACE)
            d.arc((cx - 24, 584, cx + 24, 616), start=20, end=160, fill=LINE, width=8)

    size = int(1080 * CHARA_SCALE)
    for name, fns in {"normal": [], "open": [mouth_open], "blink": [blink],
                      "blink_open": [blink, mouth_open]}.items():
        im = base.copy()
        for fn in fns:
            fn(im)
        _variants[name] = im.resize((size, size), Image.LANCZOS)
    return _variants


def chara_pos():
    content_cx = (220 + 920) / 2 * CHARA_SCALE  # 絵の左右の中心
    bottom = 964 * CHARA_SCALE                  # 影の下端
    return int(W / 2 - content_cx), int(H - 30 - bottom)


def svg_to_png(svg, png):
    """hakobu_base.png が消えたときだけ使う（通常は同梱のPNGを使う）"""
    try:
        import cairosvg  # 無料のライブラリ。普段は不要
    except ImportError:
        raise UserError("assets/hakobu_base.png がありません。リポジトリから取り直してください。")
    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=1080, output_height=1080)


# ---------------------------------------------------------------------------
# 画面づくり（プロ仕様）
#   - セリフは「ひと息」ごとに字幕を切り替え、声とぴったり合わせる
#   - 大事な言葉と数字は色を変えて目立たせる
#   - 字幕はポンッと飛び出す。背景のしま模様はゆっくり流れる
#   - 上に進み具合のバー。最後は「名前をタップ」の矢印が跳ねる
# ---------------------------------------------------------------------------
CHARA_SCALE = 0.68
ACCENT = (228, 87, 46)          # 白い枠の上の強調色（朱色）
ACCENT_ON_DARK = (255, 209, 102)  # 濃い枠の上の強調色（黄色）
SHADOW = (0, 0, 0, 45)

# 自動で目立たせる言葉（確認済みの条件の言い回し）
KEYWORDS = [
    "上司も同僚もいない", "ひとりで黙々", "経験ゼロ", "未経験", "外国籍", "持ち帰れ", "貸してもらえ",
    "OK", "関東", "固定投稿", "DM", "正直", "人間関係", "お金", "タダではありません", "3つの理由",
    "個人事業主", "ビザ",
]
NUM_RE = re.compile(r"月?約?[0-9０-９][0-9０-９,，.]*(万[0-9０-９,，]*)?円?")


def emphasis_index(text, extra=()):
    marks = set()
    for kw in list(KEYWORDS) + list(extra):
        start = 0
        while True:
            i = text.find(kw, start)
            if i < 0:
                break
            marks.update(range(i, i + len(kw)))
            start = i + 1
    for m in NUM_RE.finditer(text):
        if any(c.isdigit() for c in m.group()):
            marks.update(range(m.start(), m.end()))
    return marks


def rich_lines(d, text, f, max_w, marks):
    lines = wrap_balanced(d, text, f, max_w)
    out, i = [], 0
    for ln in lines:
        out.append([(ch, (i + k) in marks) for k, ch in enumerate(ln)])
        i += len(ln)
    return out


def draw_rich(d, lines, f, cx, top, line_h, color, ecolor):
    for li, ln in enumerate(lines):
        s = "".join(c for c, _ in ln)
        x = cx - d.textlength(s, font=f) / 2
        y = top + li * line_h
        run, flag = "", None
        for c, e in ln + [(None, None)]:
            if c is None or e != flag:
                if run:
                    d.text((x, y), run, font=f, fill=ecolor if flag else color)
                    x += d.textlength(run, font=f)
                run, flag = (c or ""), e
            else:
                run += c


def split_chunks(text):
    """ひと息ごとに分ける（文の終わり。長い文は真ん中あたりの読点でも分ける）"""
    sents = [s for s in re.findall(r"[^。！？!?]+[。！？!?]?", text) if s.strip()]
    out = []
    for s in sents:
        if len(s) > 24 and "、" in s[:-1]:
            mid = len(s) / 2
            cands = [i for i, c in enumerate(s[:-1]) if c == "、"]
            cut = min(cands, key=lambda i: abs(i - mid)) + 1
            out += [s[:cut], s[cut:]]
        else:
            out.append(s)
    return out or [text]


def make_bg_strip(bg):
    """斜めのしま模様（横に流すので少し広めに作る）"""
    period = 120
    im = Image.new("RGB", (W + period, H), bg)
    d = ImageDraw.Draw(im)
    light = tuple(min(255, int(c + (255 - c) * 0.35)) for c in bg)
    for x0 in range(-H, W + period, period):
        d.polygon([(x0, 0), (x0 + 50, 0), (x0 + 50 + H, H), (x0 + H, H)], fill=light)
    return im, period


def header_layer(saigen):
    im = Image.new("RGBA", (W, 240), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((48, 56), HEADLINE, font=font(54), fill=FG)
    f = font(36)
    tw = text_w(d, AI_LABEL, f)
    x1 = W - 40
    x0 = x1 - tw - 44
    d.rounded_rectangle((x0, 50, x1, 118), radius=16, fill=FG)
    d.text((x0 + 22, 56), AI_LABEL, font=f, fill=WHITE)
    f = font(24)
    d.text((W - 40 - text_w(d, VOICE_CREDIT, f), 128), VOICE_CREDIT, font=f, fill=FG)
    if saigen:
        f = font(36)
        tw = text_w(d, SAIGEN_LABEL, f)
        d.rounded_rectangle((48, 140, 48 + tw + 44, 208), radius=16, fill=WHITE, outline=FG, width=4)
        d.text((48 + 22, 146), SAIGEN_LABEL, font=f, fill=FG)
    return im


def box_layer(text, hook=False, label=None, extra=(), end_card=False):
    """字幕の枠（影つき）。中心に置く前提で RGBA を返す"""
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    if end_card:
        f, line_h = font(84), 120
        lines = [[(c, False) for c in ln] for ln in END_TEXT.split("\n")]
    elif hook:
        f, line_h = font(78), 110
        lines = rich_lines(tmp, text, f, 880, emphasis_index(text, extra))
    else:
        f, line_h = font(64), 94
        lines = rich_lines(tmp, text, f, 860, emphasis_index(text, extra))
    bw = W - 120
    bh = len(lines) * line_h + 90
    pad_top = 40 if label else 0
    im = Image.new("RGBA", (bw + 16, bh + 16 + pad_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, pad_top + 12, bw + 10, pad_top + bh + 12), radius=40, fill=SHADOW)
    dark = hook or end_card
    fill, color, ecolor = (FG, WHITE, ACCENT_ON_DARK) if dark else (WHITE, FG, ACCENT)
    d.rounded_rectangle((0, pad_top, bw, pad_top + bh), radius=40, fill=fill)
    draw_rich(d, lines, f, bw / 2, pad_top + 40, line_h, color, ecolor)
    if label:
        lf = font(44)
        lw = max(text_w(d, label, lf), 44)
        d.rounded_rectangle((30, 0, 30 + lw + 56, 76), radius=38, fill=ACCENT)
        d.text((30 + 28 + (lw - text_w(d, label, lf)) / 2, 8), label, font=lf, fill=WHITE)
    return im


def table_layer(table):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_table(ImageDraw.Draw(im), table)
    box = im.getbbox()
    return im.crop(box), (box[0], box[1])


def disclaimer_layer():
    im = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font(27)
    y = 0
    for para in DISCLAIMER:
        for ln in wrap(d, para, f, W - 120):
            d.text((60, y), ln, font=f, fill=FG)
            y += 38
    return im.crop((0, 0, W, y + 4))


def tap_pointer_layer():
    """最後の2秒に出す「名前をタップ」の吹き出し（下向き矢印つき）"""
    f = font(34)
    text = "名前をタップ"
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = text_w(tmp, text, f)
    w, h = int(tw + 60), 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w, 68), radius=34, fill=ACCENT)
    d.text((30, 10), text, font=f, fill=WHITE)
    d.polygon([(36, 66), (90, 66), (63, 124)], fill=ACCENT)
    return im


def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def paste(frame, layer, xy):
    frame.paste(layer, (int(xy[0]), int(xy[1])), layer)


class Timeline:
    """字幕ひとつぶんの区切り（ひと息）を並べたもの"""

    def __init__(self):
        self.items = []  # dict(start, end, line, box, label, table, first_table, new_line, end_card)

    def bounds(self):
        return np.array([it["end"] for it in self.items])


def compose_frame(k, tl, ctx):
    t = k / FPS
    bounds = ctx["bounds"]
    idx = min(int(np.searchsorted(bounds, t, side="right")), len(tl.items) - 1)
    it = tl.items[idx]
    since = t - it["start"]
    f_since = int(since * FPS)

    off = int(t * 24) % ctx["period"]
    frame = ctx["strip"].crop((off, 0, off + W, H))
    paste(frame, ctx["header"], (0, 0))

    # 表（最初に出るときだけ上からスッと入る）
    if it["table"] is not None:
        layer, (tx, ty) = it["table"]
        if it["first_table"] and f_since < 9:
            p = (f_since + 1) / 9
            a = layer.copy()
            alpha = a.getchannel("A").point(lambda v, p=p: int(v * p))
            a.putalpha(alpha)
            paste(frame, a, (tx, ty - 60 * (1 - p)))
        else:
            paste(frame, layer, (tx, ty))

    # 字幕（ポンッと出る）
    box = it["box"]
    cy = 1010 if it["table"] is not None else 760
    if f_since < 8:
        s = 0.55 + 0.45 * ease_out_back(min(1.0, (f_since + 1) / 8))
        bw, bh = max(1, int(box.width * s)), max(1, int(box.height * s))
        b = box.resize((bw, bh), Image.BILINEAR)
    else:
        b = box
    paste(frame, b, (W / 2 - b.width / 2, cy - b.height / 2))

    if ctx["disclaimer"] is not None:
        paste(frame, ctx["disclaimer"], (0, 1222 if not it["end_card"] else 1060))

    # 最後：名前をタップ
    if it["end_card"]:
        ptr = ctx["pointer"]
        bounce = abs(math.sin(2 * math.pi * 1.6 * since)) * 24
        paste(frame, ptr, (20, 1470 + bounce))

    # はこぶ
    talking = ctx["loud"][min(k, len(ctx["loud"]) - 1)] > ctx["threshold"] and (k // 3) % 2 == 0
    blinking = (k % 105) in (0, 1, 2)
    name = ("blink_" if blinking else "") + ("open" if talking else "normal")
    name = name.replace("blink_normal", "blink")
    ch = ctx["variants"][name]
    px, py = ctx["chara_pos"]
    dy = 10 * math.sin(2 * math.pi * 0.9 * t)
    if f_since < 9 and it["new_line"]:
        dy -= 34 * math.sin(math.pi * f_since / 9)  # セリフが変わるとき、ぴょんと跳ねる
    paste(frame, ch, (px, py + dy))

    # 進み具合のバー
    d = ImageDraw.Draw(frame)
    d.rectangle((0, 0, int(W * min(1.0, t / ctx["total"])), 10), fill=ACCENT)
    return frame


def draw_table(d, table):
    rows = table["rows"]
    highlight_last = table.get("highlight_last", True)
    x0, x1 = 70, W - 70
    y = 250
    if table.get("title"):
        f = font(48)
        d.text((x0, y), table["title"], font=f, fill=FG)
        y += 80
    row_h = 130
    fl, fv = font(46), font(66)
    n = len(rows)
    total_h = row_h * n
    d.rounded_rectangle((x0, y, x1, y + total_h), radius=20, fill=WHITE)
    for i, (label, value) in enumerate(rows):
        ry = y + i * row_h
        is_total = highlight_last and i == n - 1
        if is_total:
            # 最後の行（合計）は濃い色で強調
            d.rounded_rectangle((x0, ry, x1, ry + row_h), radius=20, fill=FG)
            if n > 1:
                d.rectangle((x0, ry, x1, ry + 20), fill=FG)
            color = WHITE
        else:
            color = FG
            if i > 0:
                d.line((x0 + 24, ry, x1 - 24, ry), fill=LINE_COLOR, width=3)
        cy = ry + row_h / 2
        lb = d.textbbox((0, 0), label, font=fl)
        d.text((x0 + 32, cy - (lb[3] + lb[1]) / 2), label, font=fl, fill=color)
        vb = d.textbbox((0, 0), value, font=fv)
        d.text((x1 - 32 - (vb[2] - vb[0]) - vb[0], cy - (vb[3] + vb[1]) / 2),
               value, font=fv, fill=color)
    y += total_h + 22
    # 表の下：どの地域・どの条件の例か
    f = font(34)
    for ln in wrap(d, table["note"], f, x1 - x0):
        d.text((x0, y), ln, font=f, fill=FG)
        y += 48


# ---------------------------------------------------------------------------
# YAML の読み込みとチェック
# ---------------------------------------------------------------------------
def must_str(v, where):
    # 数字を "" で囲まないと YAML が勝手に数値に変えてしまうことがあるので、文字以外は止める
    if not isinstance(v, str):
        raise UserError(f"{where} が文字になっていません（値: {v!r}）。\n"
                        f"数字や記号を含むときは \"7万6,000円\" のように \" \" で囲んでください。")
    return v


def load_script(path):
    with open(path, encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    name = Path(path).name
    if not isinstance(data, dict):
        raise UserError(f"{name}: 中身が空か、書き方がまちがっています。")
    for key in ("title", "lines", "caption"):
        if key not in data:
            raise UserError(f"{name}: 「{key}」がありません。")
    must_str(data["title"], f"{name} の title")
    must_str(data["caption"], f"{name} の caption")
    tags = [w for w in data["caption"].split() if w.startswith(("#", "＃"))]
    if len(tags) > MAX_HASHTAGS:
        raise UserError(f"{name}: ハッシュタグが{len(tags)}個あります。インスタは{MAX_HASHTAGS}個までなので減らしてください。")
    for e in data.get("emphasis", []):
        must_str(e, f"{name} の emphasis")
    if not isinstance(data["lines"], list) or not data["lines"]:
        raise UserError(f"{name}: lines にセリフが1つもありません。")
    for i, ln in enumerate(data["lines"], 1):
        where = f"{name} の {i}番目のセリフ"
        if not isinstance(ln, dict) or "text" not in ln:
            raise UserError(f"{where}: text がありません。")
        must_str(ln["text"], f"{where} の text")
        if "yomi" in ln:
            must_str(ln["yomi"], f"{where} の yomi")
        if "label" in ln:
            must_str(ln["label"], f"{where} の label")
        t = ln.get("table")
        if t is not None:
            if not isinstance(t, dict) or "rows" not in t:
                raise UserError(f"{where}: table に rows がありません。")
            if "note" not in t:
                raise UserError(f"{where}: table に note（どの地域・どの条件の例か）がありません。必ず書いてください。")
            must_str(t["note"], f"{where} の table の note")
            if "title" in t:
                must_str(t["title"], f"{where} の table の title")
            for r in t["rows"]:
                if not isinstance(r, list) or len(r) != 2:
                    raise UserError(f"{where}: table の rows は [\"項目\", \"金額\"] の形で書いてください。")
                must_str(r[0], f"{where} の表の項目")
                must_str(r[1], f"{where} の表の金額")
    return data


def is_money_video(data):
    if "kingaku" in data:
        return bool(data["kingaku"])
    if any(ln.get("table") for ln in data["lines"]):
        return True
    return any("円" in ln["text"] for ln in data["lines"])


# ---------------------------------------------------------------------------
# VOICEVOX
# ---------------------------------------------------------------------------
def http(method, path, params=None, body=None):
    url = VOICEVOX_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {}
    if body is not None:
        body = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.URLError as e:
        raise UserError(
            "VOICEVOX につながりません。\n"
            "VOICEVOX を先に起動してください（README の手順を見てください）。\n"
            f"（くわしい内容: {e}）"
        )


def find_speaker_id():
    speakers = json.loads(http("GET", "/speakers"))
    for sp in speakers:
        if sp["name"] == SPEAKER_NAME:
            for st in sp["styles"]:
                if st["name"] == STYLE_NAME:
                    return st["id"]
    raise UserError(f"VOICEVOX に「{SPEAKER_NAME}（{STYLE_NAME}）」が見つかりません。")


def synthesize(text, speaker_id):
    q = json.loads(http("POST", "/audio_query", {"text": text, "speaker": speaker_id}))
    q["speedScale"] = SPEED_SCALE
    q["prePhonemeLength"] = 0.05
    q["postPhonemeLength"] = 0.05
    return http("POST", "/synthesis", {"speaker": speaker_id}, q)


# ---------------------------------------------------------------------------
# 動画を作る
# ---------------------------------------------------------------------------
def silence(nframes, sampwidth, nch):
    return b"\x00" * (nframes * sampwidth * nch)


def pick_theme(data, order):
    """YAML の theme があればその色。なければ作る順番で色を回す（続けて同じ色にならへん）"""
    if "theme" in data:
        return THEMES[int(data["theme"]) % len(THEMES)]
    return THEMES[order % len(THEMES)]


CHUNK_GAP = 0.10   # ひと息とひと息の間（秒）


def plan_chunks(ln):
    """1つのセリフを、(画面の文字, 読ませる文字) のひと息ごとに分ける"""
    shown = split_chunks(ln["text"])
    if "yomi" in ln:
        spoken = split_chunks(ln["yomi"])
        if len(spoken) != len(shown):
            return [(ln["text"], ln["yomi"])]
        return list(zip(shown, spoken))
    return [(c, c) for c in shown]


def build_video(path, out_mp4, out_txt, speaker_id, preview=False, order=0):
    data = load_script(path)
    money = is_money_video(data)
    saigen = bool(data.get("saigen", data.get("type") in SAIGEN_TYPES))
    bg = pick_theme(data, order)
    extra = data.get("emphasis", [])

    tl = Timeline()
    rate = 24000
    voice = []
    events = []
    t = 0.0
    prev_table_key = None
    for li, ln in enumerate(data["lines"]):
        table = ln.get("table")
        tlayer = table_layer(table) if table else None
        tkey = repr(table) if table else None
        first_table = tkey is not None and tkey != prev_table_key
        prev_table_key = tkey
        chunks = plan_chunks(ln)
        t += LEAD_SILENCE
        if li > 0:
            events.append((max(0.0, t - 0.12), "whoosh"))
        for ci, (shown, spoken) in enumerate(chunks):
            if preview:
                dur = 1.5
                pcm = np.zeros(int(dur * rate), dtype=np.int16)
            else:
                wav_bytes = synthesize(spoken, speaker_id)
                with wave.open(io.BytesIO(wav_bytes)) as w:
                    rate = w.getframerate()
                    pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
                    if w.getnchannels() > 1:
                        pcm = pcm.reshape(-1, w.getnchannels())[:, 0]
            gap = CHUNK_GAP if ci < len(chunks) - 1 else TAIL_SILENCE
            start = t
            voice.append((start, pcm))
            t += len(pcm) / rate + gap
            events.append((start, "pop"))
            tl.items.append(dict(
                start=start - (LEAD_SILENCE if ci == 0 else 0), end=t, line=li,
                box=box_layer(shown, hook=(li == 0), label=ln.get("label"), extra=extra),
                table=tlayer, first_table=(first_table and ci == 0), new_line=(ci == 0), end_card=False,
            ))
    # 最後の2秒
    events.append((t, "ding"))
    tl.items.append(dict(start=t, end=t + END_SECONDS, line=-1, box=box_layer("", end_card=True),
                         table=None, first_table=False, new_line=True, end_card=True))
    t += END_SECONDS
    total = t
    tl.items[0]["start"] = 0.0

    # 声を1本につなぐ
    n = int(math.ceil(total * rate))
    track = np.zeros(n, dtype=np.int16)
    for start, pcm in voice:
        s = int(start * rate)
        e = min(n, s + len(pcm))
        track[s:e] = pcm[:e - s]

    # 口パク用：フレームごとの声の大きさ
    n_frames = int(math.ceil(total * FPS))
    per = rate / FPS
    vf = track.astype(np.float32)
    loud = np.array([
        np.sqrt(np.mean(vf[int(k * per):int((k + 1) * per)] ** 2)) if int(k * per) < len(vf) else 0.0
        for k in range(n_frames)
    ])
    strip, period = make_bg_strip(bg)
    ctx = dict(
        bounds=tl.bounds(), strip=strip, period=period, header=header_layer(saigen),
        disclaimer=disclaimer_layer() if money else None, pointer=tap_pointer_layer(),
        loud=loud, threshold=max(loud.max() * 0.15, 1.0), variants=chara_variants(),
        chara_pos=chara_pos(), total=total,
    )

    if preview:
        pdir = OUTPUT_DIR / "preview" / Path(path).stem
        pdir.mkdir(parents=True, exist_ok=True)
        for i, it in enumerate(tl.items):
            k = int((it["start"] + min(0.6, (it["end"] - it["start"]) / 2)) * FPS)
            compose_frame(k, tl, ctx).save(pdir / f"f{i:03d}.png")
        print(f"  見た目の確認用画像: {pdir}")
        return

    mixed = audio_fx.mix(track, rate, events, variant=order)

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = Path(tmp) / "voice.wav"
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(mixed.tobytes())

        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-i", str(wav_path),
            "-vf", "format=yuv420p",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",   # スマホで聞きやすい音量にそろえる
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-t", f"{total:.3f}",
            "-movflags", "+faststart",
            str(out_mp4),
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for k in range(n_frames):
            proc.stdin.write(compose_frame(k, tl, ctx).tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise UserError("ffmpeg で動画を作るのに失敗しました。")

    out_txt.write_text(make_post_text(data, money), encoding="utf-8")
    print(f"  動画: {out_mp4.name}（{total:.1f}秒）")
    print(f"  投稿文: {out_txt.name}")


def make_post_text(data, money):
    body = data["caption"].rstrip("\n")
    parts = [body]
    if money:
        parts.append("\n".join(DISCLAIMER))
    parts.append("\n".join(POST_FOOTER))
    return "\n\n".join(parts) + "\n"


def next_number(date_str):
    nums = []
    for p in OUTPUT_DIR.glob(f"{date_str}_*.mp4"):
        try:
            nums.append(int(p.stem.split("_")[1]))
        except (IndexError, ValueError):
            pass
    return max(nums, default=0) + 1


def main():
    ap = argparse.ArgumentParser(description="ショート動画をまとめて作ります")
    ap.add_argument("files", nargs="*", help="作りたいYAML（省略すると scripts/ の全部）")
    ap.add_argument("--preview", action="store_true", help="音声なしで画面だけ確認する")
    args = ap.parse_args()

    files = [Path(f) for f in args.files] or sorted(SCRIPTS_DIR.glob("*.yaml")) + sorted(SCRIPTS_DIR.glob("*.yml"))
    if not files:
        print("scripts/ に YAML がありません。")
        return 1
    if not args.preview and shutil.which("ffmpeg") is None:
        print("ffmpeg が見つかりません。README の手順で入れてください。")
        return 1
    OUTPUT_DIR.mkdir(exist_ok=True)

    try:
        # 先に全部チェックして、途中で止まらないようにする
        for f in files:
            load_script(f)
        speaker_id = None if args.preview else find_speaker_id()
        date_str = datetime.date.today().strftime("%Y%m%d")
        num = next_number(date_str)
        for f in files:
            print(f"作成中: {f.name}")
            stem = f"{date_str}_{num:02d}"
            build_video(f, OUTPUT_DIR / f"{stem}.mp4", OUTPUT_DIR / f"{stem}.txt",
                        speaker_id, preview=args.preview, order=num)
            num += 1
    except UserError as e:
        print("\n【エラー】" + str(e))
        return 1
    print("\nぜんぶ完成しました！ output フォルダを見てください。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
