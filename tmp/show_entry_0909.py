# -*- coding: utf-8 -*-
"""指定idのエントリを読みやすく表示するだけの使い捨て。"""
import sys, json
sys.path.insert(0, 'tools')
from reconcile_pia import load_events
sys.stdout.reconfigure(encoding='utf-8')

ids = [int(x) for x in sys.argv[1].split(',')]
evs = load_events('index.html')
for e in evs:
    if int(e.get('id', -1)) in ids:
        print('=' * 70)
        for k in ('id', 'name', 'artist', 'genre', 'date', 'dateLabel', 'venue', 'prefecture'):
            print(f'{k:12} = {e.get(k)!r}')
        for i, t in enumerate(e.get('tickets', []), 1):
            print(f'  [{i}] type={t.get("type")!r}')
            print(f'      startDate={t.get("startDate")} date={t.get("date")} '
                  f'soldout={t.get("soldout")} saleUntilSoldOut={t.get("saleUntilSoldOut")}')
            print(f'      url={t.get("url")}')
        print('  links=', json.dumps(e.get('links', {}), ensure_ascii=False))
