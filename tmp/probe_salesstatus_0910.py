# -*- coding: utf-8 -*-
"""楽天の生HTMLに埋まっている salesDisplayStatus を読む。

購入ボタンの文字（「購入する」「予定枚数終了」）はJSが作るので生HTMLには出ないが、
その**もとになる状態はインラインJSの中に入っている**らしい。ここを機械で取れれば
ハーベスタと照合ツールの両方で「売り切れた公演」が分かる。
"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

U = 'https://ticket.rakuten.co.jp/sports/rtep928/'
body = R.fetch(U)

for kw in ['salesDisplayStatus', 'sales_status', 'performance_btn']:
    for m in list(re.finditer(kw, body))[:3]:
        i = m.start()
        print('===== %s @%d' % (kw, i))
        print(body[max(0, i - 900):i + 900])
        print()
