# -*- coding: utf-8 -*-
"""相談待ちで新着プールに残している4件の実物を出す（記憶でなく現物を見る）。"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
idx = io.open('index.html', encoding='utf-8').read()
EV = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))}
for eid in (4377, 4400, 4417, 4418):
    e = EV.get(eid)
    if not e:
        print('id%d が無い' % eid); continue
    print('=== id%d %s' % (eid, e.get('artist', '')))
    print('   会場   %s（%s）' % (e.get('venue', ''), e.get('prefecture', '')))
    print('   公演日 %s ／ %s' % (e.get('date', ''), e.get('dateLabel', '')))
    print('   下書き _genre=%s / _piaSub=%s' % (e.get('_genre', '-'), e.get('_piaSub') or '(空)'))
    print('   URL    %s' % ((e.get('links') or {}).get('pia') or (e.get('links') or {}).get('official') or ''))
    for t in e.get('tickets') or []:
        print('   枠  %s | %s〜%s' % (t.get('type', ''), t.get('startDate'), t.get('date')))
    print()
