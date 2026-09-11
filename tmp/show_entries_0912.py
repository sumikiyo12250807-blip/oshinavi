# -*- coding: utf-8 -*-
"""指定idの登録値（date / dateLabel / prefecture / venue / tickets）を短く並べる（読むだけ）。
使い方: python tmp/show_entries_0912.py 7933,7946
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ids = [int(x) for x in sys.argv[1].split(',')]
h = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}
for i in ids:
    e = by.get(i)
    if not e:
        print('id%s 無い' % i)
        continue
    print('id%s %s [genre=%s]' % (i, e.get('name'), e.get('genre')))
    print('   date=%s | %s' % (e.get('date'), e.get('dateLabel')))
    print('   pref=%s | venue=%s' % (e.get('prefecture'), e.get('venue')))
    for t in e.get('tickets') or []:
        flags = ''.join(k for k in ('soldout', 'saleEnded', 'saleEndUnknown', 'saleUntilSoldOut') if t.get(k))
        print('   - %s | date=%s start=%s %s' % (t.get('type'), t.get('date'), t.get('startDate') or '-', flags))
