# -*- coding: utf-8 -*-
# 絵コンテ（4コマ）＋試しの動画（out_x.mp4）を携帯で見るページ board_1127.html
import io, base64, json, os
D = 'C:/Users/user/oshinavi/tmp/x1123/songs/'
b = base64.b64encode(io.open(D + 'board1127.png', 'rb').read()).decode()
v = base64.b64encode(io.open(D + 'out_x.mp4', 'rb').read()).decode()
rows = json.load(io.open(D + 'rows1127.json', encoding='utf-8'))
html = '''<title>11/27 J-POP・ロック 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root{--bg:#0b0d1a;--fg:#e9ecff;--sub:#a9b0d6;--acc:#7fd3ff;color-scheme:dark}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--bg:#f4f5fb;--fg:#15172a;--sub:#4a4f70;--acc:#2a62c9;color-scheme:light}}
:root[data-theme="light"]{--bg:#f4f5fb;--fg:#15172a;--sub:#4a4f70;--acc:#2a62c9;color-scheme:light}
body{background:var(--bg);color:var(--fg);font-family:"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.7;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:16px}
main{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:16px}
h1{font-size:1.2rem;margin:0}
h2{font-size:1rem;margin:0;color:var(--acc)}
p,li{color:var(--sub);margin:0}
ul{margin:0;padding-left:1.2em}
img{width:100%;height:auto;border-radius:10px;display:block}
video{width:100%;max-width:420px;border-radius:12px;display:block;margin:0 auto}
</style>
<main>
<h1>11/27(金)発売 J-POP・ロックのまとめ動画（14番の曲）</h1>
<p>曲＝OSHINAVI.wav（44.7秒）／背景＝96057／姐さん＝サイバーパンク9人（3人ずつ3組が順に出る）。発売の行は下から上へ流れる字幕よ。</p>
<h2>絵コンテ（1秒・12秒・26秒・40秒）</h2>
<img src="data:image/png;base64,''' + b + '''" alt="絵コンテ">
<h2>試しの動画（X 用の軽い版）</h2>
<video controls playsinline src="data:video/mp4;base64,''' + v + '''"></video>
<h2>流れる行（いまの登録で %d 行）</h2>
<ul>''' % len(rows) + ''.join('<li>%s %s／%s%s</li>' % (r['time'], r['name'], r['pref'], r['pre']) for r in rows) + '''</ul>
<p>11/26 の夕方に登録をもう一度読み直して、増えた行を入れて書き出すわ（行が増えると流れる速さが上がる）。</p>
</main>
'''
io.open(D + 'board_1127.html', 'w', encoding='utf-8').write(html)
print(os.path.getsize(D + 'board_1127.html'))
