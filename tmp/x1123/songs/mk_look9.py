# -*- coding: utf-8 -*-
# サイバーパンクの姐さん9人（2案）を背景 96057 の1コマに重ねて、携帯で見るページ look9_1127.html
import io, base64
from PIL import Image
DL = 'C:/Users/user/Downloads/'
D = 'C:/Users/user/oshinavi/tmp/x1123/songs/'
bg = Image.open(D + 'bg96057_1.png').convert('RGBA').resize((1536, 864))
def comp(f):
    im = Image.open(DL + f).convert('RGBA')
    canvas = Image.new('RGBA', (1536, 1024), (0, 0, 0, 255))
    canvas.paste(bg, (0, 80))
    canvas.alpha_composite(im)
    b = io.BytesIO()
    canvas.convert('RGB').resize((1152, 768)).save(b, 'JPEG', quality=82)
    return base64.b64encode(b.getvalue()).decode()
A, B = comp('cyberrap_chibi_1127c.png'), comp('cyberrap_chibi_1127a.png')
html = '''<title>サイバーパンク姐さん 11/27</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root{--bg:#0b0d1a;--fg:#e9ecff;--sub:#a9b0d6;--acc:#7fd3ff}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--bg:#f4f5fb;--fg:#15172a;--sub:#4a4f70;--acc:#2a62c9;color-scheme:light}}
:root[data-theme="light"]{--bg:#f4f5fb;--fg:#15172a;--sub:#4a4f70;--acc:#2a62c9;color-scheme:light}
:root{color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.7;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:16px}
main{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:18px}
h1{font-size:1.25rem;margin:0}
h2{font-size:1.05rem;margin:0;color:var(--acc)}
p{margin:0;color:var(--sub)}
img{width:100%;height:auto;border-radius:10px;display:block}
section{display:flex;flex-direction:column;gap:8px}
</style>
<main>
<h1>11/27 J-POP・ロックの動画（14番の曲）の姐さん9人</h1>
<p>背景＝背景動画/96057（黒地に青と紫の光の粒）の1コマに重ねた見本よ。服はサイバーパンク。顔は「70年代ヒッピーのステッカーシート」を見本に付けて頼んだわ。</p>
<section><h2>🆕 頼み直した9人（髪形と髪色を1人ずつ指定）</h2><p>①銀のぱっつんボブ ②水色のハイツインテール ③紫の腰までのストレート ④黒に青メッシュのショート ⑤白のハイポニー ⑥ネオンピンクのお団子2つ ⑦ミントのウルフ ⑧青から紫の外ハネ ⑨金の編み込みロング</p><img src="data:image/jpeg;base64,''' + A + '''" alt="頼み直した9人"></section>
<section><h2>（前の案＝9人ともピンクの巻き髪だった分）</h2><img src="data:image/jpeg;base64,''' + B + '''" alt="前の案"></section>
<p>OK をもらったら、絵コンテと試しの動画を作るわね。チケットは11/27発売の J-POP とロックを、下から上へ流れる字幕で出す形よ。</p>
</main>
'''
io.open(D + 'look9_1127.html', 'w', encoding='utf-8').write(html)
