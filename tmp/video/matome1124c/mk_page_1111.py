# -*- coding: utf-8 -*-
# 11/11 お笑いまとめ（X 今夜）の絵コンテのページ：流れ・試し動画2本・締めの1コマ・場面ごとの静止画 → scratchpad/owarai1111/board_page.html
import base64, io, os
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/402b246e-9e52-46c7-9b59-f5c4808ec0be/scratchpad/owarai1111/'
os.makedirs(OUT, exist_ok=True)
b = Image.open(D + 'board.png').convert('RGB')
buf = io.BytesIO(); b.save(buf, 'JPEG', quality=82)
img = base64.b64encode(buf.getvalue()).decode()
end = Image.open(D + 'frames/h_073.7.png').convert('RGB').resize((540, 960))
buf2 = io.BytesIO(); end.save(buf2, 'JPEG', quality=86)
endimg = base64.b64encode(buf2.getvalue()).decode()
vids = {k: base64.b64encode(open(D + 'clip_%s_s.mp4' % k, 'rb').read()).decode() for k in ('walk', 'end')}
rows = [('0〜10秒（頭）', '歌い出しが 0.5 秒と早いので、最初から「明日 11月11日の 発売の お笑い 言うわよ」を出す。金髪のチェックのコートの子が左から歩いて入ってくる'),
        ('10〜63秒（名前を歌う所）', '約7秒ごとに次の子へ。歩く子は歩いて出入りし、座る子はまん中にふわっと現れる＝金髪のコート（歩く）→ シャンパンの紫の髪 → 青い髪のトレンチ（歩く）→ めがねで読書 → 紙袋の子（歩く）→ 赤いドレスのカフェ → 金髪のコート（向きを反対にしてもう一度・右から左へ歩く）→ 黒い帽子でお茶 → 青い髪のトレンチ（反対向きでもう一度）'),
        ('63〜69秒（サビ）', '本物の OSHINAVI の画面で SUN「新春！よしもと大爆笑2027」（NON STYLE 石田明ほか）の 11/11 10:00 のバッジをタップ。歌詞「売り場まで 案内するのは おしなび」'),
        ('69〜75.7秒（締め・後奏）', 'エッフェル塔の子がまん中に出て「OSHINAVI.jp なのよ」。下の段に2拍に1人ずつ4人（猫の子・紙袋の子・シャンパンの子・青い髪のトレンチ）が下りてきて並ぶ＝締めは5人')]
li = ''.join('<li><b>%s</b><span>%s</span></li>' % r for r in rows)
html = f'''<title>お笑い11/11 絵コンテ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#14121c; --panel:#1e1b2a; --fg:#efeaf6; --muted:#b5aec6; --accent:#ffd84a; color-scheme: dark;
  --sans: "Hiragino Sans", "Meiryo", sans-serif; }}
:root[data-theme="light"] {{ --bg:#14121c; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.7; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 48px; }}
main {{ max-width:1100px; margin:0 auto; display:grid; gap:28px; }}
h1 {{ font-size:1.5rem; margin:0; text-wrap:balance; }}
h2 {{ font-size:1.1rem; margin:0 0 10px; color:var(--accent); }}
p {{ margin:0; color:var(--muted); max-width:65ch; }}
ul {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
li {{ display:grid; grid-template-columns:minmax(0,12em) minmax(0,1fr); gap:12px; padding:10px 12px; background:var(--panel); border-radius:8px; }}
li b {{ color:var(--accent); font-weight:700; }}
@media (max-width:640px) {{ li {{ grid-template-columns:1fr; gap:2px; }} }}
.vids {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }}
figure {{ margin:0; display:grid; gap:6px; min-width:0; }}
figcaption {{ color:var(--muted); font-size:.92rem; }}
video, img {{ width:100%; max-width:100%; border-radius:8px; background:var(--panel); display:block; }}
.end {{ max-width:360px; }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>11/11(水)発売 お笑いまとめ（今夜の X）の絵コンテ</h1>
<p>曲 1分15秒・テンポ約96。パリコレの子9人。歩いている3人（金髪のコート・青い髪のトレンチ・紙袋の子）を多めに出し、座っている子とかわりばんこ。子は拍に合わせて弾む。背景は黒地に色の線の格子（字が読めるよう暗くぼかした）。</p>
</header>
<section><h2>流れ</h2><ul>{li}</ul></section>
<section><h2>試し動画</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['walk']}"></video><figcaption>入れ替わる所（5〜19秒）＝歩く子 → 座る子 → 歩く子</figcaption></figure>
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['end']}"></video><figcaption>サビのタップ〜締め（60秒〜終わり）</figcaption></figure>
</div></section>
<section><h2>締めの1コマ（終わりの2秒前・73.7秒）</h2><img class="end" alt="締めのコマ" src="data:image/jpeg;base64,{endimg}"></section>
<section><h2>場面ごとの静止画（秒と服）</h2><img alt="絵コンテ" src="data:image/jpeg;base64,{img}"></section>
</main>
'''
io.open(OUT + 'board_page.html', 'w', encoding='utf-8').write(html)
print(len(html) // 1024, 'KB')
