# -*- coding: utf-8 -*-
# 11/21(土)発売 ロックまとめ（TikTok・70年代ソウルの姐さん）の絵コンテのページ（mk_page_1120.py の形）
#   → tmp/video/matome1124c/board_1121.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'board_1121.html'
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run(['python', D + 'contact17.py'], check=True)
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
endimg = jpg(D + 'frames/h_080.0.png', (540, 960), 86)
cut = jpg(D + 'contact_cut.png', None, 80)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜1秒（TikTok のカバー）', '最初から「11月21日 土曜日の 発売の ロックの チケット 言うわよ」の字と、アフロでマイクスタンドを持つ姐さんが出ている（歌い出しが1.3秒と早いので、前奏の題の字は入れず、この歌詞の塊がそのままカバーになる）'),
        ('0〜11秒（出だし）', '前奏はほとんど無く、すぐ歌に入る。アフロのマイクスタンド →「発売の ロックの」でフェザーカットの姐さん'),
        ('11〜56秒（名前を歌う所）', '歌っている行ごとに、その行の歌い出しの直前の拍で姐さんが替わる＝下の表。歩かせず、まん中にふわっと現れる。1人の出番は2.4〜5.2秒'),
        ('56〜65秒（タップの場面）', '本物の OSHINAVI の画面で「NIGHTMARE」の「11/21 10:00 発売」の箱をピンクの枠でタップ。歌詞「公演と アーティストの 紹介も 載せてるわ」「売り場まで 案内するのは おしなび」'),
        ('65〜88秒（締め）', '「oshinavi.jp なんだわ」。まん中はミラーボールを持つオレンジのボブの姐さん。後奏（約20秒）に4人（マイクスタンド・ピンクのアフロパフ・スカーフ・蹴り上げ）が下りて下の段に並ぶ＝まん中の子と同じ子（反転も）は下に出さない')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0.0〜6.2', 'じゅういちがつ にじゅういちにち どようびの', 'アフロ・マイクスタンド', 'カバーのコマ'),
       ('6.2〜11.4', 'はつばいの ろっくの ちけっと いうわよ', 'フェザーカット・指を天へ（反転）', ''),
       ('11.4〜16.4', 'ごぜん じゅうじは れいてんいちぐらむの ごさん あいち', 'コーンロー・サングラス', '0.1gの誤算'),
       ('16.4〜20.6', 'ないとめあ あいち／はわいあん しっくす とうきょう ほか', '黒いアフロ・タンバリン（反転）', 'NIGHTMARE・HAWAIIAN6'),
       ('20.6〜23.7', 'ざあざあ とうきょう／にゅーろてぃか とうきょう', 'えんじのロング・緑のジャンプスーツ', ''),
       ('23.7〜27.5', 'あいりふどーぱ とうきょう／こふん しすたーず おおさか', 'ピンクのアフロパフ（反転）', '古墳シスターズ'),
       ('27.5〜30.3', 'にこらす とうきょう／やまね やすひろ おおさか', 'オレンジのボブ・ミラーボール', 'NICOLAS'),
       ('30.3〜34.7', 'ひる じゅうにじは きみょう れいたろう とうきょう', 'スカーフ・ターコイズのドレス（反転）', ''),
       ('34.7〜38.8', 'ぷらすてぃっく とぅりー／へぶんすたんぷ かながわ', 'プラチナの髪・蹴り上げ', 'Plastic Tree・Heavenstamp'),
       ('38.8〜41.2', 'ぱーる きょうだい とうきょう ほか', 'アフロ・マイクスタンド（反転）', ''),
       ('41.2〜44.3', 'らいぶはうすで いっしょに さわぎましょ', '黒いアフロ・タンバリン', ''),
       ('44.3〜47.5', 'ほかにも まだまだ あるわよ', 'コーンロー（反転）', ''),
       ('47.5〜51.5', 'おおきな おとで あいたいわ', 'フェザーカット・指を天へ', ''),
       ('51.5〜56.6', 'おしなび どっと じぇーぴーで なまえを けんさくしてね', 'えんじのロング（反転）', ''),
       ('56.6〜64.9', 'こうえんと あーてぃすとの〜うりばまで あんないするのは おしなび', '（本物の OSHINAVI の画面）', 'NIGHTMARE の 11/21 10:00 の箱をタップ'),
       ('64.9〜88.4', 'おしなび どっと じぇーぴー なんだわ・後奏', 'オレンジのボブ・ミラーボール（まん中）＋下に4人', 'マイクスタンド・アフロパフ・スカーフ・蹴り上げ')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>ロックまとめ絵コンテ</title>
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
<h1>11/21(土)発売 ロックまとめ（TikTok）の絵コンテ</h1>
<p>曲は1分28秒（おしなびどっと (37)）、テンポは107前後。絵は70年代ソウル風の姐さん9人（「キャラクター着席編集」のチャットで3人ずつ3枚＝9人とも髪形・ポーズが違う）。背景はすちこが渡した 91898＝黒地にネオンの星（元の明るさと色のまま）。背景が暗いので、歌詞は白（まだ）→黄（歌った所）に濃い縁。名前の書き方は OSHINAVI の登録どおり（NIGHTMARE・HAWAIIAN6・NICOLAS・Plastic Tree・Heavenstamp・古墳シスターズ など）。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と姐さん</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さん</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜30秒＝カバーの字 →「ロックの チケット 言うわよ」→ 0.1gの誤算・NIGHTMARE・HAWAIIAN6 ほか</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め 54〜88秒＝検索してね → タップの場面 → 「oshinavi.jp なんだわ」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>0秒のコマ（カバー）と締めの1コマ（80秒）</h2><div class="two">
<figure><img alt="0秒のコマ" src="data:image/jpeg;base64,{cover}"><figcaption>0秒</figcaption></figure>
<figure><img alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"><figcaption>80秒</figcaption></figure>
</div></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
<section><h2>切り抜いた9人</h2><img alt="切り抜いた9人" src="data:image/jpeg;base64,{cut}"></section>
</main>
'''
io.open(OUT, 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
