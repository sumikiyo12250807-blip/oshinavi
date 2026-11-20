# -*- coding: utf-8 -*-
# 11/15(日)発売 お笑いまとめ（TikTok）の絵コンテのページ：流れ・試し動画2本（縮めて埋め込む）・締めの1コマ（最後の2秒前）・場面ごとの静止画
#   → scratchpad/owarai1115/board_page.html
import base64, io, os, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/3536ac19-4661-4ed4-a7d6-2b6b271a9808/scratchpad/owarai1115/'
os.makedirs(OUT, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
for k in ('clip_a', 'clip_b'):
    subprocess.run([ff, '-y', '-v', 'error', '-i', D + k + '.mp4', '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '28', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + k + '_s.mp4'], check=True)
b = Image.open(D + 'board.png').convert('RGB')
b = b.resize((b.width * 2 // 3, b.height * 2 // 3), Image.LANCZOS)
buf = io.BytesIO(); b.save(buf, 'JPEG', quality=80)
img = base64.b64encode(buf.getvalue()).decode()
end = Image.open(D + 'frames/h_107.3.png').convert('RGB').resize((540, 960))
buf2 = io.BytesIO(); end.save(buf2, 'JPEG', quality=86)
endimg = base64.b64encode(buf2.getvalue()).decode()
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜10秒（前奏）', 'まん中に「11/15(日) 発売の お笑い」。ケーキの子（シートの向き＝右向き）が左から歩いて入ってくる'),
        ('10〜87秒（名前を歌う所）', '約6秒ごとに次の子へ。2枚の絵の子を1人ずつ交互に・向きも右向き／左向き（反転）を交互に。ケーキ → 点心 → ラーメン → パスタ → すし → パン → コーヒー → たこ焼き → ピザ → すし（筆の絵） → BBQ → ケーキ（筆の絵） → 海の幸 → コーヒー（筆の絵） → スイーツの皿。似た組（ケーキ・すし・コーヒー・BBQ）はとなりに置かない'),
        ('87〜96秒（サビ）', '本物の OSHINAVI の画面（スマホの幅）で「ナイツお笑いライブ」の 11/15 10:00 の一般発売の箱をまるごとピンクの枠でタップ。歌詞「売り場まで 案内するのは おしなび」「記事も 書いたわ 読みに 来てね」'),
        ('96〜109秒（締め・後奏）', 'いちばんかわいい、ひまわり帽のアイスの子がまん中で「OSHINAVI.jp だわ」。後奏で1小節に1人ずつ4人（BBQ・ピザ・点心・ケーキ）が上から下りてきて下の段に並ぶ＝左の2人は右向き・右の2人は左向き（まん中を向く）')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
html = f'''<title>お笑い11/15 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#14121c; --panel:#1e1b2a; --fg:#efeaf6; --muted:#b5aec6; --accent:#ffd84a; color-scheme: dark;
  --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
:root[data-theme="light"] {{ --bg:#14121c; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#14121c; }} }}
:root[data-theme="dark"] {{ --bg:#14121c; }}
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
<h1>11/15(日)発売 お笑いまとめ（TikTok）の絵コンテ</h1>
<p>曲 1分49秒・テンポ約102（スネアに合わせた）。グルメの子 2枚・17人（ビールの子は使っていない）。2枚は絵の描き方が違う（目を開けた細かい絵と、目を閉じた筆の絵）＝交互に混ぜた。子は拍に合わせて弾みながら歩いて出入りする。背景はおにぎり柄（字が読めるよう半分の明るさにして少しぼかした）。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>歌い出し（9.5〜24.5秒）＝歌詞の入れ替えと、子の入れ替わり</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め〜終わり（95〜109秒）＝下の段に4人が下りてくる</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・107.3秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒と子）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(OUT + 'board_page.html', 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
