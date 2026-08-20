# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout.reconfigure(encoding='utf-8')
ids = [int(x) for x in sys.argv[1].split(',')]
raw = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))
for e in EV:
    if e['id'] in ids:
        print('=== id%s %s' % (e['id'], e.get('artist')))
        print('   date=%s / dateLabel=%s' % (e.get('date'), e.get('dateLabel')))
        print('   links=%s' % json.dumps(e.get('links'), ensure_ascii=False))
        for t in e.get('tickets') or []:
            print('   - %s | date=%s | start=%s | soldout=%s | url=%s' % (
                t.get('type'), t.get('date'), t.get('startDate'), t.get('soldout'), t.get('url')))
