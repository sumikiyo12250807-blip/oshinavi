# -*- coding: utf-8 -*-
# 11/14(土)発売 お笑いまとめ（X）の絵コンテのページ：流れ・試し動画2本（縮めて埋め込む）・締めの1コマ（最後の2秒前）・場面ごとの静止画
#   → scratchpad/owarai1114/board_page.html
import base64, io, os, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/47d82dbe-348b-45b6-9b9c-e64a11b39c3d/scratchpad/owarai1114/'
os.makedirs(OUT, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
for k in ('clip_a', 'clip_b'):
    subprocess.run([ff, '-y', '-v', 'error', '-i', D + k + '.mp4', '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '28', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + k + '_s.mp4'], check=True)
b = Image.open(D + 'board.png').convert('RGB')
b = b.resize((b.width * 2 // 3, b.height * 2 // 3), Image.LANCZOS)
buf = io.BytesIO(); b.save(buf, 'JPEG', quality=80)
img = base64.b64encode(buf.getvalue()).decode()
end = Image.open(D + 'frames/h_065.6.png').convert('RGB').resize((540, 960))
buf2 = io.BytesIO(); end.save(buf2, 'JPEG', quality=86)
endimg = base64.b64encode(buf2.getvalue()).decode()
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜9.5秒（前奏・掛け声）', 'まん中に「明日 11月14日の 発売の お笑い 言うわよ」、下に「明日 11/14(土) 発売／お笑い」。紫の魔女の子が左から歩いて入ってくる'),
        ('9.5〜47.5秒（名前を歌う所）', '約4.8秒（2小節）ごとに次の子へ。2枚の絵の子を1人ずつ交互に・向きも右向き／左向き（反転）を交互に。紫の魔女 → 氷の女王 → エルフの弓 → 海賊 → 人魚（まん中にふわっと） → 炎の魔女 → 赤い踊り子 → スチームパンク → 悪魔 → 九尾（ちょうちん）。似た組（九尾2人・魔女3人・こうもりの羽2人・エルフ2人・剣の2人）はとなりに置かない。九尾は1人だけ使った'),
        ('47.5〜55.6秒（タップの場面）', '本物の OSHINAVI の画面（スマホの幅）で「さらば青春の光寄席」の 11/14 11:00 の一般発売の箱をピンクの枠でタップ。歌詞「公演と アーティストの 紹介も 載せてるわ」「売り場まで 案内するのは おしなび」'),
        ('55.6〜67.6秒（締め・後奏）', 'いちばん華やかな天使の子がまん中で「OSHINAVI.jp なのよ」。後奏で2拍に1人ずつ4人（薬の魔女・妖精・吸血鬼・森の鹿の子）が上から下りてきて下の段に並ぶ＝左の2人は右向き・右の2人は左向き（まん中を向く）。終わりの2秒前には5人そろう')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
html = f'''<title>お笑い11/14 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* 動画の紫の夜に合わせた暗い1色の見た目（明るいテーマでも同じ） */
:root {{ --bg:#16111f; --panel:#221a30; --fg:#f1ebf8; --muted:#bdb2cf; --accent:#ffd84a; color-scheme: dark;
  --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.7; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 48px; }}
main {{ max-width:1100px; margin:0 auto; display:grid; gap:28px; }}
h1 {{ font-size:1.5rem; margin:0; text-wrap:balance; }}
h2 {{ font-size:1.1rem; margin:0 0 10px; color:var(--accent); }}
p {{ margin:0; color:var(--muted); max-width:65ch; }}
ul {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
li {{ display:grid; grid-template-columns:minmax(0,12em) minmax(0,1fr); gap:12px; padding:10px 12px; background:var(--panel); border-radius:8px; }}
li b {{ color:var(--accent); font-weight:700; }}
li span {{ min-width:0; }}
@media (max-width:640px) {{ li {{ grid-template-columns:1fr; gap:2px; }} }}
.vids {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }}
figure {{ margin:0; display:grid; gap:6px; min-width:0; }}
figcaption {{ color:var(--muted); font-size:.92rem; }}
video, img {{ width:100%; max-width:100%; border-radius:8px; background:var(--panel); display:block; }}
.end {{ max-width:360px; }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/14(土)発売 お笑いまとめ（X）の絵コンテ</h1>
<p>曲 1分8秒（おしなびどっと (28)）・テンポ 101（スネアに合わせた・最初から最後までずれ 0.004 秒以内）。絵＝ちびファンタジーの子 2枚（「華やかな九人」と「grid collage」）。同じピンク髪の子の衣装違いなので2枚を交互に混ぜた。使ったのは18人のうち15人。背景＝紫の地に赤い光の粒が渦を巻く動画（7472・もとから暗いので暗くしていない）。子は拍に合わせて弾みながら歩いて出入りする。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>歌い出し（9〜24秒）＝歌詞の入れ替えと、子の入れ替わり</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>タップ〜締め〜終わり（52〜67.6秒）＝下の段に4人が下りてくる</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・65.6秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒と子）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(OUT + 'board_page.html', 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
