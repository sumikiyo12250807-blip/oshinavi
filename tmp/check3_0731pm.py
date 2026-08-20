# -*- coding: utf-8 -*-
"""目視で気になった3件の詳細（_piaSub / links / ticket.url）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for eid in (3527, 3549, 3550, 3534, 3540):
    e = next(x for x in EVENTS if x['id'] == eid)
    print('id=%d %s' % (eid, e['name']))
    print('   _piaSub=%s  _genre=%s  _extraGenres=%s' % (
        e.get('_piaSub'), e.get('_genre'), e.get('_extraGenres')))
    print('   links=%s' % {k: v for k, v in e['links'].items() if v})
    for t in e['tickets']:
        print('     %s | url=%s' % (t['type'], t.get('url')))
    print()
