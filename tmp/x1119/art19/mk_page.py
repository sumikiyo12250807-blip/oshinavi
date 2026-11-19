# -*- coding: utf-8 -*-
# 11/19 記事3本の確認ページ（本文＋出典URL）→ artcheck_1119.html
import io, html, re
A = 'C:/Users/user/oshinavi/tmp/x1119/art19/'
ARTS = [('daibakushow', 'DAIBAKUSHOW 2026'), ('asagaya', '阿佐ヶ谷姉妹 ミーツ オーケストラ'), ('plastictree', 'Plastic Tree 年末公演')]
src = io.open(A + 'sources.md', encoding='utf-8').read()
def link(t):
    t = html.escape(t)
    return re.sub(r'(https?://[^\s<]+)', r'<a href="\1">\1</a>', t)
NOTES = [
    '独立の確かめ（別の係・出典23本を開いて「」31か所を元の文字と照らした）＝🔴0🟠1🟡6',
    'Plastic Tree：年明けの New Song Showcase も 11/21(土) 12:00 にローチケの先着先行が始まる＝1行足したわ',
    'DAIBAKUSHOW：「今年で7回目」は 2023年が4回目から数えた数＝そう分かる書き方に／「主催は〜と書いている」→「公式サイトには〜ともある」',
    '阿佐ヶ谷姉妹：観光ツアーを「グランシップが用意した」と言い切らない形に',
    '「1人6枚まで」「1人4枚まで」は枚数の上限＝書いてよい決まりなので残したわ',
    '会員だけの先行（グランシップ友の会など）は入れていないわ',
]
CSS = '''<title>記事3本 確認用</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root { --bg:#fbf9fb; --fg:#26202a; --muted:#6d6473; --card:#ffffff; --line:#e7dfe9; --accent:#b0336f; --note:#fff4e5; --font:"Noto Sans JP", system-ui, sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#17141a; --fg:#ece6ef; --muted:#a79fae; --card:#211d25; --line:#352f3a; --accent:#f07fb2; --note:#2e2418; color-scheme:dark; } }
:root[data-theme="dark"] { --bg:#17141a; --fg:#ece6ef; --muted:#a79fae; --card:#211d25; --line:#352f3a; --accent:#f07fb2; --note:#2e2418; color-scheme:dark; }
body { background:var(--bg); color:var(--fg); font-family:var(--font); font-size:16px; line-height:1.8; margin:0; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:12px 48px; }
.wrap { max-width:680px; margin:0 auto; display:flex; flex-direction:column; gap:20px; }
h1 { font-size:20px; margin:8px 0 0; text-wrap:balance; }
h2 { font-size:17px; margin:0 0 8px; color:var(--accent); }
a { color:var(--accent); overflow-wrap:anywhere; }
.note { background:var(--note); border:1px solid var(--line); border-radius:10px; padding:12px 14px; }
.note ul { margin:4px 0 0; padding-left:20px; }
nav { display:flex; flex-wrap:wrap; gap:6px 14px; }
article { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px; min-width:0; }
.txt { white-space:pre-wrap; overflow-wrap:anywhere; }
.meta { font-size:14px; color:var(--muted); }
.src { white-space:pre-wrap; overflow-wrap:anywhere; font-size:14px; }
</style>
'''
b = [CSS, '<div class="wrap">', '<h1>11/19 の記事3本（11/21・11/22 発売の組）</h1>',
     '<div class="note"><b>見てほしいところ</b><ul>' + ''.join('<li>%s</li>' % html.escape(n) for n in NOTES) + '</ul></div>',
     '<nav>' + ''.join('<a href="#%s">%s</a>' % (s, html.escape(t)) for s, t in ARTS) + '<a href="#src">出典URL</a></nav>']
for s, t in ARTS:
    body = io.open(A + s + '.md', encoding='utf-8').read().strip()
    n = len(body.replace('\n', ''))
    b.append('<article id="%s"><h2>%s</h2><div class="meta">%d字</div><div class="txt">%s</div></article>' % (s, html.escape(t), n, html.escape(body)))
b.append('<article id="src"><h2>出典URL（組ごと・どの文 → どのURL）</h2><div class="src">%s</div></article>' % link(src))
b.append('</div>')
io.open(A + 'artcheck_1119.html', 'w', encoding='utf-8').write('\n'.join(b))
print('ok')
