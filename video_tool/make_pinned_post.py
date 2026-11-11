#!/usr/bin/env python3
"""
インスタの固定投稿（条件まとめ）用の画像を作る。
1080x1350（インスタの縦長投稿サイズ）を数枚、output/pinned/ に出力する。

使い方:
    python3 make_pinned_post.py
"""
from PIL import Image, ImageDraw

import make_videos as mv

W, H = 1080, 1350
OUT_DIR = mv.OUTPUT_DIR / "pinned"

COST_TABLE = {
    "title": "毎月かかるお金",
    "rows": [
        ["車代＋最上位の保険", "月7万6,000円"],
        ["ガソリン代", "月約3万円"],
    ],
    "note": "※関東・会社の車を借りる場合の例",
}

CAPTION = """【はじめに読んでください】
このアカウントでは、Amazon配送の仕事（業務委託）のリアルを、いいこともきついことも正直に紹介しています。

✅ 経験ゼロでOK
✅ 車がなくても、貸してもらえる
✅ 車レンタルは持ち帰れる
✅ 上司も同僚もいない、ひとりで黙々
✅ 外国籍もOK（個人事業主として働けるビザがある人）
✅ 全国対応OK！基本は関東エリアの情報です

気になる人は、DMで「相談したい」と送ってください。
質問だけでも大丈夫です。

※このアカウントはAmazon公式のアカウントではありません。

※記載の金額は、実際に働いているドライバーの実績をもとにした目安です。
※収入は働く日数・時間・配達件数などによって、人によって大きく変わります。平均より多く稼ぐ人もいれば、少ない人もいます。
※記載の金額を保証するものではありません。

この投稿はAIで作っています
"""


def base(page, total):
    im = Image.new("RGB", (W, H), mv.BG)
    d = ImageDraw.Draw(im)
    d.text((48, 52), mv.HEADLINE, font=mv.font(50), fill=mv.FG)
    f = mv.font(34)
    tw = d.textlength(mv.AI_LABEL, font=f)
    x1 = W - 40
    x0 = x1 - tw - 40
    d.rounded_rectangle((x0, 46, x1, 110), radius=16, fill=mv.FG)
    d.text((x0 + 20, 51), mv.AI_LABEL, font=f, fill=mv.WHITE)
    # ページ番号
    s = f"{page}/{total}"
    f = mv.font(30)
    d.text((W - 48 - d.textlength(s, font=f), H - 70), s, font=f, fill=mv.FG)
    return im, d


def paste_chara(im, scale, cx, bottom_y):
    ch = mv.chara_image()
    size = int(1080 * scale)
    small = ch.resize((size, size), Image.LANCZOS)
    px = int(cx - (220 + 920) / 2 * scale)
    py = int(bottom_y - 964 * scale)
    im.paste(small, (px, py), small)


def white_box(d, top, bottom):
    d.rounded_rectangle((60, top, W - 60, bottom), radius=36, fill=mv.WHITE)


def centered(d, text, size, y, line_h=None):
    f = mv.font(size)
    line_h = line_h or int(size * 1.45)
    for i, ln in enumerate(text.split("\n")):
        d.text((W / 2 - d.textlength(ln, font=f) / 2, y + i * line_h), ln, font=f, fill=mv.FG)


def bullets(d, items, top, size=50, gap=36):
    f = mv.font(size)
    y = top
    for it in items:
        d.text((110, y), "●", font=mv.font(size - 14), fill=mv.FG)
        for j, ln in enumerate(mv.wrap(d, it, f, W - 300)):
            d.text((170, y - 6 + j * int(size * 1.35)), ln, font=f, fill=mv.FG)
            last = j
        y += (last + 1) * int(size * 1.35) + gap
    return y


def page1(total):
    im, d = base(1, total)
    white_box(d, 230, 760)
    centered(d, "はじめに\n読んでください", 84, 300, 120)
    centered(d, "仕事の内容と\n相談のしかた", 56, 560, 80)
    paste_chara(im, 0.6, W / 2, H - 100)
    return im


def page2(total):
    im, d = base(2, total)
    centered(d, "どんな仕事？", 64, 210)
    white_box(d, 340, 1060)
    bottom = bullets(d, [
        "Amazon配送の仕事（業務委託）",
        "経験ゼロでOK",
        "上司も同僚もいない、ひとりで黙々",
        "外国籍もOK（個人事業主として働けるビザがある人）",
        "全国対応OK！基本は関東エリアの情報です",
    ], 400, size=46, gap=34)
    paste_chara(im, 0.28, W / 2, H - 40)
    return im


def page3(total):
    im, d = base(3, total)
    centered(d, "車がない人は？", 64, 190)
    centered(d, "車がなくても、貸してもらえます。\n車レンタルは持ち帰れます。\nただし、毎月お金がかかります。", 40, 290, 58)
    # 表（動画と同じデザイン）
    tmp = Image.new("RGB", (mv.W, mv.H), mv.BG)
    mv.draw_table(ImageDraw.Draw(tmp), dict(COST_TABLE, highlight_last=False))
    table_img = tmp.crop((0, 250, mv.W, 250 + 80 + 130 * 2 + 22 + 60))
    im.paste(table_img, (0, 480))
    f = mv.font(26)
    y = 930
    for para in mv.DISCLAIMER:
        for ln in mv.wrap(d, para, f, W - 120):
            d.text((60, y), ln, font=f, fill=mv.FG)
            y += 38
    paste_chara(im, 0.3, W / 2, H - 40)
    return im


def page4(total):
    im, d = base(4, total)
    centered(d, "相談のしかた", 64, 210)
    white_box(d, 340, 820)
    centered(d, "DMで\n「相談したい」\nと送ってください", 64, 400, 96)
    centered(d, "質問だけでも大丈夫です", 44, 720)
    centered(d, "※このアカウントはAmazon公式のアカウントではありません", 28, 850)
    paste_chara(im, 0.4, W / 2, H - 70)
    return im


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = [page1, page2, page3, page4]
    for i, fn in enumerate(pages, 1):
        path = OUT_DIR / f"pinned_{i}.png"
        fn(len(pages)).save(path)
        print("作成:", path.name)
    (OUT_DIR / "pinned_caption.txt").write_text(CAPTION, encoding="utf-8")
    print("作成: pinned_caption.txt")


if __name__ == "__main__":
    main()
