# -*- coding: utf-8 -*-
"""ビルド結果JSONのうち指定idだけ表示（読むだけ）。使い方: python tmp/show_built_ids_0911.py <built.json> 7841,7846"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
IDS = {int(x) for x in sys.argv[2].split(',')}
for e in json.load(open(sys.argv[1], encoding='utf-8-sig')):
    if e.get('id') not in IDS:
        continue
    print('id%s %s | %s | %s | %s' % (e.get('id'), e.get('name'), e.get('dateLabel'), (e.get('venue') or '')[:40], (e.get('links') or {}).get('pia')))
    for t in e.get('tickets') or []:
        print('   - %s | date=%s start=%s' % (t.get('type'), t.get('date'), t.get('startDate')))
