# -*- coding: utf-8 -*-
"""削除候補の確認用URLを index.html から機械抽出する（URLの捏造禁止）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = ['463', '568', '1049', '3511', '101', '361', '900', '1985',
       '2688', '2982', '3729', '1627']

raw = open(r'C:\Users\user\oshinavi\index.html', 'rb').read().decode('utf-8')
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', raw, re.S)
events = json.loads(m.group(2))
by_id = {str(e.get('id')): e for e in events}

for i in IDS:
    e = by_id.get(i)
    if not e:
        print('id=%s 見つからない' % i)
        continue
    links = e.get('links') or {}
    alive = {k: v for k, v in links.items() if v}
    print('id=%s | %s | %s | 公演日=%s' % (i, e.get('artist'), e.get('title'), e.get('date')))
    print('   会場: %s' % e.get('venue'))
    for k, v in alive.items():
        print('   %s: %s' % (k, v))
    print('   枠数=%d' % len(e.get('tickets') or []))
    print()
