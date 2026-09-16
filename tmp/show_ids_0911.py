# -*- coding: utf-8 -*-
"""指定idのエントリを要点だけ表示（読むだけ）。使い方: python tmp/show_ids_0911.py 7795,7796"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
IDS = [int(x) for x in sys.argv[1].split(',')]
src = open('index.html', encoding='utf-8').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
by = {e['id']: e for e in json.loads(m.group(1))}
for i in IDS:
    e = by.get(i)
    if not e:
        print('id%s なし' % i); continue
    print('id%s [%s/%s] %s' % (i, e.get('genre'), e.get('_genre'), e.get('name')))
    print('   date=%s label=%s pref=%s venue=%s' % (e.get('date'), e.get('dateLabel'), e.get('prefecture'), (e.get('venue') or '')[:60]))
    print('   pia=%s' % ((e.get('links') or {}).get('pia')))
    for t in e.get('tickets') or []:
        print('   - %s | date=%s start=%s %s%s' % (t.get('type'), t.get('date'), t.get('startDate'),
              'SOLD ' if t.get('soldout') else '', (t.get('url') or '')[-40:]))
