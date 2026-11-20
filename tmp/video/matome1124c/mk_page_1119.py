# -*- coding: utf-8 -*-
# 11/19(木)発売 クラシックまとめ（TikTok）の絵コンテのページ（mk_page_1118.py の形）＝流れ・行と衣装・試し動画2本・0秒のカバー・締めの1コマ・静止画
#   → tmp/video/matome1124c/board_1119.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'board_1119.html'
ff = imageio_ffmpeg.get_ffmpeg_exe()
for k in ('clip_a', 'clip_b'):
    subprocess.run([ff, '-y', '-v', 'error', '-i', D + k + '.mp4', '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '28', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + k + '_s.mp4'], check=True)


def jpg(path, size=None, q=82):
    im = Image.open(path).convert('RGB')
    if size:
        im = im.resize(size, Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q)
    return base64.b64encode(buf.getvalue()).decode()


img = jpg(D + 'contact17.png')
cover = jpg(D + 'frames/h_000.0.png', (540, 960), 86)
endimg = jpg(D + 'frames/h_094.0.png', (540, 960), 86)
cut = jpg(D + 'contact_cut.png', None, 80)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜1秒（TikTok のカバー）', '最初から「クラシック／11/19(木) 発売」の字と、指揮棒を振る姐さんが出ている（0秒のコマをそのままカバーにできる）'),
        ('0〜14秒（出だし）', 'まん中に「11月19日 木曜日の 発売の クラシック 言うわよ」。指揮者の姐さん → 「発売のクラシック」でオペラ歌手（左向き）'),
        ('14〜65秒（名前を歌う所）', '歌っている行に合う楽器の姐さんを、その行の歌い出しの直前の拍で出す＝下の表。演奏家なので歩かせず、まん中にふわっと現れて替わる'),
        ('70〜82秒（タップの場面）', '本物の OSHINAVI の画面で「みなとみらいアフタヌーンコンサート」の「プリセール 11/19 10:00」の箱をピンクの枠でタップ。歌詞「公演と アーティストの 紹介も 載せてるわ」「売り場まで 案内するのは おしなび」'),
        ('82〜96秒（締め）', 'フルートの姐さんがまん中で「oshinavi.jp なんだわ」。後奏に2拍おきに4人（ヴァイオリン・ピアノ＝右向き／オペラ・テューバ＝左向き＝まん中を向く）が上から下りて下の段に並ぶ。終わりの2秒前には5人そろう')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0.0〜6.8', '前奏・じゅういちがつ じゅうくにち もくようびの', '指揮棒を振る指揮者', 'カバーのコマ'),
       ('6.8〜14.2', 'はつばいの くらしっく いうわよ', 'オペラ歌手（左向き）', ''),
       ('14.2〜20.1', 'ごぜん じゅうじは／みなとみらい あふたぬーん こんさーと かながわ', 'グランドピアノ', ''),
       ('20.1〜23.1', 'まえはし ていこ せんじゅ まりこ', 'ヴァイオリン', '前橋汀子さん・千住真理子さん＝ヴァイオリン'),
       ('23.1〜25.3', 'みやた だいも でるわ', 'チェロ', '宮田大さん＝チェロ'),
       ('25.3〜31.2', 'おんがくどう ほりでー あふたぬーん こんさーと かながわ', 'フルート（左向き）', ''),
       ('31.2〜37.9', 'こすげ ゆうと あおい とりおも でるのよ', 'グランドピアノ（左向き）', '小菅優さん＝ピアノ'),
       ('37.9〜40.8', 'ふじおか さちおと ほんどう しゅんやの でんえん とうきょう', 'ハープ', '「田園」'),
       ('40.8〜44.5', 'ちったでぃーの かげきだんの おぺら とうきょう', 'オペラ歌手', 'オペラ'),
       ('44.5〜49.0', 'にほん せんちゅりー こうきょうがくだん おおさか', '指揮者（左向き）', '交響楽団'),
       ('49.0〜51.9', 'ゆーふぉにあむと', 'ユーフォニアム', ''),
       ('51.9〜54.9', 'てゅーばの わーへり きょうと', 'テューバ', 'ワーヘリ＝ユーフォニアムとテューバの二人組'),
       ('54.9〜60.8', 'どれも ききに いきたいわね', 'ハープ（左向き）', ''),
       ('60.8〜65.2', 'なまの おとに つつまれたいわ', 'チェロ（左向き）', ''),
       ('65.2〜70.4', 'おしなび どっと じぇーぴーで なまえを けんさくしてね', 'ユーフォニアム（左向き）', ''),
       ('70.4〜82.7', 'こうえんと あーてぃすとの〜うりばまで あんないするのは おしなび', '（本物の OSHINAVI の画面）', 'みなとみらいの 11/19 10:00 の箱をタップ'),
       ('82.7〜96.0', 'おしなび どっと じぇーぴー なんだわ・後奏', 'フルート（まん中）＋下に4人', 'ヴァイオリン・ピアノ（右向き）／オペラ・テューバ（左向き）')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>クラシックまとめ絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#101a2e; --panel:#1b2742; --fg:#eef3ff; --muted:#b4c2dc; --accent:#ff8ad8; color-scheme: dark; --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
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
th, td {{ text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid #33456a; }}
th {{ color:var(--accent); }}
td.t {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
td b {{ color:var(--accent); }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/19(木)発売 クラシックまとめ（TikTok）の絵コンテ</h1>
<p>曲は1分36秒（おしなび どっと じぇーぴー）、テンポは81（スネアに合わせた・10秒目から終わりまで揺れなし）。絵は近未来のクラシック演奏家の姐さん9人の1枚だけ（光のもやを消してから切り抜いた・9人とも頭から靴の先まで、楽器も元の絵と並べて確かめた）。背景はすちこが選んだ2番＝黒地に赤と青の光の板が飛ぶ（221717・元の明るさと色のまま・主役とは別の背景）。背景が暗いので、歌詞は白（まだ）→黄（歌った所）に濃紺の縁。1人の出番はいちばん長くて7.4秒。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と姐さん</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さん</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜17秒＝カバーの字 → 指揮者 → オペラ歌手 → ピアノ（みなとみらい）</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め 72〜96秒＝タップの場面 → 「oshinavi.jp なんだわ」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>0秒のコマ（カバー）と締めの1コマ（終わりの2秒前・94秒）</h2><div class="two">
<figure><img alt="0秒のコマ" src="data:image/jpeg;base64,{cover}"><figcaption>0秒</figcaption></figure>
<figure><img alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"><figcaption>94秒</figcaption></figure>
</div></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
<section><h2>切り抜いた9人</h2><img alt="切り抜いた9人" src="data:image/jpeg;base64,{cut}"></section>
</main>
'''
io.open(OUT, 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
