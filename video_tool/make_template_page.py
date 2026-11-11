#!/usr/bin/env python3
"""funnel/dm_templates.md を、スマホで1タップでコピーできるページ（HTML）にする。

使い方:
    python3 make_template_page.py 出力するHTML
"""
import html
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "funnel" / "dm_templates.md"


def main():
    out = sys.argv[1]
    md = SRC.read_text(encoding="utf-8")
    parts, i = [], 0
    for m in re.finditer(r"```\n(.*?)```", md, re.S):
        parts.append(("text", md[i:m.start()]))
        parts.append(("code", m.group(1)))
        i = m.end()
    parts.append(("text", md[i:]))
    body, n = [], 0
    for kind, s in parts:
        if kind == "code":
            n += 1
            body.append(f'<div class="tpl"><pre id="t{n}">{html.escape(s.rstrip())}</pre>'
                        f'<button data-t="t{n}">コピー</button><span class="msg"></span></div>')
            continue
        for ln in s.splitlines():
            ln = ln.strip()
            if not ln or ln == "---":
                continue
            if ln.startswith("# "):
                body.append(f"<h1>{html.escape(ln[2:])}</h1>")
            elif ln.startswith("## "):
                body.append(f"<h2>{html.escape(ln[3:])}</h2>")
            elif ln.startswith("### "):
                body.append(f"<h3>{html.escape(ln[4:])}</h3>")
            elif ln.startswith("- "):
                body.append(f"<p class='li'>・{html.escape(ln[2:])}</p>")
            else:
                body.append(f"<p>{html.escape(ln)}</p>")
    page = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DM返信テンプレ集</title><style>
body{{margin:0;background:#DCEBF5;color:#23395B;font-family:system-ui,"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.6}}
main{{max-width:560px;margin:0 auto;padding:16px 16px 60px}}
h1{{font-size:22px}} h2{{font-size:19px;margin:28px 0 8px;padding:8px 12px;background:#23395B;color:#fff;border-radius:10px}}
h3{{font-size:16px;margin:16px 0 6px}} p{{margin:4px 0;font-size:14px}} .li{{margin-left:4px}}
.tpl{{background:#fff;border-radius:14px;padding:12px;margin:8px 0}}
pre{{white-space:pre-wrap;font-family:inherit;font-size:14px;margin:0 0 8px}}
button{{width:100%;padding:12px;font-size:16px;font-weight:700;border:0;border-radius:10px;background:#E4572E;color:#fff}}
.msg{{font-size:13px}}
</style></head><body><main>{''.join(body)}</main><script>
document.querySelectorAll('button[data-t]').forEach(b=>b.onclick=async()=>{{const m=b.nextElementSibling;try{{await navigator.clipboard.writeText(document.getElementById(b.dataset.t).textContent);m.textContent='コピーしたで！';}}catch(e){{m.textContent='コピーできへんかった。文を長押ししてコピーしてな。';}}}});
</script></body></html>"""
    Path(out).write_text(page, encoding="utf-8")
    print("作成:", out)


if __name__ == "__main__":
    main()
