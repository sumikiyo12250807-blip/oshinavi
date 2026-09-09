# -*- coding: utf-8 -*-
"""売り状態APIの生の返りを見る（JSONで返らない理由を確かめる）。"""
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

U = 'https://ticket.rakuten.co.jp/sports/rtep928/'
body = P.fetch(U)
cards = P.parse_cards(body)
ecd, eid = P.parse_keys(body)
print('cards=%d ecd=%s eid=%s' % (len(cards), ecd, eid))
print('ids=%s' % ','.join(c['perf'] for c in cards))

data = urllib.parse.urlencode({'ids': ','.join(c['perf'] for c in cards),
                               'ecd': ecd, 'eid': eid}).encode()
req = urllib.request.Request(P.API, data=data, headers={
    'User-Agent': P.UA,
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://ticket.rakuten.co.jp',
    'Referer': U,
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
})
try:
    r = urllib.request.urlopen(req, timeout=40)
    raw = r.read().decode('utf-8', 'replace')
    print('status=%s len=%d' % (r.status, len(raw)))
    print(raw[:1500])
except Exception as ex:
    print('失敗: %r' % (ex,))
    if hasattr(ex, 'read'):
        print(ex.read().decode('utf-8', 'replace')[:800])
