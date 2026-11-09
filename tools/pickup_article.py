# -*- coding: utf-8 -*-
"""記事1本＝1ページを組み立てる（2026-11-09 新設・pickup_list.py と組で使う）。

draft.md の形（Fable への依頼文と同じ）:
  1行目 タイトル／2〜4行目 一覧に出す3行（4行目は「チケット販売日時 …」）／空行／5行目から本文（1文1行・空行は無視）
  段の切れ目＝「ここからが」「まずは」「料金の話」「見どころ」「日本でのこれまで」などで始まる行と、最後の締め2行
使い方:
  python tools/pickup_article.py <draft.md> <slug> --q <タップで探す語> --shows-head <箱の見出し> --shows <箱の中身> [--label 深掘り]
  → pickup/a/<slug>.html を書く（台帳 tools/pickup_articles.json への登録は --watch 3674,49898 を付けたときだけ）
"""
import argparse, datetime, html as H, io, json, os, re, sys, urllib.parse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TPL = 'pickup/2026-11-08/eliza.html'
BREAK = ('ここからが', 'まずは', '料金の話', '見どころ', '日本でのこれまで', 'お話はこう')


def paragraphs(lines):
    ps, cur = [], []
    for k, s in enumerate(lines):
        last2 = k >= len(lines) - 2
        if cur and (s.startswith(BREAK) or (last2 and k == len(lines) - 2)):
            ps.append(cur); cur = []
        cur.append(s)
    if cur:
        ps.append(cur)
    return ps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('draft'); ap.add_argument('slug')
    ap.add_argument('--q', required=True); ap.add_argument('--shows-head', required=True); ap.add_argument('--shows', required=True)
    ap.add_argument('--label', default='')
    ap.add_argument('--watch', default='')
    a = ap.parse_args()
    L = [x.rstrip() for x in io.open(a.draft, encoding='utf-8').read().splitlines()]
    title, l2, l3, l4 = L[0], L[1], L[2], L[3]
    body = [x for x in L[4:] if x.strip()]
    sale = l4.replace('チケット販売日時', '').strip()
    desc = body[0]
    ps = paragraphs(body)
    text = '\n'.join('    <p>' + '<br>\n'.join(H.escape(s, quote=False) for s in p) + '</p>' for p in ps)
    t = io.open(TPL, encoding='utf-8').read()
    head = t[:t.index('<body>')]
    url = f'https://oshinavi.jp/pickup/a/{a.slug}.html'
    head = re.sub(r'<title>.*?</title>', f'<title>{H.escape(title)}｜ピックアップ記事 - OSHINAVI</title>', head)
    for p in ('name="description"', 'property="og:description"'):
        head = re.sub(rf'(<meta {p} content=")[^"]*', lambda m: m.group(1) + H.escape(desc), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + H.escape(title) + '｜ピックアップ記事', head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, head)
    q = urllib.parse.quote(a.q)
    long = ' pk-long' if len(title) > 24 else ''
    label = '📖 ピックアップ記事' + (f'・{a.label}' if a.label else '')
    page = head + f"""<body>

<header>
  <a href="../../index.html" class="logo">OSHINAVI</a>
  <a href="../../index.html" class="nav-back">← チケット・イベント一覧へ</a>
</header>

<nav class="pk-crumb"><a href="../index.html">← ピックアップ記事の一覧</a></nav>
<main class="wrap">
<article class="pickup" id="pickup">
  <span class="pk-label">{label}</span>
  <h1 class="pk-page-name{long}">{H.escape(title)}</h1>
  <span class="pk-sale">{H.escape(sale)}</span>
  <div class="pk-text">
{text}
  </div>
  <a class="pk-shows" href="../../index.html?q={q}">
    <b>{H.escape(a.shows_head)}<span class="pk-go">タップで探す →</span></b>
    {H.escape(a.shows)}
  </a>
  <a class="pk-toc" href="../index.html">ピックアップ記事の一覧へ戻る</a>
  <a class="pk-tail" href="../../index.html?status=urgent">他にも気になるアーティストがチケット発売しているわよ。<span class="pk-go">今週発売を見る →</span></a>
</article>
</main>

</body>
</html>
"""
    os.makedirs('pickup/a', exist_ok=True)
    out = f'pickup/a/{a.slug}.html'
    io.open(out, 'w', encoding='utf-8').write(page)
    nk = sum(1 for m in re.finditer(r'。(?!<br>)(?!</p>)(?!」)', text))
    print(f'書いた {out}｜段 {len(ps)}・行 {len(body)}・「。」の未改行 {nk}')
    if a.watch:
        R = json.load(io.open('tools/pickup_articles.json', encoding='utf-8'))
        R['articles'] = [x for x in R['articles'] if x['slug'] != a.slug or x['href'] != out]
        lines = [H.escape(l2, quote=False), H.escape(l3, quote=False),
                 '<b>チケット販売日時</b> ' + H.escape(sale, quote=False)]
        R['articles'].append({'slug': a.slug, 'href': out, 'name': title, 'lines': lines,
                              'added': datetime.date.today().isoformat(),
                              'watch': [int(x) for x in a.watch.split(',')], 'from': None})
        io.open('tools/pickup_articles.json', 'w', encoding='utf-8').write(json.dumps(R, ensure_ascii=False, indent=1))
        print('台帳に登録', a.slug, a.watch)


if __name__ == '__main__':
    main()
