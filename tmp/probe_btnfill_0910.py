# -*- coding: utf-8 -*-
"""購入ボタン（perf_N）を埋めているJSと、そのデータを生HTMLから探す。"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

U = 'https://ticket.rakuten.co.jp/sports/rtep928/'
body = R.fetch(U)
print('len=%d' % len(body))

for kw in ['購入する', 'data-perf', 'perf_id', 'performanceCd', 'perfCd', 'ajax', 'getJSON',
           '$.post', 'fetch(', 'XMLHttpRequest', 'performance-msg', '販売は終了']:
    idxs = [m.start() for m in re.finditer(re.escape(kw), body)]
    print('== %s hits=%d  %s' % (kw, len(idxs), idxs[:5]))

# 「購入する」の周りを見る（ボタンのテンプレートがあるはず）
for m in list(re.finditer('購入する', body))[:4]:
    i = m.start()
    print('\n----- 購入する @%d\n%s' % (i, body[max(0, i - 1200):i + 400]))
