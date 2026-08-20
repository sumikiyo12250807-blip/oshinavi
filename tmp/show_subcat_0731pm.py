# -*- coding: utf-8 -*-
"""相談候補の _piaSub / 会場 / リンクを出す。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for eid in (3521, 3523, 3525, 3544, 3564, 3565):
    e = next(x for x in EVENTS if x['id'] == eid)
    print('id=%d %s' % (eid, e['name']))
    print('   _piaSub=%s  _genre=%s  会場=%s  県=%s' % (
        e.get('_piaSub'), e.get('_genre'), e['venue'], e['prefecture']))
    print('   pia=%s' % (e['links'].get('pia')))
