#!/usr/bin/env python3
"""
ストーリーズ用の画像を作る（1080x1920）。
- 毎日の告知：「今日20時」＋その日の動画のつかみ（scripts/ の台本の順番＝投稿の順番）
- ハイライトの表紙：条件／お金／相談／Q&A

使い方:
    python3 make_stories.py --start 2026-11-12
"""
import argparse
import datetime
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

import make_videos as mv

W, H = 1080, 1920
OUT = mv.OUTPUT_DIR / "stories"
WEEK = "月火水木金土日"


def base(bg):
    im, _ = mv.make_bg_strip(bg)
    return im.crop((0, 0, W, H)).convert("RGB")


def chara(im, scale=0.8, y_bottom=H - 120):
    ch = mv.chara_image()
    size = int(1080 * scale)
    small = ch.resize((size, size), Image.LANCZOS)
    px = int(W / 2 - (220 + 920) / 2 * scale)
    py = int(y_bottom - 964 * scale)
    im.paste(small, (px, py), small)


def daily(day, hook, bg, path):
    im = base(bg)
    d = ImageDraw.Draw(im)
    tag = f"{day.month}/{day.day}（{WEEK[day.weekday()]}）20:00 公開"
    f = mv.font(52)
    tw = d.textlength(tag, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, 260, W / 2 + tw / 2 + 40, 360), radius=50, fill=mv.ACCENT)
    d.text((W / 2 - tw / 2, 274), tag, font=f, fill=mv.WHITE)
    box = mv.box_layer(hook, hook=True)
    im.paste(box, (int(W / 2 - box.width / 2), 480), box)
    f = mv.font(44)
    s = "見逃さないように、フォローしてね"
    d.text((W / 2 - d.textlength(s, font=f) / 2, 480 + box.height + 50), s, font=f, fill=mv.FG)
    f = mv.font(30)
    d.text((W - 40 - d.textlength("AI生成", font=f), 60), "AI生成", font=f, fill=mv.FG)
    chara(im, 0.62)
    im.save(path)


def highlight(title, bg, path):
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    r = 330
    d.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=mv.FG)
    f = mv.font(170 if len(title) <= 2 else 130)
    tw = d.textlength(title, font=f)
    bb = d.textbbox((0, 0), title, font=f)
    d.text((W / 2 - tw / 2, H / 2 - (bb[3] + bb[1]) / 2), title, font=f, fill=mv.WHITE)
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    d0 = datetime.date.fromisoformat(a.start)
    files = sorted(mv.SCRIPTS_DIR.glob("*.yaml"))
    for i, f in enumerate(files):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        day = d0 + datetime.timedelta(days=i)
        p = OUT / f"story_{day:%m%d}.png"
        daily(day, data["lines"][0]["text"], mv.THEMES[(i + 1) % len(mv.THEMES)], p)
        print("作成:", p.name)
    for i, t in enumerate(["条件", "お金", "相談", "Q&A"]):
        p = OUT / f"highlight_{i + 1}_{t.replace('&', 'and')}.png"
        highlight(t, mv.THEMES[i % len(mv.THEMES)], p)
        print("作成:", p.name)


if __name__ == "__main__":
    main()
