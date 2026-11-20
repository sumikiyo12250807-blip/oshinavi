# -*- coding: utf-8 -*-
# 第2版（歩く子）：試し動画を小さく（540×960）→ ページを作り直す（同じファイル＝同じ URL に出し直す）
import base64, io, os, subprocess, json
import imageio_ffmpeg
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/402b246e-9e52-46c7-9b59-f5c4808ec0be/scratchpad/owarai1113/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
for k in ('walk', 'end'):
    subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'clip_%s.mp4' % k, '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '28', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + 'clip_%s_s.mp4' % k], check=True)
b = Image.open(D + 'board.png').convert('RGB')
buf = io.BytesIO(); b.save(buf, 'JPEG', quality=84)
img = base64.b64encode(buf.getvalue()).decode()
end = Image.open(D + 'frames/h_105.0.png').convert('RGB').resize((540, 960))
buf2 = io.BytesIO(); end.save(buf2, 'JPEG', quality=86)
endimg = base64.b64encode(buf2.getvalue()).decode()
vids = {k: base64.b64encode(open(D + 'clip_%s_s.mp4' % k, 'rb').read()).decode() for k in ('walk', 'end')}
txt = io.open(D + 'prep1113e.txt', encoding='utf-8').read()
cw = [l for l in txt.splitlines() if l.startswith('clip_walk')][0].split()[1]
rows = [('0〜15秒（前奏）', '真ん中に「11/13(金) 発売の お笑い」。キャップの子が左から歩いて入ってくる'),
        ('15〜81秒（名前を歌う所）', '7秒ごとに次の子へ。前の子が右へ歩いて出ていき、次の子が左から歩いて入ってくる＝キャップ → 赤い髪の毛皮コート → スーツケース → 青い髪のトレンチ → NYCニット帽 → 紫の髪の革ジャン → 黒い帽子のトレンチ → 緑の髪のデニム。ここから向きを反対にして3人（毛皮コート・ニット帽・革ジャン）は右から左へ歩く'),
        ('81〜88秒（サビ）', '本物の OSHINAVI の画面で「とろサーモン久保田 初ソロトークライブ」の 11/13 10:00 のバッジをタップ（「発売開始まで あと3日」が見える）'),
        ('88〜107秒（締め・後奏）', 'I♥NYの袋で両手を広げる子が歩いて入ってきて、まん中で足踏み。下の段に1小節に1人ずつ、1枚目の座っている子が4人下りてきて並ぶ')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
html = f'''<title>お笑い11/13 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* 夜のビル街の動画に合わせた暗い見せ方・確認用の静かなページ */
:root {{ --bg:#14121c; --panel:#1e1b2a; --fg:#efeaf6; --muted:#b5aec6; --accent:#ffd84a; color-scheme: dark;
  --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
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
video, img {{ width:100%; max-width:100%; border-radius:8px; background:var(--panel); display:block; }}
.end {{ max-width:360px; }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/13(金)発売 お笑いまとめ（TikTok）の絵コンテ ・ 第2版</h1>
<p>2枚目の歩く子を主役にした版。曲 1分47秒・テンポ 129。子は拍に合わせて弾みながら歩き、着替えのたびに歩いて出入りする。歌詞は前より少し下げ、タップの文字も「あと3日」に重ならない所へずらした。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['walk']}"></video><figcaption>歩いて入れ替わる所（{cw}秒・14秒）</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['end']}"></video><figcaption>サビのタップ〜締め（86.5〜101秒）</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・105秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒と服）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(OUT + 'board_page.html', 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB', cw)
