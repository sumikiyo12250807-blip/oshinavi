# -*- coding: utf-8 -*-
# 11/17 記事3本の本文＋出典を携帯で読めるページに（tmp/x1116/art16/mk_review.py の形）
import io, html
D = 'C:/Users/user/oshinavi/tmp/x1117/art17/'
A = [('minamikousetsu', '南こうせつ', ['https://www.kosetsu.com/schedule/', 'https://eplus.jp/sf/detail/4603880001', 'https://eplus.jp/sf/detail/4603880001-P0030003P021001',
       'https://lp.p.pia.jp/article/news/517233/index.html']),
     ('danseiburanko', '男性ブランコ', ['https://prtimes.jp/main/html/rd/p/000005465.000029501.html', 'https://dansei-blanco.com/', 'https://ticket.fany.lol/event/detail/22805']),
     ('hikawakiyoshi', '氷川きよし', ['https://realsound.jp/2026/09/post-2518509.html', 'https://eplus.jp/sf/detail/4620100001', 'https://eplus.jp/sf/detail/0036090001'])]
CSS = '''<title>記事3本 確認</title>
<style>
:root{--bg:#fbf9fb;--fg:#26202a;--muted:#6d6473;--card:#fff;--line:#e7dfe9;--accent:#b0336f;--note:#fff4e5}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17141a;--fg:#ece6ef;--muted:#a79fae;--card:#211d25;--line:#352f3a;--accent:#f07fb2;--note:#2e2418;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#17141a;--fg:#ece6ef;--muted:#a79fae;--card:#211d25;--line:#352f3a;--accent:#f07fb2;--note:#2e2418;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:"Noto Sans JP",system-ui,sans-serif;font-size:16px;line-height:1.8;margin:0;padding:12px 16px 48px}
.wrap{max-width:680px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
h1{font-size:20px;margin:8px 0 0}
nav{display:flex;gap:14px;flex-wrap:wrap}
a{color:var(--accent)}
.note{background:var(--note);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:15px}
article{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;min-width:0}
h2{font-size:17px;margin:0 0 8px;color:var(--accent)}
.head{color:var(--muted);font-size:14px;white-space:pre-wrap;margin-bottom:10px}
.txt{white-space:pre-wrap;overflow-wrap:anywhere}
.src{margin-top:12px;font-size:14px;overflow-wrap:anywhere}
.src a{display:block}
</style>'''
b = [CSS, '<div class="wrap"><h1>今日の記事3本（OK なら今夜の公開に入れる）</h1>',
     '<div class="note">独立の確かめ（係2人・出典を開いて1文ずつ）＝3本とも 🔴0 🟠0。細かい表記の5か所は直したわ。'
     '南こうせつは「SONGS」(11/19 22:00) の回の中身をぴあのニュースから書いたわ。</div>',
     '<nav>' + ''.join('<a href="#%s">%s</a>' % (s, html.escape(t)) for s, t, _ in A) + '</nav>']
for s, t, src in A:
    lines = io.open(D + s + '.md', encoding='utf-8').read().strip().splitlines()
    head, body = lines[:4], lines[5:]
    b.append('<article id="%s"><h2>%s（%d字）</h2><div class="head">%s</div><div class="txt">%s</div><div class="src"><b>出典</b>%s</div></article>'
             % (s, html.escape(t), len(''.join(body)), html.escape('\n'.join(head)), html.escape('\n'.join(body)),
                ''.join('<a href="%s">%s</a>' % (html.escape(u), html.escape(u)) for u in src)))
b.append('</div>')
io.open(D + 'review_1117.html', 'w', encoding='utf-8').write('\n'.join(b))
print('ok')
