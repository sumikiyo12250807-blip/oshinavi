# -*- coding: utf-8 -*-
"""id7494 木下グループジャパンオープンテニス＝売り切れた枠に「予定枚数終了」を付ける。

ユーザー発見（2026-09-10）「木下グループが売り切れ出てる　売り切れで表示してね」。

🚨実測でわかったこと＝**楽天の売り状態は購入ボタンの文字にしか出ない。生HTMLには無い。**
   https://ticket.rakuten.co.jp/sports/rtep928/ を実ブラウザで読んだ結果:
     2026-09-28 11:00  購入する
     2026-09-29 11:00  購入する
     2026-09-30 11:00  予定枚数終了
     2026-09-30 16:00  予定枚数終了
     2026-10-01 11:00  予定枚数終了   （以下 10/6 まで全部 予定枚数終了）
   公演カードの class は14件とも 'active' のままなので、ハーベスタの status は「受付中」と読む。

「予定枚数終了」と明記されているので `soldout` のまま＝`saleEnded` は付けない
（[[feedback_saleended_vs_soldout]]＝裏が取れた強い主張はそのまま書く）。
売り切れは消さずに出し続ける（[[feedback_soldout_keep_visible]]）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 実ブラウザで読んだ「予定枚数終了」の公演日（この日を含む枠に印を付ける）
SOLD_DATES = {'9/30', '10/1', '10/2', '10/3', '10/4', '10/5', '10/6'}
ALIVE_DATES = {'9/28', '9/29'}
TODAY = '2026-09-10'

src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = next((e for e in events if e['id'] == 7494), None)
assert hit, 'id7494 が無い'

n = 0
for t in hit.get('tickets') or []:
    mm = re.search(r'（[^（）]*?([\d/〜]+)公演）', t.get('type') or '')
    if not mm:
        continue
    days = set(mm.group(1).split('〜'))
    # 「10/4〜10/6公演」は端の2つしか書かれていないが、実測では中の10/5も売り切れ
    if days & SOLD_DATES and not (days & ALIVE_DATES):
        t['soldout'] = True
        t['soldoutSince'] = TODAY
        t.pop('saleEnded', None)
        t.pop('saleEndedSince', None)
        n += 1
        print('予定枚数終了に: %s' % t['type'])
    else:
        print('そのまま（買える）: %s' % t['type'])

print('\n%d枠に印を付けたわ' % n)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('書き込み完了')
