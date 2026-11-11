#!/usr/bin/env python3
"""
できた動画・画像を、携帯からそのまま保存できるページ（HTML）にまとめる。
動画（.mp4）と同じ名前の .txt があれば、投稿文として「コピー」ボタン付きで載せる。

使い方:
    python3 make_download_page.py 出力するHTML ファイル1 ファイル2 ...
    python3 make_download_page.py --start 2026-11-12 --time 20:00 出力するHTML 動画1 動画2 ...
      → 動画ごとに「11/12（水）20:00 に予約」と、1日ずつずらして表示する
"""
import argparse
import datetime
import base64
import html
import shutil
from pathlib import Path

MIME = {".mp4": "video/mp4", ".png": "image/png", ".jpg": "image/jpeg"}


WEEK = "月火水木金土日"


def card(i, path, when=None, external=False):
    p = Path(path)
    mime = MIME[p.suffix.lower()]
    src = p.name if external else f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
    if mime.startswith("video"):
        media = f'<video id="m{i}" src="{src}" controls playsinline preload="metadata"></video>'
    else:
        media = f'<img id="m{i}" src="{src}" alt="{html.escape(p.name)}">'
    head = html.escape(p.name)
    if when:
        hook = p.with_suffix(".txt").read_text(encoding="utf-8").splitlines()[0] if p.with_suffix(".txt").exists() else ""
        head = f"{when} に予約<br><span class=\"hook\">{html.escape(hook)}</span>"
    out = f'''<div class="card"><div class="n">{head}</div>{media}
<button class="dl" data-i="{i}" data-f="{html.escape(p.name)}" data-mime="{mime}" hidden>保存する</button><div class="msg"></div>'''
    txt = p.with_suffix(".txt")
    if p.suffix == ".mp4" and txt.exists():
        out += f'''<div class="cap-title">投稿文</div><button class="copy" data-t="t{i}">投稿文をコピー</button><div class="msg"></div>
<pre id="t{i}">{html.escape(txt.read_text(encoding="utf-8"))}</pre>'''
    return out + "</div>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start")
    ap.add_argument("--time", default="20:00")
    ap.add_argument("--dir", help="動画を別ファイルにして、このフォルダに index.html と一緒に置く（大きいとき用）")
    ap.add_argument("out", nargs="?")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    files = a.files
    if a.dir and a.out:
        files = [a.out] + files  # --dir のときは出力先の指定がいらんので、最初の1つも動画
    if a.dir:
        outdir = Path(a.dir)
        outdir.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy(f, outdir / Path(f).name)
        out = outdir / "index.html"
    else:
        out = a.out
    whens = [None] * len(files)
    if a.start:
        d0 = datetime.date.fromisoformat(a.start)
        whens = [f"{(d0 + datetime.timedelta(days=i)).month}/{(d0 + datetime.timedelta(days=i)).day}"
                 f"（{WEEK[(d0 + datetime.timedelta(days=i)).weekday()]}）{a.time}" for i in range(len(files))]
    cards = "\n".join(card(i, f, whens[i], external=bool(a.dir)) for i, f in enumerate(files))
    page = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>保存用ページ</title><style>
body{{margin:0;background:#DCEBF5;color:#23395B;font-family:system-ui,"Hiragino Sans","Noto Sans JP",sans-serif}}
main{{max-width:560px;margin:0 auto;padding:20px 16px 60px}}
h1{{font-size:22px;margin:4px 0 8px}} p{{line-height:1.6;margin:6px 0}}
.card{{background:#fff;border-radius:16px;padding:12px;margin:18px 0}}
.n,.cap-title{{font-weight:700;margin:8px 0}} .n{{font-size:19px}} .hook{{font-size:15px;font-weight:400}} img,video{{width:100%;border-radius:8px;display:block;background:#000}}
button{{width:100%;margin-top:10px;padding:14px;font-size:17px;font-weight:700;border:0;border-radius:12px;background:#23395B;color:#fff}}
.msg{{font-size:14px;margin-top:6px;min-height:1em}}
pre{{white-space:pre-wrap;background:#F3F7FA;border-radius:12px;padding:12px;font-size:14px;line-height:1.6}}
</style></head><body><main>
<h1>保存用ページ</h1>
<p>上から順に、書いてある日時で予約してな。投稿文は「投稿文をコピー」でそのまま使える。</p>
{cards}
</main><script>
async function toBlob(src,mime){{if(!src.startsWith('data:')){{const r=await fetch(src);return new Blob([await r.arrayBuffer()],{{type:mime}});}}const bin=atob(src.split(',')[1]);const u=new Uint8Array(bin.length);for(let k=0;k<bin.length;k++)u[k]=bin.charCodeAt(k);return new Blob([u],{{type:mime}});}}
document.querySelectorAll('.copy').forEach(b=>{{b.onclick=async()=>{{const m=b.nextElementSibling;try{{await navigator.clipboard.writeText(document.getElementById(b.dataset.t).textContent);m.textContent='コピーしたで！';}}catch(e){{m.textContent='コピーできへんかった。下の文を長押しして選んでコピーしてな。';}}}};}});
(async()=>{{
  const dl = window.claude ? await window.claude.use("downloads") : null;
  if(!dl) return;
  document.querySelectorAll('.dl').forEach(b=>{{
    b.hidden=false;
    b.onclick=async()=>{{
      const m=b.nextElementSibling;
      try{{
        await dl.save({{filename:b.dataset.f,data:await toBlob(document.getElementById('m'+b.dataset.i).src,b.dataset.mime)}});
        m.textContent='保存できたで！';
      }}catch(e){{
        m.textContent=(e&&e.code==='declined')?'保存をやめたで。もう一回押してもええよ。':'保存できへんかった。長押しで保存してみてな。';
      }}
    }};
  }});
}})();
</script></body></html>'''
    Path(out).write_text(page, encoding="utf-8")
    print("作成:", out)


if __name__ == "__main__":
    main()
