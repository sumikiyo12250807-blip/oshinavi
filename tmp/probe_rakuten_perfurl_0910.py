# -*- coding: utf-8 -*-
"""公演カードの「購入する」ボタンが持つ飛び先を探す（perf_NN と data-perf の対応）。"""
import re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://ticket.rakuten.co.jp/music/rtal267/'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
body = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')

for kw in ['perf_1', 'data-perf', 'purchase', 'rt.php', 'ticket.rakuten.co.jp/purchase', 'performanceId', 'perf_id']:
    idxs = [m.start() for m in re.finditer(re.escape(kw), body)][:3]
    print('== %s  hits=%d' % (kw, body.count(kw)))
    for i in idxs:
        print('   ...%s...' % re.sub(r'\s+', ' ', body[max(0, i-160):i+260]))
