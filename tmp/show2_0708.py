# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
for i in [2218, 2223]:
    e = byid[i]
    print('id=%d %s' % (i, e['artist']))
    print('  pia:', e['links'].get('pia'))
    for t in e['tickets']:
        print('   -', t['type'], '(', t['date'], ')')
    print()
