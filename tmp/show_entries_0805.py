# -*- coding: utf-8 -*-
"""指定idのエントリの名前・公演日・会場・links・枠を表示する。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

ids = [int(x) for x in sys.argv[1].split(',')]
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S).group(1))
byid = {e['id']: e for e in E}
for i in ids:
    e = byid.get(i)
    if not e:
        print('id=%d 見つからない' % i); continue
    print('=' * 70)
    print('id=%d  %s' % (i, e.get('name')))
    print('  artist=%s  genre=%s  date=%s  pref=%s' % (e.get('artist'), e.get('genre'), e.get('date'), e.get('prefecture')))
    print('  venue=%s' % e.get('venue'))
    print('  dateLabel=%s' % e.get('dateLabel'))
    for k, v in (e.get('links') or {}).items():
        if v:
            print('  link.%s = %s' % (k, v))
    for t in (e.get('tickets') or []):
        print('  枠: %s | date=%s start=%s url=%s' % (t.get('type'), t.get('date'), t.get('startDate'), t.get('url')))
