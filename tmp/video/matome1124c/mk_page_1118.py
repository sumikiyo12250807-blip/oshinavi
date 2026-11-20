# -*- coding: utf-8 -*-
# 11/18(水)発売 舞台・トークショーまとめ（TikTok）の絵コンテのページ：mk_page_1117.py の形（流れ・行と衣装・試し動画2本・締めの1コマ・静止画）
#   → scratchpad/board_1118.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, os, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/4d4d2b83-bf2e-4e0a-accb-7c4eeb80f184/scratchpad/board_1118.html'
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
endimg = jpg(D + 'frames/h_074.1.png', (540, 960), 86)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜11.6秒（出だし）', 'まん中に「11月18日 水曜日の 発売の 舞台と トークショー 言うわね」、下に「11/18(水) 発売／舞台・トークショー」。ミュージカルの衣装でお辞儀する姐さんが歩いて入る'),
        ('11.6〜52.6秒（名前を歌う所）', '歌っている行に合わせて衣装を替える（行が歌われ始める直前の拍の頭）＝下の表。座っている子（野球のトーク・ソファの司会・バンドネオン）は歩かせず、まん中にふわっと出る'),
        ('52.6〜59.8秒（タップの場面）', '本物の OSHINAVI の画面（スマホの幅）で『スウィーニー・トッド』の「先着一般発売（東京 R9年 3/16公演）11/18 11:00」の箱をピンクの枠でタップ。歌詞「公演と アーティストの 紹介も 載せてるわ」「売り場まで 案内するのは おしなび」'),
        ('59.8〜76.1秒（締め）', '赤いドレスの姐さんがまん中で「oshinavi.jp なのよ」。この曲は後奏が13秒あるので、2拍おきに4人（お辞儀・稽古着・マラソン・和の扇）が上から下りて下の段に並ぶ＝左2人は右向き・右2人は左向き（まん中を向く）。終わりの2秒前には5人そろう')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0.0〜8.5', '前奏・じゅういちがつ じゅうはちにち すいようびの はつばいの ぶたいと', 'ミュージカルの衣装でお辞儀', '歩いて入る'),
       ('8.5〜11.6', 'とーくしょー いうわね', 'ソファでトークショーの司会', ''),
       ('11.6〜16.6', 'ごぜん じゅうじは／うえはら こうじの とーくらいぶ あいち', '野球のユニフォームでマイク', '元プロ野球選手のトーク'),
       ('16.6〜19.6', 'やまもと まさ やまさき たけし ふくどめ こうすけも でるわ', '野球のユニフォームでマイク（左向き）', 'その場で向きを変える'),
       ('19.6〜21.6', 'ますだ あけみと', 'マラソンランナー', '増田明美さん＝マラソン'),
       ('21.6〜23.6', 'こまつ りょうた ひろしま', 'バンドネオンを弾くタンゴのドレス', '小松亮太さん＝バンドネオン'),
       ('23.6〜27.6', 'とくめいげきだん おおさか', '稽古着で台本を持つ', '劇団'),
       ('27.6〜34.6', 'ごぜん じゅういちじは／みゅーじかる すうぃーにー とっど とうきょう', 'ロンドン風の黒いドレスとシルクハット', ''),
       ('34.6〜40.6', 'ひる じゅうにじは／もとき だいすけの とーくしょー', 'ソファでトークショーの司会（左向き）', ''),
       ('40.6〜44.6', 'ほかにも あるわ わすれないでね', '和の舞台衣装で扇を広げる', ''),
       ('44.6〜52.6', 'ぶたいの まくが あがるのが たのしみだわ／けんさくしてね', 'ミュージカルの衣装でお辞儀（左向き）', ''),
       ('52.6〜59.8', 'こうえんと あーてぃすとの しょうかいも のせてるわ／うりばまで あんないするのは おしなび', '（本物の OSHINAVI の画面）', 'スウィーニー・トッドの 11/18 11:00 の箱をタップ'),
       ('59.8〜76.1', 'おしなび どっと じぇーぴー なのよ・後奏', '赤いドレスでスポットライト（まん中）＋下に4人', 'お辞儀・稽古着（右向き）／マラソン・和の扇（左向き）')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>舞台まとめ 11/18 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#1c1026; --panel:#2a1838; --fg:#f6ecff; --muted:#c8b4d8; --accent:#ff8ad8; color-scheme: dark; --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.7; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 48px; }}
main {{ max-width:1100px; margin:0 auto; display:grid; gap:28px; }}
h1 {{ font-size:1.5rem; margin:0; text-wrap:balance; }}
h2 {{ font-size:1.1rem; margin:0 0 10px; color:var(--accent); }}
p {{ margin:0; color:var(--muted); max-width:65ch; }}
ul {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
li {{ display:grid; grid-template-columns:minmax(0,12em) minmax(0,1fr); gap:12px; padding:10px 12px; background:var(--panel); border-radius:8px; }}
li b {{ color:var(--accent); }}
@media (max-width:640px) {{ li {{ grid-template-columns:1fr; gap:2px; }} }}
.vids {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }}
figure {{ margin:0; display:grid; gap:6px; min-width:0; }}
figcaption {{ color:var(--muted); font-size:.92rem; }}
video, img {{ width:100%; max-width:100%; border-radius:8px; background:var(--panel); display:block; }}
.end {{ max-width:360px; }}
.tw {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; min-width:640px; font-size:.95rem; }}
th, td {{ text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid #4a3060; }}
th {{ color:var(--accent); }}
td.t {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
td b {{ color:var(--accent); }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/18(水)発売 舞台・トークショーまとめ（TikTok）の絵コンテ</h1>
<p>曲 1分16秒（おしなび どっと じぇーぴー）・テンポ 60（スネアに合わせた・10秒目から終わりまで揺れなし）。絵＝舞台の姐さん9人の1枚だけ（背景透明のまま切り抜いた・9人とも頭のてっぺんから靴の先まで、羽根・扇・ステッキ・バンドネオンも元の絵と並べて確かめた）。背景＝すちこが選んだ緑の光（21865・元の明るさと色のまま）。背景が暗いので歌詞は白（まだ）→黄（歌った所）。1人の出番はいちばん長くて 8 秒。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と衣装</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さんの衣装</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜17秒＝前奏の字 → お辞儀の子が歩いて入る → ソファの司会 → 野球のトーク</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め 50〜76秒＝検索の行 → タップの場面 → 「oshinavi.jp なのよ」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・74.1秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(OUT, 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
