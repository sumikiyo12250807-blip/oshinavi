# -*- coding: utf-8 -*-
# 絵コンテ（タップのコマを撮り直しで差し替え）＋試し動画2本を1枚のページに（画像・動画は data URI）→ board_page.html
import base64, io, os
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/402b246e-9e52-46c7-9b59-f5c4808ec0be/scratchpad/owarai1113/'
os.makedirs(OUT, exist_ok=True)
b = Image.open(D + 'board.png').convert('RGB')
W, H = 360, 640
tile = Image.open(D + 'frames/h_083.8.png').convert('RGB').resize((W, H))
b.paste(tile, (0, 2 * (H + 50) + 40))
buf = io.BytesIO(); b.save(buf, 'JPEG', quality=86)
img = base64.b64encode(buf.getvalue()).decode()
end = Image.open(D + 'frames/h_105.0.png').convert('RGB').resize((540, 960))
buf2 = io.BytesIO(); end.save(buf2, 'JPEG', quality=86)
endimg = base64.b64encode(buf2.getvalue()).decode()
vids = {k: base64.b64encode(open(D + f, 'rb').read()).decode() for k, f in (('names', 'clip_names_s.mp4'), ('end', 'clip_end_s.mp4'))}
rows = [('0〜15秒（前奏）', '真ん中に「11/13(金) 発売の お笑い」。キャラは帽子でしゃがむ子'),
        ('15〜81秒（名前を歌う所）', '7秒ごとに着替え（1人8秒以内）＝しゃがむ子 → I♥NYの袋の子 → コーヒーで歩く子 → スケボーの子 → NYCのニット帽の子 → 黒い帽子の子 → 革ジャンの子 → ここから向きを反対にして4人（歩く子・スケボー・しゃがむ子・ニット帽）'),
        ('81〜88秒（サビ）', '本物の OSHINAVI の画面で「とろサーモン久保田 初ソロトークライブ」の 11/13 10:00 のバッジをタップ'),
        ('88〜107秒（締め・後奏）', 'いちばんかわいい投げキッスの子が上に。下の段に1小節に1人ずつ4人が下りてきて並ぶ（I♥NYの子・黒い帽子の子・革ジャンの子・ニット帽の子）＝真ん中が空かない')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
html = f'''<title>お笑い11/13 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* 夜のビル街の動画に合わせた暗い見せ方・確認用の静かなページ */
:root {{ --bg:#14121c; --panel:#1e1b2a; --fg:#efeaf6; --muted:#b5aec6; --accent:#ffd84a; --line:#2f2a40; color-scheme: dark;
  --sans: "Zen Kaku Gothic New", "Hiragino Sans", "Meiryo", sans-serif; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.7; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 48px; }}
main {{ max-width:1100px; margin:0 auto; display:grid; gap:28px; }}
h1 {{ font-size:1.5rem; margin:0; text-wrap:balance; }}
h2 {{ font-size:1.1rem; margin:0 0 10px; color:var(--accent); }}
p {{ margin:0; color:var(--muted); max-width:65ch; }}
ul {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
li {{ display:grid; grid-template-columns:minmax(0,12em) minmax(0,1fr); gap:12px; padding:10px 12px; background:var(--panel); border-radius:8px; }}
li b {{ color:var(--accent); font-weight:700; }}
@media (max-width:640px) {{ li {{ grid-template-columns:1fr; gap:2px; }} }}
.vids {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }}
figure {{ margin:0; display:grid; gap:6px; min-width:0; }}
figcaption {{ color:var(--muted); font-size:.92rem; }}
video, img {{ width:100%; max-width:100%; border-radius:8px; background:#000; display:block; }}
.end {{ max-width:360px; }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/13(金)発売 お笑いまとめ（TikTok）の絵コンテ</h1>
<p>曲 1分47秒・テンポ 129。キャラはニューヨークの子8人（緑の髪の子は使っていない）。歌詞は2〜3小節ずつ、まとめて出して入れ替え。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['names']}"></video><figcaption>名前がいちばん詰まった所（44.6〜58.9秒）</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['end']}"></video><figcaption>サビのタップ〜締め（86.5〜101秒）</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・105秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒と服）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(OUT + 'board_page.html', 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
