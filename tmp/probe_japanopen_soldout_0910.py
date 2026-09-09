# -*- coding: utf-8 -*-
"""木下グループジャパンオープン(rtep928)の公演カードの売り状態を生HTMLで読む。

🚨楽天は「予定枚数終了」と「販売終了」を書き分けていない、というのが 2026-09-08 の実測。
   今回それが変わっているかを**文言そのもの**で確かめる（[[feedback_saleended_vs_soldout]]）。
   裏が取れない枠は弱いほう＝販売終了に倒す。
"""
import collections
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

U = 'https://ticket.rakuten.co.jp/sports/rtep928/'
body = R.fetch(U)
print('len=%d' % len(body))

# 売り状態の言葉を数える
WORDS = ['予定枚数終了', '完売', '売切', '売り切れ', 'SOLD OUT', 'soldout', 'sold out',
         '販売終了', '受付終了', '販売期間外', '取扱終了', '在庫なし']
cnt = collections.Counter()
for w in WORDS:
    cnt[w] = body.count(w)
print('言葉の数: %s' % {k: v for k, v in cnt.items() if v})

rec = R.parse_page(U, body)
print('\nshape=%s  perfs=%d  windows=%d' % (rec['shape'], len(rec['perfs']), len(rec['windows'])))
for w in rec['windows']:
    print('  WIN %-22s status=%r timming=%r' % (str(w.get('type'))[:22], w.get('status'), w.get('timming')))
for p in rec['perfs']:
    print('  P %s %s %-26s sale=%s〜%s  status=%s  tn=%s'
          % (p['date'], p.get('time') or '', (p.get('venue') or '')[:26],
             p.get('sale_start'), p.get('sale_end'), p.get('status'),
             (p.get('ticket_name') or '')[:30]))

# カードの状態クラスと近くの文言を生で見る
for m in list(R.CARD.finditer(body))[:60]:
    st = m.group('state')
    if 'active' in st:
        continue
    b = re.sub(r'\s+', ' ', R.strip_tags(m.group('body')))[:110]
    print('  [非active] state=%r  %s' % (st, b))
