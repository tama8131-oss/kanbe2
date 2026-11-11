#!/usr/bin/env python3
"""
⑤LP：プロフィールのリンクに置く、1枚もののページ（lp/index.html）を作る。

- 書くのは「紹介会社に確認済み」の事実だけ
- 画像はページの中に埋め込むので、index.html 1つをアップすれば動く（tiiny.site などの無料サービス向け）
- よくある質問は、AI検索にも読まれるように FAQ の構造化データ（JSON-LD）を入れる

使い方:
    python3 make_lp.py
"""
import base64
import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "lp" / "index.html"

IG_USER = "hakobu_driver"
DM_URL = f"https://ig.me/m/{IG_USER}"
IG_URL = f"https://www.instagram.com/{IG_USER}/"

CONDITIONS = [
    ("経験ゼロでOK", "配送の仕事をしたことがない人でも始められます。"),
    ("上司も同僚もいない、ひとりで黙々", "職場の人間関係に疲れた人に知ってほしい働き方です。"),
    ("車がなくても、貸してもらえる", "自分の車を持っていなくても大丈夫です。"),
    ("車レンタルは持ち帰れる", "借りた車は持ち帰れます。"),
    ("外国籍もOK", "個人事業主として働けるビザがある人に限ります。"),
    ("全国対応OK", "このページは、基本は関東エリアの情報です。"),
]

FOR_YOU = [
    "職場の人間関係に疲れた人",
    "ひとりで黙々と働きたい人",
    "経験がなくて不安な人",
    "車を持っていない人",
]

COSTS = [
    ("車代＋最上位の保険", "月7万6,000円"),
    ("ガソリン代", "月約3万円"),
    ("合計", "月約10万6,000円"),
]
COST_NOTE = "※関東・会社の車を借りる場合の例"

DISCLAIMER = [
    "※記載の金額は、実際に働いているドライバーの実績をもとにした目安です。",
    "※収入は働く日数・時間・配達件数などによって、人によって大きく変わります。平均より多く稼ぐ人もいれば、少ない人もいます。",
    "※記載の金額を保証するものではありません。",
]

FAQ = [
    ("経験ゼロでも始められますか？", "はい、経験ゼロでOKです。配送の仕事をしたことがない人でも始められます。"),
    ("車を持っていなくても大丈夫ですか？", "はい。車がなくても、車を貸してもらえます。借りた車は持ち帰れます。ただし、車代とガソリン代はかかります（関東の例：車代＋最上位の保険で月7万6,000円、ガソリン代が月約3万円）。"),
    ("人間関係が苦手でもできますか？", "上司も同僚もいない、ひとりで黙々と働ける仕事です。"),
    ("外国籍でも働けますか？", "はい、外国籍もOKです。ただし、個人事業主として働けるビザがある人に限ります。"),
    ("どこで働けますか？", "全国対応OKです。このページでは、基本は関東エリアの情報を紹介しています。"),
    ("相談では何を聞かれますか？", "住んでいる地域、車を持っているか、いつごろから働きたいか、の3つです。わかったら、くわしい条件を案内します。"),
]

STEPS = [
    ("DMで「相談したい」と送る", "質問だけでも大丈夫です。"),
    ("3つだけ答える", "住んでいる地域／車を持っているか／いつごろから働きたいか"),
    ("くわしい条件を案内", "あなたの地域と状況に合わせて案内します。"),
]

HONEST = [
    "業務委託の仕事です。",
    "車を借りる場合は、車代とガソリン代が毎月かかります。",
    "いいことだけでなく、かかるお金も正直にお伝えします。",
]


def e(s):
    return html.escape(s)


def main():
    icon = base64.b64encode((BASE / "assets" / "icon_hakobu.png").read_bytes()).decode()
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ
        ],
    }
    cond_html = "".join(f'<li><b>{e(t)}</b><span>{e(d)}</span></li>' for t, d in CONDITIONS)
    you_html = "".join(f"<li>{e(x)}</li>" for x in FOR_YOU)
    cost_rows = "".join(
        f'<tr class="{"total" if i == len(COSTS) - 1 else ""}"><th>{e(k)}</th><td>{e(v)}</td></tr>'
        for i, (k, v) in enumerate(COSTS))
    disc = "".join(f"<p>{e(x)}</p>" for x in DISCLAIMER)
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)
    steps_html = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in STEPS)
    honest_html = "".join(f"<li>{e(x)}</li>" for x in HONEST)

    page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>上司も同僚もいない、ひとりで黙々と働く配送の仕事｜はこぶ</title>
<meta name="description" content="Amazon配送の仕事（業務委託）。経験ゼロでOK、上司も同僚もいない、ひとりで黙々。車がなくても貸してもらえます。全国対応OK、基本は関東エリアの情報です。">
<meta property="og:title" content="上司も同僚もいない、ひとりで黙々と働く配送の仕事">
<meta property="og:description" content="経験ゼロでOK。車がなくても貸してもらえる。相談はDMで。">
<link rel="icon" href="data:image/png;base64,{icon}">
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
<style>
:root{{--bg:#DCEBF5;--fg:#23395B;--ac:#E4572E;--y:#FFD166}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:"Noto Sans JP","Hiragino Sans",system-ui,sans-serif;line-height:1.7}}
main{{max-width:560px;margin:0 auto;padding:0 16px 120px}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:14px 0;font-weight:700}}
.ai{{background:var(--fg);color:#fff;border-radius:10px;padding:2px 10px;font-size:13px}}
.hero{{background:var(--fg);color:#fff;border-radius:24px;padding:28px 22px;text-align:center}}
.hero h1{{font-size:28px;line-height:1.4;margin:0 0 10px}}
.hero h1 em{{color:var(--y);font-style:normal}}
.hero p{{margin:4px 0;opacity:.95}}
.hero img{{width:150px;height:150px;border-radius:50%;background:#fff;margin:14px 0 4px}}
section{{background:#fff;border-radius:20px;padding:20px;margin:16px 0}}
h2{{font-size:20px;margin:0 0 12px}}
h2 small{{display:block;font-size:13px;color:var(--ac)}}
ul{{list-style:none;margin:0;padding:0}}
.cond li,.steps li{{padding:10px 0;border-bottom:1px solid #E6EEF5;display:flex;flex-direction:column}}
.cond li:last-child,.steps li:last-child{{border:0}}
.cond b::before{{content:"✓ ";color:var(--ac)}}
.cond span,.steps span{{font-size:14px;opacity:.85}}
.you li{{padding:6px 0}} .you li::before{{content:"● ";color:var(--ac)}}
table{{width:100%;border-collapse:collapse;margin:6px 0}}
th,td{{padding:12px 8px;border-bottom:1px solid #E6EEF5;text-align:left}}
td{{text-align:right;font-weight:700;font-size:18px;white-space:nowrap}} th{{font-size:15px}}
tr.total th,tr.total td{{background:var(--fg);color:#fff}}
.note{{font-size:13px;font-weight:700;margin:6px 0}}
.disc p{{font-size:12px;margin:2px 0;opacity:.85}}
.honest li{{padding:6px 0}} .honest li::before{{content:"！ ";color:var(--ac);font-weight:700}}
.steps{{counter-reset:s}} .steps li b::before{{counter-increment:s;content:counter(s)". ";color:var(--ac)}}
details{{border-bottom:1px solid #E6EEF5;padding:10px 0}}
summary{{font-weight:700;cursor:pointer}}
details p{{margin:8px 0 0;font-size:15px}}
.cta{{display:block;text-align:center;background:var(--ac);color:#fff;font-weight:700;font-size:18px;padding:16px;border-radius:999px;text-decoration:none;margin:12px 0}}
.cta.sub{{background:#fff;color:var(--fg);border:2px solid var(--fg)}}
.bar{{position:fixed;left:0;right:0;bottom:0;padding:10px 16px calc(10px + env(safe-area-inset-bottom));background:rgba(255,255,255,.95);box-shadow:0 -4px 16px rgba(0,0,0,.08)}}
.bar .cta{{max-width:528px;margin:0 auto}}
footer{{font-size:12px;text-align:center;opacity:.8;margin:24px 0}}
</style>
</head>
<body>
<main>
  <div class="top"><span>Amazon配送ドライバーのリアル</span><span class="ai">AI生成</span></div>

  <div class="hero">
    <img src="data:image/png;base64,{icon}" alt="はこぶ">
    <h1><em>上司も同僚もいない。</em><br>ひとりで黙々と働く、<br>配送の仕事。</h1>
    <p>Amazon配送の仕事（業務委託）</p>
    <p>経験ゼロでOK／車がなくても貸してもらえる</p>
    <a class="cta" href="{DM_URL}">DMで相談する</a>
    <p style="font-size:13px">質問だけでも大丈夫です</p>
  </div>

  <section>
    <h2><small>FOR YOU</small>こんな人に知ってほしい</h2>
    <ul class="you">{you_html}</ul>
  </section>

  <section>
    <h2><small>CONDITIONS</small>条件</h2>
    <ul class="cond">{cond_html}</ul>
  </section>

  <section>
    <h2><small>MONEY</small>車を借りる場合にかかるお金</h2>
    <table>{cost_rows}</table>
    <p class="note">{e(COST_NOTE)}</p>
    <div class="disc">{disc}</div>
  </section>

  <section>
    <h2><small>HONEST</small>先に知っておいてほしいこと</h2>
    <ul class="honest">{honest_html}</ul>
  </section>

  <section>
    <h2><small>FLOW</small>相談の流れ</h2>
    <ul class="steps">{steps_html}</ul>
    <a class="cta" href="{DM_URL}">DMで「相談したい」と送る</a>
  </section>

  <section>
    <h2><small>FAQ</small>よくある質問</h2>
    {faq_html}
  </section>

  <a class="cta sub" href="{IG_URL}">毎日20時の動画を見る（Instagram）</a>

  <footer>
    <p>※このページはAmazon公式のものではありません。</p>
    <p>このページと動画はAIで作っています。</p>
  </footer>
</main>
<div class="bar"><a class="cta" href="{DM_URL}">DMで相談する</a></div>
</body>
</html>
"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print("作成:", OUT)


if __name__ == "__main__":
    main()
