# -*- coding: utf-8 -*-
# 11/16(月)発売 スポーツまとめ（TikTok）の絵コンテのページ：流れ・試し動画2本・締めの1コマ（最後の2秒前）・場面ごとの静止画
#   → scratchpad/matome1124c/board_page.html
import base64, io, os, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/47d82dbe-348b-45b6-9b9c-e64a11b39c3d/scratchpad/matome1124c/'
os.makedirs(OUT, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
for k in ('clip_a', 'clip_b'):
    subprocess.run([ff, '-y', '-v', 'error', '-i', D + k + '.mp4', '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '28', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + k + '_s.mp4'], check=True)
b = Image.open(D + 'contact16.png').convert('RGB')
buf = io.BytesIO(); b.save(buf, 'JPEG', quality=82)
img = base64.b64encode(buf.getvalue()).decode()
end = Image.open(D + 'frames/h_073.6.png')   # 終わりの2秒前.convert('RGB').resize((540, 960))
buf2 = io.BytesIO(); end.save(buf2, 'JPEG', quality=86)
endimg = base64.b64encode(buf2.getvalue()).decode()
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
# 全編（縮めて埋め込む＝ページは 16MB まで）
subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'out.mp4', '-vf', 'scale=432:768', '-c:v', 'libx264', '-crf', '30', '-preset', 'medium',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + 'full_s.mp4'], check=True)
full = base64.b64encode(open(D + 'full_s.mp4', 'rb').read()).decode()
for k in ('h_047.0', 'h_051.5', 'h_057.0'):
    pass
rows = [('0〜11.5秒（出だし）', 'まん中に「11月16日の 発売の スポーツ 言うわね」、下に「11/16(月) 発売／スポーツ」。ボクサーの姐さんが歩いて入ってくる'),
        ('11.5〜59秒（名前を歌う所）', '歌っている行に合わせて衣装を替える（行が歌われ始める直前の拍の頭で替える）＝下の表'),
        ('59〜68秒（タップの場面）', '本物の OSHINAVI の画面（スマホの幅）で「大相撲 富士宮場所」の 11/16 10:00 の一般発売の箱をピンクの枠でタップ。歌詞「公演と アーティストの 紹介も 載せてるわ」「売り場まで 案内するのは おしなび」'),
        ('68〜75.6秒（締め・後奏）', 'チアの姐さんがまん中で「oshinavi.jp だわ」。後奏で1拍に1人ずつ4人（バスケット・サッカー・ラグビー・相撲）が上から下りてきて下の段に並ぶ＝左の2人は右向き・右の2人は左向き（まん中を向く）。終わりの2秒前には5人そろう')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0.0〜11.5', '前奏・「11月16日の 発売の スポーツ 言うわね」「午前 10時は」', 'ボクサー', '11.5 秒あるので、8 秒目から1小節ごとに少し大きく跳ねる（服に OSHINAVI の字＝反転しない）'),
       ('11.5〜14.6', 'おおずもう はるじゅんぎょう ふじのみや しずおか', '相撲（化粧まわし）', ''),
       ('14.6〜19.5', 'とうきょう じょし ぷろれす あいち／ひる じゅうにじは', '女子プロレス', ''),
       ('19.5〜21.4', 'すたーだむ おおさか', '女子プロレス（左向き）', 'その場でくるっと向きを変える（歩いて出入りしない）'),
       ('21.4〜24.5', 'さがんとす たい よこはま えふしー さが', 'サッカー', ''),
       ('24.5〜31.9', 'こじまかずやの ふぁんみーてぃんぐ ちば／ゆうがた ろくじは', '野球', ''),
       ('31.9〜38.1', 'くぼた すぴあーず たい しずおか ぶるーれゔず とうきょう／よる はちじは', 'ラグビー（左向き）', ''),
       ('38.1〜45.0', 'にしかわ はるきと まつもと ごうの とーくしょー／すぎや けんしも いっしょよ', '野球（「R」の帽子・前のスポーツの絵の姐さん）', 'すちこ「前に使った子たちはどこにいるの？」＝11/13 の主役の絵（金髪の野球の子）を透明のまま切り抜いた'),
       ('45.0〜49.4', 'ほかにも あるわ わすれないでね', 'バスケット', ''),
       ('49.4〜59.1', 'こえを からして おうえん したいわ／oshinavi.jpで 名前を 検索してね', 'ペンライトのファン', '応援の行＝応援する人。9.7 秒あるので 8 秒目（57.4 秒）から1小節ごとに少し大きく跳ねる（OSHINAVI の字＝反転しない）'),
       ('59.1〜67.9', 'こうえんと あーてぃすとの しょうかいも／うりばまで あんないするのは おしなび', '（本物の OSHINAVI の画面）', '大相撲 富士宮場所の 11/16 10:00 の箱をタップ'),
       ('67.9〜75.6', 'おしなび どっと じぇーぴー だわ', 'チア（まん中）＋下に4人', 'バスケット・サッカー（左・右向き）／ラグビー・相撲（右・左向き）')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>スポーツ11/16 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* 動画の白とピンクに合わせた明るい1色の見た目 */
:root {{ --bg:#fff4f9; --panel:#ffe3ef; --fg:#2a1430; --muted:#6b4d70; --accent:#b0144a; color-scheme: light;
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
.tw {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; min-width:640px; font-size:.95rem; }}
th, td {{ text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid #f3c6d8; }}
th {{ color:var(--accent); font-weight:700; }}
td.t {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
td b {{ color:var(--accent); }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/16(月)発売 スポーツまとめ（TikTok）の絵コンテ</h1>
<p>曲 1分16秒（おしなびどっと (30)）・テンポ 約97（スネアに合わせた・後半が少しゆっくりになる曲なので、40秒すぎからテンポを当て直した）。絵＝すちこが選んだ姐さんのスポーツ9人（あごに水色の剃り跡・背景透明＝透明のまま切り抜いた）＋トークショーの行だけ前のスポーツの絵の「R」の帽子の野球の姐さん。全員、頭・髪の先・帽子・ボール・バット・ポンポン・ペンライト・タオルまで大きくして確かめた。歌っている行に合わせて衣装を替える（相撲の行は化粧まわし、プロレスの行は女子プロレス）。背景＝白とピンクのキラキラ（251638・元の明るさと色のまま・暗くしていない）。背景が明るいので、歌詞は濃紺（まだ）→えんじ（歌った所）に白い太いふち。姐さんがピンクの背景に埋もれないよう、まわりにうすい紫のふちと影を付けた。画面の字は小文字の oshinavi.jp。</p>
</header>
<section><h2>全編（1分16秒）</h2><figure class="end"><video controls playsinline preload="metadata" src="data:video/mp4;base64,{full}"></video><figcaption>書き出した全編を縮めたもの。本物は Downloads の oshinavi_1116_sports_matome.mp4（1080×1920）と _x.mp4（小さい版）</figcaption></figure></section>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と衣装</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さんの衣装</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画（絵コンテの時のもの）</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>9〜24秒＝ボクサー → 相撲 → 女子プロレス → くるっと左向き → サッカー（歌う行に合わせて替わる）</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・73.6秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(OUT + 'board_page.html', 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
