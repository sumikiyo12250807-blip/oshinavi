# -*- coding: utf-8 -*-
"""指定idのエントリ概要（公演名・会場・日付・links・tickets）を出す"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [int(x) for x in sys.argv[1].split(',')]
raw = io.open('index.html', 'r', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', raw, re.S).group(1))
by_id = {e['id']: e for e in EVENTS}

for i in IDS:
    e = by_id.get(i)
    if not e:
        print('id%d MISSING' % i); continue
    print('--- id=%d %s / %s' % (i, e.get('artist',''), e.get('title','')))
    print('    会場=%s  公演日=%s  都道府県=%s' % (e.get('venue',''), e.get('date',''), e.get('prefecture','')))
    for k, v in (e.get('links') or {}).items():
        print('    link.%s = %s' % (k, v))
    for t in e.get('tickets') or []:
        print('    枠: %s | date=%s | start=%s | soldout=%s' % (
            t.get('type'), t.get('date'), t.get('startDate'), t.get('soldout')))
        if t.get('url'):
            print('        url=%s' % t.get('url'))
