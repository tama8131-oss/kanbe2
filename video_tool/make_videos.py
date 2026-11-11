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
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

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


def svg_to_png(svg, png):
    """hakobu_base.png が消えたときだけ使う（通常は同梱のPNGを使う）"""
    try:
        import cairosvg  # 無料のライブラリ。普段は不要
    except ImportError:
        raise UserError("assets/hakobu_base.png がありません。リポジトリから取り直してください。")
    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=1080, output_height=1080)


# ---------------------------------------------------------------------------
# 画面を1枚描く
# ---------------------------------------------------------------------------
CHARA_SCALE = 0.68


def render_frame(text, table=None, saigen=False, show_disclaimer=False, end_card=False):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    # 左上：見出し
    d.text((48, 56), HEADLINE, font=font(54), fill=FG)

    # 右上：AI生成ラベル（ずっと表示）
    f = font(36)
    tw = text_w(d, AI_LABEL, f)
    x1 = W - 40
    x0 = x1 - tw - 44
    d.rounded_rectangle((x0, 50, x1, 118), radius=16, fill=FG)
    d.text((x0 + 22, 56), AI_LABEL, font=f, fill=WHITE)

    # 「再現」ラベル（1日の流れの型）
    if saigen:
        f = font(36)
        tw = text_w(d, SAIGEN_LABEL, f)
        d.rounded_rectangle((48, 140, 48 + tw + 44, 208), radius=16,
                            fill=WHITE, outline=FG, width=4)
        d.text((48 + 22, 146), SAIGEN_LABEL, font=f, fill=FG)

    # 上側：数字の表
    if table and not end_card:
        draw_table(d, table)

    # 中央：白い角丸の字幕枠
    if end_card:
        f = font(84)
        lines = END_TEXT.split("\n")
        line_h = 120
    else:
        f = font(60)
        lines = wrap_balanced(d, text, f, 860)
        line_h = 88
    box_h = len(lines) * line_h + 90
    center_y = 1010 if (table and not end_card) else 760
    top = int(center_y - box_h / 2)
    d.rounded_rectangle((60, top, W - 60, top + box_h), radius=36, fill=WHITE)
    draw_centered_lines(d, lines, f, W / 2, top + 40, line_h, FG)

    # 金額の注意書き
    if show_disclaimer:
        f = font(27)
        y = top + box_h + 40 if end_card else 1222
        for para in DISCLAIMER:
            for ln in wrap(d, para, f, W - 120):
                d.text((60, y), ln, font=f, fill=FG)
                y += 38

    # 右下：声のクレジット
    f = font(28)
    d.text((W - 40 - text_w(d, VOICE_CREDIT, f), H - 70), VOICE_CREDIT, font=f, fill=FG)

    # 画面下：キャラ「はこぶ」
    ch = chara_image()
    size = int(1080 * CHARA_SCALE)
    small = ch.resize((size, size), Image.LANCZOS)
    content_cx = (220 + 920) / 2 * CHARA_SCALE  # 絵の左右の中心
    bottom = 964 * CHARA_SCALE                  # 影の下端
    px = int(W / 2 - content_cx)
    py = int(H - 30 - bottom)
    im.paste(small, (px, py), small)
    return im


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
    if not isinstance(data["lines"], list) or not data["lines"]:
        raise UserError(f"{name}: lines にセリフが1つもありません。")
    for i, ln in enumerate(data["lines"], 1):
        where = f"{name} の {i}番目のセリフ"
        if not isinstance(ln, dict) or "text" not in ln:
            raise UserError(f"{where}: text がありません。")
        must_str(ln["text"], f"{where} の text")
        if "yomi" in ln:
            must_str(ln["yomi"], f"{where} の yomi")
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


def build_video(path, out_mp4, out_txt, speaker_id, preview=False):
    data = load_script(path)
    money = is_money_video(data)
    saigen = bool(data.get("saigen", data.get("type") in SAIGEN_TYPES))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        segments = []  # (png, 秒)
        pcm = bytearray()
        params = None

        for i, ln in enumerate(data["lines"]):
            frame = render_frame(ln["text"], ln.get("table"), saigen, money)
            png = tmp / f"f{i:03d}.png"
            frame.save(png)
            if preview:
                segments.append((png, 0))
                continue
            wav_bytes = synthesize(ln.get("yomi", ln["text"]), speaker_id)
            with wave.open(io.BytesIO(wav_bytes)) as w:
                p = (w.getnchannels(), w.getsampwidth(), w.getframerate())
                if params is None:
                    params = p
                frames = w.readframes(w.getnframes())
                n = w.getnframes()
            nch, sw, rate = params
            lead = int(LEAD_SILENCE * rate)
            tail = int(TAIL_SILENCE * rate)
            pcm += silence(lead, sw, nch) + frames + silence(tail, sw, nch)
            segments.append((png, (lead + n + tail) / rate))

        # 最後の2秒：「条件は／プロフィールの／固定投稿へ」
        end_png = tmp / "end.png"
        render_frame("", None, saigen, money, end_card=True).save(end_png)
        segments.append((end_png, END_SECONDS))

        if preview:
            pdir = OUTPUT_DIR / "preview" / Path(path).stem
            pdir.mkdir(parents=True, exist_ok=True)
            for png, _ in segments:
                shutil.copy(png, pdir / png.name)
            print(f"  見た目の確認用画像: {pdir}")
            return

        nch, sw, rate = params
        pcm += silence(int(END_SECONDS * rate), sw, nch)
        wav_path = tmp / "voice.wav"
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(nch)
            w.setsampwidth(sw)
            w.setframerate(rate)
            w.writeframes(bytes(pcm))
        total = len(pcm) / (sw * nch) / rate

        concat = tmp / "frames.txt"
        with open(concat, "w", encoding="utf-8") as fp:
            for png, sec in segments:
                fp.write(f"file '{png.as_posix()}'\nduration {sec:.4f}\n")
            fp.write(f"file '{segments[-1][0].as_posix()}'\n")

        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat),
            "-i", str(wav_path),
            "-vf", f"fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-t", f"{total:.3f}",
            "-movflags", "+faststart",
            str(out_mp4),
        ]
        subprocess.run(cmd, check=True)

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
                        speaker_id, preview=args.preview)
            num += 1
    except UserError as e:
        print("\n【エラー】" + str(e))
        return 1
    print("\nぜんぶ完成しました！ output フォルダを見てください。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
