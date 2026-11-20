# -*- coding: utf-8 -*-
# 11/23(月・祝)発売 J-POP・ロックまとめ（TikTok・ビジュアル系の姐さん）の絵コンテのページ（mk_page_1121.py の形）
#   → tmp/video/matome1124c/board_1123m.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'board_1123m.html'
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
endimg = jpg(D + 'frames/h_082.0.png', (540, 960), 86)
cut = jpg(D + 'contact_cut.png', None, 80)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜2秒（TikTok のカバー）', '最初のコマは「J-POP・ロック 11/23(月・祝) 発売」の題と、白金の髪でギターの姐さん。2秒から「11月23日 月曜日の〜」の歌詞に替わる'),
        ('2〜17秒（出だし）', '「発売の J-POPと」で青紫の髪でバラの姐さん →「ロックの チケット 言うところよ」で銀と黒の髪のベース'),
        ('17〜57秒（名前を歌う所）', '歌っている行ごとに姐さんが替わる＝下の表。歩かせず、まん中にふわっと現れる。1人の出番は2.8〜7.1秒'),
        ('65〜75秒（タップの場面）', '本物の OSHINAVI の画面で「Furui Riho」の「11/23 12:00 発売」の箱をピンクの枠でタップ'),
        ('60〜92秒（締め）', '「oshinavi.jp で 名前を 検索してね」から、まん中は黒と赤の髪でマイクの姐さん。後奏に4人（白金ギター・青紫バラ・ピンクのキャンドル・金と紫の日傘）が下りて下の段に並ぶ')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0.0〜6.9', 'じゅういちがつ にじゅうさんにち げつようびの', '白金の髪・ギター', 'カバーのコマ'),
       ('6.9〜11.8', 'はつばいの じぇいぽっぷと', '青紫の髪・バラ（反転）', ''),
       ('11.8〜16.8', 'ろっくの ちけっと いうところよ', '銀と黒の髪・ベース', ''),
       ('16.8〜20.3', 'ごぜん じゅうじは みなみ よしたか', 'ワインレッドのボブ（反転）', '南佳孝'),
       ('20.3〜23.8', 'ばれんたいん でぃなーあんどらいぶ ひょうご', '真っ白の結い上げ・ステッキ', ''),
       ('23.8〜26.7', 'でんのう ひめか あいち', '深緑の髪・ドラムスティック（反転）', '電脳ヒメカ'),
       ('26.7〜31.6', 'ひる じゅうにじは ふるい りほ とうきょう', 'ピンクと黒の髪・キャンドル', 'Furui Riho'),
       ('31.6〜35.8', 'めぐみ とうきょう／いがり しょういち また ここで とうきょう', '金と紫の髪・日傘（反転）', 'め組・猪狩翔一'),
       ('35.8〜39.4', 'ねす ぷりえーる かいん あいち', '青紫の髪・バラ', 'NETH PRIERE CAIN'),
       ('39.4〜44.3', 'じんかく らぢお かながわ', '白金の髪・ギター（反転）', '人格ラヂオ'),
       ('44.3〜49.9', 'よる じゅうじは そりっど すてーとめんと そうる とうきょう ほか', 'ワインレッドのボブ', 'Solid Statement Soul'),
       ('49.9〜57.0', 'ほかにも まだ あるわよ', '銀と黒の髪・ベース（反転）', ''),
       ('57.0〜59.8', 'らいぶで いっしょに うたいたいわ', '深緑の髪・ドラムスティック', ''),
       ('59.8〜65', 'おしなび どっと じぇーぴーで なまえを けんさくしてね', '黒と赤の髪・マイク', ''),
       ('65〜75', 'こうえんと あーてぃすとの〜うりばまで あんないするのは おしなび', '（本物の OSHINAVI の画面）', 'Furui Riho の 11/23 12:00 の箱をタップ'),
       ('75〜92', 'おしなび どっと じぇーぴー だわよ・後奏', '黒と赤の髪・マイク（まん中）＋下に4人', '白金ギター・青紫バラ・キャンドル・日傘')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>J-POPロック絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#120f1a; --panel:#221c2e; --fg:#f6f0ff; --muted:#c9bcdc; --accent:#ffb347; color-scheme: dark; --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
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
th, td {{ text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid #3a3050; }}
th {{ color:var(--accent); }}
td.t {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
td b {{ color:var(--accent); }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/23(月・祝)発売 J-POP・ロックまとめ（TikTok・ビジュアル系）の絵コンテ</h1>
<p>曲は1分32秒（おしなびどっとじぇーぴー (4)）、テンポは85前後。絵はすちこの「ビジュアル系姐さん」＝ビジュアル系の姐さん9人（髪の色・髪形・持ち物が全員ちがう）。背景はすちこが渡した 34210＝緑と橙の光が放射状に広がる。歌詞は白（まだ）→黄（歌った所）に濃い縁。名前の書き方は OSHINAVI の登録どおり（Furui Riho・め組・NETH PRIERE CAIN・人格ラヂオ・Solid Statement Soul など）。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と姐さん</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さん</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜30秒＝カバーの字 →「J-POPと ロックの チケット 言うところよ」→ 南佳孝・電脳ヒメカ・Furui Riho</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め 62〜92秒＝検索してね → タップの場面 →「oshinavi.jp だわよ」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>0秒のコマ（カバー）と締めの1コマ（82秒）</h2><div class="two">
<figure><img alt="0秒のコマ" src="data:image/jpeg;base64,{cover}"><figcaption>0秒</figcaption></figure>
<figure><img alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"><figcaption>82秒</figcaption></figure>
</div></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
<section><h2>切り抜いた9人</h2><img alt="切り抜いた9人" src="data:image/jpeg;base64,{cut}"></section>
</main>
'''
io.open(OUT, 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
