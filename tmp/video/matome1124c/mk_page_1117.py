# -*- coding: utf-8 -*-
# 11/17(火)発売 J-POP まとめ（TikTok）の絵コンテのページ：流れ・行と衣装の対応表・試し動画2本・締めの1コマ（終わりの2秒前）・場面ごとの静止画
#   → tmp/video/matome1124c/board_1117.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, os, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
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
endimg = jpg(D + 'frames/h_058.9.png', (540, 960), 86)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜13.3秒（出だし）', 'まん中に「J-POP／11/17(火) 発売」→「11月17日 火曜日の 発売の J-POP 言うわね」「午前 10時は」、下に「11/17(火) 発売／J-POP」。金のドレスで踊る姐さんが歩いて入り、6秒でその場でくるっと向きを変える'),
        ('13.3〜50.1秒（名前を歌う所）', '歌っている行に合わせて衣装を替える（行が歌われ始める直前の拍の頭）＝下の表。楽器を据えた子（スタンドマイク・座ってアコギ・キーボード）は歩かせず、まん中にふわっと出る'),
        ('50.1〜57.3秒（タップの場面）', '本物の OSHINAVI の画面（スマホの幅）で「尾崎裕哉Concert2027」の「一般発売（東京 R9年 3/14公演）11/17 10:00」の箱をピンクの枠でタップ。歌詞「公演と アーティストの 紹介も 載せてるわ」「売り場まで 案内するのは おしなび」'),
        ('57.3〜60.9秒（締め）', '両手を広げる姐さんがまん中で「oshinavi.jp なのよ」。この曲は後奏がほぼ無い（歌い終わり 60.4 秒）ので、締めに入ってすぐ 0.3 秒おきに4人（ペンライトのファン・金のダンス・ハンドマイク・ヘッドセット）が上から下りて下の段に並ぶ＝左2人は右向き・右2人は左向き（まん中を向く）。終わりの2秒前には5人そろう')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0.0〜6.1', '前奏・じゅういちがつ じゅうしちにち かようびの', '金のドレスでダンス（右向き）', '歩いて入る'),
       ('6.1〜13.3', 'はつばいの じぇいぽっぷ いうわね／ごぜん じゅうじは', '金のドレスでダンス（左向き）', 'その場でくるっと向きを変える（同じ服を続けて 7.2 秒）'),
       ('13.3〜18.1', 'ろっくんろーる さーかす にせんにじゅうなな ひょうご', 'エレキギター', ''),
       ('18.1〜20.5', 'きむら てつじ あいち', 'スタンドマイク（白いドレス）', '演歌寄りの歌手＝スタンドマイク'),
       ('20.5〜24.5', 'おざき ひろや とうきょう', '座ってアコースティックギター', ''),
       ('24.5〜30.9', 'ごぜん じゅういちじは／たかはし ゆう ほっかいどう', 'ハンドマイクで手を振る', ''),
       ('30.9〜37.3', 'ひる じゅうにじは／むつむろ あきらの らいぶ とうきょう', 'キーボード', 'ギターは先に使ったのでキーボード'),
       ('37.3〜41.3', 'ほかにも あるわ わすれないでね', 'ヘッドセットで踊る', ''),
       ('41.3〜44.5', 'すきな うたを なまで ききたいわ', 'ペンライトを振るファン（右向き）', ''),
       ('44.5〜50.1', 'おしなび どっと じぇーぴーで なまえを けんさくしてね', 'ペンライトを振るファン（左向き）', 'その場でくるっと向きを変える（1人8秒以内のため）'),
       ('50.1〜57.3', 'こうえんと あーてぃすとの しょうかいも のせてるわ／うりばまで あんないするのは おしなび', '（本物の OSHINAVI の画面）', '尾崎裕哉の 11/17 10:00 の箱をタップ'),
       ('57.3〜60.9', 'おしなび どっと じぇーぴー なのよ', '両手を広げる（まん中）＋下に4人', 'ペンライトのファン・金のダンス（左・右向き）／ハンドマイク・ヘッドセット（右・左向き）')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>J-POP 11/17 絵コンテ</title>
<style>
:root {{ --bg:#1c1026; --panel:#2a1838; --fg:#f6ecff; --muted:#c8b4d8; --accent:#ff8ad8; color-scheme: dark;
  --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.7; margin:0; padding:24px 16px 48px; }}
main {{ max-width:1100px; margin:0 auto; display:grid; gap:28px; }}
h1 {{ font-size:1.5rem; margin:0; }}
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
<h1>11/17(火)発売 J-POPまとめ（TikTok）の絵コンテ</h1>
<p>曲 1分1秒（おしなびどっと (31)）・テンポ 75（スネアに合わせた・曲の頭から終わりまで揺れなし）。絵＝J-POP のちび姐さん9人の1枚だけ（背景透明＝透明のまま切り抜いた・金のダンスの子に付いた下の子の輪郭線は落とした・全員、頭・髪の先・楽器・ペンライトまで大きくして確かめた）。歌っている行に合わせて衣装を替える。背景＝紫のきらめき（7472・元の明るさと色のまま・暗くしていない）。背景が暗いので歌詞は白（まだ）→黄（歌った所）に濃紺のふち。画面の字は小文字の oshinavi.jp。1人の出番はいちばん長くて 7.2 秒。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と衣装</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さんの衣装</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜15.5秒＝前奏の字 → 金のダンスが歩いて入る → くるっと向きを変える → エレキの子（ロックンロールサーカス）</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め 46.5〜60.9秒＝検索の行 → タップの場面 → 「oshinavi.jp なのよ」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・58.9秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(D + 'board_1117.html', 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
