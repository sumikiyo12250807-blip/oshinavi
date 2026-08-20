# -*- coding: utf-8 -*-
"""⚠️相談5件のジャンル下書きを確定させる。
 2527 アークラ大サーカス 会場内駐車場 → engeki（ユーザー指示「サーカスと同じくくり」。
      既存 id975 G-Rockets アクロバットダンス・サーカス = engeki に揃える）
 2503 飛生芸術祭「トビウの祝祭」 → art（公式で裏取り＝木造校舎内の展覧会が主体・美術展示中心。
      fes定義「複数組＋屋外」に当たらない）
 2531 秋季金剛界結縁灌頂 → dento（高野山・真言宗の伝統儀式）※推し案・ユーザー確認中
 2536 松本怜生トークショー → engeki（俳優本人のトークショー）※推し案・ユーザー確認中
 2548 夏井いつき句会ライブ → owarai（ぴあ演劇枠・寄席的トークライブ）※推し案・ユーザー確認中
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

FIX = {2527: 'engeki', 2503: 'art', 2531: 'dento', 2536: 'engeki', 2548: 'owarai'}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

changed = []
for e in E:
    i = e['id']
    if i in FIX and e.get('genre') == 'new':
        old = e.get('_genre')
        if old != FIX[i]:
            e['_genre'] = FIX[i]
            changed.append((i, e.get('artist', '')[:40], old, FIX[i]))

for i, a, o, n in changed:
    print(f'  id{i} {a} : {o} → {n}')
bak = f'index.html.bak_{datetime.date.today():%m%d}_genre_draft2'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print(f'=== {len(changed)}件確定 (backup {bak}) ===')
