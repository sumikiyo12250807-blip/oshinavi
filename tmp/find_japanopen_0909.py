# -*- coding: utf-8 -*-
"""ジャパンオープンテニスのエントリを探して、枠と締切をそのまま並べる。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))
for e in EV:
    blob = (e.get('name') or '') + (e.get('artist') or '')
    if 'ジャパンオープン' in blob or 'ジャパン オープン' in blob:
        print('=' * 66)
        for k in ('id', 'name', 'artist', 'genre', 'date', 'dateLabel', 'venue', 'prefecture'):
            print('%-11s = %s' % (k, e.get(k)))
        print('枠 %d件:' % len(e.get('tickets', [])))
        for i, t in enumerate(e.get('tickets', []), 1):
            print('  [%2d] %s' % (i, t.get('type')))
            print('       startDate=%s  date(締切)=%s  soldout=%s  saleEndUnknown=%s' %
                  (t.get('startDate'), t.get('date'), t.get('soldout'), t.get('saleEndUnknown')))
            print('       url=%s' % t.get('url'))
        print('  links=', json.dumps(e.get('links', {}), ensure_ascii=False))
