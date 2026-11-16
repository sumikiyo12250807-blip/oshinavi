# -*- coding: utf-8 -*-
# 11/16 すちこ「3本の記事をまだ確認してない」＝記事3本の本文＋出典を携帯で読めるページに
# 11/16 夕「もうちょい情報を足して」＝足した分の出典も入れる
import io, html
D = 'C:/Users/user/oshinavi/tmp/x1116/art16/'
A = [('takahashiyu', '高橋優', ['https://www.takahashiyu.com/news/livetour2027%e3%80%8cfree-style-stroke-2%e3%80%8dinfo/', 'https://fc.takahashiyu.com/feature/free_style_stroke2', 'https://t.pia.jp/pia/event/event.do?eventCd=2637991',
       'https://www.billboard-japan.com/d_news/detail/107914/2', 'https://www.takahashiyu.com/news/page/2/', 'https://www.takahashiyu.com/news/0821release_tori_info/', 'https://www.takahashiyu.com/news/nhk_minnano-uta/']),
     ('freedomofchoice', 'FREEDOM OF CHOICE', ['https://www.cubeinc.co.jp/archives/16522', 'https://www.cubeinc.co.jp/archives/theater/freedomofchoice', 'https://www.tohostage.com/freedom_of_choice/', 'https://www.hakataza.co.jp/lineup/168',
       'https://www.astage-ent.com/stage-musical/s303510.html']),
     ('sumidabasho', '大相撲すみだ場所', ['https://oosumo.com/sumida/', 'https://t.pia.jp/pia/event/event.do?eventCd=2643420', 'https://t.pia.jp/pia/ticketInformation.do?eventCd=2643420&rlsCd=003',
       'https://www.sumo.or.jp/Jungyo/timetable/', 'https://www.sumo.or.jp/Jungyo/'])]
CSS = '''<title>記事3本 確認</title>
<style>
:root{--bg:#fbf9fb;--fg:#26202a;--muted:#6d6473;--card:#fff;--line:#e7dfe9;--accent:#b0336f}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17141a;--fg:#ece6ef;--muted:#a79fae;--card:#211d25;--line:#352f3a;--accent:#f07fb2;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#17141a;--fg:#ece6ef;--muted:#a79fae;--card:#211d25;--line:#352f3a;--accent:#f07fb2;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:"Noto Sans JP",system-ui,sans-serif;font-size:16px;line-height:1.8;margin:0;padding:12px 16px 48px}
.wrap{max-width:680px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
h1{font-size:20px;margin:8px 0 0}
nav{display:flex;gap:14px;flex-wrap:wrap}
a{color:var(--accent)}
article{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;min-width:0}
h2{font-size:17px;margin:0 0 8px;color:var(--accent)}
.head{color:var(--muted);font-size:14px;white-space:pre-wrap;margin-bottom:10px}
.txt{white-space:pre-wrap;overflow-wrap:anywhere}
.src{margin-top:12px;font-size:14px;overflow-wrap:anywhere}
.src a{display:block}
</style>'''
b = [CSS, '<div class="wrap"><h1>今日の記事3本（情報を足した版・今夜の公開に入る）</h1>',
     '<nav>' + ''.join(f'<a href="#{s}">{html.escape(t)}</a>' for s, t, _ in A) + '</nav>']
for s, t, src in A:
    lines = io.open(D + s + '.md', encoding='utf-8').read().strip().splitlines()
    head, body = lines[:4], lines[5:]
    b.append(f'<article id="{s}"><h2>{html.escape(t)}（{len("".join(body))}字）</h2>'
             f'<div class="head">{html.escape(chr(10).join(head))}</div>'
             f'<div class="txt">{html.escape(chr(10).join(body))}</div>'
             '<div class="src"><b>出典</b>' + ''.join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in src) + '</div></article>')
b.append('</div>')
io.open(D + 'review_1116.html', 'w', encoding='utf-8').write('\n'.join(b))
print('ok')
