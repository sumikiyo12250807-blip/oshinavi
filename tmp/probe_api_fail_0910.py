# -*- coding: utf-8 -*-
"""売り状態APIがJSONで返らないページの原因を見る。"""
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

for U in ['https://ticket.rakuten.co.jp/music/rtax088/',
          'https://ticket.rakuten.co.jp/event/matsuri/rtg2671/']:
    print('===== %s' % U)
    body = P.fetch(U)
    cards = P.parse_cards(body)
    print('cards=%d' % len(cards))
    print('ecd候補: %s' % re.findall(r'let\s+ecd\s*=\s*"([^"]+)"', body)[:5])
    print('eid候補: %s' % re.findall(r'"eid"\s*:\s*"(\d+)"', body)[:5])
    ecd, eid = P.parse_keys(body)
    if not cards or not ecd or not eid:
        print('  → 取れない\n')
        continue
    data = urllib.parse.urlencode({'ids': ','.join(c['perf'] for c in cards),
                                   'ecd': ecd, 'eid': eid}).encode()
    req = urllib.request.Request(P.API, data=data, headers={
        'User-Agent': P.UA,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://ticket.rakuten.co.jp', 'Referer': U,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'})
    try:
        r = urllib.request.urlopen(req, timeout=40)
        raw = r.read().decode('utf-8', 'replace')
        print('  status=%s len=%d raw=%r' % (r.status, len(raw), raw[:300]))
    except Exception as ex:
        print('  失敗 %r' % (ex,))
    print()
