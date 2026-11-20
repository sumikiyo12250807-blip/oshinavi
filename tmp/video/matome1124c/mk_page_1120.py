# -*- coding: utf-8 -*-
# 11/20(金)発売 J-POP まとめ（TikTok・ゴスロリの姐さん）の絵コンテのページ（mk_page_1119.py の形）
#   → tmp/video/matome1124c/board_1120.html（全編はまだ書き出していない＝すちこの OK 待ち）
import base64, io, subprocess
from PIL import Image
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'board_1120.html'
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
endimg = jpg(D + 'frames/h_104.0.png', (540, 960), 86)
cut = jpg(D + 'contact_cut.png', None, 80)
vids = {k: base64.b64encode(open(D + '%s_s.mp4' % k, 'rb').read()).decode() for k in ('clip_a', 'clip_b')}
rows = [('0〜1秒（TikTok のカバー）', '最初から「J-POP／11/20(金) 発売」の字と、黒い縦ロールで紅茶を飲むゴスロリ姐さんが出ている（0秒のコマをそのままカバーにできる）'),
        ('0〜30秒（出だし）', '前奏は約12秒。まん中に「11月20日 金曜日の 発売の J-POPの チケット 言うわよ」。マイクの姐さん →「発売のJ-POP」で赤いツインテールの姐さん'),
        ('30〜73秒（名前を歌う所）', '歌っている行ごとに、その行の歌い出しの直前の拍でゴスロリの姐さんが替わる＝下の表。歩かせず、まん中にふわっと現れる'),
        ('77〜85秒（タップの場面）', '本物の OSHINAVI の画面で「世良公則」の「11/20 10:00 発売」の箱をピンクの枠でタップ。歌詞「公演と アーティストの 紹介も 載せてるわ」「売り場まで 案内するのは おしなび」'),
        ('85〜108秒（締め）', 'すちこが足した「Xの フォローも しておいて／毎日 情報 発信しているの」→「oshinavi.jp なのよね」。まん中は王冠をのせてお辞儀する姐さん。後奏に4人（マイク・うさぎ・赤いツインテール・紅茶）が下りて下の段に並ぶ')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
MAP = [('0.0〜6.0', '前奏', '黒い縦ロール・椅子で紅茶', 'カバーのコマ'),
       ('6.0〜11.8', '前奏', '銀髪・投げキッス（反転）', ''),
       ('11.8〜17.6', 'じゅういちがつ はつか きんようびの', 'ピンクのポニーテール・マイク', ''),
       ('17.6〜24.7', 'はつばいの じぇいぽっぷの ちけっと', '赤いツインテール・跳ねる（反転）', ''),
       ('24.7〜30.0', 'いうわよ・間奏', '王冠・お辞儀', ''),
       ('30.0〜34.0', 'ごぜん じゅうじは せら まさのり とうきょう', 'ピンクのポニーテール・マイク（反転）', '世良公則さん'),
       ('34.0〜38.7', 'はやみ ゆう まつもと いよ もりぐち ひろこ ふくおか ほか', '金髪の三つ編み・うさぎ', '「青春のアイドルヒットステージ」'),
       ('38.7〜42.6', 'なかむら まさとし とうきょう ほか', '黒い縦ロール・紅茶（反転）', ''),
       ('42.6〜45.5', 'おぐら けい ぜんこく／じゅんれつ ぜんこく', 'ラベンダーのお団子・パラソル', ''),
       ('45.5〜48.7', 'しみず みちこ ぜんこく／あまい ぼうりょく とうきょう', 'ミントの髪・寝転ぶ（反転）', ''),
       ('48.7〜52.9', 'ごぜん じゅういちじは いもきん とりお とうきょう', 'ミントの髪・寝転ぶ', ''),
       ('52.9〜57.4', 'ひる じゅうにじは やいだ ひとみ きょうと', '金髪の三つ編み・うさぎ（反転）', ''),
       ('57.4〜60.6', 'きたやま おさむ とうきょう', '茶色のボブ・本', ''),
       ('60.6〜63.1', 'あべ やすひろ ちば ほか', 'ラベンダーのお団子・パラソル（反転）', ''),
       ('63.1〜65.7', 'なつかしい うたが いっぱいね', '赤いツインテール・跳ねる', ''),
       ('65.7〜69.6', 'ほかにも あるわ わすれないでね', '茶色のボブ・本（反転）', ''),
       ('69.6〜73.0', 'あのころの うたを なまで ききたいわ', '銀髪・投げキッス', ''),
       ('73.0〜77.1', 'おしなび どっと じぇーぴーで なまえを けんさくしてね', '王冠・お辞儀（反転）', ''),
       ('77.1〜85.1', 'こうえんと あーてぃすとの〜うりばまで あんないするのは おしなび', '（本物の OSHINAVI の画面）', '世良公則の 11/20 10:00 の箱をタップ'),
       ('85.1〜108.0', 'えっくすの ふぉろーも〜おしなび どっと じぇーぴー なのよね・後奏', '王冠・お辞儀（まん中）＋下に4人', 'マイク・うさぎ・赤いツインテール・紅茶')]
tbl = ''.join('<tr><td class="t">%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % m for m in MAP)
html = f'''<title>J-POPまとめ絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#1a0f18; --panel:#2a1826; --fg:#fbeef6; --muted:#d6b8cb; --accent:#ff8ad8; color-scheme: dark; --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
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
th, td {{ text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid #4a2c42; }}
th {{ color:var(--accent); }}
td.t {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
td b {{ color:var(--accent); }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/20(金)発売 J-POPまとめ（TikTok）の絵コンテ</h1>
<p>曲は1分48秒（おしなびどっと (34)）、テンポは81前後。絵はゴスロリの姐さん9人の1枚だけ（すちこ「雑よね　髪形がいつも同じ」→「キャラクター着席編集」のチャットで描き直し＝9人とも髪形・ポーズが違う）。背景はすちこが渡した 242696＝黒とえんじのダイヤ柄（元の明るさと色のまま）。背景が暗いので、歌詞は白（まだ）→黄（歌った所）に濃い縁。1人の出番はいちばん長くて7.1秒。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>歌う行と姐さん</h2><div class="tw"><table><thead><tr><th>秒</th><th>歌っている行</th><th>姐さん</th><th>メモ</th></tr></thead><tbody>{tbl}</tbody></table></div></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_a']}"></video><figcaption>頭 0〜36秒＝カバーの字 → 前奏 →「J-POPの チケット 言うわよ」→ 世良公則・早見優さんたち</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['clip_b']}"></video><figcaption>締め 76〜108秒＝タップの場面 → Xのフォロー → 「oshinavi.jp なのよね」で4人が下りる（最後まで）</figcaption></figure>
</div></section>
<section><h2>0秒のコマ（カバー）と締めの1コマ（104秒）</h2><div class="two">
<figure><img alt="0秒のコマ" src="data:image/jpeg;base64,{cover}"><figcaption>0秒</figcaption></figure>
<figure><img alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"><figcaption>104秒</figcaption></figure>
</div></section>
<section><h2>場面ごとの静止画（秒）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
<section><h2>切り抜いた9人</h2><img alt="切り抜いた9人" src="data:image/jpeg;base64,{cut}"></section>
</main>
'''
io.open(OUT, 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
