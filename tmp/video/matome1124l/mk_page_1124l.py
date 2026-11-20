# -*- coding: utf-8 -*-
# 11/24(火)発売 クラシックとおでかけまとめ（TikTok・よそ行きの姐さん）の絵コンテのページ（mk_page_1123m.py の形）
#   → tmp/video/matome1124l/board_1124l.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124l/'
OUT = D + 'board_1124l.html'
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run(['python', D + 'contact17.py'], check=True)
for k in ('clip_a', 'clip_b'):
    subprocess.run([ff, '-y', '-v', 'error', '-i', D + k + '.mp4', '-vf', 'scale=432:768', '-c:v', 'libx264', '-crf', '30', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + k + '_s.mp4'], check=True)


def jpg(path, size=None, q=82):
    im = Image.open(path).convert('RGB')
    if size:
        im = im.resize(size, Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q)
    return base64.b64encode(buf.getvalue()).decode()


img = jpg(D + 'contact17.png')
cover = jpg(D + 'frames/h_000.0.png', (540, 960), 86)
endimg = jpg(D + 'frames/h_047.0.png', (540, 960), 86)
cut = jpg(D + 'contact_move.png', None, 80)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜2秒（TikTok のカバー）', '最初のコマは「ライブ 11/24(火) 発売」の題と、クリーム色のジャケットと帽子の姐さん。2.5秒から歌い出し'),
        ('2.5〜7秒（出だし）', '「11月24日の 発売の ライブの チケット 言うわよ」まで、水玉のワンピース（反転）の姐さん'),
        ('7〜33秒（名前を歌う所）', '歌っている行ごとに姐さんが替わる＝下の表。2拍おきに同じ服で「動いた絵」（乾杯・振り向く・会釈など）に入れ替わる'),
        ('35〜43秒（タップの場面）', '本物の OSHINAVI の画面で「奇妙礼太郎BAND／在日ファンク」の「11/24 10:00 発売」の箱をタップ'),
        ('43〜51秒（締め）', '「oshinavi.jp だわ」で、まん中は赤いドレスでグラスの姐さん。後奏に4人（白いスーツ・花柄の着物・紺のコート・水玉）が下りて下の段に並ぶ')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0〜2.5', '（前奏）', 'クリーム色のジャケットと帽子', 'カバーのコマ'),
       ('2.5〜7', 'じゅういちがつ にじゅうよっかの はつばいの らいぶの ちけっと いうわよ', '水玉のワンピース（反転）', ''),
       ('7〜12', 'あさ じゅうじ きみょう れいたろう ばんど と', '紺のベルベットのコート', '奇妙礼太郎BAND'),
       ('12〜14', 'ざいにち ふぁんく とうきょう', '花柄の着物（反転）', '在日ファンク'),
       ('14〜19', 'じゅういちじ でぃーん ほっかいどう せんこう', '大正ロマンの袴', 'DEEN'),
       ('19〜23', 'ゆうがた ろくじ あくのゆめ と ひまつぶし とうきょう', '白いパンツスーツと帽子（反転）', '惡ノ夢・暇潰シ'),
       ('23〜27', 'よる くじ とうきょう あいどる げきじょう とうきょう きゅーくる', 'エメラルドのドレス', '東京アイドル劇場・きゅ〜くる'),
       ('27〜33', 'よる じゅうじ すぎ かくめい どーぷねす たち とうきょう', '藤色の着物・扇子（反転）', '革命-DOPENESS-'),
       ('33〜35', 'わすれないでね', '水玉のワンピース', ''),
       ('35〜43', 'うりばまで あんないするのは おしなび／こうえんと あーてぃすとの しょうかいも のせてるわ', '（本物の OSHINAVI の画面）', '奇妙礼太郎BAND／在日ファンクの 11/24 10:00 の箱をタップ'),
       ('43〜51', 'おしなび どっと じぇーぴー だわ・後奏', '赤いドレス・グラス（まん中）＋下に4人', '白いスーツ・花柄の着物・紺のコート・水玉')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>ライブまとめ絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#140f12; --panel:#271c22; --fg:#fff3ec; --muted:#dcc7bb; --accent:#ffb36b; color-scheme: dark; --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.7; margin:0; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 48px; }}
main {{ max-width:1100px; margin:0 auto; display:grid; gap:28px; }}
h1 {{ font-size:1.5rem; margin:0; text-wrap:balance; }}
h2 {{ font-size:1.1rem; margin:0 0 10px; color:var(--accent); }}
p {{ margin:0; color:var(--muted); max-width:65ch; }}
ul {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
li {{ display:grid; grid-template-columns:minmax(0,12em) minmax(0,1fr); gap:12px; padding:10px 12px; background:var(--panel); border-radius:8px; }}
li b {{ color:var(--accent); }}
@media (max-width:640px) {{ li {{ grid-template-columns:1fr; gap:2px; }} }}
.vids, .two {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }}
figure {{ margin:0; display:grid; gap:6px; min-width:0; }}
figcaption {{ color:var(--muted); font-size:.92rem; }}
video, img {{ width:100%; max-width:100%; border-radius:8px; background:var(--panel); display:block; }}
.tw {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; min-width:640px; font-size:.95rem; }}
th, td {{ text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid #4a3540; }}
th {{ color:var(--accent); }}
td.t {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
td b {{ color:var(--accent); }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/24(火)発売 ライブまとめ（TikTok）の絵コンテ</h1>
<p>曲は51秒（わすれないでね）、テンポは114前後。背景はすちこが渡した 38389＝黒地に小さな光が舞う（7秒をくり返し）。絵は 1124c で描いた「よそ行きの姐さん」9人と、同じ服で動いた絵（すちこ「2本目に今絵コンテ出してくれたファッション合うわ」）。歌詞は白（まだ）→黄（歌った所）。名前の書き方は OSHINAVI の登録どおり。きゅ〜くるの行は 0.7 秒しかないので、東京アイドル劇場の行に並べた。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と姐さん</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さん</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜25秒＝カバーの字 →「ライブの チケット 言うわよ」→ 奇妙礼太郎BAND・在日ファンク／DEEN／惡ノ夢・暇潰シ／東京アイドル劇場</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>26〜51秒＝革命-DOPENESS- →「忘れないでね」→ タップの場面 →「oshinavi.jp だわ」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>0秒のコマ（カバー）と締めの1コマ（47秒）</h2><div class="two">
<figure><img alt="0秒のコマ" src="data:image/jpeg;base64,{cover}"><figcaption>0秒</figcaption></figure>
<figure><img alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"><figcaption>47秒</figcaption></figure>
</div></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
<section><h2>9人（元の絵と動いた絵の組）</h2><img alt="切り抜いた9人" src="data:image/jpeg;base64,{cut}"></section>
</main>
'''
io.open(OUT, 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
