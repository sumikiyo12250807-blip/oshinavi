# -*- coding: utf-8 -*-
# 11/21発売の X 11本（post/ の mat01〜08・shu01〜03）→ all_1121.txt（予約の順と時刻つき）＋携帯で読む確認ページ xcheck_1121.html
import io, html, re
X = 'C:/Users/user/oshinavi/tmp/x1120/x/'
ORDER = ['mat01', 'mat02', 'mat03', 'mat04', 'mat05', 'mat06', 'mat07', 'mat08', 'shu01', 'shu02', 'shu03']
TIMES = ['19:31', '19:41', '19:51', '20:01', '20:11', '20:21', '20:31', '20:41', '20:51', '21:01', '21:11']
VID = {'mat05': 'oshinavi_1121_owarai_matome_x.mp4（check_x_video ✅ 1121）', 'mat08': 'oshinavi_1121_rock_matome_x.mp4（check_x_video ✅ 1121）'}
NOTES = [
    '主役＝①TOMORROW X TOGETHER（1,520万・福岡 12/19〜20 と大阪 1/30〜31 が 13:00 一般発売）②宮川大輔×ケンドーコバヤシ あんぎゃー愛媛公演（176万・FANY 10:00 一般）③山里亮太の140 広島公演（156万・ぴあ 11:00 先行の抽選）',
    'トレンド枠は無し＝1〜8位（クレープ・おむすび・ゼンゼロ・すき家・魔法使い・PayPay・タイヤ交換・初期費用）に名前で当たる買える枠が無かった',
    '機械検品 11本とも指摘なし／独立の確かめ＝🔴1🟠2 → 直した：TXT は福岡も明日 13:00 一般発売なのに大阪だけだった（①と⑦に福岡を足した・カードにも福岡を足す作業を裏で回している）／⑦の TXT の行／④ 11/22 の『組曲虐殺』東京は「U-25受付」と書き足した',
    '📖記事の1行は ⑦広瀬香美',
    '🎬動画：⑤お笑い・⑧ロックにまとめ動画（投稿の発売日 11/21 と動画の 1121 が合うのを確かめ済み）',
    'フォロワーは検索ではほぼ拾えず、主役候補の大きい名前はブラウザで X のプロフィールを読んだ',
]
CSS = '''<title>11/21発売 確認用</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root { --bg:#fbf9fb; --fg:#26202a; --muted:#6d6473; --card:#ffffff; --line:#e7dfe9; --accent:#b0336f; --note:#fff4e5; --font:"Noto Sans JP", system-ui, sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#17141a; --fg:#ece6ef; --muted:#a79fae; --card:#211d25; --line:#352f3a; --accent:#f07fb2; --note:#2e2418; color-scheme:dark; } }
:root[data-theme="dark"] { --bg:#17141a; --fg:#ece6ef; --muted:#a79fae; --card:#211d25; --line:#352f3a; --accent:#f07fb2; --note:#2e2418; color-scheme:dark; }
body { background:var(--bg); color:var(--fg); font-family:var(--font); font-size:16px; line-height:1.75; margin:0; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:12px 48px; }
.wrap { max-width:680px; margin:0 auto; display:flex; flex-direction:column; gap:20px; }
h1 { font-size:20px; margin:8px 0 0; text-wrap:balance; }
a { color:var(--accent); }
.note { background:var(--note); border:1px solid var(--line); border-radius:10px; padding:12px 14px; }
.note ul { margin:4px 0 0; padding-left:20px; }
nav { display:flex; flex-wrap:wrap; gap:6px 14px; font-size:15px; }
article { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px; min-width:0; }
h3 { font-size:16px; margin:0 0 4px; color:var(--accent); }
.meta { font-size:14px; color:var(--muted); margin-bottom:8px; overflow-wrap:anywhere; }
.txt { white-space:pre-wrap; overflow-wrap:anywhere; }
</style>
'''
posts, allt = [], []
for f, tm in zip(ORDER, TIMES):
    body = io.open(X + 'post/' + f + '.txt', encoding='utf-8').read().strip()
    m = re.search(r'＼(.+?)／', body)
    posts.append((f, tm, m.group(1) if m else f, body))
    allt.append('===== %s.txt %s\n%s\n' % (f, tm, body))
io.open(X + 'all_1121.txt', 'w', encoding='utf-8').write('\n'.join(allt))
b = [CSS, '<div class="wrap">', '<h1>11/21(土)発売の X 11本（今夜 19:31〜 10分おき）</h1>',
     '<div class="note"><b>見てほしいところ</b><ul>' + ''.join('<li>%s</li>' % html.escape(n) for n in NOTES) + '</ul></div>',
     '<nav>' + ''.join('<a href="#p%d">%d %s</a>' % (i, i + 1, html.escape(t.replace('明日発売の', ''))) for i, (f, tm, t, _) in enumerate(posts)) + '</nav>']
for i, (f, tm, t, body) in enumerate(posts):
    v = VID.get(f)
    meta = '予約 %s／%s' % (tm, ('🎬 動画 ' + v) if v else '動画なし')
    b.append('<article id="p%d"><h3>%d %s（%d字）</h3><div class="meta">%s</div><div class="txt">%s</div></article>' % (i, i + 1, html.escape(t), len(body), html.escape(meta), html.escape(body)))
b.append('</div>')
io.open(X + 'xcheck_1121.html', 'w', encoding='utf-8').write('\n'.join(b))
print(len(posts))
