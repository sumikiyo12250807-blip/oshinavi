# -*- coding: utf-8 -*-
# 11/24(火)発売 クラシックとおでかけまとめ（TikTok・よそ行きの姐さん）の絵コンテのページ（mk_page_1123m.py の形）
#   → tmp/video/matome1124c/board_1124c.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'board_1124c.html'
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
endimg = jpg(D + 'frames/h_088.0.png', (540, 960), 86)
cut = jpg(D + 'contact_move.png', None, 80)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜7秒（TikTok のカバー）', '最初のコマは「クラシックと おでかけ 11/24(火) 発売」の題と、小花柄のワンピースにベレー帽の姐さん。7秒から「11月24日の 発売の クラシックと」の歌詞に替わる'),
        ('7〜19秒（出だし）', '「おでかけの チケット 言うわね」まで、紺のカーディガン → 水色のニットのワンピースの姐さん'),
        ('19〜65秒（名前を歌う所）', '歌っている行ごとに姐さんが替わる＝下の表。2拍おきに同じ服で「動いた絵」（手を振る・髪を押さえる・振り向くなど）に入れ替わって、踊っているように見せる'),
        ('66〜82秒（タップの場面）', '本物の OSHINAVI の画面で「N響大河ドラマ&名曲コンサート」の「11/24 10:00 発売」の箱をタップ'),
        ('82〜97秒（締め）', '「oshinavi.jp なのよ」で、まん中は白いブラウスとベージュのスカートの姐さん。後奏に4人（グレーのタートル・水色のニット・紺のカーディガン・カーキのトレンチ）が下りて下の段に並ぶ')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0〜7', '（前奏）', '小花柄のワンピースにベレー帽', 'カバーのコマ'),
       ('7〜13', 'じゅういちがつ にじゅうよっかの はつばいの くらしっくと', '紺のカーディガンと白いプリーツ（反転）', ''),
       ('13〜19', 'おでかけの ちけっと いうわね', '水色のニットのワンピース', ''),
       ('19〜26', 'あさ じゅうじ しもの たつや と たかはし ひでき とうきょう', 'グレーのタートルネックとパンツ（反転）', '下野竜也・高橋英樹'),
       ('26〜32', 'みやた だい と つじもと れいの ちぇろ とうきょう', 'カーキのトレンチ', '宮田大・辻本玲'),
       ('32〜38', 'かびら じえい いはら つよし あやの かなみ やまぐち', 'ピンクのニットとグレーのスカート（反転）', '川平慈英・伊原剛志・彩乃かなみ'),
       ('38〜47', 'たさん しま おおさか／じゅこう ちゃかい なら せんこう', 'キャメルのコートとマフラー', 'タサン志麻・珠光茶会'),
       ('47〜52', 'じゅういちじ のむら まんさい たち とうきょう せんこう', '白いシャツとデニムのスカート（反転）', '野村萬斎'),
       ('52〜59', 'よる しちじ しんこくりつ げきじょう おぺら とうきょう せんこう', '小花柄のワンピースにベレー帽', '新国立劇場オペラ'),
       ('59〜63', 'ほかにも あるわ', 'カーキのトレンチ（反転）', ''),
       ('63〜66', 'みのがさないでね', '紺のカーディガンと白いプリーツ', ''),
       ('66〜82', 'うりばまで あんないするのは おしなび／こうえんと あーてぃすとの しょうかいも のせてるわ', '（本物の OSHINAVI の画面）', 'N響大河ドラマ&名曲コンサートの 11/24 10:00 の箱をタップ'),
       ('82〜97', 'おしなび どっと じぇーぴー なのよ・後奏', '白いブラウスとベージュのスカート（まん中）＋下に4人', 'グレーのタートル・水色のニット・紺のカーディガン・カーキのトレンチ')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>クラシックおでかけ絵コンテ</title>
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
<h1>11/24(火)発売 クラシックとおでかけまとめ（TikTok）の絵コンテ</h1>
<p>曲は1分37秒（おしなびどっと (38)）、テンポは73前後のゆったりした曲。背景はすちこが渡した 30729＝夕焼けのビル街。絵は普段着でおとなしい感じの清楚な姐さん9人（すちこ「背景も夕暮れ時でしょ　清楚な感じよ」）と、同じ服で動いた絵9枚（2拍おきに入れ替え）。歌詞は白（まだ）→黄（歌った所）。名前の書き方は OSHINAVI の登録どおり。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と姐さん</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さん</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜30秒＝カバーの字 →「クラシックと おでかけの チケット 言うわね」→ 下野竜也・高橋英樹／宮田大・辻本玲</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め 66〜97秒＝タップの場面 →「oshinavi.jp なのよ」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>0秒のコマ（カバー）と締めの1コマ（88秒）</h2><div class="two">
<figure><img alt="0秒のコマ" src="data:image/jpeg;base64,{cover}"><figcaption>0秒</figcaption></figure>
<figure><img alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"><figcaption>88秒</figcaption></figure>
</div></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
<section><h2>9人（元の絵と動いた絵の組）</h2><img alt="切り抜いた9人" src="data:image/jpeg;base64,{cut}"></section>
</main>
'''
io.open(OUT, 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
